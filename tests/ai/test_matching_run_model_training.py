from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.ai.matching.dataset_split import (
    DatasetSplit,
    split_summary,
)
from src.ai.matching.run_model_training import (
    _serializable_metrics,
    validate_frozen_split,
    write_training_artifact,
)


def _frame(
    group_id: int,
    rows: int,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id_demande_version": [
                group_id
            ]
            * rows,
            "relevance_label": [
                1 if index % 2 == 0 else 0
                for index in range(rows)
            ],
        }
    )


def _frozen_split() -> DatasetSplit:
    train_groups = (
        91,
        101,
        55,
        109,
        68,
        78,
        66,
    )

    validation_groups = (
        70,
        105,
    )

    test_groups = (
        60,
        102,
    )

    train = pd.concat(
        [
            _frame(
                group_id,
                4,
            )
            for group_id in train_groups
        ],
        ignore_index=True,
    )

    validation = pd.concat(
        [
            _frame(
                group_id,
                4,
            )
            for group_id in validation_groups
        ],
        ignore_index=True,
    )

    test = pd.concat(
        [
            _frame(
                group_id,
                4,
            )
            for group_id in test_groups
        ],
        ignore_index=True,
    )

    return DatasetSplit(
        train=train,
        validation=validation,
        test=test,
        train_groups=train_groups,
        validation_groups=validation_groups,
        test_groups=test_groups,
    )


def test_serializable_metrics_converts_nested_values():
    class Value:
        def item(self):
            return 42

    result = _serializable_metrics(
        {
            "scalar": Value(),
            "nested": {
                "values": (
                    Value(),
                    Value(),
                )
            },
        }
    )

    assert result == {
        "scalar": 42,
        "nested": {
            "values": [
                42,
                42,
            ]
        },
    }


def test_validate_frozen_split_accepts_expected_groups():
    split = _frozen_split()

    result = validate_frozen_split(
        split_details=split_summary(
            split
        )
    )

    assert result[
        "frozen_split_v1"
    ] is True

    assert result[
        "train_groups_valid"
    ] is True

    assert result[
        "validation_groups_valid"
    ] is True

    assert result[
        "test_groups_valid"
    ] is True

    assert result[
        "group_leakage"
    ] is False


def test_validate_frozen_split_rejects_changed_train_groups():
    split = _frozen_split()

    details = split_summary(
        split
    )

    details[
        "train"
    ][
        "groups"
    ][0] = 999

    with pytest.raises(
        RuntimeError,
        match="Frozen TRAIN group assignment changed",
    ):
        validate_frozen_split(
            split_details=details
        )


def test_validate_frozen_split_rejects_changed_validation_groups():
    split = _frozen_split()

    details = split_summary(
        split
    )

    details[
        "validation"
    ][
        "groups"
    ][0] = 999

    with pytest.raises(
        RuntimeError,
        match="Frozen VALIDATION group assignment changed",
    ):
        validate_frozen_split(
            split_details=details
        )


def test_validate_frozen_split_rejects_changed_test_groups():
    split = _frozen_split()

    details = split_summary(
        split
    )

    details[
        "test"
    ][
        "groups"
    ][0] = 999

    with pytest.raises(
        RuntimeError,
        match="Frozen TEST group assignment changed",
    ):
        validate_frozen_split(
            split_details=details
        )


def test_write_training_artifact_contains_core_evidence(
    tmp_path: Path,
):
    generated_demande_versions = [
        {
            "id_demande_version": 55,
            "source_recherche_ref": "REC-55",
            "ingestion_batch": "generated-a",
        },
        {
            "id_demande_version": 60,
            "source_recherche_ref": "REC-60",
            "ingestion_batch": "generated-b",
        },
    ]

    informative_summary = {
        "rows": 100,
        "groups": 11,
        "positives": 60,
        "negatives": 40,
        "positive_rate": 0.6,
    }

    split = _frozen_split()

    split_details = split_summary(
        split
    )

    frozen_split_validation = (
        validate_frozen_split(
            split_details=split_details
        )
    )

    model_details = {
        "model_type": "LogisticRegression",
        "feature_columns": [
            "feature_location",
            "feature_budget",
        ],
        "coefficients": {
            "feature_location": 1.0,
            "feature_budget": 0.5,
        },
        "intercept": -0.2,
    }

    metrics = {
        "rows": 10,
        "groups": 2,
        "classification": {
            "accuracy": 0.8,
        },
        "ranking": {
            "group_count": 2,
            "aggregation": (
                "macro_average_by_id_demande_version"
            ),
            "macro_average": {
                "ndcg_at_10": 0.9,
                "mrr": 1.0,
            },
            "per_group": {},
        },
    }

    artifact_path = write_training_artifact(
        output_dir=tmp_path,
        generated_demande_versions=(
            generated_demande_versions
        ),
        informative_summary=(
            informative_summary
        ),
        split_details=(
            split_details
        ),
        frozen_split_validation=(
            frozen_split_validation
        ),
        model_details=(
            model_details
        ),
        train_metrics=metrics,
        validation_metrics=metrics,
        test_metrics=metrics,
        gitlab_traceability={
            "git_commit_sha": "abc123",
        },
    )

    assert artifact_path.exists()

    content = artifact_path.read_text(
        encoding="utf-8"
    )

    assert (
        "logistic-regression-baseline-v1"
        in content
    )

    assert (
        '"model_training": true'
        in content
    )

    assert (
        '"mlflow_tracking": false'
        in content
    )

    assert (
        '"ground_truth_used_as_feature": false'
        in content
    )

    assert (
        '"git_commit_sha": "abc123"'
        in content
    )