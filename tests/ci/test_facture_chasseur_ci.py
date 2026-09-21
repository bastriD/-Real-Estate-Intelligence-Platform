"""Offline wiring checks; PostgreSQL assertions execute only in the existing manual CI job."""
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_hunter_invoice_jobs_reuse_shared_database_controls():
    config = yaml.safe_load((ROOT / ".gitlab/ci/database-hunter-invoice.yml").read_text(encoding="utf-8"))
    for name, script in [("database:migrate-016", "migrate-016.sh"),
                         ("database:test-facture-chasseur", "test-facture-chasseur.sh")]:
        assert config[name]["extends"] == ".database-operation"
        assert config[name]["script"] == [f'. "$CI_PROJECT_DIR/scripts/ci/database/{script}"']
        content = (ROOT / "scripts/ci/database" / script).read_text(encoding="utf-8")
        assert "-v ON_ERROR_STOP=1" in content
    script = (ROOT / "scripts/ci/database/migrate-016.sh").read_text(encoding="utf-8")
    assert "version = '015'" in script and "version = '016'" in script
    assert "< database/migrations/016_facture_chasseur.sql" in script
    validation = (ROOT / "scripts/ci/database/validate.sh").read_text(encoding="utf-8")
    assert "test -f database/migrations/016_facture_chasseur.sql" in validation
    assert "test -f database/tests/019_facture_chasseur.sql" in validation


def test_hunter_sql_test_is_transactional_and_release_checks_new_schema():
    content = (ROOT / "database/tests/019_facture_chasseur.sql").read_text(encoding="utf-8")
    assert "\\set ON_ERROR_STOP on" in content and "\nBEGIN;" in content
    assert content.rstrip().endswith("ROLLBACK;") and "\nCOMMIT;" not in content
    guard = (ROOT / "scripts/ci/backend/publish-gitops/check-invoice-schema.sh").read_text(encoding="utf-8")
    assert "version = '016'" in guard and "to_regclass('real_estate.facture_chasseur')" in guard
