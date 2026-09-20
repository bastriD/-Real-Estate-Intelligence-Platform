"""Validate reproducible splits against the dataset used by the current run."""

import hashlib
import json
from typing import Any

import pandas as pd

from src.ai.matching.dataset_split import (
    DEFAULT_RANDOM_STATE,
    DEFAULT_TEST_FRACTION,
    DEFAULT_VALIDATION_FRACTION,
    GROUP_COLUMN,
    DatasetSplit,
    create_group_aware_split,
)
from src.ai.matching.run_training_dataset_split import validate_split_against_source

SPLIT_VERSION = "runtime-group-v2"


def _canonical_frame(frame: pd.DataFrame) -> pd.DataFrame:
    columns = sorted(frame.columns)
    return frame.sort_values(columns, kind="stable")[columns].reset_index(drop=True)


def validate_runtime_split(*, split: DatasetSplit, source_dataset: pd.DataFrame) -> dict[str, Any]:
    """Check coverage, rows and seeded assignments without pinning live SQL IDs.

    The fingerprint identifies the reconstructed data for this run; it is not
    a persisted dataset snapshot. Compare independent runs only when their
    dataset and split fingerprints match.
    """
    validation = validate_split_against_source(
        split=split,
        source_group_ids=set(source_dataset[GROUP_COLUMN].astype(int)),
        source_row_count=len(source_dataset),
    )
    expected = create_group_aware_split(source_dataset)
    groups = {}
    for partition in ("train", "validation", "test"):
        actual_groups = tuple(int(value) for value in getattr(split, f"{partition}_groups"))
        expected_groups = tuple(getattr(expected, f"{partition}_groups"))
        if actual_groups != expected_groups:
            raise RuntimeError(f"Non-reproducible {partition.upper()} group assignment")
        try:
            pd.testing.assert_frame_equal(
                _canonical_frame(getattr(split, partition)),
                _canonical_frame(getattr(expected, partition)),
                check_exact=True,
            )
        except AssertionError as error:
            raise RuntimeError(f"{partition.upper()} rows differ from the source dataset") from error
        groups[partition] = list(actual_groups)

    # Serialize all reconstructed columns, including features, labels and
    # provenance. Row/index order alone does not create a new dataset version.
    canonical = _canonical_frame(source_dataset)
    dataset_json = json.dumps(
        canonical.to_dict(orient="split", index=False),
        sort_keys=True, allow_nan=False, separators=(",", ":"),
    )
    dataset_fingerprint = hashlib.sha256(dataset_json.encode("utf-8")).hexdigest()
    identity = {
        "split_version": SPLIT_VERSION,
        "dataset_fingerprint": dataset_fingerprint,
        "random_state": DEFAULT_RANDOM_STATE,
        "validation_fraction": DEFAULT_VALIDATION_FRACTION,
        "test_fraction": DEFAULT_TEST_FRACTION,
        "groups": groups,
    }
    split_fingerprint = hashlib.sha256(
        json.dumps(identity, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return {
        **validation,
        "split_version": SPLIT_VERSION,
        "frozen_split_v1": False,
        "random_state": DEFAULT_RANDOM_STATE,
        "validation_fraction": DEFAULT_VALIDATION_FRACTION,
        "test_fraction": DEFAULT_TEST_FRACTION,
        "dataset_fingerprint": dataset_fingerprint,
        "split_fingerprint": split_fingerprint,
        "train_groups_valid": True,
        "validation_groups_valid": True,
        "test_groups_valid": True,
    }
