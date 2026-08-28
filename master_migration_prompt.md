# MASTER MIGRATION PROMPT — PROJECT FIL ROUGE — CHASSE IMMOBILIÈRE
## Checkpoint: 27 August 2026

You are taking over an EXISTING and already substantially implemented Diginamic Fil Rouge Data & IA project named `chasse_immobiliere`.

This is NOT a greenfield project.

Your first responsibility is to preserve the existing architecture, deployment model, technical decisions, naming, and validated work. Do not redesign working components merely because another implementation is possible.

The complete verified project checkpoint is included below. Treat it as the authoritative technical context for continuing the project.

---

# 1. HOW TO WORK WITH ME

Work step by step.

Give me ONE operational step at a time when we are executing or troubleshooting infrastructure.

After giving me a command, wait for my output before moving to the next step.

Do not give me 10 commands to execute at once unless I explicitly ask for a complete script.

When I ask for a script/file, give me the COMPLETE copy-paste-ready file, not fragments.

Do not assume Kubernetes exists on my Windows workstation.

My normal workflow is:

```text
Windows 11
  ↓
VS Code / PowerShell
  ↓
chasse_immobiliere Git repository
  ↓
GitLab
  ↓
GitLab CI
  ↓
GitOps repositories / container registry
  ↓
Argo CD / git-sync
  ↓
Kubernetes
```

Operational Kubernetes verification may be executed from `k8s-cp-01`, but application deployment must respect the existing CI/CD/GitOps design.

Do not replace GitOps with manual `kubectl apply` as the permanent deployment mechanism.

Manual Kubernetes commands are acceptable for diagnostics, verification, and deliberately triggered audit jobs.

Before proposing a new component, first determine whether the project already contains an implementation for it.

---

# 2. PROJECT OBJECTIVE

The project implements a professional Data/IA platform for a real-estate property-search business.

The architecture covers:

- operational PostgreSQL / OLTP;
- RAW ingestion;
- STAGING transformation and data quality;
- OLTP loading;
- dimensional Data Warehouse;
- dbt analytics;
- Airflow orchestration;
- Kubernetes execution;
- GitLab CI/CD;
- GitOps / Argo CD;
- OpenMetadata;
- Governance-as-Code;
- profiling and Data Quality;
- Prometheus / Pushgateway;
- Grafana;
- observability;
- security / secrets;
- documentation and Diginamic competency evidence.

The objective is not merely to make a demo work. The implementation and documentation must justify architectural choices and provide evidence for the Diginamic Fil Rouge evaluation.

---

# 3. CRITICAL DEPLOYMENT CONSTRAINTS

Remember these throughout the conversation.

## Windows

The development workstation is Windows 11 with VS Code and PowerShell.

There is NO local Kubernetes environment on Windows.

Do not tell me to run `kubectl` locally on Windows unless I explicitly tell you Kubernetes has been configured there.

## GitLab CI

The main repository is:

```text
chasse_immobiliere
```

GitLab CI is used for validation, building, publication, and deployment workflows.

## Kubernetes

The platform runs on a kubeadm Kubernetes cluster.

Relevant namespaces include:

```text
real-estate
airflow
openmetadata
monitoring
argocd
mlflow
mlops
```

## GitOps

Argo CD is used for GitOps deployment.

Do not bypass this architecture permanently with ad-hoc resources.

## Airflow DAG deployment

Airflow DAGs are NOT manually copied into Airflow.

The deployment path is:

```text
chasse_immobiliere
      ↓
GitLab CI
      ↓
airflow:publish-dags
      ↓
https://gitlab.local/root/airflow-dags.git
      ↓
git-sync sidecar
      ↓
Airflow DAG directory
      ↓
scheduler
```

The GitLab job clones the dedicated `airflow-dags` repository, copies:

```text
pipelines/airflow/*.py
```

into:

```text
dags/
```

commits and pushes to `main`.

The Airflow scheduler has containers:

```text
scheduler
git-sync
scheduler-log-groomer
```

The git-sync repository is mounted under `/git`, with `/git/repo` pointing to the active worktree.

This deployment path has already been verified.

---

# 4. CURRENT END-TO-END DATA PIPELINE

The current Airflow DAG is:

```text
real_estate_ingestion
```

The validated task chain is:

```text
start
  ↓
generate_source_data
  ↓
load_raw
  ↓
validate_raw
  ↓
transform_staging
  ↓
validate_staging
  ↓
load_oltp
  ↓
validate_oltp
  ↓
load_warehouse
  ↓
validate_warehouse
  ↓
dbt_run
  ↓
dbt_test
  ↓
collect_metrics
  ↓
end
```

A fresh run on 27 August 2026 successfully completed EVERY task.

Run ID:

```text
manual__2026-08-27T20:50:02+00:00
```

All tasks were `success`, including:

```text
load_warehouse
validate_warehouse
dbt_run
dbt_test
collect_metrics
end
```

Therefore DO NOT start by debugging the Airflow pipeline. It is currently validated end-to-end.

---

# 5. DATABASE ARCHITECTURE

