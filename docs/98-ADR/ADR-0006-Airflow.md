# ADR-0006 — Adopt Apache Airflow as the Primary Workflow Orchestration Platform

**Status:** Accepted
**Date:** 2026-08-21
**Decision Owner:** Bastri Murad
**Domain:** Data / MLOps / Platform
**Project:** Enterprise AI Platform
**Related ADRs:** ADR-0001, ADR-0002, ADR-0005
**Related Technologies:** Apache Airflow, Kubernetes, PostgreSQL, GitLab, Argo CD, dbt, MLflow
**Supersedes:** None
**Superseded By:** None

---

# 1. Context

The Enterprise AI Platform requires a workflow orchestration capability for scheduled and dependency-driven processes.

Typical workloads include:

* Data ingestion
* ETL / ELT
* dbt execution
* Data quality validation
* Metadata ingestion
* ML training
* Model validation
* Model promotion
* Batch AI workflows
* Platform validation jobs

The platform already operates multiple workflows where execution order, retries, scheduling, observability, and failure handling are required.

Simple cron jobs or manually executed scripts would become increasingly difficult to govern as the platform grows.

---

# 2. Problem

The platform needs a centralized orchestration layer capable of managing:

```text
Schedule
   │
   ▼
Dependencies
   │
   ▼
Execution
   │
   ▼
Retries
   │
   ▼
Validation
   │
   ▼
Observability
```

The orchestration platform must integrate with:

* Kubernetes
* PostgreSQL
* dbt
* MLflow
* OpenMetadata
* Git
* Observability

It must also support workflow definitions as code.

---

# 3. Decision

The platform will use **Apache Airflow** as the primary workflow orchestrator for batch-oriented data, ML, metadata, and platform workflows.

Airflow is responsible for:

* Scheduling
* Dependency management
* Workflow state
* Retry behavior
* Execution coordination
* Task observability

Airflow is **not** the primary storage engine or transformation engine.

---

# 4. Separation of Responsibilities

The architecture deliberately separates orchestration from execution responsibilities.

```text
Airflow
   │
   ├── Orchestrates
   │
   ▼
Tasks
   │
   ├── PostgreSQL
   ├── dbt
   ├── MLflow
   ├── OpenMetadata
   └── External Services
```

Examples:

```text
Airflow
→ controls when dbt runs

dbt
→ defines SQL transformations
```

and:

```text
Airflow
→ orchestrates ML training

MLflow
→ tracks experiments and models
```

This separation reduces coupling.

---

# 5. Current Implementation

Airflow is already deployed on Kubernetes.

Current architecture includes:

* Helm deployment
* KubernetesExecutor
* Kubernetes namespace
* Web interface
* Git-managed DAGs
* Multiple operational DAGs
* Integration with data and ML workflows
* Observability

Current status:

```text
IMPLEMENTED
```

---

# 6. Current Workflow Examples

Existing workflows include:

```text
platform_validation
mlflow_iris_training
mlflow_iris_promote
retail_analytics_etl
```

These demonstrate orchestration across:

* Platform validation
* Machine learning
* Data engineering

---

# 7. Alternatives Considered

## Option 1 — Apache Airflow

Advantages:

* Mature
* Widely used in Data Engineering
* Python-based DAGs
* Strong scheduling
* Strong dependency modeling
* Retry handling
* Large integration ecosystem
* Good Kubernetes support
* Good observability
* Strong alignment with Data / ML workflows

Disadvantages:

* Operationally heavier than cron
* Metadata database required
* Not designed for every real-time/event-driven workload
* DAG complexity can grow if poorly governed

Selected.

---

## Option 2 — Cron / Kubernetes CronJob

Advantages:

* Simple
* Lightweight
* Kubernetes-native
* Low overhead

Disadvantages:

* Weak dependency management
* Weak workflow visualization
* Limited retry orchestration
* Difficult multi-step workflows
* Poor cross-job lineage

Suitable for simple isolated jobs, but not the primary workflow platform.

---

## Option 3 — Prefect

Advantages:

* Modern Python workflow experience
* Good developer ergonomics
* Dynamic workflows

Disadvantages:

* Existing investment already uses Airflow
* Migration provides insufficient current value
* Would add unnecessary platform duplication

Not selected.

---

## Option 4 — Dagster

Advantages:

* Strong data asset model
* Good modern data-engineering abstractions
* Good lineage concepts

Disadvantages:

* Another orchestration platform to operate
* Existing Airflow implementation already satisfies current requirements

Not selected.

---

## Option 5 — Argo Workflows

