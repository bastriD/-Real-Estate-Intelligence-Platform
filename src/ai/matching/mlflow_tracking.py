from __future__ import annotations

import json
import shutil
import tempfile

from pathlib import Path
from typing import Any

import mlflow
import mlflow.sklearn
import pandas as pd

from src.ai.matching.evaluate import MatchingEvaluationResult


DEFAULT_EXPERIMENT_NAME = "real-estate-deterministic-matching"

DEFAULT_SUPERVISED_EXPERIMENT_NAME = (
    "real-estate-supervised-matching"
)


def configure_mlflow(
    tracking_uri: str,
    experiment_name: str = DEFAULT_EXPERIMENT_NAME,
) -> None:
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)


def _clean_parameter(value: Any) -> Any | None:
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    return value


def _flatten_metrics(
    metrics: dict[str, Any],
    *,
    prefix: str = "",
) -> dict[str, float]:
    flattened: dict[str, float] = {}

    for key, value in metrics.items():
        metric_name = (
            f"{prefix}_{key}"
            if prefix
            else str(key)
        )

        if isinstance(value, dict):
            flattened.update(
                _flatten_metrics(
                    value,
                    prefix=metric_name,
                )
            )
            continue

        if isinstance(value, bool):
            continue

        if isinstance(value, (int, float)):
            flattened[metric_name] = float(value)

    return flattened


def log_deterministic_evaluation(
    result: MatchingEvaluationResult,
    *,
    run_name: str | None = None,
    extra_tags: dict[str, Any] | None = None,
) -> str:
    demande = result.demande

    tags = {
        "model_family": "deterministic",
        "model_type": "weighted-rule-baseline",
        "business_use_case": "property-matching",
        "id_demande_version": str(
            result.id_demande_version
        ),
        "data_type": "generated-synthetic-project-data",
        "training_required": "false",
        "evaluation_ground_truth": "explicit-lineage",
        "ground_truth_used_for_scoring": "false",
        "ranking_evaluation": "true",
    }

    if extra_tags:
        tags.update(
            {
                str(key): str(value)
                for key, value in extra_tags.items()
            }
        )

    parameters = {
        "ville": demande.get("ville"),
        "code_postal": demande.get("code_postal"),
        "type_bien": demande.get("type_bien"),
        "budget_min": demande.get("budget_min"),
        "budget_max": demande.get("budget_max"),
        "surface_min": demande.get("surface_min"),
        "nb_pieces_min": demande.get(
            "nb_pieces_min"
        ),
        "nb_chambres_min": demande.get(
            "nb_chambres_min"
        ),
        "dpe_max": demande.get("dpe_max"),
        "source_recherche_ref": demande.get(
            "source_recherche_ref"
        ),
        "ingestion_batch": demande.get(
            "ingestion_batch"
        ),
    }

    parameters = {
        key: cleaned_value
        for key, value in parameters.items()
        if (
            cleaned_value := _clean_parameter(
                value
            )
        )
        is not None
    }

    metrics: dict[str, float] = {
        "properties_loaded": float(
            result.properties_loaded
        ),
        "candidates_after_filtering": float(
            result.candidates_after_filtering
        ),
        "ground_truth_total": float(
            result.ground_truth_total
        ),
        "ground_truth_in_candidates": float(
            result.ground_truth_in_candidates
        ),
        "candidate_recall": float(
            result.candidate_recall
        ),
    }

    metrics.update(
        {
            str(metric_name): float(metric_value)
            for metric_name, metric_value
            in result.ranking_metrics.items()
        }
    )

    if not result.ranked.empty:
        if "matching_score" not in result.ranked.columns:
            raise ValueError(
                "Ranked matching results do not contain "
                "'matching_score'."
            )

        metrics["top_matching_score"] = float(
            result.ranked.iloc[0][
                "matching_score"
            ]
        )

        metrics["mean_matching_score"] = float(
            result.ranked[
                "matching_score"
            ].mean()
        )

        metrics["median_matching_score"] = float(
            result.ranked[
                "matching_score"
            ].median()
        )

    with mlflow.start_run(
        run_name=run_name
    ) as run:
        mlflow.set_tags(tags)
        mlflow.log_params(parameters)
        mlflow.log_metrics(metrics)

        return run.info.run_id


def _save_and_log_sklearn_model_compatibly(
    *,
    model: Any,
) -> None:
    """
    Persist an sklearn model in a way compatible with MLflow 2.x servers.

    The project currently uses an MLflow 3.x Python client against an
    MLflow 2.16.2 tracking server. Calling mlflow.sklearn.log_model()
    from the newer client uses the logged-models API, which is not
    available on the older server.

    Therefore:
    1. save the MLflow sklearn model structure locally;
    2. upload the generated directory through the standard artifact API.

    This persists the model as a run artifact without using Model Registry
    or the MLflow 3 logged-models endpoint.
    """

    temporary_directory = Path(
        tempfile.mkdtemp(
            prefix="matching-mlflow-model-"
        )
    )

    model_directory = (
        temporary_directory
        / "model"
    )

    try:
        mlflow.sklearn.save_model(
            sk_model=model,
            path=str(model_directory),
        )

        mlflow.log_artifacts(
            local_dir=str(model_directory),
            artifact_path="model",
        )

    finally:
        shutil.rmtree(
            temporary_directory,
            ignore_errors=True,
        )


