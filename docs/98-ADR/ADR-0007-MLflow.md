# ADR-0007 — Adopt MLflow as the Experiment Tracking and Model Registry Platform

**Status:** Accepted
**Date:** 2026-08-21
**Decision Owner:** Bastri Murad
**Domain:** AI / MLOps / Data
**Project:** Enterprise AI Platform
**Related ADRs:** ADR-0001, ADR-0002, ADR-0005, ADR-0006
**Related Technologies:** MLflow, PostgreSQL, MinIO, Airflow, Kubernetes
**Supersedes:** None
**Superseded By:** None

---

# 1. Context

The Enterprise AI Platform requires a standard way to manage the machine-learning lifecycle.

The platform already performs model training and promotion workflows and therefore requires capabilities for:

* Experiment tracking
* Parameter tracking
* Metric tracking
* Artifact tracking
* Model versioning
* Model registry
* Promotion workflows
* Reproducibility
* Comparison between runs
* Auditability

Without a dedicated lifecycle platform, model training would rely on:

* Local files
* Manual naming
* Spreadsheet tracking
* Ad hoc model copies
* Weak version traceability

This would make model governance increasingly difficult.

---

# 2. Problem

The platform needs an authoritative system capable of answering questions such as:

```text
Which model version is currently approved?

Which dataset and parameters produced it?

What metrics were obtained during training?

Which artifact corresponds to the selected model?

Which model version was previously deployed?
```

The solution must integrate with:

* Airflow
* Kubernetes
* PostgreSQL
* Object storage
* Python
* AI workflows
* Governance

---

# 3. Decision

The platform will use **MLflow** as the standard MLOps tracking and model-registry platform.

MLflow is responsible for:

* Experiment tracking
* Run tracking
* Parameters
* Metrics
* Artifacts
* Model versions
* Model registry
* Lifecycle metadata

MLflow is **not** the primary workflow orchestrator and is **not** the primary inference-serving platform.

---

# 4. Separation of Responsibilities

The architecture deliberately separates the major ML responsibilities.

```text
Airflow
   │
   ▼
Workflow Orchestration
   │
   ▼
Training / Evaluation
   │
   ▼
MLflow
   │
   ├── Experiments
   ├── Metrics
   ├── Parameters
   ├── Artifacts
   └── Model Registry
        │
        ▼
Approved Model
        │
        ▼
Serving Platform
```

Airflow controls **when and in what order** ML workflows run.

MLflow records **what happened and which model artifact resulted**.

The inference platform controls **how a model is served**.

---

# 5. Current Implementation

MLflow is already deployed on the Kubernetes platform.

Existing implementation includes:

* MLflow Tracking Server
* PostgreSQL-backed metadata
* MinIO artifact storage
* Kubernetes deployment
* Airflow integration
* Model Registry
* Model promotion workflows

The Iris Random Forest workflow has already produced multiple model versions.

Current state:

```text
IMPLEMENTED
```

---

# 6. Existing Evidence

Existing model lifecycle evidence includes:

```text
Iris Random Forest

v1
v2
v3
...
v7
```

with `v7` promoted to the production lifecycle stage in the current implementation.

This demonstrates that MLflow already acts as the model lifecycle authority.

---

# 7. Alternatives Considered

## Option 1 — MLflow

Advantages:

* Open source
* Mature
* Python-friendly
* Experiment tracking
* Artifact tracking
* Model registry
* Broad framework compatibility
* Simple API
* Strong fit with Airflow
* Can run locally
* Low vendor lock-in

Disadvantages:

* Requires backend database
* Requires artifact storage
* Registry governance must still be designed
* Does not replace a complete AI serving architecture

Selected.

---

## Option 2 — Custom Database and File Storage

Advantages:

* Complete flexibility
* Potentially minimal tooling

Disadvantages:

* Requires custom experiment-tracking implementation
* Requires custom registry
* Increased maintenance
* Weak ecosystem integration
* Reinvents solved functionality

Not selected.

---

## Option 3 — Weights & Biases

Advantages:

* Mature experiment tracking
* Strong visualization
* Rich collaboration

Disadvantages:

* External service dependency
* Potential data-governance concerns
* Cost considerations
* Less aligned with the local sovereign architecture

Not selected for the current platform.

