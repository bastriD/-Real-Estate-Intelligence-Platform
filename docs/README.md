# Enterprise AI Platform — Documentation

## Current implementation references — 2026-09-11

This catalog includes architecture baselines and future platform designs. A document marked complete describes documentation maturity, not proof that every capability is implemented or currently running.

Start with the [project README](../Readme.md) and [application architecture](20-APPLICATION/01-Application-Architecture.md). The current backend is one FastAPI application with local JWT authentication, business services, and deterministic matching. React, Keycloak/OIDC, Vault, and semantic/LLM application integrations remain future capabilities in this repository.

Implementation and dated evidence references:

- [Implemented data architecture](40-DATA/ARCHITECTURE-DATA-IMPLEMENTEE.md)
- [Deterministic matching baseline](50-AI/11-Matching-Baseline-Implementation.md)
- [Labelled dataset strategy](50-AI/12-Labelled-Dataset-Strategy.md)
- [Authentication, RBAC, and audit](60-SECURITY/SECURITY-RBAC-AUDIT-IMPLEMENTATION-EVIDENCE.md)
- [Recommendation audit runtime evidence](60-SECURITY/RECOMMENDATION-AUDIT-RUNTIME-EVIDENCE.md)

Use these implementation references to interpret older target designs. Historical runtime evidence applies to its recorded date and scope; current infrastructure health requires separate verification.

## Project Fil Rouge

This directory contains the complete architecture, engineering, operations, security, data, AI and governance documentation for the **Enterprise AI Platform**.

The documentation is maintained according to the following principles:

- Documentation as Code
- Architecture as Code
- Infrastructure as Code
- GitOps
- Governance as Code
- Security by Design
- Observability by Design
- Data Governance by Design
- Local-First AI
- Evidence over Declaration
- Reproducibility
- Traceability
- Recoverability

The `docs/` directory is the primary entry point for understanding the architecture and governance of the platform.

---

# 1. Documentation Structure

```text
docs/
│
├── README.md
├── Documentation-Framework.md
│
├── 00-FOUNDATION/
├── 10-BUSINESS/
├── 20-APPLICATION/
├── 30-INFRASTRUCTURE/
├── 40-DATA/
├── 50-AI/
├── 60-SECURITY/
├── 70-DEVOPS/
├── 80-OPERATIONS/
├── 90-OBSERVABILITY/
├── 95-GOVERNANCE/
├── 98-ADR/
└── 99-DIAGRAMS/
```

Each domain answers a different architectural or operational question.

| Domain | Main Question |
|---|---|
| `00-FOUNDATION` | Why does the platform exist and what principles govern it? |
| `10-BUSINESS` | What business capabilities and requirements does it support? |
| `20-APPLICATION` | How are application services structured? |
| `30-INFRASTRUCTURE` | Where and how does the platform run? |
| `40-DATA` | How is enterprise data managed? |
| `50-AI` | How are AI and ML capabilities designed and governed? |
| `60-SECURITY` | How is the platform protected? |
| `70-DEVOPS` | How are changes built, validated and deployed? |
| `80-OPERATIONS` | How is the platform operated and recovered? |
| `90-OBSERVABILITY` | How do we know the platform is healthy? |
| `95-GOVERNANCE` | How are architecture, risk and technology governed? |
| `98-ADR` | Why were important architecture decisions made? |
| `99-DIAGRAMS` | How is the architecture represented visually? |

---

# 2. Foundation

Directory:

```text
00-FOUNDATION/
```

The Foundation domain defines the strategic and architectural baseline of the project.

```text
00-FOUNDATION/
│
├── 00-Executive-Summary.md
├── 01-Architecture-Principles.md
├── 02-Project-Vision.md
├── 03-Business-Objectives.md
├── 04-Architecture-Decisions.md
├── 05-Technology-Stack.md
├── Architecture-Playbook.md
├── Enterprise-AI-Platform.md
├── Infrastructure-Improvement-Plan.md
├── Master-Prompt.md
└── Project-Constitution.md
```

## Key Documents

### `00-Executive-Summary.md`

Executive overview of the platform, objectives, architecture and transformation strategy.

### `01-Architecture-Principles.md`

Defines the principles that guide architecture decisions.

