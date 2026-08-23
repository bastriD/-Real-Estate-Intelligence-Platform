# CHASSE IMMOBILIÈRE — MONOLITH PROJECT HANDOFF

## Complete technical context, architecture, deployment path, Kubernetes, Airflow, GitLab CI/CD, Data pipeline, validated milestones, constraints, and continuation point

**Project:** `chasse_immobiliere`  
**Status date:** 23 August 2026  
**Purpose of this document:** hand over the project to another ChatGPT conversation / engineer **without requiring the user to re-explain how the platform works, how deployment happens, how Kubernetes is used, how Airflow executes jobs, or what has already been validated**.

---

# 0. ABSOLUTE HANDOFF RULE

This is an **existing, already deployed and partially validated project**.

A new conversation MUST NOT restart the project from zero.

Do NOT ask the user again:

- what infrastructure exists;
- whether Kubernetes exists;
- whether Kubernetes is local on Windows;
- how GitLab deploys;
- whether Airflow exists;
- how Airflow receives DAGs;
- how Airflow reaches Kubernetes;
- whether MinIO exists;
- whether PostgreSQL exists;
- how the Data pipeline works;
- whether RAW / STAGING / OLTP already work;
- whether the full DAG was tested;
- whether CI/CD exists;
- whether the registry is private;
- how secrets are passed.

All of that is documented below.

The current validated milestone is:

```text
SOURCE
→ MINIO
→ RAW
→ RAW QUALITY
→ STAGING
→ STAGING QUALITY
→ OLTP
→ OLTP QUALITY
→ AIRFLOW END-TO-END SUCCESS
```

The next major phase is:

```text
OLAP / DATA WAREHOUSE
```

---

# 1. PROJECT IDENTITY

Project repository:

```text
chasse_immobiliere
```

Project type:

```text
Projet Fil Rouge
Enterprise-style Real Estate Data + AI Platform
```

The project must satisfy:

- business requirements;
- application requirements;
- infrastructure requirements;
- Data Engineering;
- OLTP;
- OLAP;
- analytics;
- AI / matching;
- MLOps;
- security;
- observability;
- governance;
- DevOps;
- testing;
- documentation;
- RNCP competency evidence.

The project must stay aligned with the project documentation and school evaluation framework.

---

# 2. USER WORKING STYLE — IMPORTANT

The user wants strict step-by-step execution.

Rules:

1. Give **one actionable step at a time**.
2. Wait for output or `yes`.
3. Do not send a long sequence of commands unless explicitly requested.
4. When asked for a file, provide the **whole file**.
5. Do not provide partial patches when the full file is requested.
6. Inspect the actual state before changing anything.
7. Preserve working components.
8. Do not redesign working architecture without proof it is needed.
9. Prefer exact commands and exact paths.
10. After each runtime change: test it before continuing.

Troubleshooting sequence:

```text
inspect
→ identify exact error
→ smallest justified fix
→ rebuild/redeploy if needed
→ retest
→ validate
→ document
```

---

# 3. USER WORKSTATION

Primary workstation:

```text
Windows 11
VS Code
PowerShell
```

Main working directory:

```text
C:\Users\bastr\Desktop\DIGINAMIC\chasse_immobiliere
```

Important:

> Kubernetes is NOT run locally on the Windows workstation.

Kubernetes commands are run against the homelab cluster, normally from:

```text
k8s-cp-01
```

---

# 4. HOMELAB — EXISTING PLATFORM

The project runs on an existing self-hosted enterprise-style homelab.

Do not rebuild the platform from scratch.

Existing major components include:

- Proxmox VE
- Kubernetes kubeadm HA
- GitLab CE
- GitLab Runner
- Argo CD
- Airflow
- PostgreSQL
- MinIO
- MLflow
- OpenMetadata
- Prometheus
- Grafana
- Loki
- Promtail
- Tempo
- OpenTelemetry Collector
- NGINX Ingress
- cert-manager
- Velero
- local Ollama
- Qwen3
- GPU-capable nodes

This platform is reused by the Real Estate project.

---

# 5. KUBERNETES CLUSTER

The environment is a kubeadm HA Kubernetes cluster.

Known control planes:

```text
k8s-cp-01
k8s-cp-02
k8s-cp-03
```

Known workers:

```text
k8s-wk-01
k8s-wk-02
k8s-wk-03
k8s-wk-04
k8s-wk-05
k8s-wk-06
```

Common namespaces include:

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

Primary CLI host used during this project:

```text
k8s-cp-01
```

Typical admin elevation:

```bash
sudo -i
```

---

# 6. PROJECT NAMESPACE

The Real Estate project uses:

```text
namespace: real-estate
```

Important workload:

```text
deployment/real-estate-postgresql
```

Typical check:

```bash
kubectl -n real-estate get pods -l app=real-estate-postgresql
```

---

# 7. AIRFLOW NAMESPACE

Airflow runs in:

```text
namespace: airflow
```

Observed Airflow version:

```text
2.10.5
```

Airflow executor:

```text
KubernetesExecutor
```

Data workloads use:

```text
KubernetesPodOperator
```

This is the chosen orchestration design.

---

# 8. ORCHESTRATION DECISION

The Data execution model is:

```text
Airflow
   ↓
KubernetesPodOperator
   ↓
Kubernetes API
   ↓
ephemeral task pod
   ↓
project runtime image
   ↓
Python / psql task
```

Do NOT introduce another Data orchestrator such as:

- Argo Workflows
- Prefect
- Dagster

unless there is a concrete architectural need.

Argo CD remains for GitOps.

Airflow remains for Data orchestration.

---

# 9. GITLAB

GitLab host:

```text
gitlab.local
```

Container registry:

```text
gitlab.local:4567
```

Main project:

```text
root/chasse_immobiliere
```

Airflow DAG publication repository:

```text
root/airflow-dags
```

---

# 10. GITLAB RUNNER

The project uses GitLab Runner for CI/CD.

Observed runner execution mode during this work:

```text
Shell executor
```

The user deploys through GitLab CI/CD.

The user does NOT manually deploy all project code from Windows directly into Kubernetes.

---

# 11. COMPLETE DEPLOYMENT FLOW

This is the most important operational architecture.

```text
Windows 11 / VS Code
        |
        | git add / commit / push
        v
GitLab CE
        |
        | GitLab CI/CD
        |
        +----------------------------+
        |                            |
        v                            v
Build Data runtime image       Publish Airflow DAG
        |                            |
        v                            v
GitLab Container Registry      airflow-dags repository
        |                            |
        |                            v
        |                       Airflow GitSync
        |                            |
        +-------------+--------------+
                      |
                      v
                   Airflow
                      |
                      v
            KubernetesPodOperator
                      |
                      v
               Kubernetes API
                      |
                      v
               ephemeral pod
                      |
          +-----------+-----------+
          |                       |
          v                       v
        MinIO                 PostgreSQL
          |                       |
          v                       v
      source files         RAW → STAGING → OLTP
                                  |
                                  v
                             quality gates
                                  |
                                  v
                               SUCCESS
```

This is how the system works.

Do not ask the user to explain this again.

---

# 12. DAG SOURCE AND DAG PUBLICATION

The source DAG is maintained in the main project:

```text
pipelines/airflow/real_estate_ingestion_dag.py
```

GitLab CI publishes DAGs to:

```text
root/airflow-dags
```

The CI job clones:

```text
https://gitlab.local/root/airflow-dags.git
```

then copies:

```text
pipelines/airflow/*.py
```

to:

```text
dags/
```

then commits and pushes the changes to the Airflow DAG repository.

Airflow GitSync consumes that repository.

---

# 13. AIRFLOW GITSYNC

GitSync repository:

```text
https://gitlab.local/root/airflow-dags.git
```

Airflow sees the Real Estate DAG at:

```text
/opt/airflow/dags/repo/dags/real_estate_ingestion_dag.py
```

Validation command:

```bash
kubectl -n airflow exec deploy/airflow-scheduler -c scheduler -- \
  airflow dags list | grep real_estate_ingestion
```

Expected:

```text
real_estate_ingestion
```

---

# 14. CURRENT AIRFLOW DAG

DAG ID:

```text
real_estate_ingestion
```

