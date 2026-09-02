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
    create_group_aware_split,
    split_summary,
)
from src.ai.matching.model_comparison import (
    compare_rankers,
)
from src.ai.matching.model_training import (
    train_and_evaluate_logistic_regression,
)
from src.ai.matching.run_model_training import (
    validate_frozen_split,
)
from src.ai.matching.run_training_dataset_split import (
    validate_split_against_source,
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


OUTPUT_FILENAME = "matching_model_comparison.json"


def _serializable_metrics(
    value: Any,
) -> Any:
    """
    Convert nested metric structures into JSON-safe Python values.
    """

    if isinstance(value, dict):
        return {
            str(key): _serializable_metrics(
                item
            )
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _serializable_metrics(
                item
            )
            for item in value
        ]

    if hasattr(value, "item"):
        return value.item()

    return value


def write_comparison_artifact(
    *,
    output_dir: Path,
    generated_batches: int,
    generated_demande_versions: int,
    informative_summary: dict[str, Any],
    split_information: dict[str, Any],
    validation_comparison: dict[str, Any],
    test_comparison: dict[str, Any],
    gitlab_traceability: dict[str, str],
) -> Path:
    """
    Persist evidence of the fair deterministic-vs-ML comparison.

    No raw training dataset is persisted.
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
            "deterministic-vs-supervised-matching-comparison"
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
        "hard_eligibility_preserved": True,
        "candidate_population_identical": True,
        "comparison_basis": (
            "same-groups-same-candidates-same-ground-truth"
        ),
        "comparison_scope": [
            "validation",
            "test",
        ],
        "training_partition_used_for_comparison": False,
        "generated_batches_discovered": (
            generated_batches
        ),
        "generated_demande_versions_discovered": (
            generated_demande_versions
        ),
        "informative_dataset_summary": (
            informative_summary
        ),
        "split": split_information,
        "validation": (
            validation_comparison
        ),
        "test": test_comparison,
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
            _serializable_metrics(
                artifact
            ),
            file,
            indent=2,
            ensure_ascii=False,
        )

    return artifact_path


def print_partition_comparison(
    *,
    name: str,
    comparison: dict[str, Any],
) -> None:
    """
    Print the macro ranking comparison for one frozen partition.
    """

    deterministic = comparison[
        "deterministic"
    ]["macro_average"]

    supervised = comparison[
        "supervised_ml"
    ]["macro_average"]

    deltas = comparison[
        "delta_ml_minus_deterministic"
    ]

    print()
    print(
        f"{name} RANKING COMPARISON"
    )
    print(
        "=============================================="
    )

    print(
        "Candidate population identical: "
        f"{comparison['candidate_population_identical']}"
    )

    print(
        "Ground truth identical: "
        f"{comparison['ground_truth_identical']}"
    )

    print(
        "Hard eligibility identical: "
        f"{comparison['hard_eligibility_identical']}"
    )

    print(
        "Metric semantics identical: "
        f"{comparison['metric_semantics_identical']}"
    )

    print()

    print(
        f"{'Metric':<24}"
        f"{'Deterministic':>16}"
        f"{'ML':>16}"
        f"{'Delta ML-DET':>16}"
    )

    print(
        "-" * 72
    )

    for metric_name in sorted(
        deltas
    ):
        print(
            f"{metric_name:<24}"
            f"{deterministic[metric_name]:>16.6f}"
            f"{supervised[metric_name]:>16.6f}"
            f"{deltas[metric_name]:>16.6f}"
        )

    print()

    summary = comparison[
        "summary"
    ]

    print(
        "ML metric wins: "
        f"{summary['ml_metric_wins']}"
    )

    print(
        "Deterministic metric wins: "
        f"{summary['deterministic_metric_wins']}"
    )

    print(
        "Ties: "
        f"{summary['ties']}"
    )


def main() -> None:
    print(
        "===== Real Estate Deterministic vs ML "
        "Comparison Started ====="
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

    print()
    print(
        "Comparison policy:"
    )
    print(
        "  same frozen validation/test groups"
    )
    print(
        "  same hard-eligible candidate population"
    )
    print(
        "  same explicit-lineage ground truth"
    )
    print(
        "  same canonical ranking metrics"
    )
    print(
        "  no training on validation/test"
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
            for item in generated_demande_versions
        )

        generated_batches = (
            count_generated_batches(
                generated_demande_versions
            )
        )

        print()
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
            "Reconstructing informative supervised dataset..."
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
            "Informative groups: "
            f"{informative_summary['groups']}"
        )

        print(
            "Informative rows: "
            f"{informative_summary['rows']}"
        )

        print()
        print(
            "Recreating frozen group-aware split..."
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

        validate_frozen_split(
            split
        )

        print(
            "Frozen split validation: PASSED"
        )

        split_information = (
            split_summary(
                split
            )
        )

        print(
            "TRAIN groups: "
            f"{list(split.train_groups)}"
        )

        print(
            "VALIDATION groups: "
            f"{list(split.validation_groups)}"
        )

        print(
            "TEST groups: "
            f"{list(split.test_groups)}"
        )

        print()
        print(
            "Training supervised baseline on TRAIN only..."
        )

        model_result = (
            train_and_evaluate_logistic_regression(
                split
            )
        )

        print(
            "Supervised baseline training: COMPLETED"
        )

        print()
        print(
            "Comparing rankers on frozen VALIDATION..."
        )

        validation_comparison = (
            compare_rankers(
                dataset=split.validation,
                ml_predictions=(
                    model_result.validation_predictions
                ),
            )
        )

        print(
            "Comparing rankers on frozen TEST..."
        )

        test_comparison = (
            compare_rankers(
                dataset=split.test,
                ml_predictions=(
                    model_result.test_predictions
                ),
            )
        )

        print_partition_comparison(
            name="VALIDATION",
            comparison=(
                validation_comparison
            ),
        )

        print_partition_comparison(
            name="TEST",
            comparison=(
                test_comparison
            ),
        )

        artifact_path = (
            write_comparison_artifact(
                output_dir=output_dir,
                generated_batches=(
                    generated_batches
                ),
                generated_demande_versions=(
                    len(
                        generated_demande_versions
                    )
                ),
                informative_summary=(
                    informative_summary
                ),
                split_information={
                    "summary": (
                        split_information
                    ),
                    "validation": (
                        split_validation
                    ),
                },
                validation_comparison=(
                    validation_comparison
                ),
                test_comparison=(
                    test_comparison
                ),
                gitlab_traceability=(
                    gitlab_traceability
                ),
            )
        )

        print()
        print(
            "Comparison artifact: "
            f"{artifact_path}"
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
        "Fair deterministic-vs-ML comparison: PASSED"
    )

    print(
        "Model promotion performed: False"
    )

    print(
        "Model Registry registration performed: False"
    )

    print()
    print(
        "===== Real Estate Deterministic vs ML "
        "Comparison Completed Successfully ====="
    )


if __name__ == "__main__":
    main()