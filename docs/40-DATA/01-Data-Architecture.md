# Data Architecture — Real Estate Intelligence Platform

**Version:** 2.0  
**Status:** Baseline aligned with StarterPack and Data Model V2  
**Primary DBMS:** PostgreSQL  
**Orchestration:** Apache Airflow  
**Transformation:** SQL / Python / dbt where justified  
**Metadata & Governance:** OpenMetadata  
**Object Storage:** MinIO  

---

# 1. Purpose

This document defines the target Data architecture of the Real Estate Intelligence Platform.

The architecture must support:

```text
Legacy migration
+
Heterogeneous ingestion
+
Operational transactions
+
Analytics
+
AI / Matching
+
Governance
+
Traceability
```

The target is not a single database receiving every source directly.

The architecture deliberately separates data by responsibility.

---

# 2. Architecture Principles

The main principles are:

```text
Preserve source data
Normalize before operational use
Separate OLTP from analytics
Version important business data
Measure before scaling
Minimize personal data propagation
Keep lineage
Automate repeatable transformations
```

---

# 3. Main Data Domains

The platform processes several classes of data:

```text
Legacy relational data
Operational relational data
Generated search criteria
Generated property advertisements
Semi-structured JSON
Documents
Analytics data
ML / AI metadata
Observability data
```

These data types have different requirements and must not all be treated identically.

---

# 4. Legacy Data

The inherited system provided by the StarterPack contains only:

```text
secteurs
utilisateurs
mandats
```

under the PostgreSQL schema:

```text
"Fil_Rouge_Depart"
```

The legacy schema is the migration source.

Rule:

```text
LEGACY
=
READ / AUDIT / MIGRATION SOURCE
```

It must not be modified as the new operational model.

---

# 5. Legacy Architecture

```text
"Fil_Rouge_Depart"
│
├── secteurs
├── utilisateurs
└── mandats
```

This model intentionally contains structural limitations that the project must correct.

---

# 6. Legacy Data Flow

```text
StarterPack PgSQL.sql
        |
        v
"Fil_Rouge_Depart"
        |
        v
Audit
        |
        v
Migration
        |
        v
real_estate
```

---

# 7. Generated Data

The StarterPack also provides a generator for synthetic real-estate data.

It creates:

```text
fixtures/annonces/recherches.csv
fixtures/annonces/annonces.csv
fixtures/annonces/json/annonce_XXXX.json
```

These files are not the inherited database.

They simulate future Data ingestion workloads.

---

# 8. Why Generated Data is Different

The generated announcements intentionally contain:

```text
missing fields
renamed fields
different date formats
optional geolocation
heterogeneous structures
nested data
```

This means they should not be inserted directly into:

```text
real_estate.bien
```

without transformation.

---

# 9. Complete Data Architecture

```text
                         +----------------------+
                         |   Legacy Fixtures    |
                         | Fil_Rouge_Depart     |
                         +----------+-----------+
                                    |
                                    | migration
                                    v
                         +----------------------+
                         |   real_estate OLTP   |
                         +----------+-----------+
                                    |
                                    |
                                    +----------------------+
                                                           |
                                                           v
Generated / External Sources                    Operational Application
        |                                                  |
        v                                                  |
      RAW                                                  |
        |                                                  |
        v                                                  |
     STAGING                                               |
        |                                                  |
        +---------------------> real_estate <---------------+
                                    |
                                    v
                                STAGING/ELT
                                    |
                                    v
                                WAREHOUSE
                                    |
                                    v
                                ANALYTICS
                                    |
                   +----------------+----------------+
                   |                                 |
                   v                                 v
                  BI                              AI / ML
```

---

# 10. PostgreSQL Logical Schemas

The target PostgreSQL architecture uses logical schemas:

```text
real_estate
raw
staging
warehouse
analytics
```

Each schema has a specific responsibility.

---

# 11. real_estate

Purpose:

```text
canonical operational data
```

It contains normalized business entities such as:

```text
client
chasseur
secteur
mandat
mandat_secteur
demande
demande_version
source
bien
presentation
commentaire
document
bareme_commission
paiement
```

This schema represents the primary OLTP model.

---

# 12. raw

Purpose:

```text
preserve source representation
```

Examples:

```text
raw.annonce_json
raw.annonce_csv
raw.recherche_csv
```

The RAW layer should preserve source data with minimal transformation.

---

# 13. Why RAW Exists

RAW enables:

```text
audit
reprocessing
debugging
schema-drift investigation
lineage
```

Without RAW, a transformation error can destroy the ability to reconstruct the original input.

---

# 14. RAW Is Not Canonical

RAW data may contain:

```text
invalid dates
unexpected field names
missing fields
duplicate records
incorrect formats
```

