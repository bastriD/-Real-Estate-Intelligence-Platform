# Architecture Decisions

**Version:** 2.0  
**Status:** Active  
**Owner:** Bastri Murad  
**Project:** Real Estate Intelligence Platform  
**Platform:** Enterprise AI Platform  
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document provides the consolidated view of the major architectural decisions that define the Enterprise AI Platform.

It complements the individual Architecture Decision Records stored in:

```text
98-ADR/
```

The responsibilities are deliberately separated:

```text
Architecture-Decisions.md
        =
Consolidated architecture decision baseline

ADR
        =
Detailed rationale, alternatives and consequences
```

This document must distinguish technologies that are currently adopted from technologies that are only planned, being evaluated or reserved for future requirements.

---

# 2. Decision Status Model

Every architectural technology decision uses one of the following statuses.

| Status | Meaning |
|---|---|
| **ADOPTED** | Selected and part of the current architecture baseline |
| **TARGET** | Selected architectural direction but not yet fully implemented |
| **CANDIDATE** | Technology being evaluated; no final architecture commitment |
| **FUTURE** | Capability or technology considered only when requirements justify it |

The distinction is important.

```text
Documented
    !=
Implemented

Candidate
    !=
Selected

Future
    !=
Current Architecture
```

Architecture documentation must not present target or candidate technologies as already implemented.

---

# 3. Decision Summary

| Domain | Technology / Approach | Status |
|---|---|---|
| Virtualization | Proxmox VE | ADOPTED |
| Container Orchestration | Kubernetes | ADOPTED |
| Kubernetes Deployment | kubeadm | ADOPTED |
| Kubernetes CNI | Flannel | ADOPTED |
| Ingress | NGINX Ingress | ADOPTED |
| TLS Automation | cert-manager | ADOPTED |
| Source Control | GitLab | ADOPTED |
| CI/CD | GitLab CI / GitLab Runner | ADOPTED |
| Continuous Delivery | Argo CD | ADOPTED |
| Deployment Model | GitOps | ADOPTED |
| API | FastAPI | ADOPTED |
| Frontend | React | TARGET |
| Relational Database | PostgreSQL | ADOPTED |
| Cache | Redis | TARGET |
| Event Streaming | Kafka | FUTURE |
| Workflow Orchestration | Apache Airflow | ADOPTED |
| Data Transformation | dbt | ADOPTED |
| Metadata / Governance | OpenMetadata | ADOPTED |
| ML Lifecycle | MLflow | ADOPTED |
| Object Storage | MinIO | ADOPTED |
| Local AI Runtime | Ollama | ADOPTED |
| Local LLM | Qwen | ADOPTED |
| Vector Storage | PostgreSQL / pgvector | CANDIDATE |
| Dedicated Vector Database | Qdrant | CANDIDATE |
| Identity Provider | Keycloak | TARGET |
| Enterprise Secrets Management | HashiCorp Vault | TARGET |
| Current Kubernetes Secrets | Kubernetes Secrets | ADOPTED |
| Monitoring | Prometheus | ADOPTED |
| Dashboards | Grafana | ADOPTED |
| Logging | Loki | ADOPTED |
| Tracing | Tempo | ADOPTED |
| Telemetry | OpenTelemetry | ADOPTED |
| Kubernetes Backup | Velero | ADOPTED |
| Architecture Diagrams | PlantUML | ADOPTED |
| Architecture Governance | ADR | ADOPTED |
| Governance Model | Governance as Code | ADOPTED |

---

# 4. Platform Decisions

## Kubernetes

**Status:** ADOPTED

### Decision

Use Kubernetes as the primary container orchestration platform.

### Rationale

- Declarative workload management
- Self-healing
- Horizontal scaling
- Service discovery
- Cloud-native ecosystem
- GitOps compatibility
- Platform standardization

The current cluster architecture uses kubeadm with multiple control-plane and worker nodes.

Detailed decision:

```text
ADR-0001 — Kubernetes
```

---

## GitOps

**Status:** ADOPTED

### Decision

Use GitOps as the standard deployment and desired-state management model for Kubernetes.

### Rationale

- Declarative configuration
- Version control
- Auditability
- Reproducibility
- Drift detection
- Automatic reconciliation
- Rollback capability

The principal model is:

```text
Git
 |
 v
Argo CD
 |
 v
Kubernetes
 |
 v
Runtime State
```

Detailed decision:

```text
ADR-0002 — Argo CD / GitOps
```

---

## Infrastructure as Code

**Status:** ADOPTED AS AN ARCHITECTURAL PRINCIPLE

Infrastructure and platform configuration should progressively be represented as code.

Examples include:

