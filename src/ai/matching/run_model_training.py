from __future__ import annotations

import json
import os

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
from src.ai.matching.mlflow_tracking import (
    DEFAULT_SUPERVISED_EXPERIMENT_NAME,
    configure_mlflow,
    log_supervised_training,
)
from src.ai.matching.model_training import (
    model_metadata,
    train_and_evaluate_logistic_regression,
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
    FEATURE_COLUMNS,
    LABEL_COLUMN,
    build_training_dataset,
    dataset_summary,
)


TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://mlflow-tracking.mlflow.svc.cluster.local:5000",
)

EXPERIMENT_NAME = os.getenv(
    "MLFLOW_EXPERIMENT_NAME",
    DEFAULT_SUPERVISED_EXPERIMENT_NAME,
)

OUTPUT_FILENAME = "matching_logistic_regression_training.json"


def _serializable_metrics(
    metrics: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize nested metric structures into JSON-safe Python values.
    """

    if isinstance(metrics, dict):
        return {
            str(key): _serializable_metrics(value)
            for key, value in metrics.items()
        }

    if isinstance(metrics, list):
        return [
            _serializable_metrics(value)
            for value in metrics
        ]

    if isinstance(metrics, tuple):
        return [
            _serializable_metrics(value)
            for value in metrics
        ]

    if hasattr(metrics, "item"):
        return metrics.item()

    return metrics


def validate_frozen_split(
    *,
    split_details: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the expected reproducible V1 group-aware split.

    These group assignments were previously validated against the real
    PostgreSQL dataset and are intentionally frozen for fair comparisons.
    """

    expected_train_groups = {
        91,
        101,
        55,
        109,
        68,
        78,
        66,
    }

    expected_validation_groups = {
        70,
        105,
    }

    expected_test_groups = {
        60,
        102,
    }

    train_groups = set(
        int(value)
        for value in split_details[
            "train"
        ][
            "groups"
        ]
    )

    validation_groups = set(
        int(value)
        for value in split_details[
            "validation"
        ][
            "groups"
        ]
    )

    test_groups = set(
        int(value)
        for value in split_details[
            "test"
        ][
            "groups"
        ]
    )

    if train_groups != expected_train_groups:
        raise RuntimeError(
            "Frozen TRAIN group assignment changed. "
            f"Expected {sorted(expected_train_groups)}, "
            f"found {sorted(train_groups)}."
        )

    if validation_groups != expected_validation_groups:
        raise RuntimeError(
            "Frozen VALIDATION group assignment changed. "
            f"Expected {sorted(expected_validation_groups)}, "
            f"found {sorted(validation_groups)}."
        )

    if test_groups != expected_test_groups:
        raise RuntimeError(
            "Frozen TEST group assignment changed. "
            f"Expected {sorted(expected_test_groups)}, "
            f"found {sorted(test_groups)}."
        )

    overlap = (
        train_groups.intersection(
            validation_groups
        )
        | train_groups.intersection(
            test_groups
        )
        | validation_groups.intersection(
            test_groups
        )
    )

    if overlap:
        raise RuntimeError(
            "Group leakage detected in frozen split: "
            f"{sorted(overlap)}"
        )

    return {
        "frozen_split_v1": True,
        "random_state": DEFAULT_RANDOM_STATE,
        "train_groups_valid": True,
        "validation_groups_valid": True,
        "test_groups_valid": True,
        "group_leakage": False,
    }


def write_training_artifact(
    *,
    output_dir: Path,
    generated_demande_versions: list[
        dict[str, Any]
    ],
    informative_summary: dict[str, Any],
    split_details: dict[str, Any],
    frozen_split_validation: dict[str, Any],
    model_details: dict[str, Any],
    train_metrics: dict[str, Any],
    validation_metrics: dict[str, Any],
    test_metrics: dict[str, Any],
    gitlab_traceability: dict[str, str],
    mlflow_tracking: bool = False,
    mlflow_run_id: str | None = None,
) -> Path:
    """
    Write certification and MLOps evidence for the supervised baseline.
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
            "supervised-matching-model-training"
        ),
        "model_version": (
            "logistic-regression-baseline-v1"
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
        "lineage_metadata_used_as_feature": False,
        "group_metadata_used_as_feature": False,
        "model_training": True,
        "mlflow_tracking": mlflow_tracking,
        "mlflow_run_id": mlflow_run_id,
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
        "informative_dataset_summary": (
            _serializable_metrics(
                informative_summary
            )
        ),
        "split_configuration": {
            "strategy": (
                "group-aware-id-demande-version"
            ),
            "group_column": (
                "id_demande_version"
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
        },
        "split_summary": (
            _serializable_metrics(
                split_details
            )
        ),
        "frozen_split_validation": (
            frozen_split_validation
        ),
        "feature_columns": list(
            FEATURE_COLUMNS
        ),
        "label_column": (
            LABEL_COLUMN
        ),
        "model": (
            _serializable_metrics(
                model_details
            )
        ),
        "metrics": {
            "train": (
                _serializable_metrics(
                    train_metrics
                )
            ),
            "validation": (
                _serializable_metrics(
                    validation_metrics
                )
            ),
            "test": (
                _serializable_metrics(
                    test_metrics
                )
            ),
        },
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


def _print_classification_metrics(
    *,
    partition_name: str,
    metrics: dict[str, Any],
) -> None:
    classification = metrics[
        "classification"
    ]

    print(
        f"{partition_name} classification:"
    )

    for metric_name in (
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "average_precision",
        "log_loss",
    ):
        print(
            f"  {metric_name}: "
            f"{float(classification[metric_name]):.6f}"
        )


def _print_ranking_metrics(
    *,
    partition_name: str,
    metrics: dict[str, Any],
) -> None:
    ranking = metrics[
        "ranking"
    ]

    macro_average = ranking[
        "macro_average"
    ]

    print(
        f"{partition_name} ranking "
        "(macro average by demande_version):"
    )

    ranking_metric_names = [
        metric_name
        for metric_name in (
            macro_average.keys()
        )
        if (
            metric_name.startswith(
                "precision_at_"
            )
            or metric_name.startswith(
                "recall_at_"
            )
            or metric_name.startswith(
                "hit_rate_at_"
            )
            or metric_name.startswith(
                "ndcg_at_"
            )
        )
    ]

    def metric_sort_key(
        metric_name: str,
    ) -> tuple[int, int]:
        prefix_order = {
            "precision": 0,
            "recall": 1,
            "hit": 2,
            "ndcg": 3,
        }

        if metric_name.startswith(
            "hit_rate_at_"
        ):
            prefix = "hit"
            cutoff = int(
                metric_name.split(
                    "hit_rate_at_"
                )[1]
            )
        else:
            prefix = metric_name.split(
                "_at_"
            )[0]

            cutoff = int(
                metric_name.split(
                    "_at_"
                )[1]
            )

        return (
            prefix_order[
                prefix
            ],
            cutoff,
        )

    for metric_name in sorted(
        ranking_metric_names,
        key=metric_sort_key,
    ):
        print(
            f"  {metric_name}: "
            f"{float(macro_average[metric_name]):.6f}"
        )

    print(
        "  mrr: "
        f"{float(macro_average['mrr']):.6f}"
    )


def print_training_summary(
    *,
    informative_summary: dict[str, Any],
    split_details: dict[str, Any],
    model_details: dict[str, Any],
    train_metrics: dict[str, Any],
    validation_metrics: dict[str, Any],
    test_metrics: dict[str, Any],
    artifact_path: Path,
) -> None:
    print()
    print(
        "=============================================="
    )
    print(
        "Supervised Matching Model Training"
    )
    print(
        "=============================================="
    )

    print(
        "Model: LogisticRegression"
    )

    print(
        "Dataset groups: "
        f"{informative_summary['groups']}"
    )

    print(
        "Dataset rows: "
        f"{informative_summary['rows']}"
    )

    print()

    print(
        "FROZEN GROUP-AWARE SPLIT V1"
    )
    print(
        "----------------------------------------------"
    )

    for partition_name in (
        "train",
        "validation",
        "test",
    ):
        partition = split_details[
            partition_name
        ]

        print(
            f"{partition_name.upper()}: "
            f"groups={partition['groups']}, "
            f"rows={partition['rows']}, "
            f"positive={partition['positives']}, "
            f"negative={partition['negatives']}"
        )

    print()

    print(
        "MODEL FEATURES"
    )
    print(
        "----------------------------------------------"
    )

    for feature_name in (
        model_details[
            "feature_columns"
        ]
    ):
        print(
            f"  {feature_name}"
        )

    print()

    print(
        "MODEL COEFFICIENTS"
    )
    print(
        "----------------------------------------------"
    )

    for (
        feature_name,
        coefficient,
    ) in model_details[
        "coefficients"
    ].items():
        print(
            f"  {feature_name}: "
            f"{float(coefficient):.6f}"
        )

    print(
        "  intercept: "
        f"{float(model_details['intercept']):.6f}"
    )

    print()
    print(
        "TRAIN METRICS"
    )
    print(
        "----------------------------------------------"
    )

    _print_classification_metrics(
        partition_name="TRAIN",
        metrics=train_metrics,
    )

    _print_ranking_metrics(
        partition_name="TRAIN",
        metrics=train_metrics,
    )

    print()
    print(
        "VALIDATION METRICS"
    )
    print(
        "----------------------------------------------"
    )

    _print_classification_metrics(
        partition_name="VALIDATION",
        metrics=validation_metrics,
    )

    _print_ranking_metrics(
        partition_name="VALIDATION",
        metrics=validation_metrics,
    )

    print()
    print(
        "TEST METRICS"
    )
    print(
        "----------------------------------------------"
    )

    _print_classification_metrics(
        partition_name="TEST",
        metrics=test_metrics,
    )

    _print_ranking_metrics(
        partition_name="TEST",
        metrics=test_metrics,
    )

    print()
    print(
        "Training artifact: "
        f"{artifact_path}"
    )


def main() -> None:
    print(
        "===== Real Estate Supervised Matching "
        "Training Started ====="
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
        "Model: LogisticRegression"
    )

    print(
        "Split random state: "
        f"{DEFAULT_RANDOM_STATE}"
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

    print()
    print(
        "Configuring MLflow tracking..."
    )

    print(
        "MLflow tracking URI: "
        f"{TRACKING_URI}"
    )

    print(
        "MLflow experiment: "
        f"{EXPERIMENT_NAME}"
    )

    configure_mlflow(
        tracking_uri=TRACKING_URI,
        experiment_name=EXPERIMENT_NAME,
    )

    connection = psycopg.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
    )

    mlflow_run_id: str | None = None

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
            "Reconstructing informative supervised dataset..."
        )

        informative_dataset = (
            build_training_dataset(
                connection=connection,
                demande_version_ids=(
                    demande_version_ids
                ),
                require_both_classes=True,
            )
        )

        validate_training_dataset(
            dataset=informative_dataset,
            discovered_demande_version_ids=(
                demande_version_ids
            ),
        )

        informative_summary = (
            dataset_summary(
                informative_dataset
            )
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
            "Creating frozen group-aware split..."
        )

        split = create_group_aware_split(
            informative_dataset,
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

        split_details = split_summary(
            split
        )

        frozen_split_validation = (
            validate_frozen_split(
                split_details=(
                    split_details
                )
            )
        )

        print(
            "Frozen split validation: PASSED"
        )

        print()
        print(
            "Training Logistic Regression on TRAIN only..."
        )

        result = (
            train_and_evaluate_logistic_regression(
                split,
                random_state=(
                    DEFAULT_RANDOM_STATE
                ),
            )
        )

        model_details = (
            model_metadata(
                result
            )
        )

        artifact_path = (
            write_training_artifact(
                output_dir=output_dir,
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
                train_metrics=(
                    result.train_metrics
                ),
                validation_metrics=(
                    result.validation_metrics
                ),
                test_metrics=(
                    result.test_metrics
                ),
                gitlab_traceability=(
                    gitlab_traceability
                ),
                mlflow_tracking=False,
                mlflow_run_id=None,
            )
        )

        print_training_summary(
            informative_summary=(
                informative_summary
            ),
            split_details=(
                split_details
            ),
            model_details=(
                model_details
            ),
            train_metrics=(
                result.train_metrics
            ),
            validation_metrics=(
                result.validation_metrics
            ),
            test_metrics=(
                result.test_metrics
            ),
            artifact_path=(
                artifact_path
            ),
        )

        print()
        print(
            "Logging supervised training run to MLflow..."
        )

        mlflow_run_id = log_supervised_training(
            model=result.model,
            model_metadata=model_details,
            train_metrics=result.train_metrics,
            validation_metrics=(
                result.validation_metrics
            ),
            test_metrics=result.test_metrics,
            split_summary=split_details,
            dataset_summary=informative_summary,
            gitlab_traceability=gitlab_traceability,
            training_artifact_path=artifact_path,
            run_name=(
                "matching-logistic-regression-baseline-v1"
            ),
        )

        print(
            "MLflow training run created successfully."
        )

        print(
            "MLflow run ID: "
            f"{mlflow_run_id}"
        )

        artifact_path = (
            write_training_artifact(
                output_dir=output_dir,
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
                train_metrics=(
                    result.train_metrics
                ),
                validation_metrics=(
                    result.validation_metrics
                ),
                test_metrics=(
                    result.test_metrics
                ),
                gitlab_traceability=(
                    gitlab_traceability
                ),
                mlflow_tracking=True,
                mlflow_run_id=mlflow_run_id,
            )
        )

        print(
            "Training evidence artifact updated "
            "with MLflow run traceability."
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
        "Frozen group-aware split validation: PASSED"
    )

    print(
        "Model training performed: True"
    )

    print(
        "MLflow tracking performed: True"
    )

    print(
        "MLflow run ID: "
        f"{mlflow_run_id}"
    )

    print(
        "MLflow model artifact persisted: True"
    )

    print(
        "MLflow Model Registry registration: False"
    )

    print()
    print(
        "===== Real Estate Supervised Matching "
        "Training Completed Successfully ====="
    )


if __name__ == "__main__":
    main()