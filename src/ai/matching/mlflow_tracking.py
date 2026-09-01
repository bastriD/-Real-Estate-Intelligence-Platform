from __future__ import annotations

from typing import Any

import mlflow

from src.ai.matching.evaluate import MatchingEvaluationResult


DEFAULT_EXPERIMENT_NAME = "real-estate-deterministic-matching"


def configure_mlflow(
    tracking_uri: str,
    experiment_name: str = DEFAULT_EXPERIMENT_NAME,
) -> None:
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)


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
        "id_demande_version": str(result.id_demande_version),
        "data_type": "generated-synthetic-project-data",
        "training_required": "false",
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
        "nb_pieces_min": demande.get("nb_pieces_min"),
        "nb_chambres_min": demande.get("nb_chambres_min"),
        "dpe_max": demande.get("dpe_max"),
    }

    parameters = {
        key: value
        for key, value in parameters.items()
        if value is not None
    }

    metrics = {
        "properties_loaded": float(result.properties_loaded),
        "candidates_after_filtering": float(
            result.candidates_after_filtering
        ),
    }

    if not result.ranked.empty:
        metrics["top_matching_score"] = float(
            result.ranked.iloc[0]["matching_score"]
        )

        metrics["mean_matching_score"] = float(
            result.ranked["matching_score"].mean()
        )

        metrics["median_matching_score"] = float(
            result.ranked["matching_score"].median()
        )

    with mlflow.start_run(run_name=run_name) as run:
        mlflow.set_tags(tags)
        mlflow.log_params(parameters)
        mlflow.log_metrics(metrics)

        return run.info.run_id