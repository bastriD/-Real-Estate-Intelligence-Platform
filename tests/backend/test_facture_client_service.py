import json
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.api.db.models.audit_log import AuditLog
from src.api.schemas.facture_client import FactureClientCreate
from src.api.services.facture_client import (
    FactureClientAlreadyExistsError, FactureClientNotFoundError,
    FactureClientService, FactureClientValidationError,
)


@pytest.fixture
def scenario():
    db = MagicMock()
    service = FactureClientService(db)
    service.repository = MagicMock()
    service.honoraires = MagicMock()
    sale = SimpleNamespace(id_vente=100, id_mandat=20, montant_achat=Decimal("420000.20"),
                           date_acte_authentique=date(2025, 1, 1))
    mandate = SimpleNamespace(id_mandat=20, id_client=35)
    parameters = SimpleNamespace(id_parametres_honoraires=7, montant_fixe=Decimal("3000.00"),
                                 taux_pourcentage=Decimal("0.0250"))
    payment = SimpleNamespace(id_paiement=8, id_mandat=20, statut="RECU",
                              date_reception_honoraires=date(2025, 1, 2),
                              date_acte_authentique=sale.date_acte_authentique,
                              montant_achat=sale.montant_achat, id_parametres_honoraires=7,
                              montant_honoraires=Decimal("13500.01"))
    service.repository.get_sale_context.return_value = (sale, mandate)
    service.repository.get_by_vente.return_value = None
    service.repository.get_payment_for_update.return_value = payment
    service.honoraires.get_effective.return_value = parameters

    def persist(invoice):
        invoice.id_facture_client = 42
        invoice.date_creation = datetime.now(timezone.utc)
        return invoice

    service.repository.create.side_effect = persist
    return SimpleNamespace(service=service, db=db, sale=sale, mandate=mandate,
                           parameters=parameters, payment=payment)


def issue(s):
    return s.service.create_facture(FactureClientCreate(id_vente=100),
                                    utilisateur="admin@example.com", id_utilisateur=1)


def test_issue_derives_lineage_selects_deed_date_and_writes_atomic_audit(scenario):
    s = scenario
    invoice = issue(s)
    assert invoice.id_client == s.mandate.id_client
    assert invoice.numero_facture == "FC-0000000100"
    assert invoice.date_emission == datetime.now(timezone.utc).date()
    assert invoice.montant_honoraires_ht == Decimal("13500.01")  # HALF_UP cent tie
    assert isinstance(invoice.montant_honoraires_ht, Decimal)
    assert invoice.montant_fixe_applique == Decimal("3000.00")
    assert invoice.taux_pourcentage_applique == Decimal("0.0250")
    assert invoice.montant_achat == s.sale.montant_achat
    s.service.honoraires.get_effective.assert_called_once_with(date(2025, 1, 1))
    audit = next(c.args[0] for c in s.db.add.call_args_list if isinstance(c.args[0], AuditLog))
    assert (audit.table_name, audit.operation, audit.record_id) == ("facture_client", "INSERT", "42")
    assert audit.utilisateur == "admin@example.com"
    assert audit.ancienne_valeur is None
    assert audit.nouvelle_valeur["montant_honoraires_ht"] == "13500.01"
    assert audit.contexte["id_utilisateur"] == 1
    assert audit.contexte["id_paiement"] == 8
    assert audit.contexte["date_reception_honoraires"] == "2025-01-02"
    json.dumps(audit.nouvelle_valeur)
    s.db.commit.assert_called_once()
    calls = [c[0] for c in s.db.method_calls]
    assert calls.index("add") < calls.index("commit")
    s.db.rollback.assert_not_called()
    s.parameters.montant_fixe = Decimal("9999")
    assert invoice.montant_fixe_applique == Decimal("3000.00")
    assert invoice.montant_honoraires_ht == Decimal("13500.01")


@pytest.mark.parametrize("state", ["RECU", "VERIFIE", "PROGRAMME", "PAYE"])
def test_received_payment_states_allow_invoice(scenario, state):
    scenario.payment.statut = state
    assert issue(scenario).id_vente == 100