Advantages:

* Kubernetes-native
* Strong container workflow execution
* Good for Kubernetes jobs

Disadvantages:

* Less aligned with the current Data Engineering workflow model
* Would partially overlap with Airflow
* Adds another orchestration technology

Not selected as the primary data orchestrator.

---

# 8. Decision Criteria

The decision considered:

| Criterion                   |    Importance |
| --------------------------- | ------------: |
| Data workflow orchestration |      Critical |
| Scheduling                  |      Critical |
| Dependency management       |      Critical |
| Python integration          |          High |
| Kubernetes integration      |          High |
| Retry handling              |          High |
| Observability               |          High |
| ML workflow compatibility   |          High |
| Resource efficiency         |        Medium |
| Event streaming             | Low currently |

Airflow provides the best current fit.

---

# 9. DAGs as Code

Airflow workflows should be defined as code.

Preferred model:

```text
Git
 ↓
DAG Repository
 ↓
Airflow
 ↓
Workflow Execution
```

Benefits include:

* Version control
* Review
* History
* Reproducibility
* Rollback

Manual DAG creation in the UI should not become the production standard.

---

# 10. DAG Ownership

Critical DAGs should define:

* Owner
* Purpose
* Schedule
* Dependencies
* Failure behavior
* Data outputs
* Runbook

This supports Governance as Code.

---

# 11. KubernetesExecutor

The current deployment uses **KubernetesExecutor**.

Architecture:

```text
Airflow Scheduler
       │
       ▼
Task Requested
       │
       ▼
Temporary Kubernetes Pod
       │
       ▼
Task Executes
       │
       ▼
Pod Completes
```

This aligns task execution with the Kubernetes platform.

---

# 12. KubernetesExecutor Benefits

Benefits include:

* Task isolation
* Kubernetes-native scheduling
* Per-task resources
* Automatic Pod lifecycle
* Reduced long-running worker footprint
* Better workload separation

This model is well suited to the current Kubernetes architecture.

---

# 13. KubernetesExecutor Consequences

The model increases dependency on:

* Kubernetes API
* Scheduler
* Container images
* Pod startup
* CNI
* DNS

A Kubernetes failure can therefore affect workflow execution.

This dependency is accepted because Kubernetes is already the primary runtime platform.

---

# 14. Resource Governance

Airflow tasks should define realistic resource requirements where possible.

Example:

```text
ETL Task
→ CPU / RAM

ML Task
→ CPU / RAM / possibly GPU

Metadata Task
→ lower resources
```

Uncontrolled task resources can create cluster contention.

---

# 15. GPU Workflows

GPU-intensive workflows should be scheduled carefully.

The platform has:

```text
2 × GTX 1080
8 GB VRAM each
```

Airflow should orchestrate GPU tasks only when appropriate.

It should not create uncontrolled simultaneous GPU workloads.

---

# 16. Idempotency

Airflow tasks should be designed to be idempotent where practical.

Meaning:

```text
Task executed once
≈
Task safely executed again
```

This is important because retries may execute a task more than once.

---

# 17. Retry Strategy

Retries should be used for transient failures.

Examples:

* Temporary API failure
* Temporary network failure
* Temporary database connection failure

Retries should not hide deterministic bugs.

Bad pattern:

```text
Retry 100 times
```

for a permanently invalid SQL query.

---

# 18. Retry Governance

Each critical DAG should define:

* Retry count
* Retry delay
* Timeout
* Failure behavior

Retry configuration should reflect the dependency being called.

---

# 19. Timeouts

Tasks should avoid unlimited execution time.

Timeouts help detect:

* Hung jobs
* Broken connections
* Infinite loops
* External-service failure

Long-running AI or data workloads may require larger limits than simple operational tasks.

---

# 20. Failure Behavior

Failures should be explicit.

Possible outcomes:

```text
Retry
Fail
Skip
Trigger Compensation
Alert
```

The correct behavior depends on business impact.

---

# 21. Data Pipeline Architecture

Typical pipeline:

```text
Source
  │
  ▼
Airflow Extraction
  │
  ▼
PostgreSQL Raw
  │
  ▼
dbt Staging
  │
  ▼
Warehouse
  │
  ▼
Analytics
  │
  ▼
Data Quality
```

Airflow coordinates the stages but does not replace their specialized tooling.

---

# 22. Data Quality Integration

Data-quality validation should be orchestrated as part of critical data workflows.

A DAG should not necessarily be considered successful merely because ingestion completed.

Example:

```text
Load
 ↓
Transform
 ↓
Data Quality
 ↓
Publish
```