PostgreSQL runs in Kubernetes namespace:

```text
real-estate
```

Deployment:

```text
real-estate-postgresql
```

Database:

```text
real_estate
```

User:

```text
real_estate_user
```

Important schemas:

```text
raw
staging
real_estate
warehouse
analytics
migration_control
Fil_Rouge_Depart
```

Logical data flow:

```text
Generated/source data
       ↓
RAW
       ↓
STAGING
       ↓
OLTP real_estate
       ↓
WAREHOUSE
       ↓
dbt
       ↓
ANALYTICS MARTS
       ↓
Grafana / OpenMetadata / downstream consumers
```

---

# 6. VERIFIED DATA STATE

At the checkpoint, important row counts included:

```text
raw.annonces                 7000
raw.recherches                 35

staging.annonces             6000
staging.recherches             30

real_estate.bien             6000
real_estate.chasseur            6
real_estate.client              18
real_estate.demande             17
real_estate.demande_version     17
real_estate.mandat              17
real_estate.mandat_secteur      17
real_estate.secteur             10

warehouse.bridge_mandat_secteur 17
warehouse.dim_bien             6001
warehouse.dim_chasseur            7
warehouse.dim_client             19
warehouse.dim_date             5844
warehouse.dim_demande_version    18
warehouse.dim_localisation       18
warehouse.dim_secteur            11
warehouse.dim_source              2
warehouse.fact_annonce          6000
warehouse.fact_mandat             17
```

The dimension counts include unknown/default dimensional records where appropriate.

OLTP-to-Warehouse reconciliation was verified:

```text
entity            oltp    warehouse
bien              6000    6000
chasseur             6       6
client               18      18
demande_version      17      17
mandat               17      17
secteur              10      10
```

---

# 7. IMPORTANT RAW/STAGING BATCH EXPLANATION

Do NOT misdiagnose the current RAW count as accidental duplication.

The RAW layer contains one historical fixture batch:

```text
generated-1000-v1
```

with:

```text
1000 rows
1000 distinct references
source_file = database/fixtures/annonces/annonces.csv
```

and six operational generated batches that propagate downstream:

```text
generated-20260822T000000
generated-20260823T073715
generated-20260823T194031
generated-20260823T205547
generated-20260824T065752
generated-20260824T142334
```

Each operational batch contains:

```text
1000 rows
1000 distinct references
```

The six operational batches are present consistently in RAW, STAGING and `warehouse.fact_annonce`.

Therefore:

```text
RAW       = 7000
STAGING   = 6000
WAREHOUSE = 6000
```

is explained by the extra historical fixture batch in RAW.

Do not delete it without first deciding/documenting the intended RAW retention policy.

---

# 8. VERIFIED STAGING DATA QUALITY

For `staging.annonces`:

```text
total_rows             6000
valid_rows             6000
invalid_rows              0
quality_not_evaluated     0
missing_reference         0
missing_price             0
invalid_price             0
missing_surface           0
invalid_surface           0
missing_city              0
missing_postal_code       0
distinct_references    6000
```

Therefore the current operational STAGING dataset passed the core quality checks.

---

# 9. VERIFIED WAREHOUSE REFERENTIAL INTEGRITY

For `warehouse.fact_annonce`:

```text
total_fact_rows              6000
missing_dim_bien                0
missing_dim_source              0
missing_dim_localisation        0
missing_publication_date        0
missing_collection_date         0
```

The fact table therefore has complete dimensional linkage for the audited dataset.

---

# 10. VERIFIED MARKET KPI

Current market summary:

```text
total_annonces          6000
total_biens_uniques     6000
total_batches              6
prix_moyen          192460.22
prix_median         188832.50
prix_min             20335.00
prix_max            458060.00
surface_moyenne         231.49
surface_mediane         237.00
prix_m2_moyen          1058.47
prix_m2_median          780.87
```

DPE completeness:

```text
total_biens   6000
dpe_present   3577
dpe_missing   2423
```

The lower row count of the DPE mart is therefore expected and explained by missing DPE data.

---

# 11. DBT / ANALYTICS

The project already contains dbt staging and analytics models.

Known marts include:

```text
mart_market_by_city
mart_market_by_dpe
mart_market_by_property_type
mart_market_by_source
mart_market_evolution
mart_market_overview
mart_mandat_performance
```

Verified source row coverage:

```text
mart_market_by_city          6000
mart_market_by_dpe           3577
mart_market_by_property_type 6000
mart_market_by_source        6000
mart_market_evolution        6000
warehouse.fact_annonce       6000
```

`mart_mandat_performance` exposes:

```text
statut
type_mandat
est_exclusif
nb_mandats
nb_clients
nb_chasseurs
duree_moyenne_jours
duree_min_jours
duree_max_jours
```

Verified mandate totals:

```text
OLTP mandats   17
mart mandats   17
OLTP clients   17 represented in mandates
chasseurs       6
```

The mart contains meaningful groupings for:

```text
ACTIF
EXPIRE
SUSPENDU
TERMINE
```

and exclusive/non-exclusive mandates.

---

# 12. OBSERVABILITY