### `02-Project-Vision.md`

Defines the long-term vision of the Enterprise AI Platform.

### `03-Business-Objectives.md`

Connects technical architecture with measurable business objectives.

### `04-Architecture-Decisions.md`

Provides a high-level view of important architectural decisions.

Detailed decision records are maintained in `98-ADR/`.

### `05-Technology-Stack.md`

Defines the approved and target technology stack.

### `Architecture-Playbook.md`

Defines architectural working practices and design rules.

### `Enterprise-AI-Platform.md`

Provides the overall platform architecture description.

### `Infrastructure-Improvement-Plan.md`

Defines the progressive infrastructure maturity roadmap.

### `Master-Prompt.md`

Provides the project-level AI working context used when developing documentation and architecture.

### `Project-Constitution.md`

Defines the project rules, constraints, architecture principles and governance expectations.

---

# 3. Business Architecture

Directory:

```text
10-BUSINESS/
```

Current documentation:

```text
10-BUSINESS/
└── 01-Business-Architecture.md
```

This domain describes the relationship between:

- Business objectives
- Stakeholders
- Capabilities
- Business processes
- Information needs
- Application services
- Data capabilities
- AI capabilities

The business architecture provides the justification for the technical platform.

---

# 4. Application Architecture

Directory:

```text
20-APPLICATION/
```

Current documentation:

```text
20-APPLICATION/
└── 01-Application-Architecture.md
```

This domain defines how application services interact with:

- Business users
- APIs
- PostgreSQL
- Data services
- AI services
- Kubernetes
- Secrets
- Configuration
- Authentication
- Authorization
- Observability

A central principle is the separation between:

```text
Business Logic
      │
      ├── Data Capabilities
      │
      └── AI Capabilities
```

AI should enhance business functionality without unnecessarily becoming a hard dependency for core business operations.

---

# 5. Infrastructure Architecture

Directory:

```text
30-INFRASTRUCTURE/
```

Documentation:

```text
30-INFRASTRUCTURE/
│
├── 01-Infrastructure-Architecture.md
├── 02-Physical-Architecture.md
├── 03-Virtual-Infrastructure.md
├── 04-Kubernetes-Architecture.md
├── 05-Network-Architecture.md
├── 06-Storage-Architecture.md
├── 07-Compute-Architecture.md
├── 08-High-Availability.md
├── 09-Capacity-Planning.md
└── 10-Disaster-Recovery.md
```

This domain covers the complete infrastructure lifecycle.

## Main Topics

### Physical Architecture

Physical hosts, compute resources, storage and network dependencies.

### Virtual Infrastructure

Virtualization and VM placement.

### Kubernetes

The Kubernetes platform provides the principal runtime environment.

The architecture includes:

- kubeadm HA
- Multiple control-plane nodes
- Multiple workers
- Flannel
- CoreDNS
- NGINX Ingress
- cert-manager
- Argo CD

### Network Architecture

Defines:

- LAN connectivity
- Node routing
- Kubernetes underlay
- Flannel overlay
- Service networking
- Internal DNS
- Ingress
- AI host connectivity

### Storage

Defines storage responsibilities for:

- Kubernetes
- PostgreSQL
- MLflow
- MinIO
- Observability
- Backup and recovery

### High Availability

Documents logical and physical failure domains.

### Capacity Planning

Documents resource limits, scaling considerations and infrastructure constraints.

### Disaster Recovery

Defines infrastructure recovery dependencies and sequencing.

---

# 6. Data Architecture

Directory:

```text
40-DATA/
```

Documentation:

```text
40-DATA/
│
├── 01-Data-Architecture.md
├── 02-Data-Model.md
├── 03-Data-Warehouse.md
├── 04-Data-Governance.md
├── 05-Data-Quality.md
├── 06-Data-Lineage.md
├── 07-Metadata-Management.md
├── 08-Master-Reference-Data.md
├── 09-Data-Lifecycle.md
└── 10-Data-Security.md
```

The target data architecture follows:

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
WAREHOUSE
   │
   ▼
ANALYTICS
   │
   ├── Business Applications
   ├── BI / Dashboards
   ├── Data Analysis
   └── AI / ML
