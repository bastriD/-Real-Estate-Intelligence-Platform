from decimal import Decimal

import pytest

from src.api.services.remuneration_calculator import (
    PerformanceScores,
    PerformanceWeights,
    RemunerationCalculationError,
    RemunerationCalculationInput,
    calculate_company_fees,
    calculate_final_rate,
    calculate_performance_modulation,
    calculate_performance_score,
    calculate_remuneration,
    calculate_seniority_bonus,
)


def test_calculate_company_fees_reference_example():
    result = calculate_company_fees(
        montant_achat=Decimal("420000"),
        montant_fixe=Decimal("3000"),
        taux_pourcentage=Decimal("0.025"),
    )

    assert result == Decimal("13500.00")


def test_calculate_company_fees_rounds_half_up():
    result = calculate_company_fees(
        montant_achat=Decimal("100.20"),
        montant_fixe=Decimal("0"),
        taux_pourcentage=Decimal("0.025"),
    )

    assert result == Decimal("2.51")


def test_calculate_company_fees_rejects_non_positive_purchase_price():
    with pytest.raises(
        RemunerationCalculationError,
        match="montant_achat must be greater than 0",
    ):
        calculate_company_fees(
            montant_achat=Decimal("0"),
            montant_fixe=Decimal("3000"),
            taux_pourcentage=Decimal("0.025"),
        )


def test_calculate_company_fees_rejects_negative_fixed_amount():
    with pytest.raises(
        RemunerationCalculationError,
        match="montant_fixe must be greater than or equal to 0",
    ):
        calculate_company_fees(
            montant_achat=Decimal("420000"),
            montant_fixe=Decimal("-1"),
            taux_pourcentage=Decimal("0.025"),
        )


def test_calculate_company_fees_rejects_invalid_percentage():
    with pytest.raises(
        RemunerationCalculationError,
        match="taux_pourcentage must be between 0 and 1",
    ):
        calculate_company_fees(
            montant_achat=Decimal("420000"),
            montant_fixe=Decimal("3000"),
            taux_pourcentage=Decimal("1.01"),
        )


def test_calculate_performance_score_reference_example():
    scores = PerformanceScores(
        delai=Decimal("80"),
        exclusivite=Decimal("100"),
        ventes=Decimal("60"),
        mandats=Decimal("70"),
        visites=Decimal("72"),
    )

    weights = PerformanceWeights(
        delai=Decimal("0.25"),
        exclusivite=Decimal("0.10"),
        ventes=Decimal("0.25"),
        mandats=Decimal("0.15"),
        visites=Decimal("0.25"),
    )

    result = calculate_performance_score(
        scores=scores,
        weights=weights,
    )

    assert result == Decimal("73.5")


def test_calculate_performance_score_requires_weights_sum_to_one():
    scores = PerformanceScores(
        delai=Decimal("80"),
        exclusivite=Decimal("100"),
        ventes=Decimal("60"),
        mandats=Decimal("70"),
        visites=Decimal("72"),
    )

    weights = PerformanceWeights(
        delai=Decimal("0.20"),
        exclusivite=Decimal("0.10"),
        ventes=Decimal("0.25"),
        mandats=Decimal("0.15"),
        visites=Decimal("0.25"),
    )

    with pytest.raises(
        RemunerationCalculationError,
        match="Performance weights must sum to 1",
    ):
        calculate_performance_score(
            scores=scores,
            weights=weights,
        )


@pytest.mark.parametrize(
    ("field_name", "scores"),
    [
        (
            "scores.delai",
            PerformanceScores(
                delai=Decimal("-1"),
                exclusivite=Decimal("100"),
                ventes=Decimal("60"),
                mandats=Decimal("70"),
                visites=Decimal("72"),
            ),
        ),
        (
            "scores.exclusivite",
            PerformanceScores(
                delai=Decimal("80"),
                exclusivite=Decimal("101"),
                ventes=Decimal("60"),
                mandats=Decimal("70"),
                visites=Decimal("72"),
            ),
        ),
    ],
)
def test_calculate_performance_score_rejects_invalid_scores(
    field_name,
    scores,
):
    weights = PerformanceWeights(
        delai=Decimal("0.25"),
        exclusivite=Decimal("0.10"),
        ventes=Decimal("0.25"),
        mandats=Decimal("0.15"),
        visites=Decimal("0.25"),
    )

    with pytest.raises(
        RemunerationCalculationError,
        match=f"{field_name} must be between 0 and 100",
    ):
        calculate_performance_score(
            scores=scores,
            weights=weights,
        )


