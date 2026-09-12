from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.api.services.paiement import (
    PaiementNotFoundError,
    PaiementService,
    PaiementTransitionError,
    PaiementValidationError,
)


def make_paiement(
    *,
    statut="ATTENDU",
    droit_remuneration=True,
    date_acte_authentique=date(2026, 9, 1),
    date_reception_honoraires=None,
    date_paiement_chasseur=None,
):
    return SimpleNamespace(
        id_paiement=10,
        id_vente=100,
        id_mandat=20,
        id_chasseur_beneficiaire=1,
        droit_remuneration=droit_remuneration,
        statut=statut,
        date_acte_authentique=(
            date_acte_authentique
        ),
        date_reception_honoraires=(
            date_reception_honoraires
        ),
        date_paiement_chasseur=(
            date_paiement_chasseur
        ),
    )


def make_service(
    paiement=None,
):
    session = MagicMock()

    service = PaiementService(
        session
    )

    service.repository = MagicMock()
    service.audit = MagicMock()

    service.repository.get_by_id_for_update.return_value = (
        paiement
    )

    return (
        service,
        session,
    )


def test_missing_paiement_raises_not_found():
    service, _ = make_service(
        paiement=None
    )

    with pytest.raises(
        PaiementNotFoundError
    ):
        service.transition(
            999,
            statut_cible="RECU",
            utilisateur="admin@example.com",
            date_reception_honoraires=(
                date(2026, 9, 5)
            ),
        )


def test_attendu_to_recu_sets_reception_date_and_audits():
    paiement = make_paiement(
        statut="ATTENDU"
    )

    service, session = make_service(
        paiement=paiement
    )

    result = service.transition(
        10,
        statut_cible="RECU",
        utilisateur="admin@example.com",
        date_reception_honoraires=(
            date(2026, 9, 5)
        ),
    )

    assert result.statut == "RECU"

    assert (
        result.date_reception_honoraires
        == date(2026, 9, 5)
    )

    service.audit.log_change.assert_called_once()

    kwargs = (
        service.audit
        .log_change
        .call_args
        .kwargs
    )

    assert kwargs["table_name"] == "paiement"
    assert kwargs["operation"] == "UPDATE"
    assert kwargs["utilisateur"] == (
        "admin@example.com"
    )

    assert (
        kwargs["ancienne_valeur"]["statut"]
        == "ATTENDU"
    )

    assert (
        kwargs["nouvelle_valeur"]["statut"]
        == "RECU"
    )

    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(
        paiement
    )


def test_recu_to_verifie():
    paiement = make_paiement(
        statut="RECU",
        date_reception_honoraires=(
            date(2026, 9, 5)
        ),
    )

    service, _ = make_service(
        paiement=paiement
    )

    result = service.transition(
        10,
        statut_cible="VERIFIE",
        utilisateur="admin@example.com",
    )

    assert result.statut == "VERIFIE"


def test_verifie_to_programme():
    paiement = make_paiement(
        statut="VERIFIE",
        date_reception_honoraires=(
            date(2026, 9, 5)
        ),
    )

    service, _ = make_service(
        paiement=paiement
    )

    result = service.transition(
        10,
        statut_cible="PROGRAMME",
        utilisateur="admin@example.com",
    )

    assert result.statut == "PROGRAMME"


def test_programme_to_paye_sets_payment_date():
    paiement = make_paiement(
        statut="PROGRAMME",
        date_reception_honoraires=(
            date(2026, 9, 5)
        ),
    )

    service, _ = make_service(
        paiement=paiement
    )

    result = service.transition(
        10,
        statut_cible="PAYE",
        utilisateur="admin@example.com",
        date_paiement_chasseur=(
            date(2026, 9, 10)
        ),
    )

    assert result.statut == "PAYE"

    assert (
        result.date_paiement_chasseur
        == date(2026, 9, 10)
    )


def test_invalid_transition_is_rejected():
    paiement = make_paiement(
        statut="ATTENDU"
    )

    service, session = make_service(
        paiement=paiement
    )

    with pytest.raises(
        PaiementTransitionError
    ):
        service.transition(
            10,
            statut_cible="PAYE",
            utilisateur="admin@example.com",
            date_paiement_chasseur=(
                date(2026, 9, 10)
            ),
        )

    session.commit.assert_not_called()


def test_terminal_paye_cannot_transition():
    paiement = make_paiement(
        statut="PAYE",
        date_reception_honoraires=(
            date(2026, 9, 5)
        ),
        date_paiement_chasseur=(
            date(2026, 9, 10)
        ),
    )

    service, _ = make_service(
        paiement=paiement
    )

    with pytest.raises(
        PaiementTransitionError
    ):
        service.transition(
            10,
            statut_cible="ANNULE",
            utilisateur="admin@example.com",
            motif_annulation="duplicate",
        )


