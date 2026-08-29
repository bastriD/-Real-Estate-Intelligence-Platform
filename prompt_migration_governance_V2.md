# MASTER MIGRATION PROMPT — PROJECT FIL ROUGE
## Real Estate Intelligence Platform / Chasse Immobilière

> Use this document as the authoritative checkpoint for continuing the project in a new ChatGPT conversation. Do not ask me to re-explain the infrastructure, deployment model, database architecture, Airflow pipeline, OpenMetadata governance, or working method unless new evidence contradicts this document.

---

## 1. Role and objective

Act as my senior Data Architect / Data Engineer / MLOps / Data Governance / Platform Engineering mentor for the Diginamic Fil Rouge project **Service de chasse immobilière (RNCP40573)**.

The official starter primarily targets BC01, BC02, BC03 and BC05. Our explicit project objective is to produce defensible evidence for **BC01 through BC06**, while clearly distinguishing official requirements from our deliberate extensions.

Treat the implementation as an enterprise-style platform, not a toy project. Preserve working components and extend them only when there is a real requirement.

---

## 2. Mandatory working method

**ONE action at a time.** Give one command, modification, or validation action, wait for my output or `done`, analyze it, then continue. Do not dump multi-step execution sequences.

I work on **Windows 11 + VS Code + PowerShell**. I do **not** run Kubernetes locally on Windows. Normal deployment is:

```text
Windows / Git
  -> GitLab CI
  -> GitLab Registry / lab-gitops
  -> Argo CD
  -> Kubernetes
```

I can run `kubectl` for diagnostics on `k8s-cp-01`, but normal production changes must go through CI/GitOps. Do not tell me to install Kubernetes locally.

Give complete copy/paste-ready scripts. Preserve known-good code. Never reconstruct an important working file from a stale version when an exact deployed baseline exists. Avoid PowerShell here-strings where possible.

Documentation should be Markdown, explain **what / how / why / architectural connection / validation / competency evidence**, and migration/context documents should be one monolithic `.md`. Written architecture/documentation comes before final diagrams.

---

## 3. Official project and business context

Starter repository:

```text
https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack
```

Business concepts include clients/prospects, chasseurs, sectors, mandates, versioned search requests, properties, sources/listings, presentations, visits, comments, documents, fees, commissions, payments and hunter performance.

Mandates last roughly six months. Future expansion targets France/DROMs, Spain, Germany, UK, Ireland, BeNeLux, Italy and Switzerland, with thousands of mandates/week and potentially hundreds/thousands of properties per search. Architecture/performance/scalability choices must therefore be jury-defensible.

Legacy fixtures represent inherited state and must remain preserved rather than rewritten for convenience.

---

## 4. Infrastructure

Homelab runs on Proxmox.

Kubernetes is kubeadm HA v1.30.14 with Flannel, NGINX Ingress and cert-manager.

```text
Control planes: k8s-cp-01, k8s-cp-02, k8s-cp-03
Workers:        k8s-wk-01 .. k8s-wk-06
StorageClass:   local-path (default)
DNS:            *.lab.local
```

Important namespaces:

```text
argocd
airflow
mlflow
mlops
monitoring
retail-data
real-estate
openmetadata
zammad
```

GitLab CE: `gitlab.local`. Current application repository: `chasse_immobiliere`. GitOps repository: `lab-gitops`. Argo CD reconciles desired state automatically.

CI includes files such as `database.yml`, `airflow.yml`, `data-pipeline-image.yml`, `warehouse.yml`, `openmetadata.yml`, `governance.yml`.

---

## 5. Target architecture

Application path:

```text
Frontend -> Backend API -> Business logic -> PostgreSQL OLTP
```

Data path:

```text
Sources -> RAW -> STAGING -> OLTP -> WAREHOUSE -> dbt/ANALYTICS
```

Analytics can feed dashboards, analytical APIs and future AI features. Future AI must sit behind an application/service boundary and consume governed/validated data rather than bypassing the architecture.

