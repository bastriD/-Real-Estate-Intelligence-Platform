# Data Quality — Real Estate Intelligence Platform

**Version:** 3.0
**Status:** Implemented / Runtime Verified
**Owner:** Bastri Murad
**Project:** PROJECT_FIL_ROUGE / CHASSE_IMMOBILIERE
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-09-15

---

# 1. Purpose

This document defines the Data Quality architecture implemented by the Real Estate Intelligence Platform.

Data Quality is not treated as a final reporting control.

It is integrated throughout the data lifecycle:

```text
Source
   |
   v
RAW
   |
   +--> Quality Gate
   |
   v
STAGING
   |
   +--> Quality Gate
   |
   v
OLTP
   |
   +--> Quality Gate
   |
   v
WAREHOUSE
   |
   +--> Quality Gate
   |
   v
dbt
   |
   +--> Tests
   |
   v
Analytics / Metrics / Consumers
```

The objective is to prevent invalid or inconsistent data from silently propagating through the platform.

---

# 2. Scope

The Data Quality framework covers:

```text
source ingestion
RAW data
STAGING data
real_estate OLTP
warehouse dimensional data
dbt models
business metrics
financial data
matching data
analytical datasets
metadata and profiling
future ML datasets
```

The framework combines:

```text
PostgreSQL constraints
+
SQL validation suites
+
Airflow quality gates
+
dbt tests
+
OpenMetadata profiling
+
Prometheus metrics
+
Grafana dashboards
```

---

# 3. Objectives

The Data Quality architecture aims to:

* detect invalid data as early as possible;
* protect transactional integrity;
* prevent corrupted data from reaching analytical consumers;
* validate business rules;
* reconcile OLTP and Warehouse data;
* protect financial consistency;
* detect missing or duplicated records;
* make quality measurable;
* expose quality state through observability;
* maintain version-controlled validation rules;
* provide evidence for audit and project validation;
* provide trustworthy datasets for future ML workloads.

---

# 4. Quality Principles

The project follows these principles:

```text
Quality is enforced as close as possible
to the source of the rule.

Database integrity belongs in PostgreSQL.

Pipeline validation belongs in the pipeline.

Analytical reconciliation belongs at the
OLTP -> Warehouse boundary.

Consumption-model validation belongs in dbt.

Metadata profiling belongs in OpenMetadata.

Operational quality state must be observable.
```

Another important principle is:

```text
Documentation
does not prove
Data Quality.

Runtime execution does.
```

---

# 5. Quality Dimensions

The platform uses the following Data Quality dimensions.

| Dimension             | Meaning                                             |
| --------------------- | --------------------------------------------------- |
| Completeness          | Required data exists                                |
| Validity              | Values respect their allowed domain                 |
| Consistency           | Related data agrees across entities/layers          |
| Uniqueness            | Business identities are not duplicated              |
| Referential Integrity | References point to valid entities                  |
| Accuracy              | Values correctly represent the known business state |
| Timeliness            | Data is available at the required processing stage  |
| Traceability          | Origin and transformations can be followed          |
| Reconciliation        | Equivalent data remains consistent across layers    |

For financial data, reconciliation is especially important.

---

# 6. Quality Architecture

The implemented quality architecture is:

```text
                   PostgreSQL
                   Constraints
                       |
                       v
Source -> RAW -> STAGING -> OLTP -> WAREHOUSE -> dbt
          |        |       |         |          |
          v        v       v         v          v
        DQ RAW   DQ STG   DQ OLTP   DQ WH     tests
          |        |       |         |          |
          +--------+-------+---------+----------+
                           |
                           v
                    Airflow result
                           |
                           v
                    collect_metrics
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

---

# 7. Defense in Depth

Data Quality is implemented using several complementary mechanisms.

## Layer 1 — PostgreSQL

```text
NOT NULL
PRIMARY KEY
FOREIGN KEY
UNIQUE
CHECK
DEFAULT
indexes
```

## Layer 2 — Pipeline SQL validation

```text
RAW validation
STAGING validation
OLTP validation
WAREHOUSE validation
```

## Layer 3 — dbt

```text
model tests
relationships
uniqueness
accepted values
analytical assertions
```

## Layer 4 — Metadata

```text
OpenMetadata profiling
schema visibility
quality metadata
lineage
```

## Layer 5 — Observability

```text
Pushgateway
Prometheus
Grafana
Airflow execution state
```

No single layer is expected to provide every quality guarantee.

---

# 8. PostgreSQL as the First Quality Boundary

The transactional schema `real_estate` enforces physical and business integrity directly in PostgreSQL.

The runtime schema currently contains:

```text
23 OLTP tables
```

with extensive:

```text
PRIMARY KEY
FOREIGN KEY
UNIQUE
CHECK
NOT NULL
DEFAULT
```

constraints.

This means many invalid states are rejected before they can become valid transactional records.

---

# 9. Referential Integrity

Foreign keys protect relationships such as:

```text
MANDAT
 -> CLIENT
 -> CHASSEUR

