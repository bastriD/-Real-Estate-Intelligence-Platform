# BC05 — C6 — Programme IA

**Bloc de compétences :** BC05  
**Compétence :** Concevoir, développer, intégrer et exploiter un programme IA complet  
**Projet :** Real Estate Intelligence Platform  
**Version :** 2.0  
**Statut :** Baseline documentaire — implémentation exécutable à produire  
**Extension projet :** entraînement réel, MLflow, registry, serving et observabilité  

---

# 1. Objectif

Cette partie décrit l'architecture du programme IA complet.

Le programme doit relier :

```text
Data
 |
 v
Preprocessing
 |
 v
Feature Engineering
 |
 v
Matching / ML
 |
 v
Evaluation
 |
 v
MLflow
 |
 v
Model Selection
 |
 v
Serving
 |
 v
API
 |
 v
Kubernetes
 |
 v
Observability
```

L'objectif est de démontrer une chaîne exécutable, reproductible et exploitable.

---

# 2. Positionnement

Le socle attendu couvre :

```text
data preparation
features
matching architecture
AI program design
```

Notre projet va plus loin en ajoutant :

```text
real training
model comparison
MLflow tracking
model registry
API inference
Docker
Kubernetes
GitLab CI
GitOps
monitoring
```

---

# 3. Architecture générale

```text
PostgreSQL
    |
    v
Dataset Builder
    |
    v
Preprocessing
    |
    v
Feature Engineering
    |
    +------------------+
    |                  |
    v                  v
Rules Baseline       ML Models
    |                  |
    +--------+---------+
             |
             v
         Evaluation
             |
             v
           MLflow
             |
             v
      Approved Version
             |
             v
        Matching API
             |
             v
          FastAPI
             |
             v
        Kubernetes
```

---

# 4. Sources principales

Le programme consomme principalement :

```text
real_estate.demande_version
```

et :

```text
real_estate.bien
```

Il peut également exploiter :

```text
real_estate.presentation
real_estate.commentaire
```

pour créer des labels ou du feedback.

---

# 5. Séparation des responsabilités

Le code doit séparer :

```text
data loading
preprocessing
feature engineering
baseline scoring
training
evaluation
tracking
registry
serving
API
observability
configuration
```

---

# 6. Structure cible

```text
src/
├── api/
├── services/
├── domain/
└── ai/

ml/
├── features/
├── training/
├── evaluation/
└── models/

tests/
├── unit/
├── integration/
├── security/
└── e2e/
```

---

# 7. Structure IA détaillée

Une structure cible possible :

```text
src/ai/
├── matching_service.py
├── model_loader.py
├── baseline_adapter.py
├── ml_adapter.py
├── ollama_client.py
└── schemas.py
```

et :

```text
ml/features/
├── build_features.py
└── validators.py

ml/training/
├── train_logistic.py
├── train_random_forest.py
└── train_all.py

ml/evaluation/
├── metrics.py
├── compare_models.py
└── report.py

ml/models/
└── model_config.yaml
```

---

# 8. Configuration

La configuration doit être séparée du code.

Exemples :

```text
DATABASE_URL
MLFLOW_TRACKING_URI
MODEL_NAME
MODEL_STAGE
OLLAMA_URL
LOG_LEVEL
```

---

# 9. Secrets

Les secrets ne doivent pas apparaître dans :

```text
source code
README
Dockerfile
Git
logs
```

Ils doivent être injectés via la stratégie de secrets de la plateforme.

---

# 10. Dataset Builder

Le dataset d'entraînement est construit à partir de :

```text
DEMANDE_VERSION
+
BIEN
+
PRESENTATION / COMMENTAIRE
```

selon la cible retenue.

---

# 11. Grain du dataset

Une ligne représente :

```text
1 DEMANDE_VERSION
+
1 BIEN
```

---

# 12. Features principales

Le dataset peut contenir :

```text
budget_ratio
budget_difference
surface_difference
room_difference
bedroom_difference
city_match
property_type_match
dpe_difference
preference_match_ratio
```

---

# 13. Preprocessing

Le preprocessing peut inclure :

```text
missing values
categorical normalization
numerical normalization
boolean conversion
DPE encoding
preference extraction
```

---

