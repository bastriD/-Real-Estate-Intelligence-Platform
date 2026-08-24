# MASTER HANDOVER MONOLITH — CHASSE IMMOBILIÈRE / FIL ROUGE DATA & IA

**Status:** 24 August 2026  
**Purpose:** single-file migration prompt for continuing the project in another ChatGPT conversation without re-explaining the infrastructure, deployment chain, data pipeline, dbt/OpenMetadata integration, validated results, or current work.

---

## 1. Instructions for the next chat

This is an EXISTING and DEPLOYED project named **Chasse Immobilière**, part of the Diginamic Fil Rouge EISI Data & IA.

Do not redesign it from scratch. Do not suggest installing Kubernetes locally on Windows. Do not bypass the existing GitLab CI / GitOps / Argo CD / Kubernetes model. Treat everything marked validated below as established unless new runtime output proves a regression.

Work strictly step by step: give ONE implementation or verification step, then wait for my output or `YES`. When I ask for a script/configuration file, give the COMPLETE file, not fragments.

The immediate continuation point is **Real Estate Governance-as-Code**.

---

## 2. Workstation and execution environment

Local workstation:

```text
Windows 11
PowerShell
VS Code
Git
```

Main repository:

```text
C:\Users\bastr\Desktop\DIGINAMIC\chasse_immobiliere
```

Local GitOps clone:

```text
C:\Users\bastr\Desktop\GIT
```

Kubernetes is NOT used locally on Windows. Cluster commands are normally run remotely from:

```text
root@k8s-cp-01
```

---

## 3. Platform

Existing homelab/platform includes:

```text
Proxmox
kubeadm HA Kubernetes
Flannel
NGINX Ingress
cert-manager
Argo CD
GitLab CE
GitLab Runner
Airflow
MLflow
OpenMetadata 1.12.11
MinIO
Prometheus/Grafana
Loki/Promtail
Tempo
OTEL Collector
```

Relevant namespaces:

```text
airflow
argocd
openmetadata
real-estate
retail-data
monitoring
mlflow
mlops
```

---

## 4. Core deployment architecture

Normal delivery is Git-based, not manual pod editing.

```text
chasse_immobiliere
        |
        v
     GitLab CI
        |
        +--------------------+
        |                    |
        v                    v
Container Registry      specialized Git repos
        |                    |
        |              +-----+------+
        |              |            |
        |              v            v
        |        airflow-dags    lab-gitops
        |              |            |
        |              v            v
        |        Airflow git-sync  Argo CD
        |              |            |
        +--------------+------------+
                       |
                       v
                   Kubernetes
```

Airflow DAG delivery:

```text
chasse_immobiliere
 -> GitLab CI
 -> root/airflow-dags
 -> Airflow git-sync
 -> Airflow scheduler
 -> KubernetesExecutor
```

OpenMetadata manifest delivery:

```text
chasse_immobiliere/deploy/openmetadata
 -> GitLab CI
 -> root/lab-gitops/workloads/openmetadata/ingestions
 -> Argo CD application openmetadata-ingestions
 -> namespace openmetadata
```

Permanent Kubernetes resources belong in GitOps.

---

## 5. Repositories

### Main project

```text
chasse_immobiliere
```

Contains database, seeds, tests, Airflow DAG, dbt project, deployment definitions, and upcoming governance code.

### Airflow DAG repository

```text
https://gitlab.local/root/airflow-dags.git
```

DAGs are published by CI.

### GitOps repository

```text
https://gitlab.local/root/lab-gitops
```

Local clone:

```text
C:\Users\bastr\Desktop\GIT
```

Important paths:

```text
workloads/openmetadata/ingestions
workloads/openmetadata-governance
apps/openmetadata-governance
```

---

## 6. Credentials / secrets model

Never reproduce actual token/password values in documentation or source code.

Known Kubernetes secrets:

```text
airflow/airflow-git-credentials
openmetadata/lab-gitops-git-credentials
openmetadata/openmetadata-ingestion-secrets
openmetadata/om-admin-token
```

`airflow-git-credentials` keys:

```text
GITSYNC_PASSWORD
GITSYNC_USERNAME
GIT_SYNC_PASSWORD
GIT_SYNC_USERNAME
```

`lab-gitops-git-credentials` keys:

```text
GIT_USERNAME
GIT_TOKEN
```

`openmetadata-ingestion-secrets` keys:

```text
AIRFLOW_DB_PASSWORD
OM_JWT_TOKEN
REAL_ESTATE_POSTGRES_PASSWORD
RETAIL_POSTGRES_PASSWORD
```

GitLab shell jobs can retrieve GitOps credentials from Kubernetes with `kubectl`, build a temporary `/tmp/.netrc`, clone/push, and delete the credential file in `after_script`.

Sensitive credentials were pasted during troubleshooting. Do not repeat them. Rotate exposed credentials if not already rotated.

---

## 7. Real Estate data architecture

Implemented logical flow:

```text
source generation
      |
      v
MinIO / S3-compatible storage
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
ANALYTICS / MARTS
      |
      v
OpenMetadata catalog + lineage
```

PostgreSQL:

```text
service: real-estate-postgresql.real-estate.svc.cluster.local
port: 5432
database: real_estate
user: real_estate_user
namespace: real-estate
```

OLTP/business model includes entities such as:

```text
client
chasseur
secteur
source
mandat
mandat_secteur
demande
bien
visite
utilisateur
role
piece_jointe
audit_log
```

---

## 8. Data pipeline container

Main image:

```text
gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
```

Dockerfile:

```text
deploy/docker/Dockerfile.data-pipeline
```

Important contents include Python 3.12 slim, `postgresql-client`, `git`, project requirements, data-generation/load/transform scripts, SQL DQ tests, warehouse loader, and `pipelines/dbt`.

`git` was added because `dbt debug` required it.

---

## 9. Airflow

DAG ID:

```text
real_estate_ingestion
```

Current validated task chain:

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
 -> end
```

A complete manual run on 24 August 2026 succeeded. Every task above reached `success`.

Therefore Airflow orchestration through dbt is operational.

DAG source is under:

```text
pipelines/airflow/real_estate_ingestion_dag.py
```

The main repository CI publishes Airflow Python files to `root/airflow-dags`.

---

## 10. dbt

Project:

```text
pipelines/dbt/
├── dbt_project.yml
├── profiles.yml.example
└── models/
    ├── staging/
    │   ├── schema.yml
    │   ├── sources.yml
    │   ├── stg_dim_bien.sql
    │   └── stg_fact_annonce.sql
    └── marts/
        ├── mart_market_by_city.sql
        └── schema.yml
```

Validated versions inside the pipeline image:

```text
dbt-core 1.9.0
dbt-postgres 1.9.0
```

Validated connection:

```text
host: real-estate-postgresql.real-estate.svc.cluster.local
port: 5432
database: real_estate
schema: analytics
user: real_estate_user
```

`dbt debug` result:

```text
profiles.yml valid
dbt_project.yml valid
git found
connection OK
All checks passed
```

### Models

```text
analytics.stg_dim_bien
analytics.stg_fact_annonce
analytics.mart_market_by_city
```

`stg_fact_annonce` exposes validated `warehouse.fact_annonce`.

`mart_market_by_city` aggregates market information by country/city/postal code and contains measures such as:

```text
nb_annonces
prix_moyen
prix_min
prix_max
surface_moyenne
prix_m2_moyen
premiere_publication
derniere_publication
```

### Validation

`dbt run`:

```text
PASS=3 WARN=0 ERROR=0 SKIP=0 TOTAL=3
```

`dbt test`:

```text
PASS=19 WARN=0 ERROR=0 SKIP=0 TOTAL=19
```

Do not re-debug dbt unless a later change causes a regression.

---

## 11. OpenMetadata PostgreSQL ingestion

OpenMetadata version:

```text
1.12.11
```

Internal API/service:

```text
http://openmetadata.openmetadata.svc.cluster.local:8585/api
```

Real Estate resources deployed by Argo CD:

```text
configmap/real-estate-postgresql-ingestion-config
configmap/real-estate-postgresql-profiler-config
cronjob/real-estate-postgresql-ingestion
cronjob/real-estate-postgresql-profiler
```

Known schedules:

```text
real-estate-postgresql-ingestion: 10 2 * * *
real-estate-postgresql-profiler: 45 2 * * *
```

They were intentionally `suspend: true` during controlled testing.

Argo tracking example:

```text
openmetadata-ingestions:batch/CronJob:openmetadata/real-estate-postgresql-ingestion
```

PostgreSQL metadata ingestion completed with 100% workflow success and 0 errors.

Known non-blocking warning:

```text
pg_stat_statements does not exist
```

This only affects optional `GetQueries` functionality. Schema/table metadata ingestion succeeds.

---

## 12. OpenMetadata dbt ingestion

Project-side files:

```text
deploy/openmetadata/dbt/cronjob.yaml
deploy/openmetadata/dbt/kustomization.yaml
```

CI publishes them to:

```text
workloads/openmetadata/ingestions/real-estate-dbt/
```

Parent OpenMetadata ingestion kustomization contains:

```text
airflow
retail-postgresql
retail-postgresql-profiler
dbt
real-estate-postgresql
real-estate-dbt
```

Argo application:

```text
openmetadata-ingestions
```

Validated revision after deployment:

```text
d6f0e3f397d74a3315e06065ec710aa71ee8c4da
```

State:

```text
Synced | Healthy
```

CronJob:

```text
real-estate-dbt-ingestion
schedule: 30 3 * * *
suspend: true
```

Argo ownership:

```text
openmetadata-ingestions:batch/CronJob:openmetadata/real-estate-dbt-ingestion
```

The job follows the existing Retail pattern:

```text
initContainer generate-dbt-artifacts
    -> dbt run
    -> dbt test
    -> dbt docs generate
    -> target artifacts
