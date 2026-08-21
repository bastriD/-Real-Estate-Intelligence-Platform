# ADR-0013 — Adopt a Layered Data Architecture with Airflow, dbt, PostgreSQL, Data Quality, and OpenMetadata

**Status:** Accepted
**Date:** 2026-08-21
**Decision Owner:** Bastri Murad
**Domain:** Data / Analytics / Governance
**Project:** Enterprise AI Platform
**Related ADRs:** ADR-0005, ADR-0006, ADR-0008, ADR-0012
**Related Technologies:** PostgreSQL, Airflow, dbt, OpenMetadata, GitLab
**Supersedes:** None
**Superseded By:** None

---

# 1. Context

The Enterprise AI Platform requires a coherent data architecture capable of supporting:

* Data ingestion
* Data transformation
* Analytical workloads
* Reporting
* Data Quality
* Metadata
* Lineage
* Governance
* AI consumption
* Future RAG and decision-support workloads

The platform already implements a working analytical data platform using PostgreSQL schemas representing different stages of data processing.

Current logical layers include:

```text id="da01"
raw
staging
warehouse
analytics
```

The platform also uses:

* Airflow for orchestration
* dbt for transformation
* OpenMetadata for governance
* Data Quality controls
* Git for version control

The architecture therefore needs to formalize these choices as a consistent enterprise data pattern.

---

# 2. Problem

Without a layered data architecture, data processing can quickly degrade into:

* Direct source-to-report queries
* Manual transformations
* Uncontrolled SQL
* Duplicate business logic
* Poor lineage
* Weak Data Quality
* Mixed OLTP and analytics concerns
* Difficult reproducibility
* Weak governance

The platform requires a standard model that separates responsibilities and keeps transformation logic traceable.

---

# 3. Decision

The platform will adopt a **layered analytical data architecture** based on:

```text id="da02"
Sources
   │
   ▼
raw
   │
   ▼
staging
   │
   ▼
warehouse
   │
   ▼
analytics
```

The responsibilities are separated as follows:

* **PostgreSQL** provides relational persistence
* **Airflow** orchestrates workflow execution
* **dbt** manages SQL transformations and tests
* **OpenMetadata** provides metadata, lineage, ownership, and governance
* **Data Quality controls** validate reliability
* **GitLab/Git** provides versioning and CI

This architecture becomes the default pattern for structured analytical workloads.

---

# 4. Architecture Principle

The platform deliberately separates:

```text id="da03"
Storage
≠
Orchestration
≠
Transformation
≠
Governance
```

Each capability is assigned to a specialized tool.

This avoids a monolithic data platform design.

---

# 5. High-Level Architecture

```text id="da04"
Operational Sources
       │
       ▼
     Airflow
       │
       ▼
┌─────────────────┐
│ PostgreSQL      │
│                 │
│ raw             │
│   ↓             │
│ staging         │
│   ↓             │
│ warehouse       │
│   ↓             │
│ analytics       │
└────────┬────────┘
         │
         ▼
        dbt
         │
         ▼
Data Quality / Metadata
         │
         ▼
    OpenMetadata
```

---

# 6. Current Implementation

The layered architecture is already operational in the current data platform.

Existing schemas include:

```text id="da05"
raw
staging
warehouse
analytics
```

Current implemented capabilities include:

* Ingestion
* Transformation
* Analytical views
* Data Quality tests
* Airflow orchestration
* dbt models
* OpenMetadata ingestion
* Profiling
* Lineage

Current state:

```text id="da06"
IMPLEMENTED
```

---

# 7. Raw Layer

The `raw` layer preserves source-oriented data with minimal transformation.

Purpose:

* Capture source data
* Preserve traceability
* Support reprocessing
* Avoid premature business logic

Typical characteristics:

```text id="da07"
Source-oriented
Minimal transformation
Technical timestamps
Ingestion metadata
```

---

# 8. Raw Layer Rules

The raw layer should avoid unnecessary business transformation.

Acceptable operations may include:

* Technical normalization
* Ingestion timestamp
* Source identifier
* Load identifier

Business calculations belong later in the pipeline.

---

# 9. Staging Layer

The `staging` layer standardizes and cleans raw data.

Typical responsibilities:

* Type normalization
* Naming normalization
* Null handling
* Deduplication
* Data cleansing
* Basic validation

The staging layer creates consistent technical representations for downstream modeling.

---

# 10. Warehouse Layer

The `warehouse` layer contains integrated business-oriented models.

Responsibilities may include:

* Facts
* Dimensions
* Business keys
* Historical modeling
* Conformed entities

Example:

```text id="da08"
dim_customer
dim_product
fact_sales
```

The exact modeling pattern should reflect business requirements.

---

# 11. Analytics Layer

The `analytics` layer exposes consumer-oriented datasets.

Examples include:

* Revenue by category
* Customer revenue
* Top customers
* Order status summaries
* Payment status summaries

This layer should be optimized for consumption rather than source fidelity.

---

# 12. Existing Analytical Views

Current examples include:

```text id="da09"
customer_revenue
top_customers
revenue_by_category
payment_status_summary
order_status_summary
```

These demonstrate the intended analytics-layer role.

---

# 13. dbt Responsibility

dbt is responsible for transformation logic.

Preferred model:

```text id="da10"
SQL Transformation
       │
       ▼
dbt Model
       │
       ▼
Git
       │
       ▼
Versioned Transformation
```

Business logic should not be hidden inside manually executed SQL scripts.

---

# 14. dbt Benefits

dbt provides:

* SQL transformation as code
* Dependency graph
* Tests
* Documentation
* Model lineage
* Reproducibility

This complements Airflow rather than replacing it.

---

# 15. Airflow Responsibility

Airflow orchestrates when transformations run.

Example:

```text id="da11"
Ingest
  │
  ▼
dbt staging
  │
  ▼
dbt warehouse
  │
  ▼
Data Quality
  │
  ▼
Publish
```

Airflow controls the workflow.

dbt controls the transformation logic.

---

# 16. Why Separate Airflow and dbt

The separation prevents orchestration code from becoming the location of all data logic.

Bad pattern:

```text id="da12"
Airflow DAG
├── 500 lines SQL
├── Business rules
└── Transformations
```

Preferred:

```text id="da13"
Airflow DAG
→ invokes dbt

dbt
→ owns SQL transformation
```

This improves maintainability.

---

# 17. OLTP and OLAP Separation

The architecture distinguishes between:

```text id="da14"
OLTP
→ Operational transactions

OLAP
→ Analytical workloads
```

This distinction applies even when both are currently implemented on PostgreSQL.

The technology may be shared.

The workload and data model responsibilities remain separate.

---

# 18. Current Scale

At the current platform scale, PostgreSQL is capable of supporting both:

* Moderate transactional workloads
* Analytical workloads

This avoids introducing a second data engine prematurely.

---

# 19. Future Scale Trigger

A separate analytical technology should only be evaluated if evidence shows PostgreSQL no longer meets requirements.

Possible triggers include:

* Significant data-volume increase
* Query performance limitations
* High concurrent analytical demand
* Columnar-storage requirement
* Distributed processing requirement

A separate ADR would be required.

---

# 20. Data Quality

Data Quality is a first-class architecture capability.

The pipeline should validate data before treating analytical outputs as reliable.

Potential controls include:

* Not null
* Unique
* Referential integrity
* Accepted values
* Freshness
* Row count
* Schema expectations

---

# 21. Existing Data Quality Evidence

The existing platform has already executed a comprehensive suite of data-quality checks successfully.

This demonstrates that quality validation is implemented as part of the platform rather than planned only as future work.

---

# 22. Data Quality Failure

A technically successful load should not automatically mean the data pipeline is healthy.

Example:

```text id="da15"
Pipeline completed
      │
      ▼
Quality checks failed
      │
      ▼
Dataset = degraded
```

This is an important reliability principle.

---

# 23. Data Quality as Code

Quality definitions should remain version controlled.

Target model:

```text id="da16"
Git
 ↓
Quality Rule
 ↓
Execution
 ↓
Result
 ↓
Governance Evidence
```

This supports Data Governance as Code.

---

# 24. Data Freshness

Critical analytical datasets should define expected refresh behavior.

Example:

```text id="da17"
Expected refresh:
Every 6 hours

Actual age:
9 hours

Status:
Degraded
```

Data freshness is a first-class reliability indicator.

---

# 25. OpenMetadata Integration

OpenMetadata provides the governance layer.

It catalogs:

* Schemas
* Tables
* Columns
* Pipelines
* dbt models
* Lineage
* Data Quality
* Ownership

This creates a central view of the data platform.

---

# 26. Data Lineage

The target lineage model is:

```text id="da18"
Source
   │
   ▼
Raw Table
   │
   ▼
Staging Model
   │
   ▼
Warehouse Model
   │
   ▼
Analytics View
   │
   ▼
Consumer
```

This improves traceability and impact analysis.

---

# 27. Data Ownership

Critical data assets should have owners.

Ownership should eventually be represented in machine-readable governance definitions and synchronized to OpenMetadata.

Unowned critical datasets represent a governance gap.

