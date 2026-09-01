from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


DPE_ORDER = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6,
    "G": 7,
}


@dataclass(frozen=True)
class MatchingWeights:
    location: float = 0.30
    budget: float = 0.30
    property_type: float = 0.10
    surface: float = 0.10
    rooms: float = 0.07
    bedrooms: float = 0.07
    dpe: float = 0.06


def _normalise_text(
    series: pd.Series,
) -> pd.Series:
    return (
        series.astype("string")
        .str.strip()
        .str.lower()
    )


def _score_budget(
    prices: pd.Series,
    budget_min: float | None,
    budget_max: float | None,
) -> pd.Series:
    prices = pd.to_numeric(
        prices,
        errors="coerce",
    )

    score = pd.Series(
        np.ones(
            len(prices),
            dtype=float,
        ),
        index=prices.index,
    )

    if budget_max is not None:
        max_budget = float(
            budget_max
        )

        over_budget = (
            prices > max_budget
        )

        score.loc[over_budget] = (
            1.0
            - (
                (
                    prices.loc[
                        over_budget
                    ]
                    - max_budget
                )
                / max_budget
            )
        ).clip(
            lower=0.0
        )

    if budget_min is not None:
        min_budget = float(
            budget_min
        )

        under_budget = (
            prices < min_budget
        )

        score.loc[under_budget] = (
            prices.loc[
                under_budget
            ]
            / min_budget
        ).clip(
            lower=0.0
        )

    return score.fillna(
        0.0
    )


def _score_minimum(
    values: pd.Series,
    minimum: float | int | None,
) -> pd.Series:
    if minimum is None:
        return pd.Series(
            np.ones(
                len(values),
                dtype=float,
            ),
            index=values.index,
        )

    numeric_values = pd.to_numeric(
        values,
        errors="coerce",
    )

    minimum_value = float(
        minimum
    )

    score = (
        numeric_values
        / minimum_value
    ).clip(
        lower=0.0,
        upper=1.0,
    )

    return score.fillna(
        0.0
    )


def _score_property_type(
    values: pd.Series,
    expected_type: str | None,
) -> pd.Series:
    if not expected_type:
        return pd.Series(
            np.ones(
                len(values),
                dtype=float,
            ),
            index=values.index,
        )

    expected = (
        expected_type
        .strip()
        .lower()
    )

    return (
        _normalise_text(values)
        == expected
    ).astype(float)


def _score_dpe(
    values: pd.Series,
    maximum_dpe: str | None,
) -> pd.Series:
    if not maximum_dpe:
        return pd.Series(
            np.ones(
                len(values),
                dtype=float,
            ),
            index=values.index,
        )

    maximum_rank = DPE_ORDER.get(
        maximum_dpe
        .strip()
        .upper()
    )

    if maximum_rank is None:
        return pd.Series(
            np.zeros(
                len(values),
                dtype=float,
            ),
            index=values.index,
        )

    ranks = (
        values.astype("string")
        .str.upper()
        .map(DPE_ORDER)
    )

    return (
        ranks <= maximum_rank
    ).astype(float).fillna(
        0.0
    )


def filter_candidates(
    biens: pd.DataFrame,
    demande: pd.Series,
) -> pd.DataFrame:
    """
    Preserve the candidate set received from the repository layer.

    Hard eligibility rules are implemented only in repository.py.
    This layer performs feature engineering and scoring only.
    """
    del demande

    return biens.copy()


def build_matching_features(
    biens: pd.DataFrame,
    demande: pd.Series,
) -> pd.DataFrame:
    candidates = filter_candidates(
        biens=biens,
        demande=demande,
    )

    if candidates.empty:
        return candidates

    result = candidates.copy()

    result["feature_location"] = 1.0

    result["feature_budget"] = _score_budget(
        prices=result["prix"],
        budget_min=(
            demande.get("budget_min")
            if pd.notna(
                demande.get("budget_min")
            )
            else None
        ),
        budget_max=(
            demande.get("budget_max")
            if pd.notna(
                demande.get("budget_max")
            )
            else None
        ),
    )

    result["feature_property_type"] = (
        _score_property_type(
            values=result["type_bien"],
            expected_type=(
                demande.get("type_bien")
                if pd.notna(
                    demande.get("type_bien")
                )
                else None
            ),
        )
    )

    result["feature_surface"] = (
        _score_minimum(
            values=result["surface"],
            minimum=(
                demande.get("surface_min")
                if pd.notna(
                    demande.get("surface_min")
                )
                else None
            ),
        )
    )

    result["feature_rooms"] = (
        _score_minimum(
            values=result["nb_pieces"],
            minimum=(
                demande.get("nb_pieces_min")
                if pd.notna(
                    demande.get("nb_pieces_min")
                )
                else None
            ),
        )
    )

    result["feature_bedrooms"] = (
        _score_minimum(
            values=result["nb_chambres"],
            minimum=(
                demande.get("nb_chambres_min")
                if pd.notna(
                    demande.get("nb_chambres_min")
                )
                else None
            ),
        )
    )

    result["feature_dpe"] = _score_dpe(
        values=result["dpe"],
        maximum_dpe=(
            demande.get("dpe_max")
            if pd.notna(
                demande.get("dpe_max")
            )
            else None
        ),
    )

    return result


def compute_matching_score(
    features: pd.DataFrame,
    weights: MatchingWeights | None = None,
) -> pd.DataFrame:
    if features.empty:
        return features.copy()

    weights = (
        weights
        or MatchingWeights()
    )

    result = features.copy()

    result["matching_score"] = (
        result["feature_location"]
        * weights.location
        + result["feature_budget"]
        * weights.budget
        + result["feature_property_type"]
        * weights.property_type
        + result["feature_surface"]
        * weights.surface
        + result["feature_rooms"]
        * weights.rooms
        + result["feature_bedrooms"]
        * weights.bedrooms
        + result["feature_dpe"]
        * weights.dpe
    ) * 100.0

    result["matching_score"] = (
        result["matching_score"]
        .clip(
            lower=0.0,
            upper=100.0,
        )
        .round(2)
    )

    return result.sort_values(
        by="matching_score",
        ascending=False,
    ).reset_index(
        drop=True
    )
