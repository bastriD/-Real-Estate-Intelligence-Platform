from unittest.mock import MagicMock

import pandas as pd

from src.ai.matching.run_training_dataset_validation import (
    build_batch_diagnostics,
    build_group_diagnostics,
    count_generated_batches,
    validate_full_dataset,
    validate_training_dataset,
)

from src.ai.matching.training_dataset import (
    DATASET_COLUMNS,
    FEATURE_COLUMNS,
    LABEL_COLUMN,
)


def make_row(
    *,
    id_demande_version: int,
    source_recherche_ref: str,
    ingestion_batch: str,
    reference_externe: str,
    label: int,
    feature_value: float = 1.0,
) -> dict:
    return {
        "id_demande_version": (
            id_demande_version
        ),
        "source_recherche_ref": (
            source_recherche_ref
        ),
        "ingestion_batch": (
            ingestion_batch
        ),
        "reference_externe": (
            reference_externe
        ),
        **{
            column: feature_value
            for column in FEATURE_COLUMNS
        },
        LABEL_COLUMN: label,
    }


def test_count_generated_batches():
    generated_demande_versions = [
        {
            "id_demande_version": 55,
            "source_recherche_ref": "REC-55",
            "ingestion_batch": "batch-1",
        },
        {
            "id_demande_version": 56,
            "source_recherche_ref": "REC-56",
            "ingestion_batch": "batch-1",
        },
        {
            "id_demande_version": 60,
            "source_recherche_ref": "REC-60",
            "ingestion_batch": "batch-2",
        },
    ]

    result = count_generated_batches(
        generated_demande_versions
    )

    assert result == 2


def test_validate_full_dataset_accepts_all_discovered_groups():
    dataset = pd.DataFrame(
        [
            make_row(
                id_demande_version=55,
                source_recherche_ref="REC-55",
                ingestion_batch="batch-1",
                reference_externe="BIEN-001",
                label=1,
            ),
            make_row(
                id_demande_version=56,
                source_recherche_ref="REC-56",
                ingestion_batch="batch-1",
                reference_externe="BIEN-002",
                label=1,
            ),
            make_row(
                id_demande_version=60,
                source_recherche_ref="REC-60",
                ingestion_batch="batch-2",
                reference_externe="BIEN-003",
                label=1,
            ),
            make_row(
                id_demande_version=60,
                source_recherche_ref="REC-60",
                ingestion_batch="batch-2",
                reference_externe="BIEN-004",
                label=0,
                feature_value=0.5,
            ),
        ]
    )[DATASET_COLUMNS]

    result = validate_full_dataset(
        dataset=dataset,
        discovered_demande_version_ids=(
            55,
            56,
            60,
        ),
    )

    assert (
        result[
            "represented_groups"
        ]
        == 3
    )

    assert (
        result[
            "discovered_groups"
        ]
        == 3
    )

    assert (
        result[
            "missing_groups"
        ]
        == []
    )

    assert (
        result[
            "query_candidate_pairs_unique"
        ]
        is True
    )

    assert (
        result[
            "features_in_range"
        ]
        is True
    )


def test_validate_full_dataset_reports_missing_groups():
    dataset = pd.DataFrame(
        [
            make_row(
                id_demande_version=55,
                source_recherche_ref="REC-55",
                ingestion_batch="batch-1",
                reference_externe="BIEN-001",
                label=1,
            ),
        ]
    )[DATASET_COLUMNS]

    result = validate_full_dataset(
        dataset=dataset,
        discovered_demande_version_ids=(
            55,
            56,
        ),
    )

    assert (
        result[
            "represented_groups"
        ]
        == 1
    )

    assert (
        result[
            "discovered_groups"
        ]
        == 2
    )

    assert (
        result[
            "missing_groups"
        ]
        == [56]
    )


def test_validate_full_dataset_rejects_duplicate_query_candidate_pair():
    row = make_row(
        id_demande_version=55,
        source_recherche_ref="REC-55",
        ingestion_batch="batch-1",
        reference_externe="BIEN-001",
        label=1,
    )

    dataset = pd.DataFrame(
        [
            row,
            row,
        ]
    )[DATASET_COLUMNS]

    try:
        validate_full_dataset(
            dataset=dataset,
            discovered_demande_version_ids=(
                55,
            ),
        )
    except RuntimeError as exc:
        assert (
            "duplicate"
            in str(exc).lower()
        )
    else:
        raise AssertionError(
            "Expected RuntimeError was not raised."
        )


def test_validate_full_dataset_rejects_invalid_feature_range():
    dataset = pd.DataFrame(
        [
            make_row(
                id_demande_version=55,
                source_recherche_ref="REC-55",
                ingestion_batch="batch-1",
                reference_externe="BIEN-001",
                label=1,
                feature_value=1.5,
            ),
        ]
    )[DATASET_COLUMNS]

    try:
        validate_full_dataset(
            dataset=dataset,
            discovered_demande_version_ids=(
                55,
            ),
        )
    except RuntimeError as exc:
        assert (
            "outside [0, 1]"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected RuntimeError was not raised."
        )


