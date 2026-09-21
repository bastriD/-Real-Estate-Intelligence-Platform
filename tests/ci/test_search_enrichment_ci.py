from pathlib import Path
import os
import shutil
import subprocess

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_search_jobs_reuse_database_controls_and_registry_guards():
    config = yaml.safe_load((ROOT / ".gitlab/ci/database-search.yml").read_text(encoding="utf-8"))
    for job, script in [("database:migrate-017", "migrate-017.sh"),
                        ("database:test-demande-version-search", "test-demande-version-search.sh")]:
        assert config[job]["extends"] == ".database-operation"
        assert config[job]["script"] == [f'. "$CI_PROJECT_DIR/scripts/ci/database/{script}"']
    migration = (ROOT / "scripts/ci/database/migrate-017.sh").read_text(encoding="utf-8")
    assert "version = '016'" in migration and "version = '017'" in migration
    sql = (ROOT / "database/tests/020_demande_version_search.sql").read_text(encoding="utf-8")
    assert "\\set ON_ERROR_STOP on" in sql and "\nBEGIN;" in sql
    assert sql.rstrip().endswith("ROLLBACK;") and "\nCOMMIT;" not in sql


def test_migration_checks_exact_sources_and_all_sector_mappings():
    migration = (ROOT / "database/migrations/017_demande_version_search_enrichment.sql").read_text(encoding="utf-8")
    legacy = (ROOT / "database/legacy/PgSQL.sql").read_text(encoding="utf-8")
    source_rows = migration.split("INSERT INTO enrichment_017_source VALUES", 1)[1].split(";", 1)[0]
    import re
    descriptions = re.findall(r"\('LEGACY-DEMANDE-(\d+)', '([^']+)'\)", source_rows)
    assert len(descriptions) == 17
    assert {int(identifier) for identifier, _ in descriptions} == set(range(1, 19)) - {13}
    assert all(description in legacy for _, description in descriptions)
    assert "description_recherche_legacy IS DISTINCT FROM e.description" in migration
    assert "refuses to overwrite already structured legacy V1" in migration
    assert "HAVING COUNT(ds.id_secteur) <> expected.sector_count" in migration
    assert "AND dv.numero_version = 1" in migration


@pytest.mark.parametrize("response,code,success", [("yes", "0", True), ("no", "0", False), ("", "1", False)])
def test_search_release_guard_fails_closed_without_contacting_cluster(response, code, success):
    bash = shutil.which("bash")
    git_bash = Path("C:/Program Files/Git/bin/bash.exe")
    if os.name == "nt" and git_bash.exists():
        bash = str(git_bash)
    if not bash:
        pytest.skip("Bash is required for the release guard regression")
    result = subprocess.run([bash, "-c",
        'set -e; kubectl() { printf "%s\\n" "$SEARCH_TEST_RESPONSE"; return "$SEARCH_TEST_CODE"; }; '
        '. scripts/ci/database/check-search-schema.sh'], cwd=ROOT, capture_output=True, text=True,
        env={**os.environ, "SEARCH_TEST_RESPONSE": response, "SEARCH_TEST_CODE": code})
    assert (result.returncode == 0) == success


def test_every_matching_workload_and_backend_publication_check_schema_first():
    paths = ["backend/publish-gitops.sh", "ai-model-comparison/compare.sh"] + [
        f"ai-mlops/{name}.sh" for name in ["evaluate", "validate-training-dataset", "split-training-dataset", "train-matching-model"]]
    for path in paths:
        content = (ROOT / "scripts/ci" / path).read_text(encoding="utf-8")
        assert '"$CI_PROJECT_DIR/scripts/ci/database/check-search-schema.sh"' in content
