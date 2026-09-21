# Repository and CI map for the next agent

Verified against the working tree on 2026-09-21. This describes the current
implementation, not a proposed directory reorganization. Start with
[AGENTS.md](../../AGENTS.md) and [the project README](../../Readme.md).

## 1. Repository layout

```text
chasse_immobiliere/
  AGENTS.md                    Agent instructions and starting point
  Readme.md                    Product overview, setup and implementation status
  .gitlab-ci.yml               Pipeline sources, stages and component includes
  .gitlab/ci/                  Job configuration and shared selection rules
  scripts/ci/                  Executable CI implementation, grouped by component
  src/
    api/                      FastAPI backend
      main.py                 Application entrypoint
      api/v1/                 HTTP router and endpoints
      core/                   Configuration, authentication and authorization
      schemas/                Request/response validation
      services/               Business rules and orchestration
      repositories/           Persistence queries
      db/                     SQLAlchemy models and sessions
      observability/          API metrics
    ai/matching/              Matching, datasets, evaluation, training and MLflow
    domain/, services/        Directory skeletons; not the active backend layers
  database/
    migrations/               Ordered SQL migrations and data evolution
    legacy/                   Legacy source schema/data
    seeds/                    Generation, S3 transfer and ingestion/load scripts
    oltp/                     Operational SQL and raw/staging schema definitions
    olap/                     Warehouse schema/load implementation
    tests/                    SQL assertions and data-quality checks
  pipelines/
    airflow/                  Ingestion DAG
    dbt/                      dbt project, sources, staging models and marts
  deploy/
    docker/                   Backend, data-pipeline and MLOps Dockerfiles
    kubernetes/backend/       Backend Kustomize and Argo CD resources
    kubernetes/pra/           PostgreSQL backup/disaster-recovery resources
    mlops/                    Ephemeral Kubernetes Job manifests
    openmetadata/             Metadata ingestion and governance manifests
    observability/            Monitoring deployment/provisioning resources
  governance/                 Governance engine, Dockerfile and JSON definitions
  observability/              Metrics Python code, Grafana dashboards and alerts
  tests/
    backend/                  API and business behavior
    ai/                       Matching and model/data behavior
    data/                     Data transformation regressions
    ci/                       Pipeline structure, rules, scripts and helper checks
  docs/                       Business, architecture and operational documentation
  evidence/                   Supporting evidence artifacts
  requirements*.txt           Dependency groups; no pyproject.toml
```

`ml/`, `deploy/helm/`, and `tests/unit`, `integration`, `security`, `e2e` are
directory skeletons, not proof that separate implementations or suites exist.
Active ML code is under `src/ai/matching/`. Check files before adding a parallel
implementation in a placeholder directory.

Documentation sections include business (`10-BUSINESS`), application
(`20-APPLICATION`), infrastructure (`30-INFRASTRUCTURE`), data (`40-DATA`), AI
(`50-AI`), security (`60-SECURITY`), DevOps (`70-DEVOPS`), operations
(`80-OPERATIONS`), observability (`90-OBSERVABILITY`), governance
(`95-GOVERNANCE`), decisions (`98-ADR`) and diagrams (`99-DIAGRAMS`).
`docs/evidence/` also holds historical evidence. Some enterprise documents are
forward-looking; do not equate their contents with deployed functionality.

## 2. CI configuration versus implementation

The root configuration includes component YAML files. Those files describe
jobs: rules, dependencies, variables, runner tags, images, artifacts and script
entrypoints. The implementation is in shell scripts, not large inline YAML.

| Configuration under `.gitlab/ci/` | Responsibility | Implementation under `scripts/ci/` |
| --- | --- | --- |
| `rules.yml` | Shared AI and governance rule templates | Configuration only |
| `pipeline-checks.yml` | `pipeline:validate` | `tests/ci/test_pipeline.py` |
| `database.yml` | SQL validation, manual migrations and operational tests | `database/*.sh` |
| `database-hunter-invoice.yml` | Migration 016 and hunter invoice assertions; shared database template | `database/migrate-016.sh`, `database/test-facture-chasseur.sh` |
| `database-search.yml` | Migration 017 and versioned search assertions; shared database template | `database/migrate-017.sh`, `database/test-demande-version-search.sh` |
| `warehouse.yml` | Warehouse validation and migration 003 | `warehouse/*.sh` |
| `backend.yml` | Backend validation, image build, GitOps publication | `backend/*.sh` and phase directories |
| `backend-tests.yml` | Backend/data test selection and coverage | `backend/tests.sh`, `backend/tests/` |
| `ai.yml` | AI validation and complete AI unit suite | `ai/validate.sh` |
| `ai-mlops.yml` | Image build and four runtime workloads | `ai-mlops/` |
| `ai-model-comparison.yml` | Runtime deterministic/ML comparison | `ai-model-comparison/compare.sh` |
| `data-pipeline-image.yml` | Build/check image and render pinned DAG artifact | `data-pipeline/build-image.sh` |
| `airflow.yml` | Publish the rendered DAG artifact | `airflow/publish-dags.sh` |
| `governance.yml` | Validate definitions and build governance image | `governance/*.sh` |
| `openmetadata.yml` | Publish metadata/governance manifests | `openmetadata/publish-gitops.sh` |
| `observability.yml` | Validate dashboards/alerts, provision Grafana, publish | `observability/*.sh` |
| `pra.yml` | Publish backup desired state | `pra/publish-gitops.sh` and phases |
| `runner-test.yml` | Runner diagnostics | Short inline commands; **not included by the root pipeline** |