It must not be exposed as trusted operational data.

---

# 15. staging

Purpose:

```text
cleaning
standardization
validation
preparation
```

Example:

```text
raw price:
"245 000 €"
```

becomes:

```text
staging price:
245000.00
```

---

# 16. STAGING Responsibilities

The staging layer can handle:

```text
column renaming
type conversion
date parsing
normalization
deduplication
quality checks
source mapping
```

---

# 17. Canonicalization

After validation:

```text
STAGING
    |
    v
real_estate.bien
```

The canonical model should have stable field names and types independent of source-specific formats.

---

# 18. Source Mapping

Example:

```text
Source A:
prix_bien
```

```text
Source B:
price
```

```text
Source C:
montant
```

all normalize to:

```text
BIEN.prix
```

---

# 19. Date Normalization

Generated source dates may arrive as:

```text
YYYY-MM-DD
DD/MM/YYYY
ISO datetime
textual French date
timestamp
US date
```

STAGING must normalize them before insertion into canonical tables.

---

# 20. Geolocation

Latitude/longitude may be:

```text
present
missing
partially available
```

The canonical model allows nullable geolocation.

The absence of coordinates should not reject an otherwise valid property record.

---

# 21. Structured Search Criteria

The generator produces structured search data such as:

```text
ville
code_postal
type_bien
budget_max
surface_min
nb_pieces_min
nb_chambres_min
dpe_max
criteres_souhaites
```

These map naturally into:

```text
DEMANDE
+
DEMANDE_VERSION
```

---

# 22. Operational OLTP Flow

```text
Client
   |
   v
Mandat
   |
   v
Demande
   |
   v
Demande Version
```

and:

```text
Source
   |
   v
Bien
```

then:

```text
Demande Version
      +
     Bien
      |
      v
Presentation
```

---

# 23. Feedback Flow

```text
Presentation
    |
    v
Client / Chasseur
    |
    v
Commentaire
```

These comments may later support:

```text
search requalification
analytics
future ML
```

---

# 24. Migration vs Ingestion

The project distinguishes:

```text
MIGRATION
```

from:

```text
INGESTION
```

Migration concerns:

```text
legacy database
```

Ingestion concerns:

```text
new or generated sources
```

---

# 25. Migration Flow

```text
"Fil_Rouge_Depart"
        |
        v
mapping
        |
        v
real_estate
```

Examples:

```text
utilisateurs -> client/chasseur
secteurs -> secteur
mandats -> mandat + demande + demande_version
```

---

# 26. Ingestion Flow

```text
CSV / JSON / API
      |
      v
RAW
      |
      v
STAGING
      |
      v
real_estate
```

---

# 27. Migration Must Preserve History

The migration must avoid destroying or fabricating information.

Example:

if the legacy system does not contain:

```text
mode_signature
```

the target should record:

```text
INCONNU
```

rather than invent:

```text
ELECTRONIQUE
```

---

# 28. Free-Text Legacy Criteria

Legacy:

```text
mandats.description_recherche
```

Target:

```text
DEMANDE_VERSION
```

The original free text should be preserved while structured extraction is performed.

---

# 29. Legacy Description Preservation

Recommended field:

```text
description_recherche_legacy
```

This permits:

```text
audit
manual review
future extraction
AI-assisted parsing
```

---

# 30. Data Warehouse

The operational model is not the analytical model.

Analytical workloads will use:

```text
warehouse
```

for dimensional structures.

---

# 31. OLTP vs OLAP

```text
OLTP
=
current transactions
integrity
normalized model
short operational queries
```

```text
OLAP
=
aggregations
historical analysis
KPI
reporting
decision support
```

---

# 32. Warehouse Architecture

Candidate dimensional architecture:

```text
dim_date
dim_client
dim_chasseur
dim_property
dim_source
dim_mandate

fact_presentation
```

The exact warehouse schema will be implemented separately.

---

# 33. Fact Grain

For:

```text
fact_presentation
```

candidate grain:

```text
one property
presented/selected
for one demand version
```

---

# 34. Analytics Schema

Purpose:

```text
business-oriented views
```

Examples:

```text
analytics.matching_performance
analytics.source_performance
analytics.mandate_summary
analytics.property_market_summary
```

---

# 35. Why analytics is separate

Consumers should not need to understand the full warehouse model.

```text
WAREHOUSE
    |
    v
ANALYTICS
    |
    +--> dashboard
    +--> BI
    +--> business analysis
```

---

# 36. Airflow

Airflow orchestrates:

```text
migration-related jobs where needed
ingestion
staging
transformation
data-quality checks
warehouse loading
AI workflows
```

Airflow does not replace PostgreSQL.

---

# 37. Airflow Responsibilities

```text
schedule
dependencies
retry
failure handling
execution history
```

