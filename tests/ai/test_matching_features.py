import pandas as pd

from src.ai.matching.features import (
    build_matching_features,
    compute_matching_score,
    filter_candidates,
)


def _sample_biens():
    return pd.DataFrame(
        [
            {
                "id_bien": 1,
                "ville": "Nantes",
                "code_postal": "44000",
                "prix": 350000,
                "type_bien": "APPARTEMENT",
                "surface": 80,
                "nb_pieces": 4,
                "nb_chambres": 2,
                "dpe": "C",
            },
            {
                "id_bien": 2,
                "ville": "Nantes",
                "code_postal": "44000",
                "prix": 420000,
                "type_bien": "APPARTEMENT",
                "surface": 75,
                "nb_pieces": 3,
                "nb_chambres": 2,
                "dpe": "D",
            },
            {
                "id_bien": 3,
                "ville": "Nantes",
                "code_postal": "44100",
                "prix": 300000,
                "type_bien": "MAISON",
                "surface": 95,
                "nb_pieces": 5,
                "nb_chambres": 3,
                "dpe": "B",
            },
            {
                "id_bien": 4,
                "ville": "Rennes",
                "code_postal": "35000",
                "prix": 250000,
                "type_bien": "APPARTEMENT",
                "surface": 70,
                "nb_pieces": 3,
                "nb_chambres": 2,
                "dpe": "C",
            },
        ]
    )


def test_exact_postcode_is_preferred_when_available():
    demande = {
        "ville": "Nantes",
        "code_postal": "44000",
        "budget_max": 410000,
    }

    result = filter_candidates(_sample_biens(), demande)

    assert set(result["id_bien"]) == {1}
    assert set(result["code_postal"]) == {"44000"}


def test_city_fallback_when_exact_postcode_does_not_exist():
    demande = {
        "ville": "Nantes",
        "code_postal": "44200",
        "budget_max": 480000,
    }

    result = filter_candidates(_sample_biens(), demande)

    assert set(result["id_bien"]) == {1, 2, 3}
    assert set(result["ville"]) == {"Nantes"}


def test_budget_max_is_a_hard_filter():
    demande = {
        "ville": "Nantes",
        "code_postal": "44000",
        "budget_max": 360000,
    }

    result = filter_candidates(_sample_biens(), demande)

    assert set(result["id_bien"]) == {1}
    assert (result["prix"] <= 360000).all()


def test_absent_optional_criteria_do_not_penalize_score():
    demande = {
        "ville": "Nantes",
        "code_postal": "44200",
        "budget_max": 480000,
        "budget_min": None,
        "type_bien": None,
        "surface_min": None,
        "nb_pieces_min": None,
        "nb_chambres_min": None,
        "dpe_max": None,
    }

    features = build_matching_features(_sample_biens(), demande)

    assert (features["feature_property_type"] == 1.0).all()
    assert (features["feature_surface"] == 1.0).all()
    assert (features["feature_rooms"] == 1.0).all()
    assert (features["feature_bedrooms"] == 1.0).all()
    assert (features["feature_dpe"] == 1.0).all()


def test_matching_score_is_between_zero_and_one_hundred():
    demande = {
        "ville": "Nantes",
        "code_postal": "44200",
        "budget_max": 480000,
        "surface_min": 70,
        "nb_pieces_min": 3,
        "nb_chambres_min": 2,
        "dpe_max": "D",
    }

    features = build_matching_features(_sample_biens(), demande)
    result = compute_matching_score(features)

    assert not result.empty
    assert result["matching_score"].between(0, 100).all()
    assert result["matching_score"].is_monotonic_decreasing