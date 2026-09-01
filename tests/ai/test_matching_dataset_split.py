import pandas as pd
import pytest

from src.ai.matching.dataset_split import (
    create_group_aware_split,
    split_summary,
)
from src.ai.matching.training_dataset import LABEL_COLUMN
from src.ai.matching.run_training_dataset_split import (
    validate_split_against_source,
)   

def build_dataset() -> pd.DataFrame:
    rows = []

    for group_id in range(1, 12):
        rows.extend(
            [
                {
                    "id_demande_version": group_id,
                    "reference_externe": f"{group_id}-P1",
                    LABEL_COLUMN: 1,
                },
                {
                    "id_demande_version": group_id,
                    "reference_externe": f"{group_id}-P2",
                    LABEL_COLUMN: 1,
                },
                {
                    "id_demande_version": group_id,
                    "reference_externe": f"{group_id}-N1",
                    LABEL_COLUMN: 0,
                },
            ]
        )

    return pd.DataFrame(rows)


def test_group_aware_split_creates_three_partitions() -> None:
    dataset = build_dataset()

    split = create_group_aware_split(dataset)

    assert len(split.train_groups) == 7
    assert len(split.validation_groups) == 2
    assert len(split.test_groups) == 2

    assert not split.train.empty
    assert not split.validation.empty
    assert not split.test.empty


def test_group_aware_split_has_no_group_leakage() -> None:
    dataset = build_dataset()

    split = create_group_aware_split(dataset)

    train_groups = set(split.train["id_demande_version"].unique())
    validation_groups = set(
        split.validation["id_demande_version"].unique()
    )
    test_groups = set(split.test["id_demande_version"].unique())

    assert train_groups.isdisjoint(validation_groups)
    assert train_groups.isdisjoint(test_groups)
    assert validation_groups.isdisjoint(test_groups)


def test_group_aware_split_preserves_all_groups() -> None:
    dataset = build_dataset()

    split = create_group_aware_split(dataset)

    original_groups = set(
        dataset["id_demande_version"].unique()
    )

    split_groups = (
        set(split.train_groups)
        | set(split.validation_groups)
        | set(split.test_groups)
    )

    assert split_groups == original_groups


def test_group_aware_split_preserves_all_rows() -> None:
    dataset = build_dataset()

    split = create_group_aware_split(dataset)

    split_row_count = (
        len(split.train)
        + len(split.validation)
        + len(split.test)
    )

    assert split_row_count == len(dataset)


def test_group_aware_split_is_deterministic() -> None:
    dataset = build_dataset()

    first = create_group_aware_split(
        dataset,
        random_state=42,
    )

    second = create_group_aware_split(
        dataset,
        random_state=42,
    )

    assert first.train_groups == second.train_groups
    assert first.validation_groups == second.validation_groups
    assert first.test_groups == second.test_groups


def test_different_random_state_can_change_groups() -> None:
    dataset = build_dataset()

    first = create_group_aware_split(
        dataset,
        random_state=42,
    )

    second = create_group_aware_split(
        dataset,
        random_state=123,
    )

    assert (
        first.train_groups != second.train_groups
        or first.validation_groups != second.validation_groups
        or first.test_groups != second.test_groups
    )


def test_every_partition_contains_both_classes() -> None:
    dataset = build_dataset()

    split = create_group_aware_split(dataset)

    for partition in (
        split.train,
        split.validation,
        split.test,
    ):
        classes = set(
            partition[LABEL_COLUMN]
            .astype(int)
            .unique()
            .tolist()
        )

        assert classes == {0, 1}


def test_single_class_group_is_rejected() -> None:
    dataset = build_dataset()

    invalid_group = pd.DataFrame(
        [
            {
                "id_demande_version": 99,
                "reference_externe": "99-P1",
                LABEL_COLUMN: 1,
            },
            {
                "id_demande_version": 99,
                "reference_externe": "99-P2",
                LABEL_COLUMN: 1,
            },
        ]
    )

    dataset = pd.concat(
        [dataset, invalid_group],
        ignore_index=True,
    )

    with pytest.raises(
        ValueError,
        match="both positive and negative",
    ):
        create_group_aware_split(dataset)