def test_terminal_annule_cannot_transition():
    paiement = make_paiement(
        statut="ANNULE"
    )

    service, _ = make_service(
        paiement=paiement
    )

    with pytest.raises(
        PaiementTransitionError
    ):
        service.transition(
            10,
            statut_cible="RECU",
            utilisateur="admin@example.com",
            date_reception_honoraires=(
                date(2026, 9, 5)
            ),
        )


def test_recu_requires_reception_date():
    paiement = make_paiement(
        statut="ATTENDU"
    )

    service, _ = make_service(
        paiement=paiement
    )

    with pytest.raises(
        PaiementValidationError
    ):
        service.transition(
            10,
            statut_cible="RECU",
            utilisateur="admin@example.com",
        )


def test_reception_date_cannot_precede_deed():
    paiement = make_paiement(
        statut="ATTENDU"
    )

    service, _ = make_service(
        paiement=paiement
    )

    with pytest.raises(
        PaiementValidationError
    ):
        service.transition(
            10,
            statut_cible="RECU",
            utilisateur="admin@example.com",
            date_reception_honoraires=(
                date(2026, 8, 31)
            ),
        )


def test_paye_requires_payment_date():
    paiement = make_paiement(
        statut="PROGRAMME",
        date_reception_honoraires=(
            date(2026, 9, 5)
        ),
    )

    service, _ = make_service(
        paiement=paiement
    )

    with pytest.raises(
        PaiementValidationError
    ):
        service.transition(
            10,
            statut_cible="PAYE",
            utilisateur="admin@example.com",
        )


def test_payment_date_cannot_precede_reception():
    paiement = make_paiement(
        statut="PROGRAMME",
        date_reception_honoraires=(
            date(2026, 9, 5)
        ),
    )

    service, _ = make_service(
        paiement=paiement
    )

    with pytest.raises(
        PaiementValidationError
    ):
        service.transition(
            10,
            statut_cible="PAYE",
            utilisateur="admin@example.com",
            date_paiement_chasseur=(
                date(2026, 9, 4)
            ),
        )


def test_cancellation_requires_reason():
    paiement = make_paiement(
        statut="ATTENDU"
    )

    service, _ = make_service(
        paiement=paiement
    )

    with pytest.raises(
        PaiementValidationError
    ):
        service.transition(
            10,
            statut_cible="ANNULE",
            utilisateur="admin@example.com",
        )


def test_attendu_can_be_cancelled():
    paiement = make_paiement(
        statut="ATTENDU"
    )

    service, _ = make_service(
        paiement=paiement
    )

    result = service.transition(
        10,
        statut_cible="ANNULE",
        utilisateur="admin@example.com",
        motif_annulation=(
            "Cancellation validated"
        ),
    )

    assert result.statut == "ANNULE"

    kwargs = (
        service.audit
        .log_change
        .call_args
        .kwargs
    )

    assert (
        kwargs["contexte"][
            "motif_annulation"
        ]
        == "Cancellation validated"
    )


def test_no_entitlement_can_only_be_cancelled():
    paiement = make_paiement(
        statut="ATTENDU",
        droit_remuneration=False,
    )

    service, _ = make_service(
        paiement=paiement
    )

    with pytest.raises(
        PaiementTransitionError
    ):
        service.transition(
            10,
            statut_cible="RECU",
            utilisateur="admin@example.com",
            date_reception_honoraires=(
                date(2026, 9, 5)
            ),
        )


def test_no_entitlement_can_be_cancelled():
    paiement = make_paiement(
        statut="ATTENDU",
        droit_remuneration=False,
    )

    service, _ = make_service(
        paiement=paiement
    )

    result = service.transition(
        10,
        statut_cible="ANNULE",
        utilisateur="admin@example.com",
        motif_annulation=(
            "No remuneration entitlement"
        ),
    )

    assert result.statut == "ANNULE"


def test_same_status_is_idempotent():
    paiement = make_paiement(
        statut="VERIFIE",
        date_reception_honoraires=(
            date(2026, 9, 5)
        ),
    )

    service, session = make_service(
        paiement=paiement
    )

    result = service.transition(
        10,
        statut_cible="VERIFIE",
        utilisateur="admin@example.com",
    )

    assert result is paiement

    service.audit.log_change.assert_not_called()
    session.commit.assert_not_called()