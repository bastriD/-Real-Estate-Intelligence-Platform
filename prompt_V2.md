# PROJECT FIL ROUGE — MASTER MIGRATION PROMPT

## Enterprise Real Estate Intelligence Platform — `chasse_immobiliere`

> This is the **single monolithic migration document** for continuing the project in another ChatGPT conversation without re-explaining the infrastructure, deployment model, databases, pipelines, Airflow, Kubernetes, GitLab, GitOps, OpenMetadata, governance, current state, or next steps.

---

# 1. WORKING RULES FOR THE NEXT CHAT

I am working on the Diginamic **Fil Rouge Data & IA** project.

The assistant must:

1. Work **step by step** during deployment/troubleshooting.
2. Give one execution step, then wait for my output before continuing.
3. When I request a script/file, provide the **whole file**, not disconnected fragments.
4. Understand that my Windows workstation is for VS Code, PowerShell, repository editing and Git.
5. Do **not** assume Kubernetes is installed or operated locally from Windows.
6. Respect the existing GitLab CI/CD + GitOps + Argo CD deployment architecture.
7. Do not redesign already validated components without a concrete reason.
8. Inspect the current implementation before modifying it.
9. Keep the system explainable for the final Diginamic soutenance.
10. After a major phase, document what was done, why, how it works, deployment, validation and competency relevance.

---

# 2. PROJECT IDENTITY

Repository:

```text
chasse_immobiliere
```

Windows workspace:

```text
C:\Users\bastr\Desktop\DIGINAMIC\chasse_immobiliere
```

Platform name:

```text
Enterprise Real Estate Intelligence Platform
```

The objective is an enterprise-style modernization of a real-estate information system covering:

- legacy migration;
- OLTP modelling;
- RAW/STAGING processing;
- warehouse;
- dbt analytics;
- orchestration;
- automated validation;
- CI/CD;
- containers;
- Kubernetes;
- GitOps;
- metadata/cataloguing;
- governance;
- lineage;
- RGPD/security;
- observability;
- later AI/ML.

This is not merely a PostgreSQL exercise.

---

# 3. HIGH-LEVEL ARCHITECTURE

```text
Windows workstation
      |
      | git push
      v
GitLab CE
      |
      +-- CI validation
      +-- DB migrations/validation
      +-- container builds
      +-- GitLab Registry
      +-- Airflow DAG publication
      +-- GitOps publication
               |
               v
           lab-gitops
               |
               v
            Argo CD
               |
               v
           Kubernetes
          /     |       \
         /      |        \
 PostgreSQL   Airflow   OpenMetadata
      |         |           |
      |         |           +-- PostgreSQL metadata ingestion
      |         |           +-- profiler
      |         |           +-- dbt ingestion
      |         |           +-- Governance-as-Code
      |         |
      |         +-- KubernetesPodOperator
      |                    |
      |                    v
      |          data-pipeline:latest
      |                    |
      +--------------------+
```

Core principle:

> Git contains desired state/source, GitLab validates/builds/publishes, Argo CD reconciles Kubernetes, Airflow orchestrates data workloads, and OpenMetadata governs/catalogues the data assets.

---

# 4. INFRASTRUCTURE

Existing homelab/platform includes:

- Proxmox;
- kubeadm HA Kubernetes;
- NGINX Ingress;
- cert-manager;
- GitLab CE;
- GitLab Runner;
- Argo CD;
- Airflow;
- PostgreSQL;
- OpenMetadata;
- OpenSearch;
- MLflow;
- MinIO;
- Prometheus/Grafana;
- Loki/Promtail;
- Tempo/OpenTelemetry;
- local Ollama/Qwen AI infrastructure.

Relevant namespaces:

```text
airflow
argocd
cert-manager
ingress-nginx
mlflow
mlops
monitoring
openmetadata
real-estate
retail-data
zammad
```

Real-estate PostgreSQL:

```text
namespace: real-estate
```

Airflow:

```text
namespace: airflow
```

OpenMetadata/governance:

```text
namespace: openmetadata
```

Argo CD:

```text
namespace: argocd
```

Kubernetes cluster-side `kubectl` is used for inspection/troubleshooting, but normal deployment is GitLab/GitOps driven.

---

