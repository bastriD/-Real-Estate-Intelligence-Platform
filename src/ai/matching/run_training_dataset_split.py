from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg

from src.ai.matching.dataset_split import (
    DEFAULT_RANDOM_STATE,
    DEFAULT_TEST_FRACTION,
    DEFAULT_VALIDATION_FRACTION,
    DatasetSplit,
    create_group_aware_split,
    split_summary,
)
from src.ai.matching.run_training_dataset_validation import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_USER,
    build_gitlab_traceability,
    count_generated_batches,
    discover_generated_demande_versions,
    validate_training_dataset,
)
from src.ai.matching.training_dataset import (
    build_training_dataset,
    dataset_summary,
)


OUTPUT_FILENAME = "training_dataset_split.json"


def validate_split_against_source(
    *,
    split: DatasetSplit,
    source_group_ids: set[int],
    source_row_count: int,
) -> dict[str, Any]:
    """
    Validate the final split against the informative source dataset.

    This provides runtime evidence that:
    - no group leaked between partitions;
    - no informative group was lost;
    - no row was lost;
    - no extra group appeared.
    """

    train_groups = set(split.train_groups)
    validation_groups = set(
        split.validation_groups
    )
    test_groups = set(split.test_groups)

    if train_groups & validation_groups:
        raise RuntimeError(
            "Group leakage detected between train and validation."
        )

    if train_groups & test_groups:
        raise RuntimeError(
            "Group leakage detected between train and test."
        )

    if validation_groups & test_groups:
        raise RuntimeError(
            "Group leakage detected between validation and test."
        )

    represented_groups = (
        train_groups
        | validation_groups
        | test_groups
    )

    if represented_groups != source_group_ids:
        missing_groups = sorted(
            source_group_ids - represented_groups
        )

        unexpected_groups = sorted(
            represented_groups - source_group_ids
        )

        raise RuntimeError(
            "Split group coverage does not match source dataset. "
            f"Missing={missing_groups}, "
            f"unexpected={unexpected_groups}"
        )

    split_row_count = (
        len(split.train)
        + len(split.validation)
        + len(split.test)
    )

    if split_row_count != source_row_count:
        raise RuntimeError(
            "Split row count does not match source dataset. "
            f"source={source_row_count}, "
            f"split={split_row_count}"
        )

    return {
        "group_leakage": False,
        "all_source_groups_preserved": True,
        "all_source_rows_preserved": True,
        "source_group_count": len(
            source_group_ids
        ),
        "represented_group_count": len(
            represented_groups
        ),
        "source_row_count": (
            source_row_count
        ),
        "split_row_count": (
            split_row_count
        ),
    }