Validated dependency tree:

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
end
```

This full chain has already completed successfully.

---

# 15. AIRFLOW TASK POD CONFIGURATION

Relevant Data tasks run as:

```text
KubernetesPodOperator
```

Typical pod settings:

```text
namespace = airflow
image = gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
get_logs = True
is_delete_operator_pod = True
```

Registry auth:

```python
image_pull_secrets=[
    k8s.V1LocalObjectReference(
        name="gitlab-registry"
    )
]
```

Environment is injected from Kubernetes secrets via:

```python
env_from=[...]
```

---

# 16. PRIVATE CONTAINER REGISTRY

The project image is private.

Runtime image:

```text
gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
```

Registry authentication secret:

```text
namespace: airflow
secret: gitlab-registry
```

Previous failure:

```text
ImagePullBackOff
403 Forbidden
failed to fetch anonymous token
```

Cause:

```text
private GitLab registry image without Kubernetes pull credentials
```

Resolved by:

```text
gitlab-registry secret
+
image_pull_secrets
```

---

# 17. SECURITY RULE — SECRETS

Do not hard-code passwords or access tokens in:

- DAGs;
- Python;
- SQL;
- Markdown documentation;
- Git repositories.

Use Kubernetes Secrets.

Important secrets:

```text
airflow/gitlab-registry
airflow/real-estate-postgresql-secret
airflow/real-estate-s3
```

Sensitive values are intentionally omitted from this handoff file.

---

# 18. POSTGRESQL

Database:

```text
real_estate
```

User:

```text
real_estate_user
```

Workload:

```text
namespace: real-estate
deployment: real-estate-postgresql
```

---

# 19. POSTGRESQL SECRET

Secret available in `airflow`:

```text
real-estate-postgresql-secret
```

Confirmed keys:

```text
POSTGRES_DB
POSTGRES_HOST
POSTGRES_PASSWORD
POSTGRES_PORT
POSTGRES_USER
```

Airflow task pods read it with `env_from`.

---

# 20. MINIO

Endpoint:

```text
http://minio.lab.local:9000
```

Known buckets:

```text
airflow
loki
mlflow
real-estate
tempo
velero
```

The Real Estate pipeline uses:

```text
bucket: real-estate
```

---

# 21. MINIO'S ROLE

MinIO is part of the actual ingestion design.

The generator does not write directly into PostgreSQL.

The flow is:

```text
Generate source dataset
        ↓
Persist dataset to MinIO
        ↓
Load later from MinIO
        ↓
RAW PostgreSQL
```

This provides a persistent landing zone and preserves source lineage.

---

# 22. S3 SECRET

Secret:

```text
airflow/real-estate-s3
```

Confirmed keys:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
S3_ENDPOINT_URL
S3_BUCKET
```

Values are intentionally omitted.

---

# 23. DATA RUNTIME IMAGE

Runtime image:

```text
gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
```

Docker base:

```dockerfile
FROM python:3.12-slim
```

The image includes:

- Python runtime
- PostgreSQL client
- project Python dependencies
- source generator
- MinIO upload/download scripts
- RAW loader
- RAW→STAGING transformer
- STAGING→OLTP loader
- SQL quality tests

---

# 24. RUNTIME IMAGE CONTENTS

Important Python scripts:

```text
database/seeds/generer_annonces.py
database/seeds/load_raw_generated_data.py
database/seeds/upload_generated_to_s3.py
database/seeds/download_generated_from_s3.py
database/seeds/transform_raw_to_staging.py
database/seeds/load_staging_to_oltp.py
```

Important Data Quality SQL:

```text
database/tests/004_raw_data_quality.sql
database/tests/005_staging_data_quality.sql
database/tests/006_oltp_data_quality.sql
```

---

# 25. CURRENT DATA LAYERS

Implemented:

```text
SOURCE
   ↓
MinIO
   ↓
RAW
   ↓
STAGING
   ↓
OLTP
```

Next:

```text
OLAP / Data Warehouse
```

Principle:

```text
RAW != STAGING
STAGING != OLTP
OLTP != OLAP
```

Do not merge these layers.

---

# 26. INGESTION BATCH

Airflow derives a batch identifier from the logical run timestamp:

```text
generated-{{ ts_nodash }}
```

Validated example:

```text
generated-20260822T000000
```

This batch is preserved through MinIO, RAW, STAGING and OLTP validation.

---

# 27. GENERATED DATASET

Validated generation:

```text
5 recherches
1000 annonces
```

MinIO upload:

```text
1002 objects
```

Breakdown:

```text
1 recherches.csv
1 annonces.csv
1000 annonce JSON files
```

---

# 28. MINIO OBJECT STRUCTURE

Validated prefix:

```text
s3://real-estate/raw/generated/generated-20260822T000000/
```

Example objects:

```text
recherches.csv
annonces.csv
json/annonce_0001.json
...
json/annonce_1000.json
```

---

# 29. AIRFLOW TASK — generate_source_data

Task ID:

```text
generate_source_data
```

Execution model:

```text
KubernetesPodOperator
```

Runs the generator:

```text
database/seeds/generer_annonces.py
```

Then:

```text
database/seeds/upload_generated_to_s3.py
```

Validated result:

```text
PASS: 1002 files uploaded
Source generation and upload completed.
```

---

# 30. AIRFLOW TASK — load_raw

Task ID:

```text
load_raw
```

Execution model:

```text
KubernetesPodOperator
```

Sequence:

```text
download_generated_from_s3.py
→ load_raw_generated_data.py
```

Validated output:

```text
DOWNLOADED recherches.csv
DOWNLOADED annonces.csv

LOADED: 5 rows into raw.recherches
LOADED: 1000 rows into raw.annonces

PASS: 5 RAW recherches loaded
PASS: 1000 RAW annonces loaded
RAW ingestion completed successfully.
```

---

# 31. RAW LAYER

Tables:

```text
raw.recherches
raw.annonces
```

Purpose:

- preserve source values;
- avoid premature normalization;
- allow reproducibility;
- retain ingestion batch lineage;
- support Data Quality before transformation.

---

# 32. AIRFLOW TASK — validate_raw

Task ID:

```text
validate_raw
```

Execution model:

```text
KubernetesPodOperator
```

SQL file:

```text
database/tests/004_raw_data_quality.sql
```

Checks include:

- batch existence;
- expected recherches count;
- expected annonces count;
- duplicate references;
- mandatory recherche fields;
- mandatory annonce fields;
- recherche_ref consistency;
- price parseability;
- surface parseability;
- quality metrics;
- distribution reports.

Validated result:

```text
PASS
RAW data quality validated successfully
```

---

# 33. IMPORTANT SQL FIX ALREADY APPLIED

A previous SQL error occurred because a `psql` variable was referenced directly inside `DO $$ ... $$`.

Broken pattern:

```sql
v_batch TEXT := :'ingestion_batch';
```

Error:

```text
syntax error at or near ":"
```

Fix:

```sql
SELECT set_config(
    'real_estate.ingestion_batch',
    :'ingestion_batch',
    false
);
```

Then inside PL/pgSQL:

```sql
current_setting('real_estate.ingestion_batch')
```

This is already solved.

---

# 34. AIRFLOW TASK — transform_staging

Task ID:

```text
transform_staging
```

Execution model:

```text
KubernetesPodOperator
```

Script:

```text
database/seeds/transform_raw_to_staging.py
```

Responsibilities include:

- date normalization;
- datetime normalization;
- price normalization;
- surface normalization;
- booleans;
- DPE normalization;
- optional fields;
- preservation of quality errors;
- typed STAGING rows;
- RAW→STAGING reconciliation.

---

# 35. DATE PARSING INCIDENT — SOLVED

Initial transform result:

```text
invalid recherches = 0
invalid annonces = 261
```

Inspection showed:

```text
date_publication | invalid datetime format | 261
```

Observed formats included:

```text
01-25-2025
03-14-2025
04-17-2026
11 avril 2025
12 décembre 2024
14 janvier 2025
1 décembre 2025
26 juillet 2026
29 mai 2025
8 février 2025
```

The parser was extended to support:

- ISO dates;
- `DD/MM/YYYY`;
- `YYYY/MM/DD`;
- `DD-MM-YYYY`;
- `MM-DD-YYYY`;
- `DD.MM.YYYY`;
- French textual month names;
- Unix timestamps;
- milliseconds;
- datetimes.

Final validated result:

```text
QUALITY: invalid recherches = 0
QUALITY: invalid annonces = 0
```

Do not regress this parser.

---

# 36. STAGING LAYER

Tables:

```text
staging.recherches
staging.annonces
```

Purpose:

- typed normalized data;
- quality flags;
- quality error details;
- reconciliation with RAW;
- preparation for OLTP.

---

# 37. AIRFLOW TASK — validate_staging

Task ID:

```text
validate_staging
```

Execution model:

```text
KubernetesPodOperator
```

SQL:

```text
database/tests/005_staging_data_quality.sql
```

Checks include:

- batch exists;
- 5 recherches;
- 1000 annonces;
- zero invalid recherches;
- zero invalid annonces;
- RAW/STAGING reconciliation;
- unique references;
- recherche_ref consistency;
- mandatory typed fields;
- positive price;
- positive surface;
- latitude bounds;
- longitude bounds;
- DPE domain;
- publication date sanity;
- numeric summaries;
- distributions.

Validated result:

```text
PASS
STAGING data quality validated successfully
```

---

# 38. STAGING METRICS

Validated:

```text
total_annonces = 1000

missing_dpe           = 204
missing_nb_pieces     = 0
missing_nb_chambres   = 510
missing_contact_email = 491
missing_latitude      = 537
missing_longitude     = 537

average_price   = 213189.63
average_surface = 213.77

min_price   = 56592.00
max_price   = 458060.00

min_surface = 34.00
max_surface = 400.00
```

Optional missing values are intentionally preserved.

---

# 39. OLTP MODEL

Operational schema:

```text
real_estate
```

Important entities include:

```text
client
chasseur
secteur
mandat
demande
bien
source
presentation
document
commentaire
utilisateur
role
audit-related structures
relationship tables
```