main OpenMetadata ingestion container
    -> metadata ingest-dbt
    -> OpenMetadata API
```

---

## 13. Critical ingestion-order lesson

Initially OpenMetadata dbt ingestion could not resolve:

```text
analytics.mart_market_by_city
analytics.stg_dim_bien
analytics.stg_fact_annonce
```

The dbt views existed in PostgreSQL but had not yet been catalogued by the PostgreSQL metadata ingestion.

Correct operational sequence:

```text
dbt creates analytics views
 -> PostgreSQL metadata ingestion
 -> OpenMetadata catalogs the views
 -> dbt OpenMetadata ingestion
 -> dbt metadata and lineage attach to catalog entities
```

After rerunning PostgreSQL ingestion and then dbt ingestion, the missing-table warnings disappeared.

---

## 14. OpenMetadata lineage — definitively validated

Lineage persistence was verified directly through the OpenMetadata REST API, not merely inferred from ingestion logs.

Because the OpenMetadata container did not contain `curl`, a temporary pod using:

```text
curlimages/curl:8.12.1
```

was used to query the API.

### `mart_market_by_city`

API entity:

```text
real-estate-postgresql.real_estate.analytics.mart_market_by_city
```

Verified upstream nodes:

```text
real-estate-postgresql.real_estate.warehouse.dim_localisation
real-estate-postgresql.real_estate.analytics.stg_fact_annonce
```

Edges have:

```text
source: DbtLineage
```

OpenMetadata persisted:

```text
table-level lineage
column-level lineage
SQL query used by dbt
```

Examples:

```text
warehouse.dim_localisation.pays
 -> analytics.mart_market_by_city.pays

warehouse.dim_localisation.ville
 -> analytics.mart_market_by_city.ville

analytics.stg_fact_annonce.prix
 -> analytics.mart_market_by_city.prix_moyen

analytics.stg_fact_annonce.prix
 -> analytics.mart_market_by_city.prix_min

analytics.stg_fact_annonce.prix
 -> analytics.mart_market_by_city.prix_max

analytics.stg_fact_annonce.prix_m2
 -> analytics.mart_market_by_city.prix_m2_moyen
```

### `stg_fact_annonce`

API entity:

```text
real-estate-postgresql.real_estate.analytics.stg_fact_annonce
```

Verified upstream:

```text
warehouse.fact_annonce
```

Verified downstream:

```text
analytics.mart_market_by_city
```

Therefore persisted chain:

```text
warehouse.fact_annonce
        |
        v
analytics.stg_fact_annonce
        |
        v