# 5. REPOSITORIES AND DEPLOYMENT FLOW

Main project repository:

```text
chasse_immobiliere
```

Dedicated Airflow repository:

```text
airflow-dags
```

GitOps repository:

```text
lab-gitops
```

Flow:

```text
chasse_immobiliere
       |
       +------> airflow-dags ------> Airflow
       |
       +------> lab-gitops --------> Argo CD ------> Kubernetes
```

Do not replace this with manual Windows Kubernetes deployment.

---

# 6. POSTGRESQL DATA ARCHITECTURE

Database:

```text
real_estate
```

Important schemas:

```text
Fil_Rouge_Depart
raw
staging
real_estate
migration_control
warehouse
analytics
```

These are logical schemas/layers inside the PostgreSQL platform.

Data lifecycle:

```text
Fil_Rouge_Depart
      |
      v
     raw
      |
      v
   staging
      |
      v
 real_estate
      |
      v
 warehouse
      |
      v
 analytics
```

Meaning:

```text
Fil_Rouge_Depart = legacy/source
raw               = immutable/raw ingestion
staging           = normalization/transformation
real_estate       = canonical OLTP/business model
warehouse         = analytical warehouse
analytics         = dbt analytics/marts
migration_control = migration/control metadata
```

This separation is intentional.

---

# 7. OLTP V2 MODEL

The PostgreSQL V2 schema has already passed structural CI validation.

Validated results included:

```text
PASS: schema real_estate exists
PASS: 16 real_estate tables found
PASS: all expected tables exist
PASS: all expected primary keys exist
PASS: all expected foreign keys exist
PASS: critical CHECK constraints exist
PASS: one-active-version partial unique index exists
PASS: legacy search description preservation column exists
PASS: real_estate.visite structure validated
PASS: real_estate.audit_log structure validated
PASS: migration 004 indexes exist
```

Final result:

```text
PASS | PostgreSQL V2 schema structure validated successfully -
       16 tables including visite and audit_log
```

Important tables include:

```text
client
chasseur
secteur
mandat
mandat_secteur
demande
demande_version
bien
commentaire
document
paiement
presentation
visite
source
audit_log
```

Repository SQL remains authoritative.

Modelling principles already implemented:

- PK/FK integrity;
- CHECK constraints;
- versioning;
- one-active-version constraints;
- auditability;
- migration preservation;
- indexes.

---

# 8. DATABASE MIGRATIONS

Migrations are designed to be idempotent.

Known successful CI behaviour:

```text
Migration 004 already applied - skipping safely.
Job succeeded
```

Transactional validation also uses:

```text
BEGIN
...
ROLLBACK
```

The database validation stage verifies actual V2 structure, not only connectivity.

---

# 9. DATA PIPELINE IMAGE

Airflow KubernetesPodOperator tasks use:

```text
gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
```

Relevant Python requirements discussed:

```text
psycopg[binary]==3.2.10
python-dotenv==1.0.1
boto3==1.35.95
dbt-core==1.9.0
dbt-postgres==1.9.0
```

The current repository `requirements.txt` is authoritative.

---

# 10. AIRFLOW

Airflow is already deployed and operational in Kubernetes.

Real-estate DAG:

```text
real_estate_ingestion
```

Loaded file:

```text
/opt/airflow/dags/repo/dags/real_estate_ingestion_dag.py
```

Owner:

```text
real-estate
```

The DAG is active.

Task chain:

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
end
```

All executable stages use:

```text
gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
```

`start` and `end` are EmptyOperators.

A complete manual DAG run has already succeeded with **every task successful**.

Therefore:

> Do not start by recreating Airflow or the DAG. The end-to-end pipeline works.

---

# 11. AIRFLOW DAG PUBLICATION

The main GitLab pipeline publishes DAGs from:

```text
pipelines/airflow/
```

to:

```text
airflow-dags/dags/
```

using CI credentials.

The validated design performs:

```text
database:validate
       |
       v
airflow:publish-dags
       |
       v
airflow-dags repository
       |
       v