MANDAT_PERIODE
 -> MANDAT

DEMANDE
 -> MANDAT

DEMANDE_AFFECTATION
 -> DEMANDE
 -> CHASSEUR

DEMANDE_VERSION
 -> DEMANDE

PRESENTATION
 -> DEMANDE_VERSION
 -> BIEN

VISITE
 -> PRESENTATION

VENTE
 -> MANDAT
 -> MANDAT_PERIODE
 -> PRESENTATION
 -> BIEN

PAIEMENT
 -> VENTE
 -> MANDAT
 -> CHASSEUR
 -> financial configuration
```

This prevents orphaned transactional relationships.

---

# 10. Domain Validation

PostgreSQL `CHECK` constraints enforce allowed business domains.

Examples include:

```text
roles
statuses
mandate types
payment statuses
sale origins
DPE values
visit ratings
audit operations
assignment states
financial rates
performance criteria
```

For example, payment status is restricted to:

```text
ATTENDU
RECU
VERIFIE
PROGRAMME
PAYE
ANNULE
```

A value outside this domain cannot become a valid persisted payment state.

---

# 11. Uniqueness Controls

Uniqueness is enforced where business identity requires it.

Examples include:

```text
CLIENT.email

CHASSEUR.email

MANDAT.reference_mandat

(id_source, reference_externe)
for BIEN

(id_demande, numero_version)
for DEMANDE_VERSION

(id_demande_version, id_bien)
for PRESENTATION

(id_mandat, numero_periode)
for MANDAT_PERIODE
```

These constraints prevent duplicate business entities and duplicate event representations.

---

# 12. Current Assignment Integrity

`DEMANDE_AFFECTATION` keeps the assignment history of a demand.

The model permits historical assignments while preventing multiple simultaneous current assignments.

Conceptually:

```text
DEMANDE
   |
   +--> old assignment
   |
   +--> refused assignment
   |
   +--> current assignment
```

A partial unique index implements the rule that a demand cannot have multiple current assignments.

This is an example of a Data Quality rule implemented physically rather than only checked after ingestion.

---

# 13. Version Authorship Integrity

Each `DEMANDE_VERSION` must have exactly one logical author:

```text
CLIENT
XOR
CHASSEUR
XOR
SYSTEME
```

The database enforces this through a `CHECK` constraint over:

```text
auteur_client_id
auteur_chasseur_id
auteur_systeme
```

This prevents ambiguous version lineage.

---

# 14. Mandate Lifecycle Quality

`MANDAT_PERIODE` protects the six-month mandate lifecycle.

The model validates:

```text
period number
period type
start date
end date
renewal information
```

For standard non-legacy periods, the six-calendar-month rule is enforced.

Historical legacy periods can be explicitly marked as:

```text
est_historique_legacy = true
```

rather than silently weakening the rule for all data.

---

# 15. Financial Configuration Quality

Financial configuration is also protected by database constraints.

For example:

```text
validity dates
positive amounts
rate ranges
performance bounds
seniority settings
floor / ceiling rates
```

The remuneration weights must satisfy:

```text
weight_delay
+
weight_exclusivity
+
weight_sales
+
weight_mandates
+
weight_visits
=
1.000000
```

This prevents invalid scoring configurations from being persisted.

---

# 16. Pipeline Quality Gates

The Real Estate Airflow DAG executes explicit validation between processing layers.

The implemented flow is:

```text
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
```

Quality is therefore evaluated repeatedly rather than only after warehouse publication.

---

# 17. RAW Quality Gate

The RAW quality gate validates the ingestion boundary.

Its role is to detect issues such as:

```text
missing source data
unexpected structure
invalid source values
ingestion anomalies
required-field problems
```

The RAW layer remains source-oriented.

Complex canonical business logic should not be implemented exclusively here.

---

# 18. STAGING Quality Gate

STAGING validation checks data after normalization and transformation.

Responsibilities include:

```text
type consistency
normalization
null handling
deduplication
format validation
preparation for OLTP loading
```

This creates a controlled boundary before data enters the canonical transactional model.

---

# 19. OLTP Quality Gate

The OLTP quality gate validates the resulting operational state after loading.

It complements PostgreSQL constraints.

PostgreSQL answers:

> Can this row legally exist?

The OLTP quality suite can additionally answer:

> Does the resulting business dataset satisfy the expected cross-record rules?

This distinction allows Data Quality to extend beyond individual-row constraints.

---

# 20. Warehouse Quality Gate

After Gold loading, Airflow executes:

```text
validate_warehouse
```

using the warehouse Data Quality suite, including:

```text
database/tests/007_warehouse_data_quality.sql
```

This validation occurs before:

```text
dbt_run
```

and:

```text
dbt_test
```

The sequence is therefore:

```text
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

