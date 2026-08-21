# BC03 — C6 — Tests exécutés

**Bloc de compétences :** BC03  
**Compétence :** C6 — Définir, exécuter et documenter des scénarios de tests  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Baseline documentaire — preuves d'exécution à consolider

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves démontrant que les tests du projet sont réellement exécutés.

Le cycle attendu est :

```text
Requirement
    |
    v
Test Scenario
    |
    v
Execution
    |
    v
Observed Result
    |
    v
Pass / Fail
    |
    v
Evidence
```

Un test seulement écrit n'est pas suffisant.

Le projet doit distinguer :

```text
PLANNED
EXECUTED
PASSED
FAILED
BLOCKED
```

---

# 2. Source principale

Le document Fil Rouge associé est :

```text
PLAN-DE-TESTS.md
```

Ce document définit les scénarios de test.

Le présent dossier doit progressivement contenir les **preuves d'exécution** correspondantes.

---

# 3. Types de tests

Les principales catégories sont :

```text
Unit Tests
Integration Tests
API Tests
Database Tests
Data Quality Tests
Security Tests
Infrastructure Tests
Kubernetes Tests
GitOps Tests
MLOps Tests
AI Tests
Backup / Restore Tests
Accessibility Tests
Smoke Tests
Regression Tests
```

---

# 4. Format d'un test

Chaque test doit contenir au minimum :

```text
Test ID
Requirement
Objective
Preconditions
Input
Execution Steps
Expected Result
Actual Result
Status
Evidence
```

---

# 5. Exemple de fiche

```text
Test ID: API-001

Objective:
Verify application health endpoint.

Preconditions:
Application deployed.

Action:
GET /health

Expected:
HTTP 200
status = ok

Actual:
To be recorded

Status:
NOT EXECUTED / PASS / FAIL

Evidence:
curl output / screenshot / CI result
```

---

# 6. Statuts

Les statuts autorisés sont :

```text
NOT EXECUTED
PASS
FAIL
BLOCKED
NOT APPLICABLE
```

Le statut doit refléter l'exécution réelle.

---

# 7. Test — Kubernetes nodes

## ID

```text
INFRA-K8S-001
```

## Objectif

Vérifier que les nœuds Kubernetes attendus sont disponibles.

## Commande

```bash
kubectl get nodes -o wide
```

## Résultat attendu

Les nœuds attendus doivent être :

```text
Ready
```

## Evidence

```text
kubectl-get-nodes.txt
```

---

# 8. Test — Kubernetes workloads

## ID

```text
INFRA-K8S-002
```

## Commande

```bash
kubectl get pods -A
```

## Résultat attendu

Les workloads critiques doivent être :

```text
Running
Completed
```

selon leur nature.

Les états :

```text
CrashLoopBackOff
ImagePullBackOff
Error
```

doivent être analysés.

---

# 9. Test — Kubernetes resources

## ID

```text
INFRA-K8S-003
```

## Commande

```bash
kubectl top nodes
```

et :

```bash
kubectl top pods -A
```

## Objectif

Vérifier la consommation réelle des ressources.

---

# 10. Test — DNS Kubernetes

## ID

```text
INFRA-NET-001
```

## Objectif

Vérifier la résolution DNS interne.

Exemple :

```bash
nslookup kubernetes.default.svc.cluster.local
```

depuis un pod adapté.

---

# 11. Test — Node connectivity

## ID

```text
INFRA-NET-002
```

## Objectif

Vérifier que les nœuds peuvent communiquer selon l'architecture prévue.

Preuve possible :

```text
ping
ip route
traceroute
```

selon le test.

---

# 12. Test — Ingress

## ID

```text
INFRA-ING-001
```

## Objectif

Vérifier qu'un service est accessible via Ingress.

Exemple :

```bash
curl -I https://service.lab.local
```

---

# 13. Test — TLS

## ID

```text
SEC-TLS-001
```

## Objectif

Vérifier l'utilisation HTTPS.

Exemple :

```bash
curl -vk https://service.lab.local
```

## Résultat attendu

Connexion TLS établie et endpoint accessible.

---

# 14. Test — Argo CD synchronization

## ID

