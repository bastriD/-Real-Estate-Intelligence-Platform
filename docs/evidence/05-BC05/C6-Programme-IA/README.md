# BC05 — C6 — Programme IA

**Bloc de compétences :** BC05  
**Compétence :** C6 — Concevoir, développer, intégrer et exploiter un programme IA complet  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Version :** 1.0  
**Statut :** Baseline documentaire — programme exécutable et preuves runtime à produire

---

# 1. Objectif

Ce dossier décrit l'architecture du programme IA complet utilisé par la plateforme.

L'objectif est de relier :

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
Matching / Model
 |
 v
Evaluation
 |
 v
Model Tracking
 |
 v
Serving
 |
 v
Application
 |
 v
Monitoring
 |
 v
Evidence
```

La compétence ne doit pas être démontrée uniquement par un notebook ou un modèle entraîné.

Le programme doit être :

- structuré ;
- versionné ;
- testable ;
- exécutable ;
- observable ;
- reproductible ;
- intégrable au SI.

---

# 2. Sources de référence

Le modèle métier est défini dans :

```text
../C5-Modele-Matching-IA/README.md
```

Le modèle de données est défini dans :

```text
../C1-MCD-Migration-SQL/MCD-MERISE-PROJET.md
../C1-MCD-Migration-SQL/MLD-PROJET.md
../C1-MCD-Migration-SQL/MPD-POSTGRESQL.md
```

Architecture AI générale :

```text
../../../50-AI/01-AI-Platform-Architecture.md
../../../50-AI/03-MLOps-Architecture.md
../../../50-AI/05-Model-Lifecycle.md
../../../50-AI/09-AI-Observability.md
```

Diagrammes :

```text
../../../99-DIAGRAMS/08-AI-Architecture.puml
../../../99-DIAGRAMS/09-MLOps-Architecture.puml
```

---

# 3. Architecture générale du programme

Le programme IA cible suit :

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
Rules Baseline       ML Model
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
        Application
```

---

# 4. Séparation des responsabilités

Le programme doit séparer :

```text
data loading
preprocessing
feature engineering
training
evaluation
tracking
serving
API
configuration
tests
```

et éviter un unique script contenant toute la logique.

---

# 5. Structure cible du code

Une structure possible est :

```text
ai-matching/
│
├── README.md
├── pyproject.toml
├── Dockerfile
├── .env.example
│
├── src/
│   └── matching/
│       ├── __init__.py
│       ├── config.py
│       ├── database.py
│       │
│       ├── data/
│       │   ├── loader.py
│       │   ├── preprocessing.py
│       │   └── features.py
│       │
│       ├── baseline/
│       │   └── scoring.py
│       │
│       ├── models/
│       │   ├── train.py
│       │   ├── evaluate.py
│       │   └── registry.py
│       │
│       ├── services/
│       │   └── matching_service.py
│       │
│       ├── api/
│       │   ├── schemas.py
│       │   └── routes.py
│       │
│       └── observability/
│           └── metrics.py
│
├── tests/
│   ├── test_scoring.py
│   ├── test_features.py
│   ├── test_model.py
│   └── test_api.py
│
└── scripts/
    ├── train.py
    ├── evaluate.py
    └── smoke_test.py
```

La structure exacte devra correspondre au code réellement produit.

---

# 6. Configuration

La configuration doit rester séparée du code.

Exemples :

```text
DATABASE_URL
MLFLOW_TRACKING_URI
MODEL_NAME
MODEL_VERSION
OLLAMA_URL
LOG_LEVEL
```

Les secrets ne doivent pas être codés en dur.

---

# 7. Configuration example

```text
DATABASE_URL=postgresql://...
MLFLOW_TRACKING_URI=http://mlflow...
MODEL_NAME=real-estate-matching
OLLAMA_URL=http://...
```

Le fichier réel :

```text
.env
```

ne doit pas être versionné avec des secrets.

---

# 8. Chargement des données

Le programme doit charger les données nécessaires depuis une source contrôlée.

Architecture :

```text
PostgreSQL
    |
    v
loader.py
    |
    v
DataFrame / internal structures
```

