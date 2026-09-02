from __future__ import annotations

import json
from pathlib import Path

from src.ai.matching.run_model_comparison import (
    _serializable_metrics,
    write_comparison_artifact,
)


def test_serializable_metrics_converts_nested_values() -> None:
    class FakeScalar:
        def item(self) -> int:
            return 7

    value = {
        "a": FakeScalar(),
        "b": [
            FakeScalar(),
            {
                "c": FakeScalar(),
            },
        ],
    }

    converted = _serializable_metrics(
        value
    )

    assert converted == {
        "a": 7,
        "b": [
            7,
            {
                "c": 7,
            },
        ],
    }


def test_write_comparison_artifact_contains_core_evidence(
    tmp_path: Path,
) -> None:
    artifact_path = write_comparison_artifact(
        output_dir=tmp_path,
        generated_batches=12,
        generated_demande_versions=60,
        informative_summary={
            "groups": 11,
            "rows": 3768,
            "positives": 2200,
            "negatives": 1568,
            "positive_rate": 0.583864,
        },
        split_information={
            "summary": {
                "validation": {
                    "groups": [
                        70,
                        105,
                    ],
                },
                "test": {
                    "groups": [
                        60,
                        102,
                    ],
                },
            },
            "validation": {
                "group_leakage": False,
                "all_source_groups_preserved": True,
                "all_source_rows_preserved": True,
            },
        },
        validation_comparison={
            "candidate_population_identical": True,
            "ground_truth_identical": True,
            "hard_eligibility_identical": True,
            "metric_semantics_identical": True,
            "deterministic": {
                "macro_average": {
                    "mrr": 0.9,
                },
            },
            "supervised_ml": {
                "macro_average": {
                    "mrr": 1.0,
                },
            },
            "delta_ml_minus_deterministic": {
                "mrr": 0.1,
            },
            "summary": {
                "ml_metric_wins": 1,
                "deterministic_metric_wins": 0,
                "ties": 0,
            },
        },
        test_comparison={
            "candidate_population_identical": True,
            "ground_truth_identical": True,
            "hard_eligibility_identical": True,
            "metric_semantics_identical": True,
            "deterministic": {
                "macro_average": {
                    "mrr": 0.8,
                },
            },
            "supervised_ml": {
                "macro_average": {
                    "mrr": 0.75,
                },
            },
            "delta_ml_minus_deterministic": {
                "mrr": -0.05,
            },
            "summary": {
                "ml_metric_wins": 0,
                "deterministic_metric_wins": 1,
                "ties": 0,
            },
        },
        gitlab_traceability={
            "git_commit_short_sha": "abc12345",
            "git_pipeline_id": "999",
            "git_job_id": "1000",
        },
    )

    assert artifact_path.exists()

    content = json.loads(
        artifact_path.read_text(
            encoding="utf-8"
        )
    )

    assert content[
        "artifact_type"
    ] == (
        "deterministic-vs-supervised-matching-comparison"
    )

    assert content[
        "dataset_source"
    ] == (
        "postgresql-runtime-reconstruction"
    )

    assert content[
        "candidate_engine"
    ] == (
        "canonical-matching-repository"
    )

    assert content[
        "ground_truth_used_as_feature"
    ] is False

    assert content[
        "hard_eligibility_preserved"
    ] is True

    assert content[
        "candidate_population_identical"
    ] is True

    assert content[
        "training_partition_used_for_comparison"
    ] is False

    assert content[
        "generated_batches_discovered"
    ] == 12

    assert content[
        "generated_demande_versions_discovered"
    ] == 60

    assert content[
        "informative_dataset_summary"
    ]["groups"] == 11

    assert content[
        "validation"
    ]["summary"][
        "ml_metric_wins"
    ] == 1

    assert content[
        "test"
    ]["summary"][
        "deterministic_metric_wins"
    ] == 1

    assert content[
        "gitlab_traceability"
    ]["git_pipeline_id"] == "999"


def test_write_comparison_artifact_does_not_persist_raw_dataset(
    tmp_path: Path,
) -> None:
    artifact_path = write_comparison_artifact(
        output_dir=tmp_path,
        generated_batches=12,
        generated_demande_versions=60,
        informative_summary={
            "groups": 11,
            "rows": 3768,
            "positives": 2200,
            "negatives": 1568,
            "positive_rate": 0.583864,
        },
        split_information={},
        validation_comparison={},
        test_comparison={},
        gitlab_traceability={},
    )

    content = json.loads(
        artifact_path.read_text(
            encoding="utf-8"
        )
    )

    forbidden_keys = {
        "raw_dataset",
        "training_dataset",
        "validation_dataset",
        "test_dataset",
        "candidate_rows",
    }

    assert forbidden_keys.isdisjoint(
        content.keys()
    )