```text
DEVOPS-GITOPS-001
```

## Objectif

Vérifier l'état des applications Argo CD.

Commande possible :

```bash
argocd app list
```

Résultat attendu :

```text
Synced
Healthy
```

pour les applications attendues.

---

# 15. Test — GitOps reconciliation

## ID

```text
DEVOPS-GITOPS-002
```

## Objectif

Démontrer un cycle réel :

```text
Git Change
   |
   v
Argo CD
   |
   v
Kubernetes Change
```

## Evidence

- commit ;
- Argo CD sync ;
- runtime state.

---

# 16. Test — CI pipeline

## ID

```text
DEVOPS-CI-001
```

## Objectif

Vérifier qu'une pipeline CI s'exécute correctement.

La preuve doit inclure :

```text
Pipeline ID
Commit SHA
Jobs
Status
```

---

# 17. Test — PostgreSQL

## ID

```text
DATA-DB-001
```

## Objectif

Vérifier la disponibilité PostgreSQL.

Exemple :

```sql
SELECT version();
```

---

# 18. Test — Data model

## ID

```text
DATA-MODEL-001
```

## Objectif

Vérifier que les tables attendues existent.

Exemple PostgreSQL :

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;
```

---

# 19. Test — Row counts

## ID

```text
DATA-DQ-001
```

## Objectif

Vérifier les volumes attendus.

Exemple :

```sql
SELECT COUNT(*) FROM raw.orders;
```

Les valeurs réellement attendues doivent être basées sur le dataset réel.

---

# 20. Test — Not Null

## ID

```text
DATA-DQ-002
```

Exemple :

```sql
SELECT COUNT(*)
FROM warehouse.fact_sales
WHERE order_id IS NULL;
```

Résultat attendu :

```text
0
```

si la règle métier l'exige.

---

# 21. Test — Uniqueness

## ID

```text
DATA-DQ-003
```

Exemple :

```sql
SELECT order_id, COUNT(*)
FROM warehouse.fact_sales
GROUP BY order_id
HAVING COUNT(*) > 1;
```

Résultat attendu :

```text
0 rows
```

si `order_id` doit être unique.

---

# 22. Test — Referential Integrity

## ID

```text
DATA-DQ-004
```

Exemple :

```sql
SELECT f.customer_id
FROM warehouse.fact_sales f
LEFT JOIN warehouse.dim_customer c
  ON f.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

Résultat attendu :

```text
0 rows
```

si la relation est obligatoire.

---

# 23. Test — dbt

## ID

```text
DATA-DBT-001
```

Commande :

```bash
dbt test
```

ou :

```bash
dbt build
```

selon le workflow.

Evidence :

```text
dbt-test-output.txt
```

---

# 24. Test — Airflow

## ID

```text
DATA-AIRFLOW-001
```

## Objectif

Vérifier qu'un DAG s'exécute jusqu'au succès.

Evidence possible :

- DAG run ;
- task status ;
- logs ;
- screenshots.

---

# 25. Test — OpenMetadata ingestion

## ID

```text
DATA-META-001
```

## Objectif

Vérifier qu'une ingestion metadata se termine correctement.

Exemples de sources :

```text
PostgreSQL
Airflow
dbt
```

---

# 26. Test — OpenMetadata lineage

## ID

```text
DATA-META-002
```

## Objectif

Vérifier qu'un asset possède un lineage visible.

Evidence :

```text
screenshot
API result
```

---

# 27. Test — OpenMetadata ownership

## ID

```text
DATA-META-003
```

## Objectif

Vérifier qu'un asset critique possède un propriétaire.

---

# 28. Test — MLflow experiment

## ID

```text
ML-MLFLOW-001
```

## Objectif

Vérifier qu'un experiment possède :

```text
run
parameters
metrics
artifacts
```

---

# 29. Test — MLflow model registry

## ID

```text
ML-MLFLOW-002
```

## Objectif

Vérifier qu'un modèle possède une version dans le registry.

Evidence possible :

- model name ;
- version ;
- run ID ;
- artifact URI.

---

# 30. Test — Model promotion

## ID

```text
ML-MLFLOW-003
```

## Objectif