analytics.mart_market_by_city
```

Column lineage includes fields such as:

```text
bien_key
prix
surface
prix_m2
ingestion_batch
reference_externe
source_file
date_publication_exacte
```

This milestone is COMPLETE.

---

## 15. Current non-blocking OpenMetadata warnings

### Technical PostgreSQL owner

`real_estate_user` is a database technical account but not an OpenMetadata business owner/team. Ownership should be handled deliberately through governance-as-code.

### dbt description PATCH warning

dbt schema YAML is valid. Long model descriptions are correctly placed under `description`, and the descriptions are visible through the OpenMetadata API.

Do not corrupt valid dbt YAML to silence a non-blocking patch warning.

### pg_stat_statements

Optional. Not required for current catalog/lineage success.

---

## 16. Current validated status

```text
Kubernetes platform                         VALIDATED
GitLab CI                                   VALIDATED
GitLab Registry                             VALIDATED
GitOps                                      VALIDATED
Argo CD                                     VALIDATED
Real Estate PostgreSQL                      VALIDATED
Airflow DAG publishing                      VALIDATED
Airflow orchestration                       VALIDATED
Source generation                           VALIDATED
RAW load                                    VALIDATED
RAW DQ                                      VALIDATED
STAGING transform                           VALIDATED
STAGING DQ                                  VALIDATED
OLTP load                                   VALIDATED
OLTP DQ                                     VALIDATED
Warehouse load                              VALIDATED
Warehouse DQ                                VALIDATED
dbt image/runtime                           VALIDATED
dbt connection                              VALIDATED
dbt run                                     3/3 PASS
dbt test                                    19/19 PASS
dbt analytics views                         VALIDATED
dbt integrated in Airflow                   VALIDATED
PostgreSQL -> OpenMetadata                  VALIDATED
Real Estate OM GitOps                       VALIDATED
dbt -> OpenMetadata                         VALIDATED
Table lineage                               VALIDATED
Column lineage                              VALIDATED
SQL lineage                                 VALIDATED
OpenMetadata API lineage proof              VALIDATED
```

Do not repeat these validations without a reason.

---

## 17. Existing governance platform pattern

Governance is the immediate next milestone.

Existing GitOps files:

```text
C:\Users\bastr\Desktop\GIT\apps\openmetadata-governance\application.yaml
C:\Users\bastr\Desktop\GIT\workloads\openmetadata-governance\governance-apply-job.yaml
C:\Users\bastr\Desktop\GIT\workloads\openmetadata-governance\kustomization.yaml
```

Current kustomization:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - governance-apply-job.yaml
```

Existing Retail job:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: retail-governance-apply
  namespace: openmetadata
spec:
  backoffLimit: 0
  template:
    metadata:
      labels:
        app: retail-governance-apply
    spec:
      restartPolicy: Never
      imagePullSecrets:
        - name: gitlab-registry-auth
      containers:
        - name: governance-apply
          image: gitlab.local:4567/root/retail_governance:latest
          imagePullPolicy: Always
          env:
            - name: OM_URL
              value: "http://openmetadata:8585/api"
            - name: OM_JWT_TOKEN
              valueFrom:
                secretKeyRef:
                  name: om-admin-token
                  key: jwtToken
```

Real Estate governance should mirror this proven pattern with its own image/job.

---

## 18. Previous Retail governance repository

The proven previous project structure is:

```text
retail_governance/
│   .gitignore
│   .gitlab-ci.yml
│   apply-governance.sh
│   Dockerfile
│   README.md
│   requirements.txt
│
├── docs/
│   └── governance-config.json
│
├── glossary/
│   └── retail_glossary.json
│
├── k8s/
│   ├── application.yaml
│   └── governance-apply-job.yaml
│
├── ownership/
│   ├── dim_customer.json
│   ├── dim_product.json
│   └── fact_sales.json
│
├── quality/
│   └── fact_sales_tests.json
│
├── scripts/
│   └── main.py
│
├── sprints/
│
└── tagging/
    └── fact_sales_tags.json
```

Do not invent a completely different Real Estate governance architecture. Adapt this pattern.

---

## 19. Real Estate governance target structure

At migration time, Real Estate governance implementation has NOT yet been built.

Target structure inside `chasse_immobiliere`:

```text
governance/
│   .gitignore
│   apply-governance.sh
│   Dockerfile
│   README.md
│   requirements.txt
│
├── docs/
│   └── governance-config.json
│
├── glossary/
│   └── real_estate_glossary.json
│
├── k8s/
│   ├── application.yaml
│   └── governance-apply-job.yaml
│
├── ownership/
│   └── Real Estate ownership definitions
│
├── quality/
│   └── Real Estate quality definitions
│
├── scripts/
│   └── main.py
│
└── tagging/
    └── Real Estate tags/classifications
