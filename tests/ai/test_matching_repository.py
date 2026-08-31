from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.ai.matching.repository import (
    load_candidate_biens,
    load_demande_version,
    load_matching_input,
)


def _mock_connection(fetchone=None, fetchall=None):
    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value.__enter__.return_value = cursor
    connection.cursor.return_value.__exit__.return_value = False

    cursor.fetchone.return_value = fetchone
    cursor.fetchall.return_value = fetchall or []

    return connection


def test_load_demande_version_returns_dictionary():
    connection = _mock_connection(
        fetchone={
            "id_demande_version": 54,
            "numero_version": 2,
            "ville": "Nantes",
            "code_postal": "44000",
            "budget_max": 410000,
            "active": True,
            "id_demande": 4,
        }
    )

    result = load_demande_version(connection, 54)

    assert result["id_demande_version"] == 54
    assert result["ville"] == "Nantes"
    assert result["code_postal"] == "44000"
    assert result["active"] is True


def test_load_demande_version_raises_when_missing():
    connection = _mock_connection(fetchone=None)

    with pytest.raises(
        ValueError,
        match="DemandeVersion 999 does not exist",
    ):
        load_demande_version(connection, 999)


def test_load_candidate_biens_returns_dataframe():
    connection = _mock_connection(
        fetchall=[
            {
                "id_bien": 1,
                "reference_externe": "TEST-001",
                "type_bien": "APPARTEMENT",
                "ville": "Nantes",
                "code_postal": "44000",
                "latitude": None,
                "longitude": None,
                "prix": 350000,
                "surface": 80,
                "nb_pieces": 4,
                "nb_chambres": 2,
                "dpe": "C",
                "statut": "DISPONIBLE",
                "id_source": 1,
            }
        ]
    )

    demande = {
        "ville": "Nantes",
    }

    result = load_candidate_biens(connection, demande)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["ville"] == "Nantes"
    assert result.iloc[0]["id_bien"] == 1


def test_load_candidate_biens_requires_city():
    connection = _mock_connection()

    with pytest.raises(
        ValueError,
        match="must contain a city",
    ):
        load_candidate_biens(
            connection,
            {"ville": None},
        )


def test_load_matching_input_combines_demande_and_biens(monkeypatch):
    demande = {
        "id_demande_version": 54,
        "ville": "Nantes",
        "code_postal": "44000",
    }

    biens = pd.DataFrame(
        [
            {
                "id_bien": 1,
                "ville": "Nantes",
                "code_postal": "44000",
            }
        ]
    )

    monkeypatch.setattr(
        "src.ai.matching.repository.load_demande_version",
        lambda connection, id_demande_version: demande,
    )

    monkeypatch.setattr(
        "src.ai.matching.repository.load_candidate_biens",
        lambda connection, demande: biens,
    )

    result_demande, result_biens = load_matching_input(
        MagicMock(),
        54,
    )

    assert result_demande == demande
    assert result_biens.equals(biens)