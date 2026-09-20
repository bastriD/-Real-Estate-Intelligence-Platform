"""Offline regression checks for this repository's GitLab rules and release DAG.

This models the subset of rules used here; GitLab CI Lint remains authoritative.
No runner, cluster, registry, credentials, or network is needed.
"""

import ast
import copy
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest
import yaml

from scripts.ci.pin_airflow_image import pin_image

ROOT = Path(__file__).resolve().parents[2]


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def read_yaml(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueLoader)


CONFIG = read_yaml(ROOT / ".gitlab-ci.yml")
DEFINITIONS = {}
for include in CONFIG["include"]:
    for name, value in read_yaml(ROOT / include["local"]).items():
        assert name not in DEFINITIONS, f"Duplicate job: {name}"
        DEFINITIONS[name] = value


def merged_job(name):
    job = copy.deepcopy(DEFINITIONS[name])
    parent = job.pop("extends", None)
    if parent:
        # Current templates only define rules, so an ordinary merge is sufficient.
        return {**merged_job(parent), **job}
    return job


JOBS = {name: merged_job(name) for name in DEFINITIONS if not name.startswith(".")}


def glob_match(path, pattern):
    """GitLab-style path globs: * excludes /, **/ also matches zero directories."""
    result = ""
    index = 0
    while index < len(pattern):
        if pattern[index:index + 3] == "**/":
            result += "(?:.*/)?"
            index += 3
        elif pattern[index:index + 2] == "**":
            result += ".*"
            index += 2
        elif pattern[index] == "*":
            result += "[^/]*"
            index += 1
        else:
            result += re.escape(pattern[index])
            index += 1
    return re.fullmatch(result, path) is not None


def condition(expression, variables):
    for term in expression.split(" && "):
        match = re.fullmatch(r'(\$\w+)(?: (==|!=) (\$\w+|"[^"]*"))?', term)
        assert match, f"Unsupported rule expression: {term}"
        left, operator, right = match.groups()
        left_value = variables.get(left[1:], "")
        if operator:
            right_value = variables.get(right[1:], "") if right.startswith("$") else right[1:-1]
            if (left_value == right_value) != (operator == "=="):
                return False
        elif not left_value:
            return False
    return True


def selected(rules, changed, variables):
    for rule in rules:
        if "if" in rule and not condition(rule["if"], variables):
            continue
        if "changes" in rule:
            # GitLab treats changes as true without a push diff (web/schedule).
            if variables["CI_PIPELINE_SOURCE"] in ("push", "merge_request_event"):
                if not any(glob_match(path, pattern) for path in changed for pattern in rule["changes"]):
                    continue
        return rule.get("when") != "never"
    return False


def variables(branch="main", source="push", open_mr="", default="main"):
    return {
        "CI_COMMIT_BRANCH": branch,
        "CI_DEFAULT_BRANCH": default,
        "CI_PIPELINE_SOURCE": source,
        "CI_OPEN_MERGE_REQUESTS": open_mr,
        "CI_MERGE_REQUEST_ID": "123" if source == "merge_request_event" else "",
    }


def selected_jobs(changed, values):
    if not selected(CONFIG["workflow"]["rules"], changed, values):
        return {}
    return {name: job for name, job in JOBS.items() if selected(job.get("rules", [{}]), changed, values)}


def dependencies(job):
    return [need if isinstance(need, dict) else {"job": need} for need in job.get("needs", [])]


SOURCE_SCRIPT = re.compile(r'^\. "\$CI_PROJECT_DIR/(scripts/ci/[\w/.-]+\.sh)"$')


def expand_commands(commands, ancestors=()):
    """Read sourced implementations without running any deployment commands."""
    expanded = []
    for command in commands:
        for line in command.splitlines():
            match = SOURCE_SCRIPT.fullmatch(line)
            if match:
                relative = match.group(1)
                assert relative not in ancestors, f"Recursive shell source: {relative}"
                path = ROOT / relative
                assert path.is_file(), f"Missing CI implementation: {relative}"
                expanded.append(expand_commands([path.read_text(encoding="utf-8")], (*ancestors, relative)))
            else:
                expanded.append(line)
    return "\n".join(expanded)


