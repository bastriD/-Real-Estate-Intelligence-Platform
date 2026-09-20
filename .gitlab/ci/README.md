# Pipeline structure and compatibility

The root `.gitlab-ci.yml` still includes component files. Existing job names,
runner tags, Kubernetes namespaces, Secret names, GitOps repositories and
manual database commands are retained. No infrastructure migration is needed.

## Where to edit

| Concern | Location |
| --- | --- |
| Pipeline stages and includes | `.gitlab-ci.yml` |
| Job selection, dependencies, images, variables and artifacts | `.gitlab/ci/<component>.yml` |
| Shared release selection | `.gitlab/ci/rules.yml` |
| Job commands | `scripts/ci/<component>/<job>.sh` |
| Phases of longer jobs | `scripts/ci/<component>/<job>/*.sh` |
| Dependency, syntax and structural checks | `tests/ci/test_pipeline.py` |

For example, `backend:publish-gitops` calls
`scripts/ci/backend/publish-gitops.sh`, which sources `prepare.sh`,
`render-and-validate.sh` and `publish.sh` in order. MLOps jobs similarly separate
preparation, execution and reporting. Database jobs each have a small dedicated
script and inherit their common manual controls from `.database-operation`.

Scripts are sourced with `. "$CI_PROJECT_DIR/..."` in the existing runner shell.
This preserves exported variables, working-directory changes, early exits and
the runner's error-handling options across phases. Keep `after_script` separate:
GitLab executes it in a fresh shell. No executable bit or additional shell
installation is needed to source the scripts.

Keep YAML below 200 lines and individual shell scripts below 250 lines. The CI
checks enforce these limits, verify every referenced script exists and expand
the scripts for shell syntax validation. Split by responsibility, keeping whole
commands and heredocs together. Component change filters include the new script
directories so editing implementation still selects the corresponding jobs.

## Release dependencies

- Backend: `backend:validate` + `backend:tests` + `ai:validate` →
  `backend:build-image` → `backend:publish-gitops`.
- Airflow: database/warehouse validation + backend/data regression tests →
  `data-pipeline:build-image` → `airflow:publish-dags`.
- Governance: `governance:validate` → `governance:build-image` →
  `openmetadata:publish-gitops`.
- MLOps: `ai:validate` → `ai-mlops:build-image` → the existing evaluation,
  dataset validation, split, training and comparison jobs.

`pipeline:validate` checks YAML, shell syntax, dependency selection and image
rendering when CI, helper or DAG files change. Build/publisher jobs wait for it
when present. Its optional dependency means it can be omitted on unrelated
commits; an included failing check still blocks its consumers.

## Rules and tests

- The configured default branch replaces hard-coded source-branch `main`
  checks. Destination GitOps branches remain `main` as before.
- Merge requests validate changed components without touching the cluster.
  Feature pushes with an open merge request do not duplicate that pipeline.
  Default-branch, web, schedule, API and trigger branch pipelines remain allowed.
  Tags can run validation but cannot deploy.
- AI build/runtime jobs share `.ai-release`; governance build/publication share
  `.governance-release`. Edit those templates in `rules.yml` together with the
  corresponding validation rules when adding an input.
- Backend and AI tests always run on the default branch, since backend images
  still build on every default-branch pipeline. Change-based filtering remains
  on feature/MR pipelines. Governance and observability validation also run
  before merging.
- AI validation runs all `tests/ai`, using the MLOps dependencies without the
  optional PyTorch stack. These unit tests do not replace live integration jobs.
- Backend and AI results are published as JUnit reports; the backend's existing
  80% API coverage gate is unchanged.

## Images and concurrency

The data-pipeline build captures the pushed image digest and renders a copy of
the Airflow DAG into its `airflow-dags/` artifact. The publisher consumes that
artifact and its dotenv image reference. The source DAG's lab default remains
unchanged. The Docker build job installs Python using Alpine's package manager;
the shell publication runner needs no new software. Publication artifacts expire
after seven days: rerun the producer before retrying an older publisher.

OpenMetadata always consumes the governance build's dotenv tag. An
OpenMetadata-only change also builds governance, avoiding a guessed image tag.
Existing SHA/latest image publication remains available for other consumers.

All publishers targeting `lab-gitops/main` share a resource group. Database jobs
share another. Each MLOps workload has a lock so its existing fixed Kubernetes
Job name cannot be deleted by another invocation of the same CI job. Image
builds and Airflow/Grafana publication also have resource groups.

Temporary paths are scoped to the project workspace and CI job ID. GitOps
authentication uses `scripts/ci/git-askpass.sh` and the existing job environment
variables rather than a shared `/tmp/.netrc` or a `HOME` override.

Resource groups serialize this project's jobs. They do not lock writers from
other projects or guarantee deployment ordering between different pipelines.
This change does not alter GitLab's resource-group processing policy.

## Deliberately retained operational behavior

All 29 database-stage jobs retain `when: manual` and `allow_failure: false`.
Their existing runtime prerequisite checks and SQL are unchanged. Serialization
prevents concurrent CI database commands, but does not choose migration order.
An operator must still run the required migrations and tests in order.

Moving these controls to a separate operations pipeline, making migrations
automatic, adding a disposable PostgreSQL migration suite and turning MLOps
jobs into scheduled-only experiments are follow-up changes. They require a
separate rollout because they change the current operational workflow. MLOps
jobs still reconstruct their own datasets; they are not a new artifact chain.

## Verification

Run the offline CI checks with Python, PyYAML, pytest and Bash installed:

```sh
python -m pytest tests/ci -q
```

The rule model covers this repository's supported expressions and globs, not
the entire GitLab rules language. It checks single-file changes across feature,
default and renamed-default branches and merge requests, plus no-diff pipeline
sources. GitLab CI Lint on the actual server is still authoritative. Docker,
registry, Kubernetes and GitOps execution must be verified on the real runners;
the local checks do not deploy anything.