Le loader ne doit pas contenir la logique métier de scoring.

---

# 9. Dataset Builder

Le dataset peut être produit à partir de :

```text
DEMANDE_VERSION
BIEN
PRESENTATION
```

et éventuellement :

```text
feedback
analytics
historical outcomes
```

---

# 10. Requête dataset

Une requête pourra joindre les éléments nécessaires.

Exemple logique :

```text
DEMANDE_VERSION
       |
       +--> PRESENTATION
               |
               +--> BIEN
```

Le SQL final devra être écrit à partir du schéma réel.

---

# 11. Séparation train / inference

Le dataset utilisé pour l'entraînement ne doit pas être confondu avec l'entrée d'inférence.

```text
Training
=
historical labeled dataset
```

```text
Inference
=
current request + candidate properties
```

---

# 12. Preprocessing

Le preprocessing peut inclure :

```text
missing-value handling
categorical normalization
numerical normalization
text cleanup
boolean conversion
```

---

# 13. Reproductibilité preprocessing

Le même preprocessing doit être utilisé pour :

```text
training
```

et :

```text
inference
```

afin d'éviter le :

```text
training-serving skew
```

---

# 14. Feature Engineering

Les features peuvent inclure :

```text
price_difference
budget_ratio
surface_difference
surface_ratio
room_difference
city_match
property_type_match
parking_match
elevator_match
outdoor_match
```

---

# 15. Feature schema

Une structure candidate :

```text
budget_score
surface_score
location_match
type_match
room_match
parking_match
elevator_match
outdoor_match
semantic_score
```

La liste finale dépendra du dataset réel.

---

# 16. Feature validation

Les features doivent être vérifiées avant utilisation.

Exemples :

```text
no invalid range
no unexpected null
valid categorical values
```

---

# 17. Baseline rules-based

Le programme doit d'abord fournir une baseline simple.

Exemple :

```python
def compute_score(features, weights):
    return sum(
        features[name] * weight
        for name, weight in weights.items()
    )
```

Le code réel devra notamment contrôler les valeurs et pondérations.

---

# 18. Version baseline

La baseline elle-même doit être versionnée.

Exemple :

```text
rules-v1
```

---

# 19. Configuration des poids

Les poids peuvent être définis séparément.

Exemple :

```yaml
budget: 0.30
location: 0.25
surface: 0.20
property_type: 0.10
criteria: 0.15
```

Le total doit être validé.

---

# 20. Validation poids

Règle :

```text
sum(weights) = 1
```

ou équivalent selon la formule retenue.

Un test automatique doit vérifier cette propriété.

---

# 21. Machine Learning

Après la baseline, le programme peut entraîner des modèles ML.

Candidats :

```text
Logistic Regression
Random Forest
Gradient Boosting
```

Le choix final doit être comparé à la baseline.

---

# 22. train.py

Le module training doit être responsable de :

```text
load dataset
split data
fit model
calculate metrics
log experiment
save artifact
```

---

# 23. Train / Test Split

Une séparation doit éviter d'évaluer sur les mêmes données utilisées pour entraîner.

Exemple :

```text
Training Set
Validation Set
Test Set
```

ou une stratégie adaptée au dataset.

---

# 24. Random State

Pour améliorer la reproductibilité :

```text
random_state
```

doit être défini lorsque l'algorithme le permet.

---

# 25. Data Leakage

Le dataset ne doit pas contenir une feature révélant directement la cible.

Exemple dangereux :

```text
target = retained
feature = final_status_retained
```

Cela donnerait artificiellement des métriques très élevées.

---

# 26. Temporal leakage

Lorsque les données sont temporelles, il faut éviter d'utiliser une information future pour prédire le passé.

---

# 27. evaluate.py

Le module d'évaluation doit calculer les métriques retenues.

Exemple :

```python
metrics = {
    "precision": ...,
    "recall": ...,
    "f1": ...
}
```

---

# 28. Métriques

Les métriques principales dépendront du problème final.

Candidats :

```text
precision
recall
f1
roc_auc
top_k_recall
latency
```

---

# 29. Métriques métier

Les métriques techniques doivent être complétées par des indicateurs métier lorsque disponibles.