```

## Core Technologies

### PostgreSQL

Primary relational data platform.

### Apache Airflow

Workflow orchestration.

### dbt

Transformation and analytical modeling.

### OpenMetadata

Metadata management, lineage, profiling and governance.

## Responsibility Separation

```text
Airflow      → orchestration
dbt          → transformation
PostgreSQL   → persistence
OpenMetadata → metadata and governance
Data Quality → validation
```

## Data Governance

The data domain includes:

- Ownership
- Classification
- Glossary
- Metadata
- Lineage
- Data Quality
- Lifecycle
- Security
- Master and reference data

Governance definitions should progressively become machine-readable and version controlled.

---

# 7. AI Architecture

Directory:

```text
50-AI/
```

Documentation:

```text
50-AI/
│
├── 01-AI-Platform-Architecture.md
├── 02-LLM-Architecture.md
├── 03-MLOps-Architecture.md
├── 04-RAG-Architecture.md
├── 05-Model-Lifecycle.md
├── 06-Prompt-Engineering.md
├── 07-AI-Governance.md
├── 08-AI-Security.md
├── 09-AI-Observability.md
└── 10-Agentic-AI-Architecture.md
```

This domain defines the AI and ML capabilities of the platform.

## Local-First AI

The default strategy is:

```text
Enterprise Application
        │
        ▼
Internal AI Service
        │
        ▼
RAG / AI Gateway
        │
        ▼
Ollama
        │
        ▼
Local Model
        │
        ▼
Local GPU
```

Local inference is preferred where technically appropriate.

External AI providers are treated as governed exceptions.

## AI Platform

The platform includes:

- Ollama
- Qwen
- Local GPU inference
- MLflow
- RAG
- Prompt management
- Model lifecycle
- AI observability
- AI governance

## RAG

Retrieval-Augmented Generation combines:

```text
Governed Knowledge
       │
       ▼
Embeddings
       │
       ▼
Vector Retrieval
       │
       ▼
Relevant Context
       │
       ▼
Prompt
       │
       ▼
LLM
```

## AI Governance

AI governance covers:

- Model ownership
- Model inventory
- Prompt governance
- Risk classification
- Evaluation
- Data provenance
- RAG source governance
- Human oversight
- External AI approval
- Traceability

---

# 8. Security Architecture

Directory:

```text
60-SECURITY/
```

Documentation:

```text
60-SECURITY/
│
├── 01-Security-Architecture.md
├── 02-Identity-and-Access-Management.md
├── 03-Zero-Trust-Architecture.md
├── 04-Secret-Management.md
├── 05-Network-Security.md
├── 06-Application-Security.md
├── 07-Container-Security.md
├── 08-Kubernetes-Security.md
├── 09-Compliance-and-Risk.md
└── 10-Security-Monitoring.md
```

Security follows a defense-in-depth model.

```text
Identity
   │
   ▼
Authorization
   │
   ▼
Network Security
   │
   ▼
Platform Security
   │
   ▼
Application Security
   │
   ▼
Data Security
   │
   ▼
AI Security
   │
   ▼
Monitoring
   │
   ▼
Evidence
```

## Security Domains

The documentation covers:

- IAM
- Zero Trust
- Secret management
- Network security
- Application security
- Container security
- Kubernetes security
- Compliance
- Risk
- Security monitoring

Security controls should progressively move from written rules toward:

```text
Policy Definition
       │
       ▼
Git
       │
       ▼
CI Validation
       │
       ▼
Runtime Enforcement
       │
       ▼
Evidence
```

---

# 9. DevOps and Platform Engineering

Directory:

```text
70-DEVOPS/
```

Documentation:

```text
70-DEVOPS/
│
├── 01-DevOps-Architecture.md
├── 02-GitOps-Architecture.md
├── 03-CI-CD-Architecture.md
├── 04-Infrastructure-as-Code.md
├── 05-Configuration-Management.md
├── 06-Artifact-Management.md
├── 07-Release-Management.md
├── 08-Environment-Strategy.md
├── 09-Platform-Engineering.md
└── 10-Developer-Experience.md
```

The delivery model follows:

```text
Engineer
   │
   ▼
GitLab
   │
   ▼
Merge Request
   │
   ▼
CI Validation
   │
   ▼
Artifact
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

