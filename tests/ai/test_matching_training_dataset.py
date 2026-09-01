from unittest.mock import MagicMock

import pandas as pd

from src.ai.matching.training_dataset import (
    DATASET_COLUMNS,
    FEATURE_COLUMNS,
    LABEL_COLUMN,
    build_training_dataset,
    build_training_group,
    dataset_summary,
)


def test_build_training_group_labels_from_ground_truth(monkeypatch):
    demande = {
        "id_demande_version": 60,
        "source_recherche_ref": "REC-TEST",
        "ingestion_batch": "generated-test",
        "ville": "Annecy",
        "type_bien": "Villa",
        "budget_min": 100000,
        "budget_max": 500000,
        "surface_min": 80,
        "nb_pieces_min": 3,
        "nb_chambres_min": 2,
        "dpe_max": "D",
    }

    candidates = pd.DataFrame(
        [
            {
                "id_bien": 1,
                "reference_externe": "BIEN-001",
                "type_bien": "Villa",
                "ville": "Annecy",
                "code_postal": "74000",
                "latitude": None,
                "longitude": None,
                "prix": 300000,
                "surface": 100,
                "nb_pieces": 4,
                "nb_chambres": 3,
                "dpe": "C",
                "statut": "DISPONIBLE",
                "id_source": 1,
            },
            {
                "id_bien": 2,
                "reference_externe": "BIEN-002",
                "type_bien": "Villa",
                "ville": "Annecy",
                "code_postal": "74000",
                "latitude": None,
                "longitude": None,
                "prix": 450000,
                "surface": 90,
                "nb_pieces": 3,
                "nb_chambres": 2,
                "dpe": "E",
                "statut": "DISPONIBLE",
                "id_source": 1,
            },
        ]
    )

    monkeypatch.setattr(
        "src.ai.matching.training_dataset.load_matching_input",
        lambda connection, id_demande_version: (
            demande,
            candidates,
        ),
    )

    monkeypatch.setattr(
        "src.ai.matching.training_dataset.load_ground_truth_references",
        lambda connection, source_recherche_ref: {
            "BIEN-001"
        },
    )

    result = build_training_group(
        connection=MagicMock(),
        id_demande_version=60,
    )

    assert list(result.columns) == DATASET_COLUMNS
    assert len(result) == 2

    labels = dict(
        zip(
            result["reference_externe"],
            result[LABEL_COLUMN],
        )
    )

    assert labels["BIEN-001"] == 1
    assert labels["BIEN-002"] == 0

    assert (
        result["id_demande_version"]
        == 60
    ).all()

    assert (
        result["source_recherche_ref"]
        == "REC-TEST"
    ).all()

    assert (
        result["ingestion_batch"]
        == "generated-test"
    ).all()

    for column in FEATURE_COLUMNS:
        assert column in result.columns


def test_build_training_group_requires_lineage(monkeypatch):
    demande = {
        "id_demande_version": 61,
        "source_recherche_ref": None,
    }

    monkeypatch.setattr(
        "src.ai.matching.training_dataset.load_matching_input",
        lambda connection, id_demande_version: (
            demande,
            pd.DataFrame(
                [
                    {
                        "reference_externe": "BIEN-001",
                    }
                ]
            ),
        ),
    )

    try:
        build_training_group(
            connection=MagicMock(),
            id_demande_version=61,
        )
    except ValueError as exc:
        assert "has no source_recherche_ref" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )


def test_build_training_dataset_keeps_only_informative_groups(
    monkeypatch,
):
    groups = {
        60: pd.DataFrame(
            [
                {
                    **{
                        column: 1.0
                        for column in FEATURE_COLUMNS
                    },
                    "id_demande_version": 60,
                    "source_recherche_ref": "REC-60",
                    "ingestion_batch": "batch-1",
                    "reference_externe": "A",
                    LABEL_COLUMN: 1,
                },
                {
                    **{
                        column: 0.5
                        for column in FEATURE_COLUMNS
                    },
                    "id_demande_version": 60,
                    "source_recherche_ref": "REC-60",
                    "ingestion_batch": "batch-1",
                    "reference_externe": "B",
                    LABEL_COLUMN: 0,
                },
            ]
        )[DATASET_COLUMNS],
        61: pd.DataFrame(
            [
                {
                    **{
                        column: 1.0
                        for column in FEATURE_COLUMNS
                    },
                    "id_demande_version": 61,
                    "source_recherche_ref": "REC-61",
                    "ingestion_batch": "batch-2",
                    "reference_externe": "C",
                    LABEL_COLUMN: 1,
                },
                {
                    **{
                        column: 0.8
                        for column in FEATURE_COLUMNS
                    },
                    "id_demande_version": 61,
                    "source_recherche_ref": "REC-61",
                    "ingestion_batch": "batch-2",
                    "reference_externe": "D",
                    LABEL_COLUMN: 1,
                },
            ]
        )[DATASET_COLUMNS],
    }

    monkeypatch.setattr(
        "src.ai.matching.training_dataset.build_training_group",
        lambda connection, id_demande_version: groups[
            id_demande_version
        ],
    )

    result = build_training_dataset(
        connection=MagicMock(),
        demande_version_ids=[60, 61],
    )

    assert len(result) == 2
    assert set(
        result["id_demande_version"]
    ) == {60}

    assert set(
        result[LABEL_COLUMN]
    ) == {0, 1}


def test_build_training_dataset_can_keep_single_class_groups(
    monkeypatch,
):
    group = pd.DataFrame(
        [
            {
                **{
                    column: 1.0
                    for column in FEATURE_COLUMNS
                },
                "id_demande_version": 61,
                "source_recherche_ref": "REC-61",
                "ingestion_batch": "batch-2",
                "reference_externe": "C",
                LABEL_COLUMN: 1,
            }
        ]
    )[DATASET_COLUMNS]

    monkeypatch.setattr(
        "src.ai.matching.training_dataset.build_training_group",
        lambda connection, id_demande_version: group,
    )

    result = build_training_dataset(
        connection=MagicMock(),
        demande_version_ids=[61],
        require_both_classes=False,
    )

    assert len(result) == 1
    assert result.iloc[0][LABEL_COLUMN] == 1


def test_build_training_dataset_deduplicates_ids(
    monkeypatch,
):
    calls = []

    group = pd.DataFrame(
        [
            {
                **{
                    column: 1.0
                    for column in FEATURE_COLUMNS
                },
                "id_demande_version": 60,
                "source_recherche_ref": "REC-60",
                "ingestion_batch": "batch-1",
                "reference_externe": "A",
                LABEL_COLUMN: 1,
            },
            {
                **{
                    column: 0.5
                    for column in FEATURE_COLUMNS
                },
                "id_demande_version": 60,
                "source_recherche_ref": "REC-60",
                "ingestion_batch": "batch-1",
                "reference_externe": "B",
                LABEL_COLUMN: 0,
            },
        ]
    )[DATASET_COLUMNS]

    def fake_build_group(
        connection,
        id_demande_version,
    ):
        calls.append(id_demande_version)
        return group

    monkeypatch.setattr(
        "src.ai.matching.training_dataset.build_training_group",
        fake_build_group,
    )

    result = build_training_dataset(
        connection=MagicMock(),
        demande_version_ids=[60, 60],
    )

    assert calls == [60]
    assert len(result) == 2


def test_dataset_summary():
    dataset = pd.DataFrame(
        [
            {
                "id_demande_version": 60,
                LABEL_COLUMN: 1,
            },
            {
                "id_demande_version": 60,
                LABEL_COLUMN: 0,
            },
            {
                "id_demande_version": 68,
                LABEL_COLUMN: 1,
            },
        ]
    )

    result = dataset_summary(
        dataset
    )

    assert result["rows"] == 3
    assert result["groups"] == 2
    assert result["positives"] == 2
    assert result["negatives"] == 1
    assert result["positive_rate"] == 2 / 3


def test_dataset_summary_empty():
    result = dataset_summary(
        pd.DataFrame()
    )

    assert result == {
        "rows": 0,
        "groups": 0,
        "positives": 0,
        "negatives": 0,
        "positive_rate": 0.0,
    }