- Terraform
- Ansible
- Kubernetes manifests
- Helm values
- GitLab CI pipelines
- GitOps definitions
- Configuration files

The target principle is:

```text
Infrastructure Change
        |
        v
Code
        |
        v
Git
        |
        v
Review
        |
        v
Automation
        |
        v
Infrastructure
```

Manual changes must not become undocumented permanent state.

---

## Argo CD

**Status:** ADOPTED

Argo CD is the standard Kubernetes GitOps reconciliation platform.

It is responsible for:

- Desired-state reconciliation
- Drift detection
- Automated synchronization
- Application deployment
- Git-based rollback

---

# 5. Application Decisions

## FastAPI

**Status:** ADOPTED

FastAPI is the preferred Python API framework for platform and AI-facing services.

### Rationale

- Python ecosystem
- Strong AI/data integration
- OpenAPI generation
- Type validation
- Asynchronous support
- Container-friendly runtime

FastAPI does not imply that every future service must be implemented in Python.

---

## React

**Status:** TARGET

React is the preferred frontend technology where a dedicated web application is required.

### Rationale

- Component-based architecture
- Mature ecosystem
- API integration
- Enterprise adoption

React is part of the target application architecture but must not be described as a universal dependency of the platform.

---

## Redis

**Status:** TARGET

Redis may provide:

- Distributed caching
- Temporary state
- Session storage
- High-speed key/value access

Redis should be introduced where a concrete application requirement justifies it.

It is not a mandatory dependency for every service.

---

# 6. Data Decisions

## PostgreSQL

**Status:** ADOPTED

PostgreSQL is the primary relational data platform.

### Rationale

- ACID compliance
- Mature ecosystem
- Strong SQL capabilities
- Reliability
- Analytics support
- Extension ecosystem
- Compatibility with data and AI workloads

Detailed decision:

```text
ADR-0005 — PostgreSQL
```

---

## Apache Airflow

**Status:** ADOPTED

Apache Airflow is the standard workflow orchestration platform for data and ML workflows.

Airflow owns:

```text
WHEN
and
IN WHAT ORDER
```

workflows execute.

It does not replace dbt, MLflow or OpenMetadata.

Detailed decision:

```text
ADR-0006 — Airflow
```

---

## dbt

**Status:** ADOPTED

dbt is responsible for SQL-based transformation and analytical modeling.

The responsibility separation is:

```text
Airflow      = orchestration
dbt          = transformation
PostgreSQL   = persistence
OpenMetadata = metadata / governance
```

---

## OpenMetadata

**Status:** ADOPTED

OpenMetadata is the standard metadata and data-governance platform.

It provides:

- Data catalog
- Ownership
- Classification
- Glossary
- Lineage
- Profiling
- Data Quality visibility
- Governance metadata

Detailed decision:

```text
ADR-0008 — OpenMetadata
```

---

## Kafka

**Status:** FUTURE

Kafka is **not part of the current mandatory platform architecture**.

Kafka may be introduced if future requirements require:

- High-volume event streaming
- Durable event logs
- Event-driven integration
- Multiple independent consumers
- Streaming analytics
- Real-time data pipelines

The architectural rule is:

```text
No Event-Streaming Requirement
            |
            v
       No Kafka
```

Kafka must not be introduced merely because it is common in enterprise data architectures.

A dedicated ADR must be created before Kafka becomes an adopted platform component.

---

# 7. AI and ML Decisions

## MLflow

**Status:** ADOPTED

MLflow is the standard ML lifecycle platform.

It provides:

- Experiment tracking
- Runs
- Parameters
- Metrics
- Artifacts
- Model versions
- Model registry

Detailed decision:

```text
ADR-0007 — MLflow
```

---

## Ollama

**Status:** ADOPTED

Ollama is the standard local AI inference runtime for the current architecture.

### Rationale

- Local execution
- Data sovereignty
- Simple model lifecycle
- GPU support
- API access
- Reduced external dependency

Detailed decision:

```text
ADR-0009 — Ollama Local AI
```

---

## Qwen

**Status:** ADOPTED

Qwen is the current local LLM family used by the platform.

The architecture separates:

```text
Application
     |
     v
Internal AI Interface
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

The model itself may evolve without requiring the entire application architecture to change.

---

## RAG

**Status:** TARGET

Retrieval-Augmented Generation is part of the target AI architecture.

The intended flow is:

```text
Enterprise Knowledge
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
Vector Retrieval
        |
        v
Relevant Context
        |
        v
