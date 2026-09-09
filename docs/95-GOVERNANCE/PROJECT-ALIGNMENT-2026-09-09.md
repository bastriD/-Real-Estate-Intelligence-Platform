# Project alignment review — 9 September 2026

Reviewed commit: `d43ea13`.

## Verdict

The implementation is broadly aligned with the repository's real-estate business and architecture objectives. Delivery is substantially beyond the main README's “Implementation STARTING” status. Full acceptance, production readiness, and certification completion are not established by this review.

The main gap is consolidation: finish authorization, demonstrate the integrated business flow, and reconcile project tracking with dated execution evidence before expanding the platform.

## Scope and evidence limits

This is a repository review against the project constitution, business architecture, backlog, implementation, CI definitions, and evidence indexes. It is not a fresh cluster audit or an independent verification against the official RNCP evaluation grid. Historical runtime statements in `prompts/` are treated as reported observations, not fresh verification. Screenshot files exist under `evidence/`; their contents were not inspected in this review.

The working tree was clean before this report. No application or deployment changes were made.

## Alignment by capability

| Capability | Repository evidence | Assessment |
|---|---|---|
| Real-estate operations | `src/api/api/v1/router.py` exposes clients, mandates, versioned requests, properties, presentations, recommendations, and visits | Strong implementation alignment; integrated acceptance remains to be demonstrated |
| Data platform | SQL migrations and quality checks; Airflow chains source generation, RAW, STAGING, OLTP, warehouse, dbt, and metrics | Strong alignment with the planned layered data flow |
| Explainable matching | `src/api/services/recommendation.py` filters, scores, ranks, and persists deterministic recommendations | Aligned with the constitution's requirement to retain deterministic business rules |
| ML progression | Dataset preparation, validation, splitting, logistic regression training, model comparison, and MLflow integration under `src/ai/matching/` | Substantial implementation exists; this alone does not prove business improvement or justify model promotion |
| Governance | Governance engine, OpenMetadata configurations and jobs, dbt ingestion assets | Implemented foundation; current ownership, classification, and lineage still need dated verification |
| CI and delivery | Modular GitLab pipeline, Dockerfiles, Kubernetes manifests, GitOps publication | Broadly aligned; deployed health and successful execution were not checked |
| Observability | API Prometheus middleware, recommendation metrics, ServiceMonitor, dashboard and alert assets | Metrics implementation is concrete; a complete logs/traces/alert-delivery demonstration was not established |
| Security | JWT identity, password hashing, active-account checks, admin authorization on client endpoints | Partial; authorization coverage is the most immediate implementation gap |
| Recovery and privacy evidence | Evidence indexes explicitly retain runtime work and restore measurements as pending | Completion cannot be claimed |
| Project tracking | README and backlog disagree with implementation and later progress notes | Material documentation drift |

## Prioritized findings

### 1. Complete application authorization

`src/api/api/v1/endpoints/clients.py` protects its operations with `require_roles("ADMIN")`. Other business endpoint modules do not reference `require_roles` or `get_current_user`; neither the aggregate router nor the application supplies global authentication. For example, listing requests in `demandes.py` only depends on the database session.

Consequently, the application code does not enforce authentication on those business routes. Network exposure and any external gateway controls were not verified. Define the intended role/resource-access matrix, apply it to mandates, requests, presentations, visits, recommendations, and properties as appropriate, and verify anonymous, forbidden-role, and cross-owner access cases.

### 2. Reconcile project status with what exists

The root README still declares implementation starting and runtime evidence pending. The application backlog leaves API endpoints, Pydantic validation, health endpoints, tests, and observability unchecked, although their implementations exist. The older `prompts/project_alignment.md` says warehouse and analytics are absent; later code and progress notes supersede that statement.

The README also presents `pyproject.toml` and `src/services` as repository structure, whereas dependencies use requirements files and business services currently live under `src/api/services`.

Update one authoritative status matrix with separate columns for planned, implemented, executed, and accepted. Link historical notes rather than treating all snapshots as current. Do not convert implementation presence into a PASS claim.

### 3. Establish integrated business acceptance

The repository contains 199 `def test_` declarations across backend and AI tests. This is a source count, not a collected or passing test count. Sampled API tests use mocks and dependency overrides; these are useful but do not establish a real PostgreSQL-backed end-to-end flow.

Demonstrate an authenticated scenario covering client, request/version, mandate association according to business rules, recommendations, presentation feedback, and visit tracking. Include persistence, duplicate recommendation handling, and access denial. Record commit, environment, commands, results, and artifact locations.

The backend CI job enforces 80% coverage, but this review did not fetch its current result. The Windows Python alias could not run; the available bundled Python lacks pytest and backend dependencies. No tests were rerun, and no fresh coverage claim is made.

### 4. Close operational evidence gaps

The recovery evidence index still records restore execution and measured RPO/RTO as incomplete. The privacy evidence index describes runtime evidence as pending. Prioritize a controlled restore with content validation, the implemented privacy controls and their results, and dated pipeline/GitOps/monitoring evidence tied to the reviewed version.

Existing screenshots and historical runtime notes mean evidence is not wholly absent. The problem is traceable acceptance and current verification.

### 5. Remove certificate-verification bypasses from delivery

GitOps publication in `.gitlab/ci/backend.yml` sets `GIT_SSL_NO_VERIFY=true` for clone and push; similar settings exist in other publication jobs. This weakens the documented secure-default/TLS objective. Configure trust for the lab certificate authority and verify publication with certificate checks enabled.

## Recommended next milestone

Make the current application demonstrably complete enough for review:

1. Finish role and resource authorization and its tests.
2. Run the backend/AI CI checks and a PostgreSQL-backed business acceptance scenario; retain results.
3. Capture data pipeline, governance, observability, and recovery evidence against known versions.
4. Refresh the README, backlog, and competency evidence matrix from those results.

RAG, additional agents, and further platform expansion should follow this milestone unless an explicit evaluation requirement makes them necessary sooner. The existing data, backend, matching, and governance work is relevant to the project; the next increment should turn that work into secure, reproducible, demonstrated business behavior.
