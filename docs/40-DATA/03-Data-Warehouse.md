# Data Warehouse Architecture — Real Estate Intelligence Platform

**Version:** 3.0
**Status:** Implemented / Runtime Verified
**Owner:** Bastri Murad
**Project:** PROJECT_FIL_ROUGE / CHASSE_IMMOBILIERE
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-09-15

---

# 1. Purpose

This document defines the Data Warehouse architecture of the Real Estate Intelligence Platform.

It describes how data moves from ingestion through operational storage into dimensional analytical models and finally into reporting, observability, governance and AI workloads.

The implemented analytical chain is:

```text id="m90sna"
Sources
   |
   v
RAW
   |
   v
STAGING
   |
   v
real_estate OLTP
   |
   v
WAREHOUSE
   |
   v
dbt / ANALYTICS
   |
   +--> Business Analytics
   +--> Data Quality
   +--> Prometheus / Grafana
   +--> ML / AI datasets
   +--> OpenMetadata
```

The warehouse provides a trusted analytical representation without changing the responsibilities of the transactional `real_estate` schema.

---

# 2. Scope

This document covers:

```text id="l8c4cc"
RAW ingestion
STAGING transformations
OLTP -> Warehouse propagation
dimensional modeling
fact tables
dimension tables
dbt transformations
analytical marts
Airflow orchestration
Data Quality
financial analytics
observability integration
metadata and lineage
AI / ML analytical consumption
```

The detailed transactional model is documented separately in:

```text id="yvtux9"
docs/40-DATA/02-Data-Model.md
```

---

# 3. Architectural Objectives

The warehouse architecture aims to:

* separate transactional and analytical workloads;
* preserve raw source data;
* standardize and validate incoming data;
* provide stable analytical grains;
* centralize reusable business metrics;
* preserve financial consistency;
* provide reproducible analytical transformations;
* support reporting and dashboards;
* expose trusted datasets for ML experimentation;
* provide lineage and metadata;
* make Data Quality observable;
* enable automated pipeline execution.

---

# 4. Architectural Principles

The implementation follows these principles:

```text id="3vm0hb"
Layered data architecture

RAW data preservation

Explicit STAGING validation

Transactional integrity in OLTP

Dimensional modeling for analytics

Stable fact-table grain

Reproducible transformations

Automated Data Quality

Version-controlled SQL and dbt

Orchestrated execution

Metadata-driven governance

Observable pipelines

No direct manual warehouse population
for normal production flows
```

A key principle is:

```text id="7h3cvy"
OLTP != OLAP
```

The transactional database remains responsible for business state and integrity.

The warehouse remains responsible for analytical representation.

---

# 5. Implemented Data Architecture

The current implemented path is:

```text id="6o28hl"
External / Generated Sources
          |
          v
       Airflow
          |
          v
      raw schema
          |
          v
    staging schema
          |
          v
 real_estate schema
       (OLTP)
          |
          v
   warehouse schema
       (Gold)
          |
          v
        dbt
          |
          v
  analytics / marts
```

Cross-cutting services:

```text id="c5rd1j"
OpenMetadata
     |
metadata / lineage / profiling / DQ

Prometheus + Grafana
     |
pipeline / data / business observability

MLflow
     |
ML experiments / model lifecycle
```

---

# 6. PostgreSQL Schemas

The data platform uses several PostgreSQL schemas with distinct responsibilities.

| Schema              | Responsibility                   |
| ------------------- | -------------------------------- |
| `raw`               | Source-oriented ingestion        |
| `staging`           | Cleaning and standardization     |
| `real_estate`       | Transactional OLTP model         |
| `warehouse`         | Dimensional analytical model     |
| `analytics`         | Analytical consumption and marts |
| `migration_control` | Database migration tracking      |
| `Fil_Rouge_Depart`  | Historical starter/legacy data   |

This separation prevents analytical transformations from being mixed with transactional business logic.

---

# 7. Bronze / Silver / Gold Mapping