@pytest.mark.parametrize("missing", ["sale", "parameters", "payment"])
def test_missing_prerequisites_roll_back(scenario, missing):
    s = scenario
    if missing == "sale":
        s.service.repository.get_sale_context.return_value = None
    elif missing == "parameters":
        s.service.honoraires.get_effective.return_value = None
    else:
        s.service.repository.get_payment_for_update.return_value = None
    with pytest.raises(FactureClientNotFoundError if missing == "sale" else FactureClientValidationError):
        issue(s)
    s.db.rollback.assert_called_once()
    s.db.commit.assert_not_called()
    s.service.repository.create.assert_not_called()


def test_duplicate_precheck(scenario):
    scenario.service.repository.get_by_vente.return_value = object()
    with pytest.raises(FactureClientAlreadyExistsError):
        issue(scenario)
    scenario.service.repository.create.assert_not_called()


@pytest.mark.parametrize("field,value", [
    ("statut", "ATTENDU"), ("statut", "ANNULE"),
    ("date_reception_honoraires", None), ("date_reception_honoraires", date(2024, 1, 1)),
    ("date_reception_honoraires", date(9999, 1, 1)),
    ("id_mandat", 99), ("date_acte_authentique", date(2024, 1, 1)),
    ("montant_achat", Decimal("1")), ("id_parametres_honoraires", 99),
    ("montant_honoraires", Decimal("1")),
])
def test_invalid_receipt_or_snapshot_rejected(scenario, field, value):
    setattr(scenario.payment, field, value)
    with pytest.raises(FactureClientValidationError):
        issue(scenario)
    scenario.db.commit.assert_not_called()
    scenario.service.repository.create.assert_not_called()


def test_future_deed_is_rejected(scenario):
    scenario.sale.date_acte_authentique = date.today() + timedelta(days=1)
    with pytest.raises(FactureClientValidationError, match="deed"):
        issue(scenario)


def test_valid_sale_and_parameters_cannot_overflow_invoice_amount(scenario):
    scenario.sale.montant_achat = Decimal("999999999999.99")
    scenario.parameters.taux_pourcentage = Decimal("1")
    with pytest.raises(FactureClientValidationError, match="precision"):
        issue(scenario)
    scenario.service.repository.create.assert_not_called()


@pytest.mark.parametrize("constraint,expected", [
    ("uq_facture_client_vente", FactureClientAlreadyExistsError),
    ("uq_facture_client_numero", FactureClientAlreadyExistsError),
    ("fk_facture_client_client", FactureClientValidationError),
])
def test_database_race_or_integrity_failure_is_translated(scenario, constraint, expected):
    original = Exception("database constraint")
    original.diag = SimpleNamespace(constraint_name=constraint)
    scenario.service.repository.create.side_effect = IntegrityError("insert", {}, original)
    with pytest.raises(expected):
        issue(scenario)
    scenario.db.rollback.assert_called_once()
    scenario.db.commit.assert_not_called()


@pytest.mark.parametrize("stage", ["read", "create", "audit", "commit"])
def test_unexpected_failure_rolls_back_invoice_and_audit(scenario, stage):
    s = scenario
    target = {"read": s.service.repository.get_sale_context,
              "create": s.service.repository.create,
              "audit": s.db.add, "commit": s.db.commit}[stage]
    target.side_effect = RuntimeError("unavailable")
    with pytest.raises(RuntimeError, match="unavailable"):
        issue(s)
    s.db.rollback.assert_called_once()


def test_scoped_get_and_list_and_not_found(scenario):
    service = scenario.service
    service.repository.get_by_id.return_value = None
    with pytest.raises(FactureClientNotFoundError, match="Resource not found"):
        service.get_facture(42, client_id=35)
    service.repository.get_by_id.assert_called_with(42, client_id=35, chasseur_id=None)
    sentinel = object()
    service.repository.get_by_id.return_value = sentinel
    assert service.get_facture(42, chasseur_id=3) is sentinel
    service.list_factures(chasseur_id=3)
    service.repository.list_accessible.assert_called_with(client_id=None, chasseur_id=3)