`git-askpass.sh` supplies the existing GitOps credentials from environment
variables. `pin_airflow_image.py` edits a copied DAG to reference the image
digest built by its producer job. Neither helper contains real credentials.

## 3. How longer scripts are organized

```text
scripts/ci/backend/
  validate.sh
  validate/
    files-and-syntax.sh
    runtime-imports.sh
    authorization-and-payments.sh
    openapi-and-summary.sh
  tests.sh
  tests/
    files.sh
    imports-and-openapi.sh
    regression-suite.sh
  build-image.sh
  publish-gitops.sh
  publish-gitops/
    check-invoice-schema.sh    Read-only migrations 015/016 release prerequisite
    prepare.sh
    render-and-validate.sh
    publish.sh

scripts/ci/ai-mlops/
  build-image.sh
  evaluate.sh                 Entrypoint
  evaluate/                   prepare.sh, execute.sh, report.sh
  evaluate-after.sh           Diagnostics in after_script
  validate-training-dataset.sh
  validate-training-dataset/  Same phase convention
  split-training-dataset.sh
  split-training-dataset/     Same phase convention
  train-matching-model.sh
  train-matching-model/       Same phase convention
  *-after.sh                  Per-workload diagnostics

scripts/ci/pra/
  publish-gitops.sh
  publish-gitops/
    validate-runtime.sh
    validate-backup.sh
    prepare-gitops.sh
    publish.sh
    report.sh
```

Entrypoints source their phases in order using absolute paths based on
`CI_PROJECT_DIR`. Sourcing preserves shell variables, `cd`, `exit` and the
runner's shell options. Do not casually replace it with independent `sh`/`bash`
subprocesses or place sourced scripts inside conditionals that change error
handling. `after_script` runs in a fresh shell; it cannot rely on earlier exports.

Short setup and cleanup commands remain in YAML. Database scripts remain
separate per operation. `.database-operation` in `database.yml` centralizes
their identical manual rules, runner selection, dependency and resource lock.

## 4. Runtime flow and retained constraints

- Stages remain `validate -> database -> build -> deploy`. Explicit `needs`
  controls each path; stage order is not a universal release gate.
- Backend validation + backend tests + AI validation gate the backend image,
  which gates backend GitOps publication.
- Database/warehouse validation + backend/data tests gate the data image.
  Its rendered `airflow-dags/` artifact and dotenv image reference feed Airflow
  publication. The deployed DAG uses a digest; the source DAG retains its lab
  default. Publication artifacts expire after seven days.
- Governance validation gates its image, which is required by OpenMetadata
  publication. Never restore a guessed current-commit image fallback.
- AI validation gates the MLOps image. Evaluation, dataset validation, split,
  training and comparison remain separate runtime jobs. They do not consume a
  new shared dataset artifact chain. Training/comparison validate all current
  informative groups through `src/ai/matching/split_validation.py` and record
  `runtime-group-v2` plus dataset/split fingerprints in their evidence. Compare
  independent runs only when those identities match; a seed is not a dataset snapshot.
- All 37 database-stage operations are manual and blocking
  (`allow_failure: false`). Migration ordering is still an operational concern;
  a common resource group serializes jobs but does not pick the migration order.
- Client invoice migration 015 and SQL test 018 have dedicated jobs using the
  same database template. Backend GitOps publication checks migration 015 and
  `facture_client` table presence before writing GitOps. If the schema is absent,
  run `database:migrate-015`, then `database:test-facture-client`, and retry
  publication. This guard reads the database; it does not apply migrations.
- Hunter invoice migration 016 and SQL test 019 add two manual jobs through
  `database-hunter-invoice.yml`, inheriting the same resource lock. Publication
  also requires migration 016 and `facture_chasseur`; run `database:migrate-016`
  and `database:test-facture-chasseur` before publishing this backend version.
  See [GAP-BUS-004](../10-BUSINESS/GAP-BUS-004-FACTURE-CHASSEUR.md) for API,
  legacy-payment handling, file ownership and pending runtime verification.
- Search enrichment migration 017 is required by the backend and shared matching
  repository. Backend publication and all five matching workloads source the
  read-only `scripts/ci/database/check-search-schema.sh` prerequisite. Run
  `database:migrate-017`, then `database:test-demande-version-search` before
  those workloads. [Search enrichment handoff](../10-BUSINESS/DEMANDE-VERSION-SEARCH-ENRICHMENT.md)
  explains versioned sectors, explicit property assignment and matching policy.
- Docker-tagged runners handle containerized checks/builds. Shell-tagged jobs
  interact with Kubernetes and the separate GitOps/DAG repositories.
