from __future__ import annotations

from dataclasses import dataclass
from math import log2

import pandas as pd
import psycopg

from src.ai.matching.features import (
    build_matching_features,
    compute_matching_score,
)
from src.ai.matching.repository import (
    load_ground_truth_references,
    load_matching_input,
)


DEFAULT_RANKING_KS = (10, 20, 50, 100)


@dataclass(frozen=True)
class MatchingEvaluationResult:
    id_demande_version: int
    demande: pd.Series

    properties_loaded: int
    candidates_after_filtering: int

    ground_truth_total: int
    ground_truth_in_candidates: int
    candidate_recall: float

    ranking_metrics: dict[str, float]

    ranked: pd.DataFrame


def _normalise_reference(value: object) -> str:
    return str(value).strip()


def _ranked_references(
    ranked: pd.DataFrame,
) -> list[str]:
    if ranked.empty:
        return []

    if "reference_externe" not in ranked.columns:
        raise ValueError(
            "The ranked candidate dataset does not contain "
            "'reference_externe'."
        )

    return [
        _normalise_reference(value)
        for value in ranked["reference_externe"].tolist()
        if pd.notna(value)
    ]


def _normalise_ground_truth(
    ground_truth: set[str],
) -> set[str]:
    return {
        _normalise_reference(reference)
        for reference in ground_truth
        if reference is not None
    }


def _precision_at_k(
    ranked_references: list[str],
    ground_truth: set[str],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError("k must be greater than zero.")

    top_k = ranked_references[:k]

    if not top_k:
        return 0.0

    relevant = sum(
        reference in ground_truth
        for reference in top_k
    )

    return relevant / len(top_k)


def _recall_at_k(
    ranked_references: list[str],
    ground_truth: set[str],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError("k must be greater than zero.")

    if not ground_truth:
        return 0.0

    top_k = ranked_references[:k]

    relevant = sum(
        reference in ground_truth
        for reference in top_k
    )

    return relevant / len(ground_truth)


def _hit_rate_at_k(
    ranked_references: list[str],
    ground_truth: set[str],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError("k must be greater than zero.")

    top_k = ranked_references[:k]

    return float(
        any(
            reference in ground_truth
            for reference in top_k
        )
    )


def _mean_reciprocal_rank(
    ranked_references: list[str],
    ground_truth: set[str],
) -> float:
    for position, reference in enumerate(
        ranked_references,
        start=1,
    ):
        if reference in ground_truth:
            return 1.0 / position

    return 0.0


def _dcg_at_k(
    ranked_references: list[str],
    ground_truth: set[str],
    k: int,
) -> float:
    if k <= 0:
        raise ValueError("k must be greater than zero.")

    score = 0.0

    for position, reference in enumerate(
        ranked_references[:k],
        start=1,
    ):
        relevance = (
            1.0
            if reference in ground_truth
            else 0.0
        )

        if relevance == 0.0:
            continue

        score += relevance / log2(position + 1)

    return score


def _ideal_dcg_at_k(
    ground_truth_size: int,
    k: int,
) -> float:
    if k <= 0:
        raise ValueError("k must be greater than zero.")

    relevant_positions = min(
        ground_truth_size,
        k,
    )

    return sum(
        1.0 / log2(position + 1)
        for position in range(
            1,
            relevant_positions + 1,
        )
    )


def _ndcg_at_k(
    ranked_references: list[str],
    ground_truth: set[str],
    k: int,
) -> float:
    if not ground_truth:
        return 0.0

    dcg = _dcg_at_k(
        ranked_references=ranked_references,
        ground_truth=ground_truth,
        k=k,
    )

    ideal_dcg = _ideal_dcg_at_k(
        ground_truth_size=len(ground_truth),
        k=k,
    )

    if ideal_dcg == 0.0:
        return 0.0

    return dcg / ideal_dcg


def compute_ranking_metrics(
    ranked: pd.DataFrame,
    ground_truth: set[str],
    ks: tuple[int, ...] = DEFAULT_RANKING_KS,
) -> dict[str, float]:
    ranked_references = _ranked_references(
        ranked=ranked,
    )

    normalised_ground_truth = (
        _normalise_ground_truth(
            ground_truth=ground_truth,
        )
    )

    metrics: dict[str, float] = {}

    for k in ks:
        metrics[f"precision_at_{k}"] = (
            _precision_at_k(
                ranked_references=ranked_references,
                ground_truth=normalised_ground_truth,
                k=k,
            )
        )

        metrics[f"recall_at_{k}"] = (
            _recall_at_k(
                ranked_references=ranked_references,
                ground_truth=normalised_ground_truth,
                k=k,
            )
        )

        metrics[f"hit_rate_at_{k}"] = (
            _hit_rate_at_k(
                ranked_references=ranked_references,
                ground_truth=normalised_ground_truth,
                k=k,
            )
        )

        metrics[f"ndcg_at_{k}"] = (
            _ndcg_at_k(
                ranked_references=ranked_references,
                ground_truth=normalised_ground_truth,
                k=k,
            )
        )

    metrics["mrr"] = _mean_reciprocal_rank(
        ranked_references=ranked_references,
        ground_truth=normalised_ground_truth,
    )

    return metrics


def evaluate_demande_version(
    connection: psycopg.Connection,
    id_demande_version: int,
) -> MatchingEvaluationResult:
    demande_dict, biens = load_matching_input(
        connection=connection,
        id_demande_version=id_demande_version,
    )

    demande = pd.Series(demande_dict)

    source_recherche_ref = demande.get(
        "source_recherche_ref"
    )

    if (
        source_recherche_ref is None
        or pd.isna(source_recherche_ref)
        or not str(source_recherche_ref).strip()
    ):
        raise ValueError(
            "DemandeVersion "
            f"{id_demande_version} has no "
            "source_recherche_ref. "
            "Ground-truth ranking evaluation requires "
            "explicit generated-search lineage."
        )

    ground_truth = load_ground_truth_references(
        connection=connection,
        source_recherche_ref=str(
            source_recherche_ref
        ).strip(),
    )

    if not ground_truth:
        raise ValueError(
            "No ground-truth properties found for "
            f"DemandeVersion {id_demande_version} "
            f"and recherche_ref "
            f"{source_recherche_ref!r}."
        )

    features = build_matching_features(
        biens=biens,
        demande=demande,
    )

    ranked = compute_matching_score(
        features=features,
    )

    ranked_references = set(
        _ranked_references(
            ranked=ranked,
        )
    )

    normalised_ground_truth = (
        _normalise_ground_truth(
            ground_truth=ground_truth,
        )
    )

    ground_truth_in_candidates = len(
        normalised_ground_truth.intersection(
            ranked_references
        )
    )

    candidate_recall = (
        ground_truth_in_candidates
        / len(normalised_ground_truth)
    )

    ranking_metrics = compute_ranking_metrics(
        ranked=ranked,
        ground_truth=normalised_ground_truth,
    )

    return MatchingEvaluationResult(
        id_demande_version=id_demande_version,
        demande=demande,
        properties_loaded=len(biens),
        candidates_after_filtering=len(features),
        ground_truth_total=len(
            normalised_ground_truth
        ),
        ground_truth_in_candidates=(
            ground_truth_in_candidates
        ),
        candidate_recall=candidate_recall,
        ranking_metrics=ranking_metrics,
        ranked=ranked,
    )