Airflow
```

Current `.gitlab-ci.yml` remains authoritative if it has changed.

---

# 12. OPENMETADATA

Version:

```text
OpenMetadata 1.12.11
```

Namespace:

```text
openmetadata
```

Observed components:

```text
mysql-0
openmetadata-...
opensearch-0
```

OpenMetadata is the:

- data catalogue;
- glossary;
- ownership catalogue;
- Domain catalogue;
- classification/tag catalogue;
- profiler surface;
- quality metadata surface;
- lineage/governance surface.

It is **not** the physical data lake/database.

---

# 13. OPENMETADATA INGESTION

Existing CronJobs include:

```text
real-estate-postgresql-ingestion
real-estate-postgresql-profiler
real-estate-dbt-ingestion
```

Observed schedules:

```text
real-estate-postgresql-ingestion   10 2 * * *
real-estate-postgresql-profiler    45 2 * * *
real-estate-dbt-ingestion          30 3 * * *
```

They have been intentionally suspended at times for controlled/manual execution.

Important corrected name:

```text
real-estate-postgresql-ingestion
```

Do not use the previously mistaken:

```text
real-estate-openmetadata-ingestion
```

---

# 14. OPENMETADATA API AUTHENTICATION

Anonymous API access returns HTTP 401.

Token secret:

```text
om-admin-token
```

key:

```text
jwtToken
```

Useful authenticated diagnostic pattern:

```bash
kubectl -n openmetadata run om-api-check \
  --rm -it \
  --image=curlimages/curl:8.10.1 \
  --restart=Never \
  --env="OM_TOKEN=$(kubectl -n openmetadata get secret om-admin-token -o jsonpath='{.data.jwtToken}' | base64 -d)" \
  -- \
  sh -c 'curl -s \
    -H "Authorization: Bearer ${OM_TOKEN}" \
    "http://openmetadata:8585/api/v1/..."'
```

The OpenMetadata application image itself does not contain `curl`; use a temporary curl pod.

---

# 15. GOVERNANCE-AS-CODE STRUCTURE

Current project structure:

```text
governance
|   .gitignore
|   apply-governance.sh
|   Dockerfile
|   README.md
|   requirements.txt
|
+---data-products
+---docs
|       governance-config.json
|
+---domains
|       real_estate_domains.json
|
+---glossary
|       real_estate_glossary.json
|
+---k8s
|       governance-apply-job.yaml
|
+---lineage
+---ownership
|       real_estate_ownership.json
|
+---quality
|       real_estate_quality.json
|
+---scripts
|       main.py
|
+---tagging
        real_estate_tags.json
```

Git does not preserve empty directories. If `data-products` or `lineage` remain empty but the Dockerfile copies them, preserve them with `.gitkeep`.

This previously caused Docker build failures:

```text
"/lineage": not found
"/data-products": not found
```

That issue has been solved.

---

# 16. GOVERNANCE DOCKERFILE

The working design includes:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY docs /app/docs
COPY glossary /app/glossary
COPY ownership /app/ownership
COPY quality /app/quality
COPY scripts /app/scripts
COPY tagging /app/tagging
COPY apply-governance.sh /app/apply-governance.sh
COPY domains /app/domains
COPY data-products /app/data-products
COPY lineage /app/lineage

RUN chmod +x /app/apply-governance.sh

ENTRYPOINT ["/app/apply-governance.sh"]
```

The governance image builds and publishes successfully.

---

# 17. GOVERNANCE GITOPS

GitOps resources include paths such as:

```text
workloads/openmetadata-governance/governance-apply-job.yaml
workloads/openmetadata-governance/kustomization.yaml
workloads/openmetadata-governance/real-estate/governance-apply-job.yaml
workloads/openmetadata-governance/real-estate/kustomization.yaml
```

Argo CD application:

```text
openmetadata-governance
```

Validated status:

```text
Synced
Healthy
```

Important behaviour:

A new Docker image tagged `latest` does not necessarily alter GitOps YAML, so CI may correctly report:

```text
No OpenMetadata GitOps changes to publish.
```

For controlled reruns, the existing governance Job has been deleted and recreated by desired state.

---

# 18. GOVERNANCE V1.1.0 — VALIDATED BASELINE

Current version:

```text
Governance version: 1.1.0
OpenMetadata: 1.12.11
```

Latest fresh Kubernetes execution:

```text
job.batch/real-estate-governance-apply   Complete   1/1
pod/real-estate-governance-apply-szhcn   Completed
RESTARTS                                 0
```

