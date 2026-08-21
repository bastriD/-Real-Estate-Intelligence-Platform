# Data Lineage

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document defines the Data Lineage architecture of the Enterprise AI Platform.

It describes how data moves from its original source through ingestion, transformation, storage and consumption while maintaining complete traceability.

The objective is to provide transparency, impact analysis and governance across the entire data lifecycle.

---

# 2. Scope

This document covers:

- Source systems
- Data ingestion
- Data transformations
- Data warehouse
- Metadata
- AI datasets
- Business applications
- Reporting
- Machine learning pipelines

---

# 3. Objectives

The lineage architecture aims to:

- Trace every dataset to its origin
- Understand transformation history
- Support impact analysis
- Improve troubleshooting
- Strengthen governance
- Enable regulatory compliance
- Increase confidence in analytical results

---

# 4. Lineage Principles

The platform follows these principles:

- Every critical dataset must be traceable.
- Transformations should be documented.
- Metadata should be generated automatically whenever possible.
- Lineage should remain synchronized with the implemented platform.
- Consumers must know the origin of the data they use.

---

# 5. End-to-End Lineage

The Enterprise AI Platform follows an end-to-end lineage model.

```
Data Sources

↓

Apache Airflow

↓

RAW Schema

↓

dbt Models

↓

STAGING Schema

↓

dbt Models

↓

WAREHOUSE Schema

↓

Analytics Schema

↓

Dashboards
Business APIs
AI Models
```

Every stage contributes metadata describing the data flow.

---

# 6. Source Lineage

Current data sources include:

- Business applications
- CSV imports
- APIs
- Generated datasets
- Manual data loads

Future sources may include:

- IoT devices
- Real estate APIs
- Government open data
- Financial services
- Geospatial providers

Each source should have an identified owner and description.

---

# 7. Ingestion Lineage

Apache Airflow records:

- Source
- DAG
- Execution time
- Schedule
- Pipeline status
- Execution logs
- Retry history

Airflow provides operational lineage for ingestion activities.

---

# 8. Transformation Lineage

dbt documents transformation dependencies.

Lineage includes:

- Source models
- Intermediate models
- Final models
- SQL logic
- Dependencies
- Test execution

This creates a complete transformation graph.

---

# 9. Warehouse Lineage

Warehouse lineage connects:

```
RAW

↓

STAGING

↓

WAREHOUSE

↓

ANALYTICS
```

Every analytical object should identify:

- Source tables
- Transformation models
- Business owner
- Refresh schedule

---

# 10. Metadata Lineage

OpenMetadata automatically captures lineage across:

- Tables
- Views
- Pipelines
- Dashboards
- Columns
- Owners
- Data quality tests

Metadata becomes the central view of enterprise lineage.

---

# 11. Business Lineage

Business lineage explains how data supports business outcomes.

Example:

```
Customer Orders

↓

Revenue Calculation

↓

Revenue KPIs

↓

Executive Dashboard
```

This perspective helps business users understand metric origins.

---

# 12. Column-Level Lineage

Where supported, lineage should extend to the column level.

Example:

```
customer_id

↓

stg_customers.customer_id

↓

dim_customer.customer_key

↓

analytics.customer_revenue
```

Column-level lineage simplifies troubleshooting and impact analysis.

---

# 13. AI Lineage

AI lineage documents:

- Training dataset
- Validation dataset
- Feature engineering
- Model version
- Experiment
- Prediction outputs

MLflow links models to the datasets used during training.

---

# 14. Data Consumption Lineage

Consumers include:

- Dashboards
- APIs
- Machine learning models
- Business applications
- Analysts
- Data scientists

Each consumer should be identifiable from the lineage graph.

---

# 15. Impact Analysis

Lineage supports change management.

Example questions include:

- Which dashboards depend on this table?
- Which pipelines use this dataset?
- Which AI models consume this feature?
- What breaks if a column changes?

Impact analysis reduces deployment risk.

---

# 16. Operational Monitoring

Lineage health should be monitored through:

- Failed pipelines
- Missing metadata
- Broken dependencies
- Schema drift
- Refresh failures

Broken lineage should be investigated promptly.

---

# 17. Current Implementation

Current lineage capabilities include:

- Airflow DAG lineage
- dbt dependency graph
- OpenMetadata lineage
- Warehouse layer traceability
- Git version history
- Automated metadata synchronization

These capabilities provide end-to-end visibility across the current platform.

---

# 18. Future Evolution

Planned enhancements include:

- Column-level lineage expansion
- API lineage
- Event-stream lineage
- Kafka lineage
- AI feature lineage
- Real-time lineage updates
- Cross-platform lineage federation

The overall lineage model remains unchanged as the platform evolves.

---

# 19. Architecture Decisions

Key decisions include:

- OpenMetadata as the lineage catalog
- dbt as the transformation lineage engine
- Airflow as the orchestration lineage source
- Automated lineage generation
- Metadata-first governance
- End-to-end traceability

---

# 20. Related Documents

- Data Architecture
- Data Warehouse
- Data Governance
- Data Quality
- Metadata Management
- Master & Reference Data
- Business Glossary
- AI Architecture
- OpenMetadata Documentation