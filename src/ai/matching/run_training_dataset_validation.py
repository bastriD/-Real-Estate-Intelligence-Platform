from __future__ import annotations

import json
import os

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg

from src.ai.matching.training_dataset import (
    FEATURE_COLUMNS,
    LABEL_COLUMN,
    build_training_dataset,
    dataset_summary,
)


DATABASE_HOST = os.getenv(
    "POSTGRES_HOST",
    "real-estate-postgresql.real-estate.svc.cluster.local",
)

DATABASE_PORT = int(
    os.getenv(
        "POSTGRES_PORT",
        "5432",
    )
)

DATABASE_NAME = os.getenv(
    "POSTGRES_DB",
    "real_estate",
)

DATABASE_USER = os.getenv(
    "POSTGRES_USER"
)

DATABASE_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD"
)


def optional_env(
    name: str,
) -> str | None:
    value = os.getenv(name)

    if value is None:
        return None

    value = value.strip()

    if not value:
        return None

    return value


def build_gitlab_traceability() -> dict[str, str]:
    mapping = {
        "git_commit_sha": "CI_COMMIT_SHA",
        "git_commit_short_sha": (
            "CI_COMMIT_SHORT_SHA"
        ),
        "git_branch": "CI_COMMIT_BRANCH",
        "git_ref_name": "CI_COMMIT_REF_NAME",
        "git_repository": "CI_PROJECT_URL",
        "git_project_path": "CI_PROJECT_PATH",
        "git_pipeline_id": "CI_PIPELINE_ID",
        "git_pipeline_url": "CI_PIPELINE_URL",
        "git_job_id": "CI_JOB_ID",
        "git_job_name": "CI_JOB_NAME",
        "git_job_url": "CI_JOB_URL",
    }

    traceability: dict[str, str] = {}

    for key, env_name in mapping.items():
        value = optional_env(
            env_name
        )

        if value is not None:
            traceability[key] = value

    return traceability


def discover_generated_demande_versions(
    connection: psycopg.Connection,
) -> list[dict[str, Any]]:
    """
    Discover all generated demande versions currently persisted
    in PostgreSQL.

    This function only determines dataset scope.

    Candidate eligibility remains exclusively implemented in
    src.ai.matching.repository.
    """
    query = """
        SELECT
            dv.id_demande_version,
            dv.source_recherche_ref,
            dv.ingestion_batch
        FROM real_estate.demande_version AS dv
        INNER JOIN real_estate.demande AS d
            ON d.id_demande = dv.id_demande
        WHERE d.origine = 'GENERATED'
          AND dv.source_recherche_ref IS NOT NULL
          AND dv.ingestion_batch IS NOT NULL
        ORDER BY
            dv.ingestion_batch,
            dv.id_demande_version
    """

    rows = connection.execute(
        query
    ).fetchall()

    return [
        {
            "id_demande_version": int(
                row[0]
            ),
            "source_recherche_ref": str(
                row[1]
            ),
            "ingestion_batch": str(
                row[2]
            ),
        }
        for row in rows
    ]


def count_generated_batches(
    generated_demande_versions: list[
        dict[str, Any]
    ],
) -> int:
    batches = {
        str(
            item[
                "ingestion_batch"
            ]
        )
        for item in generated_demande_versions
    }

    return len(batches)


