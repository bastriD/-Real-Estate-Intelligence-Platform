# Application Architecture

**Version:** 1.1

**Status:** Implementation-aligned repository snapshot

**Owner:** Bastri Murad  
**Project:** Real Estate Intelligence Platform  
**Platform:** Enterprise AI Platform  
**Last Updated:** 2026-09-11

## 1. Scope and current architecture

The application is a modular FastAPI backend. HTTP handlers, business services, repositories, schemas, and deterministic matching are packaged together in one image. They are Python modules within one deployment, not independently deployed business services.

This document describes repository implementation. Manifests and historical evidence do not independently establish current deployment health. Broader platform documents describe shared infrastructure and target capabilities that may be managed elsewhere.

```text
API client / FastAPI OpenAPI UI
              |
              v
FastAPI routes (/api/v1)
              |
       JWT identity + role checks
              |
              v
Business services -----------------> Deterministic matching
              |                            |
              v                            v
SQLAlchemy repositories             Psycopg candidate queries
              |                            |
              +------------+---------------+
                           v
               PostgreSQL real_estate
                  business + audit data
```

React is planned. No React application or frontend build is implemented in this repository; the current browser interface is FastAPI's API documentation.

## 2. Components and source locations

| Component | Location | Responsibility |
|---|---|---|
| Entry point | `src/api/main.py` | FastAPI app, routes, metrics middleware |
| HTTP API | `src/api/api/v1/` | Authentication, clients, mandates, demands, properties, presentations, recommendations, visits, health |
| Business services | `src/api/services/` | Business validation, operations, recommendation persistence, auditing |
| Persistence | `src/api/repositories/`, `src/api/db/` | SQLAlchemy access, models, sessions |
| API schemas | `src/api/schemas/` | Request and response contracts |
| Security/configuration | `src/api/core/` | Settings, password/JWT helpers, identity and role dependencies |
| Matching and experiments | `src/ai/matching/` | Retrieval, scoring, evaluation, datasets, training, comparison, MLflow tracking |
| Metrics | `src/api/observability/metrics.py` | HTTP and business Prometheus instrumentation |

`src/services/`, `src/domain/`, and `ml/` are directory skeletons, not current implementation locations. Standalone notification and analytics HTTP services are not implemented; analytical transformations are in `pipelines/dbt/`.

## 3. Business and data behavior

The backend manages clients, mandates, versioned search demands, properties, presentations, and visits. A demand can exist before a mandate, as introduced by migration 005. Matching uses a specific `demande_version`, preserving the association between results and the customer's criteria used for evaluation.

The recommendation service retrieves PostgreSQL candidates, computes deterministic scores, and persists presentations with business audit handling. It imports matching code directly; it does not call an LLM or a separately deployed recommendation service.

Separate pipeline code implements raw ingestion, staging, warehouse loading, and dbt analytics. Airflow orchestrates the data workflow, and OpenMetadata governance code manages metadata. These workflows complement the transactional API.

## 4. Authentication, authorization, and secrets

The implemented identity flow is:

1. `POST /api/v1/auth/login` accepts JSON email and password.
2. `AuthService` checks `real_estate.utilisateur` and verifies its password hash.
3. The backend issues a JWT; defaults are HS256 and a 30-minute lifetime.
4. Protected requests supply `Authorization: Bearer <token>`.
5. `get_current_user()` validates the token and reloads the active PostgreSQL identity. `require_roles()` enforces endpoint role requirements using that identity.

Roles are `ADMIN`, `CHASSEUR`, `CLIENT`, and `SERVICE`. Password hashing uses `pwdlib` with Argon2 support. Business audit records are stored in `real_estate.audit_log`. Migration 006 creates no default account.

Configuration comes from environment variables or a local `.env`. `POSTGRES_PASSWORD` and `JWT_SECRET_KEY` are required. The backend Deployment references `real-estate-postgresql-secret` and `real-estate-backend-auth` Kubernetes Secrets.

Keycloak, OAuth2/OIDC federation, and Vault are future integration options. They are not the current authentication or secret-loading mechanisms. The backend serves HTTP on port 8000; TLS termination is an infrastructure responsibility and is not established by its Deployment manifest.

## 5. Deployment and availability

`deploy/docker/Dockerfile.backend` uses Python 3.12, copies `src/`, installs `requirements-ai.txt` (which includes backend dependencies), and starts `uvicorn src.api.main:app` as a non-root user.

`deploy/kubernetes/backend/` contains a Deployment, Service, ServiceMonitor, Kustomize configuration, and Argo CD Application. The Deployment specifies one replica, resource requests/limits, registry credentials, and liveness/readiness probes. One replica does not establish high availability or tested horizontal scalability.

Backend CI validates and builds the image, substitutes its tag, and publishes desired state to a separate GitOps repository. Argo CD reconciles the permanent workload. CI additionally performs secret bootstrap; database and transient job workflows have separate execution paths.

React deployment, independent business-service deployments, autoscaling, and event consumers remain future work requiring implementation and validation evidence.

## 6. Health and observability

| Endpoint | Behavior |
|---|---|
| `/docs`, `/redoc`, `/openapi.json` | Generated API documentation and contract |
| `/health` | Liveness without a database query |
| `/ready` | PostgreSQL connectivity; 503 when unavailable |
| `/api/v1/health`, `/api/v1/ready` | Versioned health routes |
| `/metrics` | Prometheus metrics; excluded from OpenAPI |

HTTP middleware and business services expose Prometheus metrics. Dashboards and alert definitions are maintained in observability directories. Loki, Tempo, and OpenTelemetry appear in platform architecture, but `src/api/main.py` does not configure distributed tracing or an OpenTelemetry exporter.

## 7. Validation and evidence

Python suites are in `tests/backend/`, `tests/data/`, and `tests/ai/`; SQL tests are in `database/tests/`. Backend CI runs its selected tests with an 80% API coverage threshold.

On 2026-09-11, the complete local Python suite passed in the existing review environment: 239 tests, 7 deprecation warnings. This confirms that run, not live database integration, deployment health, fresh dependency installation, or historical runtime claims.

Use the [root README](../../Readme.md) for dependencies, settings, tests, and API startup. Dated security and recommendation evidence describes the scope of earlier live validation.

## 8. Planned capabilities

- React interface using the existing API and backend authorization.
- Enterprise identity federation and secret-manager integration where justified.
- Semantic search, Ollama/LLM integration, and an AI assistant; Qdrant is a target option, not a current application dependency.
- Notifications, event-driven workers, independent deployment, and scaling based on measured needs.

Training and comparison tooling already exists in `src/ai/matching/`; its presence does not mean a trained model replaces the deterministic recommendation path.

## 9. Related documentation

- [Documentation index](../README.md)
- [Implemented data architecture](../40-DATA/ARCHITECTURE-DATA-IMPLEMENTEE.md)
- [Matching baseline](../50-AI/11-Matching-Baseline-Implementation.md)
- [Authentication, RBAC, and audit](../60-SECURITY/SECURITY-RBAC-AUDIT-IMPLEMENTATION-EVIDENCE.md)
- [Recommendation audit runtime evidence](../60-SECURITY/RECOMMENDATION-AUDIT-RUNTIME-EVIDENCE.md)
