# Data Model

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document defines the enterprise data model of the Enterprise AI Platform.

It describes how business information is organized independently of implementation technologies.

The model provides a common language for business stakeholders, data engineers, software engineers and AI engineers.

---

# 2. Scope

The data model covers:

- Conceptual model
- Logical model
- Physical model
- Business entities
- Relationships
- Keys
- Data integrity
- Modeling principles

---

# 3. Objectives

The enterprise data model aims to:

- Establish a common business vocabulary
- Eliminate ambiguity
- Reduce data duplication
- Support analytics
- Support AI workloads
- Ensure long-term consistency
- Facilitate future system evolution

---

# 4. Modeling Principles

The platform follows these principles:

- Business-first modeling
- Technology-independent design
- Normalization where appropriate
- Controlled denormalization for analytics
- Stable identifiers
- Explicit relationships
- Traceable ownership

---

# 5. Modeling Levels

The Enterprise AI Platform distinguishes three modeling levels.

```
Conceptual

↓

Logical

↓

Physical
```

Each level serves a different purpose.

---

# 6. Conceptual Data Model

The conceptual model identifies the main business objects without implementation details.

Examples include:

- User
- Property
- Listing
- Agency
- Market
- Transaction
- Region
- Recommendation
- AI Model

These entities represent business concepts rather than database tables.

---

# 7. Logical Data Model

The logical model defines:

- Attributes
- Relationships
- Cardinalities
- Business rules
- Primary identifiers

Example:

```
User

1

↓

N

Property Search

↓

N

Property
```

The logical model remains independent of PostgreSQL or any specific database engine.

---

# 8. Physical Data Model

The physical model maps logical entities to implementation structures.

Examples:

- Tables
- Columns
- Constraints
- Indexes
- Foreign Keys
- Views
- Materialized Views

Implementation details are documented separately within the warehouse architecture.

---

# 9. Business Entities

Typical enterprise entities include:

| Entity | Description |
|---------|-------------|
| User | Platform user |
| Property | Real estate asset |
| Listing | Published advertisement |
| Agency | Real estate agency |
| Region | Geographic location |
| Transaction | Purchase or rental |
| Market Indicator | Market statistics |
| Recommendation | AI recommendation |
| Model Version | ML model metadata |

Additional entities may be introduced as business capabilities evolve.

---

# 10. Relationships

Relationships describe business interactions.

Examples:

```
Agency

1

↓

N

Property
```

```
Property

1

↓

N

Listing
```

```
User

N

↓

N

Property
```

The definitive conceptual model is maintained separately in the MCD documentation.

---

# 11. Keys

Every persistent entity should define:

- Primary Key
- Candidate Keys
- Foreign Keys
- Business Identifier (where applicable)

Primary keys should remain stable throughout the entity lifecycle.

---

# 12. Data Integrity

Integrity is maintained through:

- Primary Keys
- Foreign Keys
- Unique constraints
- Check constraints
- Referential integrity
- Validation rules

Business rules should be enforced as close to the data layer as practical.

---

# 13. Naming Standards

Entity names should:

- Use business terminology
- Be singular
- Be descriptive
- Avoid abbreviations unless standardized

Attributes should:

- Follow consistent naming conventions
- Be self-explanatory
- Remain stable over time

---

# 14. Normalization Strategy

Operational data should generally follow Third Normal Form (3NF).

Benefits include:

- Reduced redundancy
- Improved consistency
- Simplified maintenance

Analytical models may intentionally introduce controlled denormalization to optimize reporting and query performance.

---

# 15. Reference Data

Reference data includes stable values shared across the platform.

Examples:

- Countries
- Regions
- Property types
- Transaction types
- Currency codes
- User roles

Reference datasets should be centrally managed.

---

# 16. Master Data

Master data represents core business entities shared across applications.

Examples:

- Users
- Agencies
- Properties
- Geographic locations

Master data should maintain a single authoritative source.

---

# 17. Analytical Models

The warehouse derives analytical structures from operational data.

Examples include:

- Fact tables
- Dimension tables
- Aggregated views
- KPI datasets

These models support dashboards, reporting and AI.

---

# 18. AI Data Models

AI workloads extend the enterprise model with:

- Training datasets
- Validation datasets
- Feature datasets
- Embedding collections (future)
- Prediction results
- Model metadata

These structures complement, rather than replace, the enterprise data model.

---

# 19. Governance

The enterprise data model supports governance through:

- Data ownership
- Metadata
- Business glossary
- Lineage
- Classification
- Quality rules

Every major entity should have an identified owner.

---

# 20. Current State

Current implementation includes:

- PostgreSQL relational schema
- Normalized operational data
- Warehouse schemas
- dbt transformation models
- OpenMetadata catalog
- AI metadata managed by MLflow

The logical enterprise model is progressively implemented across the platform.

---

# 21. Future Evolution

Future enhancements may include:

- Knowledge graph
- Semantic relationships
- Vector representations
- Feature Store
- Event-driven data model
- Real-time entities

The conceptual model should remain stable despite technological evolution.

---

# 22. Architecture Decisions

Key modeling decisions include:

- Three-level modeling approach
- Business-first design
- Stable identifiers
- Controlled denormalization for analytics
- Centralized master data
- Shared reference data
- Technology-independent conceptual modeling

---

# 23. Related Documents

- Data Architecture
- Data Warehouse
- Data Governance
- Metadata Management
- Data Lineage
- Master & Reference Data
- MCD (Merise)
- Business Glossary