# 14. Consistency

Le même preprocessing doit être utilisé pour :

```text
training
```

et :

```text
inference
```

pour éviter le :

```text
training-serving skew
```

---

# 15. Validation des features

Avant entraînement :

```text
expected columns
valid ranges
no invalid target
controlled null values
valid types
```

doivent être vérifiés.

---

# 16. Baseline rules-based

La première implémentation sera déterministe.

Architecture :

```text
features
  |
  v
weighted scoring
  |
  v
score
```

Cette baseline fournit le benchmark de référence.

---

# 17. Modèles ML prévus

Premiers modèles :

```text
Logistic Regression
Random Forest
```

Ils seront comparés à la baseline.

---

# 18. Pourquoi ces modèles

Ils offrent :

```text
low complexity
fast training
easy evaluation
interpretability
good tabular baselines
```

---

# 19. Training Pipeline

Le pipeline doit exécuter :

```text
load dataset
split data
build features
train
evaluate
log MLflow
register candidate
```

---

# 20. Train / Validation / Test

Le dataset sera séparé pour éviter l'évaluation sur les données d'entraînement.

Selon le volume :

```text
train
validation
test
```

ou :

```text
cross-validation
```

---

# 21. Data Leakage

Le pipeline doit empêcher :

```text
future outcome
```

d'être utilisé comme feature pour prédire ce même outcome.

---

# 22. Temporal Leakage

Si les données sont temporelles, les informations futures ne doivent pas être visibles au modèle lors d'une prédiction historique.

---

# 23. Metrics

Métriques principales :

```text
Precision
Recall
F1
ROC-AUC
PR-AUC
```

et pour le ranking :

```text
Precision@K
Recall@K
NDCG@K
HitRate@K
```

---

# 24. Business Metrics

À terme :

```text
visit rate
retention rate
conversion rate
time to successful match
```

compléteront les métriques techniques.

---

# 25. Comparison

Le rapport comparera :

```text
Rules
Logistic Regression
Random Forest
```

sur le même jeu de test.

---

# 26. Pas de métriques théoriques

Aucune valeur ne doit être annoncée avant exécution.

Avant entraînement :

```text
TBD
```

---

# 27. MLflow

MLflow centralise :

```text
parameters
metrics
artifacts
model versions
run metadata
```

---

# 28. Experiment

Nom candidat :

```text
real-estate-matching
```

---

# 29. Run Metadata

Chaque run doit identifier autant que possible :

```text
algorithm
parameters
feature version
dataset reference
Git SHA
metrics
artifact
```

---

# 30. Artifacts

Les modèles et rapports peuvent être stockés via :

```text
MLflow
+
MinIO
```

---

# 31. Model Registry

Le modèle sélectionné peut être enregistré dans :

```text
MLflow Model Registry
```

---

# 32. Promotion

Cycle :

```text
Experiment
   |
   v
Candidate
   |
   v
Evaluation
   |
   v
Approval
   |
   v
Selected Model
```

---

# 33. Human Approval

Pour la première version, la promotion reste contrôlée.

Un modèle ne doit pas être automatiquement remplacé uniquement parce qu'un training a terminé.

---

# 34. Champion / Challenger

Évolution possible :

```text
Champion
vs
Challenger
```

Le challenger doit démontrer une amélioration avant remplacement.

---

# 35. Model Selection Criteria

La sélection prend en compte :

```text
metrics
ranking quality
latency
model size
interpretability
resource usage
operational complexity
```

---

# 36. Model Card

Le modèle final doit disposer d'une fiche contenant :

```text
name
version
purpose
algorithm
features
dataset
metrics
limitations
risks
intended use
```

---

# 37. Dataset Card

Le dataset important doit également documenter :

```text
origin
schema
generation
personal data status
quality
limitations
```

---

# 38. Synthetic Data

Le générateur StarterPack peut fournir des données techniques.

Ces données peuvent valider :

```text
pipeline
training
evaluation
tracking
serving
```

mais ne prouvent pas automatiquement la performance métier réelle.

---

# 39. Training vs Business Validation

Nous distinguons :

```text
Technical ML Validation
```

de :

```text
Business Validation
```

---

# 40. Technical Validation