## GitOps

Git represents approved desired state.

Argo CD reconciles Kubernetes against Git.

```text
Git Desired State
       │
       ▼
Argo CD
       │
       ▼
Kubernetes
       │
       ▼
Actual State
       │
       ▼
Drift Detection
       │
       └──────────► Reconciliation
```

## Platform Engineering

The platform engineering model aims to provide reusable capabilities rather than requiring each project to independently solve:

- Deployment
- Networking
- Security
- Observability
- Secrets
- CI/CD
- Data integration
- AI runtime
- Governance

---

# 10. Operations

Directory:

```text
80-OPERATIONS/
```

Documentation:

```text
80-OPERATIONS/
│
├── 01-Service-Management.md
├── 02-Incident-Management.md
├── 03-Problem-Management.md
├── 04-Change-Management.md
├── 05-Capacity-Management.md
├── 06-Availability-Management.md
├── 07-Backup-and-Restore.md
├── 08-Business-Continuity.md
├── 09-Disaster-Recovery.md
└── 10-SRE-Practices.md
```

Operations documentation covers the lifecycle of the production platform.

## Service Management

Defines service ownership and operational responsibilities.

## Incident Management

Defines response to service disruption.

## Problem Management

Focuses on root-cause elimination.

## Change Management

Integrates operational change with Git, CI/CD and GitOps.

## Capacity Management

Tracks compute, storage, network, database and AI capacity.

## Availability

Defines availability expectations and failure domains.

## Backup and Restore

The operational model is:

```text
Backup
   │
   ▼
Restore
   │
   ▼
Validate
   │
   ▼
Measure
   │
   ▼
Evidence
```

A successful backup alone does not prove recoverability.

## Business Continuity

Defines how critical capabilities continue during degraded conditions.

## Disaster Recovery

Defines recovery order and dependencies.

## SRE

Introduces:

- SLIs
- SLOs
- Error budgets
- Reliability engineering
- Automation
- Operational feedback loops

---

# 11. Observability

Directory:

```text
90-OBSERVABILITY/
```

Documentation:

```text
90-OBSERVABILITY/
│
├── 01-Observability-Architecture.md
├── 02-Metrics-Architecture.md
├── 03-Logging-Architecture.md
├── 04-Distributed-Tracing.md
├── 05-OpenTelemetry-Architecture.md
├── 06-Dashboard-Strategy.md
├── 07-Alerting-Strategy.md
├── 08-SLI-SLO-Monitoring.md
├── 09-Observability-Governance.md
└── 10-Observability-Operations.md
```

The observability architecture is based on three principal signals:

```text
Metrics ─────► Prometheus ──┐
                            │
Logs ────────► Loki ────────┼──► Grafana
                            │
Traces ──────► Tempo ───────┘
```

OpenTelemetry provides vendor-neutral instrumentation and telemetry collection.

## Metrics

Used for:

- Infrastructure health
- Kubernetes health
- Application performance
- Data pipeline health
- AI inference performance
- SLOs
- Alerts
- Capacity

## Logs

Centralized through Loki.

## Traces

Stored in Tempo and correlated with application requests where instrumentation is available.

## SLI / SLO

Observability supports:

```text
Telemetry
   │
   ▼
SLI
   │
   ▼
SLO
   │
   ▼
Error Budget
   │
   ▼
Operational Decision
```

## Governance

Observability also provides machine-readable evidence for:

- Reliability
- Risk
- Security
- Compliance
- Governance controls

---

# 12. Governance

Directory:

```text
95-GOVERNANCE/
```

Documentation:

```text
95-GOVERNANCE/
│
├── 01-Governance-Architecture.md
├── 02-Architecture-Governance.md
├── 03-Decision-Governance.md
├── 04-Risk-Management.md
├── 05-Compliance-Governance.md
├── 06-Technology-Governance.md
├── 07-Documentation-Governance.md
├── 08-Technical-Debt-Management.md
├── 09-Architecture-Maturity-Model.md
└── 10-Architecture-Roadmap.md
```

Governance provides the control system around the architecture.

## Governance Model

```text
Requirements
     │
     ▼
Controls
     │
     ▼
Policies
     │
     ▼
Implementation
     │
     ▼
Runtime
     │
     ▼
Evidence
     │
     ▼
Review
     │
     ▼
Improvement
```

