from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.ai.matching.training_dataset import LABEL_COLUMN


GROUP_COLUMN = "id_demande_version"

DEFAULT_RANDOM_STATE = 42
DEFAULT_VALIDATION_FRACTION = 0.18
DEFAULT_TEST_FRACTION = 0.18


@dataclass(frozen=True)
class DatasetSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame

    train_groups: tuple[int, ...]
    validation_groups: tuple[int, ...]
    test_groups: tuple[int, ...]


def _validate_input_dataset(dataset: pd.DataFrame) -> None:
    """
    Validate the minimum structural requirements before creating
    a group-aware train / validation / test split.
    """

    if dataset.empty:
        raise ValueError("Cannot split an empty dataset.")

    required_columns = {
        GROUP_COLUMN,
        LABEL_COLUMN,
    }

    missing_columns = required_columns.difference(dataset.columns)

    if missing_columns:
        raise ValueError(
            "Dataset is missing required split columns: "
            + ", ".join(sorted(missing_columns))
        )

    if dataset[GROUP_COLUMN].isna().any():
        raise ValueError(
            f"Dataset contains null values in {GROUP_COLUMN}."
        )

    if dataset[LABEL_COLUMN].isna().any():
        raise ValueError(
            f"Dataset contains null values in {LABEL_COLUMN}."
        )

    unique_labels = set(
        dataset[LABEL_COLUMN]
        .astype(int)
        .unique()
        .tolist()
    )

    if not unique_labels.issubset({0, 1}):
        raise ValueError(
            f"{LABEL_COLUMN} must contain binary labels only."
        )

    groups = dataset[GROUP_COLUMN].drop_duplicates()

    if len(groups) < 3:
        raise ValueError(
            "At least 3 distinct groups are required to create "
            "train, validation and test partitions."
        )


def _validate_group_classes(dataset: pd.DataFrame) -> None:
    """
    Every group used for supervised training must contain
    at least one positive and one negative example.
    """

    grouped_labels = dataset.groupby(GROUP_COLUMN)[LABEL_COLUMN]

    invalid_groups: list[int] = []

    for group_id, labels in grouped_labels:
        classes = set(labels.astype(int).unique().tolist())

        if classes != {0, 1}:
            invalid_groups.append(int(group_id))

    if invalid_groups:
        raise ValueError(
            "All groups must contain both positive and negative labels. "
            f"Invalid groups: {invalid_groups}"
        )


def _calculate_partition_sizes(
    number_of_groups: int,
    validation_fraction: float,
    test_fraction: float,
) -> tuple[int, int, int]:
    """
    Calculate the number of groups assigned to train,
    validation and test.

    At least one group is kept for every partition.
    """

    if number_of_groups < 3:
        raise ValueError(
            "At least 3 groups are required."
        )

    if not 0 < validation_fraction < 1:
        raise ValueError(
            "validation_fraction must be between 0 and 1."
        )

    if not 0 < test_fraction < 1:
        raise ValueError(
            "test_fraction must be between 0 and 1."
        )

    if validation_fraction + test_fraction >= 1:
        raise ValueError(
            "validation_fraction + test_fraction must be lower than 1."
        )

    validation_groups = max(
        1,
        round(number_of_groups * validation_fraction),
    )

    test_groups = max(
        1,
        round(number_of_groups * test_fraction),
    )

    train_groups = (
        number_of_groups
        - validation_groups
        - test_groups
    )

    if train_groups < 1:
        raise ValueError(
            "Split fractions leave no group available for training."
        )

    return (
        train_groups,
        validation_groups,
        test_groups,
    )


def _validate_no_group_overlap(
    train_groups: set[int],
    validation_groups: set[int],
    test_groups: set[int],
) -> None:
    """
    Ensure no demande_version is present in more than one partition.
    """

    if train_groups.intersection(validation_groups):
        raise AssertionError(
            "Group leakage detected between train and validation."
        )

    if train_groups.intersection(test_groups):
        raise AssertionError(
            "Group leakage detected between train and test."
        )

    if validation_groups.intersection(test_groups):
        raise AssertionError(
            "Group leakage detected between validation and test."
        )


def _validate_partition_classes(
    partition: pd.DataFrame,
    partition_name: str,
) -> None:
    """
    Ensure each resulting partition contains both classes.
    """

    if partition.empty:
        raise AssertionError(
            f"{partition_name} partition is empty."
        )

    classes = set(
        partition[LABEL_COLUMN]
        .astype(int)
        .unique()
        .tolist()
    )

    if classes != {0, 1}:
        raise AssertionError(
            f"{partition_name} partition does not contain both classes. "
            f"Classes found: {sorted(classes)}"
        )