Exemples :

```text
property presented
property visited
property retained
```

---

# 30. MLflow

MLflow doit centraliser les expérimentations.

Architecture :

```text
train.py
   |
   v
MLflow Tracking
   |
   +--> params
   +--> metrics
   +--> artifacts
   +--> model
```

---

# 31. Experiment

Nom candidat :

```text
real-estate-matching
```

---

# 32. Run metadata

Chaque run doit idéalement identifier :

```text
algorithm
parameters
dataset reference
Git commit
metrics
artifact
```

---

# 33. Exemple MLflow

```python
with mlflow.start_run():
    mlflow.log_params(params)
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(model, "model")
```

Le code final dépendra du modèle retenu.

---

# 34. Model Registry

Après évaluation :

```text
Experiment Run
     |
     v
Model Candidate
     |
     v
MLflow Model Registry
```

---

# 35. Versioning

Le registry doit permettre :

```text
version 1
version 2
version 3
```

avec association au run correspondant.

---

# 36. Model Selection

La sélection doit comparer :

```text
candidate
```

et :

```text
baseline / current model
```

---

# 37. Quality Gate

Exemple logique :

```text
Candidate
   |
   v
Metrics acceptable?
   |
   +--> NO -> reject
   |
   +--> YES -> register / approve
```

---

# 38. Promotion

Le MVP peut conserver une étape humaine.

```text
Automated evaluation
        |
        v
Human approval
        |
        v
Selected model
```

---

# 39. registry.py

Le module registry peut gérer :

```text
get selected model version
load model
retrieve metadata
```

---

# 40. Serving

Le modèle sélectionné doit être exposé par un service.

Architecture :

```text
FastAPI
   |
   v
MatchingService
   |
   v
Model / Baseline
```

---

# 41. MatchingService

Responsabilités :

```text
validate request
load candidates
compute features
execute matching
rank results
return explanations
```

Il ne doit pas contenir directement toute la logique HTTP.

---

# 42. API Schema

Exemple conceptuel :

```python
class MatchRequest(BaseModel):
    request_version_id: int
    limit: int = 20
```

---

# 43. API Response

```python
class MatchResult(BaseModel):
    property_id: int
    rank: int
    score: float
```

La réponse finale pourra inclure les sous-scores et explications.

---

# 44. Endpoint

Candidat :

```text
POST /api/v1/matching
```

---

# 45. Health endpoint

Le programme doit fournir :

```text
GET /health
```

---

# 46. Readiness

Une readiness probe peut vérifier :

```text
application started
model loaded
critical dependencies reachable
```

selon le design retenu.

---

# 47. Error Handling

Les erreurs doivent distinguer :

```text
invalid request
database unavailable
model unavailable
internal error
```

---

# 48. Timeout

Les appels aux dépendances doivent utiliser des timeouts adaptés.

En particulier :

```text
database
Ollama
external AI if any
```

---

# 49. Ollama

Le programme peut utiliser Ollama pour des tâches complémentaires.

Exemples :

```text
criteria extraction
match explanation
document summary
semantic assistance
```

Ollama ne remplace pas nécessairement le modèle de matching.

---

# 50. Client Ollama

Une couche dédiée doit isoler l'intégration.

```text
MatchingService
      |
      v
OllamaClient
      |
      v
Ollama API
```

---

# 51. Pourquoi isoler Ollama

Cela permet :

- mock dans les tests ;
- changement d'endpoint ;
- changement de modèle ;
- gestion timeout/retry ;
- observabilité.

---

# 52. Structured AI Output

Les sorties destinées à être consommées par le programme doivent être structurées et validées.

---

# 53. Example

```json
{
  "preferences": [
    "quiet",
    "tram",
    "bright"
  ]
}
```

doit être validé avant utilisation.

---

# 54. RAG future

Une capacité RAG peut être intégrée comme un service distinct.

```text
Matching API
    |
    +--> Structured Matching
    |
    +--> RAG Service
```

Elle ne doit pas être obligatoire pour le fonctionnement de base si le besoin peut être satisfait sans elle.

---

# 55. Tests unitaires

Tests principaux :

