# Real Estate Intelligence Platform

An end-to-end **Data & AI platform** built around a real-estate business application, combining data engineering, MLOps, Kubernetes, GitOps, observability, governance, and backend engineering.

The project demonstrates how a business application can evolve into a governed and observable data platform: from operational transactions and versioned customer requirements to data pipelines, analytical models, property matching, ML experimentation, monitoring, and automated deployment.

> **Status:** Active engineering project developed as part of my Data & AI specialization.

---

## What this project demonstrates

This repository is not only a REST API.

It brings together several engineering disciplines in one practical platform:

* Data Engineering
* MLOps
* Platform Engineering
* DevOps / GitOps
* Backend Engineering
* Data Governance
* Observability
* Security
* Architecture as Code

The objective is to build a reproducible platform where application, data and AI workloads share the same engineering foundations.

---

## Architecture

```text
                         BUSINESS USERS
                               │
                               ▼
                         FastAPI Backend
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
          PostgreSQL      Matching Engine    Prometheus
            OLTP               │
              │                ▼
              │             MLflow
              ▼
        Data Pipelines
              │
        ┌─────┴─────┐
        ▼           ▼
      Airflow      dbt
        │           │
        └─────┬─────┘
              ▼
        Data Warehouse
              │
              ▼
         Analytics / AI

──────────────── PLATFORM LAYER ────────────────

GitLab CI → GitOps Repository → Argo CD → Kubernetes

OpenMetadata → Metadata / Lineage / Governance

Prometheus → Grafana
Loki       → Logs
Tempo      → Traces
OpenTelemetry → Telemetry
```

The application and data workloads run on a Kubernetes-based platform and are delivered through GitOps.

---

## Technology Stack

| Area              | Technologies                                    |
| ----------------- | ----------------------------------------------- |
| Backend           | Python, FastAPI, SQLAlchemy, Pydantic           |
| Database          | PostgreSQL                                      |
| Data Engineering  | Apache Airflow, dbt, SQL                        |
| ML / MLOps        | Python, MLflow, MinIO                           |
| Data Governance   | OpenMetadata                                    |
| Containers        | Docker                                          |
| Orchestration     | Kubernetes                                      |
| GitOps            | Argo CD                                         |
| CI/CD             | GitLab CI, GitLab Runner                        |
| Observability     | Prometheus, Grafana, Loki, Tempo, OpenTelemetry |
| Networking        | NGINX Ingress, Flannel, cert-manager            |
| Local AI Platform | Ollama, Qwen, CUDA GPU                          |
| Architecture      | PlantUML, ADRs                                  |
| Engineering Model | Documentation as Code, Governance as Code       |

---

## Real Estate Business Domain

The platform implements a real business workflow around property-search mandates.

Core concepts include:

```text
Client
  │
  ▼
Demande
  │
  ▼
Demande Version
  │
  ▼
Matching
  │
  ▼
Recommendation
  │
  ▼
Presentation
  │
  ▼
Visit
  │
  ▼
Transaction
  │
  ▼
Remuneration
```

The backend exposes business APIs for:

* authentication
* clients
* hunters
* mandates
* search requests
* properties
* recommendations
* presentations
* visits
* transactions
* remuneration

Business access is protected through authenticated application identities and role-based authorization.

---

## Versioned Search Requirements

Customer property requirements are versioned rather than overwritten.

```text
Demande
   │
   ├── Version 1
   ├── Version 2
   └── Version N
```

This preserves the history of changing requirements and provides traceability between a recommendation and the exact search criteria used to generate it.

Assignment history between requests and real-estate hunters is also maintained explicitly.

---

## Mandate Lifecycle

Real-estate mandates implement a contractual lifecycle with support for:

* initial periods
* renewals
* start/end dates
* mandate status
* historical legacy periods
* auditability

```text
MANDATE
   │
   ├── INITIAL PERIOD
   │
   ├── RENEWAL 1
   │
   ├── RENEWAL 2
   │
   └── ...
```

The operational model is propagated into the analytical warehouse while preserving the appropriate fact-table grain.

---

## Property Matching

The platform includes a deterministic property-matching engine.

Matching considers several business dimensions:

| Feature            | Weight |
| ------------------ | -----: |
| Location           |    30% |
| Budget             |    30% |
| Property type      |    10% |
| Surface            |    10% |
| Rooms              |     7% |
| Bedrooms           |     7% |
| Energy performance |     6% |

Budget eligibility is enforced as a hard business constraint before ranking.

The matching pipeline includes:

```text
Search Version
      │
      ▼
Candidate Retrieval
      │
      ▼
Eligibility Filters
      │
      ▼
Feature Scoring
      │
      ▼
Weighted Score
      │
      ▼
Ranking
      │
      ▼
Recommendations
```

Evaluation datasets and experiments are tracked through **MLflow**.

---

## Data Engineering

The platform follows a layered data architecture:

```text
Sources
   │
   ▼
RAW
   │
   ▼
STAGING
   │
   ▼
Operational / Warehouse Models
   │
   ▼
ANALYTICS
   │
   ├── Business KPIs
   ├── Data Analysis
   └── AI / ML
```

Responsibilities are intentionally separated:

```text
Airflow       → orchestration
dbt           → transformation
PostgreSQL    → persistence
OpenMetadata  → metadata and governance
MLflow        → ML experiment lifecycle
```

Database evolution is managed through controlled SQL migrations with validation in CI.

---

## MLOps

