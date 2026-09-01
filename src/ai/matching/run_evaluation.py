from __future__ import annotations

import json
import os

from datetime import datetime, timezone
from pathlib import Path

import mlflow
import psycopg

from src.ai.matching.evaluate import evaluate_demande_version
from src.ai.matching.mlflow_tracking import log_deterministic_evaluation


TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://mlflow-tracking.mlflow.svc.cluster.local:5000",
)

EXPERIMENT_NAME = os.getenv(
    "MLFLOW_EXPERIMENT_NAME",
    "real-estate-deterministic-matching",
)

DEMANDE_VERSION_ID = int(
    os.getenv("MATCHING_DEMANDE_VERSION_ID", "54")
)

DATABASE_HOST = os.getenv(
    "POSTGRES_HOST",
    "real-estate-postgresql.real-estate.svc.cluster.local",
)
DATABASE_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DATABASE_NAME = os.getenv("POSTGRES_DB", "real_estate")
DATABASE_USER = os.getenv("POSTGRES_USER")
DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD")


def main() -> None:
    print("===== Real Estate Matching Evaluation Started =====")
    print(f"MLflow Tracking URI: {TRACKING_URI}")
    print(f"MLflow Experiment: {EXPERIMENT_NAME}")
    print(f"DemandeVersion: {DEMANDE_VERSION_ID}")

    if not DATABASE_USER:
        raise RuntimeError("POSTGRES_USER is required")

    if not DATABASE_PASSWORD:
        raise RuntimeError("POSTGRES_PASSWORD is required")

    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    connection = psycopg.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
    )

    try:
        result = evaluate_demande_version(
            connection=connection,
            id_demande_version=DEMANDE_VERSION_ID,
        )
    finally:
        connection.close()

    run_name = f"matching-baseline-dv-{DEMANDE_VERSION_ID}"

    run_id = log_deterministic_evaluation(
        result,
        run_name=run_name,
        extra_tags={
            "project": "chasse_immobiliere",
            "platform": "enterprise-homelab",
            "execution_mode": "kubernetes-job",
            "evaluation_type": "deterministic-baseline",
            "model_registry_enabled": "false",
        },
    )

    ranked_path = output_dir / "ranked_candidates.csv"
    metadata_path = output_dir / "evaluation_metadata.json"

    result.ranked.to_csv(
        ranked_path,
        index=False,
    )

    metadata = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_name": EXPERIMENT_NAME,
        "tracking_uri": TRACKING_URI,
        "id_demande_version": DEMANDE_VERSION_ID,
        "properties_loaded": result.properties_loaded,
        "candidates_after_filtering": result.candidates_after_filtering,
        "top_matching_score": (
            float(result.ranked.iloc[0]["matching_score"])
            if not result.ranked.empty
            else None
        ),
        "baseline_type": "deterministic-weighted-rules",
        "data_type": "generated-synthetic-project-data",
        "model_training": False,
        "model_registry": False,
    }

    with open(
        metadata_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False,
        )

    with mlflow.start_run(run_id=run_id):
        mlflow.log_artifact(
            str(ranked_path),
            artifact_path="evaluation",
        )

        mlflow.log_artifact(
            str(metadata_path),
            artifact_path="evaluation",
        )

    print("===== Matching evaluation completed successfully =====")
    print(f"MLflow Run ID: {run_id}")
    print(f"Properties loaded: {result.properties_loaded}")
    print(
        "Candidates after filtering: "
        f"{result.candidates_after_filtering}"
    )

    if not result.ranked.empty:
        print(
            "Top matching score: "
            f"{result.ranked.iloc[0]['matching_score']}"
        )

    print(f"Artifacts logged under run: {run_id}")


if __name__ == "__main__":
    main()