---

# 21. Why Warehouse Reconciliation Matters

The existence of valid OLTP data does not prove that the warehouse contains the same information.

Possible propagation problems include:

```text
missing fact rows
duplicate fact rows
incorrect foreign keys
incorrect date keys
stale measures
incorrect financial amounts
incorrect status
```

Therefore the project validates the boundary:

```text
OLTP
  |
  v
WAREHOUSE
```

explicitly.

---

# 22. FACT_PAIEMENT Quality

`warehouse.fact_paiement` is a particularly important analytical object because it carries financial information.

The source is:

```text
real_estate.paiement
```

The expected grain is:

```text
1 warehouse fact row
=
1 source payment
```

The source identifier is preserved for reconciliation.

---

# 23. Payment Row-Count Reconciliation

The warehouse quality suite checks the relationship between source payments and payment facts.

Conceptually:

```text
OLTP payment population
       |
       v
warehouse payment population
```

Unexpected missing or duplicated payment facts must be detected.

This was the original payment warehouse reconciliation baseline before the financial controls were strengthened.

---

# 24. Payment Financial Reconciliation

The Data Quality suite now also compares the financial content.

The following values are reconciled:

```text
montant_achat
montant_honoraires
montant_chasseur
statut
```

between:

```text
real_estate.paiement
```

and:

```text
warehouse.fact_paiement
```

The expected invariant is:

```text
OLTP value
=
Warehouse value
```

for the same source payment.

---

# 25. Null-Safe Reconciliation

Financial comparisons use null-safe semantics where necessary.

This is important because ordinary SQL comparisons can fail to identify some differences involving `NULL`.

The reconciliation therefore treats:

```text
NULL
```

and:

```text
non-NULL value
```

as different states.

This prevents incomplete warehouse propagation from being silently ignored.

---

# 26. Hunter Remuneration Business Rule

A specific warehouse quality rule verifies:

```text
montant_chasseur
<=
montant_honoraires
```

Conceptually:

```text
Hunter remuneration
cannot exceed
company fees
```

A violation indicates a financial consistency anomaly requiring investigation.

---

# 27. PAYE Completeness

A payment with:

```text
statut = PAYE
```

must contain the lifecycle information required to explain the completed payment.

The warehouse validation therefore verifies the presence of:

```text
date_reception_honoraires_key
date_paiement_chasseur_key
```

for paid payments.

This prevents records such as:

```text
PAYE
but
no payment date
```

from being accepted analytically.

---

# 28. Payment Date Reconciliation

Dates are also reconciled between OLTP and warehouse.

The source dates include:

```text
date_acte_authentique
date_reception_honoraires
date_paiement_chasseur
```

The corresponding warehouse keys use:

```text
YYYYMMDD
```

For example:

```text
2026-09-14
      |
      v
20260914
```

The quality suite checks that the generated warehouse key represents the source date correctly.

---

# 29. Controlled Payment Validation

A controlled E2E scenario produced:

```text
Vente    = 3
Paiement = 9
```

with:

```text
montant_achat
=
300000.00 €

montant_honoraires
=
10500.00 €

montant_chasseur
=
3939.60 €

taux_final
=
37.52 %

statut
=
PAYE
```

This scenario is a controlled validation fixture and not a real commercial transaction.

---

# 30. Runtime Warehouse Propagation