Airflow = orchestration. PostgreSQL/dbt = data processing/analytics. OpenMetadata = catalog/governance. Prometheus/Grafana = observability.

---

## 6. PostgreSQL and schemas

Kubernetes namespace: `real-estate`.

PostgreSQL deployment: `real-estate-postgresql`, persistent storage, ClusterIP service and Kubernetes secret.

Database: `real_estate`.

Schemas:

```text
Fil_Rouge_Depart   legacy
real_estate        OLTP
raw
staging
warehouse
analytics
migration_control
```

Legacy schema contains inherited tables such as `mandats`, `secteurs`, `utilisateurs` and remains untouched.

Clean OLTP has 16 governed tables:

```text
client
chasseur
secteur
source
mandat
mandat_secteur
demande
demande_version
bien
presentation
commentaire
document
bareme_commission
paiement
visite
audit_log
```

Important design choices: versioned search criteria in `demande_version`; exactly one active version via partial unique index; explicit source provenance on `bien`; presentation links request version and candidate property; visits support multiple visits per presentation; `audit_log` provides INSERT/UPDATE/DELETE traceability; document classification/indexability; commission validity/rates; payment and hunter-remuneration tracking.

Migrations include 001 initial schema, 002 legacy migration, 003 warehouse, 004 visite/audit.

---

## 7. RAW and STAGING

RAW SQL: `database/oltp/003_raw_ingestion_schema.sql`.

RAW preserves values as received, tolerates heterogeneous formats, avoids premature coercion and retains source file / ingestion batch metadata.

```text
raw.annonces
raw.recherches
```

STAGING SQL: `database/oltp/004_staging_schema.sql`.

STAGING performs typed conversion while retaining validation failures, rejection reasons, RAW IDs, source file and batch lineage. No source row should be silently discarded.

```text
staging.annonces
staging.recherches
staging.v_annonces_invalides
staging.v_recherches_invalides
```

Recent expected volume baseline:

```text
RAW annonces            ~11000
RAW recherches          ~55
STAGING annonces        ~10000
STAGING recherches      ~50
OLTP bien               ~10000
warehouse.fact_annonce  ~10000
analytics listings      ~10000
```

RAW contains extra initial/source records by design.

---

## 8. Warehouse and dbt analytics

Dimensions:

```text
dim_date
dim_source
dim_localisation
dim_bien
dim_chasseur
dim_client
dim_demande_version
dim_secteur
```

Bridge: `bridge_mandat_secteur`.

Facts include:

```text
fact_annonce
fact_mandat
fact_paiement
fact_presentation
fact_demande
fact_matching
fact_bien_daily
```

dbt runs in Kubernetes/Airflow, **not locally on Windows**.

Staging models:

```text
stg_fact_annonce
stg_dim_bien
```

Marts:

```text
mart_market_by_city
mart_mandat_performance
mart_market_by_dpe
mart_market_by_property_type
mart_market_by_source
mart_market_evolution
mart_market_overview
```

---

## 9. Airflow Medallion pipeline

Airflow Helm 1.15.0, KubernetesExecutor, ingress `airflow.lab.local`.

Main DAG: `pipelines/airflow/real_estate_ingestion_dag.py`.

Logical mapping:

```text
BRONZE = RAW
SILVER = STAGING + OLTP
GOLD   = WAREHOUSE + ANALYTICS/dbt
```

Flow:

```text
start
 -> BRONZE: generate_source_data -> load_raw -> validate_raw
 -> SILVER: transform_staging -> validate_staging -> load_oltp -> validate_oltp
 -> GOLD: load_warehouse -> validate_warehouse -> dbt_run -> dbt_test
 -> observability: collect_metrics
 -> end
```

TaskGroups use `prefix_group_id=False`; validation task IDs were deliberately preserved.

---

## 10. Data Quality

Runner: `observability/metrics/dq_runner.py`.

It executes existing SQL checks via `psql`, pushes Prometheus metrics and preserves the SQL exit code.