The cluster already contains:

- kube-prometheus-stack;
- Prometheus;
- Alertmanager;
- Grafana;
- Loki;
- Promtail;
- Tempo;
- OpenTelemetry Collector;
- Pushgateway.

Pushgateway service:

```text
retail-pushgateway.monitoring.svc.cluster.local:9091
```

The Real Estate pipeline uses:

```text
PUSHGATEWAY_JOB=real_estate_data_platform
```

The Airflow `collect_metrics` task executes:

```text
/app/observability/metrics/collect_metrics.py
```

from the project data-pipeline image.

The fresh Airflow audit proved `collect_metrics` succeeds.

---

# 13. GRAFANA

A PostgreSQL datasource for Real Estate has been provisioned.

Kubernetes Secret:

```text
monitoring/real-estate-grafana-datasource
```

The Grafana datasource sidecar successfully mounted:

```text
/etc/grafana/provisioning/datasources/datasource.yaml
```

The datasource is visible in the Grafana UI.

A Real Estate dashboard was also created and validated visually.

It includes Prometheus KPI panels such as:

```text
Listings
Clients
Chasseurs
Mandates
Active Mandates
Average Property Price
```

and PostgreSQL analytics panels such as:

```text
Listings by City
Average Price by City
```

This observability/dashboard work was deliberately put aside temporarily as a side quest after confirming it works.

Do not restart Grafana design work unless it becomes the next agreed project step.

---

# 14. SECRET HANDLING

The Real Estate PostgreSQL Kubernetes Secret exists:

```text
real-estate-postgresql-secret
```

Keys:

```text
POSTGRES_DB
POSTGRES_HOST
POSTGRES_PASSWORD
POSTGRES_PORT
POSTGRES_USER
```

There is currently no External Secrets Operator / SecretStore / ClusterSecretStore / SealedSecret CRD installed.

For Grafana datasource provisioning, GitLab CI reads the existing Kubernetes PostgreSQL Secret, renders a template with `envsubst`, and creates/updates the Grafana datasource Secret in `monitoring`.

Do not hard-code PostgreSQL credentials into Git.

Also note that the shell GitLab runner has `/usr/bin/envsubst` but did not have `python`, which is why the rendering logic was changed away from Python.

---

# 15. OPENMETADATA

OpenMetadata version:

```text
1.12.11
```

Namespace:

```text
openmetadata
```

Core components are healthy:

```text
mysql-0
openmetadata
opensearch-0
```

Three Real Estate CronJobs exist:

```text
real-estate-postgresql-ingestion
real-estate-postgresql-profiler
real-estate-dbt-ingestion
```

Schedules:

```text
PostgreSQL ingestion   10 2 * * *
Profiler               45 2 * * *
dbt ingestion          30 3 * * *
```

IMPORTANT:

All three currently have:

```text
suspend: true
```

Do not automatically unsuspend them without discussing whether we want permanent scheduling.

For the audit we manually created fresh Jobs from the CronJobs.

---

# 16. OPENMETADATA AUDIT RESULTS — 27 AUGUST 2026

## PostgreSQL metadata ingestion

Fresh audit Job:

```text
real-estate-postgresql-ingestion-audit
```

Result:

```text
Complete 1/1
```

The ingestion workflow completed successfully.

There is a non-blocking warning:

```text
pg_stat_statements does not exist
```

OpenMetadata therefore cannot retrieve PostgreSQL query-history metadata through `GetQueries`.

`GetQueries` is non-mandatory and does NOT break metadata ingestion.

Do not enable or modify PostgreSQL extensions blindly. Treat this as a later optional improvement.

## PostgreSQL profiler

Fresh audit Job:

```text
real-estate-postgresql-profiler-audit
```

Result:

```text
Complete 1/1
Duration: ~2m26s
```

Profiler log reported:

```text
Profiler: Processed 231 records
Profiler errors: 0
```

Warnings such as:

```text
No implementation found for postgresql
```

did not prevent profiler completion.

The same optional `pg_stat_statements` warning was present.

## dbt ingestion

Fresh audit Job:

```text
real-estate-dbt-ingestion-audit
```

Result:

```text
Complete 1/1
```

The init phase generated/currently exposed dbt artifacts:

```text
catalog.json
manifest.json
run_results.json
semantic_manifest.json
graph.gpickle
graph_summary.json
compiled/
run/
```

Effective configuration targets:

```text
OpenMetadata:
http://openmetadata.openmetadata.svc.cluster.local:8585/api

service:
real-estate-postgresql

update_descriptions: true
update_owners: false
include_tags: true
```

The dbt/OpenMetadata workflow reported:

```text
dbt records processed:          108
OpenMetadata records processed: 126
errors:                           0
workflow success:              100%
```

Lineage processing ran successfully.

---

# 17. CURRENT OPENMETADATA ISSUE TO RESUME FROM

THIS IS THE MAIN UNFINISHED POINT AT THE CURRENT CHECKPOINT.

Although dbt ingestion completed successfully, OpenMetadata rejected description PATCH operations for several marts with messages similar to:

```text
Invalid name ...
```

Affected models include:

```text
mart_mandat_performance
mart_market_overview
mart_market_by_source
mart_market_by_property_type
mart_market_by_dpe
mart_market_evolution
```

The workflow still completed successfully, so this is a metadata-quality issue, NOT a broken ingestion pipeline.

The previous conversation was about to inspect the local dbt `schema.yml` definitions to determine why these descriptions are rejected.

DO NOT immediately modify OpenMetadata or the marts.

FIRST locate and inspect the relevant dbt YAML metadata definitions in the repository.

A suggested Windows discovery command was:

```powershell
Get-ChildItem -Recurse -Filter schema.yml | Select-Object FullName
```

Then inspect occurrences of the affected model names.

This is the precise technical point from which continuation should begin after reviewing this migration document.

---

# 18. GOVERNANCE-AS-CODE

Governance has already been implemented and deployed.

Repository structure includes:

```text
governance/
├── Dockerfile
├── apply-governance.sh
├── README.md
├── requirements.txt
├── scripts/
│   └── main.py
├── docs/
│   └── governance-config.json
├── glossary/
│   └── real_estate_glossary.json
├── ownership/
│   └── real_estate_ownership.json
├── quality/
│   └── real_estate_quality.json
└── tagging/
    ├── real_estate_tags.json
    └── real_estate_data_layers.json
```

Governance is published through CI/GitOps into OpenMetadata.

Argo CD application:

```text
openmetadata-governance
```

A Governance-as-Code Kubernetes Job has already completed successfully.

DataLayer tagging was verified for warehouse entities including dimensions and facts.

Do not recreate governance from scratch.

---

# 19. GITOPS / OPENMETADATA DEPLOYMENT

OpenMetadata deployment manifests live under:

```text
deploy/openmetadata/
```

including configuration for ingestion, dbt and governance.

GitLab publishes the relevant manifests into the GitOps repository:

```text
lab-gitops
```

Argo CD then reconciles the cluster.

Again: permanent configuration changes should follow Git → GitLab CI → GitOps → Argo CD, rather than only being patched manually in Kubernetes.

---

# 20. DATA-PIPELINE IMAGE

The project builds a reusable data-pipeline container.

It includes tooling such as:

```text
postgresql-client
git
dbt-core
dbt-postgres
prometheus-client
boto3
psycopg
python-dotenv
```

and project scripts for:

- generated source data;
- RAW loading;
- S3 transfer;
- RAW → STAGING;
- validation;
- warehouse loading;
- metrics collection.

Airflow KubernetesPodOperator tasks use the GitLab registry image:

```text
gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
```

with image pull secret:

```text
gitlab-registry
```

Do not assume scripts execute on the Windows machine.

---

# 21. DOCUMENTATION PHILOSOPHY

Documentation is an important project deliverable, not an afterthought.

We document:

- what was implemented;
- why it was implemented;
- how it works;
- architecture choices;
- logical relationships;
- deployment mechanism;
- tests;
- validation evidence;
- governance;
- security;
- observability;
- limitations;
- remaining work;
- relationship to the Diginamic competency framework.

Prefer completing written documentation before spending time on architecture diagrams unless a diagram is explicitly needed.

A consolidated progress checkpoint already exists:

```text
PROJECT-PROGRESS-2026-08-27.md
```

Use it as supporting project evidence.

---

# 22. THINGS THAT ARE ALREADY PROVEN — DO NOT REDO WITHOUT REASON

The following have already been validated:

```text
PostgreSQL running                         ✅
RAW ingestion                              ✅
RAW validation                             ✅
STAGING transformation                     ✅
STAGING validation                         ✅
OLTP load                                  ✅
OLTP validation                            ✅
Warehouse load                             ✅
Warehouse validation                       ✅
dbt run                                    ✅
dbt test                                   ✅
Prometheus metrics collection              ✅
Fresh full Airflow DAG                     ✅
Grafana PostgreSQL datasource              ✅
Grafana dashboard proof of concept         ✅
OpenMetadata PostgreSQL ingestion          ✅
OpenMetadata profiler                      ✅
OpenMetadata dbt ingestion                 ✅
OpenMetadata dbt lineage processing        ✅
Governance-as-Code                         ✅
Argo CD / GitOps deployment mechanisms     ✅
```

Do not send me back through all of these validations unless a new change requires regression testing.

---

# 23. KNOWN TECHNICAL DEBT / OPEN ITEMS

Keep these separate from already validated functionality.

### OpenMetadata dbt descriptions

Investigate and fix `Invalid name` PATCH warnings for several marts.

### pg_stat_statements

Optional improvement.

OpenMetadata cannot currently retrieve query history because PostgreSQL does not expose `pg_stat_statements`.

This does NOT block the project.

### OpenMetadata schedules

The three Real Estate CronJobs are currently suspended.

Later decide whether production-like scheduled execution should be enabled.

### Observability

The foundation works, but dashboards/alerts can be expanded later.

### Documentation

Continue producing evidence-oriented project documentation and mapping implementation to the Diginamic competencies.

### Final evaluation