```text
scoring functions
feature functions
validation
model wrapper
ranking
```

---

# 56. Exemple scoring test

```python
def test_score_is_between_zero_and_hundred():
    ...
```

---

# 57. Test poids

```python
def test_weights_sum_to_one():
    ...
```

---

# 58. Test ranking

Avec des scores :

```text
80
95
70
```

le résultat doit être classé :

```text
95
80
70
```

---

# 59. Test filter

Si une propriété ne respecte pas une contrainte obligatoire, elle ne doit pas atteindre l'étape de ranking avancé.

---

# 60. Tests dataset

Tester :

```text
expected columns
no invalid target
valid data types
```

---

# 61. Tests model

Tester notamment :

```text
model loads
model predicts
output shape
valid score domain
```

---

# 62. Tests API

Exemples :

```text
GET /health -> 200
```

```text
POST matching valid -> 200
```

```text
invalid request -> 422
```

---

# 63. Tests d'intégration

Tester :

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

# 64. Test MLflow

Une campagne de test doit démontrer qu'un run est réellement créé.

Preuves :

```text
experiment
run ID
params
metrics
artifact
```

---

# 65. Test Model Registry

Vérifier :

```text
model name
version
source run
```

---

# 66. Test Ollama

Le projet dispose déjà d'un exemple de connectivité Ollama distante.

Une preuve future pourra être centralisée dans le dossier evidence.

---

# 67. Packaging Python

Les dépendances doivent être versionnées via :

```text
pyproject.toml
```

ou :

```text
requirements.txt
```

---

# 68. Python Version

Une version explicite doit être utilisée.

Exemple candidat :

```text
Python 3.12
```

selon la compatibilité des bibliothèques retenues.

---

# 69. Docker

Le programme sera conteneurisé.

Architecture :

```text
Source Code
    |
    v
Docker Build
    |
    v
Image
    |
    v
Registry
    |
    v
Kubernetes
```

---

# 70. Dockerfile

Le Dockerfile doit :

- utiliser une image adaptée ;
- installer uniquement les dépendances nécessaires ;
- ne contenir aucun secret ;
- utiliser un utilisateur non-root lorsque possible ;
- fournir une commande claire.

---

# 71. Exemple logique

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install ...

COPY src ./src

CMD ["uvicorn", "..."]
```

Le Dockerfile final sera produit lors de l'implémentation.

---

# 72. Image Tagging

Les images doivent être traçables.

Exemples :

```text
matching-api:<git-sha>
matching-api:v1.0.0
```

---

# 73. Container Registry

GitLab Container Registry peut stocker les images si utilisé dans le repository final.

---

# 74. Kubernetes

Le service doit pouvoir être déployé sur Kubernetes.

Composants possibles :

```text
Deployment
Service
Ingress
ConfigMap
Secret
```

---

# 75. Deployment

Le Deployment doit notamment définir :

```text
image
replicas
resources
health probes
configuration
```

---

# 76. Resource Requests

Le service doit définir des requests réalistes.

Exemple à mesurer :

```text
cpu
memory
```

---

# 77. Resource Limits

Les limites doivent éviter une consommation incontrôlée tout en restant adaptées au workload.

---

# 78. Liveness

Une liveness probe vérifie si le processus doit être redémarré.

---

# 79. Readiness

Une readiness probe vérifie si le pod est prêt à recevoir du trafic.

---

# 80. Ingress

L'API peut être exposée via :

```text
NGINX Ingress
```

avec TLS selon le besoin.

---

# 81. GitOps

Le déploiement doit être géré via GitOps.

```text
GitLab
  |
  v
GitOps Repository
  |
  v
Argo CD
  |
  v
Kubernetes
```

---

# 82. CI

La CI du programme peut exécuter :

```text
lint
unit tests
integration tests
security checks
Docker build
publish
```

---

# 83. Pipeline cible

```text
validate
  |
  v
test
  |
  v
security
  |
  v
build
  |
  v
publish
```

Le déploiement reste réalisé par Argo CD.

---

# 84. ML Training Pipeline

Le training ne doit pas nécessairement être exécuté dans chaque CI applicative.

Il peut être orchestré séparément par Airflow.

---

# 85. Airflow Training DAG

Architecture :

```text
prepare_data
    |
    v