---

# 28. Business Glossary

Business terms should be separated from technical schema names.

Example:

```text id="da19"
Technical:
customer_revenue

Business Term:
Customer Revenue
```

OpenMetadata glossary and repository documentation should remain aligned.

---

# 29. Data Classification

Data should progressively be classified according to sensitivity and business importance.

Possible examples:

```text id="da20"
Public
Internal
Confidential
Personal
Sensitive
Critical
```

Classification supports:

* Access control
* Retention
* GDPR
* AI governance

---

# 30. GDPR Integration

Personal data handled by the data platform must align with:

* GDPR processing records
* Retention
* Access controls
* Purpose limitation
* Data minimization

The data architecture does not override privacy governance.

---

# 31. Data Contracts

Future maturity may introduce Data Contracts.

A contract may define:

```text id="da21"
Dataset
Owner
Schema
Freshness
Quality
Compatibility
Consumers
```

Data Contracts can strengthen producer/consumer relationships.

---

# 32. Schema Evolution

Schema changes should be controlled.

Potential impacts include:

* dbt
* Airflow
* Applications
* OpenMetadata
* Data Quality
* BI/reporting
* AI workflows

Destructive schema changes require careful migration.

---

# 33. Backward Compatibility

Where feasible, schema evolution should preserve compatibility for dependent consumers.

A column removal may impact multiple layers.

Lineage should assist impact analysis.

---

# 34. Data Pipeline Idempotency

Pipeline operations should be idempotent where practical.

This is important because:

* Airflow retries
* Backfills
* Recovery

may repeat processing.

---

# 35. Incremental Processing

Where data volumes grow, incremental processing may be preferred over full reloads.

However the architecture should remain simple until data scale justifies additional complexity.

---

# 36. Backfills

Backfills should be governed because they can increase:

* Database load
* Pipeline duration
* Storage
* Downstream processing

Large backfills should be treated as controlled operational changes.

---

# 37. Data Observability

The data platform should expose metrics for:

* Pipeline success
* Pipeline duration
* Rows processed
* Data freshness
* Data Quality

This connects Data Engineering with SRE practices.

---

# 38. Data SLOs

Potential SLOs include:

```text id="da22"
Critical DAG Success
Data Freshness
Quality Pass Rate
```

Exact targets must be validated against business requirements.

---

# 39. Data Security

Controls include:

* Database roles
* Least privilege
* Secret management
* Network controls
* Classification
* Auditability

Analytical convenience should not bypass data-security requirements.

---

# 40. Data Access

Consumers should receive access to appropriate curated data layers rather than unrestricted access to every raw source where practical.

Example:

```text id="da23"
Business Consumer
      │
      ▼
Analytics Layer
```

rather than:

```text id="da24"
Business Consumer
      │
      ▼
All Raw Tables
```

---

# 41. AI Integration

AI workloads should consume governed datasets.

Preferred model:

```text id="da25"
Governed Dataset
      │
      ▼
Classification / Quality Check
      │
      ▼
AI / ML Workflow
```

AI should not treat every available table as automatically appropriate.

---

# 42. MLflow Integration

Training workflows should progressively reference:

* Dataset
* Data version
* Training run
* Model version

This creates:

```text id="da26"
Dataset
  │
  ▼
MLflow Run
  │
  ▼
Model Version
```

---

# 43. RAG Integration

Future RAG systems should ingest from governed sources.

Potential flow:

```text id="da27"
Governed Data / Documents
        │
        ▼
RAG Ingestion
        │
        ▼
Metadata / Classification
        │
        ▼
Vector Index
```

This prevents the vector layer from becoming an uncontrolled secondary data store.

---

# 44. Vector Architecture

Before introducing a separate vector database, PostgreSQL + pgvector should be evaluated.

This follows:

```text id="da28"
Reuse Existing Platform
Before Adding New Data Technology
```

A separate vector store requires an ADR if adopted.

---

# 45. Backup

Data recovery must protect the authoritative relational state.

Important components include:

* PostgreSQL data
* Transformation code
* Pipeline code
* Governance definitions

Git protects code and configuration.

Database backups protect state.

---

# 46. Disaster Recovery

Recovery sequence may include:

```text id="da29"
PostgreSQL
   │
   ▼
Raw / Warehouse Data
   │
   ▼
Airflow
   │
   ▼
dbt
   │
   ▼
Quality Validation
   │
   ▼
OpenMetadata Re-ingestion
```

---

# 47. Reconstructable Data

Some data can potentially be reconstructed from original source systems.

Other data may be unique.

The backup strategy should distinguish:

```text id="da30"
Reconstructable
vs
Non-Reconstructable
```

This helps define recovery priority.

---

# 48. GitLab Integration

Data transformations, DAGs, tests, and governance definitions should remain in Git.

GitLab CI can validate:

* dbt
* SQL
* Python
* Data Quality definitions
* Governance metadata

This supports Data Engineering as software engineering.

---

# 49. Governance as Code

The layered data architecture is deeply integrated with Governance as Code.

Target chain:

```text id="da31"
Data Definition
      │
      ▼
Git
      │
      ▼
CI Validation
      │
      ▼
Airflow / dbt
      │
      ▼
OpenMetadata
      │
      ▼
Quality / Lineage / Evidence
```

---

# 50. Data Governance as Code

Machine-readable definitions may include:

* Dataset owner
* Domain
* Criticality
* Classification
* Quality rules
* Freshness
* Retention

These can be applied automatically to OpenMetadata.

---

# 51. Data Architecture Anti-Patterns

Avoid:

* Direct reporting from raw sources without justification
* Business logic copied into multiple SQL scripts
* Manual production transformations
* Data without owners
* Data without quality controls
* Mixing operational tables with analytical models without separation
* Adding databases without clear requirements

---

# 52. Technology Duplication

A new data technology should only be introduced when it solves a requirement that the current stack cannot meet efficiently.

Technology count is not a maturity metric.

---

# 53. Technical Debt Consideration

The layered architecture is not technical debt.

Potential debt includes:

* Logic outside dbt
* Missing data owners
* Manual transformations
* Missing lineage
* Missing quality tests
* Raw-to-report shortcuts

These should be tracked through Technical Debt Management.

---

# 54. Technology Governance Status

Recommended status:

```text id="da32"
PostgreSQL → ADOPT
Airflow    → ADOPT
dbt        → ADOPT
OpenMetadata → ADOPT
```

Each retains a distinct architecture responsibility.

---

# 55. Risks

## Risk — Data Quality Degradation

Mitigation:

* Automated tests
* Freshness checks
* Alerts

## Risk — Transformation Duplication

Mitigation:

* dbt
* Code review
* Standard models

## Risk — Database Resource Saturation

Mitigation:

* Capacity monitoring
* Query optimization
* Workload review

## Risk — Governance Drift

Mitigation:

* OpenMetadata
* Governance as Code

---

# 56. Positive Consequences

The platform gains:

* Clear data lifecycle
* Strong separation of responsibilities
* Reproducible transformations
* Better quality
* Better lineage
* Stronger governance
* Easier AI integration
* Lower technology duplication

---

# 57. Negative Consequences

The platform accepts:

* Multiple coordinated components
* Need for data modeling discipline
* dbt maintenance
* Metadata maintenance
* Pipeline governance

These costs are justified.

---

# 58. Success Criteria

The decision remains successful while:

* Data moves through controlled layers
* Transformation logic remains versioned
* Critical outputs pass quality checks
* Ownership and lineage are visible
* Analytical consumers use governed outputs
* PostgreSQL remains sufficient for current scale

---

# 59. Review Triggers

Review this ADR if:

* Data scale exceeds PostgreSQL capabilities
* Streaming becomes a major architectural requirement
* Lakehouse/object-storage architecture becomes necessary
* Real-time analytics becomes critical
* Data domains require stronger decentralization
* Current layered architecture blocks required business outcomes

---

# 60. Governance as Code Metadata

Future machine-readable representation:

```yaml id="da33"
id: ADR-0013
title: Adopt Layered Data Architecture with Airflow dbt PostgreSQL Data Quality and OpenMetadata
status: accepted

domain:
  - data
  - analytics
  - governance

owner: data-platform
implementation_status: implemented

layers:
  - raw
  - staging
  - warehouse
  - analytics

technologies:
  storage:
    - postgresql
  orchestration:
    - airflow
  transformation:
    - dbt
  governance:
    - openmetadata

principles:
  - separation-of-responsibilities
  - data-quality-by-design
  - governance-by-design
  - reuse-before-new-technology

related_adrs:
  - ADR-0005
  - ADR-0006
  - ADR-0008
  - ADR-0012

supersedes: null
superseded_by: null
```

---

# 61. Related Documents

* ADR-0005-PostgreSQL
* ADR-0006-Airflow
* ADR-0008-OpenMetadata
* ADR-0012-GitLab-CI-CD
* Data Architecture
* OLTP Architecture
* OLAP Architecture
* Data Quality
* Data Governance
* Data Lineage
* MCD / MERISE
* Business Glossary
* Backup and Restore
* Disaster Recovery