The OLTP model uses:

- PK;
- FK;
- CHECK;
- UNIQUE;
- indexes;
- identity columns;
- business constraints.

---

# 40. REAL_ESTATE.SOURCE

Important columns:

```text
id_source
nom
type_source
url_base
actif
niveau_confiance
date_creation
```

Allowed source types include:

```text
AGENCE
PARTICULIER
PLATEFORME
API
OPEN_DATA
MANUEL
AUTRE
```

Generated source used by this pipeline:

```text
nom               = GENERATEUR_ANNONCES
type_source       = AUTRE
actif             = true
niveau_confiance  = MOYEN
```

---

# 41. REAL_ESTATE.BIEN

Important columns:

```text
id_bien
reference_externe
type_bien
titre
adresse
code_postal
ville
latitude
longitude
prix
surface
nb_pieces
nb_chambres
dpe
description
date_publication
date_collecte
statut
id_source
```

Important uniqueness constraint:

```text
(id_source, reference_externe)
```

This is the business/idempotence key for ingestion.

---

# 42. AIRFLOW TASK — load_oltp

Task ID:

```text
load_oltp
```

Execution model:

```text
KubernetesPodOperator
```

Script:

```text
database/seeds/load_staging_to_oltp.py
```

Responsibilities:

- read validated STAGING rows;
- get/create generated source;
- UPSERT into `real_estate.bien`;
- preserve source relationship;
- avoid duplicates;
- reconcile STAGING→OLTP.

---

# 43. OLTP UPSERT

Pattern:

```text
(id_source, reference_externe)
```

First appearance:

```text
INSERT
```

Existing record:

```text
ON CONFLICT
DO UPDATE
```

Validated result:

```text
Valid staging annonces: 1000
Created source: id_source=4
UPSERTED: 1000 annonces into real_estate.bien
Current biens for source 4: 1000
PASS: 1000 validated staging annonces reconciled with real_estate.bien
PASS: no duplicate (id_source, reference_externe) pairs
STAGING -> OLTP load completed successfully.
```

---

# 44. AIRFLOW TASK — validate_oltp

Task ID:

```text
validate_oltp
```

Execution model:

```text
KubernetesPodOperator
```

SQL:

```text
database/tests/006_oltp_data_quality.sql
```

Validated checks:

```text
PASS: generated source exists exactly once
PASS: generated source is active
PASS: 1000 biens loaded for current batch
PASS: all staging references exist in OLTP
PASS: no duplicate source/reference pairs
PASS: bien -> source foreign keys are valid
PASS: mandatory bien fields are populated
PASS: bien prices are valid
PASS: bien surfaces are valid
PASS: room counts are valid
PASS: DPE values are valid
PASS: latitude values are valid
PASS: longitude values are valid
PASS: bien statuses are valid
```

Final:

```text
PASS
OLTP data quality validated successfully
```

---

# 45. FINAL DATA RECONCILIATION

Validated:

```text
staging_valid_annonces = 1000
oltp_matched_biens     = 1000
```

Duplicate business pairs:

```text
0
```

---

# 46. FINAL DATA DISTRIBUTION

Types:

```text
Appartement       200
Duplex            200
Local commercial  200
Loft              200
Villa             200
```

Cities:

```text
Limoges     400
Annecy      200
Marseille   200
Strasbourg  200
```

---

# 47. FULL AIRFLOW END-TO-END RUN

Reference run:

```text
manual__2026-08-23T07:37:15+00:00
```

State:

```text
success
```

Task states:

```text
start                  success
generate_source_data   success
load_raw               success
validate_raw           success
transform_staging      success
validate_staging       success
load_oltp              success
validate_oltp          success
end                    success
```

Start:

```text
2026-08-23T07:37:16.408384+00:00
```

End:

```text
2026-08-23T07:40:01.427073+00:00
```

Approximate duration:

```text
2 minutes 45 seconds
```

This proves the actual runtime architecture works end-to-end.

---

# 48. AIRFLOW COMMANDS ALREADY VALIDATED

List DAGs:

```bash
kubectl -n airflow exec deploy/airflow-scheduler -c scheduler -- \
  airflow dags list
```

List tasks:

```bash
kubectl -n airflow exec deploy/airflow-scheduler -c scheduler -- \
  airflow tasks list real_estate_ingestion --tree
```

Import errors:

```bash
kubectl -n airflow exec deploy/airflow-scheduler -c scheduler -- \
  airflow dags list-import-errors
```

List runs:

```bash
kubectl -n airflow exec deploy/airflow-scheduler -c scheduler -- \
  airflow dags list-runs \
  -d real_estate_ingestion
```

Important:

```text
--limit 5
```

was not supported by this Airflow CLI for `list-runs`.

---

# 49. TEST A SINGLE AIRFLOW TASK

Pattern:

```bash
kubectl -n airflow exec deploy/airflow-scheduler -c scheduler -- \
  airflow tasks test \
  real_estate_ingestion \
  <TASK_ID> \
  2026-08-22
```

Validated task IDs:

```text
generate_source_data
load_raw
validate_raw
transform_staging
validate_staging
load_oltp
validate_oltp
```

---

# 50. CHECK STATES FOR ONE RUN

Pattern:

```bash
kubectl -n airflow exec deploy/airflow-scheduler -c scheduler -- \
  airflow tasks states-for-dag-run \
  real_estate_ingestion \
  <RUN_ID>
```

Example:

```text
manual__2026-08-23T07:37:15+00:00
```

---

# 51. CI/CD IMAGE BUILD

GitLab CI builds:

```text
gitlab.local:4567/root/chasse_immobiliere/data-pipeline:<commit-tag>
```

and:

```text
gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
```

The image is pushed to the GitLab Registry.

Do not manually assume `latest` contains a file; if needed, verify it inside Kubernetes.

---

# 52. VALIDATING IMAGE CONTENT INSIDE KUBERNETES

A prior issue occurred because `load_staging_to_oltp.py` had not been saved before build.

It was diagnosed by running a direct pod against the actual image.

Pattern:

```bash
kubectl -n airflow run real-estate-image-check \
  --rm -it \
  --restart=Never \
  --image=gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest \
  --overrides='
{
  "spec": {
    "imagePullSecrets": [
      {
        "name": "gitlab-registry"
      }
    ]
  }
}' \
  --command -- \
  /bin/sh -c 'ls -lah /app/database/seeds'
```

Validated:

```text
load_staging_to_oltp.py exists
python -m py_compile succeeds
```

---

# 53. INCIDENTS ALREADY SOLVED

## 53.1 GitLab registry 403 / ImagePullBackOff

Cause:

```text
private image pull without auth
```

Fixed with:

```text
gitlab-registry
image_pull_secrets
```

## 53.2 Duplicate Airflow task ID

Error:

```text
DuplicateTaskIdFound
```

Resolved.

## 53.3 Undefined Airflow task variable

Error:

```text
validate_raw_task is not defined
```

Resolved.

## 53.4 psql variable inside PL/pgSQL block

Error:

```text
syntax error at or near ":"
```

Resolved with session setting + `current_setting()`.

## 53.5 Missing OLTP loader in image

Error:

```text
No such file or directory
```

Resolved by saving file, rebuilding image, verifying inside Kubernetes.

## 53.6 Date parser

Problem:

```text
261 invalid annonces
```

Resolved.

Final:

```text
0 invalid annonces
```

---

# 54. GITOPS POSITION

Argo CD already exists in the platform.

The project uses Git-based deployment practices.

The current Data pipeline path specifically relies on:

```text
GitLab CI/CD
→ image build
→ DAG publication
→ Airflow execution
```

Do not confuse this with "kubectl from Windows".

---

# 55. OPENMETADATA

OpenMetadata already exists in:

```text
namespace: openmetadata
```

It should eventually ingest Real Estate metadata / lineage.

Possible future integration:

```text
real_estate PostgreSQL
dbt models
warehouse models
lineage
ownership
descriptions
quality metadata
```

Do not reinstall OpenMetadata.

---

# 56. MLFLOW

MLflow already exists in:

```text
namespace: mlflow
```

It is part of the homelab MLOps platform.

The Real Estate AI/ML phase can reuse it later.

Do not reinstall MLflow.

---

# 57. OLLAMA / LOCAL AI

The platform already has local Ollama/Qwen3 capability on GPU hardware.

This is intended for later AI work.

It is **not the immediate next task**.

---

# 58. PROJECT DOCUMENTATION

Existing project files include:

```text
00-project-constitution.md
prompt.md
architecture-playbook.md
README.md

NOTE-DE-CADRAGE.md
CAHIER-DES-CHARGES-TECHNIQUE.md
MCD-MERISE.md
OLTP.md
OLAP.md
FICHE-COURS-OLTP-OLAP.md

PLAN-DE-TESTS.md
MATRICE-DECISION.md
JOURNAL-DE-DECISIONS.md
RACI.md

REGISTRE-RGPD.md
SOUVERAINETE-SECURITE-IA.md
NOTE-ECO-CONCEPTION.md

TRACABILITE-COMPETENCES.md
GRILLE-EVALUATION.md
TRAME-SOUTENANCE.md
GLOSSAIRE-METIER.md
MODELE-SWOT.md

PCA-PRA-MIGRATION.md
ORGANISATION-DEPOT.md
```

