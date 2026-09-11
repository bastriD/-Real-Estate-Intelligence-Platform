# BC05 — C5 — Modèle de Matching IA

**Bloc de compétences :** BC05  
**Compétence :** Concevoir les données, variables et mécanismes nécessaires à un modèle de matching IA  
**Projet :** Real Estate Intelligence Platform  
**Version :** 2.0  
**Statut :** Baseline et régression logistique implémentées — évaluation et intégration ML à consolider
**Extension projet :** Entraînement, évaluation, versionnement et serving de modèles ML  

---

# 1. Objectif

Cette partie définit le système de matching entre :

```text
DEMANDE_VERSION
        |
        v
   Matching Engine
        ^
        |
       BIEN
```

Le système doit identifier les biens les plus pertinents pour une version donnée d'une recherche immobilière.

L'objectif minimum est de concevoir :

```text
data
features
matching logic
evaluation strategy
```

Le projet va volontairement plus loin avec :

```text
baseline algorithm
+
ML training
+
model comparison
+
MLflow tracking
+
model versioning
+
API inference
+
monitoring
```

---

# 2. Positionnement du projet

Nous distinguons deux niveaux.

## Certification Core

```text
Matching problem definition
Feature design
Input/output definition
Evaluation strategy
Data preparation
```

## Project Extension

```text
Actual training
Model evaluation
Experiment tracking
Model Registry
Model serving
MLOps
```

L'entraînement ML constitue donc une extension technique du projet.

---

# 3. Pourquoi aller plus loin

Un modèle uniquement décrit sur papier démontre la conception.

Un modèle réellement entraîné permet également de démontrer :

```text
implementation
reproducibility
experimentation
evaluation
deployment
observability
MLOps
```

Cette extension exploite directement l'architecture Enterprise AI Platform du projet.

---

# 4. Problème métier

Pour une demande immobilière donnée :

```text
Budget
Location
Property Type
Surface
Rooms
Bedrooms
DPE
Preferences
```

le système doit identifier les biens les plus pertinents.

---

# 5. Exemple

Demande :

```text
Ville:
Montpellier

Type:
Appartement

Budget max:
350000 €

Surface min:
70 m²

Rooms min:
3

Bedrooms min:
2

DPE max:
D

Preferences:
balcony
parking
quiet
```

Biens candidats :

```text
Property A
Property B
Property C
...
```

Le système produit :

```text
Property A -> 92
Property C -> 84
Property B -> 61
```

---

# 6. Architecture de Matching

```text
DEMANDE_VERSION
        |
        v
Feature Extraction
        |
        v
Hard Filtering
        |
        v
Candidate Set
        |
        v
Deterministic Scoring
        |
        v
ML Scoring
        |
        v
Optional Semantic Enrichment
        |
        v
Final Ranking
        |
        v
Top-K Properties
        |
        v
PRESENTATION
```

---

# 7. Principe fondamental

Le système ne doit pas commencer par un LLM.

Des contraintes telles que :

```text
budget
surface
city
property type
number of rooms
```

sont structurées.

Elles doivent être traitées par :

```text
SQL
Python
deterministic rules
```

avant toute couche IA plus coûteuse.

---

# 8. Hard Filters

Les contraintes incompatibles peuvent éliminer un bien.

Exemples :

```text
wrong city
price far above hard budget
wrong property type
surface below mandatory minimum
```

---

# 9. Exemple SQL

```sql
SELECT *
FROM real_estate.bien
WHERE ville = :ville
  AND type_bien = :type_bien
  AND prix <= :budget_max
  AND surface >= :surface_min;
```

Le filtrage réduit le nombre de candidats avant scoring.

---

# 10. Pourquoi filtrer tôt

Supposons :

```text
1000 properties
```

Après filtres :

```text
100 properties
```

Le moteur de scoring ne traite plus que :

```text
10 %
```

du dataset initial.

Cela réduit :

```text
CPU
memory
latency
AI inference
GPU workload
```

---

# 11. Feature Engineering

Les features doivent représenter la compatibilité :

```text
DEMANDE_VERSION
vs
BIEN
```

---

# 12. Budget Feature

Exemple :

```text
budget_ratio
=
property_price / budget_max
```

---

# 13. Budget Difference

```text
budget_difference
=
budget_max - property_price
```

Une valeur positive signifie :

```text
within budget
```

---