## Governance Domains

The platform distinguishes:

- Architecture governance
- Decision governance
- Risk management
- Compliance governance
- Technology governance
- Documentation governance
- Technical debt
- Architecture maturity
- Architecture roadmap

These concepts remain related but separate.

For example:

```text
Risk            ≠ Policy
ADR             ≠ Control
Technical Debt  ≠ Risk
SLO             ≠ Requirement
```

---

# 13. Governance as Code

Governance as Code is a cross-cutting architecture principle.

Governance artifacts should progressively become machine-readable.

Potential representations include:

```text
YAML
JSON
Markdown Front Matter
JSON Schema
Policy Definitions
Stable IDs
```

The target governance lifecycle is:

```text
Requirement
     │
     ▼
Machine-Readable Control
     │
     ▼
Git
     │
     ▼
Merge Request
     │
     ▼
CI Validation
     │
     ▼
Approved Governance State
     │
     ▼
Runtime Enforcement
     │
     ▼
Runtime Evidence
     │
     ▼
Continuous Governance
```

Possible enforcement and evidence systems include:

- GitLab CI
- Argo CD
- Kubernetes policy engines
- OpenMetadata
- Prometheus
- Alertmanager
- MLflow
- Observability systems

The principle is:

> Evidence over declaration.

---

# 14. Architecture Decision Records

Directory:

```text
98-ADR/
```

Current ADR catalog:

```text
98-ADR/
│
├── ADR-0001-Kubernetes.md
├── ADR-0002-ArgoCD-GitOps.md
├── ADR-0003-Flannel-CNI.md
├── ADR-0004-NGINX-Ingress.md
├── ADR-0005-PostgreSQL.md
├── ADR-0006-Airflow.md
├── ADR-0007-MLflow.md
├── ADR-0008-OpenMetadata.md
├── ADR-0009-Ollama-Local-AI.md
├── ADR-0010-Prometheus-Grafana.md
├── ADR-0011-Loki-Tempo-OpenTelemetry.md
├── ADR-0012-GitLab-CI-CD.md
├── ADR-0013-Data-Architecture.md
└── ADR-0014-Governance-as-Code.md
```

ADRs answer:

```text
WHY WAS THIS ARCHITECTURAL DECISION MADE?
```

Architecture documentation answers:

```text
HOW IS THE SYSTEM STRUCTURED?
```

Both must remain synchronized.

---

# 15. Architecture Diagrams

Directory:

```text
99-DIAGRAMS/
```

PlantUML is used as the architecture diagram source format.

```text
99-DIAGRAMS/
│
├── README.md
│
├── 01-Enterprise-Context.puml
├── 02-Enterprise-Platform-Architecture.puml
├── 03-Infrastructure-Architecture.puml
├── 04-Kubernetes-Architecture.puml
├── 05-Network-Architecture.puml
├── 06-Application-Architecture.puml
├── 07-Data-Architecture.puml
├── 08-AI-Architecture.puml
├── 09-MLOps-Architecture.puml
├── 10-DevOps-GitOps-Architecture.puml
├── 11-Observability-Architecture.puml
├── 12-Security-Architecture.puml
├── 13-Governance-as-Code.puml
├── 14-Backup-DR-Architecture.puml
│
└── rendered-diagrams/
    ├── 01-Enterprise-Context.svg
    ├── 02-Enterprise-Platform-Architecture.svg
    ├── 03-Infrastructure-Architecture.svg
    ├── 04-Kubernetes-Architecture.svg
    ├── 05-Network-Architecture.svg
    ├── 06-Application-Architecture.svg
    ├── 07-Data-Architecture.svg
    ├── 08-AI-Architecture.svg
    ├── 09-MLOps-Architecture.svg
    ├── 10-DevOps-GitOps-Architecture.svg
    ├── 11-Observability-Architecture.svg
    ├── 12-Security-Architecture.svg
    ├── 13-Governance-as-Code.svg
    └── 14-Backup-DR-Architecture.svg
```

## Diagram Catalog

