# Data Lineage

**Version:** 3.0
**Status:** Implemented / Runtime Partially Verified
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-09-15

---

# 1. Purpose

This document defines the Data Lineage architecture of the Enterprise AI Platform and its Real Estate Intelligence Platform.

Data lineage describes how business and technical data originates, moves, changes and is consumed across the platform.

The objective is to make critical information traceable from its business origin through:

* source ingestion,
* RAW and STAGING processing,
* operational storage,
* business transactions,
* matching,
* analytical transformation,
* Data Warehouse loading,
* Data Quality controls,
* metadata governance,
* observability,
* and AI/ML experimentation.

Lineage is treated as an operational and governance capability rather than only as a documentation diagram.

---

# 2. Scope

The lineage model covers:

* source datasets,
* generated real-estate advertisements,
* ingestion batches,
* RAW data,
* STAGING data,
* PostgreSQL OLTP data,
* search requests and their versions,
* hunter assignments,
* mandates and mandate periods,
* properties,
* matching results,
* presentations,
* visits,
* sales,
* company fees,
* hunter remuneration,
* payments,
* audit events,
* Data Warehouse dimensions and facts,
* dbt analytical models,
* Data Quality controls,
* Airflow execution metadata,
* OpenMetadata catalog metadata,
* Prometheus business and Data Quality metrics,
* Grafana dashboards,
* MLflow experiments and matching evaluations.

---

# 3. Lineage Principles

The platform follows the following principles.

## 3.1 Business origin must remain identifiable

Critical business information should be traceable to the entity, event or source that created it.

Examples include:

* a property to its source and external reference,
* a search version to its parent request and author,
* a presentation to the exact search version and property used by matching,
* a sale to its mandate, mandate period, property and beneficiary hunter,
* a remuneration calculation to its business inputs and configuration.

## 3.2 Operational data is the source of truth

The PostgreSQL operational model is the authoritative source for transactional business state.

The Data Warehouse and analytical models are derived representations.

Corrections to transactional business information must therefore originate from the operational domain and subsequently propagate to analytical layers.

## 3.3 Lineage must survive transformations

Moving data between RAW, STAGING, OLTP, WAREHOUSE and ANALYTICS must not remove the identifiers required to reconcile derived data with its origin.

## 3.4 Historical business context must be preserved

Versioned and financial information must retain enough context to explain historical decisions.

This is particularly important for:

* search criteria,
* mandate periods,
* matching,
* sales,
* remuneration calculations,
* payments.

## 3.5 Catalog lineage and transactional lineage are complementary

OpenMetadata provides catalog and governance visibility.

Database identifiers, foreign keys, business references, audit records and transformation logic provide transactional lineage.

OpenMetadata does not replace the lineage implemented in the application and database model.

---

# 4. Platform Lineage Overview

The implemented data flow is:

```text
External / Generated Sources
            |
            v
      Apache Airflow
            |
            v
           RAW
            |
            v
        STAGING
            |
            v
   PostgreSQL OLTP
      real_estate
            |
            +--------------------------+
            |                          |
            v                          v
   Business Operations          Matching Process
            |                          |
            |                          v
            |                    PRESENTATION
            |                          |
            |                          v
            |                       VISITE
            |                          |
            |                          v
            +----------------------> VENTE
                                       |
                                       v
                              REMUNERATION CALCULATION
                                       |
                                       v
                                   PAIEMENT
                                       |
                                       v
                                  WAREHOUSE
                                       |
                                       v
                                      dbt
                                       |
                                       v
                                  ANALYTICS
```

Governance and operational systems observe different parts of this flow:

```text
Airflow        -> orchestration and pipeline execution
PostgreSQL     -> transactional and relational lineage
audit_log      -> business mutation traceability
dbt            -> analytical dependency lineage
OpenMetadata   -> metadata catalog and governance lineage
MLflow         -> experiment/evaluation lineage
Prometheus     -> operational and business metrics
Grafana        -> metric consumption and visualization
Git            -> implementation and documentation history
```

---

# 5. Source and Ingestion Lineage

The ingestion pipeline accepts generated or external real-estate data and moves it through controlled processing layers.

The implemented Airflow DAG is:

```text
start
  |
generate_source_data
  |
load_raw
  |
validate_raw
  |
transform_staging
  |
validate_staging
  |
load_oltp
  |
validate_oltp
  |
load_warehouse
  |
validate_warehouse
  |
dbt_run
  |
dbt_test
  |
collect_metrics
  |
end
```

