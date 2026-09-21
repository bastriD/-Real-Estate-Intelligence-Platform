"""Service invariants without connecting to a database; SQL is tested by CI test 019."""
from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.api.db.models.facture_chasseur import FactureChasseur
from src.api.schemas.facture_chasseur import FactureChasseurCreate, FactureChasseurDecision
from src.api.services.facture_chasseur import (
    FactureChasseurService, FactureChasseurConflictError,
    FactureChasseurNotFoundError, FactureChasseurValidationError,
)
from src.api.services.paiement import PaiementTransitionError


ACTOR = {"utilisateur": "actor@example.com", "id_utilisateur": 7}


def invoice(**overrides):
    values = dict(id_facture_chasseur=1, id_paiement=10, id_chasseur=3,
                  numero_version=1, numero_facture="H-2026-1", date_facture=date(2026, 1, 5),
                  montant=Decimal("3939.60"), statut="SOUMISE",
                  date_soumission=datetime(2026, 1, 6, tzinfo=timezone.utc),
                  date_verification=None, id_verificateur=None, motif_rejet=None)
    return FactureChasseur(**(values | overrides))


def setup_service(**payment_overrides):
    session = MagicMock()
    service = FactureChasseurService(session)
    service.repository = MagicMock()
    service.payments = MagicMock()
    service.audit = MagicMock()
    payment = SimpleNamespace(**(dict(
        id_paiement=10, id_vente=2, id_mandat=4, id_chasseur_beneficiaire=3,
        droit_remuneration=True, montant_chasseur=Decimal("3939.60"), statut="RECU",
        date_acte_authentique=date(2026, 1, 1), date_reception_honoraires=date(2026, 1, 5),
        date_paiement_chasseur=None,
    ) | payment_overrides))
    service.payments.get_by_id_for_update.return_value = payment
    service.repository.get_latest.return_value = None
    record = invoice()
    service.repository.get_by_id.return_value = record
    service.repository.get_by_id_for_update.return_value = record

    def create(record):
        record.id_facture_chasseur = 2
        return record

    service.repository.create.side_effect = create
    # Exercise the real payment transition service, sharing the enclosing transaction.
    service.payment_service.repository = service.payments
    service.payments.has_conforming_invoice.return_value = True
    service.payment_service.audit = MagicMock()
    return service, session, payment, record


def submit(service, **overrides):
    payload = FactureChasseurCreate(**(dict(id_paiement=10, numero_facture="H-1",
        date_facture=date(2026, 1, 5), montant=Decimal("3939.60")) | overrides))
    return service.submit(payload, chasseur_id=3, **ACTOR)


def decide(service, **overrides):
    return service.decide(1, FactureChasseurDecision(**({"statut": "CONFORME"} | overrides)), **ACTOR)


def test_submission_uses_persisted_beneficiary_and_preserves_submitted_amount():
    service, session, payment, _ = setup_service()
    record = submit(service, montant=Decimal("3900.00"))
    assert (record.id_chasseur, record.numero_version, record.statut) == (3, 1, "SOUMISE")
    assert record.montant == Decimal("3900.00")
    assert payment.montant_chasseur == Decimal("3939.60")
    assert payment.statut == "RECU"
    audit = service.audit.log_change.call_args.kwargs
    assert audit["contexte"]["montant_chasseur_attendu"] == "3939.60"
    assert audit["contexte"]["id_utilisateur"] == 7
    assert audit["nouvelle_valeur"]["numero_facture"] == "H-1"
    session.commit.assert_called_once()


@pytest.mark.parametrize("missing", [False, True])
def test_foreign_or_missing_payment_has_identical_error(missing):
    service, session, _, _ = setup_service(id_chasseur_beneficiaire=99)
    if missing:
        service.payments.get_by_id_for_update.return_value = None
    with pytest.raises(FactureChasseurNotFoundError, match="^Resource not found$"):
        submit(service)
    service.repository.create.assert_not_called()
    session.commit.assert_not_called()
    session.rollback.assert_called_once()


@pytest.mark.parametrize("overrides", [
    {"statut": "ATTENDU"}, {"statut": "PAYE"}, {"statut": "ANNULE"},
    {"droit_remuneration": False}, {"droit_remuneration": None}, {"id_vente": None},
    {"montant_chasseur": Decimal("0")}, {"montant_chasseur": None},
    {"date_reception_honoraires": None}, {"date_acte_authentique": None},
    {"date_reception_honoraires": date(2025, 12, 31)},
    {"date_reception_honoraires": date(2099, 1, 1)},
])
def test_ineligible_payment_cannot_accept_invoice(overrides):
    service, session, _, _ = setup_service(**overrides)
    with pytest.raises(FactureChasseurConflictError):
        submit(service)
    session.commit.assert_not_called()


@pytest.mark.parametrize("value", [date(2026, 1, 4), date(2099, 1, 1)])
def test_submission_rejects_invalid_business_date(value):
    service, session, _, _ = setup_service()
    with pytest.raises(FactureChasseurValidationError):
        submit(service, date_facture=value)
    session.commit.assert_not_called()


@pytest.mark.parametrize("state", ["SOUMISE", "CONFORME"])
def test_duplicate_active_invoice_is_conflict(state):
    service, session, _, _ = setup_service()
    service.repository.get_latest.return_value = invoice(statut=state)
    with pytest.raises(FactureChasseurConflictError):
        submit(service)
    session.commit.assert_not_called()