Final log:

```text
Governance-as-Code execution completed successfully
Governance apply completed successfully
```

This is the current stable baseline.

---

# 19. OPENMETADATA DOMAINS

Hierarchy:

```text
RealEstateIntelligence
|
+-- RealEstateOperational
+-- RealEstateDataPlatform
+-- RealEstateAnalytics
```

Actual FQNs:

```text
RealEstateIntelligence
RealEstateIntelligence.RealEstateOperational
RealEstateIntelligence.RealEstateDataPlatform
RealEstateIntelligence.RealEstateAnalytics
```

Validated assignments:

```text
real-estate-postgresql.real_estate.real_estate
 -> RealEstateIntelligence.RealEstateOperational

real-estate-postgresql.real_estate.raw
 -> RealEstateIntelligence.RealEstateDataPlatform

real-estate-postgresql.real_estate.staging
 -> RealEstateIntelligence.RealEstateDataPlatform

real-estate-postgresql.real_estate.migration_control
 -> RealEstateIntelligence.RealEstateDataPlatform

real-estate-postgresql.real_estate.Fil_Rouge_Depart
 -> RealEstateIntelligence.RealEstateDataPlatform

real-estate-postgresql.real_estate.warehouse
 -> RealEstateIntelligence.RealEstateDataPlatform

real-estate-postgresql.real_estate.analytics
 -> RealEstateIntelligence.RealEstateAnalytics
```

Domain governance is working.

---

# 20. DOMAIN API BUGS ALREADY SOLVED

Do not rediscover/reintroduce these.

Child domains are FQN entities such as:

```text
RealEstateIntelligence.RealEstateOperational
```

An earlier implementation attempted assignment using:

```text
RealEstateOperational
```

which caused:

```text
RuntimeError: Domain does not exist: RealEstateOperational
```

Current code resolves/uses the actual domain FQN.

OpenMetadata 1.12.11 `domainType` API compatibility issues were also solved.

Inspect the current `governance/scripts/main.py` before touching Domain code.

---

# 21. BUSINESS GLOSSARY

Glossary:

```text
RealEstateBusinessGlossary
```

Current successful execution applies **30 terms**:

```text
Client
Prospect
Chasseur
Mandat
MandatExclusif
MandatNonExclusif
Demande
VersionDemande
Bien
Annonce
Source
Secteur
Presentation
Visite
Commentaire
Prix
PrixM2
Surface
DPE
Honoraires
Commission
BaremeCommission
Paiement
PerformanceChasseur
IngestionBatch
SourceFile
DataQuality
OLTP
Warehouse
Analytics
```

This works. Do not recreate it from scratch.

---

# 22. CLASSIFICATIONS AND TAG DEFINITIONS

Successful governance creates:

```text
5 classifications
23 tags
```

## RealEstateDataSensitivity

```text
Public
Internal
Confidential
Restricted
```

## RealEstatePrivacy

```text
PersonalData
DirectIdentifier
IndirectIdentifier
FinancialData
RequiresPseudonymisation
AIRestricted
```

## RealEstateDataLayer

```text
Legacy
Raw
Staging
OLTP
Warehouse
Analytics
```

## RealEstateDataQuality

```text
QualityControlled
CriticalDataset
SourceOfTruth
DerivedData
```

## RealEstateTechnicalMetadata

```text
LineageMetadata
IngestionMetadata
AuditMetadata
```

Critical distinction:

> Tag definitions exist successfully, but not all desired assets/columns are yet systematically assigned those tags.

That is the next governance phase.

---

# 23. OWNERSHIP

Teams:

```text
RealEstateDataTeam
RealEstateBusiness
RealEstateAnalytics
```

Business tables are assigned primarily to:

```text
RealEstateBusiness
```

Technical source/audit assets and warehouse responsibility use:

```text
RealEstateDataTeam
```

Analytics schema responsibility uses:

```text
RealEstateAnalytics
```

Examples already validated:

```text
real_estate.client          -> RealEstateBusiness
real_estate.chasseur        -> RealEstateBusiness
real_estate.mandat          -> RealEstateBusiness
real_estate.demande         -> RealEstateBusiness
real_estate.bien            -> RealEstateBusiness
real_estate.paiement        -> RealEstateBusiness
real_estate.visite          -> RealEstateBusiness
real_estate.source          -> RealEstateDataTeam
real_estate.audit_log       -> RealEstateDataTeam
warehouse schema            -> RealEstateDataTeam
analytics schema            -> RealEstateAnalytics
```