This ordering is important.

dbt is not responsible for loading RAW or STAGING in the current implementation. It executes after the warehouse loading and validation stages to produce and validate analytical models.

The Airflow execution provides operational provenance through:

* DAG identity,
* run identifier,
* task identity,
* execution timestamps,
* task state,
* logs,
* retries and failures.

The DAG currently uses manual triggering rather than a periodic production schedule.

A complete successful pipeline execution has been runtime verified.

---

# 6. RAW Lineage

The RAW layer preserves ingested source information before business normalization.

Its purpose is to retain sufficient source fidelity for:

* replay,
* troubleshooting,
* reconciliation,
* Data Quality validation,
* transformation auditing.

The RAW layer corresponds to the Bronze stage of the platform's data architecture.

Data Quality controls are executed before data progresses further through the pipeline.

---

# 7. STAGING Lineage

STAGING represents the normalized intermediate layer.

Its role is to transform heterogeneous source representations into structures suitable for operational loading.

The lineage is:

```text
Source
   |
   v
RAW
   |
   | normalization / transformation
   v
STAGING
   |
   | operational loading
   v
real_estate OLTP
```

The STAGING layer corresponds to the Silver stage.

Validation is performed before operational loading.

---

# 8. Operational OLTP Lineage

The `real_estate` PostgreSQL schema contains the authoritative operational business state.

Lineage is supported primarily through:

* primary keys,
* foreign keys,
* business identifiers,
* version identifiers,
* source references,
* audit records,
* database constraints.

The principal business lineage is:

```text
CLIENT
  |
  v
DEMANDE
  |
  +-----------------> DEMANDE_AFFECTATION -> CHASSEUR
  |
  v
DEMANDE_VERSION
  |
  v
PRESENTATION <-------- BIEN <-------- SOURCE
  |
  v
VISITE
  |
  v
VENTE
  |
  v
PAIEMENT
```

The mandate lifecycle forms another critical part of this chain:

```text
CLIENT
   |
   v
MANDAT ---------> CHASSEUR
   |
   v
MANDAT_PERIODE
   |
   v
VENTE
```

These relationships allow the platform to reconstruct the business context of a transaction.

---

# 9. Search Version Lineage

Search criteria are versioned rather than overwritten.

The relationship is:

```text
DEMANDE
   |
   v
DEMANDE_VERSION v1
DEMANDE_VERSION v2
DEMANDE_VERSION v3
...
```

A version contains the search criteria applicable at that point in time.

Relevant criteria include:

* city,
* postcode,
* property type,
* minimum and maximum budget,
* minimum surface,
* number of rooms,
* number of bedrooms,
* maximum DPE,
* additional desired criteria.

Authorship is also represented.

A version may originate from:

* a client,
* a hunter,
* the system.

The model enforces mutually exclusive authorship.

Additional provenance fields such as source search reference and ingestion batch support traceability between generated/ingested searches and their operational representation.

This prevents later changes to a search from silently changing the context of an earlier recommendation.

---

# 10. Assignment Lineage

A request can exist before a mandate.

Hunter assignment is represented independently through `demande_affectation`.

The lineage is:

```text
DEMANDE
   |
   v
DEMANDE_AFFECTATION
   |
   v
CHASSEUR
```

Assignment state includes:

* assigned,
* accepted,
* refused.

Assignment and decision metadata preserve who handled the request and how the assignment evolved.

The database prevents multiple current assignments for the same request through a partial unique index.

---

# 11. Mandate Lifecycle Lineage

Mandate validity is represented through `mandat_periode`.

```text
MANDAT
   |
   +--> INITIAL PERIOD
   |
   +--> RENEWAL PERIOD 1
   |
   +--> RENEWAL PERIOD 2
   |
   ...
```

This design preserves contractual history instead of overwriting the original mandate period.

Standard periods represent six calendar months.

Historical legacy exceptions are explicitly identified rather than silently rewritten.

A sale references the mandate period applicable to the transaction, allowing the system to identify the contractual context under which the transaction occurred.

---

# 12. Property Source Lineage

A property is linked to its source.

The operational identity currently includes:

```text
SOURCE
   |
   v
BIEN
   |
   +-- id_source
   |
   +-- reference_externe
```

The combination of source and external reference prevents duplicate loading of the same source advertisement.