The architecture can also be represented as:

```text id="72itk6"
BRONZE
=
raw

SILVER
=
staging

OPERATIONAL CORE
=
real_estate

GOLD
=
warehouse
+
analytics
```

OpenMetadata is not a Gold data layer.

It provides:

```text id="o1tfh3"
catalog
metadata
lineage
governance
profiling
quality visibility
```

---

# 8. RAW Layer

The `raw` schema preserves ingested source data as close as practical to its original representation.

Responsibilities:

```text id="8ihyz8"
source preservation
ingestion traceability
reprocessing capability
initial technical validation
```

RAW should avoid embedding complex business logic.

Its purpose is to answer:

> What did the source provide?

rather than:

> What is the final business interpretation?

---

# 9. STAGING Layer

The `staging` schema prepares data for operational integration.

Responsibilities include:

```text id="3p7gzz"
typing
normalization
standardization
deduplication
null handling
schema validation
business preparation
```

The staging layer acts as the controlled boundary between source-oriented data and the canonical operational model.

---

# 10. OLTP Layer

The `real_estate` schema contains the operational model.

Examples:

```text id="b0g6rh"
client
chasseur
utilisateur

mandat
mandat_periode

demande
demande_affectation
demande_version

bien
source
presentation
visite

vente
paiement

audit_log
```

The OLTP layer is responsible for:

```text id="5my89f"
transactional consistency
business state
referential integrity
auditability
operational history
financial calculation snapshots
```

The warehouse does not replace these responsibilities.

---

# 11. Warehouse Layer

The `warehouse` schema provides the dimensional analytical model.

Its primary structures are:

```text id="7h1j9e"
Dimensions
Facts
Bridge tables
```

Dimensions provide analytical context.

Facts represent measurable events or states at explicitly defined grains.

---

# 12. Implemented Dimensions

The warehouse includes dimensions such as:

```text id="2jm15e"
dim_date
dim_source
dim_localisation
dim_bien
dim_chasseur
dim_client
dim_demande_version
dim_secteur
```

These dimensions provide reusable analytical axes for the fact tables.

---

# 13. DIM_DATE

`dim_date` provides the shared calendar dimension.

The implemented calendar covers:

```text id="5a86rr"
2020-01-01
through
2035-12-31
```

with:

```text id="adkbb5"
5844 rows
```

Date keys use a representation compatible with:

```text id="15cr9d"
YYYYMMDD
```

Example:

```text id="4knyhw"
2026-09-14
    ->
20260914
```

This allows transaction dates to be analyzed consistently across facts.

---

# 14. Bridge Table

The many-to-many relationship between mandates and sectors is represented analytically through:

```text id="h7ihqr"
bridge_mandat_secteur
```

This preserves the ability to analyze a mandate across multiple geographical sectors without duplicating the mandate fact grain.

---

# 15. Implemented Fact Tables

The warehouse currently includes facts such as:

```text id="sdtqf8"
fact_annonce
fact_mandat
fact_mandat_periode
fact_paiement
fact_presentation
fact_demande
fact_matching
fact_bien_daily
```

Each fact has a specific analytical grain.

Facts must not be merged merely because they reference related business entities.

---

# 16. Fact Grain Principle

A fundamental dimensional-modeling rule used by the project is:

> Define the grain before defining the measures.

For example:

```text id="5nqgoi"
MANDAT
```

and:

```text id="hcntr7"
MANDAT_PERIODE
```

are related but do not have the same grain.

Therefore:

```text id="j1lpfh"
fact_mandat
```

and:

```text id="d11rxg"
fact_mandat_periode
```

remain separate.

This avoids duplicating mandate-level measures when a mandate has multiple contractual periods.

---

# 17. FACT_MANDAT

`fact_mandat` represents the analytical mandate grain.

Conceptually:

```text id="lxy56q"
1 row
=
1 mandate
```

It supports analyses around:

```text id="c34v2x"
mandate counts
mandate status
client
hunter
contract characteristics
dates
```