# 14. Surface Feature

```text
surface_difference
=
property_surface - requested_surface_min
```

---

# 15. Room Feature

```text
room_difference
=
property_rooms - requested_rooms_min
```

---

# 16. Bedroom Feature

```text
bedroom_difference
=
property_bedrooms - requested_bedrooms_min
```

---

# 17. Location Feature

Version simple :

```text
city_match
=
0 / 1
```

Évolution possible :

```text
distance_km
```

si les coordonnées sont disponibles.

---

# 18. Property Type Feature

```text
property_type_match
=
0 / 1
```

---

# 19. DPE Feature

Le DPE peut être converti en ordre :

```text
A = 1
B = 2
C = 3
D = 4
E = 5
F = 6
G = 7
```

pour comparer :

```text
requested_dpe_max
```

et :

```text
property_dpe
```

---

# 20. Preference Features

Les critères souhaités peuvent produire des variables :

```text
has_balcony
has_garden
has_parking
has_elevator
has_terrace
has_cellar
has_view
is_quiet
is_bright
has_pool
```

---

# 21. Preference Match Ratio

Exemple :

```text
preference_match_ratio
=
matched_preferences
/
requested_preferences
```

---

# 22. Missing Data

Les annonces peuvent avoir des informations absentes.

Le système doit distinguer :

```text
FALSE
```

de :

```text
UNKNOWN
```

Exemple :

```text
balcony = false
```

n'est pas équivalent à :

```text
balcony information missing
```

---

# 23. Feature Dataset

Une ligne du dataset ML représente :

```text
1 DEMANDE_VERSION
+
1 BIEN
```

Exemple :

```text
request_version_id
property_id

budget_ratio
surface_difference
room_difference
bedroom_difference
city_match
property_type_match
dpe_difference
preference_match_ratio

target
```

---

# 24. Target Variable

Pour un apprentissage supervisé, il faut définir une vérité terrain.

Les événements possibles sont :

```text
PRESENTE
REJETE
VISITE
RETENU
```

et les commentaires métier.

---

# 25. Première cible binaire

Une première cible possible :

```text
relevant = 1
```

si :

```text
RETENU
or
VISITE
```

et :

```text
relevant = 0
```

si :

```text
REJETE
```

Cette définition devra être validée à partir des données réellement disponibles.

---

# 26. Attention au Label Design

La cible ne doit pas être choisie uniquement parce qu'elle est facile à produire.

Exemple :

```text
PRESENTE
```

signifie que le système ou le chasseur a sélectionné le bien.

Cela ne signifie pas automatiquement :

```text
client likes property
```

---

# 27. Feedback Loop

Architecture future :

```text
Matching
    |
    v
Presentation
    |
    v
Client / Hunter Feedback
    |
    v
Commentaire
    |
    v
Training Dataset
    |
    v
New Model
```

---

# 28. Cold Start

Au démarrage, nous n'aurons probablement pas suffisamment de labels réels.

Nous commençons donc avec :

```text
Rule-Based Baseline
```

avant de dépendre d'un modèle supervisé.

---

# 29. Baseline déterministe

Exemple de score :

```text
Location      25 %
Budget        25 %
Property Type 15 %
Surface       15 %
Rooms         10 %
DPE            5 %
Preferences    5 %
```

Total :

```text
100 %
```

Ces pondérations sont initiales et doivent être évaluées.

---

# 30. Pourquoi une baseline

Une baseline permet de comparer les modèles ML à quelque chose de concret.

Un modèle ML n'est intéressant que s'il apporte une amélioration mesurable.

---

# 31. Baseline Score

Exemple :

```text
score =
location_score      * 0.25
+
budget_score        * 0.25
+
type_score          * 0.15
+
surface_score       * 0.15
+
room_score          * 0.10
+
dpe_score           * 0.05
+
preference_score    * 0.05
```

---

# 32. Premier modèle ML

Premier candidat :

```text
Logistic Regression
```

Pourquoi :

```text
simple
fast
interpretable
strong baseline
easy to debug
```

---

# 33. Deuxième modèle

Deuxième candidat :

```text
Random Forest
```

Pourquoi :

```text
non-linear relationships
feature interactions
robust baseline
feature importance
```

---

# 34. Modèles futurs

Selon les résultats :

```text
Gradient Boosting
XGBoost
LightGBM
Learning-to-Rank
Neural Ranking
```

