from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.api.services.remuneration import (
    RemunerationAlreadyCalculatedError,
    RemunerationConfigurationError,
    RemunerationDataError,
    RemunerationNotFoundError,
    RemunerationService,
)


def make_service():
    session = MagicMock()
    service = RemunerationService(session)

    service.vente_repository = MagicMock()
    service.paiement_repository = MagicMock()
    service.honoraires_repository = MagicMock()
    service.remuneration_repository = MagicMock()
    service.palier_repository = MagicMock()
    service.bareme_repository = MagicMock()
    service.audit = MagicMock()

    return service, session


def make_vente(
    *,
    beneficiary=1,
    period_id=10,
    origine="CHASSEUR",
):
    return SimpleNamespace(
        id_vente=100,
        id_mandat=20,
        id_mandat_periode=period_id,
        id_presentation=30,
        id_bien=40,
        id_chasseur_beneficiaire=beneficiary,
        origine_vente=origine,
        date_acte_authentique=date(2026, 9, 1),
        montant_achat=Decimal("420000.00"),
    )


def make_mandat(
    *,
    type_mandat="EXCLUSIF",
):
    return SimpleNamespace(
        id_mandat=20,
        type_mandat=type_mandat,
        date_debut=date(2026, 1, 1),
        date_signature=date(2026, 1, 1),
        id_chasseur=1,
    )


def make_honoraires():
    return SimpleNamespace(
        id_parametres_honoraires=1,
        montant_fixe=Decimal("3000.00"),
        taux_pourcentage=Decimal("0.0250"),
    )


def make_remuneration_parameters():
    return SimpleNamespace(
        id_parametres_remuneration=2,
        fenetre_mois=12,
        poids_delai=Decimal("0.25"),
        poids_exclusivite=Decimal("0.10"),
        poids_ventes=Decimal("0.25"),
        poids_mandats=Decimal("0.15"),
        poids_visites=Decimal("0.25"),
        note_exclusif=Decimal("100"),
        note_non_exclusif=Decimal("60"),
        points_par_vente=Decimal("20"),
        points_par_mandat=Decimal("10"),
        taux_anciennete_par_annee=Decimal("0.02"),
        plafond_anciennete=Decimal("0.10"),
        score_pivot=Decimal("50"),
        amplitude_performance=Decimal("0.20"),
        taux_plancher=Decimal("0.20"),
        taux_plafond=Decimal("0.60"),
    )


def make_bareme():
    return SimpleNamespace(
        id_bareme=3,
        taux_commission=Decimal("0.40"),
    )


def make_chasseur():
    return SimpleNamespace(
        id_chasseur=1,
        date_entree=date(2021, 1, 1),
    )


def make_created_paiement(
    *,
    vente,
    paiement_id=50,
    beneficiary=None,
    droit=False,
    motif=None,
    montant_honoraires=Decimal("13500.00"),
    montant_chasseur=Decimal("0.00"),
):
    return SimpleNamespace(
        id_paiement=paiement_id,
        id_vente=vente.id_vente,
        id_mandat=vente.id_mandat,
        id_chasseur_beneficiaire=beneficiary,
        id_bareme=None,
        id_parametres_honoraires=1,
        id_parametres_remuneration=None,
        date_acte_authentique=vente.date_acte_authentique,
        date_calcul=None,
        montant_achat=vente.montant_achat,
        montant_honoraires=montant_honoraires,
        montant_chasseur=montant_chasseur,
        droit_remuneration=droit,
        motif_refus=motif,
        semaines_mandat_acte=34,
        nb_visites_calcul=None,
        annees_anciennete_calcul=None,
        nb_ventes_fenetre=None,
        nb_mandats_fenetre=None,
        note_delai=None,
        note_exclusivite=None,
        note_ventes=None,
        note_mandats=None,
        note_visites=None,
        score_performance=None,
        taux_base=None,
        majoration_anciennete=None,
        modulation_performance=None,
        taux_final=None,
        statut="ATTENDU",
    )


def test_calculate_for_vente_fails_when_vente_missing():
    service, _ = make_service()

    service.vente_repository.get_by_id.return_value = None

    with pytest.raises(
        RemunerationNotFoundError
    ):
        service.calculate_for_vente(
            999
        )


def test_calculate_for_vente_rejects_duplicate():
    service, _ = make_service()

    vente = make_vente()

    service.vente_repository.get_by_id.return_value = vente

    service.paiement_repository.get_by_vente.return_value = (
        SimpleNamespace(
            id_paiement=1
        )
    )

    with pytest.raises(
        RemunerationAlreadyCalculatedError
    ):
        service.calculate_for_vente(
            vente.id_vente
        )


