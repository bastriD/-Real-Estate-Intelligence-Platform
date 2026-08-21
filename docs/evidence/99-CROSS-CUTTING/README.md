# Evidence — Cross-Cutting

**Projet :** Real Estate Intelligence Platform  
**Statut :** Documentation baseline complete

---

# Objectif

Ce dossier centralise uniquement les preuves qui couvrent plusieurs blocs de compétences à la fois.

Il ne doit pas dupliquer les documents déjà présents dans :

```text
01-BC01
02-BC02
03-BC03
05-BC05
```

---

# Preuves transverses principales

Les artifacts suivants peuvent démontrer plusieurs compétences simultanément :

```text
Git history
Merge Requests
GitLab CI pipelines
Container images
Argo CD synchronization
Kubernetes runtime state
Airflow DAG executions
MLflow experiments
OpenMetadata lineage
Prometheus metrics
Grafana dashboards
Loki logs
Tempo traces
Backup / restore tests
Security tests
Application screenshots
API responses
Executed test reports
```

---

# Chaîne de traçabilité cible

```text
Requirement
   |
   v
Architecture
   |
   v
Code / Configuration
   |
   v
Git Commit
   |
   v
CI
   |
   v
Artifact
   |
   v
GitOps
   |
   v
Runtime
   |
   v
Test
   |
   v
Evidence
```

---

# Git

Les preuves Git peuvent inclure :

```text
Commit SHA
Author
Timestamp
Changed files
Branch
Merge Request
```

Git permet de démontrer :

```text
versioning
traceability
change history
documentation as code
infrastructure as code
```

---

# CI/CD

Les preuves GitLab CI peuvent inclure :

```text
Pipeline ID
Commit SHA
Job status
Test result
Build result
Artifact
Container tag
```

---

# GitOps

Les preuves Argo CD peuvent inclure :

```text
Application
Revision
Sync status
Health status
Reconciliation
```

---

# Kubernetes

Les preuves runtime peuvent inclure :

```text
kubectl get nodes
kubectl get pods -A
kubectl get deployments -A
kubectl get ingress -A
kubectl get pvc -A
```

---

# Data

Les preuves Data peuvent inclure :

```text
PostgreSQL schema
Migration execution
SQL query results
EXPLAIN ANALYZE
Airflow DAG
dbt results
Data Quality tests
OpenMetadata lineage
```

---

# IA / MLOps

Les preuves peuvent inclure :

```text
MLflow Experiment
Run ID
Parameters
Metrics
Artifact
Model version
Ollama inference
Matching API response
Model Card
```

---

# Observabilité

Les preuves peuvent inclure :

```text
Prometheus metric
Grafana dashboard
Loki log
Tempo trace
Alertmanager alert
```

---

# Sécurité

Les preuves peuvent inclure :

```text
RBAC test
TLS test
Secret scan
Container scan
Authorization test
AI security test
```

---

# PCA / PRA

Les preuves peuvent inclure :

```text
Backup ID
Restore execution
Validation result
Measured RPO
Measured RTO
```

---

# Tests

Les résultats doivent toujours distinguer :

```text
PLANNED
EXECUTED
PASS
FAIL
BLOCKED
```

Une documentation de test sans exécution ne constitue pas une preuve suffisante.

---

# Evidence Naming

Convention recommandée :

```text
<domain>-<test-id>-<description>.<ext>
```

Exemples :

```text
data-DATA-DQ-001-row-count.txt
ai-AI-OLLAMA-001-inference.json
dr-DR-RESTORE-001-output.txt
security-SEC-TLS-001.txt
```

---

# Evidence Integrity

Une preuve doit permettre de comprendre :

```text
What?
Where?
When?
Which version?
Expected result?
Observed result?
Pass or fail?
```

---

# Ne pas inventer de preuve

Aucun artifact ne doit être créé artificiellement pour laisser croire qu'une opération a été exécutée.

Les preuves runtime doivent provenir d'une exécution réelle.

---

# Documentation Freeze

À partir de ce point :

```text
DOCUMENTATION BASELINE = FROZEN
```

La documentation ne sera modifiée que pour refléter :

```text
real implementation
real decisions
real tests
real measurements
real incidents
real evidence
```

---

# Prochaine phase

```text
IMPLEMENTATION
      |
      v
EXECUTION
      |
      v
TESTING
      |
      v
EVIDENCE COLLECTION
      |
      v
FINAL DOCUMENTATION UPDATE
      |
      v
SOUTENANCE
```

---

**CROSS-CUTTING EVIDENCE INDEX — COMPLETE**