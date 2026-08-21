# Architecture Diagrams

**Project:** Enterprise AI Platform  
**Business Application:** Real Estate Intelligence Platform  
**Format:** PlantUML source + generated SVG  
**Source of Truth:** `.puml` files  
**Rendered Output:** `rendered-diagrams/`

---

## 1. Purpose

This directory contains the architecture diagrams of the Enterprise AI Platform.

The diagrams are maintained using a **Diagrams as Code** approach.

Authoritative sources are stored as PlantUML files:

```text
*.puml
```

Rendered versions are generated as:

```text
rendered-diagrams/*.svg
```

The `.puml` source files are authoritative.

The generated `.svg` files are visualization artifacts and must not be manually edited.

The diagram repository supports the wider project principles of:

- Documentation as Code
- Architecture as Code
- Governance as Code
- GitOps
- Traceability
- Reproducibility
- Continuous validation

---

## 2. Rendering

### Render one diagram

```bash
plantuml -tsvg -o rendered-diagrams 01-Enterprise-Context.puml
```

### Render all diagrams

From `docs/99-DIAGRAMS/`:

```bash
plantuml -tsvg -o rendered-diagrams *.puml
```

Generated SVG files are written to:

```text
rendered-diagrams/
```

### Verify generated diagrams

```bash
ls -lh rendered-diagrams/
```

---

## 3. Directory Structure

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

---

## 4. Diagram Catalog

| ID | Diagram | Purpose |
|---|---|---|
| 01 | Enterprise Context | High-level enterprise system context |
| 02 | Enterprise Platform Architecture | Main platform technologies and integrations |
| 03 | Infrastructure Architecture | Physical, virtual, Kubernetes and AI infrastructure |
| 04 | Kubernetes Architecture | Control plane, workers, namespaces and platform services |
| 05 | Network Architecture | LAN, routing, DNS, Flannel overlay and ingress |
| 06 | Application Architecture | Business APIs, data, AI and application integration |
| 07 | Data Architecture | Raw, staging, warehouse, analytics and governance |
| 08 | AI Architecture | Local AI, RAG, Ollama, Qwen and AI governance |
| 09 | MLOps Architecture | Training, MLflow, evaluation, promotion and deployment |
| 10 | DevOps & GitOps Architecture | GitLab CI, GitOps, Argo CD and Kubernetes delivery |
| 11 | Observability Architecture | Metrics, logs, traces, SLOs and alerting |
| 12 | Security Architecture | Identity, policies, secrets, data and AI security |
| 13 | Governance as Code | Governance lifecycle, enforcement and runtime evidence |
| 14 | Backup & DR Architecture | Backup, restore, recovery ordering and validation |

---

## 5. Diagram 01 — Enterprise Context

**Source**

```text
01-Enterprise-Context.puml
```

**Rendered**

```text
rendered-diagrams/01-Enterprise-Context.svg
```

### Purpose

Provides the highest-level view of the platform and its relationships with:

- Business users
- Data and AI engineers
- Platform and DevOps engineers
- Governance and security stakeholders
- Enterprise source systems
- Enterprise knowledge
- Data capabilities
- AI capabilities
- External AI providers

This diagram intentionally hides implementation details.

Its purpose is to explain **what the platform interacts with**, not how every internal component is implemented.

---

## 6. Diagram 02 — Enterprise Platform Architecture

**Source**

```text
02-Enterprise-Platform-Architecture.puml
```

**Rendered**

```text
rendered-diagrams/02-Enterprise-Platform-Architecture.svg
```

### Purpose

Provides the main technical view of the Enterprise AI Platform.

It includes:

- GitLab
- GitLab Runner
- Argo CD
- Kubernetes
- NGINX Ingress
- PostgreSQL
- Apache Airflow
- dbt
- MLflow
- OpenMetadata
- Ollama
- Prometheus
- Grafana
- Loki
- Tempo
- OpenTelemetry
- Governance as Code

This diagram establishes how the principal platform technologies interact.

---

## 7. Diagram 03 — Infrastructure Architecture

**Source**

```text
03-Infrastructure-Architecture.puml
```

**Rendered**

```text
rendered-diagrams/03-Infrastructure-Architecture.svg
```

### Purpose

Describes the infrastructure hosting the platform.

It includes:

