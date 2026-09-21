# Real Estate Intelligence Platform

Real-estate business API and Data & AI platform for versioned search requirements, property matching, analytics, and governance.

**For the next agent:** start with [AGENTS.md](AGENTS.md) and the
[current repository and CI map](docs/70-DEVOPS/REPOSITORY-AND-CI-MAP.md).
CI configuration and extracted scripts are documented in the
[CI guide](.gitlab/ci/README.md).

**Implementation snapshot: 2026-09-11.** This repository contains an implemented FastAPI backend, PostgreSQL migrations, data pipelines, deterministic matching, ML experiment tooling, automated tests, and deployment configuration. Broader enterprise documents also describe future capabilities; documentation alone does not establish that a capability is deployed.

## Current architecture

```text
API clients / OpenAPI UI
          |
          v
FastAPI: authentication, business services, recommendations, audit
          |
          v
PostgreSQL: real_estate (OLTP)

Source / MinIO -> raw -> staging -> OLTP / warehouse -> dbt analytics
                         Airflow orchestration
                         OpenMetadata governance

GitLab CI -> images and GitOps repository -> Argo CD -> Kubernetes
Prometheus / Grafana <- backend and data pipeline metrics
```

Business services and deterministic matching are packaged in one backend application. Authentication uses application identities, password hashing, JWT, and role checks. React, Keycloak/OIDC, Vault integration, semantic search, and an LLM assistant are future application capabilities, not implemented integrations in this repository. Shared infrastructure may be managed in separate repositories.

## Repository map

| Path | Responsibility |
|---|---|
| `src/api/api/v1/` | HTTP routes for authentication and business operations |
| `src/api/services/` | Business services and audit handling |
| `src/api/repositories/`, `src/api/db/` | Persistence access, SQLAlchemy models, sessions |
| `src/api/schemas/`, `src/api/core/` | API validation, settings, password/JWT helpers, identity and role checks |
| `src/ai/matching/` | Candidate retrieval, scoring, evaluation, datasets, training, comparison, MLflow tracking |
| `database/` | SQL migrations, legacy input, seed/load scripts, OLTP/warehouse SQL, SQL tests |
| `pipelines/airflow/` | Ingestion DAG; currently triggered manually (`schedule=None`) |
| `pipelines/dbt/` | Staging views and analytical marts |
| `governance/` | OpenMetadata definitions and governance script |
| `observability/` | Metrics collectors, dashboards, alert rules |
| `deploy/` | Dockerfiles, Kubernetes/Kustomize resources, OpenMetadata and MLOps jobs |
| `.gitlab/ci/` | Validation, tests, image builds, database and GitOps workflows |
| `scripts/ci/` | CI implementation scripts and named phases; YAML contains job configuration |
| `tests/ci/` | Offline pipeline selection, dependency, script and helper regression checks |
| `tests/backend/`, `tests/data/`, `tests/ai/` | Executable Python test suites |
| `docs/`, `evidence/` | Architecture, implementation documentation, evidence |

The `src/domain/`, `src/services/`, `ml/`, `deploy/helm/`, and unit/integration/security/e2e directory skeletons are placeholders. Dependencies are defined in `requirements*.txt`; there is no `pyproject.toml`.

## Local setup and tests

Use Python 3.12, matching the backend Dockerfile and CI. Run these PowerShell commands from the repository root. They invoke the virtual environment directly, without activation.

```powershell
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-backend-test.txt
$env:POSTGRES_PASSWORD = 'local-test-only'
$env:JWT_SECRET_KEY = 'local-test-only-secret-at-least-32-characters'
.venv/Scripts/python.exe -m pytest tests/backend tests/data tests/ai/test_candidate_availability.py -v --cov=src/api --cov-report=term-missing --cov-fail-under=80
```

This uses the backend CI test selection and coverage threshold. For all Python tests, install training dependencies as well:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-ai-training.txt
.venv/Scripts/python.exe -m pip install 'PyYAML>=6,<7'
.venv/Scripts/python.exe -m pytest tests -q
```

These tests do not establish live PostgreSQL, Kubernetes, Airflow, or MLflow availability. SQL validation is maintained separately under `database/tests/` and in database CI workflows.

## Run the API

Business operations require a reachable PostgreSQL database with application migrations applied. Migration prerequisites and execution paths are maintained in the [database CI workflow](.gitlab/ci/database.yml) and [implemented data architecture](docs/40-DATA/ARCHITECTURE-DATA-IMPLEMENTEE.md). Scripts include legacy-data dependencies and execution guards; they are not a generic replayable bootstrap loop.

Set values for your local database, replacing the placeholders:

```powershell
$env:POSTGRES_HOST = '127.0.0.1'
$env:POSTGRES_PORT = '5432'
$env:POSTGRES_DB = 'real_estate'
$env:POSTGRES_USER = 'real_estate_user'
$env:POSTGRES_PASSWORD = '<your-local-database-password>'
$env:JWT_SECRET_KEY = '<your-generated-local-signing-secret>'
.venv/Scripts/python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