---

## Option 4 — Kubeflow

Advantages:

* Broad Kubernetes-native ML platform
* Pipeline and model-management capabilities
* Powerful ecosystem

Disadvantages:

* Significant platform footprint
* Much greater operational complexity
* Overlaps with Airflow and existing services
* Current requirements do not justify the resource cost

Not selected.

---

# 8. Decision Criteria

The decision considered:

| Criterion                     | Importance |
| ----------------------------- | ---------: |
| Local deployment              |   Critical |
| Experiment tracking           |   Critical |
| Model versioning              |   Critical |
| Model registry                |   Critical |
| Python integration            |       High |
| Airflow integration           |       High |
| Kubernetes compatibility      |       High |
| Resource efficiency           |       High |
| Open source                   |       High |
| AI governance potential       |       High |
| Integrated production serving |     Medium |

MLflow provides the best fit for the current architecture.

---

# 9. Experiment Tracking

Every governed ML training process should record relevant information.

Typical fields include:

```text
Experiment
Run
Parameters
Metrics
Tags
Artifacts
Model
```

Example:

```text
Experiment:
iris-classification

Parameters:
n_estimators=100
max_depth=5

Metrics:
accuracy=0.96
```

This improves reproducibility.

---

# 10. Model Artifacts

Model binaries and related artifacts should be stored through MLflow's artifact architecture rather than manually copied between arbitrary filesystem locations.

Conceptually:

```text
Training
   │
   ▼
MLflow Run
   │
   ├── Parameters
   ├── Metrics
   └── Artifact
          │
          ▼
        MinIO
```

---

# 11. Metadata Backend

MLflow metadata is stored using PostgreSQL.

This includes information such as:

* Experiments
* Runs
* Tags
* Metrics
* Registered models
* Model versions

This creates a dependency on the PostgreSQL platform defined in ADR-0005.

---

# 12. Artifact Storage

MinIO provides the artifact-storage layer.

Architecture:

```text
MLflow
  │
  ├── Metadata → PostgreSQL
  │
  └── Artifacts → MinIO
```

This separates structured metadata from object artifacts.

---

# 13. Model Registry

The MLflow Model Registry provides governed model identity and versioning.

Conceptually:

```text
Model
  │
  ├── Version 1
  ├── Version 2
  ├── Version 3
  └── Version N
```

Each model version can reference its originating training run.

---

# 14. Model Promotion

Model promotion should be an explicit workflow.

Target:

```text
Candidate
   │
   ▼
Evaluation
   │
   ▼
Governance Checks
   │
   ▼
Approved
   │
   ▼
Production
```

Promotion should not rely on manually copying a model file.

---

# 15. Airflow Integration

Airflow can orchestrate:

```text
Training
   │
   ▼
Log Run to MLflow
   │
   ▼
Evaluation
   │
   ▼
Register Model
   │
   ▼
Promotion Decision
```

This combination provides strong MLOps separation of concerns.

---

# 16. Promotion Governance

A production promotion should progressively require evidence such as:

* Required metrics
* Evaluation success
* Model metadata
* Model owner
* Risk classification
* Security checks
* Approval where required

These controls support **AI Governance as Code**.

---

# 17. AI Governance as Code

MLflow can become one enforcement and evidence point for AI Governance as Code.

Conceptually:

```text
Model Candidate
      │
      ▼
MLflow Metadata
      │
      ▼
Governance Rules
      │
      ├── Required Metrics
      ├── Required Tags
      ├── Owner
      ├── Risk Level
      └── Approval
      │
      ▼
Promotion Allowed / Blocked
```

This is a target-state capability.

---

# 18. Required Model Metadata

Future governed model registrations may require fields such as:

```text
owner
business_use_case
model_type
training_dataset
risk_level
evaluation_status
approval_status
```

These should be machine-readable.

---

# 19. Reproducibility

A model should ideally be reproducible from:

```text
Source Code
+
Dataset Version
+
Parameters
+
Environment
+
Run Metadata
```

MLflow provides part of this evidence.

Git and data-governance systems provide the remaining context.

---

# 20. Source-Code Traceability

MLflow runs should eventually include references to:

* Git repository
* Commit SHA
* Branch/tag
* Pipeline execution

This enables:

```text
Model Version
   │
   ▼
MLflow Run
   │
   ▼
Git Commit
```

---

# 21. Dataset Traceability

A training run should progressively reference the dataset or data version used.

This may be implemented through:

* OpenMetadata references
* Dataset IDs
* Snapshot IDs
* Version tags

Model reproducibility depends on data traceability as much as code traceability.

---

# 22. Model Serving Separation

MLflow is not selected as the universal production serving layer.

The architecture separates:

```text
MLflow
→ Model Lifecycle

Serving Platform
→ Runtime Inference
```

Serving may be performed through:

* FastAPI
* Ollama
* Dedicated model service
* Future AI Gateway

depending on model type.

---

# 23. Deployment Mapping

A production service should identify which model version it serves.

Example:

```text
ai-classifier
model=iris-random-forest
version=7
```

This metadata should be observable.

---

# 24. Rollback

Model registry versioning enables rollback to a previously approved model.

Example:

```text
v7
  │
  ▼
Regression Detected
  │
  ▼
Promote / redeploy v6
```

Rollback must still be validated through the deployment system.

---

# 25. Model Promotion Is Not Deployment

The architecture distinguishes:

```text
Model Approved
```

from:

```text
Model Deployed
```

A model may be approved in MLflow but not yet active in production.

This distinction should remain explicit.

---

# 26. Model Lifecycle Status

Model status should eventually align with governance terminology.

Potential states:

```text
Candidate
Validated
Approved
Production
Deprecated
Rejected
```

The exact implementation should reflect the MLflow version and governance workflow in use.

---

# 27. Model Deprecation

Old model versions should normally remain traceable even after they are no longer approved for new deployments.

Deleting historical model metadata removes useful audit evidence.

---

# 28. Security Consequences

MLflow exposes valuable information and artifacts.

Controls should include:

* Authentication where applicable
* Restricted network exposure
* Kubernetes RBAC
* Storage credential protection
* Database credential protection
* TLS
* Access control

MLflow should primarily remain an internal service.

---

# 29. Artifact Security

Model artifacts may represent valuable intellectual property.

Artifact storage should therefore restrict:

* Unauthorized reads
* Unauthorized writes
* Uncontrolled deletion

Storage credentials must be protected.

---

# 30. Model Integrity

Future maturity may include:

* Artifact checksums
* Model signing
* Provenance
* SBOM for model environments

These capabilities should only be introduced where operationally valuable.

---

# 31. Observability

MLflow itself should be monitored for:

* Availability
* API latency
* API failures
* PostgreSQL connectivity
* MinIO connectivity
* Storage usage

MLflow service health is separate from model quality.

---

# 32. Model Quality Monitoring

Production model quality may include:

* Prediction performance
* Drift
* Business outcome
* Error rate

This information may be stored or referenced through MLflow, but operational production monitoring requires dedicated observability.

---

# 33. AI Quality vs Service Reliability

The architecture separates:

```text
MLflow Experiment Metric
→ Model quality during evaluation

Prometheus Metric
→ Runtime service reliability
```

Both are required for mature MLOps.

---

# 34. Backup

MLflow recovery requires protection of:

```text
PostgreSQL Metadata
+
MinIO Artifacts
+
Configuration
```

Git should preserve deployment configuration.

---

# 35. Disaster Recovery

Conceptual recovery:

```text
Kubernetes
    │
    ▼
PostgreSQL
    │
    ▼
MinIO
    │
    ▼
MLflow
    │
    ▼
Registry Validation
```

Both metadata and artifact consistency are necessary.

---

# 36. Recovery Validation

After restore:

* MLflow UI/API available
* Experiments visible
* Runs visible
* Registered models visible
* Model versions correct
* Artifacts retrievable

A healthy MLflow Pod alone does not prove full recovery.

---

# 37. Resource Governance

MLflow itself does not require large GPU resources.

The primary resource concerns are:

* Metadata database
* Artifact storage
* Tracking requests
* Storage growth

Training workloads remain separate.

---

# 38. Artifact Retention

Model artifact retention should reflect governance requirements.

Not every failed experimental artifact needs indefinite retention.

However production and decision-relevant artifacts may require longer retention.

Retention policy should eventually distinguish:

* Experimental
* Candidate
* Approved
* Production

---

# 39. Model Registry as Governance Evidence

The registry provides evidence for questions such as:

* What models exist?
* Which versions exist?
* Which run created a version?
* Which model is approved?
* Which model was previously used?

This makes MLflow a significant AI governance source.

---

# 40. Governance Integration

MLflow should eventually integrate conceptually with:

```text
Git
OpenMetadata
Airflow
Risk Registry
AI Asset Registry
Observability
```

Example:

```text
MLflow Model Version
     │
     ├── Git Commit
     ├── Dataset
     ├── AI Risk
     ├── Evaluation
     └── Deployment
```

---

# 41. Prompt Governance

MLflow may store some prompt-related experimentation metadata, but it is not automatically selected as the sole Prompt Registry.

Prompt Governance may use:

* Git
* Dedicated structured definitions
* MLflow references

The final pattern depends on future AI architecture needs.

---

# 42. LLM Lifecycle

MLflow may also support parts of LLM evaluation and experiment tracking.

However local foundation models served by Ollama have a somewhat different lifecycle from custom-trained predictive models.

The architecture should not force every AI asset into an identical lifecycle.

---

# 43. When MLflow Should NOT Be Used

MLflow should not replace:

* Airflow orchestration
* Git source control
* OpenMetadata data catalog
* Prometheus
* Production API serving by default
* General object storage management

Each platform retains a distinct responsibility.

---

# 44. Technical Debt Consideration

MLflow is not currently technical debt.

Potential future debt could include:

* Models without owners
* Runs without source traceability
* Artifacts without retention policy
* Manual model promotion
* Missing evaluation evidence

These are governance gaps rather than reasons to replace MLflow.

---

# 45. Technology Governance Status

Recommended classification:

```text
Technology: MLflow
Category: MLOps
Lifecycle: ADOPT
```

---

# 46. Risks

## Risk — Metadata Database Loss

Mitigation:

* PostgreSQL backup
* Restore validation

## Risk — Artifact Loss

Mitigation:

* MinIO backup/recovery
* Artifact integrity checks

## Risk — Uncontrolled Model Promotion

Mitigation:

* Airflow workflow
* Governance gates
* Required metadata

## Risk — Untraceable Model

Mitigation:

* Git references
* Dataset references
* MLflow run metadata

---

# 47. Positive Consequences

The platform gains:

* Standard experiment tracking
* Model versioning
* Reproducibility
* Registry
* Promotion traceability
* Centralized artifacts
* Strong foundation for AI Governance as Code

---

# 48. Negative Consequences

The platform accepts:

* MLflow service operations
* PostgreSQL dependency
* MinIO dependency
* Registry governance effort
* Artifact lifecycle management

These costs are justified by the lifecycle capabilities gained.

---

# 49. Success Criteria

The MLflow decision remains successful while:

* Training runs are traceable
* Important experiments record metadata
* Model versions are governed
* Production model lineage can be reconstructed
* Artifacts are recoverable
* Promotion workflows remain controlled

---

# 50. Review Triggers

Review this ADR if:

* MLflow no longer supports required model lifecycle patterns
* LLM/agent lifecycle requirements significantly exceed current capabilities
* Artifact scale changes substantially
* A replacement provides major measurable governance value
* MLflow support or lifecycle changes materially

---

# 51. Governance as Code Metadata

Future machine-readable representation:

```yaml
id: ADR-0007
title: Adopt MLflow as Experiment Tracking and Model Registry Platform
status: accepted

domain:
  - ai
  - mlops
  - data

technologies:
  - mlflow
  - postgresql
  - minio

owner: mlops
implementation_status: implemented

related_adrs:
  - ADR-0001
  - ADR-0002
  - ADR-0005
  - ADR-0006

alternatives:
  - custom-tracking
  - weights-and-biases
  - kubeflow

supersedes: null
superseded_by: null
```

---

# 52. Related Documents

* ADR-0001-Kubernetes
* ADR-0002-ArgoCD-GitOps
* ADR-0005-PostgreSQL
* ADR-0006-Airflow
* MLOps Architecture
* AI Architecture
* Model Governance
* AI Governance
* OpenMetadata Architecture
* Backup and Restore
* Disaster Recovery
* Technology Governance
