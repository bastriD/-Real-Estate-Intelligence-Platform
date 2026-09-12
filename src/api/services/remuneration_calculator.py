from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


MONEY_QUANTUM = Decimal("0.01")
RATE_QUANTUM = Decimal("0.0001")
SCORE_QUANTUM = Decimal("0.1")

ZERO = Decimal("0")
ONE_HUNDRED = Decimal("100")


class RemunerationCalculationError(ValueError):
    pass


@dataclass(frozen=True)
class PerformanceScores:
    delai: Decimal
    exclusivite: Decimal
    ventes: Decimal
    mandats: Decimal
    visites: Decimal


@dataclass(frozen=True)
class PerformanceWeights:
    delai: Decimal
    exclusivite: Decimal
    ventes: Decimal
    mandats: Decimal
    visites: Decimal


@dataclass(frozen=True)
class RemunerationCalculationInput:
    montant_achat: Decimal

    montant_fixe_honoraires: Decimal
    taux_honoraires: Decimal

    scores: PerformanceScores
    weights: PerformanceWeights

    taux_base: Decimal

    annees_anciennete: int
    taux_anciennete_par_annee: Decimal
    plafond_anciennete: Decimal

    score_pivot: Decimal
    amplitude_performance: Decimal

    taux_plancher: Decimal
    taux_plafond: Decimal


@dataclass(frozen=True)
class RemunerationCalculationResult:
    montant_achat: Decimal
    montant_honoraires: Decimal

    score_performance: Decimal

    taux_base: Decimal
    majoration_anciennete: Decimal
    modulation_performance: Decimal
    taux_final: Decimal

    montant_chasseur: Decimal


def _quantize_money(
    value: Decimal,
) -> Decimal:
    return value.quantize(
        MONEY_QUANTUM,
        rounding=ROUND_HALF_UP,
    )


def _quantize_rate(
    value: Decimal,
) -> Decimal:
    return value.quantize(
        RATE_QUANTUM,
        rounding=ROUND_HALF_UP,
    )


def _quantize_score(
    value: Decimal,
) -> Decimal:
    return value.quantize(
        SCORE_QUANTUM,
        rounding=ROUND_HALF_UP,
    )


def _bound(
    value: Decimal,
    minimum: Decimal,
    maximum: Decimal,
) -> Decimal:
    return max(
        minimum,
        min(value, maximum),
    )


def _validate_score(
    name: str,
    value: Decimal,
) -> None:
    if value < ZERO or value > ONE_HUNDRED:
        raise RemunerationCalculationError(
            f"{name} must be between 0 and 100"
        )


def _validate_rate(
    name: str,
    value: Decimal,
) -> None:
    if value < ZERO or value > Decimal("1"):
        raise RemunerationCalculationError(
            f"{name} must be between 0 and 1"
        )


def calculate_performance_score(
    scores: PerformanceScores,
    weights: PerformanceWeights,
) -> Decimal:
    _validate_score(
        "scores.delai",
        scores.delai,
    )
    _validate_score(
        "scores.exclusivite",
        scores.exclusivite,
    )
    _validate_score(
        "scores.ventes",
        scores.ventes,
    )
    _validate_score(
        "scores.mandats",
        scores.mandats,
    )
    _validate_score(
        "scores.visites",
        scores.visites,
    )

    weight_values = (
        weights.delai,
        weights.exclusivite,
        weights.ventes,
        weights.mandats,
        weights.visites,
    )

    for weight in weight_values:
        _validate_rate(
            "performance weight",
            weight,
        )

    total_weight = sum(
        weight_values,
        ZERO,
    )

    if total_weight != Decimal("1"):
        raise RemunerationCalculationError(
            "Performance weights must sum to 1"
        )

    score = (
        scores.delai
        * weights.delai
        + scores.exclusivite
        * weights.exclusivite
        + scores.ventes
        * weights.ventes
        + scores.mandats
        * weights.mandats
        + scores.visites
        * weights.visites
    )

    return _quantize_score(
        score
    )


def calculate_company_fees(
    montant_achat: Decimal,
    montant_fixe: Decimal,
    taux_pourcentage: Decimal,
) -> Decimal:
    if montant_achat <= ZERO:
        raise RemunerationCalculationError(
            "montant_achat must be greater than 0"
        )

    if montant_fixe < ZERO:
        raise RemunerationCalculationError(
            "montant_fixe must be greater than or equal to 0"
        )

    _validate_rate(
        "taux_pourcentage",
        taux_pourcentage,
    )

    honoraires = (
        montant_fixe
        + (
            taux_pourcentage
            * montant_achat
        )
    )

    return _quantize_money(
        honoraires
    )