Démontrer le passage d'un modèle candidat vers une version sélectionnée.

La preuve doit refléter le lifecycle réellement utilisé.

---

# 31. Test — Ollama connectivity

## ID

```text
AI-OLLAMA-001
```

Exemple :

```bash
curl http://AI_HOST:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:8b",
    "prompt": "Reply only with: Ollama remote inference works",
    "stream": false
  }'
```

Résultat attendu :

```text
Ollama remote inference works
```

Le projet dispose déjà d'une exécution réelle de ce type.

---

# 32. Test — AI latency

## ID

```text
AI-OLLAMA-002
```

Mesures possibles :

```text
request start
request end
duration
```

---

# 33. Test — GPU

## ID

```text
AI-GPU-001
```

Commande possible :

```bash
nvidia-smi
```

Objectif :

Vérifier :

```text
GPU
VRAM
utilization
temperature
```

pendant un workload AI.

---

# 34. Test — AI unavailable

## ID

```text
AI-RES-001
```

## Objectif

Si l'application implémente graceful degradation :

```text
AI Service Down
      |
      v
Core Feature Still Available
```

Le test doit le démontrer.

---

# 35. Test — RAG retrieval

## ID

```text
AI-RAG-001
```

## Objectif

Vérifier qu'une question connue retourne un document attendu parmi les résultats.

Ce test ne peut être exécuté que lorsque RAG existe réellement.

---

# 36. Test — RAG authorization

## ID

```text
AI-RAG-SEC-001
```

## Objectif

Vérifier qu'un utilisateur ne récupère pas un document non autorisé.

---

# 37. Test — API health

## ID

```text
APP-API-001
```

Commande :

```bash
curl -i http://application/health
```

Résultat attendu :

```text
HTTP 200
```

---

# 38. Test — API validation

## ID

```text
APP-API-002
```

## Objectif

Envoyer une entrée invalide.

Résultat attendu :

```text
400 / 422
```

selon l'API.

---

# 39. Test — API valid request

## ID

```text
APP-API-003
```

## Objectif

Vérifier un endpoint métier avec entrée valide.

La réponse doit correspondre aux critères d'acceptation.

---

# 40. Test — Authentication

## ID

```text
SEC-AUTH-001
```

À exécuter uniquement lorsqu'un endpoint authentifié existe réellement.

```text
No credentials
      |
      v
401
```

---

# 41. Test — Authorization

## ID

```text
SEC-AUTHZ-001
```

```text
Authenticated
but unauthorized
      |
      v
403
```

---

# 42. Test — SQL injection

## ID

```text
SEC-INJECT-001
```

Une valeur de test peut inclure :

```text
' OR 1=1 --
```

L'application doit traiter l'entrée de manière sûre.

---

# 43. Test — Secret scan

## ID

```text
SEC-SECRET-001
```

Objectif :

Vérifier l'absence de secrets connus dans Git.

La preuve peut venir :

- d'un scanner ;
- d'une commande ;
- de la CI.

---

# 44. Test — Container security

## ID

```text
SEC-CONTAINER-001
```

Vérifications possibles :

```text
user
image
packages
securityContext
```

---

# 45. Test — Observability metrics

## ID

```text
OBS-METRICS-001
```

Objectif :

Vérifier qu'une métrique attendue est disponible dans Prometheus.

---

# 46. Test — Logs

## ID

```text
OBS-LOGS-001
```

Objectif :

Générer une requête connue et retrouver son log dans Loki.

---

# 47. Test — Traces

## ID

```text
OBS-TRACE-001
```

Objectif :

Générer une requête instrumentée et retrouver la trace dans Tempo.

---

# 48. Test — Alert

## ID

```text
OBS-ALERT-001
```

Objectif :

Déclencher de manière contrôlée une condition d'alerte.

Vérifier :

```text
Prometheus
   |
   v
Alertmanager
   |
   v
Alert State
```

---

# 49. Test — Backup

## ID

```text
DR-BACKUP-001
```

Objectif :

Créer un backup contrôlé.

Evidence :

```text
backup ID
timestamp
status
```

---

# 50. Test — Restore

## ID

```text
DR-RESTORE-001
```

Processus :