ML experimentation is integrated with the platform rather than maintained as an isolated notebook workflow.

```text
Dataset
   │
   ▼
Matching Evaluation
   │
   ▼
Metrics
   │
   ▼
MLflow Experiment
   │
   ▼
Model / Algorithm Comparison
   │
   ▼
Deployment Decision
```

MLflow provides experiment and metric tracking while MinIO provides artifact storage.

Evaluation workloads can also execute as Kubernetes Jobs.

---

## Kubernetes & GitOps

The project runs on a multi-node Kubernetes platform.

The infrastructure architecture includes:

* kubeadm-based Kubernetes
* multiple control-plane nodes
* multiple worker nodes
* Flannel CNI
* NGINX Ingress
* cert-manager
* Argo CD
* persistent storage
* monitoring stack

Application delivery follows GitOps principles:

```text
Developer
    │
    ▼
GitLab
    │
    ▼
CI Validation
    │
    ▼
Container Image
    │
    ▼
GitOps Repository
    │
    ▼
Argo CD
    │
    ▼
Kubernetes
```

Argo CD continuously reconciles the declared Git state with the Kubernetes runtime.

---

## Observability

Observability is integrated into both application and platform layers.

```text
Metrics ──────► Prometheus ──┐
                             │
Logs ─────────► Loki ────────┼──► Grafana
                             │
Traces ───────► Tempo ───────┘

Applications ─► OpenTelemetry
```

The backend exposes technical and business metrics, including recommendation activity, failures, processing duration, candidate volumes, and presentation creation.

Grafana dashboards provide operational visibility over the platform.

---

## Security

The application implements:

* password hashing
* JWT authentication
* role-based access control
* resource ownership controls
* application audit trails
* Kubernetes Secrets
* non-root container execution
* security validation through automated tests

Roles currently include:

```text
ADMIN
CHASSEUR
```

Authorization is enforced at both API and business-resource level.

---

## Data Governance

Governance is treated as an engineering capability rather than only documentation.

The project covers:

* metadata
* ownership
* classification
* lineage
* data quality
* reference data
* lifecycle
* security
* auditability

OpenMetadata provides the central metadata and governance platform.

The long-term principle is:

> **Evidence over declaration.**

Controls should progressively become machine-readable, version-controlled, validated through CI, and connected to runtime evidence.

---

## Testing & Quality

The project contains automated tests covering multiple layers:

```text
tests/
├── backend/
├── data/
├── ai/
└── ci/
```

The test strategy covers areas such as:

* API behavior
* business services
* RBAC
* audit
* mandate lifecycle
* transaction workflows
* remuneration
* recommendations
* matching
* data validation
* CI behavior

A recorded local validation of the repository reached:

```text
239 passed
```

Runtime and infrastructure validation are maintained separately from unit and integration testing.

---

## Repository Structure

```text
.
├── src/
│   ├── api/
│   └── ai/
│
├── database/
│   ├── migrations/
│   └── tests/
│
├── pipelines/
│   ├── airflow/
│   └── dbt/
│
├── governance/
├── observability/
├── deploy/
├── scripts/
├── tests/
├── docs/
└── evidence/
```

---

## Documentation

The project contains extensive architecture and engineering documentation under [`docs/`](docs/).

Key areas include:

```text
00-FOUNDATION
10-BUSINESS
20-APPLICATION
30-INFRASTRUCTURE
40-DATA
50-AI
60-SECURITY
70-DEVOPS
80-OPERATIONS
90-OBSERVABILITY
95-GOVERNANCE
98-ADR
99-DIAGRAMS
```

Start with:

* [Documentation Index](docs/README.md)
* [Application Architecture](docs/20-APPLICATION/01-Application-Architecture.md)
* [Implemented Data Architecture](docs/40-DATA/ARCHITECTURE-DATA-IMPLEMENTEE.md)
* [Matching Baseline](docs/50-AI/11-Matching-Baseline-Implementation.md)
* [Security / RBAC / Audit](docs/60-SECURITY/SECURITY-RBAC-AUDIT-IMPLEMENTATION-EVIDENCE.md)
* [Repository & CI Map](docs/70-DEVOPS/REPOSITORY-AND-CI-MAP.md)
* [Architecture Diagrams](docs/99-DIAGRAMS/)

Architecture diagrams are maintained as **PlantUML source files** and rendered to SVG.

---

## Engineering Principles

The project follows several cross-cutting principles:

```text
Git as Source of Truth
Documentation as Code
Architecture as Code
Infrastructure as Code
GitOps
Security by Design
Observability by Design
Data Governance by Design
AI Governance by Design
Governance as Code
Recovery by Design
Evidence over Declaration
```

---

## Current Scope

Implemented capabilities include the FastAPI backend, PostgreSQL data model and migrations, business workflows, authentication and RBAC, deterministic matching, MLflow evaluation tooling, data pipelines, warehouse components, automated testing, Kubernetes deployment configuration, GitOps delivery, and observability integration.

Some architecture documents also describe the platform's **target state**.

Capabilities such as enterprise OIDC/Keycloak integration, Vault-based secret management, React UI, semantic search, RAG and LLM-powered business functionality should therefore be interpreted as planned architecture unless supported by implementation and runtime evidence.

---

## About this Project

This project was developed as part of my professional transition toward **Data Engineering, MLOps and AI Platform Engineering**.

It combines my previous experience with systems and infrastructure with my current Data & AI specialization, with a particular focus on building systems that are:

**reproducible · automated · observable · governed · secure · traceable**