| ID | Diagram |
|---|---|
| 01 | Enterprise Context |
| 02 | Enterprise Platform Architecture |
| 03 | Infrastructure Architecture |
| 04 | Kubernetes Architecture |
| 05 | Network Architecture |
| 06 | Application Architecture |
| 07 | Data Architecture |
| 08 | AI Architecture |
| 09 | MLOps Architecture |
| 10 | DevOps & GitOps Architecture |
| 11 | Observability Architecture |
| 12 | Security Architecture |
| 13 | Governance as Code |
| 14 | Backup & Disaster Recovery |

The authoritative source is:

```text
*.puml
```

The generated representation is:

```text
rendered-diagrams/*.svg
```

Generated SVG files must not be manually edited.

---

# 16. Rendering Architecture Diagrams

From:

```text
docs/99-DIAGRAMS/
```

render all diagrams using:

```bash
plantuml -tsvg -o rendered-diagrams *.puml
```

Render one diagram using:

```bash
plantuml -tsvg -o rendered-diagrams 08-AI-Architecture.puml
```

The target workflow is:

```text
Architecture Change
        │
        ▼
PlantUML
        │
        ▼
Git
        │
        ▼
CI Validation
        │
        ▼
SVG Generation
        │
        ▼
Documentation
```

This is the project's **Diagrams as Code** model.

---

# 17. Cross-Cutting Architecture

The architecture can be viewed vertically as:

```text
                   BUSINESS
                      │
                      ▼
                 APPLICATION
                      │
            ┌─────────┴─────────┐
            ▼                   ▼
           DATA                 AI
            │                   │
            └─────────┬─────────┘
                      ▼
               PLATFORM SERVICES
                      │
                      ▼
                  KUBERNETES
                      │
                      ▼
                INFRASTRUCTURE
```

Across every layer:

```text
────────────────────────────────────────────
SECURITY
DEVOPS / GITOPS
OBSERVABILITY
GOVERNANCE AS CODE
OPERATIONS
BACKUP / DISASTER RECOVERY
────────────────────────────────────────────
```

These are cross-cutting capabilities rather than isolated architectural silos.

---

# 18. Platform Technology Model

The current platform technology model includes:

| Capability | Technology / Approach |
|---|---|
| Virtualization | Proxmox VE |
| Container Orchestration | Kubernetes |
| Kubernetes Deployment | kubeadm |
| CNI | Flannel |
| Ingress | NGINX Ingress |
| TLS Automation | cert-manager |
| Source Control | GitLab |
| CI | GitLab CI / GitLab Runner |
| GitOps | Argo CD |
| Data Orchestration | Apache Airflow |
| Data Transformation | dbt |
| Relational Data | PostgreSQL |
| Metadata / Governance | OpenMetadata |
| ML Lifecycle | MLflow |
| Artifact Storage | MinIO |
| Local AI Runtime | Ollama |
| LLM | Qwen |
| Metrics | Prometheus |
| Visualization | Grafana |
| Logs | Loki |
| Traces | Tempo |
| Telemetry | OpenTelemetry |
| Kubernetes Backup | Velero |
| Documentation | Markdown |
| Architecture Diagrams | PlantUML |
| Architecture Decisions | ADR |
| Governance | Governance as Code |

---

# 19. Architectural Operating Model

The platform follows:

```text
PLAN
 │
 ▼
DOCUMENT
 │
 ▼
DECIDE
 │
 ▼
IMPLEMENT
 │
 ▼
VALIDATE
 │
 ▼
DEPLOY
 │
 ▼
OBSERVE
 │
 ▼
GOVERN
 │
 ▼
IMPROVE
 │
 └───────────────► PLAN
```

The documentation therefore does not describe architecture as a static object.

It describes a continuously governed engineering system.

---

# 20. Documentation as Code

Documentation is stored in Git alongside architecture and engineering artifacts.

The target workflow is:

```text
Documentation Change
        │
        ▼
Git
        │
        ▼
Merge Request
        │
        ▼
Review
        │
        ▼
Validation
        │
        ▼
Approved Documentation
```

Documentation changes should be traceable to:

- Requirements
- Architecture changes
- ADRs
- Risk changes
- Operational experience
- Incidents
- Security requirements
- Governance requirements

where applicable.

---

# 21. Architecture as Code

