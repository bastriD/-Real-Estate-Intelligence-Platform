# EXECUTION AND DEPLOYMENT ENVIRONMENT — AUTHORITATIVE

This section is critical.

Do not ask where the project will be deployed unless a genuinely new deployment decision becomes necessary.

The target execution environment is already defined.

---

## 1. Development Workstation

Development and administration are performed from:

```text
Windows 11
PowerShell
VS Code
Git
Docker / Docker Compose when useful for local tests
```

Project working directory:

```text
C:\Users\bastr\Desktop\DIGINAMIC\chasse_immobiliere
```

Windows is used for:

```text
source-code editing
Git operations
documentation
SQL authoring
Python development
local unit tests
administrative commands
kubectl
helm
GitLab interaction
```

Windows is NOT the final runtime platform.

Do not design the architecture around Windows-specific deployment.

---

# 2. Target Infrastructure

The final project runs on the existing homelab infrastructure.

Physical/virtual foundation:

```text
Proxmox VE
    |
    v
Virtual Machines
    |
    v
Kubernetes Cluster
```

The existing infrastructure should be reused.

Do not propose replacing the homelab with:

```text
AWS
Azure
GCP
new managed Kubernetes
new physical servers
```

unless explicitly requested.

---

# 3. Kubernetes Platform

The target application/runtime platform is the existing kubeadm Kubernetes cluster.

Architecture:

```text
Proxmox
   |
   +--> Kubernetes Control Plane
   |
   +--> Kubernetes Workers
```

Existing cluster:

```text
k8s-cp-01
k8s-cp-02
k8s-cp-03

k8s-wk-01
k8s-wk-02
k8s-wk-03

additional workers:
k8s-wk-04
k8s-wk-05
k8s-wk-06
```

Kubernetes baseline:

```text
kubeadm
Kubernetes 1.30.x
Flannel CNI
NGINX Ingress
cert-manager
```

Do not redesign the Kubernetes foundation during the database implementation.

---

# 4. Runtime Deployment Principle

The target architecture is:

```text
Development Workstation
        |
        v
       Git
        |
        v
     GitLab
        |
        v
    GitLab CI
        |
        v
Container Registry
        |
        v
GitOps Desired State
        |
        v
      Argo CD
        |
        v
   Kubernetes Cluster
```

Application workloads ultimately run on Kubernetes.

---

# 5. Local Development vs Runtime

Keep these environments clearly separated.

## Development

```text
Windows
+
Python virtual environment
+
Docker / Docker Compose where useful
```

Purpose:

```text
fast development
unit tests
SQL validation
local component tests
```

## Integration / Platform

```text
Kubernetes homelab
```

Purpose:

```text
real deployment
integration tests
Airflow
MLflow
PostgreSQL
MinIO
observability
GitOps
runtime evidence
```

Local Docker is therefore:

```text
DEVELOPMENT / TEST TOOL
```

and not the final architecture.

---

# 6. PostgreSQL Deployment Target

PostgreSQL is the primary relational database for the project.

The database implementation being developed under:

```text
database/
```

must ultimately execute against PostgreSQL in the controlled homelab environment.

Target logical database architecture:

```text
PostgreSQL
│
├── legacy/source schema
├── real_estate
├── raw
├── staging
├── warehouse
└── analytics
```

The initial implementation begins with:

```text
real_estate
```

and the migration from the supplied legacy database.

---

# 7. Database Development Workflow

Database work follows:

```text
SQL authored on Windows
        |
        v
Git repository
        |
        v
Local validation if useful
        |
        v
PostgreSQL integration environment
        |
        v
Migration execution
        |
        v
Tests
        |
        v
Runtime evidence
```

Do not treat a successful local syntax check as final evidence.

Final evidence must come from an actual PostgreSQL execution.

---

# 8. Database Persistence

PostgreSQL must use persistent storage.

Conceptually:

```text
PostgreSQL Pod / Service
        |
        v
PVC
        |
        v
StorageClass
        |
        v
Persistent Infrastructure Storage
```

Never deploy the project database with ephemeral-only storage.

The exact StorageClass/PVC configuration should be inspected from the existing Kubernetes platform before implementation rather than invented.

---

# 9. Deployment Namespace

The project should use a dedicated Kubernetes namespace.

Preferred logical name:

```text
real-estate
```

or another project-specific namespace if one already exists.

Before creating it, inspect the current cluster.