The introduction of mandate renewals did **not** change this grain.

---

# 18. FACT_MANDAT_PERIODE

`fact_mandat_periode` was introduced to represent the contractual-period grain.

Conceptually:

```text id="kvkxwg"
1 row
=
1 mandate period
```

It contains analytical information such as:

```text id="7q3s3b"
mandat_periode_fact_key
mandat_fact_key
date keys
duration
period count
legacy-history indicator
```

This supports:

```text id="ynjdsb"
initial period analysis
renewal analysis
contract duration
period chronology
legacy comparison
```

without changing `fact_mandat`.

---

# 19. Why Separate Mandate and Mandate Period?

Consider:

```text id="h3sm7u"
Mandat 11
```

with:

```text id="5ow4py"
Period 1
INITIAL

Period 2
RENOUVELLEMENT
```

If both periods were represented by duplicating the mandate fact, a query counting mandates could incorrectly return:

```text id="ml77a6"
2
```

instead of:

```text id="b2fak4"
1
```

The architecture therefore preserves:

```text id="vr9vse"
fact_mandat
=
mandate grain
```

and:

```text id="sfuzhm"
fact_mandat_periode
=
period grain
```

---

# 20. FACT_PAIEMENT

`fact_paiement` represents the analytical payment grain.

Conceptually:

```text id="4c5yka"
1 row
=
1 source payment
```

The source is:

```text id="3pc4g4"
real_estate.paiement
```

The fact retains the source payment identifier for reconciliation.

---

# 21. FACT_PAIEMENT Analytical Content

The fact includes financial measures such as:

```text id="9g3w3d"
montant_achat
montant_honoraires
montant_chasseur
paiement_count
```

and analytical context including:

```text id="g93f46"
mandate
client
hunter
status
act date
company-fee receipt date
hunter-payment date
source payment
source commission scale
```

The analytical representation therefore supports both financial totals and lifecycle analysis.

---

# 22. Payment Date Dimensions

The payment fact contains distinct date keys because the following events are not equivalent:

```text id="3ebfvn"
acte authentique
```

```text id="vk77nh"
réception des honoraires
```

```text id="s15m9d"
paiement du chasseur
```

Therefore the fact can reference:

```text id="63qzsl"
date_acte_authentique_key

date_reception_honoraires_key

date_paiement_chasseur_key
```

This allows questions such as:

```text id="s72wzv"
When was the sale completed?

When did the company receive its fees?

When was the hunter paid?
```

to be analyzed independently.

---

# 23. Financial Source of Truth

The transactional financial source is:

```text id="enl4u9"
real_estate.paiement
```

The analytical representation is:

```text id="9n54bm"
warehouse.fact_paiement
```

The relationship is:

```text id="syvnqh"
real_estate.paiement
        |
        | controlled warehouse load
        v
warehouse.fact_paiement
```

The warehouse does not independently recalculate the authoritative payment result.

It propagates the validated transactional values.

---

# 24. Financial Calculation Snapshot

The OLTP payment preserves the detailed remuneration calculation, including:

```text id="7w1ymg"
eligibility
performance counters
performance notes
performance score
base rate
seniority adjustment
performance modulation
final rate
company fees
hunter remuneration
```

The warehouse receives the resulting analytical financial measures.

This preserves the separation:

```text id="8ggn7v"
OLTP
=
authoritative deterministic calculation

Warehouse
=
analytical representation
```

---

# 25. Controlled Financial E2E Evidence

A controlled E2E validation scenario produced:

```text id="a7i8lr"
Vente    = 3
Paiement = 9
```

Transaction:

```text id="08mgej"
Purchase amount
=
300000.00 €
```

Company fees:

```text id="7olzfn"
10500.00 €
```

Hunter remuneration:

```text id="4b6rxo"
3939.60 €
```

Final remuneration rate:

```text id="wz00kh"
37.52 %
```

Payment status:

```text id="dtflva"
PAYE
```

