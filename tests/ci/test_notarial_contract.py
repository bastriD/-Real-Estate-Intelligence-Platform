import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_notarial_migration_publication_and_warehouse_are_connected():
    migration = read("database/migrations/019_notarial_workflow.sql")
    assert "version = '018'" in migration
    for table in ("notaire", "dossier_notarial", "mouvement_notarial"):
        assert f"CREATE TABLE real_estate.{table}" in migration
    assert "DEFERRABLE INITIALLY DEFERRED" in migration
    assert "FOR UPDATE" in migration
    assert "append-only" in migration
    jobs = yaml.safe_load(read(".gitlab/ci/database-notarial.yml"))
    assert all(job["extends"] == ".database-operation" for job in jobs.values())
    assert "load_notarial_projection(cur)" in read("database/olap/load_warehouse.py")
    assert "COPY database/olap/notarial_projection.py /app/database/olap/notarial_projection.py" in read("deploy/docker/Dockerfile.data-pipeline")
    sources = yaml.safe_load(read("pipelines/dbt/models/staging/sources.yml"))["sources"]
    assert "fact_dossier_notarial" in {t["name"] for s in sources if s["name"] == "warehouse" for t in s["tables"]}


def test_notarial_dashboard_only_reads_agency_fee_mart():
    dashboard = json.loads(read("observability/grafana/dashboards/real-estate-business-platform.json"))
    panels = [p for p in dashboard["panels"] if p["id"] in (50, 51, 52)]
    assert len(panels) == 3
    for panel in panels:
        assert "FROM analytics.mart_notarial_reconciliation" in panel["targets"][0]["rawSql"]
        assert panel["datasource"]["uid"] == "real-estate-postgresql"
        assert "purchase prices" in panel["description"]
