"""Offline cross-layer contracts for sector governance and dashboard queries."""
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREFIX = "real-estate-postgresql.real_estate."


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def config(path):
    return json.loads(read(path))


def test_sector_metadata_tracks_migration_and_dbt_fields():
    assignments = config("governance/glossary/real_estate_glossary_assignments.json")
    glossary = config("governance/glossary/real_estate_glossary.json")
    terms = {"RealEstateBusinessGlossary." + term["name"] for term in glossary["terms"]}
    for assignment in assignments["column_assignments"] + assignments["table_assignments"]:
        assert set(assignment["terms"]) <= terms
    columns = {(a["entity"].removeprefix(PREFIX), a["column"])
               for a in assignments["column_assignments"]}
    migration = read("database/migrations/018_ingestion_sector_contract.sql")
    for layer in ("raw", "staging"):
        for table in ("annonces", "recherches"):
            assert f"{layer}.{table}" in migration
            assert (f"{layer}.{table}", "secteur_code") in columns
    assert ("warehouse.dim_bien", "secteur_key") in columns
    assert ("analytics.stg_dim_bien", "secteur_key") in columns
    assert "secteur_key" in read("pipelines/dbt/models/staging/stg_dim_bien.sql")


def test_sector_operational_lineage_satisfies_quality_requirements():
    lineage = config("governance/lineage/real_estate_lineage.json")["lineage_edges"]
    edges = {(e["from"], e["to"]) for e in lineage}
    assert len(edges) == len(lineage)
    quality = config("governance/quality/real_estate_quality.json")
    targets = {PREFIX + "real_estate.demande_version_secteur",
               PREFIX + "warehouse.bridge_demande_version_secteur"}
    requirements = [r for r in quality["lineage_requirements"] if r["entity"] in targets]
    assert len(requirements) == 2
    for requirement in requirements:
        for upstream in requirement["required_upstream"]:
            assert (upstream, requirement["entity"]) in edges
    # A configuration file cannot attest to a runtime test result.
    assert all("validated_result" not in domain for domain in quality["quality_domains"])


def test_dashboard_sector_queries_use_real_columns_and_preserve_layout():
    for name, first_new in (("real-estate-business-platform", 47), ("real-estate-data-quality", 11)):
        dashboard = config(f"observability/grafana/dashboards/{name}.json")
        panels = dashboard["panels"]
        assert len({p["id"] for p in panels}) == len(panels)
        for panel in panels:
            if panel["id"] < first_new:
                continue
            assert panel["datasource"]["uid"] == "real-estate-postgresql"
            for target in panel["targets"]:
                sql = target["rawSql"]
                assert sql.startswith(("SELECT ", "WITH "))
                assert not re.search(r"\b(INSERT|UPDATE|DELETE|DROP|generation_mode|batch_id)\b", sql)
            a = panel["gridPos"]
            for other in panels:
                if other is panel:
                    continue
                b = other["gridPos"]
                assert (a["x"] + a["w"] <= b["x"] or b["x"] + b["w"] <= a["x"]
                        or a["y"] + a["h"] <= b["y"] or b["y"] + b["h"] <= a["y"])
    staging = read("database/oltp/004_staging_schema.sql")
    for column in ("ingestion_batch", "staged_at"):
        assert column in staging
    business = config("observability/grafana/dashboards/real-estate-business-platform.json")
    for panel in business["panels"]:
        if 47 <= panel["id"] <= 49:
            assert "id_bien_source <> 0" in panel["targets"][0]["rawSql"]
    coverage = next(p for p in business["panels"] if p["id"] == 49)
    assert "NULLIF(COUNT(*), 0)" in coverage["targets"][0]["rawSql"]


def test_dq_count_includes_executed_sector_assertions():
    module = ast.parse(read("observability/metrics/dq_runner.py"))
    counts = next(ast.literal_eval(n.value) for n in module.body
                  if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "CHECK_COUNTS" for t in n.targets))
    assert "\\ir 021_ingestion_sectors.sql" in read("database/tests/006_oltp_data_quality.sql")
    sector_sql = read("database/tests/021_ingestion_sectors.sql")
    assert counts["oltp"] == 14 + sector_sql.count("IF EXISTS (")
