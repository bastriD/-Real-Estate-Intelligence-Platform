# ADR-0005 — Adopt PostgreSQL as the Primary Relational Data Platform

**Status:** Accepted
**Date:** 2026-08-21
**Decision Owner:** Bastri Murad
**Domain:** Data / Application / Platform
**Project:** Enterprise AI Platform
**Related ADRs:** ADR-0001, ADR-0002
**Related Technologies:** PostgreSQL, Airflow, dbt, MLflow, OpenMetadata
**Supersedes:** None
**Superseded By:** None

---

# 1. Context

The Enterprise AI Platform requires a relational data platform capable of supporting several different workloads, including:

* Business application data
* Analytical data
* Data pipelines
* Data quality processes
* Metadata-related services
* MLOps metadata
* Reporting workloads
* Future AI retrieval workloads where appropriate

The platform already operates PostgreSQL successfully for the Retail Analytics platform using logical layers such as:

```text
raw
staging
warehouse
analytics
```

The data platform must remain:

* Reliable
* Open source
* Mature
* Easy to operate
* Well integrated with Python
* Compatible with Airflow
* Compatible with dbt
* Observable
* Recoverable
* Resource efficient

The existing physical infrastructure is fixed, so introducing multiple specialized databases without a clear requirement would increase unnecessary operational and resource overhead.

---

# 2. Problem

The platform requires a standard relational database technology for persistent structured data.

Without a common relational database standard, the architecture could progressively accumulate multiple database engines for similar workloads.

This would increase:

* Operational complexity
* Backup complexity
* Security surface
* Monitoring requirements
* Upgrade burden
* Recovery procedures
* Knowledge requirements
* Resource consumption

A primary relational platform must therefore be selected.

---

# 3. Decision

The platform will use **PostgreSQL** as the primary relational database technology.

PostgreSQL is the default choice for:

* New structured application data
* Analytical relational workloads
* Data platform storage
* Platform-service databases where supported
* SQL-based integration services

unless a documented functional requirement justifies another technology.

PostgreSQL becomes an **Adopt** technology in Technology Governance.

---

# 4. Architecture Role

PostgreSQL may serve several architectural roles.

```text
Applications
     │
     ▼
PostgreSQL

Data Sources
     │
     ▼
Airflow
     │
     ▼
PostgreSQL
     │
     ├── raw
     ├── staging
     ├── warehouse
     └── analytics
          │
          ▼
         dbt
```

Other platform systems may also use PostgreSQL-compatible backends where appropriate.

---

# 5. Current Implementation

PostgreSQL is already implemented in the platform.

Current evidence includes the Retail Analytics environment with schemas such as:

```text
raw
staging
warehouse
analytics
```

Existing capabilities include:

* Data ingestion
* Transformations
* Analytical views
* Data quality validation
* Airflow integration
* dbt integration
* OpenMetadata ingestion

Current status:

```text
IMPLEMENTED
```

---

# 6. Alternatives Considered

## Option 1 — PostgreSQL

Advantages:

* Mature
* Open source
* Strong SQL support
* ACID transactions
* Rich data types
* Strong Python ecosystem
* Excellent Airflow/dbt integration
* Mature backup tooling
* Large community
* Good observability support
* Extension ecosystem
* Potential vector support through pgvector

Disadvantages:

* Requires operational management
* Not specialized for every analytical workload
* Horizontal scale is more complex than some distributed systems

Selected.

---

## Option 2 — MySQL / MariaDB

Advantages:

* Mature
* Widely adopted
* Relatively simple
* Strong ecosystem

Disadvantages:

* PostgreSQL provides a stronger fit with the current analytics/data-engineering direction
* Would introduce duplication
* Existing platform investment already favors PostgreSQL

Not selected as the strategic default.

MySQL/MariaDB may still be used for specific training exercises or third-party application requirements.

---

## Option 3 — Microsoft SQL Server

Advantages:

* Strong enterprise ecosystem
* Mature tooling
* Good BI integration

Disadvantages:

* Licensing considerations
* Larger platform footprint
* Less alignment with the current open-source stack
* No current requirement that justifies introduction

