from __future__ import annotations

import pandas as pd
import pytest

from src.ai.matching.dataset_split import (
    DatasetSplit,
)
from src.ai.matching.model_training import (
    PROBABILITY_COLUMN,
    PREDICTION_COLUMN,
    build_model_matrix,
    compute_classification_metrics,
    compute_grouped_ranking_metrics,
    model_coefficients,
    model_metadata,
    predict_relevance,
    train_and_evaluate_logistic_regression,
    train_logistic_regression,
)
from src.ai.matching.training_dataset import (
    FEATURE_COLUMNS,
    LABEL_COLUMN,
)


def _group_rows(
    group_id: int,
    *,
    positives: int,
    negatives: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for index in range(positives):
        rows.append(
            {
                "id_demande_version": group_id,
                "source_recherche_ref": f"REC-{group_id}",
                "ingestion_batch": "generated-test",
                "reference_externe": (
                    f"PROP-{group_id}-P-{index}"
                ),
                "feature_location": 1.0,
                "feature_budget": 0.95,
                "feature_property_type": 1.0,
                "feature_surface": 0.90,
                "feature_rooms": 0.80,
                "feature_bedrooms": 0.75,
                "feature_dpe": 0.70,
                "relevance_label": 1,
            }
        )

    for index in range(negatives):
        rows.append(
            {
                "id_demande_version": group_id,
                "source_recherche_ref": f"REC-{group_id}",
                "ingestion_batch": "generated-test",
                "reference_externe": (
                    f"PROP-{group_id}-N-{index}"
                ),
                "feature_location": 1.0,
                "feature_budget": 0.40,
                "feature_property_type": 1.0,
                "feature_surface": 0.35,
                "feature_rooms": 0.25,
                "feature_bedrooms": 0.20,
                "feature_dpe": 0.30,
                "relevance_label": 0,
            }
        )

    return rows


def _dataset(
    group_ids: list[int],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for group_id in group_ids:
        rows.extend(
            _group_rows(
                group_id,
                positives=4,
                negatives=4,
            )
        )

    return pd.DataFrame(rows)


def _split() -> DatasetSplit:
    train = _dataset(
        [10, 11, 12]
    )

    validation = _dataset(
        [20]
    )

    test = _dataset(
        [30]
    )

    return DatasetSplit(
        train=train,
        validation=validation,
        test=test,
        train_groups=(10, 11, 12),
        validation_groups=(20,),
        test_groups=(30,),
    )


def test_build_model_matrix_uses_only_canonical_features():
    dataset = _dataset(
        [10]
    )

    features, target = build_model_matrix(
        dataset
    )

    assert list(features.columns) == FEATURE_COLUMNS

    assert "id_demande_version" not in features.columns
    assert "source_recherche_ref" not in features.columns
    assert "ingestion_batch" not in features.columns
    assert "reference_externe" not in features.columns
    assert LABEL_COLUMN not in features.columns

    assert len(features) == len(dataset)
    assert len(target) == len(dataset)


def test_build_model_matrix_rejects_missing_feature():
    dataset = _dataset(
        [10]
    ).drop(
        columns=[
            "feature_budget",
        ]
    )

    with pytest.raises(
        ValueError,
        match="missing required model columns",
    ):
        build_model_matrix(
            dataset
        )


def test_build_model_matrix_rejects_out_of_range_feature():
    dataset = _dataset(
        [10]
    )

    dataset.loc[
        dataset.index[0],
        "feature_budget",
    ] = 1.5

    with pytest.raises(
        ValueError,
        match=r"inside \[0, 1\]",
    ):
        build_model_matrix(
            dataset
        )


def test_train_logistic_regression_fits_binary_classifier():
    dataset = _dataset(
        [10, 11, 12]
    )

    model = train_logistic_regression(
        dataset
    )

    assert list(model.classes_) == [
        0,
        1,
    ]

    assert model.coef_.shape == (
        1,
        len(FEATURE_COLUMNS),
    )


def test_predict_relevance_adds_probability_and_prediction():
    dataset = _dataset(
        [10, 11, 12]
    )

    model = train_logistic_regression(
        dataset
    )

    predictions = predict_relevance(
        model=model,
        dataset=dataset,
    )

    assert PROBABILITY_COLUMN in predictions.columns
    assert PREDICTION_COLUMN in predictions.columns

    assert predictions[
        PROBABILITY_COLUMN
    ].between(
        0.0,
        1.0,
    ).all()

    assert set(
        predictions[
            PREDICTION_COLUMN
        ].unique()
    ).issubset(
        {
            0,
            1,
        }
    )


def test_classification_metrics_are_bounded():
    dataset = _dataset(
        [10, 11, 12]
    )

    model = train_logistic_regression(
        dataset
    )

    predictions = predict_relevance(
        model=model,
        dataset=dataset,
    )

    metrics = compute_classification_metrics(
        predictions
    )

    bounded_metrics = [
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "average_precision",
    ]

    for metric_name in bounded_metrics:
        assert (
            0.0
            <= metrics[metric_name]
            <= 1.0
        )

    assert metrics[
        "log_loss"
    ] >= 0.0


def test_grouped_ranking_metrics_are_macro_averaged_by_group():
    dataset = _dataset(
        [10, 11]
    )

    model = train_logistic_regression(
        dataset
    )

    predictions = predict_relevance(
        model=model,
        dataset=dataset,
    )

    metrics = compute_grouped_ranking_metrics(
        predictions,
        ks=(1, 3),
    )

    assert metrics[
        "group_count"
    ] == 2

    assert (
        metrics[
            "aggregation"
        ]
        == "macro_average_by_id_demande_version"
    )

    assert set(
        metrics[
            "per_group"
        ]
    ) == {
        "10",
        "11",
    }

    assert (
        0.0
        <= metrics[
            "macro_average"
        ][
            "ndcg_at_1"
        ]
        <= 1.0
    )


def test_train_and_evaluate_uses_all_three_partitions():
    split = _split()

    result = (
        train_and_evaluate_logistic_regression(
            split
        )
    )

    assert result.train_metrics[
        "groups"
    ] == 3

    assert result.validation_metrics[
        "groups"
    ] == 1

    assert result.test_metrics[
        "groups"
    ] == 1

    assert len(
        result.train_predictions
    ) == len(
        split.train
    )

    assert len(
        result.validation_predictions
    ) == len(
        split.validation
    )

    assert len(
        result.test_predictions
    ) == len(
        split.test
    )


def test_model_coefficients_match_feature_columns():
    split = _split()

    result = (
        train_and_evaluate_logistic_regression(
            split
        )
    )

    coefficients = model_coefficients(
        result
    )

    assert set(
        coefficients
    ) == set(
        FEATURE_COLUMNS
    )


def test_model_metadata_excludes_lineage_from_features():
    split = _split()

    result = (
        train_and_evaluate_logistic_regression(
            split
        )
    )

    metadata = model_metadata(
        result
    )

    assert metadata[
        "feature_columns"
    ] == FEATURE_COLUMNS

    assert metadata[
        "ground_truth_used_as_feature"
    ] is False

    assert metadata[
        "group_metadata_used_as_feature"
    ] is False

    assert metadata[
        "lineage_metadata_used_as_feature"
    ] is False