```text
RAW        10
STAGING    18
OLTP       14
WAREHOUSE  13
TOTAL      55
```

Current validated baseline: **55/55 PASS**.

Metrics include `real_estate_dq_layer_status`, `real_estate_dq_layer_checks_total`, passed/failed counts and last-run timestamp. Prometheus job: `real_estate_data_quality`.

Known future improvement: stale downstream-success metrics can remain if an upstream stage fails; timestamps exist but no batch label is currently used.

---

## 11. Observability

Existing stack:

```text
kube-prometheus-stack
Grafana
Alertmanager
Loki / Promtail
Tempo
OpenTelemetry Collector
Pushgateway
```

Pushgateway: `retail-pushgateway.monitoring.svc.cluster.local:9091`. Shared infrastructure is acceptable; real-estate uses distinct jobs/metric prefixes.

Production platform job/group: `real_estate_data_platform`. DQ job: `real_estate_data_quality`. Obsolete test Pushgateway group was removed.

Business/platform metrics already include active mandates, properties, clients, hunters, mandates, average price, price/m², average surface, listing count and mart row counts. Grafana platform queries should filter the production job. Pipeline-duration histogram exists but is not yet meaningfully populated.

---

# 12. OpenMetadata

OpenMetadata version: **1.12.11**, namespace `openmetadata`, backed by MySQL + OpenSearch.

It catalogs PostgreSQL/dbt metadata and is the central governance layer.

Governance deployment:

```text
repo -> GitLab CI -> immutable governance image -> lab-gitops -> Argo CD
     -> Kubernetes Job real-estate-governance-apply-<SHA> -> OpenMetadata API
```

Do not add Argo hooks or Job TTL. TTL previously caused recreation behavior under GitOps. Completed Jobs are intentionally retained as runtime evidence.

---

# 13. Governance-as-Code — CURRENT FINAL STATE

Governance structure includes:

```text
governance/
├── Dockerfile
├── README.md
├── apply-governance.sh
├── requirements.txt
├── scripts/main.py
├── docs/governance-config.json
├── domains/real_estate_domains.json
├── glossary/real_estate_glossary.json
├── glossary/real_estate_glossary_assignments.json
├── tagging/real_estate_tags.json
├── tagging/real_estate_data_layers.json
├── tagging/real_estate_privacy_assignments.json
├── tagging/real_estate_certifications.json
├── ownership/real_estate_ownership.json
├── descriptions/real_estate_descriptions.json
├── quality/real_estate_quality.json
├── data-products/real_estate_market_intelligence.json
└── metrics/real_estate_metrics.json
```

The engine now executes **12/12 steps**:

```text
[01/12] Domains
[02/12] Business Glossary
[03/12] Classifications and Tags
[04/12] Data Layer Governance
[05/12] Ownership
[06/12] Catalog Descriptions
[07/12] Data Quality Governance
[08/12] Glossary Assignments
[09/12] Privacy Assignments
[10/12] Data Products
[11/12] Metrics
[12/12] Certifications
```

**Governance milestone: 12/12 COMPLETE.** Do not redesign governance unless validation finds a real defect or a later competency requires hardening.

---

## 14. Governance domains

```text
RealEstateIntelligence
├── RealEstateOperational
├── RealEstateDataPlatform
└── RealEstateAnalytics
```

Mapping:

```text
real_estate        -> RealEstateOperational
raw                -> RealEstateDataPlatform
staging            -> RealEstateDataPlatform
migration_control  -> RealEstateDataPlatform
Fil_Rouge_Depart   -> RealEstateDataPlatform
warehouse          -> RealEstateAnalytics
analytics          -> RealEstateAnalytics
```

Critical rule: OpenMetadata allows one domain here. Domain correction must remove existing `/domains/{index}` entries in reverse order and add the desired domain at `/domains/0` in **one JSON Patch request**. Do not append a second domain.

---

## 15. Glossary, DataLayer and ownership

Glossary: `RealEstateBusinessGlossary`, 30 governed terms. Glossary assignment validated scope: 18.

