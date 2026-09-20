"""Query contracts plus opt-in tests against an isolated, migrated PostgreSQL DB.

FACTURE_TEST_DATABASE_URL must target localhost and a database named gap003_*.
The database must already contain migrations through 015 and a mandate fixture.
Each integration test holds an outer transaction; service commits use savepoints.
"""
import os
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from src.api.db.models.facture_client import FactureClient
from src.api.repositories.facture_client import FactureClientRepository


def compiled(statement):
    return str(statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


def test_scope_uses_persisted_lineage_not_invoice_client_snapshot():
    db = MagicMock()
    repository = FactureClientRepository(db)
    repository.list_accessible(client_id=35)
    sql = compiled(db.scalars.call_args.args[0])
    assert "JOIN real_estate.vente" in sql
    assert "JOIN real_estate.mandat" in sql
    assert "WHERE real_estate.mandat.id_client = 35" in sql
    assert "WHERE real_estate.facture_client.id_client" not in sql
    repository.get_by_id(42, chasseur_id=4)
    sql = compiled(db.scalar.call_args.args[0])
    assert "real_estate.vente.id_chasseur_beneficiaire = 4" in sql
    assert "real_estate.facture_client.id_facture_client = 42" in sql


def test_sale_and_payment_are_locked_and_lookup_methods_are_specific():
    db = MagicMock()
    repository = FactureClientRepository(db)
    repository.get_sale_context(100)
    assert "FOR UPDATE OF vente, mandat" in compiled(db.execute.call_args.args[0])
    repository.get_payment_for_update(100)
    assert "FOR UPDATE" in compiled(db.scalar.call_args.args[0])
    repository.get_by_vente(100)
    assert "WHERE real_estate.facture_client.id_vente = 100" in compiled(db.scalar.call_args.args[0])
    repository.get_by_numero("FC-0000000100")
    assert "WHERE real_estate.facture_client.numero_facture = 'FC-0000000100'" in compiled(db.scalar.call_args.args[0])


@pytest.fixture
def postgres_db():
    from src.api.main import app  # Register models through the production router imports.

    dsn = os.environ.get("FACTURE_TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("Set FACTURE_TEST_DATABASE_URL for isolated PostgreSQL integration tests")
    url = make_url(dsn)
    assert url.host in {"localhost", "127.0.0.1"} and url.database.startswith("gap003_"), (
        "Invoice integration tests require an explicitly isolated local gap003_* database"
    )
    engine = create_engine(url)
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
            try:
                yield session
            finally:
                session.close()
                transaction.rollback()
    engine.dispose()


def sale_fixture(db, *, entitled=False):
    from src.api.db.models.mandat import Mandat
    from src.api.db.models.vente import Vente
    from src.api.services.remuneration import RemunerationService

    mandate = db.scalar(select(Mandat).order_by(Mandat.id_mandat).limit(1))
    assert mandate is not None
    sale = Vente(id_mandat=mandate.id_mandat, origine_vente="CLIENT_SEUL",
                 date_acte_authentique=date(2026, 1, 15), montant_achat=Decimal("420000.20"))
    db.add(sale)
    db.flush()
    payment = RemunerationService(db).calculate_for_vente(sale.id_vente, utilisateur="local-test")
    assert payment.droit_remuneration is False
    if entitled:
        # Exercise read scope with a persisted beneficiary without changing
        # the unrelated remuneration-calculation fixture requirements.
        sale.id_chasseur_beneficiaire = mandate.id_chasseur
        db.commit()
    return sale, mandate, payment


@pytest.mark.parametrize("entitled", [False, True])
def test_postgres_api_invoice_receipt_audit_ownership_and_duplicate(postgres_db, entitled):
    from src.api.api.v1.endpoints.factures_clients import router
    from src.api.core.dependencies import get_current_user
    from src.api.db.models.audit_log import AuditLog
    from src.api.db.session import get_db
    from src.api.schemas.auth import AuthenticatedUser
    from src.api.services.paiement import PaiementService

    db = postgres_db
    sale, mandate, payment = sale_fixture(db, entitled=entitled)
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db

    def login(role, identity=None):
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
            id_utilisateur=1, email="invoice-test@example.com", role=role,
            id_client=identity if role == "CLIENT" else None,
            id_chasseur=identity if role == "CHASSEUR" else None,
        )

    login("ADMIN")
    with TestClient(app) as client:
        assert client.post("/factures-clients", json={"id_vente": sale.id_vente}).status_code == 422
        PaiementService(db).transition(
            payment.id_paiement, statut_cible="RECU", utilisateur="local-test",
            date_reception_honoraires=date(2026, 1, 16),
        )
        response = client.post("/factures-clients", json={"id_vente": sale.id_vente})
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["montant_honoraires_ht"] == "13500.01"
        assert body["id_client"] == mandate.id_client
        invoice_id = body["id_facture_client"]
        assert client.post("/factures-clients", json={"id_vente": sale.id_vente}).status_code == 409
        # Reproduce a stale pre-check, as in a concurrent writer: the real
        # PostgreSQL UNIQUE violation must still become the domain conflict.
        from src.api.schemas.facture_client import FactureClientCreate
        from src.api.services.facture_client import FactureClientAlreadyExistsError, FactureClientService

        racing_service = FactureClientService(db)
        racing_service.repository.get_by_vente = lambda sale_id: None
        with pytest.raises(FactureClientAlreadyExistsError):
            racing_service.create_facture(
                FactureClientCreate(id_vente=sale.id_vente),
                utilisateur="local-test", id_utilisateur=1,
            )
        path = f"/factures-clients/{invoice_id}"
        for role, own_id in [("CLIENT", mandate.id_client), ("CHASSEUR", mandate.id_chasseur)]:
            login(role, own_id)
            if role == "CHASSEUR" and not entitled:
                assert client.get(path).status_code == 404
                assert client.get("/factures-clients").json() == []
                continue
            assert client.get(path).status_code == 200
            assert any(row["id_facture_client"] == invoice_id for row in client.get("/factures-clients").json())
            login(role, own_id + 1000000)
            assert client.get(path).status_code == 404
            assert client.get("/factures-clients").json() == []
        audit = db.scalar(select(AuditLog).where(
            AuditLog.table_name == "facture_client", AuditLog.record_id == str(invoice_id),
        ))
        assert audit.nouvelle_valeur["montant_honoraires_ht"] == "13500.01"
        assert audit.contexte["id_paiement"] == payment.id_paiement
        assert audit.utilisateur == "invoice-test@example.com"
        db.execute(text("UPDATE real_estate.parametres_honoraires SET montant_fixe = montant_fixe + 1 WHERE id_parametres_honoraires = :id"),
                   {"id": body["id_parametres_honoraires"]})
        db.expire_all()
        invoice = FactureClientRepository(db).get_by_id(invoice_id)
        assert invoice.montant_honoraires_ht == Decimal("13500.01")
        assert invoice.montant_fixe_applique == Decimal("3000.00")


def test_postgres_model_matches_migration(postgres_db):
    from sqlalchemy import inspect

    inspector = inspect(postgres_db.connection())
    columns = inspector.get_columns("facture_client", schema="real_estate")
    model = FactureClient.__table__
    assert {c["name"] for c in columns} == set(model.columns.keys())
    for column in columns:
        expected = model.c[column["name"]]
        assert column["nullable"] == expected.nullable
        assert str(column["type"].compile(dialect=postgresql.dialect())) == str(expected.type.compile(dialect=postgresql.dialect()))
    assert {c["name"] for c in inspector.get_unique_constraints("facture_client", schema="real_estate")} == {
        "uq_facture_client_vente", "uq_facture_client_numero",
    }