- Physical infrastructure
- Proxmox virtualization
- Kubernetes control-plane nodes
- Kubernetes worker nodes
- Additional worker capacity
- AI compute hosts
- GPU resources
- Storage
- Networking
- Backup and recovery infrastructure

The infrastructure architecture distinguishes between:

```text
Physical Infrastructure
        │
        ├── Virtualization
        │
        ├── Kubernetes
        │
        ├── AI Compute
        │
        ├── Network
        │
        └── Storage / Recovery
```

A key architectural constraint is that logical Kubernetes high availability does not automatically eliminate physical host failure domains.

---

## 8. Diagram 04 — Kubernetes Architecture

**Source**

```text
04-Kubernetes-Architecture.puml
```

**Rendered**

```text
rendered-diagrams/04-Kubernetes-Architecture.svg
```

### Purpose

Describes the Kubernetes runtime architecture.

It includes:

- kubeadm HA control plane
- Three control-plane nodes
- etcd
- Scheduler
- Controller Manager
- Kubernetes API Server
- Worker nodes
- Flannel
- CoreDNS
- NGINX Ingress
- cert-manager
- Argo CD
- Root Application
- Application namespaces
- Platform namespaces
- Persistent storage
- Observability
- Velero

The cluster follows the principle:

```text
Git
 ↓
Argo CD
 ↓
Kubernetes desired state
 ↓
Continuous reconciliation
```

Git is therefore the desired-state source of truth for managed Kubernetes resources.

---

## 9. Diagram 05 — Network Architecture

**Source**

```text
05-Network-Architecture.puml
```

**Rendered**

```text
rendered-diagrams/05-Network-Architecture.svg
```

### Purpose

Documents the networking relationships required by the platform.

It includes:

- Enterprise LAN
- Main router / gateway
- LAN routing
- Primary infrastructure network
- Additional worker network
- AI compute network
- Kubernetes node connectivity
- Flannel overlay
- Pod networking
- Kubernetes Service network
- CoreDNS
- Internal DNS
- NGINX Ingress
- TLS
- AI host connectivity
- Network observability

The fundamental dependency is:

```text
Physical / Logical Underlay
            ↓
Node-to-Node Routing
            ↓
Flannel Overlay
            ↓
Pod Connectivity
            ↓
Kubernetes Services
            ↓
Ingress
            ↓
Applications
```

Flannel cannot compensate for broken underlay routing between Kubernetes nodes.

Correct node-to-node connectivity is therefore a prerequisite for reliable cluster networking.

---

## 10. Diagram 06 — Application Architecture

**Source**

```text
06-Application-Architecture.puml
```

**Rendered**

```text
rendered-diagrams/06-Application-Architecture.svg
```

### Purpose

Describes how business applications consume platform capabilities.

It includes:

- Business frontend
- Business APIs
- FastAPI services
- Background jobs
- PostgreSQL
- Analytics data
- AI integration services
- Internal AI API
- AI Gateway target state
- RAG
- Ollama
- Qwen
- Configuration
- Kubernetes Secrets
- Observability
- Authentication and authorization

The architecture separates:

```text
Business Logic
      │
      ├── Data Services
      │
      └── AI Services
```

AI capabilities should not unnecessarily become hard dependencies of core business functionality.

Where possible:

```text
AI unavailable
      ↓
Core application remains operational
```

This supports graceful degradation.

---

## 11. Diagram 07 — Data Architecture

**Source**

```text
07-Data-Architecture.puml
```

**Rendered**

```text
rendered-diagrams/07-Data-Architecture.svg
```

### Purpose

Documents the complete governed data lifecycle.

The principal data flow is:

```text
Source Systems
      ↓
Apache Airflow
      ↓
raw
      ↓
staging
      ↓
warehouse
      ↓
analytics
      ↓
Business / BI / AI Consumers
```

### Data Layers

#### RAW

Preserves source-oriented data with minimal transformation.

#### STAGING

Performs:

- Standardization
- Type normalization
- Cleaning
- Deduplication
- Technical preparation

#### WAREHOUSE

Contains integrated business models such as:

- Facts
- Dimensions
- Business entities
- Historical structures
- Consolidated business rules

#### ANALYTICS

Contains consumer-oriented:

- Views
- KPIs
- Aggregations
- Reporting datasets
- AI-ready curated datasets