Recent milestone docs:

```text
REAL-ESTATE-INGESTION-PIPELINE.md
PROJECT-ALIGNMENT-REVIEW-2026-08-23.md
PROJECT-HANDOFF-OLAP-MIGRATION-PROMPT.md
```

This monolith should become the primary handoff file.

---

# 59. PROJECT ALIGNMENT STATUS

Validated current status:

```text
PROJECT ALIGNMENT               CONFIRMED
INGESTION PIPELINE              VALIDATED
RAW                             VALIDATED
STAGING                         VALIDATED
OLTP                            VALIDATED
DATA QUALITY                    VALIDATED
CI/CD                           VALIDATED
KUBERNETES EXECUTION            VALIDATED
AIRFLOW END-TO-END              VALIDATED
```

Still incomplete:

```text
OLAP / WAREHOUSE                NOT BUILT YET
ANALYTICS                       NOT BUILT YET
3V                              TO FORMALIZE
RGPD OPERATIONALIZATION         PARTIAL
MATCHING / ML                   NOT BUILT YET
AI ARCHITECTURE                 FUTURE
OBSERVABILITY FOR THIS PIPELINE PARTIAL
SECURITY TESTING                NOT DONE
PERFORMANCE TESTING             NOT DONE
```

---

# 60. BC05 POSITION

Current conceptual status:

```text
BC05
│
├── 3V
│      └── TO COMPLETE
│
├── ETL + Data Quality
│      └── STRONGLY IMPLEMENTED
│
├── RGPD
│      └── PARTIAL
│
├── Database
│      ├── OLTP       DONE
│      └── OLAP       NEXT
│
├── Matching / ML
│      └── FUTURE
│
└── AI architecture
       └── FUTURE
```

Do not declare whole BC05 complete.

---

# 61. NEXT MAJOR PHASE

Next phase:

# OLAP / DATA WAREHOUSE

Current architecture:

```text
SOURCE
   ↓
MinIO
   ↓
RAW
   ↓
STAGING
   ↓
OLTP
   ↓
QUALITY
```

Target extension:

```text
OLTP / STAGING
      ↓
Warehouse transformation
      ↓
OLAP / Data Warehouse
      ↓
Dimensions
      +
Facts
      ↓
Marts
      ↓
Analytics / KPI
```

---

# 62. BEFORE OLAP IMPLEMENTATION

Read and compare:

```text
OLAP.md
OLTP.md
MCD-MERISE.md
CAHIER-DES-CHARGES-TECHNIQUE.md
GRILLE-EVALUATION.md
TRACABILITE-COMPETENCES.md
REAL-ESTATE-INGESTION-PIPELINE.md
PROJECT-ALIGNMENT-REVIEW-2026-08-23.md
```

Do not immediately create SQL.

First determine:

1. explicit analytical requirements;
2. business KPIs;
3. source OLTP tables;
4. usable data currently present;
5. fact grain;
6. dimensions;
7. measures;
8. refresh strategy;
9. dbt role;
10. Data Quality for OLAP.

---

# 63. OLAP DIRECTION FROM EXISTING PROJECT

Existing project direction includes analytical questions such as:

- performance by chasseur;
- performance by quarter;
- delay between mandate and purchase;
- analysis by sector;
- client budget behavior;
- property performance;
- later matching performance.

Potential dimensions may include:

```text
dim_date
dim_chasseur
dim_client
dim_bien
dim_secteur
dim_source
```

Potential facts may include:

```text
fact_performance
fact_vente
fact_matching
```

These are NOT to be created blindly.

They must be justified by the actual project documents and available OLTP data.

---

# 64. DBT

dbt is a candidate for the warehouse transformation layer.

Possible flow:

```text
OLTP / STAGING
   ↓
dbt
   ↓
dimensions
   ↓
facts
   ↓
marts
```

The homelab already has dbt experience.

Do not introduce extra tools unless justified.

---

# 65. FUTURE AI DIRECTION

Future target may include:

```text
OLAP / OLTP
    ↓
feature engineering
    ↓
matching
    ↓
ML
    ↓
MLflow
    ↓
vector / semantic layer
    ↓
Qdrant
    ↓
Ollama / Qwen3
```

But AI is not the immediate next task.

---

# 66. FUTURE GOVERNANCE

After OLAP is built, integrate metadata and lineage into existing OpenMetadata.

Expected evidence:

```text
PostgreSQL schemas
dbt models
lineage
ownership
descriptions
quality
```

---

# 67. OBSERVABILITY