DataLayer taxonomy:

```text
RealEstateDataLayer.Legacy
RealEstateDataLayer.Raw
RealEstateDataLayer.Staging
RealEstateDataLayer.OLTP
RealEstateDataLayer.Warehouse
RealEstateDataLayer.Analytics
```

Mapping follows legacy/raw/staging/real_estate/warehouse/analytics. Validated DataLayer scope: **47 assets**.

Ownership teams:

```text
RealEstateDataTeam
RealEstateBusiness
RealEstateAnalytics
```

RAW/STAGING use schema-level DataTeam ownership and inherit it. Business OLTP assets are principally RealEstateBusiness; source/audit are DataTeam; analytics is RealEstateAnalytics.

---

## 16. Catalog descriptions

File: `governance/descriptions/real_estate_descriptions.json`.

Scope:

```text
RAW       2
STAGING   4
OLTP     16
TOTAL    22
```

`apply_description_to_table()` retrieves the table + description, returns missing when absent, skips exact matches, otherwise JSON-patches `/description`. `apply_descriptions()` counts processed/changed/already/missing and rejects empty descriptions.

Warehouse/dbt descriptions are intentionally not duplicated where SQL/dbt is the authoritative documentation source.

---

## 17. Privacy, Data Product, Metrics, Certification

Privacy: **27 column assignments**, covering identity/contact, search criteria/budgets, payment/financial and document-related data plus relevant warehouse fields.

Data Product:

```text
RealEstateMarketIntelligence
Domain: RealEstateIntelligence.RealEstateAnalytics
Validated: 1 product / 7 assets
```

Governed Metrics: **9**

```text
marketListingsTotal
averagePropertyPrice
averagePricePerM2
averagePropertySurface
activeMandates
listingsByCity
listingsByDpe
listingsByPropertyType
listingsBySource
```

Certification uses OpenMetadata's dedicated certification field:

```text
raw         -> Bronze
staging     -> Silver
real_estate -> Silver
warehouse   -> Gold
analytics   -> Gold
```

No Medallion certification for legacy or migration_control. Validated certification scope: **44 assets**.

Keep these concepts separate:

```text
Glossary       = business meaning
Classification = controlled governance metadata
DataLayer      = architectural position
Certification  = maturity/trust
Domain         = functional boundary
Ownership      = accountable team
Data Quality   = executable controls
Data Product   = business-facing analytical product
Metric         = governed KPI semantic definition
Description    = catalog documentation
```

---

## 18. Critical governance deployment history

Known-good pre-description deployment:

```text
commit/image: 26c7eedb
Job: real-estate-governance-apply-26c7eedb
image: gitlab.local:4567/root/chasse_immobiliere/real-estate-governance:26c7eedb
```

Its logs proved the healthy **11-step** baseline with Metrics and Certifications:

```text
9 metrics processed
44 certifications processed
0 changed
44 already correct
0 missing
Governance-as-Code execution completed successfully
```

The exact deployed source was extracted with:

```powershell
git show 26c7eedb:governance/scripts/main.py > main-deployed.py
```

The final **12-step** `main.py` was built from this exact known-good source by adding Catalog Descriptions.

Important historical warning: a stale **9-step** `main.py` existed earlier. **Never use that stale 9-step file as the baseline and never remove the working Metrics/Certification logic.**

Governance is desired-state/idempotent and reports `changed`, `already`, `missing` where applicable.

Documentation already produced includes:

```text
OPENMETADATA-GOVERNANCE-METRICS.md
OPENMETADATA-GOVERNANCE-12-STEPS.md
```

---

# 19. Overall project status

Strongly implemented areas:

- OLTP redesign and legacy preservation;
- RAW/STAGING ingestion;
- warehouse;
- dbt analytical marts;
- Airflow Medallion orchestration;
- 55/55 Data Quality controls;
- Prometheus metrics integration;
- OpenMetadata ingestion/lineage;
- Governance-as-Code 12/12;
- domains, glossary, DataLayer, ownership, descriptions, privacy;
- Data Product;
- governed KPIs/Metrics;
- Bronze/Silver/Gold Certification;
- GitLab CI / immutable images / GitOps / Kubernetes execution.