This is a controlled validation fixture, not a claim of a genuine commercial transaction.

---

# 26. Runtime FACT_PAIEMENT Evidence

Before the normal warehouse load, the controlled payment was absent from `fact_paiement`.

The normal Airflow pipeline was then executed.

After the pipeline:

```text id="ns26ly"
id_paiement_source
=
9
```

was present in `warehouse.fact_paiement`.

Observed analytical values included:

```text id="0kkw9w"
paiement_fact_key             = 1

id_paiement_source            = 9

id_bareme_source              = 24

mandat_fact_key               = 5

client_key                    = 18

chasseur_key                  = 2

date_acte_authentique_key     = 20260914

date_reception_honoraires_key = 20260914

date_paiement_chasseur_key    = 20260914

montant_achat                 = 300000.00

montant_honoraires            = 10500.00

montant_chasseur              = 3939.60

statut                        = PAYE

paiement_count                = 1
```

The warehouse load timestamp was also persisted.

---

# 27. Significance of the Payment Evidence

This runtime validation proves the path:

```text id="idjrcw"
Business API
     |
     v
real_estate.paiement
     |
     v
Airflow
     |
     v
load_warehouse.py
     |
     v
warehouse.fact_paiement
```

No manual insertion into the warehouse was required.

This distinction is important:

```text id="nvbckq"
manual SQL insertion
!=
pipeline validation
```

The validated result came through the normal data pipeline.

---

# 28. Airflow Orchestration

The main Real Estate pipeline is orchestrated by Airflow.

DAG:

```text id="b7brzi"
real_estate_ingestion
```

The DAG uses:

```text id="f9sd8s"
KubernetesExecutor
+
KubernetesPodOperator
```

for containerized execution.

The data-pipeline image is deployed through the project CI/CD workflow.

---

# 29. Implemented DAG Flow

The implemented dependency chain is:

```text id="0dr5t3"
start
  |
  v
generate_source_data
  |
  v
load_raw
  |
  v
validate_raw
  |
  v
transform_staging
  |
  v
validate_staging
  |
  v
load_oltp
  |
  v
validate_oltp
  |
  v
load_warehouse
  |
  v
validate_warehouse
  |
  v
dbt_run
  |
  v
dbt_test
  |
  v
collect_metrics
  |
  v
end
```

The DAG currently uses manual triggering:

```text id="ltwe48"
schedule = None
```

and:

```text id="pk5ks8"
max_active_runs = 1
```

---

# 30. Warehouse Load

The Gold load is performed by:

```text id="h58d9u"
database/olap/load_warehouse.py
```

The loader contains dedicated fact-loading logic, including:

```text id="3spcqz"
load_fact_paiement(...)
```

The warehouse population is therefore part of the normal version-controlled data-pipeline image.

---

# 31. Warehouse Validation

After loading Gold, Airflow executes warehouse Data Quality validation.

The relevant SQL suite includes:

```text id="0uuj1q"
database/tests/007_warehouse_data_quality.sql
```

The pipeline order is deliberately:

```text id="z9hxlz"
load_warehouse
      |
      v
validate_warehouse
      |
      v
dbt_run
      |
      v
dbt_test
```

A critical warehouse validation failure therefore prevents the normal downstream analytical chain from being considered successful.

---

# 32. Financial Data Quality

Financial Data Quality includes reconciliation between:

```text id="8k6dtf"
real_estate.paiement
```

and:

```text id="vvz3p5"
warehouse.fact_paiement
```

The validation covers the payment row count and detailed financial consistency.

---

# 33. Payment Financial Reconciliation

The strengthened controls compare:

```text id="p55wrq"
montant_achat

montant_honoraires

montant_chasseur

statut
```

between OLTP and warehouse.

The comparison uses null-safe semantics where required.

The expected invariant is:

```text id="ctov7v"
OLTP financial value
=
Warehouse financial value
```

for the same source payment.

---

# 34. Financial Business Consistency

The warehouse quality suite also checks:

```text id="uf71kr"
montant_chasseur
<=
montant_honoraires
```

A hunter remuneration greater than the company's fee base would therefore be treated as a Data Quality anomaly.

---

# 35. PAYE Completeness

For payments with:

```text id="gkm2y3"
statut = PAYE
```

the analytical model expects the relevant lifecycle dates to be available.

This includes:

```text id="e81b2i"
date_reception_honoraires_key

date_paiement_chasseur_key
```

This prevents a payment from appearing analytically complete while missing its core lifecycle dates.

---

# 36. Date Reconciliation

Date keys in `fact_paiement` are reconciled with the corresponding OLTP dates.

Conceptually:

```text id="3p0txq"
2026-09-14
      |
      v
20260914
```

The comparison covers:

```text id="gqgw2i"
act date

company fee receipt date

hunter payment date
```

---

# 37. dbt Transformation Layer

After warehouse validation, Airflow executes:

```text id="igzwdq"
dbt run
```

followed by:

```text id="z06g4m"
dbt test
```

dbt is responsible for:

```text id="myrcmw"
analytical SQL transformations
model dependencies
tests
documentation
lineage contribution
reusable marts
```

dbt does not replace the transactional business logic implemented in the application and PostgreSQL OLTP layer.

---

# 38. Implemented dbt Marts

Current analytical marts include:

```text id="50lmr6"
mart_mandat_performance

mart_market_by_city

mart_market_by_dpe

mart_market_by_property_type

mart_market_by_source

mart_market_evolution

mart_market_overview
```

These models provide consumption-oriented analytical representations over the underlying warehouse.

---

# 39. Market Analytics

The market marts support analyses such as:

```text id="pb2cga"
market overview

city comparison

DPE distribution

property-type distribution

source comparison

market evolution
```

This separates consumption queries from the lower-level warehouse facts and dimensions.

---

# 40. Mandate Analytics

`mart_mandat_performance` provides an analytical consumption layer around mandate activity.

The introduction of:

```text id="ednmqu"
fact_mandat_periode
```

allows future and current mandate analytics to distinguish:

```text id="frb5ig"
mandate-level performance
```

from:

```text id="2pp2so"
contract-period / renewal behavior
```

without corrupting fact grain.

---

# 41. Data Quality by Layer

Data Quality is executed across the platform layers.

Current monitored layers include:

```text id="y2tt3g"
raw
staging
oltp
warehouse
```

Each layer has its own validation responsibilities.

Conceptually:

```text id="34wwmv"
RAW
 |
 +--> structural/source quality

STAGING
 |
 +--> standardization quality

OLTP
 |
 +--> business/integrity quality

WAREHOUSE
 |
 +--> analytical/reconciliation quality
```

---

# 42. Pipeline Quality Gate

The pipeline follows:

```text id="vsv4qq"
LOAD
 |
 v
VALIDATE
 |
 +-- failure --> pipeline failure
 |
 v
NEXT LAYER
```

This pattern is repeated across the architecture.

It prevents invalid data from silently progressing through the entire analytical chain.

---

# 43. Runtime Pipeline Validation

A complete normal Airflow run after the latest warehouse and DQ changes completed successfully.

Run:

```text id="7a4s4r"
manual__2026-09-14T22:45:30+00:00
```

Tasks completed successfully:

```text id="1h7j9u"
start

generate_source_data

load_raw

validate_raw

transform_staging

validate_staging

load_oltp

validate_oltp

load_warehouse

validate_warehouse

dbt_run

dbt_test

collect_metrics

end
```

This provides runtime evidence for the complete normal pipeline chain.

---

# 44. Metrics Collection

After dbt tests, Airflow executes:

```text id="a75vx7"
collect_metrics
```

using:

```text id="px2yxb"
observability/metrics/collect_metrics.py
```

The collector exports platform and business metrics.

---

# 45. Pushgateway Integration

Metrics are pushed to:

```text id="flf8b6"
Prometheus Pushgateway
```