- `lab-gitops/main` publishers share a lock; individual MLOps workloads keep
  fixed Kubernetes Job names protected by per-workload locks. Locks are scoped
  to this GitLab project and do not guarantee newest-first publication.
- Temporary files use `$CI_PROJECT_DIR/.ci-tmp/$CI_JOB_ID`. GitOps auth uses
  environment credentials through askpass, not a shared `/tmp/.netrc`.
- Source branch rules use `CI_DEFAULT_BRANCH`. Destination GitOps branches
  remain `main`. Merge requests and tags validate without deploying.

See [the detailed CI guide](../../.gitlab/ci/README.md) for artifact handling,
pipeline-source behavior and changes deliberately deferred to a later rollout.

## 5. Verification and the encoding regression

Use Python 3.12. For offline CI checks, install pytest and PyYAML; Bash enables
shell syntax and executable observability checks. For AI tests install
`requirements-ai-mlops.txt`. Backend tests use `requirements-backend-test.txt`.
The optional `requirements-ai-training.txt` also includes PyTorch and is not
needed just to run the current AI regression suite.

```sh
python -m pip install 'PyYAML>=6,<7' 'pytest>=8,<9'
python -m pytest tests/ci -q
python -m pytest tests/ci/test_pipeline.py -q -k observability_validation
git diff --check
```

For backend/AI changes, after installing the matching requirements:

```sh
python -m pytest tests/ai -q
POSTGRES_PASSWORD=ci-test-only JWT_SECRET_KEY=ci-test-secret-at-least-32-characters \
  python -m pytest tests/backend tests/data tests/ai/test_candidate_availability.py \
  --cov=src/api --cov-fail-under=80
```

Windows example using the existing local environment, **if present**:

```powershell
& ./.venv-review/Scripts/python.exe -m pytest tests/ci -q
$env:POSTGRES_PASSWORD = 'ci-test-only'
$env:JWT_SECRET_KEY = 'ci-test-secret-at-least-32-characters'
& ./.venv-review/Scripts/python.exe -m pytest tests/backend tests/data tests/ai/test_candidate_availability.py --cov=src/api --cov-fail-under=80
```

The `.venv-review/` directory and previous extraction snapshots are local-only.
A fresh checkout should create its own environment using the project README.

**Known regression, now fixed:** the extracted observability validator expected
corrupted em dashes in two dashboard titles. The JSON dashboards were correct.
`scripts/ci/observability/validate.sh` now expresses the expected em dash as
Python `\u2014`. `test_observability_validation_executes_and_rejects_wrong_titles`
runs the actual sourced script and verifies both success and rejection of
incorrect titles. Preserve this regression coverage. Always specify UTF-8 when
reading/writing files; syntax checks and text-preservation comparisons alone
cannot detect an already-corrupted semantic expectation.

**Training/comparison incident:** generated data grew from the historical
11-group benchmark to 27 informative groups. Runtime jobs had still enforced
the V1 ID lists. The shared runtime validator now checks source coverage,
partition row contents, seeded assignment and leakage against the current
dataset. Historical `validate_frozen_split` remains available for explicit V1
benchmark validation; it no longer gates live training/comparison. Artifact and
MLflow split versions distinguish new runs from that benchmark. The artifact
field `frozen_split_validation` is retained for compatibility but carries
`frozen_split_v1: false` for runtime V2 results.

A separate stray `- .gitlab-ci.yml` command in training's extracted cleanup
script has been removed. The CI suite executes every MLOps cleanup script with
`kubectl` stubbed out, so valid shell syntax alone cannot hide that failure again.
`tests/ai/test_matching_runtime_split.py` runs both Python entrypoints with a
synthetic 27-group dataset, real training/comparison and mocked external services.

The observed local check results are historical evidence, not a promise about
a new checkout or live runners. Tests
check the repository's supported rule expressions, graph, shell syntax, script
references, image pinning, authentication helper and observability validation.
GitLab CI Lint and actual runner execution remain the authority for the live
pipeline. Do not run publication/migration scripts locally as a substitute.

## 6. Editing checklist

1. Read the component YAML, entrypoint and relevant phases before editing.
2. Put runtime application behavior in `src/`, manifests in `deploy/`, CI
   execution in `scripts/ci/`, and job orchestration in `.gitlab/ci/`.
3. Keep job names and operational behavior stable for a structural-only change.
4. Update change filters for moved/new implementation paths. Ensure every
   selected consumer still has its required producer selected.
5. Keep YAML at most 200 lines and shell files at most 250 lines, as currently
   checked by `tests/ci/test_pipeline.py`. Split by operation, not arbitrary chunks.
6. Run affected behavior checks and CI checks; distinguish offline evidence
   from live infrastructure verification in the handoff.
7. Update this map when entrypoints or conventions change. Treat root scratch
   files, ignored local environments and credentials as local context, not new
   application architecture.

## 7. Client invoice increment

See [GAP-BUS-003](../10-BUSINESS/GAP-BUS-003-FACTURE-CLIENT.md) for the layer map,
receipt prerequisite, authorization, audit and live verification handoff.
It is implemented and locally tested; the user owns commit/push and lab checks.
Do not confuse the local PostgreSQL verification with deployed runtime evidence.
