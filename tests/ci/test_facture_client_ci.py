"""Invoice migration wiring: use the existing manual, serialized DB workflow."""
from pathlib import Path
import os
import shutil
import subprocess

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_invoice_database_jobs_use_existing_runner_and_lock():
    config = yaml.safe_load((ROOT / ".gitlab/ci/database.yml").read_text(encoding="utf-8"))
    for name, script in [
        ("database:migrate-015", "migrate-015.sh"),
        ("database:test-facture-client", "test-facture-client.sh"),
    ]:
        assert config[name]["extends"] == ".database-operation"
        assert config[name]["script"] == [f'. "$CI_PROJECT_DIR/scripts/ci/database/{script}"']
        contents = (ROOT / "scripts/ci/database" / script).read_text(encoding="utf-8")
        assert "-v ON_ERROR_STOP=1" in contents
        assert "real-estate-postgresql" in contents
    migration_script = (ROOT / "scripts/ci/database/migrate-015.sh").read_text(encoding="utf-8")
    assert "version = '014'" in migration_script
    assert "version = '015'" in migration_script
    assert "< database/migrations/015_facture_client.sql" in migration_script
    test_script = (ROOT / "scripts/ci/database/test-facture-client.sh").read_text(encoding="utf-8")
    assert "< database/tests/018_facture_client.sql" in test_script


def test_sql_validation_and_rollback_contract():
    validation = (ROOT / "scripts/ci/database/validate.sh").read_text(encoding="utf-8")
    assert "test -f database/migrations/015_facture_client.sql" in validation
    assert "test -f database/tests/018_facture_client.sql" in validation
    sql = (ROOT / "database/tests/018_facture_client.sql").read_text(encoding="utf-8")
    assert "\\set ON_ERROR_STOP on" in sql
    assert "\nBEGIN;" in sql
    assert sql.rstrip().endswith("ROLLBACK;")
    assert "\nCOMMIT;" not in sql
    assert "taux_tva" not in sql


@pytest.mark.parametrize("response,code,success", [("yes", "0", True), ("no", "0", False), ("", "1", False)])
def test_gitops_schema_guard_executes_and_fails_closed(response, code, success):
    bash = shutil.which("bash")
    git_bash = Path("C:/Program Files/Git/bin/bash.exe")
    if os.name == "nt" and git_bash.exists():
        bash = str(git_bash)
    if not bash:
        pytest.skip("Bash is required to execute the release guard")
    result = subprocess.run(
        [bash, "-c", 'set -e; kubectl() { printf "%s\\n" "$INVOICE_TEST_RESPONSE"; return "$INVOICE_TEST_CODE"; }; '
         '. scripts/ci/backend/publish-gitops/check-invoice-schema.sh'],
        cwd=ROOT, capture_output=True, text=True,
        env={**os.environ, "INVOICE_TEST_RESPONSE": response, "INVOICE_TEST_CODE": code},
    )
    assert (result.returncode == 0) == success
    entrypoint = (ROOT / "scripts/ci/backend/publish-gitops.sh").read_text(encoding="utf-8")
    assert entrypoint.index("check-invoice-schema.sh") < entrypoint.index("prepare.sh")
