"""Governance preflight regressions and KPI results on grouped fixture data."""
import importlib.util
import json
import shutil
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("governance_validation", ROOT / "governance/scripts/validate_config.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


@pytest.fixture
def configuration(tmp_path):
    base = tmp_path / "governance"
    for path in (ROOT / "governance").rglob("*.json"):
        target = base / path.relative_to(ROOT / "governance")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    return base


def edit(base, relative, change):
    path = base / relative
    data = json.loads(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_all_enabled_definitions_and_references_validate():
    validator.validate(ROOT / "governance", ROOT)


@pytest.mark.parametrize("path,change,error", [
    ("tagging/real_estate_tags.json", lambda d: d.clear(), "classifications"),
    ("tagging/real_estate_tags.json", lambda d: d.update(classifications=[]), "classifications"),
    ("tagging/real_estate_tags.json", lambda d: d["classifications"][0].update(tags="invalid"), "tags"),
    ("tagging/real_estate_privacy_assignments.json", lambda d: d["column_assignments"][0].update(tags=["Missing.Tag"]), "Unknown tags"),
    ("metrics/real_estate_metrics.json", lambda d: d["metrics"][0].update(owner="Nobody"), "Unknown owner"),
    ("metrics/real_estate_metrics.json", lambda d: d["metrics"][0].update(glossary_terms=["Missing.Term"]), "Unknown glossary_terms"),
    ("metrics/real_estate_metrics.json", lambda d: d["metrics"][0].update(domain="Missing.Domain"), "Unknown domain"),
    ("metrics/real_estate_metrics.json", lambda d: d["metrics"][0].update(source="real-estate-postgresql.real_estate.analytics.missing"), "Unknown repository assets"),
    ("metrics/real_estate_metrics.json", lambda d: d["metrics"][0].update(expression="COUNT(*)"), "summary rows"),
    ("metrics/real_estate_metrics.json", lambda d: d["metrics"][1].update(expression="AVG(prix)"), "unknown source columns"),
    ("metrics/real_estate_metrics.json", lambda d: d["metrics"].append(d["metrics"][0]), "duplicate identifier"),
    ("docs/governance-config.json", lambda d: d["governance"]["classification"].update(enabled="true"), "boolean"),
    ("docs/governance-config.json", lambda d: d["governance"]["classification"].update(files=["../outside.json"]), "escapes"),
])
def test_invalid_configuration_fails_before_publication(configuration, path, change, error):
    edit(configuration, path, change)
    with pytest.raises(ValueError, match=error):
        validator.validate(configuration, ROOT)


def test_duplicate_json_keys_are_rejected(configuration):
    path = configuration / "tagging/real_estate_tags.json"
    path.write_text('{"classifications": [], "classifications": []}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate JSON key"):
        validator.validate(configuration)


def test_kpis_measure_observations_not_summary_rows():
    metrics = json.loads((ROOT / "governance/metrics/real_estate_metrics.json").read_text(encoding="utf-8"))["metrics"]
    expressions = {m["name"]: m["expression"] for m in metrics}
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE overview(total_annonces, prix_moyen, prix_m2_moyen, surface_moyenne)")
        db.execute("INSERT INTO overview VALUES (1000, 250000, 3500, 72)")
        for name, expected in (("marketListingsTotal", 1000), ("averagePropertyPrice", 250000),
                               ("averagePricePerM2", 3500), ("averagePropertySurface", 72)):
            assert db.execute(f"SELECT {expressions[name]} FROM overview").fetchone()[0] == expected
        db.execute("CREATE TABLE grouped(ville, dpe, type_bien, source_nom, nb_annonces)")
        db.executemany("INSERT INTO grouped VALUES (?, ?, ?, ?, ?)",
                       [("Nantes", "A", "MAISON", "Generator", 20),
                        ("Nantes", "A", "MAISON", "Generator", 35)])
        for name in ("listingsByCity", "listingsByDpe", "listingsByPropertyType", "listingsBySource"):
            measure, group = expressions[name].split(" GROUP BY ")
            assert db.execute(f"SELECT {measure} FROM grouped GROUP BY {group}").fetchall() == [(55,)]
        db.execute("CREATE TABLE mandates(statut, nb_mandats)")
        assert db.execute(f"SELECT {expressions['activeMandates']} FROM mandates").fetchone()[0] == 0
        db.executemany("INSERT INTO mandates VALUES (?, ?)", [("ACTIF", 3), ("ACTIF", 5), ("EXPIRE", 20)])
        assert db.execute(f"SELECT {expressions['activeMandates']} FROM mandates").fetchone()[0] == 8