def create_group_aware_split(
    dataset: pd.DataFrame,
    *,
    validation_fraction: float = DEFAULT_VALIDATION_FRACTION,
    test_fraction: float = DEFAULT_TEST_FRACTION,
    random_state: int = DEFAULT_RANDOM_STATE,
) -> DatasetSplit:
    """
    Create a deterministic group-aware train / validation / test split.

    The split is performed exclusively at id_demande_version level.

    Therefore, candidates belonging to the same search group can never
    appear in multiple partitions.

    The function expects the informative supervised dataset where every
    group already contains both positive and negative labels.
    """

    _validate_input_dataset(dataset)
    _validate_group_classes(dataset)

    unique_groups = sorted(
        int(group_id)
        for group_id in dataset[GROUP_COLUMN]
        .drop_duplicates()
        .tolist()
    )

    (
        train_group_count,
        validation_group_count,
        test_group_count,
    ) = _calculate_partition_sizes(
        number_of_groups=len(unique_groups),
        validation_fraction=validation_fraction,
        test_fraction=test_fraction,
    )

    rng = np.random.default_rng(random_state)

    shuffled_groups = rng.permutation(
        np.array(unique_groups, dtype=int)
    ).tolist()

    train_group_ids = tuple(
        int(group_id)
        for group_id in shuffled_groups[
            :train_group_count
        ]
    )

    validation_start = train_group_count
    validation_end = (
        validation_start
        + validation_group_count
    )

    validation_group_ids = tuple(
        int(group_id)
        for group_id in shuffled_groups[
            validation_start:validation_end
        ]
    )

    test_group_ids = tuple(
        int(group_id)
        for group_id in shuffled_groups[
            validation_end:
        ]
    )

    if len(test_group_ids) != test_group_count:
        raise AssertionError(
            "Unexpected number of test groups."
        )

    train_group_set = set(train_group_ids)
    validation_group_set = set(validation_group_ids)
    test_group_set = set(test_group_ids)

    _validate_no_group_overlap(
        train_groups=train_group_set,
        validation_groups=validation_group_set,
        test_groups=test_group_set,
    )

    all_partition_groups = (
        train_group_set
        | validation_group_set
        | test_group_set
    )

    if all_partition_groups != set(unique_groups):
        raise AssertionError(
            "Some dataset groups were lost during splitting."
        )

    train = dataset[
        dataset[GROUP_COLUMN].isin(train_group_set)
    ].copy()

    validation = dataset[
        dataset[GROUP_COLUMN].isin(validation_group_set)
    ].copy()

    test = dataset[
        dataset[GROUP_COLUMN].isin(test_group_set)
    ].copy()

    _validate_partition_classes(
        train,
        "train",
    )

    _validate_partition_classes(
        validation,
        "validation",
    )

    _validate_partition_classes(
        test,
        "test",
    )

    return DatasetSplit(
        train=train.reset_index(drop=True),
        validation=validation.reset_index(drop=True),
        test=test.reset_index(drop=True),
        train_groups=train_group_ids,
        validation_groups=validation_group_ids,
        test_groups=test_group_ids,
    )


def split_summary(split: DatasetSplit) -> dict[str, object]:
    """
    Produce a serializable diagnostic summary for evidence,
    CI logs and future MLflow tracking.
    """

    def partition_summary(
        frame: pd.DataFrame,
        groups: tuple[int, ...],
    ) -> dict[str, object]:
        positives = int(
            (frame[LABEL_COLUMN].astype(int) == 1).sum()
        )

        negatives = int(
            (frame[LABEL_COLUMN].astype(int) == 0).sum()
        )

        rows = len(frame)

        return {
            "groups": list(groups),
            "group_count": len(groups),
            "rows": rows,
            "positives": positives,
            "negatives": negatives,
            "positive_rate": (
                positives / rows
                if rows
                else 0.0
            ),
        }

    return {
        "split_strategy": "group_aware",
        "group_column": GROUP_COLUMN,
        "group_leakage": False,
        "train": partition_summary(
            split.train,
            split.train_groups,
        ),
        "validation": partition_summary(
            split.validation,
            split.validation_groups,
        ),
        "test": partition_summary(
            split.test,
            split.test_groups,
        ),
    }