Eventually perform a complete gap analysis against the Fil Rouge reference/evaluation grid, but do not assume missing work until comparing against the actual project documents.

---

# 24. HOW TO CONTINUE THIS CONVERSATION

At the beginning of the new chat:

1. Read this entire migration prompt.
2. Do NOT ask me to explain the infrastructure again.
3. Do NOT propose rebuilding components already marked validated.
4. Respect the GitLab CI / GitOps / Kubernetes deployment model.
5. Work one operational step at a time.
6. Wait for my command output before proceeding.
7. When we modify a repository file, provide the complete file when requested.
8. Preserve evidence useful for final documentation and the Diginamic evaluation.

The immediate technical continuation point is:

```text
Investigate OpenMetadata dbt description PATCH warnings
→ locate dbt schema.yml
→ inspect affected mart metadata
→ identify exact naming/description problem
→ fix in Git
→ deploy through existing pipeline
→ rerun dbt/OpenMetadata ingestion
→ verify descriptions + lineage
```

After that, return to the project roadmap and determine the next highest-priority Fil Rouge requirement rather than drifting into optional side quests.

---

# 25. AUTHORITATIVE PROJECT CHECKPOINT

The following is the complete consolidated progress document produced immediately before this migration prompt.

It should be treated as supporting evidence and additional detail for everything above.

---

# Projet Fil Rouge — Chasse Immobilière
## État d'avancement technique consolidé

**Date de consolidation : 27 août 2026**

## 1. Objectif du document

Ce document constitue un point de situation technique consolidé du projet **chasse_immobiliere**. Il décrit ce qui a été conçu, déployé, exécuté et effectivement validé sur l'infrastructure Kubernetes, ainsi que les décisions techniques et les points restant à traiter.

Il sert de preuve d'avancement, de support de soutenance et de référence avant la poursuite des travaux.

---

## 2. Architecture générale actuellement validée

La plateforme suit une chaîne Data complète :

```text
Git repository chasse_immobiliere
        |
        v
GitLab CI/CD
        |
        +--> validation / migrations / construction image
        +--> publication des DAG Airflow
        +--> publication GitOps OpenMetadata
        |
        v
Kubernetes
        |
        +--> PostgreSQL real-estate
        |       +--> raw
        |       +--> staging
        |       +--> real_estate (OLTP)
        |       +--> warehouse (OLAP)
        |       +--> analytics (dbt marts)
        |
        +--> Airflow
        |       +--> génération
        |       +--> ingestion RAW
        |       +--> contrôles qualité
        |       +--> STAGING
        |       +--> OLTP
        |       +--> Warehouse
        |       +--> dbt run/test
        |       +--> métriques
        |
        +--> OpenMetadata
        |       +--> ingestion PostgreSQL
        |       +--> profiler
        |       +--> ingestion dbt
        |       +--> lineage
        |       +--> Governance-as-Code
        |
        +--> Prometheus / Pushgateway / Grafana / Loki / Tempo
```

Le poste Windows n'est pas utilisé comme environnement Kubernetes local. Le code est développé dans le dépôt puis publié/déployé par GitLab CI, GitOps/Argo CD et les composants du cluster.

---

## 3. PostgreSQL et organisation des données

La base `real_estate` est organisée en couches séparées afin de distinguer ingestion, nettoyage, exploitation transactionnelle et analytique.

### 3.1 RAW

La couche `raw` conserve les données telles qu'elles arrivent de la source et leur contexte d'ingestion.

État contrôlé avant le dernier run du 27 août :

- `raw.annonces` : 7 000 lignes
- `raw.recherches` : 35 lignes

Le batch historique `generated-1000-v1` contient 1 000 annonces distinctes provenant de :

```text
database/fixtures/annonces/annonces.csv
```

Il s'agit d'un batch initial/historique qui explique l'écart entre RAW et les couches aval.

### 3.2 STAGING

La couche staging transforme les valeurs textuelles RAW vers des types métier et porte les résultats des contrôles qualité.

État contrôlé :

- `staging.annonces` : 6 000 lignes
- `staging.recherches` : 30 lignes

Contrôle qualité réalisé sur les 6 000 annonces :

```text
total_rows              = 6000
valid_rows              = 6000
invalid_rows            = 0
quality_not_evaluated   = 0
missing_reference       = 0
missing_price           = 0
invalid_price           = 0
missing_surface         = 0
invalid_surface         = 0
missing_city            = 0
missing_postal_code     = 0
distinct_references     = 6000
```

Ainsi, **100 % des 6 000 annonces staging contrôlées sont valides sur les règles testées**.

### 3.3 OLTP — schéma `real_estate`

Le modèle métier transactionnel contient notamment :

- `client`
- `chasseur`
- `secteur`
- `source`
- `mandat`
- `mandat_secteur`
- `demande`
- `demande_version`
- `bien`
- `commentaire`
- `document`
- `paiement`
- `presentation`
- `visite`
- `utilisateur`
- `piece_jointe`
- `audit_log`
- `bareme_commission`

État contrôlé :

