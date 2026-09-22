import ast
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_new_runtime_modules_and_reconciliation_are_packaged():
    docker = read("deploy/docker/Dockerfile.data-pipeline")
    for path in ("database/seeds/sector_contract.py", "database/olap/sector_projection.py",
                 "database/tests/021_ingestion_sectors.sql"):
        assert f"COPY {path} /app/{path}" in docker
        assert (ROOT / path).is_file()
    assert "\\ir 021_ingestion_sectors.sql" in read("database/tests/006_oltp_data_quality.sql")


def generation_task():
    tree = ast.parse(read("pipelines/airflow/real_estate_ingestion_dag.py"))
    task = next(node.value for node in ast.walk(tree) if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "generate_source_data_task" for target in node.targets))
    return {item.arg: item.value for item in task.keywords}


def test_generator_task_defaults_to_standard_and_separates_schema_check():
    tree = ast.parse(read("pipelines/airflow/real_estate_ingestion_dag.py"))
    dag = next(node for node in ast.walk(tree) if isinstance(node, ast.Call)
               and isinstance(node.func, ast.Name) and node.func.id == "DAG")
    params = next(kw.value for kw in dag.keywords if kw.arg == "params")
    param = params.values[0]
    assert ast.literal_eval(params.keys[0]) == "generation_mode"
    assert ast.literal_eval(param.args[0]) == "standard"
    assert ast.literal_eval(next(kw.value for kw in param.keywords if kw.arg == "enum")) == ["standard", "sector_test"]
    kwargs = generation_task()
    assert kwargs["env_from"].id == "S3_AND_POSTGRES_ENV"
    assert ast.literal_eval(kwargs["env_vars"]) == {"GENERATION_MODE": "{{ params.generation_mode }}"}
    script = ast.literal_eval(kwargs["arguments"])[0]
    assert script.index("--check-schema") < script.index("rm -rf")


@pytest.mark.parametrize("mode,check_fails,success", [
    ("standard", False, True), ("sector_test", False, True),
    ("invalid", False, False), ('standard; echo invalid', False, False),
    ("standard", True, False), ("sector_test", True, False),
])
def test_generation_shell_executes_only_the_selected_mode(tmp_path, mode, check_fails, success):
    bash = "C:/Program Files/Git/bin/bash.exe" if os.name == "nt" else shutil.which("bash")
    if not bash or not Path(bash).exists():
        pytest.skip("Bash required for shell routing regression")
    script = ast.literal_eval(generation_task()["arguments"])[0]
    # Execute real branching with all filesystem/database/network operations stubbed.
    prefix = '''
rm() { :; }
mkdir() { :; }
python() {
  printf '%s\\n' "$*" >> "$SECTOR_TEST_TRACE"
  if [ "$2" = "--check-schema" ] && [ "$SECTOR_TEST_FAIL" = "1" ]; then return 9; fi
}
'''
    trace = tmp_path / "commands.txt"
    result = subprocess.run([bash, "-c", prefix + script], cwd=ROOT,
        env={**os.environ, "GENERATION_MODE": mode, "SECTOR_TEST_TRACE": trace.as_posix(),
             "SECTOR_TEST_FAIL": "1" if check_fails else "0"},
        capture_output=True, text=True)
    assert (result.returncode == 0) == success, result.stderr
    commands = trace.read_text(encoding="utf-8").splitlines() if trace.exists() else []
    if mode not in ("standard", "sector_test"):
        assert not commands
    elif check_fails:
        assert len(commands) == 1 and commands[0].endswith("--check-schema")
    else:
        assert commands[0].endswith("--check-schema")
        generate = next(command for command in commands if "generer_annonces.py" in command)
        assert "-r 5 --min-annonces 200 --max-annonces 200" in generate
        assert ("--secteurs-catalogue" in generate) == (mode == "sector_test")
        assert len(commands) == (4 if mode == "sector_test" else 3)
        assert commands[-1].endswith("upload_generated_to_s3.py")


def test_migration_jobs_keep_manual_database_controls():
    config = yaml.safe_load(read(".gitlab/ci/database-search.yml"))
    for name in ("database:migrate-018", "database:test-ingestion-sectors"):
        assert config[name]["extends"] == ".database-operation"
    sql = read("database/migrations/018_ingestion_sector_contract.sql")
    assert "version = '017'" in sql and "version = '018'" in sql
    assert "\nBEGIN;" in sql and sql.rstrip().endswith("COMMIT;")


def test_dbt_sector_models_reference_declared_sources():
    config = yaml.safe_load(read("pipelines/dbt/models/staging/sources.yml"))
    sources = {source["name"]: {table["name"] for table in source["tables"]} for source in config["sources"]}
    assert "bridge_demande_version_secteur" in sources["warehouse"]
    assert "demande_version_secteur" in sources["real_estate_oltp"]
    assert "db.secteur_key" in read("pipelines/dbt/models/staging/stg_dim_bien.sql")