pourront être évalués.

Ils ne doivent pas être introduits sans justification.

---

# 35. Pourquoi commencer simple

La stratégie est :

```text
Rules
  |
  v
Logistic Regression
  |
  v
Random Forest
  |
  v
Compare
  |
  v
More complex model only if justified
```

---

# 36. Train / Validation / Test

Le dataset doit être séparé en :

```text
training
validation
test
```

ou via :

```text
cross-validation
```

selon le volume disponible.

---

# 37. Data Leakage

Il faut empêcher qu'une information future soit utilisée pour prédire le passé.

Exemple incorrect :

```text
final purchase result
```

utilisé comme feature pour prédire la pertinence avant présentation.

---

# 38. Temporal Split

Lorsque suffisamment d'historique existe, un split temporel peut être préférable :

```text
past
   |
   v
TRAIN

later period
   |
   v
TEST
```

---

# 39. Class Imbalance

Le nombre de biens rejetés peut être largement supérieur au nombre de biens retenus.

Exemple :

```text
95 % rejected
5 % relevant
```

L'accuracy seule serait alors trompeuse.

---

# 40. Métriques classification

Nous mesurerons notamment :

```text
Precision
Recall
F1 Score
ROC-AUC
PR-AUC
```

selon la distribution des classes.

---

# 41. Ranking Metrics

Le problème est également un problème de ranking.

Métriques candidates :

```text
Precision@K
Recall@K
Hit Rate@K
NDCG@K
MAP
```

---

# 42. Pourquoi Precision@K

Le client ne consulte pas forcément 500 résultats.

Le système peut présenter :

```text
Top 10
```

Donc :

```text
Precision@10
```

peut être plus pertinente qu'une simple accuracy globale.

---

# 43. Business Metrics

Les métriques ML doivent être complétées par :

```text
visit rate
retention rate
time to successful match
properties reviewed per mandate
```

---

# 44. Evaluation Matrix

| Model | Precision@10 | Recall@10 | F1 | Latency | Interpretability |
|---|---:|---:|---:|---:|---|
| Rules | TBD | TBD | TBD | TBD | HIGH |
| Logistic Regression | TBD | TBD | TBD | TBD | HIGH |
| Random Forest | TBD | TBD | TBD | TBD | MEDIUM |

Les valeurs seront remplies uniquement après exécution.

---

# 45. Pas de résultats inventés

La documentation ne doit jamais annoncer :

```text
95 % accuracy
```

ou une autre métrique avant entraînement réel.

Statut actuel :

```text
TBD
```

---

# 46. MLflow

MLflow sera utilisé pour suivre les expérimentations.

Chaque run doit enregistrer :

```text
model
parameters
features
dataset version
metrics
artifacts
code version
```

---

# 47. Architecture MLflow

```text
Training Pipeline
      |
      v
MLflow Tracking
      |
      +--> parameters
      +--> metrics
      +--> artifacts
      +--> models
```

---

# 48. Experiment

Nom candidat :

```text
real-estate-matching
```

---

# 49. Run Logistic Regression

Exemple logique :

```text
Experiment:
real-estate-matching

Run:
logistic-regression-v1
```

---

# 50. Run Random Forest

```text
Experiment:
real-estate-matching

Run:
random-forest-v1
```

---

# 51. Model Comparison

Après entraînement :

```text
Rules
vs
Logistic Regression
vs
Random Forest
```

seront comparés sur le même dataset de test.

---

# 52. Model Selection

La sélection ne dépend pas uniquement :

```text
best metric
```

mais aussi :

```text
latency
resource consumption
interpretability
operational complexity
```

---

# 53. Model Registry

Le modèle sélectionné pourra être enregistré dans le registre MLflow.

Cycle :

```text
Training
   |
   v
Candidate Model
   |
   v
Evaluation
   |
   v
Registry
   |
   v
Approved Version
```

---

# 54. Promotion

Une version ne devient pas automatiquement production.

Elle doit satisfaire les critères définis.

Exemple :

```text
Precision@10 threshold
Recall@10 threshold
latency threshold
tests passed
```

---

# 55. Reproducibilité

Un run doit permettre de retrouver :

```text
dataset
features
parameters
model
metrics
code commit
```

---

# 56. Dataset Versioning

Au minimum, nous enregistrerons :

```text
dataset path/version
row count
generation timestamp
feature schema
```