Before running the normal pipeline, the controlled payment was absent from:

```text
warehouse.fact_paiement
```

The normal Airflow pipeline was executed.

After execution, the warehouse contained:

```text
id_paiement_source            = 9

date_acte_authentique_key     = 20260914

date_reception_honoraires_key = 20260914

date_paiement_chasseur_key    = 20260914

montant_achat                 = 300000.00

montant_honoraires            = 10500.00

montant_chasseur              = 3939.60

statut                        = PAYE

paiement_count                = 1
```

This provides runtime evidence that the controlled financial record propagated through the normal warehouse loader.

---

# 31. Data Quality and the Normal Pipeline

The payment was not inserted manually into the warehouse.

The validated path was:

```text
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
        |
        v
validate_warehouse
```

This distinction is essential when using the result as project evidence.

---

# 32. Latest Full Pipeline Validation

A complete Airflow execution after the latest warehouse/DQ changes completed successfully.

Run:

```text
manual__2026-09-14T22:45:30+00:00
```

Successful tasks included:

```text
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

This proves that the normal end-to-end pipeline completed with all quality gates in the successful task chain.

---

# 33. Evidence Boundary

The successful Airflow run proves that:

```text
validate_warehouse
=
SUCCESS
```

in the complete pipeline.

However, unless individual validation logs have been captured separately, documentation should not claim that every exact SQL `PASS:` message has independently been archived as runtime evidence.

The project therefore distinguishes:

```text
successful quality task
```

from:

```text
captured line-by-line quality output
```

This distinction preserves evidence integrity.

---

# 34. dbt Quality Tests

After warehouse validation, the pipeline executes:

```text
dbt run
```

followed by:

```text
dbt test
```

dbt validation can include:

```text
not_null
unique
relationships
accepted_values
custom analytical tests
```

dbt provides validation at the analytical-model level rather than replacing OLTP constraints.

---

# 35. Separation of Quality Responsibilities

The project intentionally separates responsibilities.

```text
PostgreSQL
=
transactional integrity
```

```text
SQL DQ suites
=
cross-record and cross-layer validation
```

```text
dbt
=
analytical model quality
```

```text
OpenMetadata
=
profiling and governance visibility
```

```text
Prometheus / Grafana
=
operational quality observability
```

This is more robust than relying on a single testing technology.

---

# 36. OpenMetadata Profiling

OpenMetadata contributes to Data Quality through capabilities such as:

```text
column profiling
null statistics
distinct values
distribution information
schema metadata
quality metadata
lineage visibility
```

OpenMetadata is used as the governance and metadata plane.

It is not the mechanism responsible for enforcing transactional constraints.

---

# 37. Data Quality Observability

Data Quality results are exported into the observability stack.

The path is:

```text
Airflow DQ
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

This allows pipeline quality to be monitored without manually reading SQL output after every run.

---

# 38. Layer Status Metrics

The platform exports:

```text
real_estate_dq_layer_status
```

for layers including:

```text
raw
staging
oltp
warehouse
```

A successful state is represented as:

```text
1
```

for the corresponding layer.

---

# 39. Runtime DQ Observability Evidence

Runtime Prometheus/Pushgateway evidence showed:

```text
raw       = 1
staging   = 1
oltp      = 1
warehouse = 1
```

for:

```text
real_estate_dq_layer_status
```

The observed quality execution also reported successful checks across the four layers.

At the captured point, the reported counts were:

```text
RAW
10 passed
0 failed

STAGING
18 passed
0 failed

OLTP
14 passed
0 failed

WAREHOUSE
13 passed
0 failed
```

These numbers represent the observed execution at that point in time and should not be interpreted as a permanently fixed number of tests.

---

# 40. Pipeline Status Metric

The platform also exposes:

```text
real_estate_pipeline_run_status
```

A successful pipeline was observed as:

```text
real_estate_pipeline_run_status = 1
```

This provides a high-level health indicator for the data pipeline.

---

# 41. Push Failure Monitoring

The observability implementation also exposes Pushgateway failure state.

Observed failure-time metrics for the platform and Data Quality jobs were:

```text
0
```

at the inspected runtime point.

This confirms that the corresponding metrics publication had not recorded a push failure at that point.

---

# 42. Grafana Data Quality Dashboard

Grafana contains a dedicated Data Quality dashboard.

Its purpose is to expose:

```text
quality layer state
validation results
pipeline health
quality failures
```