def test_rejected_submission_retained_when_next_version_submitted():
    service, _, _, _ = setup_service()
    previous = invoice(statut="REJETEE", numero_version=2, motif_rejet="Wrong amount")
    service.repository.get_latest.return_value = previous
    record = submit(service)
    assert record.numero_version == 3
    assert previous.statut == "REJETEE" and previous.motif_rejet == "Wrong amount"


@pytest.mark.parametrize("initial", ["RECU", "VERIFIE", "PROGRAMME"])
def test_conformity_programs_existing_payment_and_audits_in_one_commit(initial):
    service, session, payment, record = setup_service(statut=initial)
    assert decide(service) is record
    assert record.statut == "CONFORME" and record.id_verificateur == 7
    assert record.date_verification >= record.date_soumission
    assert payment.statut == "PROGRAMME"
    assert payment.montant_chasseur == Decimal("3939.60")
    session.commit.assert_called_once()
    decision = service.audit.log_change.call_args.kwargs
    assert decision["ancienne_valeur"]["statut"] == "SOUMISE"
    assert decision["nouvelle_valeur"]["statut"] == "CONFORME"
    events = service.payment_service.audit.log_change.call_args_list
    expected = {"RECU": ["VERIFIE", "PROGRAMME"], "VERIFIE": ["PROGRAMME"], "PROGRAMME": []}
    assert [event.kwargs["nouvelle_valeur"]["statut"] for event in events] == expected[initial]


def test_rejection_preserves_invoice_and_does_not_advance_payment():
    service, session, payment, record = setup_service()
    decide(service, statut="REJETEE", motif_rejet="Incorrect amount")
    assert record.statut == "REJETEE" and record.motif_rejet == "Incorrect amount"
    assert payment.statut == "RECU"
    service.payment_service.audit.log_change.assert_not_called()
    session.commit.assert_called_once()


@pytest.mark.parametrize("field,value", [
    ("montant", Decimal("3939.59")), ("id_chasseur", 88),
    ("date_facture", date(2025, 12, 31)), ("date_facture", date(2099, 1, 1)),
])
def test_conformity_requires_matching_snapshot(field, value):
    service, session, payment, record = setup_service()
    setattr(record, field, value)
    with pytest.raises(FactureChasseurValidationError):
        decide(service)
    assert record.statut == "SOUMISE" and payment.statut == "RECU"
    session.commit.assert_not_called()


@pytest.mark.parametrize("state", ["PAYE", "ANNULE"])
def test_terminal_payment_never_reopened(state):
    service, session, payment, _ = setup_service(statut=state)
    with pytest.raises(FactureChasseurConflictError):
        decide(service, statut="REJETEE", motif_rejet="Rejected")
    assert payment.statut == state
    session.commit.assert_not_called()


def test_review_uses_fresh_locked_invoice_state():
    service, session, _, _ = setup_service()
    service.repository.get_by_id_for_update.return_value = invoice(statut="CONFORME")
    with pytest.raises(FactureChasseurConflictError):
        decide(service)
    session.commit.assert_not_called()


@pytest.mark.parametrize("failure_at", ["invoice_audit", "payment_audit", "second_transition", "commit"])
def test_failure_never_commits_partial_decision(failure_at):
    service, session, _, _ = setup_service()
    if failure_at == "invoice_audit":
        service.audit.log_change.side_effect = RuntimeError("audit unavailable")
    elif failure_at == "payment_audit":
        service.payment_service.audit.log_change.side_effect = RuntimeError("audit unavailable")
    elif failure_at == "second_transition":
        service.payments.has_conforming_invoice.side_effect = [True, False]
    else:
        session.commit.side_effect = RuntimeError("commit failed")
    with pytest.raises((RuntimeError, FactureChasseurConflictError)):
        decide(service)
    assert session.commit.call_count == (1 if failure_at == "commit" else 0)
    assert session.rollback.called


@pytest.mark.parametrize("constraint,expected", [
    ("uq_facture_chasseur_active", FactureChasseurConflictError),
    ("uq_facture_chasseur_paiement_version", FactureChasseurConflictError),
    ("ck_facture_chasseur_montant", FactureChasseurValidationError),
])
def test_database_conflicts_roll_back(constraint, expected):
    service, session, _, _ = setup_service()
    error = IntegrityError("insert", {}, SimpleNamespace(diag=SimpleNamespace(constraint_name=constraint)))
    service.repository.create.side_effect = error
    with pytest.raises(expected):
        submit(service)
    session.rollback.assert_called_once()
    session.commit.assert_not_called()


@pytest.mark.parametrize("initial,target", [("RECU", "VERIFIE"), ("VERIFIE", "PROGRAMME"), ("PROGRAMME", "PAYE")])
def test_direct_payment_transition_cannot_bypass_conforming_invoice(initial, target):
    service, session, payment, _ = setup_service(statut=initial)
    service.payments.has_conforming_invoice.return_value = False
    kwargs = {"date_paiement_chasseur": date(2026, 1, 6)} if target == "PAYE" else {}
    with pytest.raises(PaiementTransitionError, match="conforming hunter invoice"):
        service.payment_service.transition(10, statut_cible=target, utilisateur="admin@example.com", **kwargs)
    assert payment.statut == initial
    session.commit.assert_not_called()


def test_scoped_reads_and_missing_invoice():
    service, _, _, _ = setup_service()
    service.list_factures(3)
    service.repository.list_accessible.assert_called_once_with(3)
    service.repository.get_by_id.return_value = None
    with pytest.raises(FactureChasseurNotFoundError):
        service.get_facture(99, 3)
    service.repository.get_by_id.assert_called_once_with(99, 3)