validate_data
    |
    v
train_model
    |
    v
evaluate_model
    |
    v
log_mlflow
    |
    v
quality_gate
```

---

# 86. Training vs Deployment

La plateforme sépare :

```text
Model Training
```

de :

```text
Application Deployment
```

Un nouveau training ne doit pas automatiquement remplacer le modèle actif sans validation.

---

# 87. Model Artifact

Les artifacts peuvent être stockés dans :

```text
MinIO
```

via MLflow.

---

# 88. Dependency chain

```text
Airflow
   |
   v
Training code
   |
   v
MLflow
   |
   v
MinIO
```

---

# 89. Observability

Le service doit fournir :

```text
metrics
logs
traces
health
```

---

# 90. Metrics

Exemples :

```text
matching_requests_total
matching_errors_total
matching_duration_seconds
matching_candidates_total
model_version_info
```

---

# 91. Histogram

La latence peut être exposée via un histogramme Prometheus.

---

# 92. Logs

Les logs doivent contenir des informations opérationnelles utiles.

Exemple :

```text
request_id
duration
candidate_count
model_version
status
```

---

# 93. Données à ne pas logger

Éviter :

```text
full client name
email
phone
full free-text requirement
full confidential document
```

dans les logs standards.

---

# 94. Tracing

OpenTelemetry peut instrumenter :

```text
FastAPI
PostgreSQL
AI call
```

selon l'intégration.

---

# 95. Trace example

```text
HTTP request
    |
    v
matching
    |
    v
database query
    |
    v
model inference
```

---

# 96. Grafana

Dashboard candidat :

```text
Request rate
Latency
Errors
Candidate count
Model versions
```

---

# 97. Alerting

Alertes possibles :

```text
high error rate
API unavailable
high latency
model load failure
database unavailable
```

---

# 98. AI Host Observability

Pour Ollama :

```text
GPU utilization
VRAM
temperature
inference duration
```

peuvent être observés.

---

# 99. Security

Le programme doit respecter :

```text
input validation
authentication
authorization
secret management
TLS
least privilege
dependency security
```

---

# 100. AI Security

Les traitements AI doivent également prendre en compte :

```text
prompt injection
data leakage
unsafe input
unsafe output
unauthorized document access
```

---

# 101. RGPD

Le programme doit minimiser les données transmises aux modèles.

Exemple :

pour calculer un matching immobilier, le modèle n'a généralement pas besoin de connaître :

```text
client email
client phone
full identity
```

---

# 102. Data Minimization

Architecture préférée :

```text
Client Data
    |
    v
Relevant Criteria Only
    |
    v
Matching
```

---

# 103. Souveraineté

Le traitement local est privilégié pour les données internes et sensibles.

```text
Private Data
    |
    v
Local Infrastructure
    |
    v
Local AI
```

---

# 104. External AI

Une API AI externe, si elle est utilisée, doit être une exception gouvernée.

Les données envoyées doivent être analysées avant transmission.

---

# 105. Model Card

Le modèle final doit être accompagné d'une fiche décrivant :

```text
purpose
version
features
training dataset
metrics
limitations
security considerations
intended use
```

---

# 106. Runbook

Le service final devrait disposer d'un runbook minimum.

Exemples :

```text
API unavailable
model cannot load
MLflow unavailable
database unavailable
Ollama unavailable
```

---

# 107. Graceful Degradation

Si le modèle ML n'est pas disponible, une stratégie possible peut être :

```text
ML unavailable
      |
      v
Rules baseline
```

si cela est techniquement et fonctionnellement acceptable.

---

# 108. LLM degradation

Si Ollama est indisponible :

```text
semantic explanation unavailable
```

mais le matching structuré peut continuer si son architecture est indépendante.

---

# 109. Reproductibilité

Le programme final doit pouvoir identifier :

```text
Git SHA
Container image
Model version
Dataset version/reference
Configuration
```

---

# 110. Evidence chain

La preuve idéale est :

```text
Git Commit
    |
    v