This dashboard is distinct from the Business KPI dashboard.

Financial business KPIs belong to:

```text
Real Estate — Business KPIs & Platform
```

while Data Quality state belongs to the dedicated DQ dashboard.

---

# 43. Data Quality vs Business Metrics

The project distinguishes:

```text
Data Quality metrics
```

from:

```text
business metrics
```

For example:

```text
real_estate_dq_layer_status
```

is a Data Quality metric.

Whereas:

```text
real_estate_honoraires_total_euros
```

is a business metric.

The financial reconciliation tests protect the reliability of the data used to produce those business metrics.

---

# 44. Financial Quality Lineage

The financial Data Quality path is:

```text
VENTE
  |
  v
PAIEMENT
  |
  | OLTP integrity
  v
FACT_PAIEMENT
  |
  | warehouse reconciliation
  v
METRICS
  |
  v
PROMETHEUS
  |
  v
GRAFANA
```

Therefore a dashboard value is not treated as isolated evidence.

It can be traced back to the transactional source.

---

# 45. Quality Rule Storage

Quality rules are stored in version-controlled source files.

Examples include:

```text
database/tests/
```

and dbt test definitions.

This provides:

```text
reviewability
history
reproducibility
CI compatibility
documentation
```

Quality rules should not exist only as manual SQL queries executed by an operator.

---

# 46. Airflow Failure Semantics

A critical validation command returning failure causes the corresponding Airflow task to fail.

The dependency chain then prevents the normal successful progression of downstream tasks.

Conceptually:

```text
validate_warehouse
       |
       +--> SUCCESS --> dbt_run
       |
       +--> FAILURE --> stop successful chain
```

This turns Data Quality into a pipeline gate rather than passive reporting.

---

# 47. Severity

Quality controls should be interpreted according to their business impact.

The general severity model is:

| Severity | Expected Treatment                                |
| -------- | ------------------------------------------------- |
| Critical | Pipeline/data publication blocked                 |
| High     | Investigation required before trusted consumption |
| Medium   | Warning and follow-up                             |
| Low      | Informational / improvement backlog               |

Current executable SQL quality gates primarily focus on conditions severe enough to fail validation.

Not every future severity workflow is yet implemented as a separate automated incident-management mechanism.

---

# 48. Quality Incident Process

When a Data Quality failure occurs:

```text
1. Identify failing layer.

2. Identify failing rule.

3. Identify affected dataset.

4. Determine source vs transformation issue.

5. Assess downstream impact.

6. Correct source/code/configuration.

7. Re-run the affected pipeline.

8. Verify the quality gate.

9. Verify downstream consistency.

10. Record significant architectural or
    governance implications where required.
```

Production corrections should be implemented through version-controlled project changes rather than undocumented manual database manipulation.

---

# 49. Quality and Audit

Data Quality and audit serve different purposes.

```text
Data Quality
=
Is the data valid and consistent?
```

```text
Audit
=
Who changed what, when and in what context?
```

For sensitive transactional events such as sales and payments, both are required.

The controlled E2E scenario has runtime audit evidence for:

```text
VENTE creation
PAIEMENT calculation
payment lifecycle transitions
```

while the Data Quality system validates propagation and analytical consistency.

---

# 50. Quality and Lineage

Lineage answers:

```text
Where did this value come from?
```

Quality answers:

```text
Can this value be trusted?
```

For payment analytics:

```text
real_estate.paiement
        |
        v
warehouse.fact_paiement
        |
        v
metrics
        |
        v
Grafana
```

The project combines lineage and reconciliation so that analytical values can be both traced and validated.

---

# 51. Quality and Governance

OpenMetadata provides governance visibility around:

```text
datasets
schemas
columns
profiles
lineage
quality metadata
```

The Data Quality framework provides executable validation.

Together they provide:

```text
Governance
+
Validation
+
Observability
```

rather than treating governance as documentation only.

---

# 52. AI / ML Data Quality

Future production ML models will require additional quality controls.

Relevant dimensions include:

```text
feature completeness
feature validity
training/validation separation
dataset reproducibility
class or target consistency
data leakage prevention
drift
model-input schema stability
```

The platform already has foundations for these concerns through:

```text
versioned demande criteria
lineage
Airflow
Data Quality gates
MLflow
OpenMetadata
```

However, the final production matching ML model is not yet finalized.