Une solution spécialisée de versioning pourra être évaluée ultérieurement si nécessaire.

---

# 57. Feature Pipeline

Implémentation cible :

```text
ml/features/
```

Responsabilités :

```text
feature extraction
feature normalization
training/inference consistency
```

---

# 58. Training Pipeline

Implémentation cible :

```text
ml/training/
```

Responsabilités :

```text
dataset loading
split
training
evaluation
MLflow logging
model registration
```

---

# 59. Evaluation

Implémentation cible :

```text
ml/evaluation/
```

Responsabilités :

```text
metrics
model comparison
business evaluation
reports
```

---

# 60. Models

Artifacts et configuration :

```text
ml/models/
```

Les binaires lourds ne doivent pas nécessairement être commités dans Git.

---

# 61. API Serving

Le modèle pourra être exposé via :

```text
FastAPI
```

---

# 62. Endpoint candidat

```text
POST /api/v1/matching/rank
```

Entrée :

```json
{
  "request_version_id": 123
}
```

Sortie :

```json
{
  "request_version_id": 123,
  "model_version": "1",
  "results": [
    {
      "property_id": 501,
      "score": 0.93
    }
  ]
}
```

---

# 63. Endpoint Explain

Un endpoint ou une fonction interne pourra expliquer :

```text
why property was ranked
```

Exemple :

```text
budget match
location match
surface match
parking preference
```

---

# 64. Explainability

Pour les modèles simples :

```text
coefficients
feature importance
```

peuvent fournir une première explication.

---

# 65. LLM Role

Le LLM n'est pas le moteur principal de matching.

Il peut aider pour :

```text
free-text understanding
preference extraction
explanations
document analysis
semantic enrichment
```

---

# 66. Ollama

Les fonctions LLM peuvent utiliser le modèle local servi via :

```text
Ollama
```

Cela permet :

```text
local inference
controlled data exposure
cost control
```

---

# 67. Semantic Matching

Exemple futur :

```text
"quartier calme proche tram"
```

peut nécessiter une compréhension plus sémantique que :

```text
price <= 350000
```

---

# 68. Embeddings

Des embeddings peuvent représenter :

```text
property description
free-text preferences
documents
```

---

# 69. Vector Storage

Deux candidats :

```text
PostgreSQL + pgvector
```

et :

```text
Qdrant
```

---

# 70. Qdrant Status

Qdrant reste :

```text
CANDIDATE
```

et non dépendance obligatoire.

---

# 71. pgvector First Evaluation

Comme PostgreSQL existe déjà, une première comparaison doit considérer :

```text
pgvector
```

afin d'éviter un composant supplémentaire sans justification.

---

# 72. Vector Decision

Avant adoption :

```text
Dataset
   |
   +--> pgvector
   |
   +--> Qdrant
   |
   v
Benchmark
   |
   v
ADR
```

---

# 73. Hybrid Matching

L'architecture future peut combiner :

```text
Structured Score
+
ML Score
+
Semantic Score
```

---

# 74. Exemple

```text
final_score =
0.40 structured_score
+
0.40 ml_score
+
0.20 semantic_score
```

Ces poids ne sont qu'un exemple.

Ils devront être déterminés expérimentalement.

---

# 75. Feature Store

Un Feature Store n'est pas nécessaire pour la première version.

Il devient pertinent si nous rencontrons :

```text
many models
shared features
online/offline consistency problems
```

---

# 76. Model Monitoring

Une fois servi, le modèle doit être observé.

Métriques :

```text
inference_count
inference_latency
error_count
score_distribution
```

---

# 77. Prometheus

Le service peut exposer :

```text
matching_requests_total
matching_errors_total
matching_duration_seconds
matching_candidates_total
matching_results_total
```

---

# 78. Grafana

Dashboard candidat :

```text
Matching Service
```

avec :

```text
request rate
latency
errors
candidate count
result count
```

---

# 79. ML Monitoring

Lorsque les labels futurs deviennent disponibles :

```text
Precision@K
Recall@K
acceptance rate
```

peuvent être recalculés.

---

# 80. Drift

Types :

```text
data drift
feature drift
prediction drift
concept drift
```

---

# 81. Data Drift

Exemple :

```text
average property price
```

change fortement avec le temps.

Cela peut modifier la distribution d'une feature.

---

# 82. Concept Drift