```text
bien                6000
chasseur               6
client                 18
demande                17
demande_version        17
mandat                 17
mandat_secteur         17
secteur                10
source                  1
bareme_commission       6
```

Les tables prévues pour des événements métier futurs (`paiement`, `presentation`, `visite`, etc.) sont présentes même lorsqu'elles ne contiennent pas encore de données.

---

## 4. Warehouse / OLAP

Le schéma `warehouse` implémente le modèle analytique.

Dimensions principales :

- `dim_date`
- `dim_source`
- `dim_localisation`
- `dim_bien`
- `dim_chasseur`
- `dim_client`
- `dim_demande_version`
- `dim_secteur`

Bridge :

- `bridge_mandat_secteur`

Tables de faits :

- `fact_annonce`
- `fact_mandat`
- `fact_paiement`
- `fact_presentation`
- `fact_demande`
- `fact_matching`
- `fact_bien_daily`

### 4.1 Volumétrie contrôlée

```text
bridge_mandat_secteur   17
dim_bien              6001
dim_chasseur             7
dim_client              19
dim_date              5844
dim_demande_version     18
dim_localisation        18
dim_secteur             11
dim_source               2
fact_annonce           6000
fact_mandat              17
```

Les dimensions utilisent une ligne technique/inconnue, ce qui explique les différences `6000 -> 6001`, `18 -> 19`, etc.

### 4.2 Réconciliation OLTP / Warehouse

La cohérence a été contrôlée explicitement :

```text
entity            OLTP    Warehouse
bien              6000    6000
chasseur             6       6
client              18      18
demande_version     17      17
mandat              17      17
secteur             10      10
```

La réconciliation est donc correcte pour les entités contrôlées.

### 4.3 Intégrité de `fact_annonce`

Sur les 6 000 faits :

```text
total_fact_rows             = 6000
missing_dim_bien            = 0
missing_dim_source          = 0
missing_dim_localisation    = 0
missing_publication_date    = 0
missing_collection_date     = 0
```

Aucune clé dimensionnelle manquante n'a été détectée dans ce contrôle.

---

## 5. Analyse des batches d'ingestion

Six batches applicatifs ont été retrouvés simultanément dans RAW, STAGING et Warehouse :

```text
generated-20260822T000000
generated-20260823T073715
generated-20260823T194031
generated-20260823T205547
generated-20260824T065752
generated-20260824T142334
```

Chaque batch contient :

```text
1000 lignes
1000 références distinctes
```

Cela donne :

```text
6000 observations
6000 biens/références uniques
```

L'impression initiale de « multiplication » des annonces a donc été expliquée : les exécutions successives du générateur ont produit des références différentes et non plusieurs observations du même ensemble de 1 000 biens.

Le batch `generated-1000-v1` existe uniquement dans RAW et correspond aux fixtures historiques.

---

## 6. dbt et couche Analytics

Le projet dbt transforme les données du Warehouse en modèles analytiques utilisables pour les KPI, dashboards et usages métier.

Staging dbt notamment :

- `stg_fact_annonce`
- `stg_dim_bien`

Marts créés :

- `mart_market_overview`
- `mart_market_by_city`
- `mart_market_by_dpe`
- `mart_market_by_property_type`
- `mart_market_by_source`
- `mart_market_evolution`
- `mart_mandat_performance`

### 6.1 Couverture des annonces

Contrôle effectué :

```text
mart_market_by_city             6000
mart_market_by_property_type    6000
mart_market_by_source           6000
mart_market_evolution           6000
warehouse.fact_annonce          6000
```

`mart_market_by_dpe` couvre 3 577 biens. Ce résultat a été expliqué par la donnée source et non par une perte du pipeline :

```text
total_biens   = 6000
dpe_present   = 3577
dpe_missing   = 2423
```

### 6.2 KPI marché contrôlés

```text
total_annonces          6000
total_biens_uniques     6000
total_batches              6
prix_moyen          192460.22
prix_median         188832.50
prix_min             20335.00
prix_max            458060.00
surface_moyenne         231.49
surface_mediane         237.00
prix_m2_moyen          1058.47
prix_m2_median          780.87
```

### 6.3 Mart performance des mandats

`analytics.mart_mandat_performance` expose :

- statut
- type_mandat
- est_exclusif
- nb_mandats
- nb_clients
- nb_chasseurs
- duree_moyenne_jours
- duree_min_jours
- duree_max_jours

Réconciliation :

```text
oltp_mandats     = 17
mart_mandats     = 17
oltp_clients     = 17 (clients représentés dans les mandats)
oltp_chasseurs   = 6
```

Les six groupes métier observés incluent ACTIF, EXPIRE, SUSPENDU et TERMINE, ainsi que les mandats EXCLUSIF / NON_EXCLUSIF.

---

## 7. Orchestration Airflow

Le DAG principal est :

```text
real_estate_ingestion
```

Il est publié dans le dépôt `airflow-dags` par le job GitLab CI `airflow:publish-dags`. Le scheduler utilise un conteneur `git-sync` qui synchronise ce dépôt dans un worktree monté dans Airflow.