Therefore ML-specific production quality controls must not be documented as fully runtime verified yet.

---

# 53. Deterministic Matching Quality

The current matching baseline is deterministic.

Quality therefore includes verifying:

```text
eligibility rules
budget filtering
candidate selection
score calculation
Top-N persistence
presentation uniqueness
```

The persistence constraint:

```text
UNIQUE(id_demande_version, id_bien)
```

also prevents duplicate presentations for the same demand version/property pair.

---

# 54. Data Quality Ownership

Quality responsibilities are distributed across the platform.

| Area                       | Primary Responsibility   |
| -------------------------- | ------------------------ |
| Business rules             | Application/domain model |
| Transaction integrity      | PostgreSQL               |
| Ingestion validation       | Airflow + SQL DQ         |
| Warehouse reconciliation   | SQL DQ                   |
| Analytical model tests     | dbt                      |
| Metadata/profiling         | OpenMetadata             |
| Pipeline operation         | Airflow                  |
| Quality metrics            | Prometheus               |
| Quality visualization      | Grafana                  |
| Deployment/reproducibility | GitLab CI + GitOps       |

Formal organizational Data Owner/Data Steward assignments can be expanded as governance matures.

---

# 55. Deployment and Change Management

Permanent changes to quality rules follow the project delivery path:

```text
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

Runtime commands are used for:

```text
inspection
diagnostics
evidence
controlled validation
```

rather than replacing the version-controlled deployment process.

---

# 56. Evidence Hierarchy

For Data Quality claims, the project uses:

```text
Runtime evidence
      >
source implementation
      >
CI evidence
      >
GitOps desired state
      >
documentation
      >
assumptions
```

Examples:

```text
SQL test exists
=
IMPLEMENTED
```

```text
Airflow validate task succeeded
=
RUNTIME VERIFIED at task level
```

```text
exact PASS line captured
=
RUNTIME VERIFIED for that exact assertion
```

This avoids overstating evidence.

---

# 57. Current Implementation Status

| Capability                            | Status                               |
| ------------------------------------- | ------------------------------------ |
| PostgreSQL PK/FK integrity            | RUNTIME VERIFIED                     |
| PostgreSQL business CHECK constraints | RUNTIME VERIFIED                     |
| Business uniqueness constraints       | RUNTIME VERIFIED                     |
| Demande authorship integrity          | RUNTIME VERIFIED                     |
| Mandate-period integrity              | RUNTIME VERIFIED                     |
| Financial configuration constraints   | RUNTIME VERIFIED                     |
| RAW validation gate                   | RUNTIME VERIFIED                     |
| STAGING validation gate               | RUNTIME VERIFIED                     |
| OLTP validation gate                  | RUNTIME VERIFIED                     |
| Warehouse validation gate             | RUNTIME VERIFIED                     |
| dbt run                               | RUNTIME VERIFIED                     |
| dbt test                              | RUNTIME VERIFIED                     |
| Payment row reconciliation            | IMPLEMENTED                          |
| Payment financial reconciliation      | IMPLEMENTED / PIPELINE GATE VERIFIED |
| Hunter remuneration consistency       | IMPLEMENTED / PIPELINE GATE VERIFIED |
| PAYE completeness control             | IMPLEMENTED / PIPELINE GATE VERIFIED |
| Payment date reconciliation           | IMPLEMENTED / PIPELINE GATE VERIFIED |
| Payment OLTP → Warehouse propagation  | RUNTIME VERIFIED                     |
| DQ Prometheus metrics                 | RUNTIME VERIFIED                     |
| DQ Grafana dashboard                  | RUNTIME VERIFIED                     |
| OpenMetadata profiling                | RUNTIME VERIFIED                     |
| ML production-quality framework       | PARTIAL / FUTURE MODEL DEPENDENT     |
| Automated anomaly detection           | NOT IMPLEMENTED                      |
| Predictive DQ alerts                  | NOT IMPLEMENTED                      |

---

# 58. Important Evidence Distinction

The four strengthened payment controls are implemented in the warehouse Data Quality SQL suite.

The latest complete Airflow pipeline successfully passed:

```text
validate_warehouse
```

and continued through:

```text
dbt_run
dbt_test
collect_metrics
end
```

Therefore the warehouse quality gate is runtime verified.

However, the individual exact output messages for each newly added payment assertion have not been separately retained as evidence.

They should therefore be described as:

```text
IMPLEMENTED
+
successful warehouse pipeline gate
```

rather than falsely claiming independent captured runtime output for each individual assertion.

---

# 59. Current Limitations

The following limitations are explicitly recognized.

## Exact assertion evidence

Not every individual SQL `PASS:` line is permanently captured as jury evidence.

---

## Pushgateway persistence

Pushgateway storage is currently ephemeral.

It must not be treated as the authoritative historical Data Quality database.

---

## Advanced anomaly detection

Statistical or ML-driven anomaly detection is not currently part of the validated production Data Quality path.

---

## Data contracts

Formal producer/consumer data contracts are not yet fully implemented.

---

## Final ML quality gates

The final production ML model has not yet been finalized, so model-specific production Data Quality and drift controls remain future work.

---

# 60. Future Evolution

Potential improvements include:

```text
persistent DQ execution history