Les préférences utilisateurs peuvent évoluer.

Un modèle entraîné sur un historique ancien peut devenir moins pertinent.

---

# 83. Retraining

Le retraining ne doit pas nécessairement être automatique au début.

Processus :

```text
Drift / Performance Alert
        |
        v
Analysis
        |
        v
Retrain
        |
        v
Evaluate
        |
        v
Promote
```

---

# 84. Airflow ML Pipeline

DAG candidat :

```text
matching_model_training
```

---

# 85. DAG

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
             select_model
                  |
                  v
             log_mlflow
                  |
                  v
         register_candidate
```

---

# 86. CI Validation

Avant merge :

```text
unit tests
feature tests
lint
security scan
```

doivent passer.

---

# 87. Model Training in CI

Le pipeline CI ne doit pas forcément effectuer un entraînement complet.

Il peut exécuter :

```text
small training smoke test
```

sur un dataset réduit.

---

# 88. Full Training

Le vrai entraînement peut être exécuté via :

```text
Airflow
manual controlled pipeline
scheduled training
```

selon la stratégie retenue.

---

# 89. Security

Le modèle ne doit pas recevoir automatiquement :

```text
client email
telephone
full identity
```

pour effectuer le matching.

---

# 90. Data Minimization

Features préférées :

```text
budget
location
property criteria
preferences
feedback
```

plutôt que données personnelles non nécessaires.

---

# 91. Documents

Les documents utilisés pour une éventuelle couche RAG doivent respecter :

```text
indexable_ia = TRUE
```

---

# 92. Prompt Injection

Les documents externes doivent être considérés comme :

```text
untrusted content
```

Ils ne doivent pas pouvoir modifier les règles système.

---

# 93. Human Oversight

Le modèle :

```text
recommends
```

mais ne remplace pas automatiquement :

```text
client
hunter
```

pour les décisions importantes.

---

# 94. Feedback

Le feedback humain doit être conservé afin de :

```text
explain decisions
improve matching
create future labels
```

---

# 95. Bias

Le modèle doit éviter d'utiliser des variables non pertinentes ou sensibles pour le matching.

Le matching doit être fondé sur :

```text
property requirements
business criteria
explicit preferences
```

---

# 96. Model Card

Chaque modèle promu doit disposer d'une Model Card.

---

# 97. Model Card Content

```text
Model Name
Version
Purpose
Algorithm
Training Dataset
Features
Target
Metrics
Limitations
Known Risks
Owner
Deployment Status
```

---

# 98. Limitation Example

```text
Model trained primarily
on synthetic / generated data
```

doit être explicitement documenté si c'est le cas.

---

# 99. Synthetic Data

Le générateur StarterPack permet de construire des datasets techniques.

Mais les données synthétiques ne prouvent pas automatiquement la performance sur des utilisateurs réels.

---

# 100. Validation Strategy

Nous distinguons :

```text
Technical Validation
```

et :

```text
Business Validation
```

---

# 101. Technical Validation

```text
pipeline works
features valid
model reproducible
metrics calculated
API serves predictions
```

---

# 102. Business Validation

```text
ranking useful
recommendations coherent
hunter accepts results
client feedback positive
```

Cette partie nécessite idéalement des données ou retours réels.

---

# 103. Performance Benchmark

Nous mesurerons :

```text
candidate count
feature extraction time
model inference time
total ranking time
memory
CPU
GPU if used
```

---

# 104. Rules Benchmark

La baseline rules fournit la référence de performance.

---

# 105. Logistic Regression Benchmark

Mesurer :

```text
training duration
inference latency
metrics
model size
```

---

# 106. Random Forest Benchmark

Même méthodologie :

```text
training duration
inference latency
metrics
model size
```

---

# 107. LLM Benchmark

Si un enrichissement LLM est utilisé :

```text
tokens
latency
GPU utilization
throughput
```

doivent être mesurés séparément.

---

# 108. Scaling

Le système ne doit pas exécuter le modèle sur tous les biens de la plateforme sans préfiltrage.

Architecture :

```text
Database Filters
      |
      v
Candidate Reduction
      |
      v
