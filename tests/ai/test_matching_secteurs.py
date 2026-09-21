from unittest.mock import MagicMock

import pandas as pd

from src.ai.matching.features import build_matching_features, compute_matching_score
from src.ai.matching.repository import load_candidate_biens, load_demande_version


def connection():
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = []
    return db, cursor


def test_matching_loads_sectors_from_requested_version_not_mandate():
    db, cursor = connection()
    cursor.fetchone.return_value = {"id_demande_version": 8, "secteur_ids": [1, 3]}
    assert load_demande_version(db, 8)["secteur_ids"] == [1, 3]
    query, parameters = cursor.execute.call_args.args
    assert "ds.id_demande_version = dv.id_demande_version" in query
    assert "mandat_secteur" not in query
    assert parameters == (8,)


def test_matching_alternative_sectors_are_bound_as_or_not_postcode_inference():
    db, cursor = connection()
    load_candidate_biens(db, dict(ville="Montpellier", type_bien="Appartement",
        budget_max=300000, surface_min=65, secteur_ids=[1, 3], code_postal="34000"))
    query, parameters = cursor.execute.call_args.args
    assert "id_secteur = ANY(%s)" in query
    assert parameters == ("Appartement", 300000, "Montpellier", 65, [1, 3])
    assert "code_postal =" not in query and "id_secteur IS NULL" not in query
    assert "statut = 'ACTIF'" in query


def test_missing_surface_has_no_invented_filter_and_no_sector_keeps_city_matching():
    db, cursor = connection()
    load_candidate_biens(db, dict(ville="Nantes", type_bien="Appartement", budget_max=480000))
    query, parameters = cursor.execute.call_args.args
    assert "surface >=" not in query and "id_secteur" not in query
    assert parameters == ("Appartement", 480000, "Nantes")


def test_sector_only_search_does_not_require_redundant_city():
    db, cursor = connection()
    load_candidate_biens(db, dict(type_bien="Maison", budget_max=390000, secteur_ids=[9]))
    query, parameters = cursor.execute.call_args.args
    assert "LOWER(TRIM(ville))" not in query
    assert parameters == ("Maison", 390000, [9])


def test_enriched_optional_criteria_keep_existing_scoring_and_or_text():
    demande = pd.Series(dict(type_bien="Appartement", budget_max=300000, surface_min=None,
        nb_pieces_min=3, nb_chambres_min=None, dpe_max="C", criteres_souhaites=["terrasse ou jardin"]))
    biens = pd.DataFrame([
        dict(id_bien=1, type_bien="Appartement", prix=280000, surface=None, nb_pieces=3, nb_chambres=2, dpe="C"),
        dict(id_bien=2, type_bien="Appartement", prix=280000, surface=100, nb_pieces=2, nb_chambres=2, dpe="E"),
    ])
    ranked = compute_matching_score(build_matching_features(biens, demande))
    assert ranked.id_bien.tolist() == [1, 2]
    assert ranked.feature_surface.tolist() == [1.0, 1.0]
    assert demande.criteres_souhaites == ["terrasse ou jardin"]
