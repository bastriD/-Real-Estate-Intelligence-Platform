from __future__ import annotations

import json
import os

from datetime import datetime, timezone
from pathlib import Path

import mlflow
import psycopg

from src.ai.matching.evaluate import (
    MatchingEvaluationResult,
    evaluate_demande_version,
)
from src.ai.matching.mlflow_tracking import (
    log_deterministic_evaluation,
)


TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://mlflow-tracking.mlflow.svc.cluster.local:5000",
)

EXPERIMENT_NAME = os.getenv(
    "MLFLOW_EXPERIMENT_NAME",
    "real-estate-deterministic-matching",
)

DEFAULT_DEMANDE_VERSION_IDS = (
    55,
    56,
    57,
    58,
    59,
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


def parse_demande_version_ids() -> tuple[int, ...]:
    """
    Resolve the demande versions to evaluate.

    Priority:
    1. MATCHING_DEMANDE_VERSION_IDS
       Example: 55,56,57,58,59

    2. MATCHING_DEMANDE_VERSION_ID
       Backward-compatible single-DV execution.

    3. Default generated evaluation suite:
       55,56,57,58,59
    """
    multiple_value = optional_env(
        "MATCHING_DEMANDE_VERSION_IDS"
    )

    if multiple_value is not None:
        raw_values = (
            item.strip()
            for item in multiple_value.split(",")
        )

        demande_version_ids: list[int] = []

        for raw_value in raw_values:
            if not raw_value:
                continue

            try:
                demande_version_id = int(
                    raw_value
                )
            except ValueError as exc:
                raise ValueError(
                    "MATCHING_DEMANDE_VERSION_IDS "
                    "must contain comma-separated integers. "
                    f"Invalid value: {raw_value!r}"
                ) from exc

            if demande_version_id <= 0:
                raise ValueError(
                    "Demande version IDs must be positive. "
                    f"Invalid value: {demande_version_id}"
                )

            demande_version_ids.append(
                demande_version_id
            )

        if not demande_version_ids:
            raise ValueError(
                "MATCHING_DEMANDE_VERSION_IDS "
                "did not contain any valid IDs."
            )

        unique_ids = tuple(
            dict.fromkeys(
                demande_version_ids
            )
        )

        return unique_ids

    single_value = optional_env(
        "MATCHING_DEMANDE_VERSION_ID"
    )

    if single_value is not None:
        try:
            demande_version_id = int(
                single_value
            )
        except ValueError as exc:
            raise ValueError(
                "MATCHING_DEMANDE_VERSION_ID "
                "must be an integer."
            ) from exc

        if demande_version_id <= 0:
            raise ValueError(
                "MATCHING_DEMANDE_VERSION_ID "
                "must be positive."
            )

        return (
            demande_version_id,
        )

    return DEFAULT_DEMANDE_VERSION_IDS


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

    for tag_name, env_name in mapping.items():
        value = optional_env(
            env_name
        )

        if value is not None:
            traceability[
                tag_name
            ] = value

    return traceability


def matching_score_statistics(
    result: MatchingEvaluationResult,
) -> dict[str, float | None]:
    if result.ranked.empty:
        return {
            "top_matching_score": None,
            "mean_matching_score": None,
            "median_matching_score": None,
        }

    return {
        "top_matching_score": float(
            result.ranked.iloc[0][
                "matching_score"
            ]
        ),
        "mean_matching_score": float(
            result.ranked[
                "matching_score"
            ].mean()
        ),
        "median_matching_score": float(
            result.ranked[
                "matching_score"
            ].median()
        ),
    }


def build_metadata(
    *,
    run_id: str,
    id_demande_version: int,
    result: MatchingEvaluationResult,
    score_statistics: dict[
        str,
        float | None,
    ],
    gitlab_traceability: dict[str, str],
    suite_ids: tuple[int, ...],
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "timestamp_utc": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "experiment_name": (
            EXPERIMENT_NAME
        ),
        "tracking_uri": (
            TRACKING_URI
        ),
        "evaluation_scope": (
            "multi-demande-version-suite"
            if len(suite_ids) > 1
            else "single-demande-version"
        ),
        "evaluation_suite_ids": list(
            suite_ids
        ),
        "evaluation_suite_size": len(
            suite_ids
        ),
        "id_demande_version": (
            id_demande_version
        ),
        "source_recherche_ref": (
            result.demande.get(
                "source_recherche_ref"
            )
        ),
        "ingestion_batch": (
            result.demande.get(
                "ingestion_batch"
            )
        ),
        "properties_loaded": (
            result.properties_loaded
        ),
        "candidates_after_filtering": (
            result.candidates_after_filtering
        ),
        "ground_truth_total": (
            result.ground_truth_total
        ),
        "ground_truth_in_candidates": (
            result.ground_truth_in_candidates
        ),
        "candidate_recall": (
            result.candidate_recall
        ),
        "ranking_metrics": (
            result.ranking_metrics
        ),
        **score_statistics,
        "baseline_type": (
            "deterministic-weighted-rules"
        ),
        "ground_truth_type": (
            "explicit-generated-search-lineage"
        ),
        "ground_truth_used_for_scoring": (
            False
        ),
        "data_type": (
            "generated-synthetic-project-data"
        ),
        "model_training": False,
        "model_registry": False,
        "gitlab_traceability": (
            gitlab_traceability
        ),
    }


def log_evaluation_artifacts(
    *,
    run_id: str,
    id_demande_version: int,
    result: MatchingEvaluationResult,
    metadata: dict[str, object],
    output_dir: Path,
) -> None:
    dv_output_dir = (
        output_dir
        / f"dv-{id_demande_version}"
    )

    dv_output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    ranked_path = (
        dv_output_dir
        / "ranked_candidates.csv"
    )

    metadata_path = (
        dv_output_dir
        / "evaluation_metadata.json"
    )

    result.ranked.to_csv(
        ranked_path,
        index=False,
    )

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

    with mlflow.start_run(
        run_id=run_id
    ):
        mlflow.log_artifact(
            str(ranked_path),
            artifact_path="evaluation",
        )

        mlflow.log_artifact(
            str(metadata_path),
            artifact_path="evaluation",
        )


def print_evaluation_result(
    *,
    id_demande_version: int,
    run_id: str,
    result: MatchingEvaluationResult,
    score_statistics: dict[
        str,
        float | None,
    ],
) -> None:
    print()
    print(
        "=============================================="
    )
    print(
        "Deterministic matching evaluation"
    )
    print(
        "=============================================="
    )

    print(
        "DemandeVersion: "
        f"{id_demande_version}"
    )

    print(
        f"MLflow Run ID: {run_id}"
    )

    print(
        "Source recherche ref: "
        f"{result.demande.get('source_recherche_ref')}"
    )

    print(
        "Properties loaded: "
        f"{result.properties_loaded}"
    )

    print(
        "Candidates after filtering: "
        f"{result.candidates_after_filtering}"
    )

    print(
        "Ground truth total: "
        f"{result.ground_truth_total}"
    )

    print(
        "Ground truth in candidates: "
        f"{result.ground_truth_in_candidates}"
    )

    print(
        "Candidate recall: "
        f"{result.candidate_recall:.4f}"
    )

    print(
        "Ranking metrics:"
    )

    for metric_name, metric_value in sorted(
        result.ranking_metrics.items()
    ):
        print(
            f"  {metric_name}: "
            f"{metric_value:.6f}"
        )

    top_matching_score = (
        score_statistics[
            "top_matching_score"
        ]
    )

    if top_matching_score is not None:
        print(
            "Top matching score: "
            f"{top_matching_score}"
        )

        print(
            "Mean matching score: "
            f"{score_statistics['mean_matching_score']}"
        )

        print(
            "Median matching score: "
            f"{score_statistics['median_matching_score']}"
        )


def evaluate_one_demande_version(
    *,
    connection: psycopg.Connection,
    id_demande_version: int,
    suite_ids: tuple[int, ...],
    gitlab_traceability: dict[str, str],
    output_dir: Path,
) -> dict[str, object]:
    print()
    print(
        "----------------------------------------------"
    )
    print(
        "Evaluating demande version "
        f"{id_demande_version}"
    )
    print(
        "----------------------------------------------"
    )

    result = evaluate_demande_version(
        connection=connection,
        id_demande_version=id_demande_version,
    )

    run_name = (
        f"matching-baseline-dv-"
        f"{id_demande_version}"
    )

    mlflow_tags = {
        "project": (
            "chasse_immobiliere"
        ),
        "platform": (
            "enterprise-homelab"
        ),
        "execution_mode": (
            "kubernetes-job"
        ),
        "evaluation_type": (
            "deterministic-baseline"
        ),
        "evaluation_scope": (
            "multi-demande-version-suite"
            if len(suite_ids) > 1
            else "single-demande-version"
        ),
        "evaluation_suite_size": str(
            len(suite_ids)
        ),
        "model_registry_enabled": (
            "false"
        ),
        **gitlab_traceability,
    }

    run_id = log_deterministic_evaluation(
        result,
        run_name=run_name,
        extra_tags=mlflow_tags,
    )

    score_statistics = (
        matching_score_statistics(
            result
        )
    )

    metadata = build_metadata(
        run_id=run_id,
        id_demande_version=(
            id_demande_version
        ),
        result=result,
        score_statistics=(
            score_statistics
        ),
        gitlab_traceability=(
            gitlab_traceability
        ),
        suite_ids=suite_ids,
    )

    log_evaluation_artifacts(
        run_id=run_id,
        id_demande_version=(
            id_demande_version
        ),
        result=result,
        metadata=metadata,
        output_dir=output_dir,
    )

    print_evaluation_result(
        id_demande_version=(
            id_demande_version
        ),
        run_id=run_id,
        result=result,
        score_statistics=(
            score_statistics
        ),
    )

    return {
        "id_demande_version": (
            id_demande_version
        ),
        "run_id": run_id,
        "source_recherche_ref": (
            result.demande.get(
                "source_recherche_ref"
            )
        ),
        "properties_loaded": (
            result.properties_loaded
        ),
        "candidates_after_filtering": (
            result.candidates_after_filtering
        ),
        "ground_truth_total": (
            result.ground_truth_total
        ),
        "ground_truth_in_candidates": (
            result.ground_truth_in_candidates
        ),
        "candidate_recall": (
            result.candidate_recall
        ),
        "ranking_metrics": (
            result.ranking_metrics
        ),
        **score_statistics,
    }


def write_suite_summary(
    *,
    output_dir: Path,
    suite_results: list[
        dict[str, object]
    ],
    gitlab_traceability: dict[str, str],
) -> Path:
    summary_path = (
        output_dir
        / "evaluation_suite_summary.json"
    )

    summary = {
        "timestamp_utc": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "experiment_name": (
            EXPERIMENT_NAME
        ),
        "tracking_uri": (
            TRACKING_URI
        ),
        "evaluation_type": (
            "deterministic-baseline"
        ),
        "evaluation_scope": (
            "multi-demande-version-suite"
        ),
        "suite_size": len(
            suite_results
        ),
        "all_candidate_recall_complete": all(
            float(
                result[
                    "candidate_recall"
                ]
            )
            == 1.0
            for result in suite_results
        ),
        "demande_versions": (
            suite_results
        ),
        "gitlab_traceability": (
            gitlab_traceability
        ),
    }

    with open(
        summary_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return summary_path


def main() -> None:
    print(
        "===== Real Estate Matching Evaluation Suite Started ====="
    )

    if not DATABASE_USER:
        raise RuntimeError(
            "POSTGRES_USER is required"
        )

    if not DATABASE_PASSWORD:
        raise RuntimeError(
            "POSTGRES_PASSWORD is required"
        )

    demande_version_ids = (
        parse_demande_version_ids()
    )

    print(
        f"MLflow Tracking URI: {TRACKING_URI}"
    )

    print(
        f"MLflow Experiment: {EXPERIMENT_NAME}"
    )

    print(
        "DemandeVersions: "
        + ", ".join(
            str(value)
            for value in demande_version_ids
        )
    )

    print(
        "Evaluation suite size: "
        f"{len(demande_version_ids)}"
    )

    mlflow.set_tracking_uri(
        TRACKING_URI
    )

    mlflow.set_experiment(
        EXPERIMENT_NAME
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

    suite_results: list[
        dict[str, object]
    ] = []

    connection = psycopg.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
    )

    try:
        for id_demande_version in (
            demande_version_ids
        ):
            suite_result = (
                evaluate_one_demande_version(
                    connection=connection,
                    id_demande_version=(
                        id_demande_version
                    ),
                    suite_ids=(
                        demande_version_ids
                    ),
                    gitlab_traceability=(
                        gitlab_traceability
                    ),
                    output_dir=(
                        output_dir
                    ),
                )
            )

            suite_results.append(
                suite_result
            )
    finally:
        connection.close()

    summary_path = write_suite_summary(
        output_dir=output_dir,
        suite_results=suite_results,
        gitlab_traceability=(
            gitlab_traceability
        ),
    )

    print()
    print(
        "=============================================="
    )
    print(
        "Evaluation suite summary"
    )
    print(
        "=============================================="
    )

    for result in suite_results:
        print(
            "DV "
            f"{result['id_demande_version']}: "
            f"candidates="
            f"{result['candidates_after_filtering']}, "
            f"ground_truth="
            f"{result['ground_truth_total']}, "
            f"candidate_recall="
            f"{float(result['candidate_recall']):.4f}, "
            f"run_id="
            f"{result['run_id']}"
        )

    all_candidate_recall_complete = all(
        float(
            result[
                "candidate_recall"
            ]
        )
        == 1.0
        for result in suite_results
    )

    print()
    print(
        "All demande versions preserve "
        "100% ground-truth candidate recall: "
        f"{all_candidate_recall_complete}"
    )

    print(
        "Suite summary artifact: "
        f"{summary_path}"
    )

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
        "===== Real Estate Matching Evaluation "
        "Suite Completed Successfully ====="
    )


if __name__ == "__main__":
    main()