Settings also support an ignored root `.env` file. The default database host is a Kubernetes service address, so local runs normally need `POSTGRES_HOST` overridden. `POSTGRES_PASSWORD` and `JWT_SECRET_KEY` are required. JWT defaults are HS256 and a 30-minute access-token lifetime.

- [OpenAPI UI](http://127.0.0.1:8000/docs): routes and request schemas.
- [Liveness](http://127.0.0.1:8000/health): application health without a database query.
- [Readiness](http://127.0.0.1:8000/ready): database connectivity; returns 503 when unavailable.
- [Metrics](http://127.0.0.1:8000/metrics): Prometheus endpoint.

Business endpoints are under `/api/v1`. Login is `POST /api/v1/auth/login` with JSON `email` and `password`; use the returned token as `Authorization: Bearer <token>`. An active, provisioned `real_estate.utilisateur` account is required. Migration 006 creates no default account. Account roles and provisioning evidence are described in the [security implementation document](docs/60-SECURITY/SECURITY-RBAC-AUDIT-IMPLEMENTATION-EVIDENCE.md).

## Deployment and observability

The [root pipeline](.gitlab-ci.yml) includes the actual CI modules. Backend image construction uses `deploy/docker/Dockerfile.backend` and packages `src/api` and `src/ai`. Backend manifests use Kustomize and specify one replica, resource requests/limits, health probes, a Service, and a ServiceMonitor. CI replaces image-tag placeholders before GitOps publication.

Argo CD reconciles permanent backend deployment from a separate GitOps repository. CI also contains database operations, secret bootstrap, and transient jobs. The backend consumes Kubernetes Secrets for database and authentication settings.

Prometheus instrumentation, pipeline metrics, Grafana dashboards, and alert definitions are implemented here. Loki, Tempo, OpenTelemetry, TLS termination, and other shared infrastructure are discussed in platform architecture documents; live configuration must be verified separately.

## Documentation and evidence

Start with the [documentation index](docs/README.md), then use these implementation references:

- [Application architecture](docs/20-APPLICATION/01-Application-Architecture.md)
- [Client invoice implementation and pending deployment checks](docs/10-BUSINESS/GAP-BUS-003-FACTURE-CLIENT.md)
- [Hunter invoice workflow, file map and GitLab/runtime handoff](docs/10-BUSINESS/GAP-BUS-004-FACTURE-CHASSEUR.md)
- [Implemented data architecture](docs/40-DATA/ARCHITECTURE-DATA-IMPLEMENTEE.md)
- [Deterministic matching baseline](docs/50-AI/11-Matching-Baseline-Implementation.md)
- [Labelled dataset strategy](docs/50-AI/12-Labelled-Dataset-Strategy.md)
- [Authentication, RBAC, and audit](docs/60-SECURITY/SECURITY-RBAC-AUDIT-IMPLEMENTATION-EVIDENCE.md)
- [Governance implementation](governance/README.md)

ADRs are under `docs/98-ADR/`, PlantUML sources and renders under `docs/99-DIAGRAMS/`, and competency evidence under `docs/evidence/`.

| Status | Meaning and current evidence |
|---|---|
| Implemented | Source, SQL, tests, and deployment configuration exist in this repository. |
| Locally verified | On 2026-09-11, `python -m pytest tests -q` in the existing review environment completed with 239 passed and 7 deprecation warnings. This was not a fresh dependency-install or live-platform test. |
| Historically runtime-evidenced | Dated documents record earlier platform executions; consult their scope and limitations. |
| Planned | React UI, enterprise IAM/secret integration, semantic/LLM application capabilities, and other explicitly future architecture items. |
| Requires live verification | Current deployment health, external platform configuration, database state, and recovery readiness. |

Documentation should evolve with implementation and evidence. A target design or an old successful execution does not prove current runtime state.