def test_empty_dataset_is_rejected() -> None:
    dataset = pd.DataFrame(
        columns=[
            "id_demande_version",
            LABEL_COLUMN,
        ]
    )

    with pytest.raises(
        ValueError,
        match="empty dataset",
    ):
        create_group_aware_split(dataset)


def test_less_than_three_groups_is_rejected() -> None:
    dataset = build_dataset()

    dataset = dataset[
        dataset["id_demande_version"].isin([1, 2])
    ].copy()

    with pytest.raises(
        ValueError,
        match="At least 3 distinct groups",
    ):
        create_group_aware_split(dataset)


def test_invalid_split_fractions_are_rejected() -> None:
    dataset = build_dataset()

    with pytest.raises(
        ValueError,
        match="lower than 1",
    ):
        create_group_aware_split(
            dataset,
            validation_fraction=0.6,
            test_fraction=0.5,
        )


def test_split_summary_contains_expected_metadata() -> None:
    dataset = build_dataset()

    split = create_group_aware_split(dataset)

    summary = split_summary(split)

    assert summary["split_strategy"] == "group_aware"
    assert summary["group_column"] == "id_demande_version"
    assert summary["group_leakage"] is False

    assert summary["train"]["group_count"] == 7
    assert summary["validation"]["group_count"] == 2
    assert summary["test"]["group_count"] == 2

    assert (
        summary["train"]["rows"]
        + summary["validation"]["rows"]
        + summary["test"]["rows"]
        == len(dataset)
    )
def test_runtime_split_validation_accepts_valid_split() -> None:
    dataset = build_dataset()

    split = create_group_aware_split(
        dataset,
        random_state=42,
    )

    source_groups = set(
        dataset["id_demande_version"]
        .astype(int)
        .unique()
        .tolist()
    )

    result = validate_split_against_source(
        split=split,
        source_group_ids=source_groups,
        source_row_count=len(dataset),
    )

    assert result["group_leakage"] is False
    assert result["all_source_groups_preserved"] is True
    assert result["all_source_rows_preserved"] is True
    assert result["source_group_count"] == 11
    assert result["represented_group_count"] == 11
    assert result["source_row_count"] == len(dataset)
    assert result["split_row_count"] == len(dataset)


def test_runtime_split_validation_rejects_missing_group() -> None:
    dataset = build_dataset()

    split = create_group_aware_split(
        dataset,
        random_state=42,
    )

    source_groups = set(
        dataset["id_demande_version"]
        .astype(int)
        .unique()
        .tolist()
    )

    source_groups.add(999)

    with pytest.raises(
        RuntimeError,
        match="Split group coverage does not match source dataset",
    ):
        validate_split_against_source(
            split=split,
            source_group_ids=source_groups,
            source_row_count=len(dataset),
        )


def test_runtime_split_validation_rejects_unexpected_group() -> None:
    dataset = build_dataset()

    split = create_group_aware_split(
        dataset,
        random_state=42,
    )

    source_groups = set(
        dataset["id_demande_version"]
        .astype(int)
        .unique()
        .tolist()
    )

    source_groups.remove(
        next(iter(source_groups))
    )

    with pytest.raises(
        RuntimeError,
        match="Split group coverage does not match source dataset",
    ):
        validate_split_against_source(
            split=split,
            source_group_ids=source_groups,
            source_row_count=len(dataset),
        )


def test_runtime_split_validation_rejects_row_loss() -> None:
    dataset = build_dataset()

    split = create_group_aware_split(
        dataset,
        random_state=42,
    )

    source_groups = set(
        dataset["id_demande_version"]
        .astype(int)
        .unique()
        .tolist()
    )

    with pytest.raises(
        RuntimeError,
        match="Split row count does not match source dataset",
    ):
        validate_split_against_source(
            split=split,
            source_group_ids=source_groups,
            source_row_count=len(dataset) + 1,
        )