Local LLM
```

RAG sources must remain subject to:

- Ownership
- Classification
- Data Quality
- Access control
- Lineage
- AI governance

---

## Vector Storage

**Status:** CANDIDATE

A final dedicated vector-storage technology has **not yet been adopted**.

The architecture should evaluate the simplest solution satisfying the actual requirements.

Initial candidates include:

```text
PostgreSQL + pgvector
```

and, if dedicated vector-database capabilities are justified:

```text
Qdrant
```

Evaluation criteria include:

- Dataset size
- Query latency
- Vector volume
- Filtering requirements
- Operational complexity
- Backup requirements
- Kubernetes footprint
- Existing PostgreSQL capabilities

The architectural principle is:

```text
Prefer existing governed infrastructure
            |
            v
Introduce specialized infrastructure
only when requirements justify it
```

---

## Qdrant

**Status:** CANDIDATE

Qdrant is **not currently an adopted platform dependency**.

It remains a candidate for dedicated vector-search workloads.

Potential capabilities include:

- Semantic search
- Vector similarity
- Metadata filtering
- RAG retrieval

Before adoption, Qdrant must be compared against PostgreSQL/pgvector and documented through an ADR.

---

# 8. Security Decisions

## Identity and Access Management

Identity architecture must support:

- Authentication
- Authorization
- RBAC
- Service identities
- Human identities
- Auditability
- Least privilege

The current architecture does not claim that enterprise IAM is fully implemented.

---

## Keycloak

**Status:** TARGET

Keycloak is the target enterprise identity provider.

Potential responsibilities include:

- Identity management
- OAuth 2.0
- OpenID Connect
- SSO
- Central authentication
- Federation
- Application identity integration

Keycloak must therefore be described as:

```text
TARGET ARCHITECTURE
```

not:

```text
CURRENT IMPLEMENTED PLATFORM
```

A dedicated ADR should be created when the implementation decision is finalized.

---

## Secrets Management

The current platform uses Kubernetes-native and CI/CD secret mechanisms where appropriate.

Current mechanisms include:

- Kubernetes Secrets
- Protected GitLab CI variables
- Application-specific secret injection

Secrets must never be committed to Git in plaintext.

---

## HashiCorp Vault

**Status:** TARGET

HashiCorp Vault is the target enterprise secrets-management capability.

Potential responsibilities include:

- Central secret management
- Dynamic credentials
- PKI integration
- Secret rotation
- Kubernetes authentication
- Short-lived credentials

Vault is not currently considered a fully implemented mandatory platform dependency.

The migration model is:

```text
Current
Kubernetes Secrets
Protected CI Variables

        |
        v

Target
Enterprise Secrets Management
        |
        v
HashiCorp Vault
```

A dedicated ADR should accompany final adoption and implementation.

---

# 9. Object Storage

## MinIO

**Status:** ADOPTED

MinIO provides S3-compatible object storage for platform workloads where required.

Current use includes MLflow artifact storage.

The separation is:

```text
MLflow
   |
   +---- Metadata ----> Database
   |
   +---- Artifacts ----> MinIO
```

---

# 10. Observability Decisions

The platform uses a unified observability architecture.

## Prometheus

**Status:** ADOPTED

Primary metrics platform.

---

## Grafana

**Status:** ADOPTED

Primary visualization and dashboard platform.

---

## Loki

**Status:** ADOPTED

Primary centralized log platform.

---

## Tempo

**Status:** ADOPTED

Primary distributed tracing backend.

---

## OpenTelemetry

**Status:** ADOPTED

Standard telemetry instrumentation and collection architecture.

The combined model is:

```text
Metrics ----> Prometheus ---+
                            |
Logs ------> Loki ----------+----> Grafana
                            |
Traces ----> Tempo ---------+
       ^
       |
OpenTelemetry
```

Detailed decisions:

```text
ADR-0010 — Prometheus / Grafana
ADR-0011 — Loki / Tempo / OpenTelemetry
```

---

# 11. Backup and Recovery

## Velero

**Status:** ADOPTED

Velero is part of the Kubernetes backup and recovery architecture.

Backup is not considered equivalent to recovery.

The operational model is:

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
Measure
   |
   v
Evidence
```

Recovery capabilities must be tested.

---

# 12. Documentation Decisions

## Documentation as Code

**Status:** ADOPTED

Documentation is maintained in Git using Markdown.

Documentation changes are:

- Version controlled
- Reviewable
- Traceable
- Evolvable

---

## Diagrams as Code

**Status:** ADOPTED

PlantUML is the authoritative architecture diagram source format.

```text
*.puml
   |
   v
PlantUML
   |
   v
*.svg
```

SVG files are generated artifacts.

Draw.io is not the authoritative architecture diagram format for this documentation baseline.

---

## Architecture Decision Records

**Status:** ADOPTED

Important architecture decisions must be documented through ADRs.