### Responsibilities

Airflow owns orchestration.

dbt owns transformation logic.

OpenMetadata owns metadata and data-governance visibility.

Data Quality validates expected properties of data.

The intended separation is:

```text
Airflow = WHEN
dbt     = HOW DATA IS TRANSFORMED
DQ      = WHETHER DATA IS VALID
Metadata = WHAT DATA MEANS AND WHO OWNS IT
```

---

## 12. Diagram 08 — AI Architecture

**Source**

```text
08-AI-Architecture.puml
```

**Rendered**

```text
rendered-diagrams/08-AI-Architecture.svg
```

### Purpose

Describes the local-first AI architecture.

It includes:

- Internal AI API
- AI Gateway target state
- RAG
- Prompt construction
- Embeddings
- Retrieval
- Vector storage
- PostgreSQL / pgvector candidate
- Ollama
- Qwen
- Local GPU compute
- MLflow
- OpenMetadata
- AI Governance as Code
- External AI governance

The default inference path is:

```text
Application
    ↓
Internal AI API
    ↓
AI Gateway
    ↓
RAG / Direct Inference
    ↓
Ollama
    ↓
Qwen
    ↓
Local GPU
```

The core architectural principle is:

```text
LOCAL AI = DEFAULT

EXTERNAL AI = GOVERNED EXCEPTION
```

Enterprise prompts, documents and contextual data remain inside the controlled platform by default.

External AI usage requires explicit review of:

- Data classification
- Security
- Privacy
- Cost
- Architecture
- Business justification

---

## 13. Diagram 09 — MLOps Architecture

**Source**

```text
09-MLOps-Architecture.puml
```

**Rendered**

```text
rendered-diagrams/09-MLOps-Architecture.svg
```

### Purpose

Describes the complete model lifecycle.

```text
Source Code
    ↓
Training
    ↓
MLflow Tracking
    ↓
Model Candidate
    ↓
Evaluation
    ↓
Governance Gate
    ↓
Model Registry
    ↓
GitOps Promotion
    ↓
Deployment
    ↓
Runtime Monitoring
    ↓
Rollback / Improvement
```

### MLflow Responsibilities

MLflow is authoritative for:

- Experiments
- Runs
- Parameters
- Metrics
- Artifacts
- Model versions
- Registry metadata

### Promotion Principle

A model must not reach production solely because training succeeded.

Production promotion requires:

```text
Technical Evaluation
        +
Governance Validation
        +
Approval where required
```

Model approval and deployment are separate lifecycle events.

---

## 14. Diagram 10 — DevOps & GitOps Architecture

**Source**

```text
10-DevOps-GitOps-Architecture.puml
```

**Rendered**

```text
rendered-diagrams/10-DevOps-GitOps-Architecture.svg
```

### Purpose

Documents the software and platform delivery lifecycle.

The principal path is:

```text
Developer
    ↓
GitLab
    ↓
Merge Request
    ↓
CI
    ↓
Tests / Security / Governance
    ↓
Artifact
    ↓
GitOps Repository
    ↓
Argo CD
    ↓
Kubernetes
```

### CI Responsibility

GitLab CI answers:

```text
Is this change acceptable
to merge and publish?
```

### GitOps Responsibility

Argo CD answers:

```text
Does the runtime match
the approved Git state?
```

### Drift Management

```text
Git Desired State
       ↓
Argo CD
       ↓
Kubernetes
       ↓
Actual State
       ↓
Drift Detection
       ↓
Reconciliation
```

Direct runtime configuration must not become the permanent source of truth.

---

## 15. Diagram 11 — Observability Architecture

**Source**

```text
11-Observability-Architecture.puml
```

**Rendered**

```text
rendered-diagrams/11-Observability-Architecture.svg
```

### Purpose

Documents the platform observability architecture.

The three principal signals are:

```text
Metrics → Prometheus
Logs    → Loki
Traces  → Tempo
```

Grafana provides the unified exploration and visualization layer.

### Metrics

Metrics originate from:

- Applications
- Kubernetes
- Nodes
- Databases
- Airflow
- AI services
- GPUs
- Batch jobs

### Logs

Logs are collected through the centralized logging pipeline and stored in Loki.

### Traces

Distributed traces use OpenTelemetry instrumentation and the OpenTelemetry Collector before storage in Tempo.