CI Pipeline
    |
    v
Container Image
    |
    v
Argo CD
    |
    v
Kubernetes
    |
    v
FastAPI
    |
    v
Model Version
    |
    v
Matching Result
    |
    v
Metrics / Logs / Trace
```

---

# 111. Preuves attendues

Les preuves futures comprennent :

```text
source tree
training script
evaluation script
unit tests
MLflow run
model version
model artifact
Docker image
CI pipeline
Kubernetes deployment
API response
Prometheus metric
Grafana dashboard
Airflow DAG
```

---

# 112. Structure future evidence

```text
C6-Programme-IA/
│
├── README.md
│
├── source/
├── tests/
├── docker/
├── kubernetes/
├── airflow/
├── ci/
├── evidence/
└── EXECUTION-REPORT.md
```

Ces dossiers ne devront être créés que lorsqu'ils contiennent des artifacts réels.

---

# 113. Execution Report

Le rapport final devra contenir :

```text
Version
Environment
Dataset
Model
Model version
Container image
Deployment
Tests
Observed result
Metrics
Known limitations
```

---

# 114. Minimum Demonstration

Pour une démonstration convaincante :

```text
1. Dataset prepared
2. Model/baseline executed
3. Evaluation produced
4. MLflow run created
5. Model version identifiable
6. API starts
7. Matching request succeeds
8. Container runs
9. Kubernetes deployment works
10. Test suite passes
11. Metrics visible
```

---

# 115. Ce qui ne suffit pas

Les éléments suivants ne suffisent pas seuls :

```text
Python file exists
Notebook executes
MLflow is installed
Ollama answers
Dockerfile exists
Kubernetes exists
```

La compétence demande une chaîne intégrée.

---

# 116. Relation avec C5

C5 définit :

```text
what the model/matching does
```

C6 définit :

```text
how the complete AI program is engineered and operated
```

---

# 117. Relation avec C3

Le Data Warehouse peut fournir des datasets analytiques ou features historiques pour le programme IA.

---

# 118. Relation avec C4

La taille du dataset et le nombre de requêtes déterminent les limites de l'architecture IA.

---

# 119. Relation avec C7

Les données d'entraînement et d'inférence doivent respecter le RGPD.

---

# 120. Relation avec C8

Le programme IA doit intégrer les exigences de :

```text
sovereignty
security
confidentiality
model governance
```

---

# 121. Statut actuel

| Élément | Statut |
|---|---|
| Programme architecture | DOCUMENTÉE |
| Code structure | DÉFINIE |
| Data loading | DÉFINI |
| Preprocessing | DÉFINI |
| Features | DÉFINIES |
| Baseline | DÉFINIE |
| Training architecture | DÉFINIE |
| Evaluation | DÉFINIE |
| MLflow integration | DÉFINIE |
| Registry | DÉFINI |
| FastAPI serving | DÉFINI |
| Docker | DÉFINI |
| Kubernetes | DÉFINI |
| GitOps | DÉFINI |
| CI | DÉFINIE |
| Airflow training | DÉFINI |
| Observability | DÉFINIE |
| Security | DÉFINIE |
| Source code | À PRODUIRE |
| Tests | À PRODUIRE |
| Container | À PRODUIRE |
| CI execution | À PRODUIRE |
| Runtime deployment | À PRODUIRE |
| MLflow evidence | À PRODUIRE |
| API evidence | À PRODUIRE |

---

# 122. Conclusion

Le programme IA du projet doit fonctionner comme une chaîne industrielle et traçable :

```text
Data
 |
 v
Processing
 |
 v
Matching / Model
 |
 v
Evaluation
 |
 v
MLflow
 |
 v
Model Version
 |
 v
API
 |
 v
Container
 |
 v
Kubernetes
 |
 v
Observability
```

L'objectif est de dépasser le simple prototype et de démontrer une capacité réelle à intégrer l'IA dans une architecture Data/DevOps exploitable.

Les preuves finales seront basées sur le programme réellement exécuté et non uniquement sur cette architecture documentaire.

---

**BC05 / C6 — PROGRAMME IA — DOCUMENTATION BASELINE COMPLETE**