def test_missing_fee_parameters_fails():
    service, session = make_service()

    vente = make_vente()
    mandat = make_mandat()

    service.vente_repository.get_by_id.return_value = vente

    service.paiement_repository.get_by_vente.return_value = None

    service.honoraires_repository.get_effective.return_value = None

    session.scalar.return_value = mandat

    with pytest.raises(
        RemunerationConfigurationError
    ):
        service.calculate_for_vente(
            vente.id_vente
        )


def test_no_entitlement_expired_mandate():
    service, session = make_service()

    vente = make_vente(
        beneficiary=None,
        period_id=None,
    )

    mandat = make_mandat()
    honoraires = make_honoraires()

    service.vente_repository.get_by_id.return_value = vente

    service.paiement_repository.get_by_vente.return_value = None

    service.honoraires_repository.get_effective.return_value = (
        honoraires
    )

    session.scalar.return_value = mandat

    created = make_created_paiement(
        vente=vente,
        paiement_id=50,
        beneficiary=None,
        droit=False,
        motif="MANDAT_EXPIRE",
    )

    service.paiement_repository.create.return_value = created

    result = service.calculate_for_vente(
        vente.id_vente
    )

    assert result.droit_remuneration is False
    assert result.motif_refus == "MANDAT_EXPIRE"
    assert result.montant_chasseur == Decimal("0.00")

    service.paiement_repository.create.assert_called_once()

    session.commit.assert_called_once()


def test_no_entitlement_outside_dispositif():
    service, session = make_service()

    vente = make_vente(
        beneficiary=None,
        period_id=10,
        origine="CLIENT_SEUL",
    )

    mandat = make_mandat(
        type_mandat="NON_EXCLUSIF",
    )

    honoraires = make_honoraires()

    service.vente_repository.get_by_id.return_value = vente

    service.paiement_repository.get_by_vente.return_value = None

    service.honoraires_repository.get_effective.return_value = (
        honoraires
    )

    session.scalar.return_value = mandat

    created = make_created_paiement(
        vente=vente,
        paiement_id=51,
        beneficiary=None,
        droit=False,
        motif="HORS_DISPOSITIF",
    )

    service.paiement_repository.create.return_value = created

    result = service.calculate_for_vente(
        vente.id_vente
    )

    assert result.droit_remuneration is False
    assert result.motif_refus == "HORS_DISPOSITIF"
    assert result.montant_chasseur == Decimal("0.00")

    service.paiement_repository.create.assert_called_once()

    session.commit.assert_called_once()


def test_completed_years_before_anniversary():
    result = RemunerationService._completed_years(
        date(2021, 6, 15),
        date(2026, 6, 14),
    )

    assert result == 4


def test_completed_years_on_anniversary():
    result = RemunerationService._completed_years(
        date(2021, 6, 15),
        date(2026, 6, 15),
    )

    assert result == 5


def test_completed_years_rejects_invalid_order():
    with pytest.raises(
        RemunerationDataError
    ):
        RemunerationService._completed_years(
            date(2026, 6, 15),
            date(2025, 6, 15),
        )


def test_subtract_months_regular_case():
    result = RemunerationService._subtract_months(
        date(2026, 9, 12),
        12,
    )

    assert result == date(2025, 9, 12)


def test_subtract_months_handles_end_of_month():
    result = RemunerationService._subtract_months(
        date(2026, 3, 31),
        1,
    )

    assert result == date(2026, 2, 28)


def test_subtract_months_rejects_zero_window():
    with pytest.raises(
        RemunerationConfigurationError
    ):
        RemunerationService._subtract_months(
            date(2026, 3, 31),
            0,
        )


def test_weeks_between():
    result = RemunerationService._weeks_between(
        date(2026, 1, 1),
        date(2026, 1, 15),
    )

    assert result == 2


def test_weeks_between_uses_floor_weeks():
    result = RemunerationService._weeks_between(
        date(2026, 1, 1),
        date(2026, 1, 13),
    )

    assert result == 1


def test_weeks_between_rejects_invalid_date_order():
    with pytest.raises(
        RemunerationDataError
    ):
        RemunerationService._weeks_between(
            date(2026, 2, 1),
            date(2026, 1, 1),
        )


def test_performance_note_returns_configured_note():
    service, _ = make_service()

    service.palier_repository.get_note_for_value.return_value = (
        Decimal("80")
    )

    result = service._performance_note(
        id_parametres_remuneration=1,
        critere="VISITES",
        value=5,
    )

    assert result == Decimal("80")


