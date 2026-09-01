from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import psycopg

from src.ai.matching.features import (
    build_matching_features,
    compute_matching_score,
)
from src.ai.matching.repository import load_matching_input


@dataclass(frozen=True)
class MatchingEvaluationResult:
    id_demande_version: int
    demande: pd.Series
    properties_loaded: int
    candidates_after_filtering: int
    ranked: pd.DataFrame


def evaluate_demande_version(
    connection: psycopg.Connection,
    id_demande_version: int,
) -> MatchingEvaluationResult:
    demande_dict, biens = load_matching_input(
        connection=connection,
        id_demande_version=id_demande_version,
    )

    demande = pd.Series(demande_dict)

    features = build_matching_features(
        biens=biens,
        demande=demande,
    )

    ranked = compute_matching_score(features)

    return MatchingEvaluationResult(
        id_demande_version=id_demande_version,
        demande=demande,
        properties_loaded=len(biens),
        candidates_after_filtering=len(features),
        ranked=ranked,
    )