La chaîne actuelle est :

```text
start
  -> generate_source_data
  -> load_raw
  -> validate_raw
  -> transform_staging
  -> validate_staging
  -> load_oltp
  -> validate_oltp
  -> load_warehouse
  -> validate_warehouse
  -> dbt_run
  -> dbt_test
  -> collect_metrics
  -> end
```

### 7.1 Validation historique

Les runs observés des 22, 23 et 24 août étaient tous en `success`.

### 7.2 Validation complète du 27 août 2026

Run :

```text
manual__2026-08-27T20:50:02+00:00
```

Toutes les tâches ont terminé avec succès :

```text
start                 success
generate_source_data  success
load_raw              success
validate_raw          success
transform_staging     success
validate_staging      success
load_oltp             success
validate_oltp         success
load_warehouse        success
validate_warehouse    success
dbt_run               success
dbt_test              success
collect_metrics       success
end                   success
```

Ceci valide désormais la chaîne Data complète **jusqu'à la collecte des métriques**.

---

## 8. Observabilité

Une structure dédiée `observability/` a été mise en place avec notamment :

```text
observability/
├── alerts/
├── grafana/
│   └── dashboards/
├── metrics/
└── prometheus/
```

La plateforme de monitoring Kubernetes existante comprend notamment :

- Prometheus / kube-prometheus-stack
- Alertmanager
- Grafana
- Loki
- Promtail
- Tempo
- OpenTelemetry Collector
- Pushgateway

Le Pushgateway utilisé est :

```text
retail-pushgateway.monitoring.svc.cluster.local:9091
```

Le DAG Airflow exécute maintenant `collect_metrics`, utilisant l'image data-pipeline et le code sous `/app/observability/metrics`.

Le run du 27 août confirme :

```text
collect_metrics = success
```

La collecte des métriques est donc intégrée à l'orchestration. La finalisation des dashboards/alertes peut être traitée séparément sans bloquer le cœur du pipeline.

---

## 9. OpenMetadata

Version actuellement utilisée :

```text
OpenMetadata Server 1.12.11
OpenMetadata ingestion image 1.12.11
```

Les composants principaux OpenMetadata/MySQL/OpenSearch sont opérationnels.

Trois workflows Real Estate sont déployés sous forme de CronJobs Kubernetes :

```text
real-estate-postgresql-ingestion
real-estate-postgresql-profiler
real-estate-dbt-ingestion
```

Ils sont actuellement configurés avec `suspend: true`, ce qui permet leur déclenchement contrôlé/manuellement pour validation.

Planification définie :

```text
PostgreSQL ingestion : 10 2 * * *
Profiler             : 45 2 * * *
dbt ingestion        : 30 3 * * *
```

### 9.1 PostgreSQL metadata ingestion

Un Job d'audit a été créé depuis le CronJob :

```text
real-estate-postgresql-ingestion-audit
```

Résultat :

```text
Complete 1/1
```

L'ingestion PostgreSQL vers OpenMetadata est donc validée.

### 9.2 PostgreSQL profiler

Job :

```text
real-estate-postgresql-profiler-audit
```

Résultat :

```text
Complete 1/1
```

Le profiler a indiqué notamment :

```text
Profiler: Processed 231 records
found 0 errors
```

Un avertissement existe pour `pg_stat_statements` : l'extension n'est pas présente et OpenMetadata ne peut donc pas récupérer les requêtes PostgreSQL via cette fonctionnalité optionnelle.

Ce point n'empêche pas le profiler de terminer avec succès.

### 9.3 dbt ingestion

Job :

```text
real-estate-dbt-ingestion-audit
```

Résultat Kubernetes :

```text
Complete 1/1
```

Les artifacts dbt sont bien générés :

```text
catalog.json
manifest.json
run_results.json
semantic_manifest.json
compiled/
run/
```

Configuration OpenMetadata effective :

```text
update_descriptions: true
update_owners: false
include_tags: true
service: real-estate-postgresql
```

Résumé final :

```text
Workflow dbt:
  Processed records: 108
  Errors: 0
  Success: 100%

Workflow OpenMetadata:
  Processed records: 126
  Errors: 0
  Success: 100%

Workflow Success: 100%
```

Le traitement de lineage est également visible dans les logs (`GetLineageByQuery`).

### 9.4 Points non bloquants détectés

Plusieurs descriptions de marts ont produit :

```text
Failed to update Table [...]
Reason: Invalid name ...
```

Les modèles concernés incluent notamment :

- `mart_mandat_performance`
- `mart_market_overview`
- `mart_market_by_source`
- `mart_market_by_property_type`
- `mart_market_by_dpe`
- `mart_market_evolution`

Le workflow global reste à 100 % et sans erreur déclarée, mais ces PATCH de métadonnées ont été ignorés. Ce point doit être nettoyé ultérieurement afin d'obtenir une publication de descriptions totalement propre.

OpenMetadata signale également l'absence d'un utilisateur/équipe `real_estate_user` lors de tentatives de résolution d'owner dbt. La configuration actuelle demande néanmoins `update_owners: false`; ce point n'est donc pas bloquant pour l'ingestion actuelle.