Not selected.

---

## Option 4 — Distributed Analytical Database

Examples could include:

* ClickHouse
* BigQuery
* Snowflake
* Other MPP systems

Advantages:

* High-scale analytical performance
* Large analytical workloads

Disadvantages:

* Current data scale does not justify additional architecture
* Increased operational or financial complexity
* Existing PostgreSQL performance is sufficient for current requirements

Not selected at the current scale.

---

# 7. Decision Criteria

The decision considered:

| Criterion                    |    Importance |
| ---------------------------- | ------------: |
| Reliability                  |      Critical |
| SQL capability               |      Critical |
| Data engineering integration |      Critical |
| Open source                  |          High |
| Operational simplicity       |          High |
| Resource efficiency          |          High |
| Backup/recovery              |      Critical |
| Python integration           |          High |
| Extensibility                |          High |
| AI/vector potential          |        Medium |
| Extreme horizontal scaling   | Low currently |

PostgreSQL provides the strongest overall fit.

---

# 8. Data Architecture Integration

PostgreSQL supports the layered data architecture:

```text
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

This provides separation between:

* Source ingestion
* Cleaning
* Business modeling
* Consumer-facing analytical structures

---

# 9. OLTP and OLAP Position

PostgreSQL may support both moderate OLTP and analytical workloads at the current project scale.

However, the architecture distinguishes the logical purposes.

```text
OLTP
→ Transactional application operations

OLAP
→ Analytical processing and reporting
```

The fact that both may currently run on PostgreSQL does not mean their data models should be mixed.

---

# 10. dbt Integration

dbt provides transformation-as-code capabilities.

Relationship:

```text
PostgreSQL
    │
    ▼
dbt
    │
    ├── staging models
    ├── transformation models
    ├── tests
    └── analytics models
```

This separates transformation logic from manual SQL execution.

---

# 11. Airflow Integration

Airflow orchestrates data workflows involving PostgreSQL.

Example:

```text
Extract
   │
   ▼
Load PostgreSQL
   │
   ▼
Transform
   │
   ▼
Data Quality
   │
   ▼
Publish
```

Airflow is responsible for orchestration.

PostgreSQL is responsible for persistent relational storage.

---

# 12. OpenMetadata Integration

PostgreSQL metadata is ingested into OpenMetadata.

This enables:

* Schema discovery
* Table cataloging
* Ownership
* Lineage
* Profiling
* Data quality
* Governance

PostgreSQL therefore participates directly in the Data Governance architecture.

---

# 13. Security Consequences

PostgreSQL must be governed through:

* Authentication
* Role-based permissions
* Least privilege
* Secret management
* Network restrictions
* TLS where required
* Auditability

Database administrative accounts should not be used by applications.

---

# 14. Database Roles

Applications should use dedicated service accounts.

Example:

```text
Application A
→ role_application_a

Airflow
→ role_airflow

Governance job
→ role_governance
```

Permissions should match operational requirements.

---

# 15. Secrets

Database credentials must not be stored in plaintext Git repositories.

Credentials should be delivered through approved secret-management mechanisms.

GitOps manages the configuration reference, not the secret value itself.

---

# 16. Availability Consequences

PostgreSQL is a critical dependency for several workloads.

A database failure may affect:

* Business applications
* Analytical pipelines
* Metadata systems
* Model-related services

Availability must therefore be explicitly monitored.

---

# 17. High Availability

The current architecture does not assume enterprise multi-region PostgreSQL clustering.

HA requirements should be proportional to:

* Business criticality
* Physical resources
* RTO
* Operational complexity

Current priority is:

```text
Reliable backups
+
Tested recovery
+
Monitoring
+
Controlled operations
```

before adding unnecessary database-cluster complexity.

---

# 18. Backup Strategy

Critical PostgreSQL data must be backed up using database-aware backup procedures.

Possible methods include:

* `pg_dump`
* `pg_dumpall`
* Physical backup where justified

The selected method depends on database size and recovery requirements.

---

# 19. Restore Validation

Backup success alone is insufficient.

Target model:

```text
Backup
  │
  ▼