using the Real Estate data-platform job.

Conceptually:

```text id="lh5ck5"
Airflow
  |
  v
collect_metrics.py
  |
  v
Pushgateway
  |
  v
Prometheus
```

This makes batch-pipeline state observable by the monitoring stack.

---

# 46. Data Quality Metrics

Data Quality metrics expose the health of each layer.

The monitored state includes:

```text id="2tr03c"
RAW
STAGING
OLTP
WAREHOUSE
```

A healthy layer is represented through the corresponding exported status metric.

The pipeline also exports pass/fail counts for Data Quality execution.

---

# 47. Business Metrics

The collector exposes business-scale metrics such as:

```text id="6p2wvv"
clients

chasseurs

mandats

active mandates

biens

presentations

visites

paiements
```

This connects analytical data processing with platform observability.

---

# 48. Financial Metrics

The current financial metrics include:

```text id="g0f4ny"
real_estate_paiements_payes_total

real_estate_honoraires_total_euros

real_estate_remunerations_chasseur_total_euros

real_estate_taux_remuneration_moyen
```

These metrics are derived from validated business data and exported through the normal batch observability chain.

---

# 49. Financial Observability Lineage

The implemented financial lineage is:

```text id="cbf1c4"
real_estate.vente
        |
        v
real_estate.paiement
        |
        v
warehouse.fact_paiement
        |
        v
collect_metrics.py
        |
        v
Pushgateway
        |
        v
Prometheus
        |
        v
Grafana
```

This provides observability beyond simple infrastructure health.

The platform can expose business outcomes.

---

# 50. Grafana Financial KPIs

The Real Estate business dashboard includes:

```text id="ygqld5"
Paid Payments

Company Fees Collected

Hunter Remuneration Paid

Average Hunter Remuneration Rate
```

For the controlled E2E scenario, Grafana displayed:

```text id="1n00rl"
Paid Payments
=
1

Company Fees Collected
=
€10.50K

Hunter Remuneration Paid
=
€3.94K

Average Hunter Remuneration Rate
=
37.52 %
```

These values match the transactional and warehouse evidence.

---

# 51. End-to-End Financial Consistency

The same controlled scenario can therefore be followed across:

```text id="d5zglp"
API
 |
 v
OLTP
 |
 v
WAREHOUSE
 |
 v
METRICS
 |
 v
GRAFANA
```

with consistent values:

```text id="2spjdi"
Purchase
300000 €

Company fees
10500 €

Hunter remuneration
3939.60 €

Final rate
37.52 %

Payment
PAYE
```

This is a significant Data Platform validation because the value is not verified at only one layer.

---

# 52. Metadata Integration

OpenMetadata provides governance over the data platform.

It is used for:

```text id="s3jvl4"
cataloging
schema metadata
ownership
lineage
profiling
Data Quality visibility
classification
```

Integrated platform components include PostgreSQL, Airflow and dbt metadata.

---

# 53. OpenMetadata Responsibility

OpenMetadata should not be confused with the warehouse.

```text id="fvz9up"
PostgreSQL warehouse
=
analytical data storage
```

```text id="g3xdzj"
OpenMetadata
=
metadata / governance / lineage
```

Both components are complementary.

---

# 54. AI and ML Consumption

The warehouse can provide curated inputs for:

```text id="h56mx9"
matching evaluation

training datasets

validation datasets

feature engineering

market analytics

future predictive models
```

The current deterministic matching baseline is evaluated independently from the dimensional model.

MLflow is used for experiment tracking and ML lifecycle capabilities.

---

# 55. Warehouse and ML Separation

The warehouse should not embed model-training logic directly into dimensional tables.

Instead:

```text id="5n2r88"
Warehouse
    |
    v
Curated Dataset
    |
    v
Training / Evaluation
    |
    v
MLflow
```

This preserves analytical stability while allowing ML experimentation to evolve.

---

# 56. Security

Warehouse security follows the wider platform security architecture.