```text
training succeeds
metrics calculated
artifact produced
model loads
API predicts
```

---

# 41. Business Validation

```text
ranking useful
hunter accepts recommendations
client feedback positive
```

nécessite un feedback métier réaliste.

---

# 42. Airflow

Airflow peut orchestrer le training.

DAG candidat :

```text
matching_model_training
```

---

# 43. DAG cible

```text
extract_training_data
        |
        v
validate_dataset
        |
        v
build_features
        |
        v
split_dataset
        |
        +------------------+
        |                  |
        v                  v
train_logistic      train_random_forest
        |                  |
        +---------+--------+
                  |
                  v
            evaluate_models
                  |
                  v
             compare_models
                  |
                  v
              log_mlflow
                  |
                  v
         register_candidate
```

---

# 44. Airflow vs MLflow

```text
Airflow
=
workflow orchestration
```

```text
MLflow
=
experiment/model lifecycle
```

Ils ont des responsabilités différentes.

---

# 45. Training in CI

La CI ne doit pas nécessairement exécuter le training complet.

Elle peut exécuter :

```text
small dataset smoke training
```

pour vérifier :

```text
pipeline still works
```

---

# 46. Full Training

L'entraînement complet pourra être déclenché via :

```text
Airflow
```

ou manuellement dans un workflow contrôlé.

---

# 47. Serving Architecture

```text
FastAPI
   |
   v
MatchingService
   |
   +--> RulesAdapter
   |
   +--> MLAdapter
   |
   +--> OllamaAdapter
```

---

# 48. MatchingService

Responsabilités :

```text
validate request
load demand version
load candidate properties
compute features
filter
score
rank
return Top-K
```

---

# 49. API Endpoint

Candidat :

```text
POST /api/v1/matching/rank
```

---

# 50. Input

Exemple :

```json
{
  "request_version_id": 123,
  "limit": 10
}
```

---

# 51. Output

Exemple :

```json
{
  "request_version_id": 123,
  "results": [
    {
      "property_id": 501,
      "score": 0.93,
      "rank": 1
    }
  ]
}
```

---

# 52. Runtime Model Metadata

La réponse peut contenir :

```text
scoring_method
model_version
```

sans nécessairement persister immédiatement ces informations dans `PRESENTATION`.

---

# 53. Pourquoi ne pas modifier encore le modèle Data

La traçabilité ML peut d'abord être assurée par :

```text
API response
logs
MLflow
request_id
```

avant de décider si elle doit devenir une donnée métier persistante.

---

# 54. Future Scoring Audit

Si nécessaire, une future entité dédiée pourra représenter :

```text
SCORING_RUN
```

ou :

```text
MATCHING_EXECUTION
```

au lieu de surcharger `PRESENTATION`.

---

# 55. Health Endpoint

```text
GET /health
```

---

# 56. Readiness

```text
GET /ready
```

peut vérifier :

```text
service started
model loaded
critical dependencies available
```

---

# 57. Error Handling

Le service doit distinguer :

```text
invalid request
request version not found
database unavailable
model unavailable
AI dependency unavailable
internal error
```

---

# 58. Timeout

Les dépendances doivent utiliser des timeouts :

```text
PostgreSQL
Ollama
external service
```

---

# 59. Ollama

Ollama est réservé aux tâches où un LLM apporte réellement de la valeur.

Exemples :

```text
criteria extraction
semantic preferences
match explanation
document summarization
```

---

# 60. LLM Isolation

Le code métier ne doit pas appeler directement Ollama partout.

Utiliser :

```text
OllamaClient
```

ou :

```text
AIAdapter
```

---

# 61. Pourquoi Adapter

Cela facilite :

```text
tests
mock
provider replacement
timeouts
monitoring
fallback
```

---

# 62. Structured Output

Les sorties LLM utilisées par l'application doivent être structurées et validées.

Exemple :

```json
{
  "preferences": [
    "quiet",
    "tram",
    "bright"
  ]
}
```

---

# 63. Hallucination

Le LLM ne doit pas être considéré comme source de vérité pour :

```text
price
surface
address
legal fact
client identity
```

---

# 64. Grounding

Les réponses factuelles doivent provenir :

```text
PostgreSQL
authorized documents
```

