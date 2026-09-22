from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.api.repositories.paiement import PaiementRepository
from src.api.services.paiement import PaiementService, PaiementTransitionError


@pytest.mark.parametrize("total,last_date,allowed", [(Decimal("1000"), date(2025,1,3), True),
    (Decimal("400"), date(2025,1,3), False), (Decimal("1000"), date(2025,1,2), False)])
def test_receipt_requires_full_amount_and_actual_completion_date(total, last_date, allowed):
    db = MagicMock()
    db.scalar.return_value = 1
    db.execute.return_value.one.return_value = (total, last_date)
    assert PaiementRepository(db).notarial_receipt_is_complete(
        SimpleNamespace(id_vente=1, montant_honoraires=Decimal("1000")), date(2025,1,3)) is allowed


def test_legacy_sales_keep_existing_receipt_path():
    db = MagicMock()
    db.scalar.return_value = None
    assert PaiementRepository(db).notarial_receipt_is_complete(SimpleNamespace(id_vente=1), date(2025,1,3))


def test_direct_payment_transition_cannot_bypass_notarial_receipt():
    payment = SimpleNamespace(id_paiement=1, id_vente=1, id_mandat=2, id_chasseur_beneficiaire=3,
        droit_remuneration=True, statut="ATTENDU", date_acte_authentique=date(2025,1,1),
        date_reception_honoraires=None, date_paiement_chasseur=None)
    service = PaiementService(MagicMock())
    service.repository = MagicMock()
    service.repository.get_by_id_for_update.return_value = payment
    service.repository.notarial_receipt_is_complete.return_value = False
    with pytest.raises(PaiementTransitionError, match="Full company receipt"):
        service.transition(1, statut_cible="RECU", utilisateur="admin", date_reception_honoraires=date(2025,1,3))
    assert payment.statut == "ATTENDU"
    service.session.commit.assert_not_called()
