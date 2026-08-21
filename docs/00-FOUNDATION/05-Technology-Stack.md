# Technology Stack

**Version:** 2.0  
**Status:** Active  
**Project:** Real Estate Intelligence Platform  
**Platform:** Enterprise AI Platform  
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the technology landscape of the Enterprise AI Platform.

It describes:

- technologies currently adopted,
- technologies targeted for future implementation,
- technologies under evaluation,
- technologies reserved for future requirements,
- the role of each technology,
- major dependencies between platform components.

Architecture decisions and their rationale remain authoritative in:

```text
04-Architecture-Decisions.md
98-ADR/
```

This document describes the technology portfolio.

---

# 2. Technology Lifecycle

Every technology belongs to one of four lifecycle states.

| Status | Meaning |
|---|---|
| **ADOPTED** | Selected and part of the current architecture baseline |
| **TARGET** | Selected architectural direction but not yet fully implemented |
| **CANDIDATE** | Under evaluation; no final commitment |
| **FUTURE** | Introduced only when future requirements justify it |

The architecture must distinguish:

```text
ADOPTED != TARGET != CANDIDATE != FUTURE
```

---

# 3. Selection Criteria

Technologies are evaluated according to:

- Business requirements
- Functional suitability
- Enterprise adoption
- Open-source availability
- Community support
- Documentation quality
- Security
- Maintainability
- Automation capability
- Cloud-native compatibility
- Kubernetes compatibility
- Observability
- Data sovereignty
- Operational complexity
- Infrastructure footprint
- Integration capability
- Portability
- Recoverability
- Governance capability
- Total operational cost

The project favors the simplest technology that satisfies the actual requirement.

```text
Requirement
    |
    v
Evaluate
    |
    v
Select
    |
    v
ADR
    |
    v
Implement
    |
    v
Validate
```

---

# 4. Technology Portfolio

| Domain | Technology | Status | Primary Purpose |
|---|---|---|---|
| Virtualization | Proxmox VE | ADOPTED | VM infrastructure |
| Containers | Docker | ADOPTED | Container packaging |
| Orchestration | Kubernetes | ADOPTED | Container orchestration |
| Kubernetes Bootstrap | kubeadm | ADOPTED | Cluster lifecycle |
| CNI | Flannel | ADOPTED | Pod networking |
| DNS | CoreDNS | ADOPTED | Kubernetes service discovery |
| Ingress | NGINX Ingress | ADOPTED | HTTP/S ingress |
| TLS | cert-manager | ADOPTED | Certificate automation |
| Package Management | Helm | ADOPTED | Kubernetes packaging |
| Source Control | GitLab | ADOPTED | Git repositories |
| CI/CD | GitLab CI / Runner | ADOPTED | Build and validation |
| GitOps | Argo CD | ADOPTED | Kubernetes reconciliation |
| API | FastAPI | ADOPTED | Python APIs |
| Language | Python | ADOPTED | Data, AI and API development |
| Frontend | React | TARGET | Web interface |
| Database | PostgreSQL | ADOPTED | Relational persistence |
| Cache | Redis | TARGET | Cache / transient state |
| Data Transformation | dbt | ADOPTED | Analytical transformations |
| Workflow | Apache Airflow | ADOPTED | Data/ML orchestration |
| Metadata | OpenMetadata | ADOPTED | Catalog and governance |
| Object Storage | MinIO | ADOPTED | S3-compatible artifacts |
| ML Lifecycle | MLflow | ADOPTED | Experiments and model registry |
| AI Runtime | Ollama | ADOPTED | Local LLM inference |
| LLM | Qwen | ADOPTED | Local language model |
| RAG | RAG Architecture | TARGET | Governed knowledge retrieval |
| Vector Storage | PostgreSQL + pgvector | CANDIDATE | Vector search |
| Vector Database | Qdrant | CANDIDATE | Dedicated vector search |
| Identity | Keycloak | TARGET | Enterprise IAM |
| Secrets | Kubernetes Secrets | ADOPTED | Current secret mechanism |
| Enterprise Secrets | HashiCorp Vault | TARGET | Central secret management |
| Metrics | Prometheus | ADOPTED | Metrics |
| Dashboards | Grafana | ADOPTED | Visualization |
| Logs | Loki | ADOPTED | Central logs |
| Traces | Tempo | ADOPTED | Distributed tracing |
| Telemetry | OpenTelemetry | ADOPTED | Telemetry standard |
| Alerting | Alertmanager | ADOPTED | Alert routing |
| Backup | Velero | ADOPTED | Kubernetes backup |
| Documentation | Markdown | ADOPTED | Documentation as Code |
| Diagrams | PlantUML | ADOPTED | Diagrams as Code |
| Governance | OpenMetadata + Git | ADOPTED | Governance as Code |
| Event Streaming | Kafka | FUTURE | Event streaming |