formal data contracts

dataset SLAs / SLOs

freshness thresholds

automatic anomaly detection

quality scorecards

alert routing

historical quality trends

ML feature validation

model-input drift monitoring

formal Data Owner / Steward workflows
```

These should be introduced based on actual project requirements rather than as technology for its own sake.

---

# 61. Architecture Decisions

Key Data Quality decisions are:

| Decision                                       | Rationale                             |
| ---------------------------------------------- | ------------------------------------- |
| PostgreSQL constraints for transactional rules | Reject invalid states early           |
| Layer-specific SQL validation                  | Detect pipeline-level inconsistencies |
| Validation after each major layer              | Prevent propagation                   |
| OLTP/Warehouse reconciliation                  | Protect analytical correctness        |
| Financial reconciliation                       | Protect high-value business metrics   |
| dbt tests after warehouse validation           | Validate analytical models            |
| OpenMetadata profiling                         | Governance and visibility             |
| Prometheus metrics                             | Machine-readable operational state    |
| Grafana dashboard                              | Human-readable quality monitoring     |
| Git-managed rules                              | Reproducibility and reviewability     |
| Airflow quality gates                          | Automated enforcement                 |

---

# 62. Related Documents

This document should be read with:

```text
docs/40-DATA/01-Data-Architecture.md

docs/40-DATA/02-Data-Model.md

docs/40-DATA/03-Data-Warehouse.md

docs/40-DATA/04-Data-Governance.md

docs/40-DATA/06-Data-Lineage.md

docs/40-DATA/07-Metadata-Management.md

docs/40-DATA/09-Data-Lifecycle.md

docs/40-DATA/10-Data-Security.md
```

Implementation evidence includes:

```text
database/tests/007_warehouse_data_quality.sql

Airflow DAG:
real_estate_ingestion

warehouse loader:
database/olap/load_warehouse.py

metrics collector:
observability/metrics/collect_metrics.py
```

---

# 63. Conclusion

Data Quality in the Real Estate Intelligence Platform is no longer a generic future framework.

It is embedded in the implemented data pipeline:

```text
RAW
 |
 +--> VALIDATE
 |
 v
STAGING
 |
 +--> VALIDATE
 |
 v
OLTP
 |
 +--> VALIDATE
 |
 v
WAREHOUSE
 |
 +--> VALIDATE
 |
 v
dbt
 |
 +--> TEST
 |
 v
METRICS
```

Transactional integrity is protected through PostgreSQL.

Cross-layer integrity is protected through SQL Data Quality suites.

Analytical models are tested through dbt.

Metadata and profiling are provided through OpenMetadata.

Operational quality state is exported through Prometheus and visualized through Grafana.

The financial domain now receives additional protection through:

```text
payment row reconciliation

financial amount reconciliation

status reconciliation

hunter remuneration consistency

PAYE completeness

date-key reconciliation
```

The controlled E2E payment demonstrates the importance of these controls:

```text
OLTP
300000 €
10500 €
3939.60 €
PAYE

        |
        v

WAREHOUSE
300000 €
10500 €
3939.60 €
PAYE

        |
        v

PROMETHEUS / GRAFANA
financial KPIs
```

The resulting architecture combines:

```text
Prevention
+
Validation
+
Reconciliation
+
Observability
+
Governance
```

to provide a trustworthy foundation for business analytics and future Data & AI workloads.

---

**DATA QUALITY V3 — IMPLEMENTED, OBSERVABLE AND ALIGNED WITH THE REAL ESTATE RUNTIME**