def validate_common_dataset_structure(
    *,
    dataset: pd.DataFrame,
    dataset_name: str,
) -> dict[str, Any]:
    """
    Validate common structural invariants shared by both
    full and informative datasets.
    """
    if dataset.empty:
        raise RuntimeError(
            f"{dataset_name} is empty."
        )

    required_columns = {
        "id_demande_version",
        "source_recherche_ref",
        "ingestion_batch",
        "reference_externe",
        *FEATURE_COLUMNS,
        LABEL_COLUMN,
    }

    missing_columns = (
        required_columns
        - set(dataset.columns)
    )

    if missing_columns:
        raise RuntimeError(
            f"{dataset_name} is missing required columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    metadata_columns = [
        "id_demande_version",
        "source_recherche_ref",
        "reference_externe",
    ]

    for column in metadata_columns:
        if dataset[
            column
        ].isna().any():
            raise RuntimeError(
                f"{dataset_name} contains null values "
                f"in {column}."
            )

    duplicate_pair_count = int(
        dataset.duplicated(
            subset=[
                "id_demande_version",
                "reference_externe",
            ]
        ).sum()
    )

    if duplicate_pair_count != 0:
        raise RuntimeError(
            f"{dataset_name} contains duplicate "
            "(id_demande_version, reference_externe) "
            f"pairs: {duplicate_pair_count}"
        )

    labels = set(
        dataset[
            LABEL_COLUMN
        ]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    if not labels:
        raise RuntimeError(
            f"{dataset_name} contains no labels."
        )

    if not labels.issubset(
        {0, 1}
    ):
        raise RuntimeError(
            f"{dataset_name} contains invalid labels: "
            f"{sorted(labels)}"
        )

    feature_frame = dataset[
        FEATURE_COLUMNS
    ]

    null_feature_count = int(
        feature_frame
        .isna()
        .sum()
        .sum()
    )

    if null_feature_count != 0:
        raise RuntimeError(
            f"{dataset_name} contains null feature "
            f"values: {null_feature_count}"
        )

    invalid_feature_mask = (
        (feature_frame < 0)
        | (feature_frame > 1)
    )

    invalid_feature_count = int(
        invalid_feature_mask
        .sum()
        .sum()
    )

    if invalid_feature_count != 0:
        raise RuntimeError(
            f"{dataset_name} contains feature values "
            "outside [0, 1]: "
            f"{invalid_feature_count}"
        )

    return {
        "required_columns_valid": True,
        "metadata_non_null": True,
        "labels_binary": True,
        "features_non_null": True,
        "features_in_range": True,
        "query_candidate_pairs_unique": True,
        "duplicate_query_candidate_pairs": (
            duplicate_pair_count
        ),
        "null_feature_values": (
            null_feature_count
        ),
        "invalid_feature_values": (
            invalid_feature_count
        ),
    }


def validate_full_dataset(
    *,
    dataset: pd.DataFrame,
    discovered_demande_version_ids: tuple[
        int,
        ...
    ],
) -> dict[str, Any]:
    """
    Validate full reconstructed dataset.

    Every discovered generated demande version is expected to
    be represented unless its canonical candidate set is empty.
    """
    validation = (
        validate_common_dataset_structure(
            dataset=dataset,
            dataset_name=(
                "Full reconstructed dataset"
            ),
        )
    )

    dataset_ids = set(
        dataset[
            "id_demande_version"
        ]
        .astype(int)
        .unique()
        .tolist()
    )

    discovered_ids = set(
        discovered_demande_version_ids
    )

    unexpected_ids = (
        dataset_ids
        - discovered_ids
    )

    if unexpected_ids:
        raise RuntimeError(
            "Full dataset contains unexpected demande "
            "versions: "
            + ", ".join(
                str(value)
                for value in sorted(
                    unexpected_ids
                )
            )
        )

    missing_ids = (
        discovered_ids
        - dataset_ids
    )

    validation[
        "discovered_groups"
    ] = len(
        discovered_ids
    )

    validation[
        "represented_groups"
    ] = len(
        dataset_ids
    )

    validation[
        "missing_groups"
    ] = sorted(
        missing_ids
    )

    validation[
        "represented_groups_subset_of_discovered_scope"
    ] = True

    return validation


def validate_training_dataset(
    *,
    dataset: pd.DataFrame,
    discovered_demande_version_ids: tuple[
        int,
        ...
    ],
) -> dict[str, Any]:
    """
    Validate informative supervised training dataset.

    Every retained group must contain both classes.
    """
    validation = (
        validate_common_dataset_structure(
            dataset=dataset,
            dataset_name=(
                "Informative training dataset"
            ),
        )
    )

    group_class_counts = (
        dataset
        .groupby(
            "id_demande_version"
        )[LABEL_COLUMN]
        .nunique()
    )

    invalid_groups = (
        group_class_counts[
            group_class_counts != 2
        ]
        .index
        .astype(int)
        .tolist()
    )

    if invalid_groups:
        raise RuntimeError(
            "Informative training dataset contains "
            "groups without both classes: "
            + ", ".join(
                str(value)
                for value in invalid_groups
            )
        )

    retained_ids = set(
        dataset[
            "id_demande_version"
        ]
        .astype(int)
        .unique()
        .tolist()
    )

    discovered_ids = set(
        discovered_demande_version_ids
    )

    unexpected_ids = (
        retained_ids
        - discovered_ids
    )

    if unexpected_ids:
        raise RuntimeError(
            "Informative dataset contains demande "
            "versions outside discovered scope: "
            + ", ".join(
                str(value)
                for value in sorted(
                    unexpected_ids
                )
            )
        )

    validation[
        "all_retained_groups_have_both_classes"
    ] = True

    validation[
        "retained_groups_subset_of_discovered_scope"
    ] = True

    validation[
        "informative_group_count"
    ] = len(
        retained_ids
    )

    return validation


def build_group_diagnostics(
    dataset: pd.DataFrame,
) -> list[dict[str, Any]]:
    diagnostics: list[
        dict[str, Any]
    ] = []

    grouped = dataset.groupby(
        "id_demande_version",
        sort=True,
    )

    for (
        id_demande_version,
        group,
    ) in grouped:
        rows = int(
            len(group)
        )

        positives = int(
            group[
                LABEL_COLUMN
            ].sum()
        )

        negatives = (
            rows
            - positives
        )

        labels = sorted(
            group[
                LABEL_COLUMN
            ]
            .astype(int)
            .unique()
            .tolist()
        )

        source_recherche_ref = (
            group[
                "source_recherche_ref"
            ]
            .iloc[0]
        )

        ingestion_batch = (
            group[
                "ingestion_batch"
            ]
            .iloc[0]
        )

        diagnostics.append(
            {
                "id_demande_version": int(
                    id_demande_version
                ),
                "source_recherche_ref": str(
                    source_recherche_ref
                ),
                "ingestion_batch": (
                    None
                    if pd.isna(
                        ingestion_batch
                    )
                    else str(
                        ingestion_batch
                    )
                ),
                "rows": rows,
                "positives": positives,
                "negatives": negatives,
                "positive_rate": (
                    positives / rows
                    if rows
                    else 0.0
                ),
                "labels": labels,
                "informative": (
                    labels == [0, 1]
                ),
            }
        )

    return diagnostics


def build_batch_diagnostics(
    *,
    generated_demande_versions: list[
        dict[str, Any]
    ],
    full_dataset: pd.DataFrame,
) -> list[dict[str, Any]]:
    discovery_frame = pd.DataFrame(
        generated_demande_versions
    )

    dataset_summary_by_batch = (
        full_dataset
        .groupby(
            "ingestion_batch"
        )
        .agg(
            groups=(
                "id_demande_version",
                "nunique",
            ),
            rows=(
                "reference_externe",
                "size",
            ),
            positives=(
                LABEL_COLUMN,
                "sum",
            ),
        )
        .reset_index()
    )

    dataset_summary_by_batch[
        "negatives"
    ] = (
        dataset_summary_by_batch[
            "rows"
        ]
        - dataset_summary_by_batch[
            "positives"
        ]
    )

    discovered_by_batch = (
        discovery_frame
        .groupby(
            "ingestion_batch"
        )[
            "id_demande_version"
        ]
        .nunique()
        .to_dict()
    )

    diagnostics: list[
        dict[str, Any]
    ] = []

    for _, row in (
        dataset_summary_by_batch
        .sort_values(
            "ingestion_batch"
        )
        .iterrows()
    ):
        batch = str(
            row[
                "ingestion_batch"
            ]
        )

        diagnostics.append(
            {
                "ingestion_batch": batch,
                "discovered_groups": int(
                    discovered_by_batch.get(
                        batch,
                        0,
                    )
                ),
                "represented_groups": int(
                    row[
                        "groups"
                    ]
                ),
                "rows": int(
                    row[
                        "rows"
                    ]
                ),
                "positives": int(
                    row[
                        "positives"
                    ]
                ),
                "negatives": int(
                    row[
                        "negatives"
                    ]
                ),
            }
        )

    return diagnostics


def write_validation_artifact(
    *,
    output_dir: Path,
    generated_demande_versions: list[
        dict[str, Any]
    ],
    full_summary: dict[str, Any],
    training_summary: dict[str, Any],
    full_validation: dict[str, Any],
    training_validation: dict[str, Any],
    full_group_diagnostics: list[
        dict[str, Any]
    ],
    training_group_diagnostics: list[
        dict[str, Any]
    ],
    batch_diagnostics: list[
        dict[str, Any]
    ],
    gitlab_traceability: dict[
        str,
        str,
    ],
) -> Path:
    artifact_path = (
        output_dir
        / "training_dataset_validation.json"
    )

    discovered_ids = [
        int(
            item[
                "id_demande_version"
            ]
        )
        for item in generated_demande_versions
    ]

    artifact = {
        "timestamp_utc": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "validation_type": (
            "supervised-matching-dataset"
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
        "generated_batches_discovered": (
            count_generated_batches(
                generated_demande_versions
            )
        ),
        "generated_demande_versions_discovered": (
            len(
                generated_demande_versions
            )
        ),
        "discovered_demande_version_ids": (
            discovered_ids
        ),
        "full_dataset_summary": (
            full_summary
        ),
        "informative_training_dataset_summary": (
            training_summary
        ),
        "single_class_groups": (
            int(
                full_summary[
                    "groups"
                ]
            )
            - int(
                training_summary[
                    "groups"
                ]
            )
        ),
        "full_dataset_validation": (
            full_validation
        ),
        "informative_training_dataset_validation": (
            training_validation
        ),
        "batch_diagnostics": (
            batch_diagnostics
        ),
        "full_group_diagnostics": (
            full_group_diagnostics
        ),
        "informative_group_diagnostics": (
            training_group_diagnostics
        ),
        "feature_columns": list(
            FEATURE_COLUMNS
        ),
        "label_column": (
            LABEL_COLUMN
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


def print_validation_summary(
    *,
    generated_demande_versions: list[
        dict[str, Any]
    ],
    full_summary: dict[str, Any],
    training_summary: dict[str, Any],
    batch_diagnostics: list[
        dict[str, Any]
    ],
    training_group_diagnostics: list[
        dict[str, Any]
    ],
    artifact_path: Path,
) -> None:
    generated_batches = (
        count_generated_batches(
            generated_demande_versions
        )
    )

    single_class_groups = (
        int(
            full_summary[
                "groups"
            ]
        )
        - int(
            training_summary[
                "groups"
            ]
        )
    )

    print()
    print(
        "=============================================="
    )
    print(
        "Supervised matching dataset validation"
    )
    print(
        "=============================================="
    )

    print(
        "Generated batches discovered: "
        f"{generated_batches}"
    )

    print(
        "Generated demande versions discovered: "
        f"{len(generated_demande_versions)}"
    )

    print()
    print(
        "FULL RECONSTRUCTED DATASET"
    )
    print(
        "----------------------------------------------"
    )

    print(
        "Groups: "
        f"{full_summary['groups']}"
    )

    print(
        "Rows: "
        f"{full_summary['rows']}"
    )

    print(
        "Positive labels: "
        f"{full_summary['positives']}"
    )

    print(
        "Negative labels: "
        f"{full_summary['negatives']}"
    )

    print(
        "Positive rate: "
        f"{float(full_summary['positive_rate']):.6f}"
    )

    print()
    print(
        "INFORMATIVE TRAINING DATASET"
    )
    print(
        "----------------------------------------------"
    )

    print(
        "Groups: "
        f"{training_summary['groups']}"
    )

    print(
        "Rows: "
        f"{training_summary['rows']}"
    )

    print(
        "Positive labels: "
        f"{training_summary['positives']}"
    )

    print(
        "Negative labels: "
        f"{training_summary['negatives']}"
    )

    print(
        "Positive rate: "
        f"{float(training_summary['positive_rate']):.6f}"
    )

    print(
        "Single-class groups excluded from training: "
        f"{single_class_groups}"
    )

    print()
    print(
        "BATCH DIAGNOSTICS"
    )
    print(
        "----------------------------------------------"
    )

    for batch in batch_diagnostics:
        print(
            f"  {batch['ingestion_batch']}: "
            f"groups="
            f"{batch['represented_groups']}/"
            f"{batch['discovered_groups']}, "
            f"rows={batch['rows']}, "
            f"positive={batch['positives']}, "
            f"negative={batch['negatives']}"
        )

    print()
    print(
        "INFORMATIVE GROUP DIAGNOSTICS"
    )
    print(
        "----------------------------------------------"
    )

    for group in (
        training_group_diagnostics
    ):
        print(
            "  DV "
            f"{group['id_demande_version']}: "
            f"rows={group['rows']}, "
            f"positive={group['positives']}, "
            f"negative={group['negatives']}, "
            f"source={group['source_recherche_ref']}, "
            f"batch={group['ingestion_batch']}"
        )

    print()
    print(
        "Validation artifact: "
        f"{artifact_path}"
    )


def main() -> None:
    print(
        "===== Real Estate Training Dataset "
        "Validation Started ====="
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

        print(
            "Generated batches discovered: "
            f"{count_generated_batches(generated_demande_versions)}"
        )

        print(
            "Generated demande versions discovered: "
            f"{len(demande_version_ids)}"
        )

        print()
        print(
            "Building full reconstructed dataset..."
        )

        full_dataset = (
            build_training_dataset(
                connection=connection,
                demande_version_ids=(
                    demande_version_ids
                ),
                require_both_classes=False,
            )
        )

        print(
            "Building informative training dataset..."
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

        full_summary = dataset_summary(
            full_dataset
        )

        training_summary = (
            dataset_summary(
                training_dataset
            )
        )

        full_validation = (
            validate_full_dataset(
                dataset=full_dataset,
                discovered_demande_version_ids=(
                    demande_version_ids
                ),
            )
        )

        training_validation = (
            validate_training_dataset(
                dataset=training_dataset,
                discovered_demande_version_ids=(
                    demande_version_ids
                ),
            )
        )

        full_group_diagnostics = (
            build_group_diagnostics(
                full_dataset
            )
        )

        training_group_diagnostics = (
            build_group_diagnostics(
                training_dataset
            )
        )

        batch_diagnostics = (
            build_batch_diagnostics(
                generated_demande_versions=(
                    generated_demande_versions
                ),
                full_dataset=(
                    full_dataset
                ),
            )
        )

        artifact_path = (
            write_validation_artifact(
                output_dir=output_dir,
                generated_demande_versions=(
                    generated_demande_versions
                ),
                full_summary=(
                    full_summary
                ),
                training_summary=(
                    training_summary
                ),
                full_validation=(
                    full_validation
                ),
                training_validation=(
                    training_validation
                ),
                full_group_diagnostics=(
                    full_group_diagnostics
                ),
                training_group_diagnostics=(
                    training_group_diagnostics
                ),
                batch_diagnostics=(
                    batch_diagnostics
                ),
                gitlab_traceability=(
                    gitlab_traceability
                ),
            )
        )

        print_validation_summary(
            generated_demande_versions=(
                generated_demande_versions
            ),
            full_summary=(
                full_summary
            ),
            training_summary=(
                training_summary
            ),
            batch_diagnostics=(
                batch_diagnostics
            ),
            training_group_diagnostics=(
                training_group_diagnostics
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
        "Structural dataset validation: PASSED"
    )

    print(
        "Model training performed: False"
    )

    print()
    print(
        "===== Real Estate Training Dataset "
        "Validation Completed Successfully ====="
    )


if __name__ == "__main__":
    main()