---

# 5. Infrastructure

## Proxmox VE

**Status:** ADOPTED

Provides the virtualization layer supporting the platform infrastructure.

Responsibilities include:

- VM hosting
- Compute allocation
- Virtual networking
- Infrastructure isolation
- Resource management

Kubernetes nodes operate above this infrastructure layer.

---

## Docker

**Status:** ADOPTED

Docker is used for:

- Application packaging
- Local development
- CI builds
- Reproducible runtimes
- Container image creation

Docker packages workloads.

Kubernetes orchestrates them.

---

## Kubernetes

**Status:** ADOPTED

Kubernetes is the principal workload orchestration platform.

Current architecture:

```text
Control Plane
├── k8s-cp-01
├── k8s-cp-02
└── k8s-cp-03

Workers
├── k8s-wk-01
├── k8s-wk-02
├── k8s-wk-03
├── k8s-wk-04
├── k8s-wk-05
└── k8s-wk-06
```

Primary capabilities:

- Scheduling
- Self-healing
- Service discovery
- Configuration
- Secret injection
- Horizontal scaling
- Declarative deployment
- Platform standardization

Detailed decision:

```text
ADR-0001-Kubernetes.md
```

---

## kubeadm

**Status:** ADOPTED

kubeadm provides the current Kubernetes cluster bootstrap and lifecycle model.

The architecture deliberately uses a self-managed Kubernetes environment rather than a managed cloud Kubernetes service.

---

## Flannel

**Status:** ADOPTED

Flannel provides Kubernetes pod networking.

Detailed decision:

```text
ADR-0003-Flannel-CNI.md
```

---

## Helm

**Status:** ADOPTED

Helm provides Kubernetes application packaging and configurable deployment.

It is used for platform components where appropriate.

Helm configuration should remain version controlled.

---

# 6. Networking

## CoreDNS

**Status:** ADOPTED

CoreDNS provides Kubernetes internal DNS and service discovery.

---

## NGINX Ingress

**Status:** ADOPTED

NGINX Ingress provides controlled HTTP/S access to Kubernetes services.

```text
Client
   |
   v
DNS
   |
   v
NGINX Ingress
   |
   v
Kubernetes Service
   |
   v
Pod
```

Detailed decision:

```text
ADR-0004-NGINX-Ingress.md
```

---

## cert-manager

**Status:** ADOPTED

cert-manager automates Kubernetes certificate lifecycle management.

It supports:

- Certificate requests
- TLS secrets
- Renewal
- Ingress TLS integration

---

## Network Policies

**Status:** TARGET

Network policies are part of the target security architecture.

Their effectiveness depends on CNI enforcement capabilities and must therefore be validated against the implemented network architecture.

---

# 7. Source Control and CI/CD

## GitLab

**Status:** ADOPTED

GitLab provides:

- Git repositories
- Merge requests
- CI/CD
- Source history
- Governance traceability

Git is the source of truth for code and progressively for infrastructure, architecture and governance artifacts.

---

## GitLab CI

**Status:** ADOPTED

GitLab CI provides automated:

- Validation
- Testing
- Builds
- Security checks
- Artifact generation
- Deployment preparation

Detailed decision:

```text
ADR-0012-GitLab-CI-CD.md
```

---

## Argo CD

**Status:** ADOPTED

Argo CD provides GitOps reconciliation.

```text
Git
 |
 v
Argo CD
 |
 v
Kubernetes
```

Capabilities include:

- Synchronization
- Drift detection
- Self-healing
- Declarative deployment
- Rollback through Git

Detailed decision:

```text
ADR-0002-ArgoCD-GitOps.md
```

---

# 8. Application Platform

## Python

**Status:** ADOPTED

Python is the principal language for:

- Data engineering
- AI
- ML
- Automation
- APIs
- Platform integration

---