ML Ranking
```

---

# 109. Top-K

Le système retourne principalement :

```text
Top-K
```

résultats.

Exemple :

```text
Top 10
Top 20
```

selon le workflow métier.

---

# 110. Persisted Result

Les résultats retenus peuvent alimenter :

```text
real_estate.presentation
```

avec :

```text
score_matching
```

---

# 111. Model Traceability

À terme, `PRESENTATION` pourrait également conserver :

```text
model_name
model_version
scoring_timestamp
```

si la traçabilité réglementaire ou opérationnelle le justifie.

---

# 112. Recommandation V2

Cette extension est intéressante pour le projet.

Exemple futur :

```text
presentation
│
├── score_matching
├── scoring_method
├── model_name
└── model_version
```

Cette modification doit être intégrée au MCD/MLD/MPD avant implémentation si elle est retenue comme donnée métier persistante.

---

# 113. Scoring Method

Valeurs candidates :

```text
RULES
ML
HYBRID
```

Cela permet de comparer les performances des différentes générations du moteur.

---

# 114. Champion / Challenger

Une évolution MLOps possible :

```text
Champion
vs
Challenger
```

Le challenger est évalué avant de remplacer le modèle actif.

---

# 115. Rollback

Le registre doit permettre de revenir à une version précédente si :

```text
new model performs worse
```

ou :

```text
runtime problems appear
```

---

# 116. GitOps

Le déploiement du service de matching suit :

```text
Git
 |
 v
GitLab CI
 |
 v
Container Registry
 |
 v
GitOps repository
 |
 v
Argo CD
 |
 v
Kubernetes
```

---

# 117. Kubernetes

Le service peut être déployé comme :

```text
Deployment
Service
Ingress
ConfigMap
Secret
```

---

# 118. Health Endpoints

Le service expose :

```text
/health
/ready
```

---

# 119. Model Loading

Le service ne doit pas télécharger arbitrairement un modèle non validé.

Il charge une version explicitement approuvée.

---

# 120. Failure Mode

Si le modèle ML est indisponible, une stratégie possible est :

```text
fallback to deterministic rules
```

selon les exigences de disponibilité.

---

# 121. Architecture finale cible

```text
                  DEMANDE_VERSION
                         |
                         v
                  Structured Filters
                         |
                         v
                       BIEN
                         |
                         v
                  Candidate Dataset
                         |
              +----------+----------+
              |                     |
              v                     v
       Rules Baseline          ML Model
              |                     |
              +----------+----------+
                         |
                         v
                  Hybrid Ranking
                         |
                         v
                      Top-K
                         |
                         v
                   PRESENTATION
                         |
                         v
                     Feedback
                         |
                         v
                 Training Dataset
                         |
                         v
                     MLflow
```

---

# 122. Implementation Structure

L'implémentation actuelle se trouve dans `src/ai/matching/`. Les répertoires `ml/` ci-dessous décrivent l'organisation cible initiale ; ils ne doivent pas masquer les modules réellement présents.

```text
src/ai/matching/
├── repository.py
├── features.py
├── training_dataset.py
├── dataset_split.py
├── model_training.py
├── evaluate.py
├── model_comparison.py
└── mlflow_tracking.py
```

L'API utilise `src/api/services/recommendation.py`. Les tests sont dans `tests/ai/` et `tests/backend/`.

Organisation cible historique :

```text
ml/
├── features/
├── training/
├── evaluation/
└── models/
```

Application code:

```text
src/
├── ai/
├── api/
├── domain/
└── services/
```

---

# 123. Tests

Tests prévus :

```text
feature calculation
missing values
hard filtering
baseline scoring
model loading
model prediction
ranking order
API contract
fallback
```

---

# 124. Evidence

## Baseline actuellement utilisée

Le repository sélectionne les biens actifs compatibles avec les critères obligatoires. Les features puis le score pondéré produisent le classement utilisé par l'API de recommandations.

```text
DemandeVersion
      |
      v
Biens éligibles
      |
      v
Features / score déterministe
      |
      v
Classement
      |
      v