Do not create duplicate namespaces blindly.

---

# 10. GitLab

The existing self-hosted GitLab CE installation is the CI source.

GitLab is already part of the platform.

Use:

```text
.gitlab-ci.yml
```

at the repository root.

Modular CI definitions belong under:

```text
.gitlab/ci/
```

GitLab CI responsibilities:

```text
lint
tests
SQL validation
security checks
Docker build
image publishing
artifact production
```

---

# 11. Argo CD

Argo CD is the Continuous Delivery / GitOps component.

Do not make GitLab CI directly own production Kubernetes state.

Correct model:

```text
GitLab CI
    |
    v
Build / Test / Publish
    |
    v
GitOps configuration
    |
    v
Argo CD
    |
    v
Kubernetes reconciliation
```

---

# 12. Airflow

Apache Airflow already exists on the Kubernetes platform.

Airflow is the target orchestrator for:

```text
data ingestion
ETL / ELT
warehouse loading
Data Quality workflows
ML training workflows
scheduled processing
```

Do not install a second independent Airflow platform for this project unless explicitly required.

Project DAGs belong in:

```text
pipelines/airflow/
```

and are deployed/integrated with the existing Airflow platform.

---

# 13. MLflow

MLflow already exists in the platform.

MLflow is used for:

```text
experiment tracking
training runs
parameters
metrics
artifacts
model registry
model lifecycle
```

Do not create a competing model-registry solution.

Project ML code belongs in:

```text
ml/
```

and communicates with the existing MLflow service.

---

# 14. MinIO

MinIO is the platform object-storage service.

It is the target for appropriate:

```text
ML artifacts
datasets
documents
large objects
```

PostgreSQL stores metadata and relational information.

MinIO stores the binary/object payload where appropriate.

Architecture:

```text
PostgreSQL
     |
     +--> metadata

MinIO
     |
     +--> objects/artifacts
```

---

# 15. OpenMetadata

OpenMetadata already exists in the platform.

It is the target governance/catalog capability for:

```text
metadata
ownership
lineage
profiling
Data Quality
classification
glossary
```

Do not introduce another metadata catalog unless a documented architectural decision justifies it.

---

# 16. Observability Platform

The existing observability stack must be reused:

```text
Prometheus
Grafana
Loki
Tempo
OpenTelemetry
Alertmanager
```

Project workloads should eventually expose:

```text
metrics
logs
traces
health
```

Do not deploy separate standalone observability stacks for this project.

---

# 17. Local AI / Ollama

Ollama runs on the existing dedicated AI/GPU host.

It is outside the Kubernetes cluster but reachable from the controlled internal network.

Architecture:

```text
Kubernetes
    |
    v
AI / Application Service
    |
    v
Internal Network
    |
    v
Dedicated GPU Host
    |
    v
Ollama
    |
    v
Local LLM
```

Do not move Ollama into Kubernetes merely for consistency.

The current dedicated GPU-host architecture is intentional.

---

# 18. Ollama Usage

Ollama is intended for:

```text
semantic enrichment
criteria extraction
document understanding
explanations
future RAG
```

It is NOT the primary engine for basic structured matching.

Matching order remains:

```text
PostgreSQL filtering
        |
        v
Deterministic rules
        |
        v
ML ranking
        |
        v
Optional LLM enrichment
```

---

# 19. ML Training Runtime

ML training can be orchestrated from Kubernetes/Airflow while using the platform services:

```text
Airflow
   |
   v
Training Code
   |
   +--> PostgreSQL
   |
   +--> MLflow
   |
   +--> MinIO
```

The first models are intentionally lightweight:

```text
Logistic Regression
Random Forest
```

Therefore GPU execution is not required for these models.

The GPU host remains primarily relevant to Ollama/LLM workloads.

---

# 20. FastAPI Runtime

The project backend will eventually run as a Kubernetes workload.

Target:

```text
FastAPI
   |
   v
Docker Image
   |
   v
Kubernetes Deployment
   |
   +--> Service
   |
   +--> Ingress
```

NGINX Ingress and cert-manager already exist and should be reused.

---

# 21. Application-to-Database Flow

Target runtime:

```text
User
 |
 v
NGINX Ingress
 |
 v
FastAPI
 |
 v
PostgreSQL
```

Matching:

```text
FastAPI
 |
 v
Matching Service
 |
 +--> PostgreSQL
 |
 +--> ML model
 |
 +--> optional Ollama
```