## FastAPI

**Status:** ADOPTED

FastAPI is the preferred Python API framework.

It provides:

- Type validation
- OpenAPI
- Async support
- High-performance APIs
- Strong Python integration

---

## Pydantic

**Status:** ADOPTED WITH FASTAPI WORKLOADS

Used for:

- Schema validation
- API models
- Configuration validation

---

## SQLAlchemy

**Status:** ADOPTED WHERE REQUIRED

Provides Python relational database abstraction.

---

## Alembic

**Status:** ADOPTED WHERE REQUIRED

Provides database schema migration management for SQLAlchemy-based applications.

---

# 9. Frontend

## React

**Status:** TARGET

React is the preferred frontend framework where a dedicated web UI is required.

It is not a mandatory dependency of the infrastructure platform.

---

## TypeScript

**Status:** TARGET

Preferred language for future React application development.

---

# 10. Data Platform

## PostgreSQL

**Status:** ADOPTED

PostgreSQL is the primary relational data platform.

Responsibilities include:

- OLTP
- Analytical storage
- Warehouse structures
- Application persistence
- Data platform persistence

Detailed decision:

```text
ADR-0005-PostgreSQL.md
```

---

## dbt

**Status:** ADOPTED

dbt provides analytical transformation.

Target architecture:

```text
RAW
 |
 v
STAGING
 |
 v
WAREHOUSE
 |
 v
ANALYTICS
```

Responsibility:

```text
Airflow = orchestration
dbt     = transformation
```

---

## Apache Airflow

**Status:** ADOPTED

Airflow orchestrates:

- ETL
- ELT
- Data Quality
- ML workflows
- Scheduled automation

Detailed decision:

```text
ADR-0006-Airflow.md
```

---

## OpenMetadata

**Status:** ADOPTED

OpenMetadata provides:

- Catalog
- Ownership
- Glossary
- Classification
- Lineage
- Profiling
- Data Quality metadata
- Governance

Detailed decision:

```text
ADR-0008-OpenMetadata.md
```

---

## Redis

**Status:** TARGET

Redis may support:

- Cache
- Session state
- Temporary data
- High-speed lookup

It should only be introduced where justified by an application requirement.

---

## Kafka

**Status:** FUTURE

Kafka is not part of the current mandatory platform.

It may be evaluated when requirements demand:

- Event streaming
- Durable event logs
- Multiple consumers
- Real-time pipelines
- High-throughput asynchronous integration

No requirement means no Kafka dependency.

---

# 11. Object Storage

## MinIO

**Status:** ADOPTED

MinIO provides S3-compatible object storage.

Current architectural use includes MLflow artifacts.

```text
MLflow
   |
   +---- Metadata ----> Database
   |
   └---- Artifacts ---> MinIO
```

---

# 12. AI and MLOps

## MLflow

**Status:** ADOPTED

MLflow provides:

- Experiment tracking
- Parameters
- Metrics
- Artifacts
- Model versions
- Model registry

Detailed decision:

```text
ADR-0007-MLflow.md
```

---

## Ollama

**Status:** ADOPTED

Ollama provides local LLM inference.

Benefits include:

- Local execution
- Data sovereignty
- GPU acceleration
- API access
- Reduced external dependency

Detailed decision:

```text
ADR-0009-Ollama-Local-AI.md
```

---

## Qwen

**Status:** ADOPTED

Qwen is the current local LLM family.

The current inference model is:

```text
Application
     |
     v
AI Service
     |
     v
Ollama
     |
     v
Qwen
     |
     v
Local GPU
```

---

# 13. RAG

**Status:** TARGET

Retrieval-Augmented Generation is part of the target AI platform.

```text
Governed Documents
       |
       v
Ingestion
       |
       v
Chunking
       |
       v
Embeddings
       |
       v
Vector Search
       |
       v
Context
       |
       v
Local LLM
```

RAG data remains subject to:

- Ownership
- Classification
- Security
- Data Quality
- Lineage
- AI governance

---

# 14. Vector Storage

No dedicated vector database has yet been adopted.

## PostgreSQL + pgvector

**Status:** CANDIDATE

Advantages:

- Reuses PostgreSQL
- Lower operational complexity
- Unified backup
- SQL integration
- Existing governance model

---

## Qdrant

**Status:** CANDIDATE

Potential advantages:

- Dedicated vector engine
- Semantic retrieval
- Metadata filtering
- Vector-search specialization

Qdrant should only be adopted if requirements justify operating a separate vector database.

A dedicated ADR is required before final adoption.

---

# 15. Security

## Kubernetes Secrets

**Status:** ADOPTED

Current Kubernetes-native mechanism for workload secrets.

Sensitive values must not be stored in Git in plaintext.

---

## GitLab Protected Variables

**Status:** ADOPTED

Used for CI/CD secret injection where appropriate.

---

## Keycloak

**Status:** TARGET

Target enterprise identity provider.

Potential capabilities:

- OAuth 2.0
- OpenID Connect
- SSO
- Identity federation
- Central authentication

Keycloak is not currently documented as a fully implemented platform dependency.

---

## HashiCorp Vault

**Status:** TARGET

Target enterprise secrets-management capability.

Potential capabilities:

- Central secret storage
- Dynamic credentials
- PKI
- Rotation
- Kubernetes authentication
- Short-lived credentials

Current:

```text
Kubernetes Secrets
+
GitLab Protected Variables
```

Target:

```text
Central Secrets Management
        |
        v
HashiCorp Vault
```

---

# 16. Observability

## Prometheus

**Status:** ADOPTED

Primary metrics platform.

Detailed decision:

```text
ADR-0010-Prometheus-Grafana.md
```

---

## Grafana

**Status:** ADOPTED

Primary visualization and dashboard platform.

---

## Loki

**Status:** ADOPTED

Primary centralized logging platform.

---

## Tempo

**Status:** ADOPTED

Primary distributed tracing backend.

---

## OpenTelemetry

**Status:** ADOPTED

Standard telemetry architecture.

---

## Alertmanager

**Status:** ADOPTED

Provides alert routing and notification handling for Prometheus-based monitoring.

The combined observability architecture is:

```text
Metrics ----> Prometheus ---+
                            |
Logs ------> Loki ----------+----> Grafana
                            |
Traces ----> Tempo ---------+
             ^
             |
       OpenTelemetry

Prometheus
    |
    v
Alertmanager
```

Detailed decision:

```text
ADR-0011-Loki-Tempo-OpenTelemetry.md
```

---

# 17. Storage

Kubernetes storage architecture uses:

- PersistentVolume
- PersistentVolumeClaim
- StorageClass

Storage requirements depend on workload characteristics.

Persistent state must have:

- Ownership
- Capacity planning
- Backup strategy
- Restore procedure
- Recovery validation

---

# 18. Backup

## Velero

**Status:** ADOPTED

Velero supports Kubernetes backup and recovery.

Backup success alone is insufficient.

```text
Backup
 |
 v
Restore
 |
 v
Validate
 |
 v
Evidence
```

---

# 19. Documentation and Architecture Tooling

## Markdown

**Status:** ADOPTED

Documentation source format.

---

## PlantUML

**Status:** ADOPTED

Architecture diagram source format.

```text
*.puml
   |
   v
PlantUML
   |
   v
*.svg
```

PlantUML source files are authoritative.

Rendered SVG files are generated artifacts.

---

## ADR

**Status:** ADOPTED

Architecture Decision Records capture important architectural decisions and their rationale.

---

# 20. Governance as Code

**Status:** ADOPTED

Governance artifacts should progressively become machine-readable and version controlled.

Technologies supporting this model include:

```text
GitLab
   |
   v
Git
   |
   v
CI Validation
   |
   +----------------+
   |                |
   v                v
Argo CD        OpenMetadata
   |                |
   v                v
Runtime        Governance State
   |
   v
Evidence
```

Detailed decision:

```text
ADR-0014-Governance-as-Code.md
```

---

# 21. Future Technologies

The following technologies are not current platform dependencies.

They may be evaluated when justified by requirements.

| Technology | Potential Purpose |
|---|---|
| Kafka | Event streaming |
| KEDA | Event-driven autoscaling |
| Service Mesh | Advanced service networking |
| Argo Events | Event automation |
| Argo Workflows | Kubernetes-native workflows |
| Feature Store | Managed ML features |
| AI Gateway | AI traffic governance |
| Crossplane | Infrastructure control plane |
| Backstage | Developer portal |
| Harbor | Dedicated container registry |
| OPA / Gatekeeper | Policy enforcement |
| Multi-cluster Kubernetes | Multi-cluster platform |