Isolated Restore
  │
  ▼
Schema Validation
  │
  ▼
Data Validation
  │
  ▼
Recovery Evidence
```

Automated restore testing is a roadmap priority.

---

# 20. RPO and RTO

RPO and RTO should be defined according to business importance.

Example architecture targets may be documented separately.

They remain operational objectives until tested through actual recovery exercises.

---

# 21. Observability

PostgreSQL should expose operational visibility including:

* Availability
* Connections
* Query latency
* Transactions
* Locks
* Deadlocks
* Database size
* Storage growth

Prometheus-compatible exporters may be used.

---

# 22. Logging

PostgreSQL logs should support diagnosis of:

* Authentication failure
* Connection failure
* Startup/shutdown
* Deadlocks
* Query errors
* Slow queries where configured

Logging must be tuned to avoid excessive volume.

---

# 23. Capacity Management

Capacity planning should monitor:

```text
Database Size
Connection Count
Disk Growth
Query Performance
I/O
```

Storage exhaustion is a critical database risk.

---

# 24. Resource Constraints

The platform has limited physical resources.

PostgreSQL configuration should therefore be tuned proportionally.

Avoid:

* Excessive memory allocation
* Unnecessary extensions
* Duplicate database platforms
* Overly complex clustering

Resource efficiency is an explicit architectural requirement.

---

# 25. Extensions

PostgreSQL extensions may be introduced when justified.

Examples may include:

* `pg_stat_statements`
* `pgvector`

Extensions should follow Technology Governance and compatibility review.

---

# 26. pgvector Consideration

Future RAG requirements may require vector storage.

Before introducing a separate vector database, the platform should evaluate:

```text
PostgreSQL + pgvector
```

because PostgreSQL already exists and is operationally governed.

Potential advantages include:

* Reuse existing database
* Reduce technology count
* Unified backup
* Unified security
* Lower operational overhead

---

# 27. Vector Database Decision

PostgreSQL + pgvector is not automatically selected for all future AI workloads.

If RAG requirements exceed its capabilities, alternatives may include:

* Qdrant
* Milvus
* Other vector-native systems

Decision process:

```text
Requirement
   │
   ▼
Benchmark / PoC
   │
   ▼
Decision Matrix
   │
   ▼
ADR
```

---

# 28. Governance as Code

Database governance should progressively become machine-readable.

Potential controls include:

* Required owner
* Data classification
* Backup policy
* Retention
* Data quality rules
* Database access roles

OpenMetadata and governance jobs provide part of this model.

---

# 29. Data Quality as Code

Critical datasets should have version-controlled data-quality expectations.

Examples:

* Not null
* Unique
* Referential integrity
* Accepted values
* Freshness

Data quality results become governance evidence.

---

# 30. Schema Governance

Production schema changes should use controlled migration processes.

Avoid direct ad hoc production modification.

Preferred:

```text
Migration Definition
      │
      ▼
Git
      │
      ▼
CI / Review
      │
      ▼
Controlled Execution
```

---

# 31. Schema Compatibility

Changes should consider:

* Existing applications
* dbt models
* Airflow DAGs
* OpenMetadata
* Reporting
* Data quality tests

Schema evolution is a cross-system concern.

---

# 32. Migration Rollback

Some schema changes cannot be safely reversed by a simple Git revert.

Destructive changes require:

* Backup
* Migration plan
* Data protection
* Validation

Database state is fundamentally different from stateless Kubernetes configuration.

---

# 33. Performance Governance

Performance problems should be addressed with evidence.

Typical workflow:

```text
Latency Increase
      │
      ▼
Prometheus
      │
      ▼
Query Analysis
      │
      ▼
Execution Plan
      │
      ▼