avant génération.

---

# 65. Semantic Matching

Une couche future peut ajouter :

```text
embedding similarity
```

pour les critères textuels.

---

# 66. Vector Candidates

```text
pgvector
Qdrant
```

restent les deux options principales à évaluer.

---

# 67. Vector Decision

```text
benchmark
   |
   v
complexity comparison
   |
   v
ADR
```

avant adoption.

---

# 68. Unit Tests

Tests prévus :

```text
feature calculation
budget calculation
surface calculation
DPE encoding
preference ratio
baseline score
ranking
```

---

# 69. Model Tests

```text
model loads
prediction shape correct
valid score
same preprocessing
```

---

# 70. API Tests

```text
GET /health -> 200
POST valid matching -> 200
invalid payload -> 422
unknown demand -> expected error
```

---

# 71. Integration Tests

Chaîne :

```text
PostgreSQL
+
MatchingService
+
Model
+
FastAPI
```

---

# 72. MLflow Test

La preuve doit montrer :

```text
experiment
run ID
params
metrics
artifact
```

---

# 73. Registry Test

La preuve doit montrer :

```text
model name
version
source run
```

---

# 74. Reproducibility Test

Un run doit permettre de retrouver :

```text
dataset
code
params
features
```

---

# 75. Docker

Le service sera conteneurisé.

```text
source
 |
 v
Docker Build
 |
 v
Image
 |
 v
Registry
```

---

# 76. Dockerfile Principles

```text
minimal image
explicit dependencies
non-root where possible
no secrets
health-aware
```

---

# 77. Image Tagging

Tags :

```text
matching-api:<git-sha>
```

et éventuellement :

```text
matching-api:v1.0.0
```

---

# 78. GitLab CI

La CI peut couvrir :

```text
lint
unit tests
integration tests
security scan
Docker build
image scan
publish
```

---

# 79. CI Separation

Pipeline modularisé :

```text
.gitlab/ci/application.yml
.gitlab/ci/ml.yml
.gitlab/ci/security.yml
.gitlab/ci/docker.yml
```

---

# 80. GitOps

Le déploiement suit :

```text
GitLab CI
    |
    v
Container Registry
    |
    v
GitOps desired state
    |
    v
Argo CD
    |
    v
Kubernetes
```

---

# 81. Kubernetes Deployment

Le service pourra utiliser :

```text
Deployment
Service
Ingress
ConfigMap
Secret
```

---

# 82. Resource Requests

À mesurer :

```text
CPU
RAM
```

et éventuellement GPU si le service exécute lui-même un modèle nécessitant une accélération.

---

# 83. Ollama GPU Separation

Le service FastAPI peut rester sur Kubernetes alors que :

```text
Ollama
```

reste sur l'hôte GPU dédié.

---

# 84. Liveness

Une liveness probe vérifie :

```text
process alive
```

---

# 85. Readiness

Une readiness probe vérifie :

```text
ready to serve traffic
```

---

# 86. Observability

Le programme expose :

```text
metrics
logs
traces
health
```

---

# 87. Prometheus Metrics

Exemples :

```text
matching_requests_total
matching_errors_total
matching_duration_seconds
matching_candidates_total
matching_results_total
```

---

# 88. Model Metrics

Métriques runtime possibles :

```text
model_load_status
model_version_info
inference_duration
```

---

# 89. Logs

Champs utiles :

```text
request_id
duration
candidate_count
result_count
scoring_method
model_version
status
```

---

# 90. Logs interdits

Éviter :

```text
email
phone
password
API key
full private prompt
full confidential document
```

---

# 91. Tracing

OpenTelemetry peut tracer :

```text
HTTP request
   |
   v
database query
   |
   v
feature generation
   |
   v
ML inference
   |
   v
optional Ollama call
```

---

# 92. Grafana

Dashboard candidat :

```text
Matching API
```

avec :

```text
request rate
latency
errors
candidate volume
model version
```

---

# 93. Security

Le service applique :

```text
authentication
authorization
input validation
least privilege
secret management
TLS
```

---

# 94. AI Security

Les risques spécifiques incluent :

```text
prompt injection
data leakage
unsafe retrieved content
model misuse
```

---

# 95. RGPD

