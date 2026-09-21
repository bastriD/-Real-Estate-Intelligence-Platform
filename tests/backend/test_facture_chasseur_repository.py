from unittest.mock import MagicMock

from sqlalchemy.dialects import postgresql

from src.api.repositories.facture_chasseur import FactureChasseurRepository
from src.api.repositories.paiement import PaiementRepository


def sql(statement):
    return str(statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


def test_hunter_reads_join_authoritative_payment_beneficiary():
    db = MagicMock()
    repo = FactureChasseurRepository(db)
    repo.get_by_id(12, 3)
    query = sql(db.scalar.call_args.args[0])
    assert "JOIN real_estate.paiement" in query
    assert "paiement.id_chasseur_beneficiaire = 3" in query
    assert "facture_chasseur.id_facture_chasseur = 12" in query
    repo.list_accessible(3)
    assert "paiement.id_chasseur_beneficiaire = 3" in sql(db.scalars.call_args.args[0])
    repo.get_by_id(12)
    assert "paiement.id_chasseur_beneficiaire =" not in sql(db.scalar.call_args.args[0])


def test_locked_review_refreshes_identity_map_after_waiting():
    db = MagicMock()
    FactureChasseurRepository(db).get_by_id_for_update(12)
    statement = db.scalar.call_args.args[0]
    assert "FOR UPDATE" in sql(statement)
    assert statement.get_execution_options()["populate_existing"] is True


def test_latest_version_and_create_flush_without_commit():
    db = MagicMock()
    repo = FactureChasseurRepository(db)
    repo.get_latest(10)
    query = sql(db.scalar.call_args.args[0])
    assert "id_paiement = 10" in query and "numero_version DESC" in query and "LIMIT 1" in query
    record = object()
    assert repo.create(record) is record
    db.add.assert_called_once_with(record)
    db.flush.assert_called_once()
    db.refresh.assert_called_once_with(record)
    db.commit.assert_not_called()


def test_payment_gate_checks_amount_ownership_entitlement_and_receipt():
    db = MagicMock()
    repo = PaiementRepository(db)
    db.scalar.return_value = None
    assert repo.has_conforming_invoice(10) is False
    query = sql(db.scalar.call_args.args[0])
    for clause in ["paiement.id_paiement = 10", "facture_chasseur.statut = 'CONFORME'",
        "facture_chasseur.id_chasseur = real_estate.paiement.id_chasseur_beneficiaire",
        "facture_chasseur.montant = real_estate.paiement.montant_chasseur",
        "paiement.droit_remuneration IS true", "paiement.date_reception_honoraires IS NOT NULL"]:
        assert clause in query
    db.scalar.return_value = 1
    assert repo.has_conforming_invoice(10) is True