```text
Known Object
   |
   v
Backup
   |
   v
Delete / Modify
   |
   v
Restore
   |
   v
Validate
```

---

# 51. Test — Restore validation

## ID

```text
DR-RESTORE-002
```

Vérifier :

- ressource ;
- contenu ;
- état ;
- fonction.

---

# 52. Test — RTO

## ID

```text
DR-RTO-001
```

Mesurer :

```text
Failure / Start
      |
      v
Recovery
      |
      v
Validated Service
```

La durée réellement observée constitue l'evidence.

---

# 53. Test — Accessibility keyboard

## ID

```text
ACC-001
```

Objectif :

Vérifier que les fonctions essentielles sont accessibles au clavier.

À exécuter uniquement lorsqu'une UI existe.

---

# 54. Test — Form labels

## ID

```text
ACC-002
```

Objectif :

Vérifier que les champs possèdent des labels compréhensibles.

---

# 55. Test — Responsive

## ID

```text
ACC-003
```

Objectif :

Vérifier l'affichage sur les tailles d'écran prévues.

---

# 56. Test — Eco resource baseline

## ID

```text
ECO-001
```

Commandes possibles :

```bash
kubectl top nodes
kubectl top pods -A
```

Objectif :

Créer une baseline avant optimisation.

---

# 57. Test — SQL optimization

## ID

```text
ECO-SQL-001
```

Processus :

```text
Query
 |
 v
EXPLAIN ANALYZE
 |
 v
Optimization
 |
 v
EXPLAIN ANALYZE
 |
 v
Compare
```

---

# 58. Test — Container image size

## ID

```text
ECO-IMG-001
```

Comparer les tailles avant/après optimisation si une amélioration réelle est effectuée.

---

# 59. Test — Documentation links

## ID

```text
DOC-001
```

Objectif :

Vérifier les liens internes Markdown.

Le projet a déjà exécuté un contrôle de ce type.

---

# 60. Test — Empty documents

## ID

```text
DOC-002
```

Objectif :

Vérifier qu'aucun document requis n'est vide.

Le projet a déjà exécuté ce contrôle et identifié puis corrigé :

```text
ADR-0008-OpenMetadata.md
```

---

# 61. Test — ADR references

## ID

```text
DOC-003
```

Objectif :

Vérifier que les références ADR correspondent au catalogue réel.

Le projet a déjà exécuté ce contrôle.

---

# 62. Preuve d'exécution

Chaque test réellement exécuté doit produire une preuve.

Formats possibles :

```text
.txt
.log
.json
.xml
.html
.png
.md
```

selon le test.

---

# 63. Convention de nommage

Exemple :

```text
APP-API-001-health.txt
DATA-DQ-002-not-null.txt
AI-OLLAMA-001-inference.json
DR-RESTORE-001-output.txt
```

---

# 64. Répertoire proposé

Ce dossier peut progressivement évoluer vers :

```text
C6-Tests-Executes/
│
├── README.md
├── infrastructure/
├── application/
├── data/
├── ai/
├── security/
├── observability/
├── dr/
├── accessibility/
└── eco/
```

Ne créer les sous-dossiers que lorsqu'ils contiennent de vraies preuves.

---

# 65. Test report

Pour chaque campagne importante, un rapport peut contenir :

```text
Date
Environment
Version
Tester
Tests Executed
Passed
Failed
Blocked
Conclusion
```

---

# 66. Exemple de tableau d'exécution

| Test ID | Date | Result | Evidence |
|---|---|---|---|
| INFRA-K8S-001 | TBD | NOT EXECUTED | - |
| DEVOPS-GITOPS-001 | TBD | NOT EXECUTED | - |
| DATA-DQ-001 | TBD | NOT EXECUTED | - |
| ML-MLFLOW-001 | TBD | NOT EXECUTED | - |
| AI-OLLAMA-001 | Already observed | PASS | To centralize |
| APP-API-001 | TBD | NOT EXECUTED | - |
| DR-RESTORE-001 | TBD | NOT EXECUTED | - |

Le tableau final doit être mis à jour avec les dates et preuves réelles.

---

# 67. Critères PASS / FAIL