def test_performance_note_missing_configuration():
    service, _ = make_service()

    service.palier_repository.get_note_for_value.return_value = None

    with pytest.raises(
        RemunerationConfigurationError
    ):
        service._performance_note(
            id_parametres_remuneration=1,
            critere="VISITES",
            value=5,
        )

def test_entitled_sale_calculates_and_freezes_remuneration():
    service, session = make_service()

    vente = make_vente(
        beneficiary=1,
        period_id=10,
        origine="CHASSEUR",
    )

    mandat = make_mandat(
        type_mandat="EXCLUSIF",
    )

    honoraires = make_honoraires()
    remuneration_parameters = make_remuneration_parameters()
    bareme = make_bareme()

    chasseur = SimpleNamespace(
        id_chasseur=1,
        date_entree=date(2023, 1, 1),
    )

    service.vente_repository.get_by_id.return_value = vente
    service.paiement_repository.get_by_vente.return_value = None

    service.honoraires_repository.get_effective.return_value = (
        honoraires
    )

    service.remuneration_repository.get_effective.return_value = (
        remuneration_parameters
    )

    service.bareme_repository.get_effective_for_amount.return_value = (
        bareme
    )

    service._get_mandat = MagicMock(
        return_value=mandat
    )

    service._get_chasseur = MagicMock(
        return_value=chasseur
    )

    service._calculate_business_inputs = MagicMock(
        return_value=(
            20,  # semaines_mandat_acte
            5,   # nb_visites
            3,   # annees_anciennete
            3,   # nb_ventes
            4,   # nb_mandats
        )
    )

    def performance_note(
        *,
        id_parametres_remuneration,
        critere,
        value,
    ):
        assert id_parametres_remuneration == 2

        if critere == "DELAI_SEMAINES":
            assert value == 20
            return Decimal("80")

        if critere == "VISITES":
            assert value == 5
            return Decimal("90")

        raise AssertionError(
            f"Unexpected criterion: {critere}"
        )

    service._performance_note = MagicMock(
        side_effect=performance_note
    )

    def create_paiement(paiement):
        paiement.id_paiement = 77
        return paiement

    service.paiement_repository.create.side_effect = (
        create_paiement
    )

    result = service.calculate_for_vente(
        vente.id_vente,
        utilisateur="admin@test.local",
    )

    assert result.id_paiement == 77
    assert result.id_vente == 100
    assert result.id_mandat == 20

    assert (
        result.id_chasseur_beneficiaire
        == 1
    )

    assert result.droit_remuneration is True
    assert result.motif_refus is None

    assert (
        result.id_parametres_honoraires
        == 1
    )

    assert (
        result.id_parametres_remuneration
        == 2
    )

    assert result.id_bareme == 3

    assert result.semaines_mandat_acte == 20
    assert result.nb_visites_calcul == 5
    assert result.annees_anciennete_calcul == 3
    assert result.nb_ventes_fenetre == 3
    assert result.nb_mandats_fenetre == 4

    assert result.note_delai == Decimal("80")
    assert (
        result.note_exclusivite
        == Decimal("100")
    )
    assert result.note_ventes == Decimal("60")
    assert result.note_mandats == Decimal("40")
    assert result.note_visites == Decimal("90")

    # Weighted score:
    #
    # 80  * 0.25 = 20.0
    # 100 * 0.10 = 10.0
    # 60  * 0.25 = 15.0
    # 40  * 0.15 =  6.0
    # 90  * 0.25 = 22.5
    #
    # Total = 73.5
    assert (
        result.score_performance
        == Decimal("73.5")
    )

    # Company fees:
    #
    # 3000 + 2.5% * 420000
    # = 3000 + 10500
    # = 13500
    assert (
        result.montant_honoraires
        == Decimal("13500.00")
    )

    assert result.taux_base == Decimal("0.4000")

    # 3 completed years * 2% = 6%
    assert (
        result.majoration_anciennete
        == Decimal("0.0600")
    )

    # (73.5 - 50) / 50 * 20%
    # = 9.4%
    assert (
        result.modulation_performance
        == Decimal("0.0940")
    )

    # 40% * (1 + 6% + 9.4%)
    # = 46.16%
    assert (
        result.taux_final
        == Decimal("0.4616")
    )

    # 13,500 * 46.16%
    # = 6,231.60
    assert (
        result.montant_chasseur
        == Decimal("6231.60")
    )

    assert result.statut == "ATTENDU"

    service.paiement_repository.create.assert_called_once()

    service.audit.log_change.assert_called_once()

    session.commit.assert_called_once()