---

# 38. ELT Strategy

For relational analytics, the preferred architecture is:

```text
Extract
   |
   v
Load
   |
   v
Transform
```

particularly:

```text
OLTP
 |
 v
STAGING
 |
 v
SQL/dbt
 |
 v
WAREHOUSE
```

---

# 39. dbt

dbt can manage:

```text
SQL models
dependencies
tests
documentation
lineage
```

It is complementary to Airflow.

---

# 40. Airflow vs dbt

```text
Airflow
=
orchestration
```

```text
dbt
=
SQL transformation
```

---

# 41. OpenMetadata

OpenMetadata provides the metadata governance layer.

Target capabilities:

```text
catalog
ownership
descriptions
classification
lineage
profiling
data quality
```

---

# 42. Data Lineage

Target lineage:

```text
Generated JSON
     |
     v
RAW
     |
     v
STAGING
     |
     v
BIEN
     |
     v
WAREHOUSE
     |
     v
ANALYTICS KPI
```

and:

```text
Legacy MANDATS
      |
      v
MANDAT
      |
      v
DEMANDE
      |
      v
DEMANDE_VERSION
```

---

# 43. Data Quality

Data quality must be applied throughout the pipeline.

Examples:

```text
not null
unique
accepted values
relationships
range checks
freshness
row counts
```

---

# 44. RAW Quality

RAW should primarily validate:

```text
file received
record readable
minimal technical structure
```

It should not aggressively reject source imperfections.

---

# 45. STAGING Quality

STAGING validates:

```text
types
required business fields
date normalization
price normalization
deduplication
```

---

# 46. Canonical Quality

`real_estate` applies:

```text
PK
FK
UNIQUE
CHECK
NOT NULL
```

for trusted operational integrity.

---

# 47. Property Deduplication

A canonical property should be unique within its source using:

```text
(id_source, reference_externe)
```

This supports idempotent ingestion.

---

# 48. Idempotence

Pipeline principle:

```text
same logical source record
+
pipeline replay
=
no uncontrolled duplication
```

---

# 49. UPSERT

PostgreSQL may use:

```sql
INSERT ... ON CONFLICT ...
```

for controlled ingestion where appropriate.

---

# 50. Matching Data Architecture

The matching engine should primarily consume:

```text
DEMANDE_VERSION
```

and:

```text
BIEN
```

rather than entire client records.

---

# 51. Matching Flow

```text
DEMANDE_VERSION
        |
        v
Hard filters
        |
        v
Candidate BIEN
        |
        v
Scoring / Matching
        |
        v
PRESENTATION
```

---

# 52. Structured First

Exact constraints should be processed using structured data.

Examples:

```text
budget
surface
city
property type
```

These do not require a LLM.

---

# 53. Semantic Enrichment

Unstructured criteria can later use:

```text
embeddings
LLM
RAG
```

when justified.

---

# 54. AI Training Requirement

The platform data model must support AI and matching.

The certification project requires the design of the model inputs and features.

Actual training is an optional implementation enhancement rather than a prerequisite for the Data architecture.

---

# 55. MLflow

If model training is implemented, MLflow provides:

```text
experiment tracking
metrics
parameters
artifacts
model versions
```

---

# 56. MinIO

MinIO can store:

```text
documents
ML artifacts
raw files
future datasets
```

depending on the implementation.

---

# 57. PostgreSQL vs Object Storage

Use PostgreSQL for:

```text
structured metadata
relations
transactions
```

Use MinIO for:

```text
large binary objects
files
artifacts
```

---

# 58. Documents

Recommended architecture:

```text
PostgreSQL
    |
    +--> document metadata

MinIO
    |
    +--> actual file
```

---

# 59. RGPD

Personal data exists in:

```text
CLIENT
CHASSEUR
COMMENTAIRE
PAIEMENT
DOCUMENT
```

and potentially free-text content.

---

# 60. Data Minimization

Data must not be propagated into every layer automatically.

Example:

an analytical KPI usually does not need:

```text
email
phone
full identity
```

---

# 61. OLAP Minimization

Warehouse dimensions should store only fields required for analytics.

Avoid copying entire operational personal records.

---

# 62. AI Minimization

AI workflows should receive:

```text
relevant criteria
property features
authorized documents
```

rather than unrestricted database access.

---

# 63. Data Sovereignty

Sensitive processing should prefer the controlled local environment.

The target architecture uses:

```text
local PostgreSQL
local MinIO
local MLflow
local Ollama
```

for relevant workflows.

---

# 64. RAG Security

Retrieval must follow:

```text
Authentication
      |
      v
Authorization
      |
      v
Allowed documents
      |
      v
Retrieval
      |
      v
LLM
```

---

# 65. Vector Storage

