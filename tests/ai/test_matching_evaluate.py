from unittest.mock import Mock, patch

import pandas as pd

from src.ai.matching.evaluate import evaluate_demande_version


def test_evaluate_demande_version_returns_ranked_result():
    connection = Mock()

    demande = {
        "id_demande_version": 54,
        "ville": "Nantes",
        "code_postal": "44000",
        "budget_max": 410000,
    }

    biens = pd.DataFrame(
        [
            {
                "id_bien": 1,
                "reference_externe": "AN-001",
                "type_bien": "Appartement",
                "ville": "Nantes",
                "code_postal": "44000",
                "prix": 300000,
                "surface": 80,
                "nb_pieces": 3,
                "nb_chambres": 2,
                "dpe": "C",
                "statut": "DISPONIBLE",
                "id_source": 1,
            }
        ]
    )

    features = biens.copy()
    features["feature_location"] = 1.0

    ranked = features.copy()
    ranked["matching_score"] = 100.0

    with (
        patch(
            "src.ai.matching.evaluate.load_matching_input",
            return_value=(demande, biens),
        ),
        patch(
            "src.ai.matching.evaluate.build_matching_features",
            return_value=features,
        ),
        patch(
            "src.ai.matching.evaluate.compute_matching_score",
            return_value=ranked,
        ),
    ):
        result = evaluate_demande_version(
            connection=connection,
            id_demande_version=54,
        )

    assert result.id_demande_version == 54
    assert result.properties_loaded == 1
    assert result.candidates_after_filtering == 1
    assert result.demande["ville"] == "Nantes"
    assert result.ranked.iloc[0]["matching_score"] == 100.0