CHANGED_PATHS = ["README.md", ".gitlab-ci.yml", "requirements-ai-mlops.txt",
                 "requirements-ai-training.txt", "requirements-backend.txt"]
for folder in (".gitlab/ci", "src", "tests", "deploy", "pipelines", "governance", "scripts/ci"):
    CHANGED_PATHS.extend(
        path.relative_to(ROOT).as_posix() for path in (ROOT / folder).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )


@pytest.mark.parametrize("path", sorted(set(CHANGED_PATHS)))
@pytest.mark.parametrize("values", [variables(), variables("feature"),
                                    variables("", "merge_request_event"),
                                    variables("trunk", default="trunk")])
def test_required_dependencies_exist_for_single_file_changes(path, values):
    jobs = selected_jobs([path], values)
    for name, job in jobs.items():
        for need in dependencies(job):
            assert need.get("optional") or need["job"] in jobs, (path, name, need)


@pytest.mark.parametrize("source", ["web", "schedule", "api", "trigger"])
def test_no_diff_pipelines_have_all_required_dependencies(source):
    jobs = selected_jobs([], variables(source=source))
    for name, job in jobs.items():
        assert all(need.get("optional") or need["job"] in jobs for need in dependencies(job)), name


def test_workflow_avoids_duplicate_branch_pipeline_but_preserves_default_branch():
    assert not selected_jobs(["src/api/main.py"], variables("feature", open_mr="1"))
    assert selected_jobs(["src/api/main.py"], variables(open_mr="1"))
    assert selected_jobs(["src/api/main.py"], variables("", "merge_request_event"))
    assert selected_jobs(["src/api/main.py"], variables("feature", "web", "1"))


def test_merge_requests_never_run_live_operations():
    for job in selected_jobs(CHANGED_PATHS, variables("", "merge_request_event")).values():
        assert job["stage"] == "validate"


def test_tag_pipelines_only_validate():
    values = {**variables(""), "CI_COMMIT_TAG": "v1.0.0"}
    jobs = selected_jobs(CHANGED_PATHS, values)
    assert jobs
    assert all(job["stage"] == "validate" for job in jobs.values())


def test_release_gates_and_artifact_handoffs():
    required = {need["job"] for need in dependencies(JOBS["backend:build-image"]) if not need.get("optional")}
    assert {"backend:tests", "backend:validate", "ai:validate"} <= required
    for consumer, producer in [("airflow:publish-dags", "data-pipeline:build-image"),
                               ("openmetadata:publish-gitops", "governance:build-image")]:
        need = next(need for need in dependencies(JOBS[consumer]) if need["job"] == producer)
        assert need["artifacts"] is True and not need.get("optional")
    assert all(job["stage"] == "build" for name, job in JOBS.items() if name.endswith(":build-image"))


def test_database_manual_controls_are_preserved_and_serialized():
    operations = {name: job for name, job in JOBS.items() if job["stage"] == "database"}
    assert len(operations) == 29
    for job in operations.values():
        assert job["resource_group"] == "real-estate-database"
        assert job["rules"][0]["when"] == "manual"
        assert job["rules"][0]["allow_failure"] is False


def test_gitops_writers_share_a_lock_and_use_environment_credentials():
    for name, job in JOBS.items():
        if name.endswith(":publish-gitops"):
            assert job["resource_group"] == "lab-gitops-main"
            commands = expand_commands(job["script"])
            assert "GIT_ASKPASS" in commands
            assert "/tmp/.netrc" not in commands
            assert "HOME=" not in commands


def test_stage_order_and_dependency_graph_are_valid():
    def visit(name, ancestors):
        assert name not in ancestors, f"Dependency cycle: {ancestors} -> {name}"
        for need in dependencies(JOBS[name]):
            target = need["job"]
            assert target in JOBS
            assert CONFIG["stages"].index(JOBS[target]["stage"]) <= CONFIG["stages"].index(JOBS[name]["stage"])
            visit(target, ancestors | {name})
    for name in JOBS:
        visit(name, set())


def test_all_job_commands_are_strings():
    for name, job in JOBS.items():
        for section in ("before_script", "script", "after_script"):
            assert all(isinstance(command, str) for command in job.get(section, [])), (name, section)