def test_validate_training_dataset_accepts_informative_groups():
    dataset = pd.DataFrame(
        [
            make_row(
                id_demande_version=60,
                source_recherche_ref="REC-60",
                ingestion_batch="batch-1",
                reference_externe="BIEN-001",
                label=1,
            ),
            make_row(
                id_demande_version=60,
                source_recherche_ref="REC-60",
                ingestion_batch="batch-1",
                reference_externe="BIEN-002",
                label=0,
                feature_value=0.5,
            ),
            make_row(
                id_demande_version=68,
                source_recherche_ref="REC-68",
                ingestion_batch="batch-2",
                reference_externe="BIEN-003",
                label=1,
            ),
            make_row(
                id_demande_version=68,
                source_recherche_ref="REC-68",
                ingestion_batch="batch-2",
                reference_externe="BIEN-004",
                label=0,
                feature_value=0.5,
            ),
        ]
    )[DATASET_COLUMNS]

    result = validate_training_dataset(
        dataset=dataset,
        discovered_demande_version_ids=(
            60,
            68,
        ),
    )

    assert (
        result[
            "all_retained_groups_have_both_classes"
        ]
        is True
    )

    assert (
        result[
            "informative_group_count"
        ]
        == 2
    )


def test_validate_training_dataset_rejects_single_class_group():
    dataset = pd.DataFrame(
        [
            make_row(
                id_demande_version=60,
                source_recherche_ref="REC-60",
                ingestion_batch="batch-1",
                reference_externe="BIEN-001",
                label=1,
            ),
            make_row(
                id_demande_version=60,
                source_recherche_ref="REC-60",
                ingestion_batch="batch-1",
                reference_externe="BIEN-002",
                label=1,
                feature_value=0.8,
            ),
        ]
    )[DATASET_COLUMNS]

    try:
        validate_training_dataset(
            dataset=dataset,
            discovered_demande_version_ids=(
                60,
            ),
        )
    except RuntimeError as exc:
        assert (
            "without both classes"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected RuntimeError was not raised."
        )


def test_build_group_diagnostics_marks_informative_groups():
    dataset = pd.DataFrame(
        [
            make_row(
                id_demande_version=60,
                source_recherche_ref="REC-60",
                ingestion_batch="batch-1",
                reference_externe="BIEN-001",
                label=1,
            ),
            make_row(
                id_demande_version=60,
                source_recherche_ref="REC-60",
                ingestion_batch="batch-1",
                reference_externe="BIEN-002",
                label=0,
                feature_value=0.5,
            ),
            make_row(
                id_demande_version=61,
                source_recherche_ref="REC-61",
                ingestion_batch="batch-2",
                reference_externe="BIEN-003",
                label=1,
            ),
        ]
    )[DATASET_COLUMNS]

    result = build_group_diagnostics(
        dataset
    )

    assert len(result) == 2

    result_by_id = {
        item[
            "id_demande_version"
        ]: item
        for item in result
    }

    assert (
        result_by_id[
            60
        ][
            "informative"
        ]
        is True
    )

    assert (
        result_by_id[
            60
        ][
            "positives"
        ]
        == 1
    )

    assert (
        result_by_id[
            60
        ][
            "negatives"
        ]
        == 1
    )

    assert (
        result_by_id[
            61
        ][
            "informative"
        ]
        is False
    )

    assert (
        result_by_id[
            61
        ][
            "positives"
        ]
        == 1
    )

    assert (
        result_by_id[
            61
        ][
            "negatives"
        ]
        == 0
    )


def test_build_batch_diagnostics():
    generated_demande_versions = [
        {
            "id_demande_version": 55,
            "source_recherche_ref": "REC-55",
            "ingestion_batch": "batch-1",
        },
        {
            "id_demande_version": 56,
            "source_recherche_ref": "REC-56",
            "ingestion_batch": "batch-1",
        },
        {
            "id_demande_version": 60,
            "source_recherche_ref": "REC-60",
            "ingestion_batch": "batch-2",
        },
    ]

    dataset = pd.DataFrame(
        [
            make_row(
                id_demande_version=55,
                source_recherche_ref="REC-55",
                ingestion_batch="batch-1",
                reference_externe="BIEN-001",
                label=1,
            ),
            make_row(
                id_demande_version=56,
                source_recherche_ref="REC-56",
                ingestion_batch="batch-1",
                reference_externe="BIEN-002",
                label=1,
            ),
            make_row(
                id_demande_version=60,
                source_recherche_ref="REC-60",
                ingestion_batch="batch-2",
                reference_externe="BIEN-003",
                label=1,
            ),
            make_row(
                id_demande_version=60,
                source_recherche_ref="REC-60",
                ingestion_batch="batch-2",
                reference_externe="BIEN-004",
                label=0,
                feature_value=0.5,
            ),
        ]
    )[DATASET_COLUMNS]

    result = build_batch_diagnostics(
        generated_demande_versions=(
            generated_demande_versions
        ),
        full_dataset=dataset,
    )

    assert len(result) == 2

    result_by_batch = {
        item[
            "ingestion_batch"
        ]: item
        for item in result
    }

    assert (
        result_by_batch[
            "batch-1"
        ][
            "discovered_groups"
        ]
        == 2
    )

    assert (
        result_by_batch[
            "batch-1"
        ][
            "represented_groups"
        ]
        == 2
    )

    assert (
        result_by_batch[
            "batch-1"
        ][
            "rows"
        ]
        == 2
    )

    assert (
        result_by_batch[
            "batch-1"
        ][
            "positives"
        ]
        == 2
    )

    assert (
        result_by_batch[
            "batch-1"
        ][
            "negatives"
        ]
        == 0
    )

    assert (
        result_by_batch[
            "batch-2"
        ][
            "discovered_groups"
        ]
        == 1
    )

    assert (
        result_by_batch[
            "batch-2"
        ][
            "represented_groups"
        ]
        == 1
    )

    assert (
        result_by_batch[
            "batch-2"
        ][
            "rows"
        ]
        == 2
    )

    assert (
        result_by_batch[
            "batch-2"
        ][
            "positives"
        ]
        == 1
    )

    assert (
        result_by_batch[
            "batch-2"
        ][
            "negatives"
        ]
        == 1
    )