```

Potential governance domains include:

```text
Client
Chasseur
Bien
Mandat
Demande
Secteur
Annonce
Présentation
Visite
Source
Prix
Prix/m²
Surface
Localisation
personal/contact information
business-sensitive data
financial data where present
audit/technical data
```

Do not assume every candidate is a current warehouse asset; inspect actual schemas before binding rules.

---

## 20. Governance objectives

Implement governance-as-code for OpenMetadata covering:

### Business glossary

Real Estate/chasse immobilière terms and definitions.

### Ownership

Separate technical ownership from business/data ownership. Do not blindly use PostgreSQL `real_estate_user` as business owner.

### Classification/tagging

At minimum consider:

```text
PII
RGPD/GDPR
business-sensitive
financial
technical
analytics
future AI/model-input classifications
```

### Data quality

Connect governance to real existing checks instead of inventing fake ones.

Already available:

```text
RAW DQ
STAGING DQ
OLTP DQ
WAREHOUSE DQ
19 dbt tests
```

### Traceability

Complement existing:

```text
Airflow orchestration
ingestion_batch
source_file
warehouse
dbt lineage
OpenMetadata table/column/SQL lineage
```

---

## 21. Expected governance deployment

Target:

```text
chasse_immobiliere/governance
          |
          v
       GitLab CI
          |
          v
GitLab Container Registry
          |
          v
Real Estate governance image
          |
          v
       lab-gitops
          |
          v
        Argo CD
          |
          v
real-estate-governance-apply Job
          |
          v
    OpenMetadata API
          |
    +-----+------+-------+------+
    |            |       |      |
    v            v       v      v
Glossary       Tags    Owners   DQ
```

The GitOps kustomization should only be extended with a Real Estate governance job after the Real Estate governance image/code is ready.

---

## 22. Wider Fil Rouge documentation context

The project already contains/reference documents such as:

```text
00-project-constitution.md
NOTE-DE-CADRAGE.md
CAHIER-DES-CHARGES-TECHNIQUE.md
MCD-MERISE.md
FICHE-COURS-OLTP-OLAP.md
OLTP.md
OLAP.md
RACI.md
MATRICE-DECISION.md
MODELE-SWOT.md
REGISTRE-RGPD.md
SOUVERAINETE-SECURITE-IA.md
NOTE-ECO-CONCEPTION.md
PCA-PRA-MIGRATION.md
PLAN-DE-TESTS.md
JOURNAL-DE-DECISIONS.md
GLOSSAIRE-METIER.md
GRILLE-EVALUATION.md
TRACABILITE-COMPETENCES.md
TRAME-SOUTENANCE.md
ORGANISATION-DEPOT.md
```

The goal is both a functioning platform and demonstrable coverage of the Diginamic Fil Rouge competency/reference framework.

After governance is complete, compare the real implementation against the project requirements before choosing the next milestone.

---

## 23. What NOT to redo

Unless new evidence shows a regression, do not ask:

```text
Does Kubernetes exist?                    YES
Does PostgreSQL work?                     YES
Does Airflow work?                        YES
Does Airflow receive the DAG through Git? YES
Does dbt exist in the image?              YES
Does dbt connect?                         YES
Does dbt run?                             YES
Do tests pass?                            YES, 19/19
Does Airflow run dbt?                     YES
Does OpenMetadata ingest PostgreSQL?      YES
Does OpenMetadata see analytics views?    YES
Does OpenMetadata ingest dbt?             YES
Does table lineage persist?               YES
Does column lineage persist?              YES
Does SQL lineage persist?                 YES
Does Argo CD own OM resources?            YES
```

Do not redesign those working parts.

---

## 24. Exact continuation point

We stopped immediately before creating the Real Estate governance implementation.

Continue with:

```text
chasse_immobiliere/governance/
```

following the proven Retail structure.

Recommended implementation order:

```text
1. create/verify directory skeleton
2. requirements.txt
3. docs/governance-config.json
4. glossary/real_estate_glossary.json
5. tagging definitions
6. ownership definitions
7. quality definitions
8. scripts/main.py
9. apply-governance.sh
10. Dockerfile
11. README/documentation
12. GitLab CI image build/publish
13. registry validation
14. GitOps Real Estate governance Job
15. Argo CD deployment
16. manual governance apply
17. OpenMetadata API verification
18. update project evidence/documentation
```

Execute ONE step at a time and wait for `YES` or command output.

---

## 25. First response expected from the new chat

Acknowledge briefly that the project state has been recovered and that the next milestone is **Governance-as-Code**.

Then give only the first concrete step for creating/verifying the Real Estate governance structure.

Do not ask me to re-explain the project.

# END OF MONOLITH HANDOVER