The ADR repository is:

```text
98-ADR/
```

---

# 13. Governance Decisions

## Governance as Code

**Status:** ADOPTED

Governance artifacts should progressively become:

- Version controlled
- Machine readable
- Validatable
- Automatable
- Observable
- Auditable

The target lifecycle is:

```text
Requirement
    |
    v
Control
    |
    v
Policy
    |
    v
Machine-Readable Definition
    |
    v
Git
    |
    v
CI Validation
    |
    v
Runtime Enforcement
    |
    v
Evidence
```

Detailed decision:

```text
ADR-0014 — Governance as Code
```

---

# 14. Local-First AI Decision

**Status:** ADOPTED

Enterprise AI workloads should use local inference by default where technically appropriate.

The default model is:

```text
Enterprise Data
      |
      v
Internal AI Service
      |
      v
Local Inference
      |
      v
Ollama / Qwen
```

External AI providers are governed exceptions.

External use requires evaluation of:

- Data classification
- Security
- Privacy
- Regulatory requirements
- Cost
- Architecture
- Business justification

---

# 15. Current vs Target Architecture

The architecture deliberately distinguishes current and future state.

## Current / Adopted

```text
Proxmox
Kubernetes
kubeadm
Flannel
NGINX Ingress
cert-manager
GitLab
GitLab CI
Argo CD
PostgreSQL
Airflow
dbt
OpenMetadata
MLflow
MinIO
Ollama
Qwen
Prometheus
Grafana
Loki
Tempo
OpenTelemetry
Velero
PlantUML
ADR
Governance as Code
```

## Target

```text
React
Redis
Keycloak
HashiCorp Vault
RAG
```

## Candidate

```text
PostgreSQL + pgvector
Qdrant
```

## Future / Requirement Driven

```text
Kafka
Service Mesh
KEDA
Argo Events
Argo Workflows
Feature Store
AI Gateway
Multi-cluster Kubernetes
```

This distinction prevents roadmap technologies from being mistaken for deployed architecture.

---

# 16. Future Decision Process

A technology must not move automatically from:

```text
FUTURE
```

or:

```text
CANDIDATE
```

to:

```text
ADOPTED
```

The expected lifecycle is:

```text
Requirement
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
Implementation
    |
    v
Validation
    |
    v
ADOPTED
```

This is part of Architecture Governance and Governance as Code.

---

# 17. Decision Governance

Architecture decisions must be:

- Explicit
- Traceable
- Version controlled
- Justified
- Reviewable
- Connected to implementation
- Connected to evidence where possible

Significant changes should update:

```text
Architecture Documentation
        +
Technology Stack
        +
ADR
        +
Diagrams
        +
Governance Artifacts
```

where applicable.

---

# 18. Related ADRs

Current ADR baseline:

```text
ADR-0001 — Kubernetes
ADR-0002 — Argo CD / GitOps
ADR-0003 — Flannel CNI
ADR-0004 — NGINX Ingress
ADR-0005 — PostgreSQL
ADR-0006 — Airflow
ADR-0007 — MLflow
ADR-0008 — OpenMetadata
ADR-0009 — Ollama Local AI
ADR-0010 — Prometheus / Grafana
ADR-0011 — Loki / Tempo / OpenTelemetry
ADR-0012 — GitLab CI/CD
ADR-0013 — Data Architecture
ADR-0014 — Governance as Code
```

No ADR should be implied for Keycloak, Vault, Kafka or Qdrant until such a decision record actually exists.

---

# 19. Related Documentation

```text
00-Executive-Summary.md
01-Architecture-Principles.md
02-Project-Vision.md
03-Business-Objectives.md
05-Technology-Stack.md
Enterprise-AI-Platform.md

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

# 20. Final Architecture Decision Model

The platform architecture follows:

```text
                    BUSINESS
                       |
                       v
                  APPLICATION
                       |
             +---------+---------+
             |                   |
             v                   v
            DATA                 AI
             |                   |
             +---------+---------+
                       |
                       v
                PLATFORM SERVICES
                       |
                       v
                  KUBERNETES
                       |
                       v
                INFRASTRUCTURE
```

Across every layer:

```text
SECURITY
DEVOPS / GITOPS
OPERATIONS
OBSERVABILITY
GOVERNANCE AS CODE
BACKUP / DISASTER RECOVERY
```

The architecture decision process must always distinguish:

```text
WHAT EXISTS
     |
     +
WHAT IS TARGETED
     |
     +
WHAT IS BEING EVALUATED
     |
     +
WHAT IS ONLY A FUTURE POSSIBILITY
```

This distinction is part of the project's architecture governance model.

---

**Architecture Decision Baseline: ACTIVE**