# Real Estate Intelligence Platform

Enterprise Data & AI platform for real-estate intelligence, property matching, analytics, governance and AI-assisted workflows.

---

## 1. Project Overview

The project combines:

```text
Application
+
Data Platform
+
AI / MLOps
+
DevOps / GitOps
+
Security
+
Observability
+
Governance
```

The goal is to provide an enterprise-style platform capable of managing real-estate search requirements, property data, matching, analytics and AI-assisted processing while preserving traceability, security and data governance.

---

## 2. Architecture Overview

```text
Users
  |
  v
Application / API
  |
  +-------------------------+
  |                         |
  v                         v
PostgreSQL                AI Services
OLTP / OLAP               Ollama / ML
  |                         |
  v                         v
Airflow / dbt             MLflow
  |
  v
Analytics / Governance

        Infrastructure
             |
             v
         Kubernetes
             |
             v
           GitOps
             |
             v
          Argo CD

Observability:
Prometheus
Grafana
Loki
Tempo
OpenTelemetry
```

---

## 3. Repository Structure

```text
chasse_immobiliere/
│
├── .gitlab/
│   └── ci/
│
├── database/
│   ├── migrations/
│   ├── oltp/
│   ├── olap/
│   ├── seeds/
│   └── tests/
│
├── deploy/
│   ├── docker/
│   ├── helm/
│   └── kubernetes/
│
├── docs/
│   ├── 00-FOUNDATION/
│   ├── 10-BUSINESS/
│   ├── 20-APPLICATION/
│   ├── 30-INFRASTRUCTURE/
│   ├── 40-DATA/
│   ├── 50-AI/
│   ├── 60-SECURITY/
│   ├── 70-DEVOPS/
│   ├── 80-OPERATIONS/
│   ├── 90-OBSERVABILITY/
│   ├── 95-GOVERNANCE/
│   ├── 98-ADR/
│   ├── 99-DIAGRAMS/
│   └── evidence/
│
├── ml/
│   ├── evaluation/
│   ├── features/
│   ├── models/
│   └── training/
│
├── pipelines/
│   ├── airflow/
│   └── dbt/
│
├── scripts/
│
├── src/
│   ├── ai/
│   ├── api/
│   ├── domain/
│   └── services/
│
├── tests/
│   ├── e2e/
│   ├── integration/
│   ├── security/
│   └── unit/
│
├── .gitlab-ci.yml
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## 4. Documentation

The complete project documentation is maintained under:

```text
docs/
```

Documentation entry point:

```text
docs/README.md
```

It contains:

- project foundation;
- business architecture;
- application architecture;
- infrastructure architecture;
- Data architecture;
- AI architecture;
- security;
- DevOps;
- operations;
- observability;
- governance;
- ADRs;
- diagrams;
- competency evidence.

---

## 5. Application

Application source code is maintained under:

```text
src/
```

Main responsibilities:

```text
src/api
    FastAPI endpoints

src/services
    application / business services

src/domain
    domain models and business logic

src/ai
    AI integration layer
```

The application architecture is designed to keep HTTP, business logic, persistence and AI integrations separated.

---

## 6. Database

Database implementation is maintained under:

```text
database/
```

Structure:

```text
database/migrations
    schema migrations

database/seeds
    demonstration / synthetic data

database/oltp
    transactional SQL

database/olap
    warehouse / analytics SQL

database/tests
    SQL and database validation
```

PostgreSQL is the primary relational database.

---

## 7. Data Platform

Data workflows are maintained under:

```text
pipelines/
```

### Airflow

```text
pipelines/airflow/
```

Responsibilities:

- ingestion;
- orchestration;
- dependencies;
- scheduling;
- workflow monitoring.

### dbt

```text
pipelines/dbt/
```

Responsibilities:

- SQL transformation;
- analytical models;
- Data Quality tests;
- lineage support.

---

## 8. OLTP / OLAP

The platform separates operational and analytical processing.

```text
OLTP
    transactional workloads
    normalized data model

OLAP
    analytical workloads
    warehouse
    KPI
    reporting
```

Target PostgreSQL logical areas:

```text
real_estate
staging
warehouse
analytics
```

---

## 9. AI / Machine Learning

Machine Learning implementation is maintained under:

```text
ml/
```

Structure:

```text
ml/features
    feature engineering

ml/training
    training workflows

ml/evaluation
    model evaluation

ml/models
    model-related runtime artifacts/configuration
```

The initial real-estate matching strategy follows:

```text
SQL filtering
      |
      v
Explainable deterministic scoring
      |
      v
ML comparison
      |
      v
Optional semantic enrichment
      |
      v
Human validation
```

---

## 10. MLOps

The MLOps architecture uses:

```text
Airflow
+
MLflow
+
MinIO
+
Git
```

Responsibilities:

```text
Airflow
    workflow orchestration

MLflow
    experiment tracking
    metrics
    parameters
    model registry

MinIO
    model artifacts

Git
    source and configuration versioning