Important principles include:

```text id="mvpajv"
database authentication

least privilege

service-specific access

secret management

namespace isolation

backup protection

controlled analytical access
```

Sensitive operational attributes should only be propagated into analytical structures when required.

---

# 57. Deployment Model

The data platform runs on Kubernetes.

Key components include:

```text id="icffgn"
PostgreSQL

Airflow

dbt workloads

OpenMetadata

MLflow

Prometheus

Grafana

Pushgateway
```

Permanent deployment changes follow:

```text id="izl5gm"
Source repository
      |
      v
GitLab CI
      |
      v
GitOps repository
      |
      v
Argo CD
      |
      v
Kubernetes
```

Runtime `kubectl` operations are used primarily for inspection, evidence and controlled diagnostics.

---

# 58. Backup and Recovery

PostgreSQL is protected through the platform PRA mechanism.

The backup workflow includes:

```text id="fw7xns"
PostgreSQL
     |
     v
scheduled backup
     |
     v
external MinIO
```

A restore into an isolated PostgreSQL 16 environment has been validated.

The backup CronJob runs on:

```text id="56irsl"
0 2 * * *
```

The analytical platform therefore depends on a tested database recovery foundation.

---

# 59. Current Limitations

The architecture currently has several explicit limitations.

## Airflow scheduling

The primary Real Estate ingestion DAG is currently:

```text id="cfth7p"
schedule = None
```

It is therefore manually triggered rather than periodically scheduled.

---

## Pushgateway persistence

Pushgateway storage is currently ephemeral.

Therefore Pushgateway should not be treated as the authoritative historical store for business data.

Authoritative history remains in:

```text id="2njjmb"
PostgreSQL OLTP
+
Warehouse
```

---

## Streaming

The current architecture is batch-oriented.

Kafka or equivalent streaming infrastructure is not required by the validated current business flow.

---

## Lakehouse

No separate Databricks-style lakehouse is required for the current validated architecture.

The current stack already provides:

```text id="jjg94l"
RAW
STAGING
OLTP
WAREHOUSE
ANALYTICS
```

A lakehouse should only be introduced if a future requirement justifies the additional complexity.

---

# 60. Future Evolution

Potential future capabilities include:

```text id="dv1s3w"
larger external datasets

advanced geospatial analytics

additional financial marts

feature-store capabilities

streaming ingestion where justified

model-driven matching

additional ML training datasets

semantic / vector search where justified
```

These are evolutionary possibilities rather than current runtime claims.

The current architecture should remain the baseline until a concrete requirement requires a change.

---

# 61. Architecture Decisions

The current architecture is based on the following decisions:

| Decision                                  | Rationale                                            |
| ----------------------------------------- | ---------------------------------------------------- |
| PostgreSQL OLTP                           | Strong transactional integrity                       |
| PostgreSQL Warehouse                      | Sufficient for current analytical scale and platform |
| RAW/STAGING separation                    | Traceability and controlled transformation           |
| Separate OLTP and Warehouse schemas       | Workload and responsibility separation               |
| Dimensional Gold model                    | Stable business analytics                            |
| Separate mandate and mandate-period facts | Preserve analytical grain                            |
| `fact_paiement`                           | Financial analytics and reconciliation               |
| Airflow                                   | Pipeline orchestration                               |
| KubernetesPodOperator                     | Isolated containerized execution                     |
| dbt                                       | Version-controlled analytical transformations        |
| Data Quality gates                        | Prevent invalid downstream propagation               |
| OpenMetadata                              | Governance and lineage                               |
| Prometheus/Grafana                        | Operational and business observability               |
| MLflow                                    | ML lifecycle                                         |
| GitOps                                    | Reproducible deployment                              |

---

# 62. Source of Truth

For warehouse implementation claims, the project uses the following validation hierarchy:

```text id="7w4v5l"
Runtime evidence
      >
deployed source
      >
CI
      >
GitOps desired state
      >
documentation
      >
assumptions
```

