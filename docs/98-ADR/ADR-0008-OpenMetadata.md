# ADR-0008 — OpenMetadata as the Enterprise Metadata and Data Governance Platform

**Status:** Accepted  
**Decision ID:** ADR-0008  
**Domain:** Data / Governance / Metadata  
**Scope:** Enterprise AI Platform  
**Decision Type:** Architecture  
**Last Updated:** 2026-08-21

---

# 1. Context

The Enterprise AI Platform requires a centralized capability for understanding, governing and tracing enterprise data assets.

The platform contains multiple data-producing and data-consuming systems, including:

- PostgreSQL
- Apache Airflow
- dbt
- Analytics datasets
- Business applications
- MLflow
- AI / ML workflows
- RAG pipelines
- Kubernetes-hosted services

Without centralized metadata management, knowledge about data becomes distributed across:

- SQL definitions
- Pipeline code
- dbt models
- Airflow DAGs
- Application code
- Documentation
- Dashboards
- Individual engineers

This creates several architectural risks:

- Unknown data ownership
- Poor discoverability
- Incomplete lineage
- Duplicated datasets
- Inconsistent terminology
- Weak Data Quality visibility
- Difficult impact analysis
- Limited governance evidence
- Reduced trust in analytical data
- Poor traceability for AI data sources

The platform therefore requires a central metadata and governance capability.

---

# 2. Problem

The architecture must answer questions such as:

```text
What data assets exist?

Where does a dataset originate?

Who owns the dataset?

Which pipelines transform it?

Which downstream assets depend on it?

What business term describes it?

What classification applies to it?

What Data Quality controls apply?

When was the asset last profiled?

Which AI or analytics workloads consume it?
```

The solution must integrate with the existing platform architecture, particularly:

- PostgreSQL
- Apache Airflow
- dbt
- Kubernetes
- Data Quality processes
- Analytics
- AI / ML workloads
- Governance as Code

Metadata must not remain isolated inside individual tools.

---

# 3. Decision

The platform will use **OpenMetadata** as the standard enterprise metadata management and data-governance platform.

OpenMetadata is responsible for:

- Data catalog
- Metadata discovery
- Technical metadata
- Business metadata
- Ownership
- Classification
- Glossary
- Data lineage
- Data profiling
- Data Quality visibility
- Asset relationships
- Governance metadata
- Search and discovery

OpenMetadata becomes the central platform for answering:

```text
What data exists?
        +
What does it mean?
        +
Where did it come from?
        +
Who owns it?
        +
Can it be trusted?
        +
What depends on it?
```

OpenMetadata is **not** the primary data store, transformation engine, workflow orchestrator or ML experiment tracker.

---

# 4. Separation of Responsibilities

The architecture deliberately separates data responsibilities.

```text
Source Systems
      |
      v
Apache Airflow
      |
      v
Ingestion / Orchestration
      |
      v
PostgreSQL
      |
      v
dbt
      |
      v
Transformation / Analytics
      |
      +--------------------+
      |                    |
      v                    v
Data Consumers        OpenMetadata
                           |
                           +-- Catalog
                           +-- Ownership
                           +-- Classification
                           +-- Glossary
                           +-- Lineage
                           +-- Profiling
                           +-- Data Quality
                           +-- Governance
```

Responsibilities are therefore:

```text
Airflow
    = workflow orchestration

PostgreSQL
    = data persistence

dbt
    = transformation and analytical modeling

OpenMetadata
    = metadata, lineage and governance

MLflow
    = ML experiment and model lifecycle

Git
    = governance definitions and desired state
```

This separation prevents OpenMetadata from becoming an overloaded platform responsible for functions belonging to other systems.

---

# 5. Metadata Architecture

The target metadata flow is:

```text
PostgreSQL -----------+
                      |
Airflow --------------+
                      |
dbt ------------------+----> OpenMetadata
                      |
Data Quality ---------+
                      |
Other Data Services --+
                           |
                           v
                    Metadata Catalog
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
          Search        Lineage      Governance
```

OpenMetadata aggregates metadata from the systems that actually execute data workloads.

The underlying systems remain authoritative for their operational state.

---

# 6. Data Catalog

OpenMetadata provides the central catalog for enterprise data assets.

Cataloged assets may include:

- Databases
- Schemas
- Tables
- Views
- Pipelines
- Dashboards
- Data models
- ML-related assets where supported
- Business terms
- Data Quality tests

The catalog improves discoverability and reduces dependency on undocumented institutional knowledge.

---

# 7. Ownership

Important data assets should have explicit ownership.

The target model distinguishes where appropriate:

```text
Business Owner
      +
Technical Owner
      +
Data Steward
```

Ownership enables:

- Accountability
- Governance review
- Incident routing
- Data Quality responsibility
- Lifecycle decisions
- Access decisions
- Change impact assessment

Critical datasets should not remain permanently ownerless.

---

# 8. Business Glossary

OpenMetadata will support a governed business glossary.

The glossary connects technical assets to business meaning.

Example:

```text
Business Term
"Customer Revenue"
        |
        v
Definition
        |
        v
Related Data Assets
        |
        +-- analytics.customer_revenue
        |
        +-- warehouse.fact_sales
```

The glossary should reduce inconsistent terminology between:

- Business
- Data
- Applications
- Analytics
- AI

---

# 9. Classification

Data classification should be represented in metadata.

Possible classifications include:

```text
Public
Internal
Confidential
Restricted
Personal Data
Sensitive Personal Data
```

The exact classification taxonomy is governed by the security and compliance architecture.

Classification metadata can support:

- Access decisions
- GDPR controls
- AI data-use decisions
- Retention policies
- Security monitoring
- External sharing controls

---

# 10. Data Lineage

OpenMetadata provides centralized lineage visibility.

The target lineage model is:

```text
Source
  |
  v
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
  |
  +----> Dashboard
  |
  +----> Application
  |
  +----> AI / ML
```

Lineage allows engineers and governance stakeholders to understand:

- Upstream dependencies
- Downstream dependencies
- Transformation paths
- Impact of schema changes
- Data provenance
- AI source provenance

---

# 11. dbt Integration

dbt remains responsible for analytical transformation logic.

OpenMetadata consumes metadata generated by dbt where appropriate.

The relationship is:

```text
dbt
 |
 +-- Models
 +-- Sources
 +-- Tests
 +-- Documentation
 +-- Dependencies
 |
 v
OpenMetadata
 |
 +-- Catalog
 +-- Lineage
 +-- Quality Context
 +-- Discovery
```

OpenMetadata does not replace dbt.

---

# 12. Airflow Integration

Airflow remains the workflow orchestrator.

OpenMetadata receives pipeline metadata from Airflow.

The relationship is:

```text
Airflow
   |
   +-- DAG
   +-- Tasks
   +-- Scheduling
   +-- Execution
   |
   v
OpenMetadata
   |
   +-- Pipeline Metadata
   +-- Relationships
   +-- Lineage
```

OpenMetadata does not become responsible for scheduling workflows.

---

# 13. PostgreSQL Integration

PostgreSQL remains authoritative for relational data.

OpenMetadata extracts metadata such as:

- Databases
- Schemas
- Tables
- Columns
- Types
- Constraints
- Statistics
- Profiles

The relationship is:

```text
PostgreSQL
     |
     v
Metadata Ingestion
     |
     v
OpenMetadata
```

Metadata ingestion must not modify production data unless explicitly required and approved.

---

# 14. Data Profiling

OpenMetadata may execute or collect profiling information.

Profiling can include:

- Row counts
- Null statistics
- Distinct values
- Value distributions
- Minimum values
- Maximum values
- Column statistics

Profiling provides evidence about the actual state of datasets.

However:

```text
Profiling != Data Quality
```

Profiling describes observed characteristics.

Data Quality evaluates those characteristics against expectations.

---

# 15. Data Quality

OpenMetadata provides visibility and governance around Data Quality controls.

Examples include:

- Not-null checks
- Uniqueness
- Accepted values
- Row-count expectations
- Range checks
- Referential expectations
- Freshness

The target lifecycle is:

```text
Quality Requirement
        |
        v
Data Quality Test
        |
        v
Execution
        |
        v
Result
        |
        v
OpenMetadata
        |
        v
Governance Evidence
```

Data Quality results should progressively contribute to continuous governance.

---

# 16. Governance as Code

Governance definitions should progressively be stored in Git and applied automatically where technically appropriate.

The target model is:

```text
Governance Definition
        |
        v
Git
        |
        v
Merge Request
        |
        v
CI Validation
        |
        v
Governance Automation
        |
        v
OpenMetadata API
        |
        v
Applied Metadata State
```

Examples of Governance as Code artifacts may include:

- Owners
- Domains
- Glossary terms
- Classifications
- Tags
- Data Quality definitions
- Criticality
- Governance relationships

OpenMetadata therefore acts as both:

```text
Governance User Interface
        +
Governance Runtime
```

while Git progressively becomes the authoritative source for selected machine-readable governance definitions.

---

# 17. Git as Governance Source of Truth

Not all OpenMetadata state must immediately be managed through Git.

The transition should be progressive.

Target maturity:

```text
Level 1
Manual Metadata

      |
      v

Level 2
Documented Governance

      |
      v

Level 3
Version-Controlled Definitions

      |
      v

Level 4
Automated Application

      |
      v

Level 5
Continuous Governance Evidence
```

