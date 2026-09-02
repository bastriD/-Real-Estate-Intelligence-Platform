from __future__ import annotations

import pandas as pd
import pytest

from src.ai.matching.model_comparison import (
    DETERMINISTIC_SCORE_COLUMN,
    compare_rankers,
    compute_deterministic_scores,
    compute_grouped_metrics,
)
from src.ai.matching.model_training import (
    PROBABILITY_COLUMN,
)
from src.ai.matching.training_dataset import (
    LABEL_COLUMN,
)


def _comparison_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id_demande_version": 1,
                "reference_externe": "A",
                LABEL_COLUMN: 1,
                "feature_location": 1.0,
                "feature_budget": 1.0,
                "feature_property_type": 1.0,
                "feature_surface": 1.0,
                "feature_rooms": 1.0,
                "feature_bedrooms": 1.0,
                "feature_dpe": 1.0,
            },
            {
                "id_demande_version": 1,
                "reference_externe": "B",
                LABEL_COLUMN: 0,
                "feature_location": 1.0,
                "feature_budget": 1.0,
                "feature_property_type": 1.0,
                "feature_surface": 1.0,
                "feature_rooms": 0.0,
                "feature_bedrooms": 0.0,
                "feature_dpe": 0.0,
            },
            {
                "id_demande_version": 1,
                "reference_externe": "C",
                LABEL_COLUMN: 1,
                "feature_location": 1.0,
                "feature_budget": 1.0,
                "feature_property_type": 1.0,
                "feature_surface": 1.0,
                "feature_rooms": 0.5,
                "feature_bedrooms": 0.5,
                "feature_dpe": 1.0,
            },
            {
                "id_demande_version": 2,
                "reference_externe": "D",
                LABEL_COLUMN: 0,
                "feature_location": 1.0,
                "feature_budget": 1.0,
                "feature_property_type": 1.0,
                "feature_surface": 1.0,
                "feature_rooms": 0.0,
                "feature_bedrooms": 0.0,
                "feature_dpe": 0.0,
            },
            {
                "id_demande_version": 2,
                "reference_externe": "E",
                LABEL_COLUMN: 1,
                "feature_location": 1.0,
                "feature_budget": 1.0,
                "feature_property_type": 1.0,
                "feature_surface": 1.0,
                "feature_rooms": 1.0,
                "feature_bedrooms": 1.0,
                "feature_dpe": 1.0,
            },
            {
                "id_demande_version": 2,
                "reference_externe": "F",
                LABEL_COLUMN: 1,
                "feature_location": 1.0,
                "feature_budget": 1.0,
                "feature_property_type": 1.0,
                "feature_surface": 1.0,
                "feature_rooms": 0.5,
                "feature_bedrooms": 0.5,
                "feature_dpe": 1.0,
            },
        ]
    )


def _ml_predictions() -> pd.DataFrame:
    frame = _comparison_dataset().copy()

    frame[PROBABILITY_COLUMN] = [
        0.95,
        0.10,
        0.80,
        0.20,
        0.90,
        0.70,
    ]

    return frame


def test_compute_deterministic_scores_preserves_rows() -> None:
    dataset = _comparison_dataset()

    scored = compute_deterministic_scores(
        dataset
    )

    assert len(scored) == len(dataset)

    assert (
        DETERMINISTIC_SCORE_COLUMN
        in scored.columns
    )

    assert set(
        scored["reference_externe"]
    ) == set(
        dataset["reference_externe"]
    )


def test_compute_deterministic_scores_stays_in_range() -> None:
    scored = compute_deterministic_scores(
        _comparison_dataset()
    )

    assert scored[
        DETERMINISTIC_SCORE_COLUMN
    ].between(
        0.0,
        100.0,
    ).all()


def test_deterministic_full_match_scores_100() -> None:
    scored = compute_deterministic_scores(
        _comparison_dataset()
    )

    row = scored.loc[
        scored["reference_externe"]
        == "A"
    ].iloc[0]

    assert (
        row[
            DETERMINISTIC_SCORE_COLUMN
        ]
        == pytest.approx(100.0)
    )


def test_compute_grouped_metrics_returns_two_groups() -> None:
    predictions = _ml_predictions()

    metrics = compute_grouped_metrics(
        predictions,
        score_column=PROBABILITY_COLUMN,
        ks=(1, 2),
    )

    assert metrics[
        "group_count"
    ] == 2

    assert set(
        metrics["per_group"]
    ) == {"1", "2"}


def test_compute_grouped_metrics_macro_average_present() -> None:
    metrics = compute_grouped_metrics(
        _ml_predictions(),
        score_column=PROBABILITY_COLUMN,
        ks=(1, 2),
    )

    assert (
        "precision_at_1"
        in metrics["macro_average"]
    )

    assert (
        "recall_at_2"
        in metrics["macro_average"]
    )

    assert (
        "mrr"
        in metrics["macro_average"]
    )


def test_compare_rankers_requires_identical_candidates() -> None:
    dataset = _comparison_dataset()

    ml_predictions = (
        _ml_predictions()
        .iloc[:-1]
        .copy()
    )

    with pytest.raises(
        ValueError,
        match=(
            "candidate populations differ"
        ),
    ):
        compare_rankers(
            dataset=dataset,
            ml_predictions=ml_predictions,
            ks=(1, 2),
        )


def test_compare_rankers_confirms_fair_population() -> None:
    comparison = compare_rankers(
        dataset=_comparison_dataset(),
        ml_predictions=_ml_predictions(),
        ks=(1, 2),
    )

    assert (
        comparison[
            "candidate_population_identical"
        ]
        is True
    )

    assert (
        comparison[
            "ground_truth_identical"
        ]
        is True
    )

    assert (
        comparison[
            "hard_eligibility_identical"
        ]
        is True
    )

    assert (
        comparison[
            "metric_semantics_identical"
        ]
        is True
    )


def test_compare_rankers_produces_deltas() -> None:
    comparison = compare_rankers(
        dataset=_comparison_dataset(),
        ml_predictions=_ml_predictions(),
        ks=(1, 2),
    )

    deltas = comparison[
        "delta_ml_minus_deterministic"
    ]

    assert deltas

    assert "mrr" in deltas

    assert (
        "precision_at_1"
        in deltas
    )


def test_compare_rankers_summary_counts_metrics() -> None:
    comparison = compare_rankers(
        dataset=_comparison_dataset(),
        ml_predictions=_ml_predictions(),
        ks=(1, 2),
    )

    summary = comparison[
        "summary"
    ]

    metric_count = len(
        comparison[
            "delta_ml_minus_deterministic"
        ]
    )

    assert (
        summary[
            "ml_metric_wins"
        ]
        + summary[
            "deterministic_metric_wins"
        ]
        + summary[
            "ties"
        ]
        == metric_count
    )