def log_supervised_training(
    *,
    model: Any,
    model_metadata: dict[str, Any],
    train_metrics: dict[str, Any],
    validation_metrics: dict[str, Any],
    test_metrics: dict[str, Any],
    split_summary: dict[str, Any],
    dataset_summary: dict[str, Any],
    gitlab_traceability: dict[str, Any],
    training_artifact_path: str | Path | None = None,
    run_name: str = (
        "matching-logistic-regression-baseline-v1"
    ),
    extra_tags: dict[str, Any] | None = None,
) -> str:
    """
    Log one supervised matching-model training run to MLflow.

    Records:
    - model identity and methodology
    - exact feature set
    - dataset summary
    - frozen group-aware split
    - train / validation / test metrics
    - coefficients and intercept
    - GitLab CI traceability
    - training evidence artifact
    - persisted sklearn model artifact

    The model is NOT registered or promoted.
    """

    tags: dict[str, str] = {
        "model_family": "supervised-ml",
        "model_type": "logistic-regression",
        "model_version": (
            "logistic-regression-baseline-v1"
        ),
        "business_use_case": "property-matching",
        "training_required": "true",
        "training_performed": "true",
        "ranking_evaluation": "true",
        "evaluation_ground_truth": "explicit-lineage",
        "ground_truth_used_for_scoring": "false",
        "candidate_engine": (
            "canonical-matching-repository"
        ),
        "hard_eligibility_preserved": "true",
        "split_strategy": (
            "group-aware-id-demande-version"
        ),
        "split_version": "frozen-v1",
        "data_source": (
            "postgresql-runtime-reconstruction"
        ),
        "model_promotion_status": "baseline",
        "model_artifact_format": "mlflow-sklearn",
        "model_registry_registered": "false",
    }

    if extra_tags:
        tags.update(
            {
                str(key): str(value)
                for key, value in extra_tags.items()
            }
        )

    features = model_metadata.get(
        "feature_columns",
        [],
    )

    parameters: dict[str, Any] = {
        "model_type": model_metadata.get(
            "model_type",
            "LogisticRegression",
        ),
        "model_library": model_metadata.get(
            "model_library",
            "scikit-learn",
        ),
        "feature_count": len(features),
        "features": ",".join(
            str(feature)
            for feature in features
        ),
        "label_column": model_metadata.get(
            "label_column",
            "relevance_label",
        ),
        "group_column": model_metadata.get(
            "group_column",
            "id_demande_version",
        ),
        "reference_column": model_metadata.get(
            "reference_column",
            "reference_externe",
        ),
        "classification_threshold": (
            model_metadata.get(
                "classification_threshold",
                0.5,
            )
        ),
        "random_state": 42,
        "split_version": "frozen-v1",
    }

    for split_name in (
        "train",
        "validation",
        "test",
    ):
        split_details = split_summary.get(
            split_name,
            {},
        )

        groups = split_details.get(
            "groups",
            [],
        )

        parameters[
            f"{split_name}_group_ids"
        ] = ",".join(
            str(group)
            for group in groups
        )

        for source_key, parameter_key in (
            ("group_count", "group_count"),
            ("rows", "rows"),
            ("positives", "positives"),
            ("negatives", "negatives"),
        ):
            if source_key in split_details:
                parameters[
                    f"{split_name}_{parameter_key}"
                ] = split_details[source_key]

    coefficients = model_metadata.get(
        "coefficients",
        {},
    )

    if isinstance(coefficients, dict):
        for feature_name, coefficient in (
            coefficients.items()
        ):
            parameters[
                f"coef_{feature_name}"
            ] = float(coefficient)

    if "intercept" in model_metadata:
        parameters["intercept"] = float(
            model_metadata["intercept"]
        )

    for source_key, parameter_key in (
        ("groups", "groups"),
        ("rows", "rows"),
        ("positives", "positives"),
        ("negatives", "negatives"),
        ("positive_rate", "positive_rate"),
    ):
        if source_key in dataset_summary:
            parameters[
                f"dataset_{parameter_key}"
            ] = dataset_summary[source_key]

    for key, value in (
        gitlab_traceability.items()
    ):
        if value not in (None, ""):
            parameters[
                f"gitlab_{key}"
            ] = str(value)

    cleaned_parameters = {
        key: cleaned_value
        for key, value in parameters.items()
        if (
            cleaned_value := _clean_parameter(
                value
            )
        )
        is not None
    }

    metrics: dict[str, float] = {}

    metrics.update(
        _flatten_metrics(
            train_metrics,
            prefix="train",
        )
    )

    metrics.update(
        _flatten_metrics(
            validation_metrics,
            prefix="validation",
        )
    )

    metrics.update(
        _flatten_metrics(
            test_metrics,
            prefix="test",
        )
    )

    with mlflow.start_run(
        run_name=run_name
    ) as run:
        mlflow.set_tags(tags)

        mlflow.log_params(
            cleaned_parameters
        )

        mlflow.log_metrics(
            metrics
        )

        if training_artifact_path is not None:
            artifact_path = Path(
                training_artifact_path
            )

            if artifact_path.exists():
                mlflow.log_artifact(
                    str(artifact_path),
                    artifact_path="evidence",
                )

        with tempfile.TemporaryDirectory(
            prefix="matching-mlflow-evidence-"
        ) as temporary_directory:
            model_metadata_artifact = (
                Path(temporary_directory)
                / "matching_supervised_model_metadata.json"
            )

            model_metadata_artifact.write_text(
                json.dumps(
                    {
                        "model_metadata": (
                            model_metadata
                        ),
                        "dataset_summary": (
                            dataset_summary
                        ),
                        "split_summary": (
                            split_summary
                        ),
                        "gitlab_traceability": (
                            gitlab_traceability
                        ),
                    },
                    indent=2,
                    sort_keys=True,
                    default=str,
                ),
                encoding="utf-8",
            )

            mlflow.log_artifact(
                str(model_metadata_artifact),
                artifact_path="evidence",
            )

        _save_and_log_sklearn_model_compatibly(
            model=model,
        )

        return run.info.run_id