### Reliability

The observability architecture also supports:

- SLIs
- SLOs
- Error budgets
- Burn-rate alerts
- Operational alerts
- Key Risk Indicators
- Governance evidence

The intended model is:

```text
Telemetry
    ↓
Operational Evidence
    ↓
SLO / Risk / Control Evaluation
    ↓
Continuous Governance
```

---

## 16. Diagram 12 — Security Architecture

**Source**

```text
12-Security-Architecture.puml
```

**Rendered**

```text
rendered-diagrams/12-Security-Architecture.svg
```

### Purpose

Documents the defense-in-depth security model.

Security controls cover:

- Identity
- Authentication
- Authorization
- Kubernetes RBAC
- Application RBAC
- Least privilege
- TLS
- Secrets
- Protected CI variables
- Protected branches
- Merge Request review
- Security scanning
- Kubernetes workload security
- Policy as Code
- Network controls
- Database roles
- Data classification
- GDPR controls
- AI security
- Prompt governance
- RAG governance
- External AI governance
- Security monitoring
- Audit evidence

The security model follows:

```text
Identity
   ↓
Authorization
   ↓
Network Boundary
   ↓
Runtime Policy
   ↓
Application Controls
   ↓
Data Controls
   ↓
AI Controls
   ↓
Monitoring
   ↓
Evidence
```

Security is therefore implemented across multiple independent layers rather than relying on a single control.

---

## 17. Diagram 13 — Governance as Code

**Source**

```text
13-Governance-as-Code.puml
```

**Rendered**

```text
rendered-diagrams/13-Governance-as-Code.svg
```

### Purpose

This diagram represents the governance operating model of the platform.

The principal governance lifecycle is:

```text
Business / Architecture / Security / Compliance Requirements
                            ↓
                        Controls
                            ↓
                        Policies
                            ↓
                 Machine-Readable Rules
                            ↓
                           Git
                            ↓
                     CI Validation
                            ↓
                 Approved Governance
                            ↓
         GitOps / Policy / Metadata / SLO
                            ↓
                         Runtime
                            ↓
                         Evidence
                            ↓
                Continuous Evaluation
                            ↓
              Governance / Risk Dashboard
                            ↓
                     Human Review
                            ↓
                     Improvement
```

### Governance Artifacts

The model distinguishes between:

- Requirements
- Controls
- Policies
- Risks
- Exceptions
- ADRs
- Technology catalog
- Technical debt
- SLOs

These concepts must remain separate but cross-referenced.

For example:

```text
Risk ≠ Policy
ADR ≠ Control
Technical Debt ≠ Risk
SLO ≠ Requirement
```

### Governance as Code

Governance artifacts progressively become machine-readable using:

- YAML
- JSON
- Markdown front matter
- JSON Schema
- Stable identifiers

### Enforcement

Governance is applied through:

- GitLab CI
- Argo CD
- Kubernetes policy engines
- OpenMetadata
- Prometheus
- Alertmanager
- MLflow / AI evaluation gates

### Evidence Principle

The target maturity model is:

```text
Document
   ↓
Define
   ↓
Validate
   ↓
Enforce
   ↓
Observe
   ↓
Prove
   ↓
Improve
```

The guiding principle is:

> Evidence over declaration.

A documented control is useful.

A validated and continuously evidenced control is stronger.

---

## 18. Diagram 14 — Backup & Disaster Recovery

**Source**

```text
14-Backup-DR-Architecture.puml
```

**Rendered**

```text
rendered-diagrams/14-Backup-DR-Architecture.svg
```

### Purpose

Documents backup, restoration and disaster-recovery architecture.

Protected platform state includes:

- Git repositories
- GitOps desired state
- PostgreSQL databases
- Kubernetes resources
- Persistent volumes
- OpenMetadata state
- MLflow metadata
- MinIO artifacts
- Configuration
- AI model definitions

### Recovery Order

Recovery follows an intentional sequence:

```text
1. Infrastructure
        ↓
2. Kubernetes
        ↓
3. Git / GitOps
        ↓
4. Data
        ↓
5. Platform Services
        ↓
6. Applications
        ↓
7. AI Services
        ↓
8. Validation
```

Higher-level services must not be restored before their lower-level dependencies are operational.

### Backup Principle

```text
Backup ≠ Recovery
```