Architecture artifacts are maintained in machine-manageable formats wherever practical.

Examples include:

```text
Markdown
PlantUML
YAML
JSON
GitOps manifests
Terraform
Ansible
Kubernetes YAML
Helm values
dbt models
CI pipelines
Governance definitions
```

This improves:

- Reproducibility
- Version control
- Review
- Automation
- Traceability
- Governance

---

# 22. Infrastructure as Code

Infrastructure configuration should progressively move toward reproducible code.

Target tooling includes:

- Terraform
- Ansible
- Kubernetes manifests
- Helm
- GitLab CI
- Argo CD

Manual infrastructure changes should not become undocumented permanent state.

---

# 23. Security by Design

Security is integrated throughout the engineering lifecycle.

```text
Design
  │
  ▼
Source
  │
  ▼
CI
  │
  ▼
Artifact
  │
  ▼
Deployment
  │
  ▼
Runtime
  │
  ▼
Data / AI
  │
  ▼
Monitoring
  │
  ▼
Evidence
```

Security is therefore not a final deployment step.

---

# 24. Observability by Design

Every important platform capability should progressively expose appropriate:

```text
Metrics
Logs
Traces
Health
SLOs
Alerts
```

Observability supports both operational troubleshooting and governance evidence.

---

# 25. Data Governance by Design

Data governance is integrated into the platform lifecycle.

```text
Data Source
    │
    ▼
Ingestion
    │
    ▼
Transformation
    │
    ▼
Quality
    │
    ▼
Metadata
    │
    ▼
Lineage
    │
    ▼
Classification
    │
    ▼
Consumption
```

OpenMetadata provides the central metadata and governance capability.

---

# 26. AI Governance by Design

AI capabilities require governance throughout their lifecycle.

```text
AI Use Case
    │
    ▼
Risk Classification
    │
    ▼
Data Validation
    │
    ▼
Model / Prompt Selection
    │
    ▼
Evaluation
    │
    ▼
Approval
    │
    ▼
Deployment
    │
    ▼
Observability
    │
    ▼
Review
```

Local AI reduces external data exposure but does not eliminate AI security or governance requirements.

---

# 27. Recovery by Design

Recoverability is an architectural capability.

The expected lifecycle is:

```text
Backup
   │
   ▼
Restore
   │
   ▼
Validate
   │
   ▼
Measure
   │
   ▼
Evidence
   │
   ▼
Improve
```

The platform should progressively measure actual RPO and RTO through recovery exercises.

---

# 28. Documentation Relationships

Different artifacts have different responsibilities.

| Artifact | Question |
|---|---|
| Executive Summary | What is the platform? |
| Project Vision | Where are we going? |
| Business Objectives | Why are we building it? |
| Architecture Principles | What rules guide design? |
| Architecture Documentation | How is it structured? |
| ADR | Why did we choose this? |
| Security Documentation | How is it protected? |
| Operations Documentation | How is it operated? |
| Observability Documentation | How do we know it works? |
| Governance Documentation | How is it controlled? |
| Diagrams | How can we visualize it? |
| Runbooks | How do we execute operational procedures? |

No single document replaces all the others.

---

# 29. Documentation Navigation

For a first reading of the project, the recommended order is:

```text
1. 00-FOUNDATION/00-Executive-Summary.md
2. 00-FOUNDATION/02-Project-Vision.md
3. 00-FOUNDATION/03-Business-Objectives.md
4. 00-FOUNDATION/01-Architecture-Principles.md
5. 00-FOUNDATION/Enterprise-AI-Platform.md
6. 99-DIAGRAMS/01-Enterprise-Context.puml
7. 99-DIAGRAMS/02-Enterprise-Platform-Architecture.puml
```

Then continue according to the reader's role.

## Business / Management

```text
00-FOUNDATION
      ↓
10-BUSINESS
      ↓
95-GOVERNANCE
      ↓
99-DIAGRAMS
```

## Architect

```text
00-FOUNDATION
      ↓
10-BUSINESS
      ↓
20-APPLICATION
      ↓
30-INFRASTRUCTURE
      ↓
40-DATA
      ↓
50-AI
      ↓
60-SECURITY
      ↓
98-ADR
      ↓
99-DIAGRAMS
```