def test_calculate_seniority_bonus():
    result = calculate_seniority_bonus(
        annees_anciennete=3,
        taux_par_annee=Decimal("0.02"),
        plafond=Decimal("0.10"),
    )

    assert result == Decimal("0.06")


def test_calculate_seniority_bonus_is_capped():
    result = calculate_seniority_bonus(
        annees_anciennete=8,
        taux_par_annee=Decimal("0.02"),
        plafond=Decimal("0.10"),
    )

    assert result == Decimal("0.10")


def test_calculate_seniority_bonus_rejects_negative_years():
    with pytest.raises(
        RemunerationCalculationError,
        match="annees_anciennete must be greater than or equal to 0",
    ):
        calculate_seniority_bonus(
            annees_anciennete=-1,
            taux_par_annee=Decimal("0.02"),
            plafond=Decimal("0.10"),
        )


def test_calculate_performance_modulation_reference_example():
    result = calculate_performance_modulation(
        score_performance=Decimal("73.5"),
        score_pivot=Decimal("50"),
        amplitude=Decimal("0.20"),
    )

    assert result == Decimal("0.094")


def test_calculate_performance_modulation_is_negative_below_pivot():
    result = calculate_performance_modulation(
        score_performance=Decimal("25"),
        score_pivot=Decimal("50"),
        amplitude=Decimal("0.20"),
    )

    assert result == Decimal("-0.10")


def test_calculate_final_rate_reference_example():
    result = calculate_final_rate(
        taux_base=Decimal("0.40"),
        majoration_anciennete=Decimal("0.06"),
        modulation_performance=Decimal("0.094"),
        taux_plancher=Decimal("0.20"),
        taux_plafond=Decimal("0.60"),
    )

    assert result == Decimal("0.4616")


def test_calculate_final_rate_applies_floor():
    result = calculate_final_rate(
        taux_base=Decimal("0.20"),
        majoration_anciennete=Decimal("0"),
        modulation_performance=Decimal("-0.50"),
        taux_plancher=Decimal("0.20"),
        taux_plafond=Decimal("0.60"),
    )

    assert result == Decimal("0.2000")


def test_calculate_final_rate_applies_ceiling():
    result = calculate_final_rate(
        taux_base=Decimal("0.60"),
        majoration_anciennete=Decimal("0.10"),
        modulation_performance=Decimal("0.20"),
        taux_plancher=Decimal("0.20"),
        taux_plafond=Decimal("0.60"),
    )

    assert result == Decimal("0.6000")


def test_calculate_final_rate_rejects_inverted_bounds():
    with pytest.raises(
        RemunerationCalculationError,
        match="taux_plancher cannot exceed taux_plafond",
    ):
        calculate_final_rate(
            taux_base=Decimal("0.40"),
            majoration_anciennete=Decimal("0.06"),
            modulation_performance=Decimal("0.094"),
            taux_plancher=Decimal("0.70"),
            taux_plafond=Decimal("0.60"),
        )


def test_calculate_remuneration_reference_example():
    calculation_input = RemunerationCalculationInput(
        montant_achat=Decimal("420000"),
        montant_fixe_honoraires=Decimal("3000"),
        taux_honoraires=Decimal("0.025"),
        scores=PerformanceScores(
            delai=Decimal("80"),
            exclusivite=Decimal("100"),
            ventes=Decimal("60"),
            mandats=Decimal("70"),
            visites=Decimal("72"),
        ),
        weights=PerformanceWeights(
            delai=Decimal("0.25"),
            exclusivite=Decimal("0.10"),
            ventes=Decimal("0.25"),
            mandats=Decimal("0.15"),
            visites=Decimal("0.25"),
        ),
        taux_base=Decimal("0.40"),
        annees_anciennete=3,
        taux_anciennete_par_annee=Decimal("0.02"),
        plafond_anciennete=Decimal("0.10"),
        score_pivot=Decimal("50"),
        amplitude_performance=Decimal("0.20"),
        taux_plancher=Decimal("0.20"),
        taux_plafond=Decimal("0.60"),
    )

    result = calculate_remuneration(
        calculation_input
    )

    assert result.montant_achat == Decimal("420000.00")
    assert result.montant_honoraires == Decimal("13500.00")
    assert result.score_performance == Decimal("73.5")

    assert result.taux_base == Decimal("0.4000")
    assert result.majoration_anciennete == Decimal("0.0600")
    assert result.modulation_performance == Decimal("0.0940")
    assert result.taux_final == Decimal("0.4616")

    assert result.montant_chasseur == Decimal("6231.60")