A successful backup does not prove that the platform can be recovered.

The complete lifecycle is:

```text
Backup
   ↓
Restore
   ↓
Validate
   ↓
Measure
   ↓
Evidence
   ↓
Improve
```

### Recovery Objectives

The architecture tracks:

- RPO — Recovery Point Objective
- RTO — Recovery Time Objective
- Actual recovery time
- Actual data loss
- Restore-test evidence

RPO and RTO become meaningful only when validated by real recovery exercises.

---

## 19. Cross-Diagram Architecture Model

The diagrams are intentionally layered.

```text
01 Enterprise Context
        │
        ▼
02 Enterprise Platform
        │
        ├──────────────┐
        ▼              ▼
03 Infrastructure   06 Application
        │              │
        ▼              ├──────────────┐
04 Kubernetes          ▼              ▼
        │           07 Data         08 AI
        ▼              │              │
05 Network             └──────┬───────┘
                              ▼
                          09 MLOps
                              │
                              ▼
                       10 DevOps / GitOps
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
              11 Observ. 12 Security 13 Governance
                    │         │         │
                    └─────────┼─────────┘
                              ▼
                       14 Backup / DR
```

Each diagram answers a different architectural question.

They should not all attempt to represent the entire platform at the same level of detail.

---

## 20. Architecture Principles Represented

The diagram set represents the following architectural principles.

### Git as Source of Truth

Code, infrastructure configuration, governance artifacts and GitOps desired state are version controlled.

### GitOps

Kubernetes desired state is reconciled from Git through Argo CD.

### Data Layering

```text
raw → staging → warehouse → analytics
```

### Separation of Responsibilities

```text
Airflow      = orchestration
dbt          = transformation
PostgreSQL   = data persistence
OpenMetadata = metadata / governance
MLflow       = ML lifecycle
Argo CD      = GitOps reconciliation
Prometheus   = metrics
Loki         = logs
Tempo        = traces
Grafana      = visualization
Ollama       = local inference runtime
```

### Local-First AI

Local AI inference is preferred for enterprise workloads.

External AI providers are governed exceptions.

### Observability by Design

Metrics, logs and traces are architecture components, not operational afterthoughts.

### Security by Design

Security controls exist across:

```text
Source
→ CI
→ Artifact
→ Deployment
→ Runtime
→ Data
→ AI
→ Observability
```

### Governance as Code

Governance moves progressively from documents toward:

```text
Machine-readable definition
        ↓
Version control
        ↓
Validation
        ↓
Enforcement
        ↓
Runtime evidence
```

### Recoverability

Backup success alone is insufficient.

Recovery capability must be tested and evidenced.

---

## 21. Diagram Governance Rules

The following rules apply to all architecture diagrams.

### Source of Truth

PlantUML files are authoritative:

```text
*.puml
```

Generated SVG files are not manually edited.

### Version Control

PlantUML sources must be stored in Git.

Rendered diagrams may also be version controlled where useful for:

- Markdown rendering
- Documentation portals
- Reviews
- Project deliverables
- Offline consultation

### Architecture Changes

When an architecture decision changes the platform, review whether the following must also change:

```text
Architecture Documentation
        +
ADR
        +
PlantUML Diagram
        +
Governance Artifacts
        +
Operational Documentation
```

### Naming Convention

Use:

```text
NN-Descriptive-Name.puml
```

Example:

```text
08-AI-Architecture.puml
```

### Output Format

Preferred rendered format:

```text
SVG
```

SVG is preferred because it:

- Scales without quality loss
- Works well in Markdown
- Works well in Git repositories
- Can be embedded in documentation
- Is suitable for presentations and reports

---

## 22. Diagrams as Code

The target workflow is:

```text
Architecture Change
        │
        ▼
PlantUML Source
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
SVG Generation
        │
        ▼
Architecture Documentation
```

This integrates diagrams into the wider:

```text
Documentation as Code
        +
Architecture as Code
        +
Governance as Code
        +
GitOps
```

operating model.

---

## 23. Future CI Automation

A future GitLab CI pipeline should automatically validate and render the diagrams.

Target rendering command:

```bash
plantuml -tsvg -o rendered-diagrams docs/99-DIAGRAMS/*.puml
```

The CI pipeline should progressively validate:

- PlantUML syntax
- Successful SVG generation
- Missing rendered diagrams
- Invalid file names
- Broken references
- Duplicate diagram IDs
- Documentation links
- Diagram/source consistency

A future pipeline could follow:

```text
Commit
   ↓
PlantUML Syntax Check
   ↓
Render SVG
   ↓
Validate Outputs
   ↓
Documentation Checks
   ↓
Publish Artifacts
```

---

## 24. Governance Integration

Architecture diagrams are governance artifacts.

They provide visual evidence supporting:

- Architecture decisions
- Security controls
- Data governance
- AI governance
- Infrastructure decisions
- Operational processes
- Disaster recovery
- Risk management
- Technical debt analysis
- SLO design

The relationship is:

```text
Requirement
    ↓
Architecture
    ↓
ADR
    ↓
Implementation
    ↓
Diagram
    ↓
Runtime Evidence
```

Where possible, architecture diagrams should reference stable concepts defined elsewhere in the project rather than inventing parallel terminology.

---

## 25. Documentation Responsibilities

Architecture diagrams answer:

```text
HOW IS THE SYSTEM STRUCTURED?
```

ADRs answer:

```text
WHY WAS THIS DECISION MADE?
```

Operational documentation answers:

```text
HOW DO WE OPERATE IT?
```

Governance documentation answers:

```text
WHAT RULES AND CONTROLS APPLY?
```

Observability answers:

```text
HOW DO WE KNOW IT IS WORKING?
```

Backup and disaster recovery documentation answers:

```text
HOW DO WE RECOVER IT?
```

These documentation domains complement each other and must not be treated as substitutes.

---

## 26. Current Diagram Status

| ID | Diagram | Source | SVG | Status |
|---|---|---:|---:|---|
| 01 | Enterprise Context | ✅ | ✅ | Complete |
| 02 | Enterprise Platform Architecture | ✅ | ✅ | Complete |
| 03 | Infrastructure Architecture | ✅ | ✅ | Complete |
| 04 | Kubernetes Architecture | ✅ | ✅ | Complete |
| 05 | Network Architecture | ✅ | ✅ | Complete |
| 06 | Application Architecture | ✅ | ✅ | Complete |
| 07 | Data Architecture | ✅ | ✅ | Complete |
| 08 | AI Architecture | ✅ | ✅ | Complete |
| 09 | MLOps Architecture | ✅ | ✅ | Complete |
| 10 | DevOps & GitOps Architecture | ✅ | ✅ | Complete |
| 11 | Observability Architecture | ✅ | ✅ | Complete |
| 12 | Security Architecture | ✅ | ✅ | Complete |
| 13 | Governance as Code | ✅ | ✅ | Complete |
| 14 | Backup & Disaster Recovery | ✅ | ✅ | Complete |

---

## 27. Core Architecture Coverage

The current diagram set covers:

```text
Enterprise Context             ✅
Enterprise Platform            ✅
Infrastructure                 ✅
Kubernetes                     ✅
Network                        ✅
Application                    ✅
Data                           ✅
AI                             ✅
MLOps                          ✅
DevOps / GitOps                ✅
Observability                  ✅
Security                       ✅
Governance as Code             ✅
Backup / Disaster Recovery     ✅
```

The core architecture diagram set is therefore complete.

Future diagrams should only be added when they provide a useful architectural viewpoint not already represented by these fourteen diagrams.

---

## 28. Final Architecture Model

The project architecture can be summarized as:

```text
                    BUSINESS
                       │
                       ▼
                  APPLICATIONS
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

Across all layers:

─────────────────────────────────────────────
Security
Observability
DevOps / GitOps
Governance as Code
Backup / Disaster Recovery
─────────────────────────────────────────────
```

The architecture is designed around a controlled, observable and governed platform in which infrastructure, data and AI capabilities are managed through reproducible engineering practices.

---

## 29. Status

**Architecture diagram set:** COMPLETE  
**Diagram source format:** PlantUML  
**Rendered format:** SVG  
**Architecture approach:** Diagrams as Code  
**Governance integration:** Governance as Code  
**Deployment model:** GitOps  
**AI strategy:** Local-first  
**Observability model:** Metrics + Logs + Traces  
**Recovery model:** Backup + Restore + Validation + Evidence

---

**End of Architecture Diagrams README**