def write_split_artifact(
    *,
    output_dir: Path,
    generated_batches: int,
    generated_demande_versions: int,
    informative_dataset_summary: dict[
        str,
        Any,
    ],
    split: DatasetSplit,
    split_validation: dict[
        str,
        Any,
    ],
    gitlab_traceability: dict[
        str,
        str,
    ],
) -> Path:
    """
    Persist the group-aware split evidence.

    Only metadata and statistics are persisted here.
    The complete training dataset is not baked into the image
    or committed as an ML artifact.
    """

    artifact_path = (
        output_dir
        / OUTPUT_FILENAME
    )

    artifact = {
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "artifact_type": (
            "supervised-matching-group-aware-split"
        ),
        "dataset_source": (
            "postgresql-runtime-reconstruction"
        ),
        "candidate_engine": (
            "canonical-matching-repository"
        ),
        "ground_truth_type": (
            "explicit-generated-search-lineage"
        ),
        "ground_truth_used_as_feature": False,
        "model_training": False,
        "split_strategy": (
            "group-aware-id-demande-version"
        ),
        "random_state": (
            DEFAULT_RANDOM_STATE
        ),
        "validation_fraction": (
            DEFAULT_VALIDATION_FRACTION
        ),
        "test_fraction": (
            DEFAULT_TEST_FRACTION
        ),
        "generated_batches_discovered": (
            generated_batches
        ),
        "generated_demande_versions_discovered": (
            generated_demande_versions
        ),
        "informative_dataset_summary": (
            informative_dataset_summary
        ),
        "split_summary": (
            split_summary(
                split
            )
        ),
        "split_validation": (
            split_validation
        ),
        "gitlab_traceability": (
            gitlab_traceability
        ),
    }

    with open(
        artifact_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            artifact,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return artifact_path


def print_partition(
    *,
    name: str,
    partition: dict[str, Any],
) -> None:
    print(
        f"{name}"
    )
    print(
        "----------------------------------------------"
    )

    print(
        "Groups: "
        f"{partition['group_count']}"
    )

    print(
        "Group IDs: "
        + ", ".join(
            str(group_id)
            for group_id in partition[
                "groups"
            ]
        )
    )

    print(
        "Rows: "
        f"{partition['rows']}"
    )

    print(
        "Positive labels: "
        f"{partition['positives']}"
    )

    print(
        "Negative labels: "
        f"{partition['negatives']}"
    )

    print(
        "Positive rate: "
        f"{float(partition['positive_rate']):.6f}"
    )

    print()


def print_split_summary(
    *,
    informative_summary: dict[
        str,
        Any,
    ],
    split: DatasetSplit,
    split_validation: dict[
        str,
        Any,
    ],
    artifact_path: Path,
) -> None:
    summary = split_summary(
        split
    )

    print()
    print(
        "=============================================="
    )
    print(
        "Supervised matching group-aware dataset split"
    )
    print(
        "=============================================="
    )

    print()
    print(
        "SOURCE INFORMATIVE DATASET"
    )
    print(
        "----------------------------------------------"
    )

    print(
        "Groups: "
        f"{informative_summary['groups']}"
    )

    print(
        "Rows: "
        f"{informative_summary['rows']}"
    )

    print(
        "Positive labels: "
        f"{informative_summary['positives']}"
    )

    print(
        "Negative labels: "
        f"{informative_summary['negatives']}"
    )

    print(
        "Positive rate: "
        f"{float(informative_summary['positive_rate']):.6f}"
    )

    print()

    print_partition(
        name="TRAIN",
        partition=summary["train"],
    )

    print_partition(
        name="VALIDATION",
        partition=summary[
            "validation"
        ],
    )

    print_partition(
        name="TEST",
        partition=summary["test"],
    )

    print(
        "SPLIT VALIDATION"
    )
    print(
        "----------------------------------------------"
    )

    print(
        "Group leakage: "
        f"{split_validation['group_leakage']}"
    )

    print(
        "All source groups preserved: "
        f"{split_validation['all_source_groups_preserved']}"
    )

    print(
        "All source rows preserved: "
        f"{split_validation['all_source_rows_preserved']}"
    )

    print(
        "Source groups: "
        f"{split_validation['source_group_count']}"
    )

    print(
        "Represented groups: "
        f"{split_validation['represented_group_count']}"
    )

    print(
        "Source rows: "
        f"{split_validation['source_row_count']}"
    )

    print(
        "Split rows: "
        f"{split_validation['split_row_count']}"
    )

    print()
    print(
        "Split artifact: "
        f"{artifact_path}"
    )


def main() -> None:
    print(
        "===== Real Estate Training Dataset "
        "Group-Aware Split Started ====="
    )

    if not DATABASE_USER:
        raise RuntimeError(
            "POSTGRES_USER is required"
        )

    if not DATABASE_PASSWORD:
        raise RuntimeError(
            "POSTGRES_PASSWORD is required"
        )

    print(
        "PostgreSQL host: "
        f"{DATABASE_HOST}"
    )

    print(
        "PostgreSQL port: "
        f"{DATABASE_PORT}"
    )

    print(
        "PostgreSQL database: "
        f"{DATABASE_NAME}"
    )

    print(
        "Split group column: "
        "id_demande_version"
    )

    print(
        "Random state: "
        f"{DEFAULT_RANDOM_STATE}"
    )

    print(
        "Validation fraction: "
        f"{DEFAULT_VALIDATION_FRACTION}"
    )

    print(
        "Test fraction: "
        f"{DEFAULT_TEST_FRACTION}"
    )

    output_dir = Path(
        "outputs"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    gitlab_traceability = (
        build_gitlab_traceability()
    )

    connection = psycopg.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
    )

    try:
        connection.read_only = True

        generated_demande_versions = (
            discover_generated_demande_versions(
                connection
            )
        )

        if not generated_demande_versions:
            raise RuntimeError(
                "No generated demande versions were discovered."
            )

        demande_version_ids = tuple(
            int(
                item[
                    "id_demande_version"
                ]
            )
            for item in (
                generated_demande_versions
            )
        )

        generated_batches = (
            count_generated_batches(
                generated_demande_versions
            )
        )

        print(
            "Generated batches discovered: "
            f"{generated_batches}"
        )

        print(
            "Generated demande versions discovered: "
            f"{len(demande_version_ids)}"
        )

        print()
        print(
            "Building informative supervised dataset..."
        )

        training_dataset = (
            build_training_dataset(
                connection=connection,
                demande_version_ids=(
                    demande_version_ids
                ),
                require_both_classes=True,
            )
        )

        informative_summary = (
            dataset_summary(
                training_dataset
            )
        )

        # Reuse the already-proven structural validation
        # before any split is created.
        validate_training_dataset(
            dataset=training_dataset,
            discovered_demande_version_ids=(
                demande_version_ids
            ),
        )

        source_group_ids = set(
            training_dataset[
                "id_demande_version"
            ]
            .astype(int)
            .unique()
            .tolist()
        )

        print(
            "Informative groups discovered: "
            f"{len(source_group_ids)}"
        )

        print(
            "Informative rows reconstructed: "
            f"{len(training_dataset)}"
        )

        print()
        print(
            "Creating deterministic group-aware split..."
        )

        split = create_group_aware_split(
            training_dataset,
            validation_fraction=(
                DEFAULT_VALIDATION_FRACTION
            ),
            test_fraction=(
                DEFAULT_TEST_FRACTION
            ),
            random_state=(
                DEFAULT_RANDOM_STATE
            ),
        )

        split_validation = (
            validate_split_against_source(
                split=split,
                source_group_ids=(
                    source_group_ids
                ),
                source_row_count=(
                    len(training_dataset)
                ),
            )
        )

        artifact_path = (
            write_split_artifact(
                output_dir=output_dir,
                generated_batches=(
                    generated_batches
                ),
                generated_demande_versions=(
                    len(
                        generated_demande_versions
                    )
                ),
                informative_dataset_summary=(
                    informative_summary
                ),
                split=split,
                split_validation=(
                    split_validation
                ),
                gitlab_traceability=(
                    gitlab_traceability
                ),
            )
        )

        print_split_summary(
            informative_summary=(
                informative_summary
            ),
            split=split,
            split_validation=(
                split_validation
            ),
            artifact_path=(
                artifact_path
            ),
        )

    finally:
        connection.close()

    print()

    if gitlab_traceability:
        print(
            "GitLab traceability metadata:"
        )

        for key, value in (
            gitlab_traceability.items()
        ):
            print(
                f"  {key}: {value}"
            )
    else:
        print(
            "GitLab traceability metadata: "
            "not provided by execution environment"
        )

    print()
    print(
        "Group-aware split validation: PASSED"
    )

    print(
        "Group leakage detected: False"
    )

    print(
        "Model training performed: False"
    )

    print()
    print(
        "===== Real Estate Training Dataset "
        "Group-Aware Split Completed Successfully ====="
    )


if __name__ == "__main__":
    main()