Présentations / audit
```

Le rapport du 9 septembre 2026 documente une recommandation persistée et auditée. Ce résultat démontre le fonctionnement du baseline ; il ne correspond pas à une prédiction de régression logistique.

## Dataset et apprentissage implémentés

Le dataset actuel associe une version de demande à des candidats. Les labels proviennent de la traçabilité du générateur : `source_recherche_ref`, correspondance dans `staging.annonces` et référence du bien.

Cette provenance sert à construire la cible et ne doit pas entrer dans les features ou la sélection des candidats.

Les sept features du dataset d'entraînement portent sur :

```text
Localisation
Budget
Type de bien
Surface
Pièces
Chambres
DPE
```

Le split est réalisé par groupe `id_demande_version`. Le module d'entraînement utilise `LogisticRegression`, puis calcule les métriques sur les partitions séparées. Le module de comparaison confronte le modèle au baseline et l'intégration MLflow permet de journaliser les résultats.

Les labels synthétiques démontrent le fonctionnement du programme. Ils ne prouvent pas que le modèle prédit l'intérêt de clients réels. La stratégie de feedback métier décrite plus haut reste une évolution distincte.

## Sources et limites

```text
../../../50-AI/11-Matching-Baseline-Implementation.md
../../../50-AI/12-Labelled-Dataset-Strategy.md
../../../60-SECURITY/RECOMMENDATION-AUDIT-RUNTIME-EVIDENCE.md
../../03-BC03/C6-Tests-Executes/script-review-2026-09-09/review-tests.xml
```

Les tests IA font partie de la campagne locale de 217 tests décrite dans la revue du 9 septembre. Aucun gain métier, modèle promu ni Random Forest entraîné n'est déduit de cette campagne. La revue de scripts conserve notamment une réserve sur la validation des labels fractionnaires lors du split ; cette réserve doit être traitée avant de déclarer le contrôle exhaustif.

Les preuves finales devront inclure :

```text
training code
feature code
dataset description
MLflow experiment
actual metrics
model comparison
Model Card
registered model
API prediction
monitoring
```

---

# 125. Evidence Location

Implementation :

```text
ml/
src/ai/
src/api/
```

Tests :

```text
tests/ai/
tests/backend/
```

Documentation :

```text
docs/evidence/05-BC05/C5-Modele-Matching-IA/
```

---

# 126. Minimum Certification Evidence

Même sans l'extension ML, les preuves doivent démontrer :

```text
problem definition
features
data structure
target strategy
evaluation strategy
matching architecture
```

---

# 127. Additional Project Evidence

Notre extension ajoutera :

```text
trained models
actual experiment runs
actual metrics
MLflow tracking
model registry
serving
monitoring
```

---

# 128. Important Distinction

La soutenance doit présenter clairement :

```text
What was required
```

et :

```text
What we implemented beyond the minimum
```

Cela évite de présenter une extension volontaire comme une contrainte imposée.

---

# 129. Current Status

| Élément | Statut |
|---|---|
| Matching problem | DEFINED |
| Input model | V2 ALIGNED |
| Structured features | IMPLEMENTED |
| Preference features | DEFINED |
| Hard filtering | IMPLEMENTED |
| Rule baseline | IMPLEMENTED / TESTED |
| Label strategy | DEFINED |
| Logistic Regression | IMPLEMENTED / UNIT TESTS AVAILABLE |
| Random Forest | PLANNED |
| Ranking metrics | IMPLEMENTED |
| MLflow | TRACKING CODE IMPLEMENTED / RUNS TO LINK |
| Model Registry | PLANNED |
| Model Card | DEFINED |
| FastAPI serving | DETERMINISTIC BASELINE IMPLEMENTED / ML SERVING PENDING |
| Monitoring | RECOMMENDATION METRICS IMPLEMENTED |
| Semantic enrichment | FUTURE / EXPERIMENTAL |
| pgvector/Qdrant comparison | FUTURE |
| Runtime training | PENDING |
| Runtime metrics | PENDING |
| Runtime serving evidence | DETERMINISTIC RECOMMENDATION REPORT AVAILABLE |

---

# 130. Conclusion

Le moteur de matching adopte une architecture progressive :

```text
STRUCTURED FILTERING
        |
        v
RULE-BASED BASELINE
        |
        v
MACHINE LEARNING
        |
        v
OPTIONAL SEMANTIC ENRICHMENT
```

Cette stratégie évite de transformer inutilement chaque problème métier en problème LLM.

Le projet va volontairement au-delà de la conception minimale en implémentant :

```text
Logistic Regression
+
Random Forest
+
MLflow
+
Model Registry
+
Model Card
+
FastAPI Serving
+
Observability
```

La valeur de cette extension sera démontrée par des résultats réellement mesurés et non par des métriques théoriques.

---

**BC05 / C5 — MODÈLE DE MATCHING IA V2 — WITH ML/MLOPS EXTENSION**