---

## 10. Governance-as-Code

Une couche Governance-as-Code dédiée est intégrée au projet avec :

```text
governance/
├── Dockerfile
├── apply-governance.sh
├── requirements.txt
├── scripts/main.py
├── docs/governance-config.json
├── glossary/real_estate_glossary.json
├── ownership/real_estate_ownership.json
├── quality/real_estate_quality.json
└── tagging/
    ├── real_estate_tags.json
    └── real_estate_data_layers.json
```

Le déploiement est piloté par GitLab CI et GitOps/Argo CD, et non par des opérations Kubernetes locales depuis Windows.

Le Job Kubernetes :

```text
real-estate-governance-apply
```

avait été validé avec :

```text
Complete 1/1
Governance-as-Code execution completed
```

Le tagging `DataLayer` a notamment été vérifié sur les dimensions et facts du Warehouse.

---

## 11. CI/CD et GitOps

Le projet utilise GitLab CI comme point d'entrée d'automatisation.

Les responsabilités sont séparées :

```text
Code source
    |
    v
GitLab CI
    |
    +--> validation DB / migrations
    +--> build image data-pipeline
    +--> publication DAG -> airflow-dags
    +--> publication manifests -> lab-gitops
    |
    v
Argo CD / git-sync / Kubernetes
```

Pour Airflow, le job `airflow:publish-dags` :

1. valide la présence du DAG ;
2. clone `https://gitlab.local/root/airflow-dags.git` ;
3. copie `pipelines/airflow/*.py` vers `dags/` ;
4. commit les changements ;
5. pousse sur `main`.

Le `git-sync` du scheduler récupère ensuite le dépôt. Cette architecture explique pourquoi modifier uniquement un fichier local Windows sans le sauvegarder/committer/publier ne modifie pas immédiatement le DAG Kubernetes.

Ce comportement a été vérifié lors de l'ajout de `collect_metrics`.

---

## 12. Validation de bout en bout obtenue

À ce stade, les composants suivants ont été réellement testés :

```text
Source/générateur             VALIDÉ
        |
RAW                           VALIDÉ
        |
Data Quality RAW              VALIDÉ
        |
STAGING                       VALIDÉ
        |
Data Quality STAGING          VALIDÉ
        |
OLTP real_estate              VALIDÉ
        |
Validation OLTP               VALIDÉ
        |
Warehouse                     VALIDÉ
        |
Validation Warehouse          VALIDÉ
        |
dbt run                       VALIDÉ
        |
dbt test                      VALIDÉ
        |
Analytics marts               VALIDÉ
        |
Metrics collection            VALIDÉ

PostgreSQL -> OpenMetadata    VALIDÉ
Profiler -> OpenMetadata      VALIDÉ
dbt -> OpenMetadata           VALIDÉ
Governance-as-Code            VALIDÉ
```

Le projet n'est donc plus au stade d'une architecture théorique : la chaîne a été déployée et exécutée sur Kubernetes avec des résultats observables.

---

## 13. Points restant à traiter

Les éléments suivants ne remettent pas en cause les validations précédentes mais restent à finaliser :

1. Corriger les descriptions dbt rejetées par OpenMetadata (`Invalid name`).
2. Décider si `pg_stat_statements` doit être activé pour enrichir OpenMetadata avec les statistiques/requêtes PostgreSQL.
3. Nettoyer si nécessaire les avertissements de résolution de l'owner `real_estate_user`.
4. Finaliser les dashboards Grafana/KPI et les alertes Prometheus comme volet observabilité.
5. Décider du passage des CronJobs OpenMetadata de `suspend: true` vers une exécution planifiée automatique lorsque la phase de validation manuelle sera terminée.
6. Continuer à enrichir les preuves, tests et documentation nécessaires au référentiel/à la soutenance.

---

## 14. Conclusion au 27 août 2026

La plateforme dispose maintenant d'une chaîne Data cohérente et effectivement opérationnelle :

```text
GitLab CI/CD
    -> Kubernetes
    -> Airflow
    -> RAW
    -> Data Quality
    -> STAGING
    -> OLTP
    -> Warehouse
    -> dbt
    -> Analytics
    -> Metrics
    -> OpenMetadata
    -> Governance
```

Les contrôles effectués ont confirmé la qualité des 6 000 annonces staging, la réconciliation des principales entités OLTP/Warehouse, l'intégrité des clés de `fact_annonce`, l'exécution complète du DAG Airflow avec `collect_metrics`, ainsi que les trois workflows OpenMetadata (metadata ingestion, profiler et dbt ingestion).

Le socle Data Engineering, analytique, gouvernance et observabilité est donc suffisamment avancé pour poursuivre les travaux à partir d'une base validée et documentée, plutôt que de reconstruire ou réexpliquer l'infrastructure à chaque étape.


---

# END OF MIGRATION CONTEXT

You now have the current project state.

Do not begin by summarizing everything back to me.

Acknowledge that you understand the architecture and current checkpoint, then continue from the immediate unfinished task one step at a time.