This provides source-level advertisement lineage.

It must not be interpreted as guaranteed cross-source physical-property deduplication: two different sources may still describe the same real-world property.

---

# 13. Matching Lineage

Matching consumes a specific `DEMANDE_VERSION` and candidate properties.

The current baseline is deterministic and explainable.

```text
DEMANDE_VERSION
       |
       | criteria
       v
 MATCHING ENGINE <--------- BIEN candidates
       |
       | score / rank
       v
 PRESENTATION
```

The current scoring dimensions include:

* location,
* budget,
* property type,
* surface,
* rooms,
* bedrooms,
* DPE.

Budget acts as a hard eligibility filter.

A presentation records the relationship between:

* the exact demand version,
* the selected property,
* the matching score.

The unique relationship between demand version and property also supports idempotent recommendation generation.

Therefore a recommendation can be traced back to the criteria that produced it.

---

# 14. Presentation and Visit Lineage

A recommendation becomes operationally materialized through `presentation`.

A visit is linked to a presentation.

```text
DEMANDE_VERSION
       |
       v
PRESENTATION
       |
       +------> BIEN
       |
       v
VISITE
```

The visit contains operational feedback such as:

* visit date,
* status,
* rating,
* associated business context.

This allows the platform to trace the path from a search criterion set to a proposed property and subsequently to a visit.

---

# 15. Sale Lineage

A sale represents the authenticated transaction outcome.

Its lineage includes:

```text
MANDAT
   |
MANDAT_PERIODE
   |
PRESENTATION ---- BIEN
   |               |
   +-------+-------+
           |
           v
         VENTE
           |
           +----> beneficiary CHASSEUR
```

Relevant sale provenance includes:

* mandate,
* mandate period,
* presentation when applicable,
* property,
* beneficiary hunter,
* purchase amount,
* authenticated deed date,
* sale origin.

Supported sale origins include:

* hunter,
* client alone,
* another agency.

The authenticated deed is currently represented by the transaction attributes, including `date_acte_authentique`; there is no separate `ACTE` entity in the implemented model.

---

# 16. Remuneration Lineage

Hunter remuneration is deterministic and explainable.

The calculation uses business inputs including:

* purchase amount,
* company fees,
* mandate type,
* mandate-to-sale delay,
* number of visits,
* number of sales in the configured window,
* number of mandates in the configured window,
* hunter seniority,
* applicable remuneration configuration.

The lineage is conceptually:

```text
VENTE
  |
  +--> purchase amount
  +--> mandate / mandate period
  +--> beneficiary hunter
  +--> visit context
  |
  v
REMUNERATION CONFIGURATION
  |
  v
DETERMINISTIC CALCULATION
  |
  v
PAIEMENT calculation snapshot
```

The resulting payment record stores calculation context including:

* company fees,
* hunter remuneration,
* performance component scores,
* global performance score,
* base remuneration rate,
* seniority modifier,
* performance modifier,
* final remuneration rate,
* configuration references.

This makes the financial result explainable from stored business inputs.

Stored calculation provenance must not, however, be confused with database-level immutability. Historical financial integrity remains a separate control concern.

---

# 17. Payment Lifecycle Lineage

`PAIEMENT` represents both the financial lifecycle and the frozen calculation result associated with a sale.

The implemented lifecycle is:

```text
ATTENDU
   |
   v
RECU
   |
   v
VERIFIE
   |
   v
PROGRAMME
   |
   v
PAYE
```

`ANNULE` is also supported where appropriate.

Lifecycle transitions are auditable.

Relevant dates allow financial state to be reconciled with analytical data, including:

* authenticated deed date,
* company-fee receipt date,
* hunter payment date.

---

# 18. Audit Lineage

Business lineage is complemented by `real_estate.audit_log`.

Audit records capture relevant mutations including:

* affected table,
* operation,
* record identifier,
* timestamp,
* authenticated user or service context,
* previous value where applicable,
* new value where applicable,
* additional context.

This provides event-level traceability for critical business changes.

For example:

```text
VENTE created
    |
    v
PAIEMENT calculation created
    |
    v
PAIEMENT status changed
ATTENDU -> RECU
    |
    v
RECU -> VERIFIE
    |
    v
VERIFIE -> PROGRAMME
    |
    v
PROGRAMME -> PAYE
```

Audit lineage is complementary to relational lineage:

* foreign keys explain how records relate;
* audit events explain how records changed.

---

# 19. Controlled End-to-End Validation Evidence

A controlled E2E validation scenario has demonstrated the principal transactional chain.

The validated lineage is:

```text
Mandat 17
   |
   v
Mandat Period 2
   |
   +-------------------+
   |                   |
   v                   v
Demand Version 137   Property 16025
   |                   |
   +--------+----------+
            |
            v
     Presentation 32
            |
            v
         Visit 6
            |
            v
          Sale 3
            |
            v
        Payment 9
```

The scenario verified:

* matching,
* presentation creation,
* visit recording,
* sale creation,
* deterministic remuneration calculation,
* payment lifecycle,
* audit trail,
* Data Warehouse propagation.

This is a controlled validation scenario and must not be presented as a genuine historical commercial transaction.

---

# 20. Data Warehouse Lineage

Operational data is propagated into the analytical Data Warehouse.

The warehouse uses dimensional structures including dimensions and business facts.

Relevant lineage includes:

```text
real_estate operational tables
             |
             v
      Warehouse loader
             |
             +--> dimensions
             |
             +--> fact_mandat
             +--> fact_mandat_periode
             +--> fact_presentation
             +--> fact_matching
             +--> fact_demande
             +--> fact_annonce
             +--> fact_paiement
             +--> other analytical facts
```

Two mandate grains must remain distinct:

```text
fact_mandat
= one row per mandate

fact_mandat_periode
= one row per contractual mandate period
```

They must not be merged because they represent different analytical grains.

---

# 21. Financial Warehouse Lineage

Financial transaction lineage continues into `warehouse.fact_paiement`.

The lineage is:

```text
real_estate.vente
        |
real_estate.paiement
        |
        v
warehouse.fact_paiement
```

The warehouse preserves source identifiers allowing reconciliation with OLTP.

Relevant analytical attributes include:

* source payment identifier,
* source remuneration-grid identifier,
* mandate fact key,
* client dimension key,
* hunter dimension key,
* authenticated deed date key,
* fee-receipt date key,
* hunter-payment date key,
* purchase amount,
* company fees,
* hunter remuneration,
* payment status.

The controlled payment with source identifier `9` has been observed in `warehouse.fact_paiement`.

Its analytical values reconcile with the operational transaction:

```text
Purchase amount       = 300,000.00 EUR
Company fees          = 10,500.00 EUR
Hunter remuneration   = 3,939.60 EUR
Payment status        = PAYE
```

This provides runtime evidence of OLTP-to-Warehouse financial propagation.

---

# 22. dbt Analytical Lineage

dbt operates after warehouse loading and validation.

Its role is to construct and validate analytical models rather than to replace the operational ingestion process.

The lineage is:

```text
WAREHOUSE
    |
    v
   dbt
    |
    v
ANALYTICAL MARTS
```

Implemented marts include business views for subjects such as:

* mandate performance,
* market by city,
* market by DPE,
* market by property type,
* market by source,
* market evolution,
* market overview.

dbt provides model dependency information and analytical test execution.

This forms the transformation lineage for the analytical layer.

---

# 23. Data Quality and Lineage

Data Quality is integrated into the lineage path.

```text
RAW
 |
 +--> validate_raw
 |
STAGING
 |
 +--> validate_staging
 |
OLTP
 |
 +--> validate_oltp
 |
WAREHOUSE
 |
 +--> validate_warehouse
 |
dbt
 |
 +--> dbt_test
```

A failed quality gate prevents the pipeline from being considered successfully validated.

Financial Data Quality rules include reconciliation between operational payment information and `fact_paiement`, including:

* purchase amount,
* company fees,
* hunter remuneration,
* payment status,
* financial date keys.

The warehouse validation also checks business consistency such as hunter remuneration not exceeding company fees and required payment dates for paid transactions.

---

# 24. Observability Lineage

The pipeline publishes operational and Data Quality metrics through the observability stack.

The validated high-level path is:

```text
Pipeline / Business Data
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

Metrics include Data Quality layer state and business indicators.

Financial metrics exposed by the platform include:

* `real_estate_paiements_payes_total`,
* `real_estate_honoraires_total_euros`,
* `real_estate_remunerations_chasseur_total_euros`,
* `real_estate_taux_remuneration_moyen`.

The Grafana Business KPI dashboard has displayed values consistent with the controlled E2E transaction:

```text
Paid Payments                    1
Company Fees Collected          10.50K EUR
Hunter Remuneration Paid         3.94K EUR
Average Hunter Remuneration      37.52%
```

Consistency between a metric and a warehouse value does not by itself prove that the metric collector reads the warehouse directly.

The exact collector query/source must be used when documenting physical lineage between database objects and metrics.

This distinction prevents correlation from being incorrectly documented as direct technical lineage.

---

# 25. OpenMetadata Governance Lineage

OpenMetadata provides the governance and metadata plane of the platform.

It is used to catalog and relate assets such as:

* PostgreSQL tables,
* schemas,
* pipelines,
* dbt assets,
* Data Quality information,
* ownership and descriptions,
* tags and classifications.

OpenMetadata provides a navigable governance representation of data relationships.

It is not the Gold analytical storage layer and does not replace PostgreSQL or the Data Warehouse.

The platform therefore distinguishes:

```text
Transactional lineage
    =
database identifiers
foreign keys
business references
audit events
transformation code

Catalog lineage
    =
OpenMetadata relationships
metadata
ownership
descriptions
classification
governance context
```

Not every business relationship documented in this file should be assumed to be automatically captured in OpenMetadata unless runtime evidence confirms it.

---

# 26. ML and Matching Lineage

The current matching implementation provides a deterministic baseline.

MLflow is used for experiment and evaluation tracking.

The experiment:

`real-estate-deterministic-matching`

has been used to record matching evaluation work.

Controlled candidate datasets have demonstrated successful deterministic matching evaluation.

ML lineage currently includes:

* evaluation dataset context,
* matching configuration,
* evaluation execution,
* experiment metadata,
* metrics.

The deterministic baseline must not be presented as a finalized trained production ML model.

When a final trained model is introduced, lineage should additionally capture:

```text
Training Dataset
      |
Feature Engineering
      |
Training Run
      |
Model Version
      |
Evaluation
      |
Promotion
      |
