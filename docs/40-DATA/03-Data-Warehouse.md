# Data Warehouse Architecture

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document defines the Data Warehouse Architecture of the Enterprise AI Platform.

It describes how analytical data is ingested, transformed, stored and consumed to support business intelligence, reporting, machine learning and future AI-driven applications.

The warehouse provides a trusted, governed and scalable analytical foundation for the platform.

---

# 2. Scope

This document covers:

- Warehouse architecture
- ELT pipelines
- PostgreSQL schemas
- dbt transformations
- Airflow orchestration
- Analytical models
- Fact and dimension tables
- Data marts
- AI-ready datasets

---

# 3. Objectives

The warehouse aims to:

- Centralize analytical data
- Separate operational and analytical workloads
- Improve reporting performance
- Enable reusable business metrics
- Support AI training datasets
- Ensure data traceability
- Maintain high data quality

---

# 4. Architectural Principles

The warehouse follows these principles:

- ELT over ETL
- Layered architecture
- Immutable raw data
- Reproducible transformations
- Version-controlled models
- Automated testing
- Metadata-driven governance

---

# 5. Logical Architecture

```
External Sources

        │

        ▼

Apache Airflow
(Ingestion)

        │

        ▼

RAW Schema

        │

        ▼

STAGING Schema
(dbt Cleaning & Standardization)

        │

        ▼

WAREHOUSE Schema
(Business Model)

        │

        ▼

ANALYTICS Schema
(KPIs, Views, AI)

        │

        ▼

Dashboards
Business APIs
ML Models
```

---

# 6. Warehouse Layers

## Raw Layer

Purpose:

- Preserve source data
- Immutable ingestion
- Historical traceability

Characteristics:

- Minimal transformations
- Audit-friendly
- Source-oriented

---

## Staging Layer

Purpose:

- Standardize formats
- Clean data
- Validate records
- Remove inconsistencies

Responsibilities include:

- Data typing
- Null handling
- Deduplication
- Business rule validation

---

## Warehouse Layer

Purpose:

- Business integration
- Historical consistency
- Enterprise entities

Typical structures:

- Dimensions
- Facts
- Business relationships

---

## Analytics Layer

Purpose:

- KPI generation
- Reporting
- Dashboard queries
- AI datasets
- Feature extraction

Consumers should access analytical data through this layer whenever possible.

---

# 7. PostgreSQL Schemas

Current warehouse organization:

| Schema | Purpose |
|---------|---------|
| raw | Source ingestion |
| staging | Data cleansing |
| warehouse | Business model |
| analytics | Reporting & KPIs |

This separation simplifies governance and maintenance.

---

# 8. Data Ingestion

Apache Airflow orchestrates:

- Data extraction
- Workflow scheduling
- Dependency management
- Retry handling
- Failure notifications

Typical pipeline:

```
Source

↓

Airflow DAG

↓

RAW Schema
```

Airflow serves as the orchestration engine for all scheduled data movement.

---

# 9. Data Transformation

Transformations are implemented using dbt.

Responsibilities include:

- SQL model execution
- Dependency resolution
- Incremental processing
- Testing
- Documentation
- Lineage generation

dbt promotes modular, version-controlled transformations.

---

# 10. Analytical Modeling

The warehouse combines normalized operational data with dimensional analytical models.

Typical analytical objects include:

- Fact tables
- Dimension tables
- Aggregated views
- Materialized views (where appropriate)

This approach balances flexibility with query performance.

---

# 11. Fact Tables

Facts capture measurable business events.

Examples:

- Sales
- Transactions
- Orders
- Property visits
- User interactions (future)

Facts contain:

- Measures
- Foreign keys
- Event timestamps

---

# 12. Dimension Tables

Dimensions provide business context.

Examples:

- Customer
- Property
- Time
- Region
- Agency
- Product (Retail Analytics)
- Sensor (IoT project)

Dimensions support slicing and dicing of analytical measures.

---

# 13. Current Retail Analytics Implementation

The current warehouse includes:

Operational schemas:

- raw
- staging
- warehouse
- analytics

Implemented analytical datasets include:

- Customer revenue
- Revenue by category
- Top customers
- Payment status summary
- Order status summary

These datasets demonstrate the layered warehouse architecture in practice.

---

# 14. AI Data Preparation

The warehouse provides curated datasets for AI workloads.

Examples:

- Training datasets
- Validation datasets
- Feature engineering inputs
- Recommendation engine datasets
- Forecasting datasets

MLflow tracks experiments derived from these datasets.

---

# 15. Metadata Integration

OpenMetadata automatically catalogs:

- Tables
- Views
- Columns
- Owners
- Lineage
- Data profiles
- Quality metrics

This provides visibility across the warehouse.

---

# 16. Data Quality

Quality controls include:

- dbt tests
- Constraint validation
- Schema validation
- Freshness checks
- Completeness checks
- Uniqueness tests
- Referential integrity

Pipelines should fail when critical quality checks fail.

---

# 17. Performance Optimization

Optimization techniques include:

- Indexing
- Query optimization
- Incremental models
- Materialized views
- Partitioning (future)
- Statistics maintenance
- Execution plan analysis

Performance tuning should preserve data correctness.

---

# 18. Security

Warehouse security includes:

- Database authentication
- Role-based access control
- Read-only analytical users
- Namespace isolation
- Backup protection

Sensitive data should be exposed only through authorized access paths.

---

# 19. Current Architecture

Current implementation includes:

- PostgreSQL
- Apache Airflow
- dbt
- OpenMetadata
- MLflow
- GitOps deployment
- Automated data quality tests
- Metadata catalog
- End-to-end lineage

The warehouse supports both analytical reporting and AI experimentation.

---

# 20. Future Evolution

Planned enhancements include:

- Real-time ingestion with Kafka
- Streaming transformations
- Lakehouse integration (if required)
- Feature Store
- Qdrant vector database
- Semantic search
- Real estate market analytics
- Geospatial analytics

The layered architecture remains valid as these capabilities are introduced.

---

# 21. Architecture Decisions

Key decisions include:

- PostgreSQL as the analytical warehouse
- ELT architecture
- Apache Airflow for orchestration
- dbt for transformations
- OpenMetadata for governance
- MLflow for AI lifecycle
- Layered schema organization
- GitOps-managed deployment

---

# 22. Related Documents

- Data Architecture
- Data Model
- Data Governance
- Data Quality
- Data Lineage
- Metadata Management
- Master & Reference Data
- Data Lifecycle
- Data Security
- AI Architecture