Ownership is already functional.

---

# 24. DATA QUALITY GOVERNANCE

Required governance tags have already been validated on:

```text
real-estate-postgresql.real_estate.real_estate.bien
real-estate-postgresql.real_estate.warehouse.fact_annonce
real-estate-postgresql.real_estate.analytics.stg_fact_annonce
real-estate-postgresql.real_estate.analytics.stg_dim_bien
real-estate-postgresql.real_estate.analytics.mart_market_by_city
```

Required lineage is already verified for at least:

```text
analytics.stg_fact_annonce
analytics.mart_market_by_city
```

Some lineage therefore already exists.

Do not assume the entire platform lineage is complete.

---

# 25. EXAMPLE GOVERNED ENTITY

OpenMetadata entity:

```text
real-estate-postgresql.real_estate.real_estate.bien
```

has been queried successfully through the authenticated API.

It showed:

- PostgreSQL service;
- database/schema relation;
- column definitions;
- ownership;
- tags.

Owner:

```text
RealEstateBusiness
```

Existing Data Quality tags included:

```text
RealEstateDataQuality.CriticalDataset
RealEstateDataQuality.QualityControlled
RealEstateDataQuality.SourceOfTruth
```

Therefore Governance-as-Code is actually modifying catalogued entities.

---

# 26. WHY GOVERNANCE WAS EXPANDED

The OpenMetadata UI was considered too chaotic because it initially lacked enough visible organization:

```text
no useful systematic tags
unclear ownership
poor visualization of relationships/data flow
```

The governance layer was therefore expanded with:

- Domains;
- glossary;
- classifications;
- tags;
- ownership;
- quality metadata;
- lineage.

The goal is both operational governance and a clear soutenance/evaluation visualization.

---

# 27. CURRENT GOVERNANCE EXECUTION

Current successful sequence:

```text
Step 1/5 - Applying domains
Step 2/5 - Applying business glossary
Step 3/5 - Applying classifications and tags
Step 4/5 - Applying ownership
Step 5/5 - Applying Data Quality governance
```

Latest run completed all five successfully.

The logs show idempotent behaviour:

```text
Team already exists
Ownership already correct
Required tags already present
Required lineage verified
```

This is desirable.

---

# 28. DBT

dbt is already integrated.

Airflow executes:

```text
dbt_run
dbt_test
```

OpenMetadata has:

```text
real-estate-dbt-ingestion
```

Known analytical objects:

```text
analytics.stg_fact_annonce
analytics.stg_dim_bien
analytics.mart_market_by_city
```

Known warehouse object:

```text
warehouse.fact_annonce
```

Existing dbt lineage must be preserved rather than duplicated unnecessarily.

---

# 29. OPENMETADATA GITOPS INGESTION STRUCTURE

The GitOps repository contains OpenMetadata ingestion resources under:

```text
workloads/openmetadata/ingestions/
```

including:

```text
airflow
retail-postgresql
retail-postgresql-profiler
dbt
real-estate-postgresql
real-estate-dbt
```

The real-estate metadata stack is integrated into the same existing platform rather than deployed as an isolated second OpenMetadata instance.

---

# 30. IMPORTANT PROJECT DOCUMENTATION

Project/reference documentation includes:

```text
00-project-constitution.md
architecture-playbook(1).md
Readme.md
README(1).md
NOTE-DE-CADRAGE.md
CAHIER-DES-CHARGES-TECHNIQUE.md
MCD-MERISE.md
OLTP.md
OLAP.md
FICHE-COURS-OLTP-OLAP.md
MATRICE-DECISION.md
MODELE-SWOT.md
RACI.md
GLOSSAIRE-METIER.md
REGISTRE-RGPD.md
SOUVERAINETE-SECURITE-IA.md
PCA-PRA-MIGRATION.md
PLAN-DE-TESTS.md
GRILLE-EVALUATION.md
TRACABILITE-COMPETENCES.md
NOTE-ECO-CONCEPTION.md
JOURNAL-DE-DECISIONS.md
TRAME-SOUTENANCE.md
ORGANISATION-DEPOT.md
prompt.md
airflow_validation.md
```