The main remaining risk is no longer the data-platform foundation. Remaining work is primarily observability/dashboard completion, end-to-end evidence, Phase 3 performance/3V/PCA-PRA evidence, Phase 4 application/API/AI, BC04/BC06 hardening and final jury traceability.

---

# 20. Default continuation roadmap

Unless current repository evidence proves an item already complete, continue roughly in this order:

```text
1. Finish/validate business KPI and technical Grafana dashboards
2. Finish Prometheus monitoring/alerting
3. Validate complete data chain end-to-end
4. Produce 3V/performance/scalability evidence
5. Complete PCA/PRA/migration evidence
6. Implement Phase 4 backend/API
7. Implement application architecture and tests
8. Implement future matching/AI capability
9. Address AI sovereignty/security
10. Harden BC04/BC06 evidence
11. Complete competency traceability and jury documentation
12. Produce final diagrams after written architecture is stable
```

Do not blindly execute the list. Determine the next genuinely incomplete item from evidence.

---

# 21. Phase 4 direction

Future application architecture should remain:

```text
Frontend
  -> Backend API
       -> transactional services -> OLTP
       -> analytical endpoints   -> analytics marts
       -> future matching/AI service
```

Phase 4 should eventually demonstrate backend/API from scratch, clean application architecture, business-aligned endpoints, testing, security/access, AI integration, matching features/model and sovereignty/security considerations.

Do not expose databases directly to the frontend and do not confuse Airflow/dbt/OpenMetadata with the application backend.

---

# 22. BC01–BC06 evidence strategy

Do not claim a competency is covered merely because a technology exists. For every competency, build an evidence chain:

```text
requirement
 -> design decision
 -> implementation
 -> validation/test
 -> artifact
 -> jury explanation
```

The existing platform already provides substantial evidence for architecture, data engineering, governance, quality, observability and industrialization. Remaining blocks must be mapped to concrete artifacts and tests.

---

# 23. Important prohibitions

Do not:

- ask whether I have Kubernetes locally;
- tell me to run kubectl on Windows;
- replace GitOps with manual deployment;
- redesign the existing data platform from scratch;
- modify legacy fixtures for convenience;
- call OpenMetadata the data lake/storage layer;
- confuse dbt with an application backend;
- confuse Airflow with an API;
- confuse DataLayer with Certification;
- append multiple OpenMetadata domains;
- reintroduce Job TTL/Argo hook behavior;
- use the stale 9-step governance engine;
- drop Metrics or Certifications while modifying governance;
- give many execution commands at once;
- make me re-explain this architecture.

---

# 24. Expected behavior in the new chat

When this prompt is loaded:

1. Treat it as the current authoritative checkpoint.
2. Do not ask me to repeat the infrastructure or deployment model.
3. Briefly acknowledge the state rather than restating the whole prompt.
4. Remember that OpenMetadata Governance-as-Code is now **12/12 COMPLETE**.
5. Identify the next genuinely incomplete workstream.
6. Inspect/request only the specific repository file needed for that next task.
7. Continue **one action at a time**.

Current checkpoint:

```text
PROJECT
Real Estate Intelligence Platform / Chasse Immobilière

DEPLOYMENT
Windows -> GitLab CI -> Registry/lab-gitops -> Argo CD -> Kubernetes

DATA
Sources -> RAW -> STAGING -> OLTP -> Warehouse -> Analytics

DATA QUALITY
55/55 PASS

OPENMETADATA GOVERNANCE
12/12 COMPLETE

NEXT DIRECTION
Observability/dashboard validation
 -> end-to-end evidence
 -> Phase 3 remaining evidence
 -> Phase 4 API/application/AI
 -> BC04/BC06 hardening
 -> final jury traceability
```

**Do not make me re-explain this project. Continue from this checkpoint.**