Les features doivent être minimisées.

Le matching ne nécessite généralement pas :

```text
client email
phone
full identity
```

---

# 96. Local-first AI

Les données sensibles privilégient :

```text
local infrastructure
```

et :

```text
local Ollama
```

---

# 97. External AI

Une API externe éventuelle doit rester :

```text
governed exception
```

---

# 98. Graceful Degradation

Exemple :

```text
ML model unavailable
       |
       v
fallback rules
```

si cela reste fonctionnellement acceptable.

---

# 99. Ollama Failure

```text
Ollama unavailable
```

ne doit pas forcément rendre le matching structuré indisponible.

---

# 100. Model Rollback

Si un modèle dégrade le service :

```text
V3
 |
 v
problem
 |
 v
V2
```

doit pouvoir être restauré.

---

# 101. Runtime Traceability

Chaîne idéale :

```text
Git SHA
   |
   v
CI Pipeline
   |
   v
Container Image
   |
   v
Kubernetes Revision
   |
   v
Model Version
   |
   v
API Request
   |
   v
Metrics / Logs / Trace
```

---

# 102. Implementation Locations

Application :

```text
src/
```

ML :

```text
ml/
```

Airflow :

```text
pipelines/airflow/
```

Tests :

```text
tests/
```

Deployment :

```text
deploy/
```

CI :

```text
.gitlab/ci/
```

---

# 103. Documentation Location

Ce dossier reste uniquement :

```text
docs/evidence/05-BC05/C6-Programme-IA/
```

pour documentation et index de preuves.

---

# 104. Evidence Runtime

Preuves prévues :

```text
training execution
MLflow run
model comparison
model registry
API response
Docker image
CI pipeline
Kubernetes deployment
Prometheus metrics
Grafana dashboard
Airflow DAG
```

---

# 105. Minimum Demonstration

```text
1. Dataset generated/prepared
2. Features generated
3. Rules baseline executed
4. Logistic Regression trained
5. Random Forest trained
6. Models compared
7. MLflow run created
8. Model version registered
9. FastAPI serves ranking
10. Docker image runs
11. Tests pass
12. Kubernetes deploy succeeds
13. Metrics visible
```

---

# 106. Extension Value

Cette implémentation va volontairement au-delà du strict besoin documentaire.

Elle démontre une chaîne :

```text
Data Engineering
+
Machine Learning
+
MLOps
+
API Engineering
+
DevOps
+
Observability
```

dans le même projet.

---

# 107. Current Status

| Élément | Statut |
|---|---|
| AI program architecture | V2 COMPLETE |
| Dataset strategy | DEFINED |
| Feature pipeline | DEFINED |
| Rules baseline | DEFINED |
| Logistic Regression | PLANNED |
| Random Forest | PLANNED |
| Evaluation | DEFINED |
| MLflow | PLANNED |
| Model Registry | PLANNED |
| Model Card | DEFINED |
| FastAPI serving | DEFINED |
| Ollama integration | DEFINED |
| Docker | DEFINED |
| GitLab CI | DEFINED |
| GitOps | DEFINED |
| Kubernetes | DEFINED |
| Observability | DEFINED |
| Security | DEFINED |
| Runtime code | PENDING |
| Runtime training | PENDING |
| Runtime deployment | PENDING |
| Runtime evidence | PENDING |

---

# 108. Conclusion

Le Programme IA est conçu comme une chaîne complète :

```text
POSTGRESQL
    |
    v
DATASET
    |
    v
FEATURES
    |
    +------------------+
    |                  |
    v                  v
RULES                 ML
    |                  |
    +--------+---------+
             |
             v
         EVALUATION
             |
             v
           MLFLOW
             |
             v
       MODEL REGISTRY
             |
             v
          FASTAPI
             |
             v
          DOCKER
             |
             v
        KUBERNETES
             |
             v
      OBSERVABILITY
```

Le projet ne se limite donc pas à concevoir un modèle de matching : il met en place son cycle d'ingénierie complet, tout en conservant les fonctions ML avancées comme une extension volontaire clairement distinguée du minimum attendu.

---

**BC05 / C6 — PROGRAMME IA V2 — ML/MLOPS IMPLEMENTATION EXTENSION**