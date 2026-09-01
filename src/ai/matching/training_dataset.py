from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd
import psycopg

from src.ai.matching.features import build_matching_features
from src.ai.matching.repository import (
    load_ground_truth_references,
    load_matching_input,
)


FEATURE_COLUMNS = [
    "feature_location",
    "feature_budget",
    "feature_property_type",
    "feature_surface",
    "feature_rooms",
    "feature_bedrooms",
    "feature_dpe",
]


METADATA_COLUMNS = [
    "id_demande_version",
    "source_recherche_ref",
    "ingestion_batch",
    "reference_externe",
]


LABEL_COLUMN = "relevance_label"


DATASET_COLUMNS = [
    *METADATA_COLUMNS,
    *FEATURE_COLUMNS,
    LABEL_COLUMN,
]


def build_training_group(
    connection: psycopg.Connection,
    id_demande_version: int,
) -> pd.DataFrame:
    """
    Build one supervised query-candidate group.

    Candidates come exclusively from the canonical operational repository.

    Labels come exclusively from explicit generator provenance:

        demande_version.source_recherche_ref
            -> staging.annonces.recherche_ref
            -> real_estate.bien.reference_externe

    Ground-truth lineage is used only to construct the supervised target.
    It must never influence candidate retrieval or feature engineering.
    """
    demande, candidates = load_matching_input(
        connection=connection,
        id_demande_version=id_demande_version,
    )

    source_recherche_ref = demande.get(
        "source_recherche_ref"
    )

    if not source_recherche_ref:
        raise ValueError(
            f"DemandeVersion {id_demande_version} has no "
            "source_recherche_ref and cannot be used for "
            "supervised matching training."
        )

    if candidates.empty:
        return pd.DataFrame(
            columns=DATASET_COLUMNS
        )

    features = build_matching_features(
        biens=candidates,
        demande=pd.Series(demande),
    )

    if "reference_externe" not in features.columns:
        raise ValueError(
            "Matching features do not contain reference_externe."
        )

    ground_truth = load_ground_truth_references(
        connection=connection,
        source_recherche_ref=str(
            source_recherche_ref
        ),
    )

    result = features.copy()

    result["id_demande_version"] = int(
        id_demande_version
    )
    result["source_recherche_ref"] = str(
        source_recherche_ref
    )
    result["ingestion_batch"] = demande.get(
        "ingestion_batch"
    )

    result[LABEL_COLUMN] = (
        result["reference_externe"]
        .astype(str)
        .isin(ground_truth)
        .astype(int)
    )

    return result[DATASET_COLUMNS].reset_index(
        drop=True
    )


def build_training_dataset(
    connection: psycopg.Connection,
    demande_version_ids: Iterable[int],
    *,
    require_both_classes: bool = True,
) -> pd.DataFrame:
    """
    Build the supervised matching dataset for multiple query groups.

    The returned dataframe preserves id_demande_version so downstream
    train/validation/test splitting can occur at query level instead of
    randomly splitting candidate rows.

    When require_both_classes=True, groups containing only positives or
    only negatives are excluded from the supervised ranking dataset.
    They remain useful for operational candidate-recall evaluation.
    """
    groups: list[pd.DataFrame] = []

    seen_ids: set[int] = set()

    for raw_id in demande_version_ids:
        id_demande_version = int(
            raw_id
        )

        if id_demande_version in seen_ids:
            continue

        seen_ids.add(
            id_demande_version
        )

        group = build_training_group(
            connection=connection,
            id_demande_version=id_demande_version,
        )

        if group.empty:
            continue

        if require_both_classes:
            labels = set(
                group[LABEL_COLUMN]
                .dropna()
                .astype(int)
                .unique()
                .tolist()
            )

            if labels != {0, 1}:
                continue

        groups.append(
            group
        )

    if not groups:
        return pd.DataFrame(
            columns=DATASET_COLUMNS
        )

    dataset = pd.concat(
        groups,
        ignore_index=True,
    )

    return dataset[DATASET_COLUMNS].reset_index(
        drop=True
    )


def dataset_summary(
    dataset: pd.DataFrame,
) -> dict[str, Any]:
    """
    Return compact diagnostics for evidence, CI logs and MLflow metadata.
    """
    if dataset.empty:
        return {
            "rows": 0,
            "groups": 0,
            "positives": 0,
            "negatives": 0,
            "positive_rate": 0.0,
        }

    positives = int(
        dataset[LABEL_COLUMN].sum()
    )

    rows = int(
        len(dataset)
    )

    negatives = (
        rows
        - positives
    )

    groups = int(
        dataset[
            "id_demande_version"
        ].nunique()
    )

    return {
        "rows": rows,
        "groups": groups,
        "positives": positives,
        "negatives": negatives,
        "positive_rate": (
            positives / rows
            if rows
            else 0.0
        ),
    }