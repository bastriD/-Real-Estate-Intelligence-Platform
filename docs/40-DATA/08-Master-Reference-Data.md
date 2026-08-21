# Master & Reference Data Management

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document defines the Master and Reference Data Management (MDRM) strategy of the Enterprise AI Platform.

It establishes how critical business entities and shared reference values are created, governed, maintained and consumed across the platform.

The objective is to ensure consistency, eliminate duplication and provide a single source of truth for enterprise information.

---

# 2. Scope

This document covers:

- Master Data
- Reference Data
- Ownership
- Governance
- Synchronization
- Data quality
- Versioning
- Distribution
- Change management

---

# 3. Objectives

Master and Reference Data Management aims to:

- Eliminate duplicate business entities
- Standardize shared values
- Improve data quality
- Support interoperability
- Simplify integrations
- Enable consistent reporting
- Support AI and analytics

---

# 4. Management Principles

The platform follows these principles:

- Every master entity has a single authoritative source.
- Reference data is centrally governed.
- Shared entities are reused rather than duplicated.
- Changes follow controlled governance processes.
- Consumers read authoritative data rather than maintaining local copies.

---

# 5. Enterprise Data Categories

The platform distinguishes two major categories.

```
Master Data

↓

Reference Data
```

Each category follows different governance rules.

---

# 6. Master Data

Master data represents core business entities shared across multiple applications.

Characteristics:

- Long lifecycle
- Shared across domains
- High business value
- Frequently referenced
- Governed centrally

Examples include:

- Users
- Customers
- Properties
- Agencies
- Geographic locations
- Organizations

These entities form the core business vocabulary of the platform.

---

# 7. Reference Data

Reference data consists of relatively stable values used to classify or describe business information.

Examples include:

- Countries
- Regions
- Cities
- Property types
- Transaction types
- Property status
- Currency codes
- Languages
- User roles

Reference data changes infrequently and should be centrally maintained.

---

# 8. Ownership

Every master dataset must define:

- Business Owner
- Technical Owner
- Data Steward

Reference datasets should define:

- Responsible domain
- Approval authority
- Review frequency

Ownership information is maintained within OpenMetadata.

---

# 9. Single Source of Truth

Every enterprise entity should identify one authoritative source.

Examples:

| Entity | Authoritative Source |
|---------|----------------------|
| User | Identity Management Service |
| Property | Business Database |
| Agency | Business Database |
| Country | Reference Dataset |
| Currency | Reference Dataset |
| Region | Reference Dataset |

Applications should consume these datasets rather than creating independent copies.

---

# 10. Data Distribution

Master and reference data may be consumed through:

- PostgreSQL
- Business APIs
- Data warehouse
- AI pipelines
- Reporting
- Business applications

Consumers should avoid modifying authoritative data directly.

---

# 11. Data Synchronization

Synchronization should follow controlled processes.

Typical flow:

```
Authoritative Source

↓

Validation

↓

Publication

↓

Consumers
```

Synchronization must preserve data integrity.

---

# 12. Quality Controls

Quality controls include:

- Duplicate detection
- Referential integrity
- Mandatory fields
- Standardized naming
- Business validation rules
- Consistency checks

Critical master data should be validated before publication.

---

# 13. Version Management

Reference datasets should support controlled versioning where required.

Examples:

- Regulatory classifications
- Taxonomies
- Property categories
- Status definitions

Version history should be retained when business impact exists.

---

# 14. Change Management

Changes to master or reference data follow this process:

```
Request

↓

Review

↓

Approval

↓

Implementation

↓

Validation

↓

Publication
```

Significant changes should be documented in the Decision Log.

---

# 15. Metadata Integration

OpenMetadata documents:

- Owners
- Definitions
- Tags
- Classifications
- Business descriptions
- Relationships

This provides visibility across enterprise datasets.

---

# 16. AI Integration

AI workloads consume governed master and reference data.

Examples:

- Property categories
- Geographic hierarchy
- User segments
- Market regions
- Business classifications

Using governed datasets improves model consistency and reproducibility.

---

# 17. Current Implementation

Current platform capabilities include:

- PostgreSQL relational entities
- Business Glossary
- OpenMetadata ownership
- Warehouse dimensions
- dbt transformations
- Data quality validation

Master and reference data are progressively consolidated across the platform.

---

# 18. Future Evolution

Planned improvements include:

- Dedicated Master Data APIs
- Automated synchronization
- Reference data services
- Data product catalog
- Event-driven propagation
- Stewardship workflows

These enhancements improve operational efficiency without changing governance principles.

---

# 19. Architecture Decisions

Key decisions include:

- Single source of truth for every master entity
- Central governance of reference data
- OpenMetadata for ownership and documentation
- Controlled synchronization
- Versioned reference datasets where appropriate
- Shared enterprise business vocabulary

---

# 20. Related Documents

- Data Architecture
- Data Model
- Data Governance
- Metadata Management
- Data Quality
- Data Lineage
- Business Glossary
- Decision Log
- AI Architecture