Le résultat doit être basé sur le critère attendu.

Exemple :

```text
Expected:
All nodes Ready

Observed:
5 Ready
1 NotReady
```

Résultat :

```text
FAIL
```

même si la majorité du cluster fonctionne.

---

# 68. Gestion des échecs

Un test échoué suit :

```text
FAIL
 |
 v
Issue
 |
 v
Diagnosis
 |
 v
Correction
 |
 v
Retest
```

L'échec initial peut être conservé comme preuve du processus d'amélioration.

---

# 69. Regression Testing

Après correction :

```text
Fix
 |
 v
Original Test
 |
 v
Related Tests
```

doivent être réexécutés lorsque nécessaire.

---

# 70. Tests automatisés

Les tests automatisables doivent progressivement être exécutés dans CI.

Exemples :

```text
pytest
dbt test
lint
security scan
policy validation
```

---

# 71. Tests manuels

Certains tests restent pertinents manuellement :

```text
UI accessibility
visual inspection
DR exercise
business acceptance
```

Ils doivent néanmoins être documentés.

---

# 72. Test Environment

Chaque preuve doit préciser l'environnement.

Exemples :

```text
local
development
kubernetes lab
staging-like
```

---

# 73. Version

Associer si possible :

```text
Git commit
Container tag
Model version
Migration version
```

au test.

Cela améliore la reproductibilité.

---

# 74. Test Data

Les jeux de données utilisés doivent être :

- connus ;
- reproductibles ;
- adaptés ;
- non sensibles lorsque possible.

---

# 75. Security of Test Data

Les données personnelles ne doivent pas être copiées arbitrairement dans les environnements de test.

Lorsque possible :

```text
Synthetic
Anonymized
Pseudonymized
```

data doit être privilégiée.

---

# 76. Evidence Integrity

Les preuves doivent être suffisamment détaillées pour permettre au jury de comprendre :

```text
What was executed?
On what?
What happened?
Was it successful?
```

---

# 77. Ce qui ne constitue pas une preuve

Ce n'est pas suffisant :

```text
"Tested manually"
```

sans :

- commande ;
- résultat ;
- capture ;
- date ;
- contexte.

---

# 78. Priorité des tests

## P0

```text
Application core flow
Data integrity
Kubernetes readiness
GitOps
Restore
```

## P1

```text
Security
MLOps
AI
Observability
```

## P2

```text
Accessibility
Performance
Eco optimization
Advanced resilience
```

---

# 79. Tests minimum soutenance

La soutenance devrait idéalement pouvoir montrer :

```text
1 Kubernetes proof
1 GitOps proof
1 Data pipeline proof
1 Data Quality proof
1 MLflow proof
1 AI inference proof
1 Application proof
1 Security proof
1 Observability proof
1 Restore proof
```

---

# 80. Matrice compétence → test

| Compétence | Exemple de test |
|---|---|
| Application | API test |
| Data | SQL / DQ |
| MLOps | MLflow lifecycle |
| AI | Ollama inference |
| Security | RBAC / TLS |
| Observability | metric/log/trace |
| DR | restore |
| Eco | resource comparison |
| Accessibility | keyboard test |

---

# 81. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Scenario
  |
  v
Execution
  |
  v
Observed Result
  |
  v
Status
  |
  v
Evidence
```

et constater que les tests n'ont pas seulement été écrits mais exécutés.

---

# 82. État actuel

```text
Test strategy                 COMPLETE
Test categories               COMPLETE
Test scenarios baseline       COMPLETE
Existing test plan            AVAILABLE
Some runtime tests            ALREADY EXECUTED
Centralized evidence          TO COMPLETE
Application final tests       TO COMPLETE
Security test campaign        TO COMPLETE
Restore test                  TO COMPLETE
Accessibility tests           TO COMPLETE
```

---

# 83. Conclusion

Le niveau de preuve attendu est :

```text
Requirement
+
Scenario
+
Execution
+
Observed Result
+
Evidence
```

Le principe directeur est :

```text
A test plan proves preparation.
A test result proves execution.
```

---

**BC03 / C6 — Tests exécutés : BASELINE COMPLETE / RUNTIME EVIDENCE REQUIRED**