These technologies must not be considered adopted merely because they appear in the roadmap.

---

# 22. Technology Dependency Model

```text
                    Applications
                         |
             +-----------+-----------+
             |                       |
             v                       v
          FastAPI                 React
             |
       +-----+------+------------------+
       |            |                  |
       v            v                  v
 PostgreSQL      Data Platform      AI Platform
                    |                  |
              +-----+-----+      +-----+------+
              |           |      |            |
              v           v      v            v
           Airflow       dbt   MLflow       Ollama
              |           |      |            |
              +-----+-----+      |            v
                    |            |           Qwen
                    v            |
               OpenMetadata      v
                              MinIO

-------------------------------------------------

                Kubernetes Platform
                       |
       +---------------+---------------+
       |               |               |
       v               v               v
    Argo CD        NGINX Ingress   Observability
                                       |
                              +--------+--------+
                              |        |        |
                              v        v        v
                         Prometheus   Loki    Tempo
                              |
                              v
                         Alertmanager

-------------------------------------------------

                 Infrastructure
                       |
                       v
                   Proxmox VE
```

---

# 23. Technology Ownership

Technology ownership is defined by capability rather than by product alone.

| Capability | Primary Responsibility |
|---|---|
| Infrastructure | Platform / Infrastructure Engineering |
| Kubernetes | Platform Engineering |
| CI/CD | DevOps / Platform Engineering |
| GitOps | Platform Engineering |
| Applications | Application Engineering |
| Data | Data Engineering |
| Metadata | Data Governance |
| MLflow | MLOps |
| Local AI | AI / MLOps |
| Security | Security + Platform |
| Observability | Platform / SRE |
| Governance as Code | Architecture + Governance + Engineering |

In the project context, several responsibilities may be performed by the same person, but the architectural responsibilities remain conceptually separated.

---

# 24. Technology Lifecycle Governance

Technology lifecycle follows:

```text
Requirement
    |
    v
Candidate
    |
    v
Evaluation
    |
    v
Architecture Decision
    |
    v
ADR
    |
    v
Target
    |
    v
Implementation
    |
    v
Validation
    |
    v
Adopted
    |
    v
Operational Evidence
```

Technology can later transition to:

```text
Deprecated
    |
    v
Retired
```

Lifecycle changes should update:

- Technology Stack
- Architecture Decisions
- ADRs
- Diagrams
- Operational documentation
- Governance records

where applicable.

---

# 25. Current Technology Baseline

## ADOPTED

```text
Proxmox VE
Docker
Kubernetes
kubeadm
Flannel
CoreDNS
NGINX Ingress
cert-manager
Helm
GitLab
GitLab CI
Argo CD
GitOps
Python
FastAPI
PostgreSQL
dbt
Apache Airflow
OpenMetadata
MinIO
MLflow
Ollama
Qwen
Kubernetes Secrets
Prometheus
Grafana
Loki
Tempo
OpenTelemetry
Alertmanager
Velero
Markdown
PlantUML
ADR
Governance as Code
```

## TARGET

```text
React
TypeScript
Redis
RAG
Keycloak
HashiCorp Vault
Network Policy enforcement
```

## CANDIDATE

```text
PostgreSQL + pgvector
Qdrant
```

## FUTURE

```text
Kafka
KEDA
Service Mesh
Argo Events
Argo Workflows
Feature Store
AI Gateway
Crossplane
Backstage
Harbor
OPA / Gatekeeper
Multi-cluster Kubernetes
```

---

# 26. Architectural Principle

The platform does not seek to maximize the number of technologies.

The objective is:

```text
Minimum Necessary Complexity
          +
Clear Responsibilities
          +
Automation
          +
Observability
          +
Security
          +
Governance
          +
Recoverability
```

A new technology must solve a demonstrated requirement.

```text
Technology
without
Requirement
    =
Operational Complexity
```

---

# 27. Related Documentation

```text
04-Architecture-Decisions.md

../30-INFRASTRUCTURE/
../40-DATA/
../50-AI/
../60-SECURITY/
../70-DEVOPS/
../80-OPERATIONS/
../90-OBSERVABILITY/
../95-GOVERNANCE/
../98-ADR/
../99-DIAGRAMS/
```

---

**Technology Portfolio Status: ACTIVE**