The platform should avoid creating two uncontrolled competing sources of truth.

For governance artifacts managed as code:

```text
Git = desired governance state

OpenMetadata = applied governance state
```

---

# 18. API Integration

OpenMetadata APIs may be used to automate governance operations.

Automation can support:

- Metadata creation
- Ownership assignment
- Classification
- Glossary relationships
- Data Quality definitions
- Validation
- Governance reporting

API automation must remain:

- Version controlled
- Reviewable
- Idempotent where practical
- Observable
- Auditable

---

# 19. Kubernetes Deployment

OpenMetadata is deployed as part of the platform infrastructure.

The Kubernetes architecture provides:

- Scheduling
- Service discovery
- Configuration
- Secrets
- Ingress
- TLS
- Resource management
- Observability

The service should follow the same GitOps principles as other managed platform services.

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
OpenMetadata
```

Manual runtime changes should not become permanent undocumented configuration.

---

# 20. Security

OpenMetadata contains potentially sensitive information about enterprise data architecture.

Security controls must therefore cover:

- Authentication
- Authorization
- RBAC
- TLS
- Secrets
- Database credentials
- API credentials
- Administrative access
- Auditability

Metadata access does not automatically imply access to underlying business data.

The architecture must maintain separation between:

```text
Permission to discover metadata
            !=
Permission to access underlying data
```

---

# 21. Privacy and GDPR

OpenMetadata supports GDPR governance by improving visibility into:

- Personal data
- Sensitive data
- Ownership
- Data location
- Lineage
- Retention context
- Processing relationships

However, OpenMetadata does not itself guarantee GDPR compliance.

Compliance requires a combination of:

- Governance
- Legal interpretation
- Security controls
- Retention processes
- Data lifecycle controls
- Access management
- Operational evidence

---

# 22. AI and RAG Governance

Metadata governance becomes especially important when enterprise data is consumed by AI systems.

Before data is used for RAG or AI context, the platform should be able to determine:

```text
What is this data?

Who owns it?

Where did it originate?

What classification applies?

Is its quality acceptable?

May it be used by this AI workload?
```

OpenMetadata can provide part of this governance context.

The target relationship is:

```text
Enterprise Data
      |
      v
OpenMetadata
      |
      +-- Ownership
      +-- Classification
      +-- Quality
      +-- Lineage
      +-- Business Context
      |
      v
AI Governance Decision
      |
      v
RAG / AI Consumption
```

This does not mean every AI authorization decision must be performed directly by OpenMetadata.

OpenMetadata provides governance evidence and context used by the wider AI governance architecture.

---

# 23. Observability

OpenMetadata must itself be observable.

Operational monitoring should progressively cover:

- Service availability
- API health
- Metadata ingestion
- Ingestion failures
- Database health
- Search/index health
- Resource consumption
- Data Quality execution
- Pipeline failures

Observability should integrate with the platform monitoring architecture.

```text
OpenMetadata
      |
      +----> Metrics
      |
      +----> Logs
      |
      +----> Alerts
      |
      v