These documents support architectural choices and Diginamic competency evidence.

Use them rather than inventing requirements when formal alignment is being checked.

---

# 31. CONCEPTUAL RESPONSIBILITIES

Keep these roles distinct:

```text
PostgreSQL   = actual persisted project data
Airflow      = pipeline orchestration
dbt          = analytical transformation/testing
OpenMetadata = catalogue/governance/lineage
GitLab       = CI/CD/build/publish
Registry     = executable container images
lab-gitops   = Kubernetes desired state
Argo CD      = GitOps reconciliation
Kubernetes   = runtime platform
```

---

# 32. WHY MULTIPLE DATABASE SCHEMAS

The layer separation makes the data lifecycle visible and testable:

```text
LEGACY
  |
 RAW
  |
STAGING
  |
 OLTP
  |
WAREHOUSE
  |
ANALYTICS
```

It improves:

- traceability;
- validation;
- governance;
- lineage;
- security separation;
- architecture explanation.

Do not flatten these schemas without a strong reason.

---

# 33. DOMAINS VS DATALAYER TAGS

These are complementary concepts.

Domains answer:

```text
Which organizational/business area does this asset belong to?
```

Examples:

```text
RealEstateOperational
RealEstateDataPlatform
RealEstateAnalytics
```

DataLayer tags answer:

```text
At which technical lifecycle layer is this asset?
```

Examples:

```text
Legacy
Raw
Staging
OLTP
Warehouse
Analytics
```

This distinction is central to the next task.

---

# 34. QUALITY TAGS VS EXECUTABLE TESTS

Metadata tags such as:

```text
QualityControlled
CriticalDataset
SourceOfTruth
```

describe governance status.

Actual tests execute through mechanisms including:

```text
database CI structural validation
validate_raw
validate_staging
validate_oltp
validate_warehouse
dbt test
OpenMetadata profiler/tests where configured
```

Do not claim a governance tag itself executes a quality test.

---

# 35. IMMEDIATE NEXT PHASE

Do **not** rebuild infrastructure.

Next tasks, in order:

```text
1. Systematic DataLayer tagging
2. Column-level RGPD/privacy tagging
3. Complete lineage visualization
4. Data Products
5. Additional governance/quality polish
6. Later AI phase
```

Do them one at a time and validate each.

---

# 36. NEXT TASK — SYSTEMATIC DATALAYER TAGGING

Classification already exists:

```text
RealEstateDataLayer
```

Required systematic assignment:

```text
Fil_Rouge_Depart.* -> RealEstateDataLayer.Legacy
raw.*               -> RealEstateDataLayer.Raw
staging.*           -> RealEstateDataLayer.Staging
real_estate.*       -> RealEstateDataLayer.OLTP
warehouse.*         -> RealEstateDataLayer.Warehouse
analytics.*         -> RealEstateDataLayer.Analytics
```

Requirements:

- use existing Governance-as-Code;
- remain idempotent;
- preserve existing tags;
- preserve Data Quality metadata;
- preserve Domains;
- preserve ownership;
- preserve dbt lineage;
- report assets changed/already correct;
- handle missing assets clearly;
- make the OpenMetadata UI immediately understandable.

Before coding, inspect:

```text
governance/scripts/main.py
governance/tagging/real_estate_tags.json
governance/docs/governance-config.json
```

Do not create a parallel governance system.

---

# 37. FOLLOWING TASK — COLUMN-LEVEL RGPD

After DataLayer tagging is deployed and validated, use existing privacy classifications for appropriate columns:

```text
RealEstatePrivacy.PersonalData
RealEstatePrivacy.DirectIdentifier
RealEstatePrivacy.IndirectIdentifier
RealEstatePrivacy.FinancialData
RealEstatePrivacy.RequiresPseudonymisation
RealEstatePrivacy.AIRestricted
```

Review actual schema semantics before assignment.

Candidate categories include:

```text
names
email
telephone
address
postal information
geolocation
financial/payment data
client identifiers
free-text comments/documents
```

Align with:

```text
REGISTRE-RGPD.md
SOUVERAINETE-SECURITE-IA.md
```