## DevOps / Platform Engineer

```text
30-INFRASTRUCTURE
      ↓
60-SECURITY
      ↓
70-DEVOPS
      ↓
80-OPERATIONS
      ↓
90-OBSERVABILITY
      ↓
98-ADR
```

## Data Engineer

```text
40-DATA
   ↓
50-AI
   ↓
70-DEVOPS
   ↓
90-OBSERVABILITY
   ↓
95-GOVERNANCE
```

## AI / MLOps Engineer

```text
40-DATA
   ↓
50-AI
   ↓
60-SECURITY
   ↓
70-DEVOPS
   ↓
90-OBSERVABILITY
   ↓
95-GOVERNANCE
```

---

# 30. Initial Documentation Baseline Inventory

The counts below describe the initial architecture baseline. Later implementation and evidence documents are additional; this is not a live file count. Current implementation references are listed at the top of this index.

```text
Foundation                 11 documents
Business                    1 document
Application                 1 document
Infrastructure             10 documents
Data                       10 documents
AI                         10 documents
Security                   10 documents
DevOps                     10 documents
Operations                 10 documents
Observability              10 documents
Governance                 10 documents
ADRs                       14 documents
Architecture Diagrams      14 PlantUML sources
Rendered Diagrams          14 SVG files
```

In addition:

```text
docs/README.md
docs/Documentation-Framework.md
99-DIAGRAMS/README.md
```

provide documentation navigation and framework guidance.

---

# 31. Documentation Status

| Domain | Status |
|---|---|
| Foundation | Complete |
| Business Architecture | Baseline complete |
| Application Architecture | Updated to repository implementation on 2026-09-11 |
| Infrastructure | Complete |
| Data | Complete |
| AI | Complete |
| Security | Complete |
| DevOps | Complete |
| Operations | Complete |
| Observability | Complete |
| Governance | Complete |
| ADR | Complete baseline |
| Architecture Diagrams | Complete baseline |

The documentation baseline is therefore established across the full enterprise platform architecture.

Future changes should evolve this baseline rather than create parallel undocumented architecture.

---

# 32. Core Principles Summary

```text
Git as Source of Truth
        +
Documentation as Code
        +
Architecture as Code
        +
Infrastructure as Code
        +
GitOps
        +
Governance as Code
        +
Security by Design
        +
Observability by Design
        +
Data Governance by Design
        +
AI Governance by Design
        +
Recovery by Design
        +
Local-First AI
        +
Evidence over Declaration
```

Together these principles define the target operating model of the Enterprise AI Platform.

---

# 33. Final Platform Model

```text
                         BUSINESS
                            │
                            ▼
                       APPLICATION
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
                DATA                   AI
                 │                     │
                 └──────────┬──────────┘
                            ▼
                    PLATFORM SERVICES
                            │
                            ▼
                       KUBERNETES
                            │
                            ▼
                     INFRASTRUCTURE


CROSS-CUTTING CAPABILITIES
──────────────────────────────────────────────────
SECURITY
DEVOPS / GITOPS
OPERATIONS
OBSERVABILITY
GOVERNANCE AS CODE
BACKUP / DISASTER RECOVERY
──────────────────────────────────────────────────
```

The objective is not merely to deploy technologies.

The objective is to operate a platform that is:

- Reproducible
- Observable
- Secure
- Governed
- Recoverable
- Traceable
- Evolvable
- Data-aware
- AI-ready
- Operationally sustainable

---

# 34. Project Documentation Status

**Documentation architecture:** Established  
**Architecture baseline:** Established  
**Infrastructure architecture:** Documented  
**Data architecture:** Documented  
**AI architecture:** Documented  
**Security architecture:** Documented  
**DevOps / GitOps:** Documented  
**Operations:** Documented  
**Observability:** Documented  
**Governance:** Documented  
**Governance as Code:** Defined  
**ADR baseline:** Established  
**Architecture diagrams:** 14/14 rendered  
**Diagram format:** PlantUML → SVG  
**Documentation model:** Documentation as Code  
**Deployment model:** GitOps  
**AI strategy:** Local-first  
**Governance strategy:** Evidence-driven Governance as Code

---

**Enterprise AI Platform — Architecture & Engineering Documentation**