---

# 22. Data Pipeline Runtime

Target:

```text
StarterPack / External Data
        |
        v
Airflow
        |
        v
RAW
        |
        v
STAGING
        |
        v
real_estate
        |
        v
WAREHOUSE
        |
        v
ANALYTICS
```

---

# 23. Full Target Platform

The complete project target is therefore:

```text
                           USERS
                              |
                              v
                       NGINX INGRESS
                              |
                              v
                           FASTAPI
                         /    |    \
                        /     |     \
                       v      v      v
                 PostgreSQL   ML   Ollama
                     |        |      |
                     |        |      |
                     |      MLflow   |
                     |        |      |
                     |      MinIO    |
                     |               |
                     +-------+-------+
                             |
                             v
                          AIRFLOW
                             |
                             v
                        DATA PIPELINES
                             |
                  +----------+----------+
                  |                     |
                  v                     v
              WAREHOUSE             ANALYTICS


Deployment:
GitLab CI -> GitOps -> Argo CD -> Kubernetes

Governance:
OpenMetadata

Observability:
Prometheus + Grafana + Loki + Tempo + OpenTelemetry
```

---

# 24. Important Deployment Rule

When implementing a component, always distinguish:

```text
WHERE CODE LIVES
```

from:

```text
WHERE IT EXECUTES
```

Example:

```text
pipelines/airflow/my_dag.py

lives in:
Git repository

executes in:
existing Airflow on Kubernetes
```

Likewise:

```text
database/migrations/001_initial_schema.sql

lives in:
Git repository

executes against:
project PostgreSQL
```

---

# 25. Do Not Create Duplicate Platforms

Before proposing installation of:

```text
Airflow
MLflow
MinIO
OpenMetadata
Prometheus
Grafana
Loki
Tempo
Argo CD
NGINX Ingress
cert-manager
Ollama
```

remember that these capabilities already exist.

The project should integrate with them.

---

# 26. Deployment Sequence

The project implementation should progress approximately as:

```text
DATABASE MODEL
      |
      v
POSTGRESQL
      |
      v
MIGRATION
      |
      v
SEED / SYNTHETIC DATA
      |
      v
OLTP VALIDATION
      |
      v
RAW / STAGING
      |
      v
AIRFLOW
      |
      v
WAREHOUSE / DBT
      |
      v
DATA QUALITY
      |
      v
MATCHING BASELINE
      |
      v
ML TRAINING
      |
      v
MLFLOW
      |
      v
FASTAPI
      |
      v
DOCKER
      |
      v
GITLAB CI
      |
      v
KUBERNETES / GITOPS
      |
      v
OBSERVABILITY
```

Do not jump directly to Kubernetes manifests before the application/database component works.

---

# 27. Runtime Evidence

Final project evidence must come from the real target environment wherever practical.

Examples:

```text
PostgreSQL schema output
migration output
database tests
Airflow DAG run
MLflow experiment
Docker image
GitLab pipeline
Argo CD synchronization
Kubernetes pods
Prometheus metrics
Grafana dashboard
OpenMetadata lineage
Ollama request
```

---

# 28. Execution Rule for This Chat

When giving instructions, always state implicitly or explicitly which environment executes them:

```text
WINDOWS / POWERSHELL
```

or:

```text
POSTGRESQL
```

or:

```text
KUBERNETES
```

or:

```text
GITLAB CI
```

or:

```text
AIRFLOW
```

etc.

Never give a command without being clear about its execution context when ambiguity exists.

---

# 29. Immediate Database Phase

We are NOT deploying everything immediately.

Current phase:

```text
Windows development workstation
        |
        v
database/migrations/
        |
        v
PostgreSQL schema implementation
        |
        v
database validation
```

Only after the database is validated do we progressively integrate it into:

```text
Docker
Kubernetes
Airflow
GitOps
```

---

# 30. No Deployment Re-Discovery

Do not begin the conversation by asking:

```text
Where will PostgreSQL run?
Are you using Kubernetes?
Do you have Airflow?
Are you using MLflow?
Where is Ollama?
Which CI/CD do you want?
```

These decisions are already established above.

Only ask a deployment question if implementation reaches a genuinely unresolved detail such as:

```text
exact Kubernetes StorageClass
existing project namespace
PostgreSQL service name
available secret
specific ingress hostname
```

and the answer cannot be discovered from the current platform.