Do not blindly classify every column.

---

# 38. FOLLOWING TASK — FULL LINEAGE

Desired conceptual visualization:

```text
SOURCE / LEGACY
       |
       v
Fil_Rouge_Depart
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
DBT / ANALYTICS
       |
       v
 MARTS / KPIs
```

This should correspond to the actual Airflow processing chain.

Some dbt lineage already exists.

The objective is to complete lineage for custom ingestion/transformation steps that automatic dbt/OpenMetadata metadata does not represent.

Do not destroy existing dbt-derived lineage.

---

# 39. LATER — DATA PRODUCTS

Reserved directory:

```text
governance/data-products
```

Potential future products:

```text
Real Estate Market Intelligence
Chasseur Performance
Property Market by City
Mandate / Client Performance
```

Do not implement before tagging/privacy/lineage unless explicitly requested.

---

# 40. PREVIOUS ERRORS ALREADY SOLVED

Do not waste time rediscovering these unless a regression occurs.

### Wrong ingestion CronJob name

Correct:

```text
real-estate-postgresql-ingestion
```

### `curl` missing in OpenMetadata image

Use temporary `curlimages/curl`.

### API HTTP 401

Use `om-admin-token` / `jwtToken`.

### Domain API `domainType`

Already solved for OpenMetadata 1.12.11.

### Child Domain FQN lookup

Use:

```text
RealEstateIntelligence.RealEstateOperational
```

not merely:

```text
RealEstateOperational
```

### Docker empty directories

Keep `lineage` and `data-products` represented in Git.

### Airflow pipeline

Already works end-to-end.

---

# 41. USEFUL VALIDATION COMMANDS

PostgreSQL:

```bash
kubectl -n real-estate get deploy real-estate-postgresql
```

Airflow:

```bash
kubectl -n airflow get pods
```

```bash
kubectl -n airflow exec deploy/airflow-scheduler -c scheduler -- \
  airflow dags list
```

```bash
kubectl -n airflow exec deploy/airflow-scheduler -c scheduler -- \
  airflow tasks list real_estate_ingestion --tree
```

```bash
kubectl -n airflow exec deploy/airflow-scheduler -c scheduler -- \
  airflow dags list-runs -d real_estate_ingestion
```

OpenMetadata:

```bash
kubectl -n openmetadata get pods
```

```bash
kubectl -n openmetadata get cronjobs \
  -o custom-columns=NAME:.metadata.name,SCHEDULE:.spec.schedule,SUSPEND:.spec.suspend,LAST-SCHEDULE:.status.lastScheduleTime
```

Governance:

```bash
kubectl -n openmetadata get job,pod \
  -l app=real-estate-governance-apply
```

```bash
kubectl -n openmetadata logs \
  job/real-estate-governance-apply
```

Argo CD:

```bash
kubectl -n argocd get application openmetadata-governance \
  -o custom-columns=NAME:.metadata.name,SYNC:.status.sync.status,HEALTH:.status.health.status,REVISION:.status.sync.revision
```

Hard refresh when genuinely needed:

```bash
kubectl -n argocd annotate application openmetadata-governance \
  argocd.argoproj.io/refresh=hard \
  --overwrite
```

These are validation/diagnostic commands, not replacements for GitOps.

---

# 42. SOURCE-OF-TRUTH PRIORITY

If something conflicts, use:

```text
1. Current chasse_immobiliere repository files
2. Current Kubernetes runtime
3. Current GitLab CI/CD/logs
4. Current lab-gitops state
5. Current OpenMetadata API state
6. This migration document
7. Older conversational assumptions
```

---

# 43. HOW TO MODIFY EXISTING CODE

When changing an existing subsystem:

```text
inspect current file
       |
       v
understand current behaviour
       |
       v
propose exact change
       |
       v
provide whole file when requested
       |
       v
I commit + push
       |
       v
GitLab CI/CD
       |
       v
GitOps / Argo CD
       |
       v
Kubernetes validation
       |
       v
application/data validation
       |
       v
documentation
```

Do not give a chain of tiny unmergeable patches when a whole replacement file is appropriate.

---

# 44. CURRENT PROJECT CHECKPOINT

As of **2026-08-24**:

```text
PostgreSQL V2                    DONE
Database migration validation    DONE
Legacy/source layer              DONE
RAW                              DONE
STAGING                          DONE
Canonical OLTP                   DONE
Warehouse                        DONE
dbt analytics                    DONE
Airflow orchestration            DONE
Airflow K8s execution            DONE
GitLab pipeline image            DONE
DAG publication                  DONE
GitOps integration               DONE
OpenMetadata PostgreSQL ingest   DONE
OpenMetadata profiler            DONE
OpenMetadata dbt ingestion       DONE
Governance Domains               DONE
Business Glossary                DONE
Classification definitions       DONE
Tag definitions                  DONE
Ownership                        DONE
Quality governance metadata      DONE
Required lineage validation      DONE
Governance v1.1.0 clean rerun    DONE
Kubernetes Job Complete 1/1      DONE

Systematic DataLayer assignment  NEXT
Column-level RGPD tagging        AFTER
Full lineage visualization       AFTER
Data Products                    LATER
AI phase                         LATER
```

---

# 45. LATEST GOVERNANCE PROOF

The latest clean governance run produced:

```text
Connected to OpenMetadata: 1.12.11

Step 1/5 - Applying domains
SUCCESS

Step 2/5 - Applying business glossary
30 terms
SUCCESS

Step 3/5 - Applying classifications and tags
5 classifications
23 tags
SUCCESS

Step 4/5 - Applying ownership
SUCCESS

Step 5/5 - Applying Data Quality governance
Required tags verified
Required lineage verified
SUCCESS

Governance-as-Code execution completed successfully
Governance apply completed successfully
```

Kubernetes:

```text
job.batch/real-estate-governance-apply   Complete   1/1
pod/real-estate-governance-apply-szhcn   Completed
RESTARTS                                 0
```

This is the baseline. Do not reopen already solved governance failures without new evidence.

---

# 46. FINAL ARCHITECTURAL STORY

The final system should be explainable as:

```text
Legacy real-estate data
          |
          v
Controlled ingestion
          |
          v
         RAW
          |
     validation
          |
          v
       STAGING
          |
     validation
          |
          v
Canonical OLTP
          |
     validation
          |
          v
      WAREHOUSE
          |
     validation
          |
          v
         dbt
          |
    run + tests
          |
          v
     ANALYTICS
          |
          v
 Business insights
```

Airflow orchestrates the lifecycle.

Kubernetes executes the workloads.

GitLab validates/builds/publishes.

Argo CD deploys/reconciles desired state.

OpenMetadata governs the resulting information landscape through:

```text
Domains
Glossary
Ownership
Tags
Privacy
Quality
Lineage
Data Products
```

Later AI capabilities should consume governed, quality-controlled, traceable data rather than bypassing this architecture.

---

# 47. INSTRUCTION FOR THE NEW CHAT

Do **not** ask me to explain the project again.

Do not start with:

```text
Do you have Kubernetes?
Do you use Airflow?
Where is PostgreSQL?
Should we install OpenMetadata?
Do you want GitOps?
```

All of that is already established.

Continue directly from the current checkpoint.

The immediate task is:

> **Systematic `RealEstateDataLayer` tagging in OpenMetadata through the existing Governance-as-Code system.**

Desired mapping:

```text
Fil_Rouge_Depart.* -> RealEstateDataLayer.Legacy
raw.*               -> RealEstateDataLayer.Raw
staging.*           -> RealEstateDataLayer.Staging
real_estate.*       -> RealEstateDataLayer.OLTP
warehouse.*         -> RealEstateDataLayer.Warehouse
analytics.*         -> RealEstateDataLayer.Analytics
```

First inspect the latest governance implementation.

If the current source files are not available in the new chat, ask me specifically for:

```text
governance/scripts/main.py
governance/tagging/real_estate_tags.json
governance/docs/governance-config.json
```

Do not ask me to re-explain the architecture.

After implementation:

1. I commit/push.
2. Observe GitLab.
3. Validate governance image.
4. Validate GitOps/Argo CD as necessary.
5. Rerun governance.
6. Require Kubernetes `Complete 1/1`.
7. Validate representative OpenMetadata assets from each layer.
8. Document the phase.
9. Only then proceed to column-level RGPD tagging.

---

# END — MASTER MIGRATION PROMPT