```

---

## 11. Local AI

The platform follows a:

```text
Local-first AI
```

strategy.

Ollama is used for local LLM inference.

The architecture is designed so that sensitive data can remain within the controlled infrastructure where appropriate.

---

## 12. Tests

Tests are maintained under:

```text
tests/
```

Categories:

```text
unit
integration
security
e2e
```

Database-specific tests are located under:

```text
database/tests/
```

The project distinguishes:

```text
PLANNED
EXECUTED
PASS
FAIL
BLOCKED
```

A written test without execution is not treated as runtime evidence.

---

## 13. Deployment

Deployment artifacts are maintained under:

```text
deploy/
```

Structure:

```text
deploy/docker
deploy/kubernetes
deploy/helm
```

Kubernetes is the target orchestration platform.

---

## 14. CI/CD

The project uses:

```text
GitLab CI
```

for Continuous Integration.

The root pipeline entry point is:

```text
.gitlab-ci.yml
```

Modular pipeline definitions are maintained under:

```text
.gitlab/ci/
```

Target modules include:

```text
application.yml
database.yml
data.yml
ml.yml
security.yml
docker.yml
quality.yml
```

---

## 15. GitOps

Continuous Delivery is separated from CI.

```text
GitLab CI
    |
    v
Validate / Test / Build / Publish
    |
    v
GitOps Desired State
    |
    v
Argo CD
    |
    v
Kubernetes
```

GitLab CI does not directly own the final Kubernetes runtime state.

Argo CD performs reconciliation.

---

## 16. Observability

The observability platform includes:

```text
Prometheus
Grafana
Loki
Tempo
OpenTelemetry
```

The target standard for workloads is:

```text
Metrics
Logs
Traces
Health
```

---

## 17. Security

The platform follows principles including:

```text
Least Privilege
Defense in Depth
Secure by Default
Explicit Authorization
Secret Separation
TLS
Auditability
```

Security implementation covers:

- application;
- Kubernetes;
- containers;
- networking;
- databases;
- AI;
- CI/CD.

---

## 18. Data Governance

Data governance is supported by:

```text
OpenMetadata
```

Target capabilities include:

```text
Ownership
Glossary
Classification
Lineage
Profiling
Data Quality
Metadata discovery
```

---

## 19. Infrastructure

The platform architecture is built around:

```text
Proxmox
Kubernetes
NGINX Ingress
cert-manager
PostgreSQL
MinIO
GitLab
Argo CD
```

Detailed infrastructure documentation is located in:

```text
docs/30-INFRASTRUCTURE/
```

---

## 20. Architecture Decisions

Architecture decisions are tracked as ADRs under:

```text
docs/98-ADR/
```

Important architectural choices must remain traceable.

---

## 21. Diagrams

Architecture diagrams are maintained as code under:

```text
docs/99-DIAGRAMS/
```

Source format:

```text
PlantUML
```

Rendered versions are stored under:

```text
docs/99-DIAGRAMS/rendered-diagrams/
```

---

## 22. Evidence

Competency evidence indexing is located under:

```text
docs/evidence/
```

Structure:

```text
01-BC01
02-BC02
03-BC03
05-BC05
99-CROSS-CUTTING
```

Evidence documentation points to actual implementation and runtime results.

Implementation itself remains outside `docs/`.

---

## 23. Documentation vs Implementation

The repository intentionally separates:

```text
docs/
```

from:

```text
src/
database/
pipelines/
ml/
tests/
deploy/
```

Rule:

```text
docs
=
WHAT
WHY
ARCHITECTURE
GOVERNANCE
EVIDENCE INDEX
```

while:

```text
implementation
=
CODE
SQL
PIPELINES
TESTS
DEPLOYMENT
RUNTIME
```

---

## 24. Documentation Freeze

The initial documentation baseline has been completed.

From this stage onward, documentation should evolve only from:

```text
real implementation
real architecture decisions
real tests
real measurements
real incidents
real runtime evidence
```

---

## 25. Implementation Roadmap

The implementation phase follows:

```text
1. PostgreSQL schema
2. migration.sql
3. Seed / synthetic dataset
4. Database validation
5. OLTP queries
6. EXPLAIN ANALYZE optimization
7. OLAP warehouse
8. Airflow pipeline
9. Data Quality
10. Matching baseline
11. ML experiments
12. MLflow tracking
13. FastAPI application
14. Docker
15. GitLab CI
16. Kubernetes
17. GitOps
18. Observability
19. Security tests
20. Backup / restore evidence
21. Final evidence collection
```

---

## 26. Current Phase

```text
DOCUMENTATION BASELINE
        |
        v
      COMPLETE
        |
        v
IMPLEMENTATION
```

The project now moves from architecture and documentation into executable implementation and evidence production.

---

## 27. Quick Links

Documentation:

```text
docs/README.md
```

Architecture decisions:

```text
docs/98-ADR/
```

Diagrams:

```text
docs/99-DIAGRAMS/
```

Competency evidence:

```text
docs/evidence/
```

Database implementation:

```text
database/
```

Application implementation:

```text
src/
```

AI / ML:

```text
ml/
```

Data pipelines:

```text
pipelines/
```

Deployment:

```text
deploy/
```

Tests:

```text
tests/
```

---

# Project Status

```text
Architecture       COMPLETE BASELINE
Documentation      COMPLETE BASELINE
Evidence Mapping   COMPLETE BASELINE
Implementation     STARTING
Runtime Evidence   PENDING
Final Validation   PENDING
```

---

**REAL ESTATE INTELLIGENCE PLATFORM — PROJECT ENTRY POINT**