def calculate_seniority_bonus(
    annees_anciennete: int,
    taux_par_annee: Decimal,
    plafond: Decimal,
) -> Decimal:
    if annees_anciennete < 0:
        raise RemunerationCalculationError(
            "annees_anciennete must be greater than or equal to 0"
        )

    _validate_rate(
        "taux_par_annee",
        taux_par_annee,
    )
    _validate_rate(
        "plafond",
        plafond,
    )

    bonus = (
        Decimal(annees_anciennete)
        * taux_par_annee
    )

    return min(
        bonus,
        plafond,
    )


def calculate_performance_modulation(
    score_performance: Decimal,
    score_pivot: Decimal,
    amplitude: Decimal,
) -> Decimal:
    _validate_score(
        "score_performance",
        score_performance,
    )

    if score_pivot <= ZERO:
        raise RemunerationCalculationError(
            "score_pivot must be greater than 0"
        )

    if score_pivot > ONE_HUNDRED:
        raise RemunerationCalculationError(
            "score_pivot must be less than or equal to 100"
        )

    _validate_rate(
        "amplitude",
        amplitude,
    )

    return (
        (
            score_performance
            - score_pivot
        )
        / score_pivot
        * amplitude
    )


def calculate_final_rate(
    taux_base: Decimal,
    majoration_anciennete: Decimal,
    modulation_performance: Decimal,
    taux_plancher: Decimal,
    taux_plafond: Decimal,
) -> Decimal:
    _validate_rate(
        "taux_base",
        taux_base,
    )
    _validate_rate(
        "majoration_anciennete",
        majoration_anciennete,
    )
    _validate_rate(
        "taux_plancher",
        taux_plancher,
    )
    _validate_rate(
        "taux_plafond",
        taux_plafond,
    )

    if taux_plancher > taux_plafond:
        raise RemunerationCalculationError(
            "taux_plancher cannot exceed taux_plafond"
        )

    raw_rate = (
        taux_base
        * (
            Decimal("1")
            + majoration_anciennete
            + modulation_performance
        )
    )

    bounded_rate = _bound(
        raw_rate,
        taux_plancher,
        taux_plafond,
    )

    return _quantize_rate(
        bounded_rate
    )


def calculate_remuneration(
    calculation_input: RemunerationCalculationInput,
) -> RemunerationCalculationResult:
    score_performance = (
        calculate_performance_score(
            calculation_input.scores,
            calculation_input.weights,
        )
    )

    montant_honoraires = (
        calculate_company_fees(
            montant_achat=(
                calculation_input
                .montant_achat
            ),
            montant_fixe=(
                calculation_input
                .montant_fixe_honoraires
            ),
            taux_pourcentage=(
                calculation_input
                .taux_honoraires
            ),
        )
    )

    majoration_anciennete = (
        calculate_seniority_bonus(
            annees_anciennete=(
                calculation_input
                .annees_anciennete
            ),
            taux_par_annee=(
                calculation_input
                .taux_anciennete_par_annee
            ),
            plafond=(
                calculation_input
                .plafond_anciennete
            ),
        )
    )

    modulation_performance = (
        calculate_performance_modulation(
            score_performance=(
                score_performance
            ),
            score_pivot=(
                calculation_input
                .score_pivot
            ),
            amplitude=(
                calculation_input
                .amplitude_performance
            ),
        )
    )

    taux_final = (
        calculate_final_rate(
            taux_base=(
                calculation_input
                .taux_base
            ),
            majoration_anciennete=(
                majoration_anciennete
            ),
            modulation_performance=(
                modulation_performance
            ),
            taux_plancher=(
                calculation_input
                .taux_plancher
            ),
            taux_plafond=(
                calculation_input
                .taux_plafond
            ),
        )
    )

    montant_chasseur = (
        _quantize_money(
            montant_honoraires
            * taux_final
        )
    )

    return RemunerationCalculationResult(
        montant_achat=_quantize_money(
            calculation_input
            .montant_achat
        ),
        montant_honoraires=(
            montant_honoraires
        ),
        score_performance=(
            score_performance
        ),
        taux_base=_quantize_rate(
            calculation_input
            .taux_base
        ),
        majoration_anciennete=(
            _quantize_rate(
                majoration_anciennete
            )
        ),
        modulation_performance=(
            _quantize_rate(
                modulation_performance
            )
        ),
        taux_final=taux_final,
        montant_chasseur=(
            montant_chasseur
        ),
    )