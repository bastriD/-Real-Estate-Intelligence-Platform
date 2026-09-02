from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.ai.matching.dataset_split import (
    GROUP_COLUMN,
)
from src.ai.matching.evaluate import (
    DEFAULT_RANKING_KS,
    compute_ranking_metrics,
)
from src.ai.matching.features import (
    MatchingWeights,
)
from src.ai.matching.model_training import (
    PROBABILITY_COLUMN,
    REFERENCE_COLUMN,
)
from src.ai.matching.training_dataset import (
    LABEL_COLUMN,
)


DETERMINISTIC_SCORE_COLUMN = "deterministic_score"


def compute_deterministic_scores(
    dataset: pd.DataFrame,
    *,
    weights: MatchingWeights | None = None,
) -> pd.DataFrame:
    """
    Apply the frozen deterministic weighted-rule baseline to a supervised
    dataset that already contains the canonical matching features.

    The candidate population is not changed.

    Hard eligibility has already been applied by repository.py when the
    training dataset was constructed.
    """

    if dataset.empty:
        raise ValueError(
            "Cannot score an empty comparison dataset."
        )

    required_columns = {
        GROUP_COLUMN,
        REFERENCE_COLUMN,
        LABEL_COLUMN,
        "feature_location",
        "feature_budget",
        "feature_property_type",
        "feature_surface",
        "feature_rooms",
        "feature_bedrooms",
        "feature_dpe",
    }

    missing_columns = required_columns.difference(
        dataset.columns
    )

    if missing_columns:
        raise ValueError(
            "Comparison dataset is missing required columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    weights = (
        weights
        or MatchingWeights()
    )

    result = dataset.copy()

    result[DETERMINISTIC_SCORE_COLUMN] = (
        result["feature_location"]
        * weights.location
        + result["feature_budget"]
        * weights.budget
        + result["feature_property_type"]
        * weights.property_type
        + result["feature_surface"]
        * weights.surface
        + result["feature_rooms"]
        * weights.rooms
        + result["feature_bedrooms"]
        * weights.bedrooms
        + result["feature_dpe"]
        * weights.dpe
    ) * 100.0

    result[DETERMINISTIC_SCORE_COLUMN] = (
        result[
            DETERMINISTIC_SCORE_COLUMN
        ]
        .clip(
            lower=0.0,
            upper=100.0,
        )
        .round(2)
    )

    return result


def _compute_group_metrics(
    group: pd.DataFrame,
    *,
    score_column: str,
    ks: tuple[int, ...],
) -> dict[str, float]:
    """
    Evaluate one demande_version using one ranking score.
    """

    if group.empty:
        raise ValueError(
            "Cannot evaluate an empty comparison group."
        )

    if score_column not in group.columns:
        raise ValueError(
            "Comparison group does not contain score column "
            f"'{score_column}'."
        )

    ground_truth = set(
        group.loc[
            group[LABEL_COLUMN].astype(int) == 1,
            REFERENCE_COLUMN,
        ]
        .astype(str)
        .tolist()
    )

    if not ground_truth:
        raise ValueError(
            "Comparison group contains no positive examples."
        )

    ranked = (
        group.sort_values(
            by=[
                score_column,
                REFERENCE_COLUMN,
            ],
            ascending=[
                False,
                True,
            ],
            kind="mergesort",
        )
        .reset_index(
            drop=True
        )
    )

    return {
        metric_name: float(metric_value)
        for metric_name, metric_value
        in compute_ranking_metrics(
            ranked=ranked,
            ground_truth=ground_truth,
            ks=ks,
        ).items()
    }