Potential options:

```text
PostgreSQL + pgvector
```

or:

```text
Qdrant
```

Qdrant is not currently mandatory.

The decision must be benchmarked and documented.

---

# 66. 3V — Volume

Expected future scale includes:

```text
thousands of mandates per week
```

and:

```text
hundreds or thousands of properties
per search
```

The architecture must therefore support growth.

---

# 67. 3V — Velocity

The expected workload is primarily:

```text
batch
scheduled
moderate-frequency ingestion
```

rather than strict real-time streaming.

This currently supports the use of Airflow.

---

# 68. 3V — Variety

The platform receives:

```text
relational data
CSV
JSON
documents
text
metrics
logs
traces
```

The generated announcements explicitly simulate data variety.

---

# 69. Why Kafka is not mandatory

Kafka should not be added merely because the project handles Data.

It becomes relevant only if requirements include:

```text
high event rate
multiple consumers
durable replay
continuous streaming
low-latency event processing
```

---

# 70. Why Spark is not mandatory

Spark is not required just because datasets grow.

PostgreSQL and Airflow remain suitable until measurements show otherwise.

---

# 71. Scaling Strategy

Preferred evolution sequence:

```text
measure
 |
 v
optimize query/schema
 |
 v
right-size resources
 |
 v
separate workloads
 |
 v
consider specialized technology
```

---

# 72. PostgreSQL Scaling Options

Potential steps:

```text
indexes
query optimization
connection pooling
better storage
more RAM/CPU
replicas
partitioning
OLTP/OLAP separation
```

---

# 73. Partitioning

Potential future candidates:

```text
bien
presentation
commentaire
warehouse facts
```

Partitioning will only be introduced based on measured volume and query patterns.

---

# 74. Observability

Data pipelines should expose:

```text
execution status
duration
row counts
failures
freshness
quality results
```

---

# 75. Candidate Pipeline Metrics

```text
rows_ingested
rows_rejected
rows_normalized
pipeline_duration
pipeline_success
pipeline_failure
data_freshness
quality_failures
```

---

# 76. Auditability

The system must allow questions such as:

```text
Where did this property come from?
Which transformation produced it?
Which demand version was used?
Which pipeline run loaded it?
```

---

# 77. Reproducibility

Data transformations should be version-controlled.

```text
Git
+
SQL
+
Python
+
Airflow
+
dbt
```

---

# 78. Repository Mapping

Implementation locations:

```text
database/migrations/
database/oltp/
database/olap/
database/tests/

pipelines/airflow/
pipelines/dbt/
```

Documentation stays under:

```text
docs/
```

---

# 79. Documentation vs Runtime

This document describes the target architecture.

Actual evidence will come from:

```text
executed migration
loaded RAW data
staging transformations
canonical row counts
Airflow DAG runs
dbt tests
OpenMetadata lineage
warehouse queries
```

---

# 80. Source of Truth

Canonical Data Model:

```text
docs/40-DATA/02-Data-Model.md
```

Detailed MERISE chain:

```text
docs/evidence/05-BC05/C1-MCD-Migration-SQL/
```

OLTP:

```text
docs/evidence/05-BC05/C2-OLTP-Optimisation/
```

OLAP:

```text
docs/evidence/05-BC05/C3-OLAP-Alimentation/
```

3V:

```text
docs/evidence/05-BC05/C4-Volume-Velocite-Variete/
```

---

# 81. Current Status

| Layer | Status |
|---|---|
| Legacy source definition | COMPLETE |
| Canonical model | V2 COMPLETE |
| Generated-data integration design | COMPLETE |
| RAW architecture | DEFINED |
| STAGING architecture | DEFINED |
| OLTP architecture | DEFINED |
| OLAP architecture | DEFINED |
| Airflow strategy | DEFINED |
| dbt strategy | DEFINED |
| OpenMetadata strategy | DEFINED |
| RGPD integration | DEFINED |
| AI data flow | DEFINED |
| Runtime ingestion | PENDING |
| Runtime migration | PENDING |
| Warehouse execution | PENDING |
| Lineage runtime evidence | PENDING |

---

# 82. Conclusion

The Data architecture now distinguishes five fundamental concerns:

```text
LEGACY
    |
    v
MIGRATION


GENERATED / EXTERNAL DATA
    |
    v
RAW
    |
    v
STAGING
    |
    v
CANONICAL OLTP
    |
    v
WAREHOUSE
    |
    v
ANALYTICS / AI
```

This structure allows the project to preserve source truth, normalize heterogeneous data, maintain transactional integrity, support analytics, prepare AI features and retain governance and traceability.

---

**DATA ARCHITECTURE V2 — ALIGNED WITH STARTERPACK AND TARGET DATA MODEL**