Platform Observability
```

---

# 24. Alternatives Considered

## Alternative 1 — Documentation Only

Maintain metadata manually in Markdown, spreadsheets or wiki pages.

### Advantages

- Simple
- Low infrastructure requirement

### Disadvantages

- Poor synchronization
- Limited search
- No automatic lineage
- Weak profiling
- Difficult automation
- Poor scalability

Rejected as the primary metadata solution.

---

## Alternative 2 — Build a Custom Metadata Platform

Develop an internal catalog and governance system.

### Advantages

- Full customization

### Disadvantages

- High engineering cost
- High maintenance cost
- Large feature surface
- Significant long-term technical debt

Rejected.

---

## Alternative 3 — DataHub

Use DataHub as the enterprise metadata platform.

### Advantages

- Strong metadata architecture
- Good lineage capabilities
- Large ecosystem

### Disadvantages

- Additional operational complexity
- No decisive advantage for the current platform requirements
- OpenMetadata already aligns with the implemented platform and governance model

Not selected for the current architecture.

---

## Alternative 4 — OpenMetadata

### Advantages

- Open source
- Data catalog
- Lineage
- Profiling
- Data Quality
- Ownership
- Classification
- Glossary
- APIs
- Integration ecosystem
- Suitable for Governance as Code automation

### Disadvantages

- Operational complexity
- Additional infrastructure
- Metadata ingestion requires maintenance
- Governance still requires human ownership and processes

Selected.

---

# 25. Consequences

## Positive Consequences

The decision provides:

- Centralized metadata
- Improved data discovery
- Ownership visibility
- Data lineage
- Data Quality visibility
- Governance integration
- Better impact analysis
- Better AI data provenance
- Reduced documentation fragmentation
- API-driven governance automation
- Stronger auditability

---

## Negative Consequences

The decision introduces:

- Additional platform complexity
- Additional compute and storage consumption
- Metadata ingestion maintenance
- Search/index dependencies
- Governance process requirements
- Additional operational responsibility

OpenMetadata therefore becomes an important platform service that itself requires lifecycle management.

---

# 26. Risks

## Metadata Becomes Stale

### Risk

Metadata no longer represents actual platform state.

### Mitigation

Automate ingestion and monitor ingestion freshness.

---

## Missing Ownership

### Risk

Assets exist in the catalog without accountable owners.

### Mitigation

Introduce ownership coverage metrics and governance controls.

---

## Manual Governance Drift

### Risk

OpenMetadata configuration diverges from governance definitions stored in Git.

### Mitigation

Progressively introduce Governance as Code reconciliation and validation.

---

## Excessive Metadata Access

### Risk

Metadata exposes sensitive information about enterprise systems.

### Mitigation

Use authentication, RBAC and least privilege.

---

## Profiling Cost

### Risk

Aggressive profiling consumes excessive database resources.

### Mitigation

Control profiling frequency and scope based on asset criticality.

---

# 27. Operational Requirements

OpenMetadata must have:

- Documented deployment
- Persistent storage strategy
- Backup strategy
- Restore procedure
- Resource limits
- Monitoring
- Alerting
- Upgrade procedure
- Ingestion monitoring
- Access control
- Secret management

A metadata platform that cannot itself be reliably operated becomes a governance risk.

---

# 28. Backup and Recovery

OpenMetadata contains governance state that must be recoverable.

Protected state includes where applicable:

- Metadata database
- Ownership
- Glossary
- Classifications
- Tags
- Governance relationships
- Data Quality definitions
- Configuration

Recovery must follow the wider platform Backup and Disaster Recovery architecture.

Governance definitions stored in Git provide an additional reconstruction capability but do not automatically replace database backup.

---

# 29. Success Criteria

This decision is successful when:

- Important enterprise datasets are discoverable
- Critical assets have defined ownership
- PostgreSQL metadata is ingested
- Airflow metadata is ingested
- dbt metadata is ingested
- Lineage is visible
- Data Quality results are visible
- Classification is applied where required
- Governance definitions can be version controlled
- Metadata freshness is monitored
- AI workflows can identify governed source datasets

---

# 30. Evidence

Evidence supporting this ADR may include:

- OpenMetadata service availability
- Successful PostgreSQL ingestion
- Successful Airflow ingestion
- Successful dbt ingestion
- Profiling results
- Data Quality results
- Ownership coverage
- Classification coverage
- Lineage screenshots or API results
- Governance as Code jobs
- Git history
- CI validation
- Monitoring dashboards

The preferred principle is:

```text
Architecture Decision
        |
        v
Implementation
        |
        v
Operational Evidence
```

---

# 31. Review Triggers

This ADR should be reviewed if:

- OpenMetadata no longer satisfies metadata requirements
- Operational complexity becomes disproportionate
- A different enterprise catalog becomes mandatory
- Governance requirements materially change
- AI governance requires capabilities unavailable in OpenMetadata
- Metadata scale exceeds the current architecture
- The platform migrates to a managed metadata service
- Integration requirements fundamentally change

---

# 32. Related Documentation

Related architecture domains:

```text
40-DATA/
50-AI/
60-SECURITY/
70-DEVOPS/
80-OPERATIONS/
90-OBSERVABILITY/
95-GOVERNANCE/
99-DIAGRAMS/
```

Related ADRs include:

```text
ADR-0005 — PostgreSQL
ADR-0006 — Airflow
ADR-0007 — MLflow
ADR-0013 — Data Architecture
ADR-0014 — Governance as Code
```

---

# 33. Final Decision

The Enterprise AI Platform will use **OpenMetadata** as its standard metadata catalog and data-governance platform.

OpenMetadata provides the central capability for:

```text
Discovery
   +
Ownership
   +
Classification
   +
Glossary
   +
Lineage
   +
Profiling
   +
Data Quality
   +
Governance Metadata
```

It integrates with the wider platform while maintaining clear separation of responsibilities:

```text
Airflow      = orchestration

dbt          = transformation

PostgreSQL   = data persistence

OpenMetadata = metadata and governance

MLflow       = ML lifecycle

Git          = version-controlled governance definitions
```

OpenMetadata is also a key component of the platform's **Governance as Code** strategy.

The target architecture moves from manually documented governance toward:

```text
Governance Definition
        |
        v
Git
        |
        v
Validation
        |
        v
OpenMetadata
        |
        v
Runtime Evidence
        |
        v
Continuous Governance
```

**Decision: ACCEPTED**