Existing platform already has:

- Prometheus
- Grafana
- Loki
- Tempo
- OpenTelemetry

The Real Estate pipeline currently has Airflow/pod logs.

Dedicated pipeline metrics/alerts still need to be developed.

Do not reinstall monitoring stack.

---

# 68. RGPD

The project already contains:

```text
REGISTRE-RGPD.md
```

Operational RGPD integration into the Real Estate pipeline still needs to be completed.

Future work should cover:

- personal data classification;
- minimization;
- retention;
- lifecycle;
- deletion/anonymization rules if applicable;
- traceability;
- governance.

---

# 69. SECURITY

The project already has:

```text
SOUVERAINETE-SECURITE-IA.md
```

Secrets are already externalized into Kubernetes Secrets for this pipeline.

Still to strengthen later:

- secret lifecycle;
- least privilege;
- registry auth hardening;
- network policies;
- security tests;
- image scanning if required;
- RBAC review.

---

# 70. TESTING STATUS

Already validated:

```text
integration tests
data quality tests
runtime pod tests
end-to-end Airflow DAG
reconciliation
```

Still to add later:

```text
more unit tests
performance tests
security tests
failure/retry tests
rollback/recovery tests
```

---

# 71. DEFINITION OF DONE

A feature is not "done" just because code exists.

Where relevant:

```text
code
+
tests
+
successful execution
+
data validation
+
deployment validation
+
documentation
+
RNCP evidence
```

---

# 72. DO NOT DO THESE THINGS

Do NOT:

- restart the project;
- ask the user to re-explain infrastructure;
- ask how Kubernetes is accessed;
- ask how Airflow executes jobs;
- ask how DAGs are published;
- ask how images reach Kubernetes;
- propose local Docker Compose as final deployment;
- replace Kubernetes;
- replace Airflow;
- reinstall MinIO;
- reinstall OpenMetadata;
- reinstall MLflow;
- recreate RAW/STAGING/OLTP;
- remove quality gates;
- hard-code secrets;
- jump to AI before OLAP;
- claim BC05 complete;
- give giant multi-step execution plans without waiting;
- invent file contents instead of inspecting them.

---

# 73. NEW CHAT STARTUP INSTRUCTIONS

When this file is used in a new chat:

1. Read this monolith first.
2. Acknowledge that the existing pipeline is already validated.
3. Do not ask the user to re-explain deployment.
4. Read the project OLAP documents.
5. Compare requirements with actual existing OLTP data.
6. Propose the target warehouse model.
7. Give only **STEP 1**.
8. Stop and wait for output.

---

# 74. CURRENT CONTINUATION POINT

The project has completed:

```text
SOURCE
→ MINIO
→ RAW
→ RAW QUALITY
→ STAGING
→ STAGING QUALITY
→ OLTP
→ OLTP QUALITY
→ AIRFLOW FULL DAG SUCCESS
```

Continue from:

```text
OLAP / DATA WAREHOUSE
```

---

# 75. ONE-SCREEN TECHNICAL SUMMARY

```text
WINDOWS 11 / VS CODE / POWERSHELL
              |
              | git push
              v
           GITLAB CE
              |
              | CI/CD
              |
      +-------+--------+
      |                |
      v                v
BUILD IMAGE        PUBLISH DAG
      |                |
      v                v
GITLAB REGISTRY   AIRFLOW-DAGS
      |                |
      |                v
      |           AIRFLOW GITSYNC
      |                |
      +-------+--------+
              |
              v
            AIRFLOW
              |
              v
   KubernetesPodOperator
              |
              v
          KUBERNETES
              |
       +------+------+
       |             |
       v             v
     MINIO       POSTGRESQL
       |             |
       v             v
    SOURCE   RAW → STAGING → OLTP
                         |
                         v
                  QUALITY GATES
                         |
                         v
                      SUCCESS
                         |
                         v
                    NEXT: OLAP
```

---

# 76. FINAL HANDOFF STATEMENT

This project already has a functioning deployment chain:

```text
Windows development
→ Git push
→ GitLab CI/CD
→ GitLab Registry
→ Airflow DAG publication
→ Airflow GitSync
→ Airflow scheduler
→ KubernetesPodOperator
→ Kubernetes task pod
→ MinIO / PostgreSQL
→ RAW / STAGING / OLTP
→ Data Quality
→ SUCCESS
```

The Real Estate ingestion pipeline is **not conceptual**.

It has been:

```text
implemented
built
pushed
deployed
executed
debugged
validated
documented
```

The next conversation must continue from this state and move into:

```text
OLAP / DATA WAREHOUSE
```

without making the user explain the deployment architecture again.