Inference
```

OpenMetadata model metadata can then be expanded accordingly.

---

# 27. Git and Implementation Lineage

Git provides implementation lineage for:

* database migrations,
* application code,
* pipeline code,
* dbt models,
* Kubernetes manifests,
* GitOps definitions,
* Data Quality rules,
* dashboards,
* documentation.

Applied database migrations are also recorded through the migration-control mechanism.

This allows the platform to distinguish:

* what the source repository defines,
* what migration version the database records,
* what GitOps declares,
* what Kubernetes actually runs.

Runtime evidence remains authoritative when determining the actual deployed state.

---

# 28. Impact Analysis

The lineage architecture supports questions such as:

* Which source produced this property?
* Which search criteria produced this recommendation?
* Which search version was active when a property was presented?
* Which hunter was assigned to the request?
* Which mandate period covered a sale?
* Which property and presentation resulted in a sale?
* Which business inputs produced a hunter remuneration?
* Which configuration was used for the calculation?
* Which warehouse fact contains a given operational payment?
* Which analytical models depend on a warehouse fact?
* Which Data Quality gate validates a financial field?
* Which dashboards consume a published metric?
* Which application or migration introduced a schema change?

These questions support troubleshooting, audit, governance and change-impact analysis.

---

# 29. Implementation Status

The following lineage capabilities are currently implemented:

| Capability                                     | Status                          |
| ---------------------------------------------- | ------------------------------- |
| Source → RAW ingestion                         | IMPLEMENTED                     |
| RAW → STAGING transformation                   | IMPLEMENTED                     |
| STAGING → OLTP loading                         | IMPLEMENTED                     |
| OLTP relational lineage                        | IMPLEMENTED                     |
| Demand version provenance                      | IMPLEMENTED                     |
| Hunter assignment lineage                      | IMPLEMENTED                     |
| Mandate-period lineage                         | IMPLEMENTED                     |
| Property/source lineage                        | IMPLEMENTED                     |
| Matching → Presentation lineage                | IMPLEMENTED                     |
| Presentation → Visit lineage                   | IMPLEMENTED                     |
| Sale lineage                                   | IMPLEMENTED                     |
| Remuneration calculation provenance            | IMPLEMENTED                     |
| Payment lifecycle lineage                      | IMPLEMENTED                     |
| Business audit lineage                         | IMPLEMENTED                     |
| OLTP → Warehouse propagation                   | IMPLEMENTED                     |
| Warehouse → dbt analytical lineage             | IMPLEMENTED                     |
| Layer Data Quality lineage                     | IMPLEMENTED                     |
| Airflow execution lineage                      | IMPLEMENTED                     |
| OpenMetadata governance catalog                | IMPLEMENTED                     |
| MLflow experiment lineage                      | IMPLEMENTED                     |
| Controlled transaction → warehouse propagation | RUNTIME VERIFIED                |
| Controlled payment lifecycle audit             | RUNTIME VERIFIED                |
| Grafana financial KPI consumption              | RUNTIME VERIFIED                |
| Full automatic column-level lineage            | PARTIAL / REQUIRES VERIFICATION |
| Complete API-level lineage                     | PARTIAL                         |
| Final production ML model lineage              | NOT YET APPLICABLE              |

---

# 30. Known Limitations

The current lineage architecture has known boundaries.

## 30.1 Column-level lineage

Column-level lineage is not claimed as complete across the entire platform.

It should be expanded only where technically useful and supported by verified metadata extraction.

## 30.2 Metrics source attribution

Prometheus/Grafana values can be reconciled with business data, but the exact SQL source used by each collector must be inspected before documenting direct physical lineage from a specific warehouse table.

## 30.3 Cross-source property identity

Current property identity is source-specific.

Cross-source physical-property deduplication is not yet guaranteed.

## 30.4 Final ML lineage

A final trained production matching model has not yet been established.

Current MLflow lineage relates primarily to deterministic matching evaluation and experimentation.

## 30.5 Historical financial protection

Financial calculation context is stored, but stronger protection of finalized historical financial inputs and outputs remains an integrity requirement to assess.

---

# 31. Future Evolution

Future lineage improvements should be driven by actual business requirements.

Priority areas include:

* expanded verified column-level lineage,
* stronger financial historical integrity,
* offer lineage,
* invoice lineage,
* client feedback lineage,
* document-context lineage,
* improved transaction identity,
* final ML model lineage if a trained model is adopted,
* broader OpenMetadata relationships where they add governance value.

Technologies such as Kafka or event-stream lineage are not current requirements and should not be introduced solely for architectural fashion.

---

# 32. Architecture Decisions

The principal lineage decisions are:

* PostgreSQL OLTP remains the transactional source of truth.
* RAW and STAGING preserve ingestion and transformation traceability.
* Business identifiers and foreign keys provide relational lineage.
* Search criteria are versioned to preserve historical recommendation context.
* Mandate periods preserve contractual lifecycle history.
* Financial calculations preserve their calculation context.
* Audit records provide mutation history.
* Warehouse source identifiers allow OLTP reconciliation.
* dbt provides analytical dependency lineage.
* Airflow provides orchestration execution context.
* OpenMetadata provides the governance/catalog view.
* MLflow provides experiment and model-evaluation context.
* Prometheus and Grafana provide operational consumption of metrics.
* Git provides implementation history.
* Runtime evidence is preferred over documentation when determining actual deployed state.

---

# 33. Related Documents

* `docs/40-DATA/01-Data-Architecture.md`
* `docs/40-DATA/02-Data-Model.md`
* `docs/40-DATA/03-Data-Warehouse.md`
* `docs/40-DATA/05-Data-Quality.md`
* Data Governance documentation
* Metadata Management documentation
* Business Glossary
* AI Architecture documentation
* OpenMetadata documentation
* Observability architecture
* PCA/PRA documentation
* Database migration documentation
* MCD / MLD / MPD documentation
* controlled E2E evidence documentation

---

# 34. Conclusion

Data lineage in the Real Estate Intelligence Platform is implemented across multiple complementary mechanisms rather than through a single tool.

The operational database preserves relational and transactional provenance, Airflow records execution context, dbt describes analytical dependencies, audit records preserve business mutations, OpenMetadata provides governance visibility, MLflow records matching experimentation, and the observability stack exposes operational and business metrics.

The resulting lineage allows the platform to trace critical business information from source ingestion through search, matching, property presentation, visit, sale, remuneration, payment and analytical consumption.

The controlled E2E validation scenario additionally demonstrates that this lineage is not only architectural: the principal transaction chain has been exercised through the operational platform and propagated into the Data Warehouse.

Remaining work is therefore focused on closing specific lineage gaps—particularly offers, invoices, stronger historical financial integrity and verified column-level coverage—rather than redesigning the lineage architecture.