def compute_grouped_metrics(
    predictions: pd.DataFrame,
    *,
    score_column: str,
    ks: tuple[int, ...] = DEFAULT_RANKING_KS,
) -> dict[str, Any]:
    """
    Compute ranking metrics independently for every demande_version and
    macro-average them.

    This deliberately mirrors the supervised model evaluation semantics.
    """

    if predictions.empty:
        raise ValueError(
            "Cannot compare an empty prediction dataset."
        )

    required_columns = {
        GROUP_COLUMN,
        REFERENCE_COLUMN,
        LABEL_COLUMN,
        score_column,
    }

    missing_columns = required_columns.difference(
        predictions.columns
    )

    if missing_columns:
        raise ValueError(
            "Comparison predictions are missing required columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    if not ks:
        raise ValueError(
            "At least one ranking cutoff k is required."
        )

    group_metrics: dict[
        str,
        dict[str, float],
    ] = {}

    for group_id, group in predictions.groupby(
        GROUP_COLUMN,
        sort=True,
    ):
        group_metrics[
            str(int(group_id))
        ] = _compute_group_metrics(
            group,
            score_column=score_column,
            ks=ks,
        )

    if not group_metrics:
        raise ValueError(
            "No demande_version groups available for comparison."
        )

    metric_names = sorted(
        next(
            iter(group_metrics.values())
        ).keys()
    )

    macro_average = {
        metric_name: float(
            np.mean(
                [
                    metrics[metric_name]
                    for metrics
                    in group_metrics.values()
                ]
            )
        )
        for metric_name in metric_names
    }

    return {
        "group_count": len(
            group_metrics
        ),
        "aggregation": (
            "macro_average_by_id_demande_version"
        ),
        "score_column": score_column,
        "macro_average": macro_average,
        "per_group": group_metrics,
    }


def compare_rankers(
    *,
    dataset: pd.DataFrame,
    ml_predictions: pd.DataFrame,
    ks: tuple[int, ...] = DEFAULT_RANKING_KS,
) -> dict[str, Any]:
    """
    Compare the frozen deterministic baseline and supervised ML ranker on
    exactly the same candidate population and ground truth.

    No candidate filtering or model fitting occurs here.
    """

    deterministic = (
        compute_deterministic_scores(
            dataset
        )
    )

    dataset_keys = set(
        zip(
            dataset[
                GROUP_COLUMN
            ].astype(int),
            dataset[
                REFERENCE_COLUMN
            ].astype(str),
            strict=False,
        )
    )

    prediction_keys = set(
        zip(
            ml_predictions[
                GROUP_COLUMN
            ].astype(int),
            ml_predictions[
                REFERENCE_COLUMN
            ].astype(str),
            strict=False,
        )
    )

    if dataset_keys != prediction_keys:
        raise ValueError(
            "Deterministic and ML candidate populations differ."
        )

    deterministic_metrics = (
        compute_grouped_metrics(
            deterministic,
            score_column=(
                DETERMINISTIC_SCORE_COLUMN
            ),
            ks=ks,
        )
    )

    ml_metrics = compute_grouped_metrics(
        ml_predictions,
        score_column=(
            PROBABILITY_COLUMN
        ),
        ks=ks,
    )

    deterministic_macro = (
        deterministic_metrics[
            "macro_average"
        ]
    )

    ml_macro = (
        ml_metrics[
            "macro_average"
        ]
    )

    metric_names = sorted(
        set(
            deterministic_macro
        ).intersection(
            ml_macro
        )
    )

    deltas = {
        metric_name: float(
            ml_macro[metric_name]
            - deterministic_macro[
                metric_name
            ]
        )
        for metric_name in metric_names
    }

    ml_wins = sum(
        1
        for value in deltas.values()
        if value > 0.0
    )

    deterministic_wins = sum(
        1
        for value in deltas.values()
        if value < 0.0
    )

    ties = sum(
        1
        for value in deltas.values()
        if np.isclose(
            value,
            0.0,
        )
    )

    return {
        "candidate_population_identical": True,
        "ground_truth_identical": True,
        "hard_eligibility_identical": True,
        "metric_semantics_identical": True,
        "ranking_cutoffs": list(
            ks
        ),
        "deterministic": (
            deterministic_metrics
        ),
        "supervised_ml": (
            ml_metrics
        ),
        "delta_ml_minus_deterministic": (
            deltas
        ),
        "summary": {
            "ml_metric_wins": (
                ml_wins
            ),
            "deterministic_metric_wins": (
                deterministic_wins
            ),
            "ties": ties,
        },
    }