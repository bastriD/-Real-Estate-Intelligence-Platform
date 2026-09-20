import json
from dataclasses import replace
from unittest.mock import Mock

import pandas as pd
import pytest

from src.ai.matching.dataset_split import create_group_aware_split
from src.ai.matching.split_validation import SPLIT_VERSION, validate_runtime_split
from src.ai.matching.training_dataset import FEATURE_COLUMNS


def dataset(group_count=27):
    # Synthetic expanding cohort, not a copy of the live PostgreSQL dataset.
    return pd.DataFrame([
        {"id_demande_version": group,
         "source_recherche_ref": f"REC-{group}",
         "ingestion_batch": "generated-regression",
         "reference_externe": f"PROP-{group}-{label}",
         "relevance_label": label,
         **{feature: 0.8 if label else 0.2 for feature in FEATURE_COLUMNS}}
        for group in range(55, 55 + group_count) for label in (0, 1)
    ])


@pytest.mark.parametrize("group_count", [11, 27, 31])
def test_runtime_split_accepts_growing_datasets(group_count):
    source = dataset(group_count)
    result = validate_runtime_split(split=create_group_aware_split(source), source_dataset=source)
    assert result["source_group_count"] == group_count
    assert result["all_source_rows_preserved"]
    assert result["group_leakage"] is False
    assert result["frozen_split_v1"] is False
    assert result["split_version"] == SPLIT_VERSION


def test_dataset_and_split_identity_ignore_row_order_but_track_content():
    source = dataset()
    initial = validate_runtime_split(split=create_group_aware_split(source), source_dataset=source)
    reordered = source.sample(frac=1, random_state=9)
    assert initial == validate_runtime_split(split=create_group_aware_split(reordered), source_dataset=reordered)
    changed = source.copy()
    changed.loc[0, "feature_budget"] = 0.3
    updated = validate_runtime_split(split=create_group_aware_split(changed), source_dataset=changed)
    assert initial["dataset_fingerprint"] != updated["dataset_fingerprint"]
    assert initial["split_fingerprint"] != updated["split_fingerprint"]


def test_runtime_split_rejects_leakage():
    source = dataset()
    split = create_group_aware_split(source)
    bad = replace(split, validation_groups=(*split.validation_groups, split.train_groups[0]))
    with pytest.raises(RuntimeError, match="leakage"):
        validate_runtime_split(split=bad, source_dataset=source)


def test_runtime_split_rejects_lost_rows():
    source = dataset()
    split = create_group_aware_split(source)
    with pytest.raises(RuntimeError, match="row count"):
        validate_runtime_split(split=replace(split, train=split.train.iloc[1:]), source_dataset=source)


def test_runtime_split_rejects_changed_assignments():
    source = dataset()
    split = create_group_aware_split(source, random_state=99)
    with pytest.raises(RuntimeError, match="Non-reproducible"):
        validate_runtime_split(split=split, source_dataset=source)


def test_runtime_split_rejects_changed_features_in_partition():
    source = dataset()
    split = create_group_aware_split(source)
    train = split.train.copy()
    train.loc[0, "feature_budget"] = 0.9
    with pytest.raises(RuntimeError, match="rows differ"):
        validate_runtime_split(split=replace(split, train=train), source_dataset=source)


def test_train_and_compare_main_accept_27_groups_and_record_same_identity(tmp_path, monkeypatch):
    from src.ai.matching import run_model_training as training
    from src.ai.matching import run_model_comparison as comparison

    monkeypatch.chdir(tmp_path)
    source = dataset()
    discovered = source[["id_demande_version", "source_recherche_ref", "ingestion_batch"]].drop_duplicates().to_dict("records")
    connection = Mock()
    monkeypatch.setattr(training.psycopg, "connect", Mock(return_value=connection))
    for runner in (training, comparison):
        monkeypatch.setattr(runner, "DATABASE_USER", "test-user")
        monkeypatch.setattr(runner, "DATABASE_PASSWORD", "test-password")
        monkeypatch.setattr(runner, "discover_generated_demande_versions", lambda _: discovered)
        monkeypatch.setattr(runner, "build_training_dataset", lambda **_: source.copy())
    monkeypatch.setattr(training, "configure_mlflow", Mock())
    tracking = Mock(return_value="test-run")
    monkeypatch.setattr(training, "log_supervised_training", tracking)

    # Real splitting, validation, LogisticRegression, ranking and JSON writing;
    # only the external database and tracking services are replaced.
    training.main()
    comparison.main()
    training_artifact = json.loads((tmp_path / "outputs" / training.OUTPUT_FILENAME).read_text())
    comparison_artifact = json.loads((tmp_path / "outputs" / comparison.OUTPUT_FILENAME).read_text())
    train_details = training_artifact["split_summary"]
    compare_details = comparison_artifact["split"]["summary"]
    assert train_details["source_group_count"] == compare_details["source_group_count"] == 27
    for field in ("split_version", "dataset_fingerprint", "split_fingerprint"):
        assert train_details[field] == compare_details[field]
        assert tracking.call_args.kwargs["split_summary"][field] == train_details[field]
    assert training_artifact["frozen_split_validation"]["frozen_split_v1"] is False
    assert connection.close.call_count == 2