Index / Query / Model Improvement
```

Do not introduce a new database engine as the first response to an uninvestigated slow query.

---

# 34. Index Governance

Indexes improve some queries but add:

* Storage
* Write overhead
* Maintenance

Indexes should be created based on actual query patterns.

---

# 35. Connection Management

Applications should use appropriate connection pooling.

Uncontrolled database connections can create:

* Connection exhaustion
* Increased latency
* Resource pressure

Connection saturation should be observable.

---

# 36. Database Naming and Ownership

Databases and schemas should have clear:

* Purpose
* Owner
* Environment
* Lifecycle

This metadata should eventually integrate with OpenMetadata and Governance as Code.

---

# 37. Data Retention

Retention should follow Data Governance and compliance requirements.

Not all relational data should be stored indefinitely.

Retention automation is a future maturity objective.

---

# 38. GDPR Consequences

Where PostgreSQL stores personal information, controls must support:

* Data minimization
* Access restriction
* Retention
* Traceability
* Data subject processes where applicable

The GDPR Register remains the authoritative processing record.

---

# 39. Disaster Recovery

Database recovery is a critical Disaster Recovery stage.

Typical sequence:

```text
Infrastructure
     │
     ▼
Storage
     │
     ▼
PostgreSQL
     │
     ▼
Restore
     │
     ▼
Integrity Validation
     │
     ▼
Dependent Services
```

Applications should not be restarted against an unvalidated restored database.

---

# 40. Recovery Validation

Validation should include:

* Database available
* Expected schemas
* Critical tables
* Row counts
* Referential integrity
* Application connectivity

Where appropriate, a controlled write/read smoke test should be performed.

---

# 41. Technical Debt Consideration

Using PostgreSQL for multiple appropriate relational workloads is not technical debt.

It becomes debt if:

* Workload requirements exceed PostgreSQL capabilities
* Performance remains unacceptable after proper optimization
* A specialized requirement is intentionally ignored
* Unsupported versions remain deployed

---

# 42. Technology Governance Status

Recommended classification:

```text
Technology: PostgreSQL
Category: Database
Lifecycle: ADOPT
```

The exact supported version should be tracked through the Technology Catalog.

---

# 43. Risks

## Risk — Database Data Loss

Mitigation:

* Backup
* Restore testing
* Storage monitoring

## Risk — Storage Exhaustion

Mitigation:

* Capacity monitoring
* Growth review
* Alerting

## Risk — Credential Exposure

Mitigation:

* Secret management
* Least privilege

## Risk — Database Becomes Shared Failure Domain

Mitigation:

* Dependency awareness
* Recovery planning
* Logical database separation where appropriate

---

# 44. Positive Consequences

The platform gains:

* A standardized relational technology
* Strong SQL ecosystem
* Simplified operations
* Simplified backup strategy
* Strong Data Engineering integration
* Reduced technology duplication
* Potential future vector support

---

# 45. Negative Consequences

The platform accepts:

* PostgreSQL operational responsibility
* Shared dependency risk
* Need for backup and recovery discipline
* Potential future need for specialized data stores

These costs are considered acceptable.

---

# 46. Success Criteria

The decision remains successful while:

* PostgreSQL satisfies application and data workloads
* Performance remains acceptable
* Backup and recovery are reliable
* Data governance remains effective
* Operational resource usage remains appropriate
* Specialized technologies are introduced only when justified

---

# 47. Review Triggers

Review this ADR if:

* Data volume increases substantially
* Analytical workload exceeds PostgreSQL capability
* Availability requirements change significantly
* Distributed database requirements appear
* Vector workloads exceed pgvector capabilities
* PostgreSQL support/lifecycle changes

---

# 48. Governance as Code Metadata

Future machine-readable representation:

```yaml
id: ADR-0005
title: Adopt PostgreSQL as Primary Relational Data Platform
status: accepted

domain:
  - data
  - application
  - platform

technologies:
  - postgresql

owner: data-platform
implementation_status: implemented

alternatives:
  - mysql
  - mariadb
  - sql-server
  - distributed-analytics-database

future_evaluations:
  - pgvector

supersedes: null
superseded_by: null
```

---

# 49. Related Documents

* ADR-0001-Kubernetes
* Data Architecture
* OLTP Architecture
* OLAP Architecture
* Data Governance
* Data Quality
* Airflow Architecture
* OpenMetadata Architecture
* Backup and Restore
* Disaster Recovery
* Capacity Management
* Technology Governance