def bash_executable():
    if os.name == "nt":
        candidate = Path("C:/Program Files/Git/bin/bash.exe")
        if candidate.exists():
            return str(candidate)
    return shutil.which("bash")


@pytest.mark.parametrize("name", sorted(JOBS))
def test_shell_syntax(name):
    bash = bash_executable()
    if not bash:
        pytest.skip("Bash is not installed")
    job = JOBS[name]
    for sections in (("before_script", "script"), ("after_script",)):
        commands = [command for section in sections for command in job.get(section, [])]
        result = subprocess.run([bash, "-n"], input=expand_commands(commands), text=True, capture_output=True)
        assert result.returncode == 0, (name, result.stderr)


def test_pin_real_dag_without_importing_airflow(tmp_path):
    source = (ROOT / "pipelines/airflow/real_estate_ingestion_dag.py").read_text(encoding="utf-8")
    path = tmp_path / "dag.py"
    path.write_text(source, encoding="utf-8")
    image = "gitlab.local:4567/root/chasse_immobiliere/data-pipeline@sha256:" + "a" * 64
    pin_image(path, image)
    result = path.read_text(encoding="utf-8")
    before, after = ast.parse(source), ast.parse(result)
    for tree in (before, after):
        assignment = next(node for node in tree.body if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name) and target.id == "DATA_PIPELINE_IMAGE" for target in node.targets))
        if tree is after:
            assert assignment.value.value == image
        assignment.value = ast.Constant(value="normalized")
    assert ast.dump(before) == ast.dump(after)


@pytest.mark.parametrize("image", ["repo:latest", "repo", "repo:tag;echo bad", "repo:\nmalformed"])
def test_pin_rejects_unversioned_or_unsafe_image(tmp_path, image):
    path = tmp_path / "dag.py"
    path.write_text('DATA_PIPELINE_IMAGE = "old"\n', encoding="utf-8")
    with pytest.raises(ValueError):
        pin_image(path, image)


@pytest.mark.parametrize("source", ["OTHER_IMAGE = 'old'\n", "DATA_PIPELINE_IMAGE = 'a'\nDATA_PIPELINE_IMAGE = 'b'\n"])
def test_pin_fails_closed_when_dag_structure_changes(tmp_path, source):
    path = tmp_path / "dag.py"
    path.write_text(source, encoding="utf-8")
    with pytest.raises(ValueError):
        pin_image(path, "repo:abc123")
    assert path.read_text(encoding="utf-8") == source


@pytest.mark.parametrize("prompt,expected", [("Username for 'https://gitlab.local':", "test-user\n"),
                                            ("Password for 'https://test-user@gitlab.local':", "test-token\n")])
def test_git_askpass_reads_job_environment(prompt, expected):
    bash = bash_executable()
    if not bash:
        pytest.skip("Bash is not installed")
    result = subprocess.run([bash, "scripts/ci/git-askpass.sh", prompt], cwd=ROOT, text=True,
                            capture_output=True, env={**os.environ,
                            "LAB_GITOPS_GIT_USER": "test-user", "LAB_GITOPS_GIT_TOKEN": "test-token"})
    assert result.returncode == 0, result.stderr
    assert result.stdout == expected


def test_shared_runtime_jobs_cannot_overlap_the_same_kubernetes_job():
    locks = []
    for name, job in JOBS.items():
        if name.startswith(("ai-mlops:", "ai-model-comparison:")) and job["stage"] == "deploy":
            locks.append(job["resource_group"])
            commands = expand_commands(job.get("before_script", []) + job["script"])
            assert 'mkdir -p "$CI_PROJECT_DIR/.ci-tmp/$CI_JOB_ID"' in commands
    assert len(locks) == len(set(locks)) == 5


def test_ci_files_stay_small_and_jobs_reference_existing_scripts():
    for path in (ROOT / ".gitlab/ci").glob("*.yml"):
        assert len(path.read_text(encoding="utf-8").splitlines()) <= 200, path
    for path in (ROOT / "scripts/ci").rglob("*.sh"):
        assert len(path.read_text(encoding="utf-8").splitlines()) <= 250, path
    for job in JOBS.values():
        for section in ("before_script", "script", "after_script"):
            commands = job.get(section, [])
            assert all(len(command.splitlines()) <= 10 for command in commands)
            expand_commands(commands)
