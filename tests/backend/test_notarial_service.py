from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.api.schemas.notaire import DossierNotarialCreate, MouvementNotarialCreate, NotaireCreate, SignatureNotariale
from src.api.services.notaire import NotaireService, NotarialConflictError, NotarialNotFoundError, NotarialValidationError


@pytest.fixture
def scenario(monkeypatch):
    service = NotaireService(MagicMock())
    service.repository = MagicMock()
    service.audit = MagicMock()
    dossier = SimpleNamespace(id_dossier_notarial=1, id_notaire=2, id_offre=3, id_vente=4,
        date_rendez_vous=datetime(2025, 1, 1, tzinfo=timezone.utc), reference_acte="ACT-1",
        reference_document="archive/act-1", date_creation=datetime.now(timezone.utc))
    payment = SimpleNamespace(id_paiement=5, id_vente=4, statut="ATTENDU",
        montant_honoraires=Decimal("1000.00"), date_acte_authentique=date(2025, 1, 2))
    offer = SimpleNamespace(statut="ACCEPTEE", id_presentation=6,
                            date_decision=datetime(2024, 12, 31, tzinfo=timezone.utc))
    service.repository.dossier.return_value = dossier
    service.repository.payment.return_value = payment
    service.repository.offer_context.return_value = (offer, 7)
    movements = []
    service.repository.movements.return_value = movements

    def add(record):
        record.date_creation = datetime.now(timezone.utc)
        table = record.__tablename__
        setattr(record, "id_" + table, 10)
        if table == "mouvement_notarial":
            movements.append(record)
        return record
    service.repository.add.side_effect = add
    transition = MagicMock()
    monkeypatch.setattr("src.api.services.notaire.PaiementService", lambda session: transition)
    sale_service = MagicMock()
    sale_service.create_vente.return_value = SimpleNamespace(id_vente=4)
    monkeypatch.setattr("src.api.services.notaire.VenteService", lambda session: sale_service)
    return SimpleNamespace(service=service, dossier=dossier, payment=payment, offer=offer,
                           movements=movements, transition=transition, sale_service=sale_service)


def record(s, nature="COLLECTE_NOTAIRE", amount="1000.00", ref="collect-1", day=3):
    return s.service.record_movement(1, MouvementNotarialCreate(
        nature=nature, montant=amount, date_operation=date(2025, 1, day), reference=ref,
    ), utilisateur="admin@example.com")


def test_collection_partial_receipts_and_full_receipt_are_distinct(scenario):
    s = scenario
    record(s)
    s.transition.transition.assert_not_called()
    record(s, "RECEPTION_ENTREPRISE", "400", "receipt-1", 4)
    s.transition.transition.assert_not_called()
    record(s, "RECEPTION_ENTREPRISE", "600", "receipt-2", 5)
    s.transition.transition.assert_called_once_with(5, statut_cible="RECU", utilisateur="admin@example.com",
                                                    date_reception_honoraires=date(2025, 1, 5), commit=False)
    assert s.service.audit.log_change.call_count == 3
    assert s.service.session.commit.call_count == 3


def test_retry_is_idempotent_even_after_full_receipt(scenario):
    s = scenario
    record(s)
    received = record(s, "RECEPTION_ENTREPRISE", ref="receipt-1", day=4)
    s.payment.statut = "RECU"
    assert record(s, "RECEPTION_ENTREPRISE", ref="receipt-1", day=4) is received
    assert len(s.movements) == 2
    assert s.transition.transition.call_count == 1


@pytest.mark.parametrize("nature,amount", [("RECEPTION_ENTREPRISE", "1"), ("COLLECTE_NOTAIRE", "1000.01")])
def test_over_collection_and_unbacked_receipt_are_rejected(scenario, nature, amount):
    with pytest.raises(NotarialValidationError):
        record(scenario, nature, amount)
    scenario.service.session.rollback.assert_called_once()
    scenario.service.session.commit.assert_not_called()


def test_conflicting_retry_and_backdating_fail(scenario):
    record(scenario, day=4)
    with pytest.raises(NotarialConflictError):
        record(scenario, amount="10", day=4)
    with pytest.raises(NotarialValidationError, match="chronological"):
        record(scenario, "RECEPTION_ENTREPRISE", "10", "earlier", 3)


@pytest.mark.parametrize("case", ["unsigned", "no_payment", "cancelled", "before_deed"])
def test_movement_prerequisites(scenario, case):
    if case == "unsigned": scenario.dossier.id_vente = None
    if case == "no_payment": scenario.service.repository.payment.return_value = None
    if case == "cancelled": scenario.payment.statut = "ANNULE"
    with pytest.raises((NotarialValidationError, NotarialConflictError)):
        record(scenario, day=1 if case == "before_deed" else 3)


def test_signature_creates_sale_inside_dossier_transaction(scenario):
    s = scenario
    s.dossier.id_vente = None
    signed = s.service.sign(1, SignatureNotariale(date_acte_authentique=date(2025, 1, 2),
        montant_achat="200000", reference_acte="ACT-2", reference_document="archive/act-2"), utilisateur="admin")
    assert signed.id_vente == 4
    assert signed.reference_acte == "ACT-2"
    kwargs = s.sale_service.create_vente.call_args.kwargs
    assert kwargs == {"utilisateur": "admin", "commit": False}
    s.service.session.commit.assert_called_once()
    with pytest.raises(NotarialConflictError):
        s.service.sign(1, MagicMock(), utilisateur="admin")


@pytest.mark.parametrize("case", ["future", "before_appointment", "not_accepted", "no_mandate"])
def test_invalid_signature(scenario, case):
    s = scenario
    s.dossier.id_vente = None
    if case == "not_accepted": s.offer.statut = "REFUSEE"
    if case == "no_mandate": s.service.repository.offer_context.return_value = (s.offer, None)
    day = date(2099, 1, 1) if case == "future" else date(2024, 1, 1) if case == "before_appointment" else date(2025, 1, 2)
    with pytest.raises(NotarialValidationError):
        s.service.sign(1, SignatureNotariale(date_acte_authentique=day, montant_achat="200000",
            reference_acte="ACT-2", reference_document="archive/act-2"), utilisateur="admin")
    s.service.session.commit.assert_not_called()


def test_create_entities_audits_and_reports_missing_resources(scenario):
    s = scenario
    n = s.service.create_notaire(NotaireCreate(nom="Notary", office="Office", email="notary@example.com"), utilisateur="admin")
    assert n.nom == "Notary"
    d = s.service.create_dossier(DossierNotarialCreate(id_notaire=2, id_offre=3,
        date_rendez_vous=datetime(2025, 1, 1, tzinfo=timezone.utc)), utilisateur="admin")
    assert d.id_vente is None
    s.service.repository.dossier.return_value = None
    with pytest.raises(NotarialNotFoundError): s.service.get_dossier(999)
    s.service.session.get.return_value = None
    with pytest.raises(NotarialNotFoundError):
        s.service.create_dossier(DossierNotarialCreate(id_notaire=2, id_offre=3,
            date_rendez_vous=datetime(2025, 1, 1, tzinfo=timezone.utc)), utilisateur="admin")


def test_failed_ledger_insert_rolls_back_and_does_not_receive_payment(scenario):
    scenario.service.repository.add.side_effect = IntegrityError("insert", {}, Exception("constraint"))
    with pytest.raises(NotarialConflictError): record(scenario)
    scenario.service.session.rollback.assert_called_once()
    scenario.transition.transition.assert_not_called()