A warehouse capability should not be described as runtime verified solely because it appears in documentation.

---

# 63. Implementation Status

| Capability               | Status                                   |
| ------------------------ | ---------------------------------------- |
| RAW layer                | RUNTIME VERIFIED                         |
| STAGING layer            | RUNTIME VERIFIED                         |
| OLTP layer               | RUNTIME VERIFIED                         |
| Warehouse layer          | RUNTIME VERIFIED                         |
| Analytics/dbt layer      | RUNTIME VERIFIED                         |
| `dim_date`               | RUNTIME VERIFIED                         |
| Core dimensions          | IMPLEMENTED                              |
| `fact_mandat`            | IMPLEMENTED                              |
| `fact_mandat_periode`    | RUNTIME VERIFIED                         |
| `fact_paiement`          | RUNTIME VERIFIED                         |
| Payment OLTP → Warehouse | RUNTIME VERIFIED                         |
| Warehouse DQ             | RUNTIME VERIFIED                         |
| dbt run                  | RUNTIME VERIFIED                         |
| dbt test                 | RUNTIME VERIFIED                         |
| Full Airflow chain       | RUNTIME VERIFIED                         |
| Business metrics         | RUNTIME VERIFIED                         |
| Financial metrics        | RUNTIME VERIFIED                         |
| Grafana financial KPIs   | RUNTIME VERIFIED                         |
| OpenMetadata integration | RUNTIME VERIFIED                         |
| MLflow integration       | RUNTIME VERIFIED                         |
| Streaming architecture   | NOT IMPLEMENTED / NOT CURRENTLY REQUIRED |
| Lakehouse                | NOT IMPLEMENTED / NOT CURRENTLY REQUIRED |

---

# 64. Related Documents

The warehouse architecture should be read together with:

```text id="yp2c0i"
docs/40-DATA/01-Data-Architecture.md

docs/40-DATA/02-Data-Model.md

docs/40-DATA/05-Data-Quality.md

docs/40-DATA/06-Data-Lineage.md

docs/40-DATA/07-Metadata-Management.md

docs/40-DATA/09-Data-Lifecycle.md

docs/40-DATA/10-Data-Security.md
```

Detailed transactional modeling:

```text id="o04tdw"
docs/evidence/05-BC05/C1-MCD-Migration-SQL/
    MCD-MERISE-PROJET.md
    MLD-PROJET.md
    MPD-POSTGRESQL.md
```

---

# 65. Conclusion

The Real Estate Data Warehouse is no longer a generic architectural proposal.

It is an implemented analytical platform with a verified processing chain:

```text id="c7f20a"
SOURCE
   |
   v
RAW
   |
   v
STAGING
   |
   v
OLTP
   |
   v
WAREHOUSE
   |
   v
dbt
   |
   v
METRICS
   |
   v
GRAFANA
```

The architecture now supports the complete real-estate lifecycle:

```text id="93wh4g"
Demand
   |
   v
Matching
   |
   v
Presentation
   |
   v
Visit
   |
   v
Sale
   |
   v
Payment
   |
   v
Analytics
```

Two important modeling extensions are now represented analytically:

```text id="20ijb6"
MANDAT_PERIODE
    ->
fact_mandat_periode
```

and:

```text id="snb4bc"
PAIEMENT
    ->
fact_paiement
```

The controlled payment scenario demonstrates the analytical and observability lineage:

```text id="04e7i8"
Vente 3
   |
   v
Paiement 9
   |
   v
fact_paiement
   |
   v
Prometheus
   |
   v
Grafana
```

with consistent financial values across the platform.

The warehouse therefore provides a reliable foundation for:

```text id="25ayvf"
business analytics
Data Quality
governance
observability
ML experimentation
future AI workloads
```

while preserving the separation between transactional business rules and analytical processing.

---

**DATA WAREHOUSE ARCHITECTURE V3 — IMPLEMENTED AND ALIGNED WITH THE REAL ESTATE RUNTIME**