Failure of critical data-quality controls should affect workflow status.

---

# 23. MLflow Integration

Airflow may orchestrate the ML lifecycle:

```text
Dataset
  │
  ▼
Training
  │
  ▼
MLflow Tracking
  │
  ▼
Evaluation
  │
  ▼
Model Registry
  │
  ▼
Promotion
```

Airflow controls workflow sequence.

MLflow remains authoritative for ML lifecycle metadata.

---

# 24. OpenMetadata Integration

Metadata ingestion jobs may be orchestrated through Airflow.

Examples:

* PostgreSQL ingestion
* dbt ingestion
* Metadata workflows
* Profiler execution

This connects operational orchestration with Data Governance.

---

# 25. Scheduling

Schedules should reflect business and technical requirements.

Examples:

```text
Hourly
Daily
Weekly
Eventually ad hoc / triggered
```

Do not schedule jobs more frequently than required.

Excessive schedules waste platform resources.

---

# 26. Catchup

Airflow catchup behavior should be intentionally configured.

For some pipelines:

```text
catchup = false
```

may be appropriate.

For others, missed historical runs may be required.

The setting must reflect data semantics.

---

# 27. Backfills

Backfills should be controlled because they can create significant resource load.

Before running a large backfill, consider:

* Database capacity
* Kubernetes capacity
* API limits
* GPU availability
* Downstream impact

Large backfills should be treated as operational changes.

---

# 28. Concurrency

Airflow concurrency must be governed.

Controls may include:

* DAG concurrency
* Task concurrency
* Pool limits
* Kubernetes resource controls

This protects shared platform capacity.

---

# 29. Airflow Pools

Pools may be used to limit scarce resources.

Examples:

```text
gpu_pool
external_api_pool
database_heavy_pool
```

This is especially valuable for the fixed-resource platform.

---

# 30. Secrets

Airflow connections and credentials must not be hard-coded into DAGs.

Preferred sources include:

* Kubernetes Secrets
* Approved secret-management mechanisms
* Airflow Connections populated securely

Git should contain configuration references, not secret values.

---

# 31. Observability

Airflow should expose visibility into:

* DAG success
* DAG failure
* Task failure
* Retry count
* Duration
* Scheduler health
* Queue state

Critical workflow failures should trigger alerts.

---

# 32. Logging

Task logs should be centralized through the platform logging architecture.

This supports:

```text
Failed task
   │
   ▼
Airflow UI
   │
   ▼
Central logs
   │
   ▼
Root Cause Analysis
```

---

# 33. Data Freshness

For critical pipelines, data freshness is more important than simply checking the Scheduler.

Example:

```text
Scheduler healthy
DAG healthy

but

Last successful data refresh = 12 hours ago
```

The platform should therefore monitor output freshness.

---

# 34. SLI / SLO

Potential Airflow-related SLI:

```text
Successful critical DAG runs
----------------------------
Expected critical DAG runs
```

Potential target:

```text
99%
```

This remains a proposed objective until operationally validated.

---

# 35. Alerting

Potential alerts include:

* Critical DAG failed
* Scheduler unavailable
* Critical task retries exhausted
* Data freshness breached
* Pipeline duration abnormally high

Alerts should remain business-aware.

---

# 36. Airflow Database

Airflow depends on a metadata database.

This database contains:

* DAG run state
* Task state
* Scheduler metadata
* Connection metadata depending on configuration

Its recovery must be considered in backup planning.

---

# 37. Backup

Airflow recovery depends on several assets:

```text
DAGs
+
Configuration
+
Metadata Database
+
Connections / Secrets
```

DAGs and configuration should primarily recover from Git.

---

# 38. Disaster Recovery

Recovery flow:

```text
Kubernetes
   │
   ▼
PostgreSQL / Metadata DB
   │
   ▼
Airflow Deployment
   │
   ▼
DAG Repository
   │
   ▼
Secrets / Connections
   │
   ▼
Validation
```

---

# 39. Recovery Validation

After recovery:

* Scheduler operational
* Web UI available
* DAGs loaded
* Metadata database reachable
* Known DAG can execute
* Logs available
* Alerts operational

---

# 40. Security Consequences

Airflow has significant execution capability.

It can potentially:

* Call databases
* Call APIs
* Run scripts
* Create Kubernetes tasks

Therefore controls include:

* RBAC
* Authentication
* Least-privilege credentials
* Secure DAG repository
* Restricted Kubernetes ServiceAccount

---

# 41. Code Execution Risk

A malicious or incorrect DAG can execute arbitrary logic with its assigned permissions.

Therefore DAG repositories must use:

* Protected branches
* Review
* CI validation
* Controlled ownership

DAGs are production code.

---

# 42. GitOps Relationship

Airflow platform configuration should be GitOps-managed.

DAG code should also remain Git-managed.

Conceptually:

```text
Platform Config
→ GitOps

Workflow Logic
→ DAG Git Repository
```

The exact repositories may remain separate.

---

# 43. CI/CD Governance

Future DAG CI may validate:

* Python syntax
* DAG import
* Tests
* Naming
* Ownership
* Security patterns

This supports Governance as Code.

---

# 44. Airflow as Governance Execution Engine

Airflow may execute governance workflows where scheduled orchestration is appropriate.

Examples:

* Metadata ingestion
* Data-quality jobs
* Governance synchronization
* Evidence generation

However it should not become the only Governance as Code engine.

CI/CD, Kubernetes policy engines, GitOps, and OpenMetadata retain their own roles.

---

# 45. When Airflow Should NOT Be Used

Airflow should not automatically be used for every automation.

Avoid Airflow for:

* Simple deployment reconciliation
* Real-time request routing
* Kubernetes desired-state management
* Very simple one-off shell automation
* High-frequency event streaming
* Application request processing

Use the appropriate tool for each responsibility.

---

# 46. Real-Time Workloads

Airflow is primarily batch/workflow oriented.

If the platform later requires true streaming or event-driven processing, alternatives may include:

* Kafka-based processing
* Dedicated event consumers
* Stream-processing technology

That would require separate architecture evaluation.

---

# 47. Technical Debt Consideration

Airflow is not currently technical debt.

It satisfies current data and ML orchestration needs.

Debt may arise if:

* DAGs become excessively complex
* Business logic is embedded directly into orchestration
* Workflows are not version controlled
* Airflow is used for unsuitable real-time workloads

---

# 48. Technology Governance Status

Recommended classification:

```text
Technology: Apache Airflow
Category: Workflow Orchestration
Lifecycle: ADOPT
```

---

# 49. Risks

## Risk — Scheduler Failure

Mitigation:

* Kubernetes monitoring
* Health checks
* Recovery procedures

## Risk — DAG Failure

Mitigation:

* Retries
* Tests
* Alerting
* Runbooks

## Risk — Workflow Overconsumes Cluster Resources

Mitigation:

* Kubernetes resources
* Pools
* Concurrency controls

## Risk — Malicious / Incorrect DAG Code

Mitigation:

* Git review
* Protected repository
* Least privilege

---

# 50. Positive Consequences

The platform gains:

* Centralized workflow orchestration
* Repeatable scheduling
* Dependency management
* Retry handling
* Operational visibility
* Better data/ML workflow governance
* Python-based extensibility
* Kubernetes-native task execution

---

# 51. Negative Consequences

The platform accepts:

* Airflow operational complexity
* Metadata database dependency
* Scheduler dependency
* DAG governance requirements
* Additional resource consumption

These costs are considered justified.

---

# 52. Success Criteria

The decision remains successful while:

* Critical workflows execute reliably
* DAGs remain maintainable
* Retry behavior is controlled
* Data freshness remains observable
* Kubernetes resources remain manageable
* Airflow continues to satisfy batch orchestration requirements

---

# 53. Review Triggers

Review this ADR if:

* Real-time/event workloads dominate
* Airflow becomes operationally excessive
* DAG complexity becomes unmanageable
* Another orchestrator provides substantial demonstrated value
* Kubernetes execution architecture changes materially

---

# 54. Governance as Code Metadata

Future representation:

```yaml
id: ADR-0006
title: Adopt Apache Airflow as Primary Workflow Orchestration Platform
status: accepted

domain:
  - data
  - mlops
  - platform

technologies:
  - airflow
  - kubernetes

owner: data-platform
implementation_status: implemented

alternatives:
  - kubernetes-cronjob
  - prefect
  - dagster
  - argo-workflows

related_adrs:
  - ADR-0001
  - ADR-0002
  - ADR-0005

supersedes: null
superseded_by: null
```

---

# 55. Related Documents

* ADR-0001-Kubernetes
* ADR-0002-ArgoCD-GitOps
* ADR-0005-PostgreSQL
* Data Architecture
* Data Pipeline Architecture
* MLOps Architecture
* MLflow Architecture
* OpenMetadata Architecture
* Data Quality
* Observability Architecture
* Backup and Restore
* Disaster Recovery
* Technology Governance
