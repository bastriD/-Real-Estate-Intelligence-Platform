# BC05 — C5 — Modèle de Matching IA

**Bloc de compétences :** BC05  
**Compétence :** C5 — Concevoir, entraîner, évaluer et exploiter un modèle de traitement / matching IA  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Version :** 1.0  
**Statut :** Baseline documentaire — modèle et preuves expérimentales à produire

---

# 1. Objectif

Ce dossier décrit la stratégie de matching entre :

```text
Demande immobilière client
            |
            v
      Matching Engine
            |
            v
        Biens candidats
            |
            v
      Score / Ranking
            |
            v
       Présentation
```

L'objectif n'est pas d'utiliser de l'IA simplement parce que le projet possède une plateforme IA.

Le système doit utiliser le mécanisme le plus simple, explicable et mesurable permettant de satisfaire le besoin métier.

---

# 2. Problème métier

Un chasseur immobilier doit identifier les biens correspondant le mieux à une demande.

Une demande peut contenir :

```text
Localisation
Budget
Surface
Nombre de pièces
Type de bien
Critères obligatoires
Critères souhaités
Description libre
Préférences
Contraintes
```

Les sources immobilières peuvent fournir :

```text
Prix
Surface
Localisation
Nombre de pièces
Type
Description
Équipements
Caractéristiques
```

Le système doit rapprocher ces deux ensembles.

---

# 3. Objectif fonctionnel

À partir d'une demande :

```text
D
```

et d'un ensemble de biens :

```text
B1 ... Bn
```

le système produit :

```text
score(D, Bi)
```

puis classe les biens :

```text
B7     94
B23    89
B12    84
B4     72
...
```

---

# 4. Architecture de matching

L'architecture cible est hybride.

```text
All Properties
      |
      v
Hard SQL Filters
      |
      v
Candidate Properties
      |
      v
Deterministic Scoring
      |
      v
Candidate Ranking
      |
      v
Optional ML / Semantic Analysis
      |
      v
Final Ranking
      |
      v
Human Validation
```

---

# 5. Pourquoi une approche hybride

Toutes les règles ne nécessitent pas du Machine Learning.

Exemple :

```text
budget_max = 350000
```

peut être évalué directement en SQL.

Il serait inutile d'utiliser un LLM pour déterminer si :

```text
420000 > 350000
```

---

# 6. Principe

Le système applique :

```text
Deterministic where possible
AI where useful
Human validation where necessary
```

---

# 7. Hard Constraints

Les contraintes obligatoires peuvent éliminer directement un bien.

Exemples :

```text
maximum budget
minimum surface
mandatory city
mandatory property type
```

Architecture :

```text
100,000 properties
        |
        v
Hard Filters
        |
        v
2,500 candidates
```

Le nombre exact dépendra des données réelles.

---

# 8. Soft Constraints

Les préférences non obligatoires peuvent contribuer au score.

Exemples :

```text
balcony preferred
quiet area preferred
near public transport
south-facing
parking preferred
```

Un bien peut ne pas satisfaire une préférence tout en restant pertinent.

---

# 9. Critères structurés

Les critères structurés peuvent être comparés directement.

Exemple :

```text
Request:
budget_max = 350000

Property:
price = 320000
```

Résultat :

```text
Budget criterion satisfied
```

---

# 10. Critères non structurés

Une demande peut contenir :

```text
"Je recherche un appartement lumineux,
calme, proche du tram et adapté au télétravail."
```

Ces critères sont plus difficiles à traiter avec uniquement :

```text
SQL equality
```

Ils constituent un candidat pour une analyse sémantique.

---

# 11. Sources du matching

Le matching exploite principalement :

```text
DEMANDE_VERSION
```

et :

```text
BIEN
```

Le résultat peut être matérialisé dans :

```text
PRESENTATION
```

---

# 12. Version de demande

Le matching doit utiliser une version déterminée de la demande.

```text
MANDAT
   |
   +--> DEMANDE_VERSION 1
   |
   +--> DEMANDE_VERSION 2
```

Un score calculé pour la version 1 ne doit pas être présenté comme ayant été calculé pour la version 2.

---

# 13. Reproductibilité

Un résultat de matching doit idéalement permettre d'identifier :

```text
Request Version
Property Version / State
Algorithm Version
Model Version
Configuration
Timestamp
```

---

# 14. Pipeline logique

```text
Request
   |
   v
Validation
   |
   v
Structured Filtering
   |
   v
Feature Computation
   |
   v
Scoring
   |
   v
Ranking
   |
   v
Optional AI Enrichment
   |
   v
Business Validation
```

---

# 15. Étape 1 — Validation

Avant matching, vérifier :

```text
budget_min <= budget_max
surface_min >= 0
valid property type
valid location
mandatory fields present
```

Une entrée invalide ne doit pas être transmise silencieusement au modèle.

---

# 16. Étape 2 — SQL Filtering

Exemple :

```sql
SELECT
    id_bien,
    prix,
    surface,
    nb_pieces,
    ville,
    type_bien
FROM real_estate.bien
WHERE statut = 'ACTIF'
  AND ville = :ville
  AND prix <= :budget_max
  AND surface >= :surface_min;
```

Cette étape réduit l'espace de recherche.

---

# 17. Étape 3 — Feature Engineering

Les données métier doivent être transformées en variables utilisables.

Exemples :

```text
price_difference
surface_difference
room_difference
location_match
property_type_match
budget_ratio
surface_ratio
```

---

# 18. Exemple price_difference

```text
budget_target = 300000
property_price = 285000

price_difference = 15000
```

Une version normalisée peut être utilisée.

---

# 19. Budget Score

Exemple conceptuel :

```text
property <= target budget
        |
        v
high score
```

Plus l'écart devient défavorable, plus le score peut diminuer.

La formule exacte devra être testée.

---

# 20. Surface Score

Exemple :

```text
requested = 80 m²
property = 82 m²
```

doit généralement produire un meilleur résultat que :

```text
property = 45 m²
```

si la surface est importante pour le client.

---

# 21. Location Score

La localisation peut être évaluée à plusieurs niveaux :

```text
Exact city
Postal code
Area
Distance
Coordinates
Travel time
```

Le MVP peut commencer avec une comparaison simple avant d'introduire une logique géospatiale.

---

# 22. PostgreSQL / PostGIS

Si les besoins géographiques deviennent plus avancés, PostGIS pourra être évalué pour :

```text
distance
radius
geospatial filtering
```

Il ne doit être introduit que si le besoin le justifie.

---

# 23. Criteria Score

Les critères supplémentaires peuvent produire un score :

```text
criteria_matched
----------------
criteria_requested
```

avec pondération éventuelle.

---

# 24. Score global

Un score déterministe peut suivre une formule de type :

```text
Score =
    w1 * budget_score
  + w2 * location_score
  + w3 * surface_score
  + w4 * type_score
  + w5 * criteria_score
```

avec :

```text
w1 + w2 + w3 + w4 + w5 = 1
```

---

# 25. Exemple

Exemple uniquement illustratif :

```text
Budget      90
Location   100
Surface     80
Type       100
Criteria    70
```

avec pondérations :

```text
Budget      0.30
Location    0.25
Surface     0.20
Type        0.10
Criteria    0.15
```

Le score final est calculable et explicable.

Les valeurs définitives ne sont pas encore adoptées.

---

# 26. Pondération

Les poids peuvent être :

```text
global defaults
```

ou éventuellement adaptés selon les priorités client.

Exemple :

```text
Budget:
MANDATORY

Balcony:
PREFERRED
```

ne doivent pas nécessairement avoir la même influence.

---

# 27. Explainability

Le système ne doit pas uniquement retourner :

```text
87
```

Il doit pouvoir expliquer :

```text
Overall score: 87/100

Budget:       95
Location:    100
Surface:      80
Type:        100
Preferences:  65
```

---

# 28. Pourquoi l'explicabilité est importante

Elle permet :

- validation métier ;
- compréhension utilisateur ;
- debugging ;
- amélioration ;
- audit ;
- gouvernance IA.

---

# 29. Human-in-the-loop

Le modèle ne remplace pas nécessairement le chasseur immobilier.

Architecture :

```text
AI / Matching
      |
      v
Recommendation
      |
      v
Real Estate Professional
      |
      v
Validation
      |
      v
Client
```

---

# 30. Feedback

Le retour métier/client constitue une source de données importante.

Exemples :

```text
Presented
Rejected
Visited
Retained
Purchased
```

Ces résultats peuvent servir à évaluer le matching.

---

# 31. Feedback Loop

```text
Matching
   |
   v
Presentation
   |
   v
Client Feedback
   |
   v
Historical Dataset
   |
   v
Model Evaluation / Improvement
```

---

# 32. Baseline

Avant de créer un modèle ML, une baseline déterministe doit être construite.

Exemple :

```text
Weighted rules-based scoring
```

Elle fournit un point de comparaison.

---

# 33. Pourquoi une baseline

Sans baseline, il est impossible de démontrer qu'un modèle ML apporte réellement une amélioration.

La question doit être :

```text
Does ML outperform the simpler solution?
```

---

# 34. Dataset ML

Un futur dataset d'apprentissage peut contenir :

```text
request features
property features
matching features
business feedback
target
```

---

# 35. Target

Une cible possible pourrait être :

```text
0 = rejected
1 = relevant
```

ou plusieurs classes :

```text
REJECTED
INTERESTED
VISITED
RETAINED
```

Le choix dépendra des données disponibles.

---

# 36. Limitation initiale

Le projet peut ne pas disposer immédiatement d'un volume suffisant de feedback réel pour entraîner un modèle supervisé fiable.

Cette limitation doit être explicitement documentée.

---

# 37. Données synthétiques

Des données synthétiques peuvent être utilisées pour démontrer techniquement :

```text
training
tracking
evaluation
deployment pipeline
```

mais elles ne prouvent pas la performance métier réelle du modèle.

---

# 38. Séparation importante

Il faut distinguer :

```text
Technical ML pipeline validation
```

de :

```text
Business model validation
```

Un modèle entraîné sur données synthétiques peut valider la plateforme MLOps sans démontrer une valeur commerciale réelle.

---

# 39. Modèles candidats

Pour des features principalement tabulaires, des modèles candidats simples sont :

```text
Logistic Regression
Decision Tree
Random Forest
Gradient Boosting
```

Un réseau neuronal n'est pas automatiquement nécessaire.

---

# 40. Baseline ML

Une première expérimentation peut comparer :

```text
Rules-based
vs
Logistic Regression
vs
Random Forest
```

---

# 41. Métriques de classification

Selon la cible :

```text
Accuracy
Precision
Recall
F1-score
ROC-AUC
```

peuvent être utilisées.

---

# 42. Accuracy

L'accuracy seule peut être trompeuse en cas de classes déséquilibrées.

Exemple :

```text
95% rejected
5% retained
```

Un modèle retournant toujours :

```text
rejected
```

aurait 95 % d'accuracy mais aucune utilité.

---

# 43. Precision

La precision répond approximativement à :

```text
Among properties predicted relevant,
how many actually were relevant?
```

---

# 44. Recall

Le recall répond approximativement à :

```text
Among actually relevant properties,
how many did the model find?
```

---

# 45. Trade-off métier

Dans la chasse immobilière, manquer un excellent bien peut être coûteux.

Le recall peut donc avoir une importance particulière.

Mais présenter trop de biens inutiles réduit également la valeur du service.

Il faut équilibrer :

```text
Precision
vs
Recall
```

---

# 46. Ranking

Le problème peut également être considéré comme un problème de classement :

```text
Rank the most relevant properties first.
```

Des métriques de ranking pourront être étudiées si les données le permettent.

---

# 47. Top-K

Une métrique métier simple peut être :

```text
Relevant property present in Top 5?
```

ou :

```text
Top 10?
```

---

# 48. Semantic Matching

Les descriptions textuelles peuvent bénéficier d'embeddings.

Architecture :

```text
Request text
     |
     v
Embedding
     |
     +----------------+
                      |
Property description |
     |                |
     v                |
Embedding             |
     |                |
     +-------+--------+
             |
             v
     Similarity Score
```

---

# 49. Embeddings

Un embedding représente du texte sous forme de vecteur numérique.

Il permet de comparer une proximité sémantique plutôt qu'une simple égalité de mots.

---

# 50. Exemple

Demande :

```text
"proche du tram"
```

Annonce :

```text
"station de tramway située à 3 minutes à pied"
```

Une recherche par égalité textuelle peut échouer alors qu'une recherche sémantique peut détecter la proximité de sens.

---

# 51. Vector Store

Deux approches sont envisagées :

```text
PostgreSQL + pgvector
```

ou éventuellement :

```text
Qdrant
```

Qdrant reste actuellement :

```text
CANDIDATE
```

et non une dépendance obligatoire.

---

# 52. Choix vectoriel

Avant adoption :

```text
Dataset
   |
   +--> pgvector benchmark
   |
   +--> Qdrant benchmark
   |
   v
Comparison
   |
   v
ADR
```

---

# 53. Similarity

Une métrique candidate est :

```text
Cosine Similarity
```

mais le choix dépend du modèle d'embedding utilisé.

---

# 54. Hybrid Search

Une architecture intéressante combine :

```text
SQL filters
+
structured scoring
+
semantic similarity
```

Exemple :

```text
SQL:
Montpellier
<= 350k
>= 70m²

        |
        v

Semantic:
quiet
bright
near tram
```

---

# 55. Pourquoi Hybrid Search

Cela évite d'utiliser la recherche vectorielle pour des contraintes exactes.

```text
Structured constraints
       |
       v
SQL
```

```text
Semantic preferences
       |
       v
Embeddings
```

---

# 56. LLM

Le LLM local peut être utilisé pour certaines tâches spécifiques.

Exemples :

```text
extract criteria from free text
summarize property
explain match
normalize user request
```

---

# 57. Ollama

Le projet prévoit :

```text
Ollama
```

pour l'inférence LLM locale.

L'objectif est notamment :

- expérimentation ;
- contrôle local ;
- souveraineté ;
- limitation des transferts externes.

---

# 58. LLM non utilisé pour tout

À éviter :

```text
LLM decides everything
```

Un LLM n'est pas nécessaire pour :

```text
price comparison
surface comparison
exact type
database joins
```

---

# 59. Structured Output

Lorsqu'un LLM extrait des critères, le résultat doit être structuré.

Exemple :

```json
{
  "city": "Montpellier",
  "budget_max": 350000,
  "surface_min": 70,
  "preferences": [
    "tram",
    "quiet",
    "bright"
  ]
}
```

---

# 60. Validation après LLM

Une sortie LLM ne doit pas être considérée comme valide simplement parce qu'elle est syntaxiquement correcte.

Flux :

```text
LLM output
   |
   v
Schema Validation
   |
   v
Business Validation
   |
   v
Accepted Data
```

---

# 61. Pydantic

Pydantic peut valider les structures extraites avant utilisation par l'application.

---

# 62. Hallucination

Le LLM peut produire une information non présente dans la source.

Il ne doit donc pas inventer :

```text
property price
surface
address
diagnostic
legal information
```

---

# 63. Grounding

Les explications générées doivent être fondées sur les données disponibles.

```text
Database / Documents
        |
        v
Context
        |
        v
LLM
        |
        v
Grounded Explanation
```

---

# 64. RAG

RAG signifie :

```text
Retrieval-Augmented Generation
```

Il peut être utilisé lorsque l'IA doit répondre à partir de documents ou données de référence.

---

# 65. RAG et matching

RAG n'est pas automatiquement le moteur principal de matching.

Il peut compléter le système pour :

- documents ;
- descriptions longues ;
- contexte métier ;
- justification.

---

# 66. MLflow

MLflow est utilisé pour assurer la traçabilité des expérimentations ML.

Il peut enregistrer :

```text
parameters
metrics
artifacts
model versions
```

---

# 67. Exemple d'expérience

```text
Experiment:
real-estate-matching

Run:
random-forest-v1

Parameters:
n_estimators
max_depth
random_state

Metrics:
precision
recall
f1
```

---

# 68. Version du modèle

Chaque modèle exploité doit être identifiable.

```text
Model
  |
  +--> Version 1
  +--> Version 2
  +--> Version 3
```

---

# 69. Artifact

Le modèle entraîné doit être associé à son artifact.

Il faut pouvoir répondre :

```text
Which artifact corresponds to this model version?
```

---

# 70. Dataset traceability

Une expérience devrait également identifier le dataset utilisé.

```text
Model Version
      |
      +--> Code version
      +--> Dataset version
      +--> Parameters
      +--> Metrics
      +--> Artifact
```

---

# 71. Reproductibilité ML

Idéalement :

```text
Git commit
+
Dataset reference
+
Environment
+
Parameters
+
Random seed
```

permettent de reproduire l'expérience autant que possible.

---

# 72. Airflow

Airflow peut orchestrer :

```text
prepare dataset
      |
      v
train
      |
      v
evaluate
      |
      v
log to MLflow
      |
      v
quality gate
```

---

# 73. Séparation Airflow / MLflow

```text
Airflow
=
workflow orchestration
```

```text
MLflow
=
experiment/model lifecycle tracking
```

Les responsabilités restent distinctes.

---

# 74. Quality Gate

Un nouveau modèle ne doit pas être promu uniquement parce que l'entraînement s'est terminé.

Exemple :

```text
New Model
   |
   v
Evaluation
   |
   v
Metrics >= threshold?
   |
   +--> NO --> Reject
   |
   +--> YES --> Candidate
```

---

# 75. Comparaison avec baseline

Le quality gate doit idéalement comparer :

```text
candidate model
```

à :

```text
current baseline / production model
```

---

# 76. Promotion

Une promotion peut suivre :

```text
Experiment
   |
   v
Candidate
   |
   v
Validation
   |
   v
Approved
   |
   v
Deployment
```

---

# 77. Human Approval

Pour le MVP, la promotion d'un modèle peut nécessiter une validation humaine.

Cela réduit le risque d'un déploiement automatique d'un modèle dégradé.

---

# 78. Serving

MLflow n'est pas obligatoirement le serveur d'inférence final.

Le modèle peut être chargé dans :

```text
FastAPI service
```

pour fournir une API contrôlée.

---

# 79. API candidate

Exemple :

```text
POST /api/v1/matching
```

Entrée :

```text
request_version_id
```

Sortie :

```text
ranked properties
scores
explanations
model version
```

---

# 80. Exemple de résultat

```json
{
  "request_version_id": 42,
  "model_version": "rules-v1",
  "results": [
    {
      "property_id": 1004,
      "score": 91.2,
      "rank": 1
    }
  ]
}
```

---

# 81. Model Metadata

Une réponse peut inclure :

```text
algorithm_version
model_version
generated_at
```

pour améliorer la traçabilité.

---

# 82. Tests unitaires

Les fonctions de scoring déterministe doivent être testables indépendamment.

Exemples :

```text
budget score
surface score
location score
weight calculation
```

---

# 83. Test — budget

Exemple conceptuel :

```text
budget_max = 300000
property = 250000

expected:
accepted
```

---

# 84. Test — hard rejection

```text
mandatory city = Montpellier
property city = Lyon
```

si la ville est une contrainte stricte :

```text
expected:
filtered out
```

---

# 85. Test — score boundaries

Le score doit respecter :

```text
0 <= score <= 100
```

si cette échelle est retenue.

---

# 86. Tests d'intégration

Tester :

```text
PostgreSQL
      |
      v
Matching Service
      |
      v
Result
```

avec un dataset connu.

---

# 87. Golden Dataset

Un petit dataset validé manuellement peut servir de référence.

Exemple :

```text
Request A
Property 1 -> excellent
Property 2 -> medium
Property 3 -> reject
```

Le système doit reproduire un classement cohérent.

---

# 88. Pourquoi un Golden Dataset

Il facilite :

- tests de régression ;
- validation métier ;
- comparaison d'algorithmes ;
- démonstration.

---

# 89. Evaluation Offline

Avant déploiement :

```text
historical dataset
       |
       v
candidate model
       |
       v
metrics
```

---

# 90. Evaluation Online

Une évolution future peut comparer le comportement réel après déploiement.

Exemples :

```text
acceptance rate
visit rate
retention rate
```

---

# 91. Model Drift

Avec le temps :

```text
market changes
client behavior changes
sources change
```

Le modèle peut perdre en pertinence.

C'est le :

```text
Model Drift
```

---

# 92. Data Drift

La distribution des entrées peut également changer.

Exemple :

```text
average property price
```

augmente fortement.

Il faut distinguer :

```text
Data Drift
```

et :

```text
Model Performance Drift
```

---

# 93. Monitoring

Une évolution MLOps doit observer :

```text
request count
latency
errors
score distribution
model version
prediction distribution
```

et, lorsque les labels sont disponibles :

```text
business performance
```

---

# 94. Prometheus

Le service peut exposer des métriques telles que :

```text
matching_requests_total
matching_errors_total
matching_duration_seconds
matching_candidates_count
```

---

# 95. Grafana

Grafana peut visualiser :

```text
Matching request rate
Latency
Errors
Candidate count
Model version usage
```

---

# 96. Logs

Les logs doivent permettre le diagnostic sans exposer inutilement des données personnelles.

À éviter :

```text
full client request
full personal profile
```

dans des logs généraux.

---

# 97. Security

Le service de matching doit respecter :

```text
authentication
authorization
input validation
rate limiting where needed
secret management
```

---

# 98. RGPD

Le matching peut constituer un traitement de données personnelles.

Il doit donc respecter :

```text
Purpose limitation
Data minimization
Retention
Access control
Traceability
```

---

# 99. Automated Decision Making

Le système doit clairement documenter le niveau d'autonomie.

Pour le MVP :

```text
Decision Support
```

plutôt que :

```text
Fully autonomous consequential decision
```

Le chasseur conserve une validation métier.

---

# 100. Biais

Un modèle peut reproduire ou amplifier des biais présents dans les données.

Les variables utilisées doivent être examinées.

Une feature n'est pas acceptable uniquement parce qu'elle améliore une métrique.

---

# 101. Features sensibles

Les données non nécessaires au matching immobilier ne doivent pas être utilisées.

Le principe est :

```text
Use business-relevant features only.
```

---

# 102. Explainable recommendation

Une recommandation doit pouvoir être formulée comme :

```text
Strong match because:

+ budget satisfied
+ requested city
+ surface above minimum
+ correct property type

Partial match:

- no parking information
```

plutôt qu'une justification inventée.

---

# 103. Souveraineté IA

Lorsque possible, les traitements sensibles peuvent rester sur l'infrastructure locale.

Architecture :

```text
Private Data
    |
    v
Local Platform
    |
    v
Ollama / Local Model
```

Les transferts externes doivent être contrôlés.

---

# 104. Performance

Le matching doit être évalué selon deux dimensions :

```text
Model quality
```

et :

```text
System performance
```

Un excellent modèle prenant plusieurs minutes par bien peut être inutilisable.

---

# 105. Latency Pipeline

```text
SQL filtering
+
feature computation
+
model inference
+
optional LLM
=
total latency
```

Chaque partie doit pouvoir être mesurée.

---

# 106. Batch Matching

Le matching peut être exécuté en batch après :

```text
new properties imported
```

ou :

```text
request updated
```

---

# 107. Interactive Matching

Une API peut également déclencher un matching à la demande.

Le choix dépend du besoin fonctionnel.

---

# 108. Cache

Certains résultats peuvent éventuellement être mis en cache lorsque :

```text
request unchanged
+
property data unchanged
+
algorithm unchanged
```

Mais l'invalidation doit être maîtrisée.

---

# 109. Version de l'algorithme

Même un moteur déterministe doit être versionné.

Exemple :

```text
rules-v1
rules-v2
```

Une modification des pondérations peut modifier les résultats.

---

# 110. Auditability

Pour un résultat important, nous devons pouvoir retrouver :

```text
request version
property
algorithm/model version
score
score components
timestamp
```

---

# 111. Data Model Evolution

La table `PRESENTATION` pourra éventuellement stocker ou référencer :

```text
algorithm_version
model_version
```

si la traçabilité métier le nécessite.

La modification exacte du MPD devra être décidée avant implémentation.

---

# 112. Evidence Runtime

Les preuves finales pourront inclure :

```text
dataset
training script
matching code
unit tests
evaluation report
MLflow run
MLflow model version
API response
Prometheus metrics
Airflow execution
```

---

# 113. Structure future

```text
C5-Modele-Matching-IA/
│
├── README.md
│
├── baseline/
│   ├── scoring.py
│   └── weights.yaml
│
├── dataset/
│   └── ...
│
├── training/
│   └── train.py
│
├── evaluation/
│   └── evaluate.py
│
├── tests/
│   └── test_matching.py
│
├── evidence/
│   ├── mlflow-run.png
│   ├── model-metrics.txt
│   ├── api-result.json
│   └── test-results.txt
│
└── EVALUATION-REPORT.md
```

Ces fichiers seront créés pendant l'implémentation.

---

# 114. Expériences prévues

Au minimum :

```text
Experiment 1
Rules-based baseline

Experiment 2
Simple ML model

Experiment 3
Alternative ML model
```

si un dataset adapté peut être produit.

---

# 115. Comparaison

Le rapport devra présenter :

| Modèle | Precision | Recall | F1 | Latency | Explainability |
|---|---:|---:|---:|---:|---|
| Rules baseline | À mesurer | À mesurer | À mesurer | À mesurer | Forte |
| Logistic Regression | À mesurer | À mesurer | À mesurer | À mesurer | Forte/modérée |
| Random Forest | À mesurer | À mesurer | À mesurer | À mesurer | Modérée |

Aucune valeur ne doit être inventée.

---

# 116. Critères de sélection

Le meilleur modèle n'est pas nécessairement celui avec le score ML maximal.

La décision doit considérer :

```text
Business relevance
Precision / Recall
Latency
Explainability
Operational complexity
Resource consumption
Maintainability
```

---

# 117. Decision Matrix

Exemple :

```text
Accuracy improvement: +1%
Infrastructure complexity: +200%
```

peut ne pas justifier l'adoption d'un modèle plus complexe.

---

# 118. Model Card

Le modèle final devra disposer d'une fiche contenant :

```text
Purpose
Version
Training data
Features
Metrics
Limitations
Known risks
Intended use
Non-intended use
Owner
```

---

# 119. Limites

Le système devra explicitement documenter :

```text
insufficient historical labels
synthetic data limitations
source quality dependency
market evolution
subjective client preferences
```

---

# 120. Gouvernance

Toute évolution majeure du matching doit suivre :

```text
Experiment
      |
      v
Evaluation
      |
      v
Decision
      |
      v
Versioning
      |
      v
Deployment
      |
      v
Monitoring
```

---

# 121. Critère de réussite C5

La compétence sera démontrée lorsque nous disposerons de :

```text
Business problem definition
+
Dataset
+
Baseline
+
Feature engineering
+
At least one evaluated model
+
Metrics
+
Comparison
+
MLflow traceability
+
Model artifact
+
API/runtime evidence
+
Explanation of limitations
```

---

# 122. Ce qui ne constitue pas une preuve suffisante

Les affirmations suivantes ne suffisent pas :

```text
"We use AI."

"We use Ollama."

"We use MLflow."

"We have a matching score."

"The model works."
```

Il faut démontrer :

```text
input
algorithm
dataset
experiment
metric
artifact
version
result
```

---

# 123. Matrice de preuve

| Élément | Baseline | Preuve runtime |
|---|---|---|
| Problème métier | DOCUMENTÉ | Cas de test |
| Hard filters | DÉFINIS | SQL/tests |
| Scoring | DÉFINI | Code |
| Features | IDENTIFIÉES | Dataset |
| Baseline | DÉFINIE | Metrics |
| ML model | CANDIDAT | Training run |
| Evaluation | MÉTHODE DÉFINIE | Report |
| Tracking | MLflow | Run |
| Model version | DÉFINIE | Registry |
| Artifact | DÉFINI | MLflow/MinIO |
| API | DÉFINIE | Response |
| Explainability | DÉFINIE | Match explanation |
| Monitoring | DÉFINI | Metrics |
| Governance | DÉFINIE | Model Card |

---

# 124. Relation avec C1

```text
DEMANDE_VERSION
+
BIEN
+
PRESENTATION
```

proviennent du modèle Data conçu dans C1.

---

# 125. Relation avec C2

C2 optimise la sélection initiale :

```text
SQL filtering
```

afin de réduire le nombre de biens envoyés au moteur de matching.

---

# 126. Relation avec C3

Les résultats historiques peuvent alimenter :

```text
warehouse.fact_presentation
```

pour mesurer les performances du matching.

---

# 127. Relation avec C4

C4 détermine si le volume de biens, de documents et de vecteurs nécessite une évolution de l'architecture.

---

# 128. Relation avec C6

C6 couvrira le programme IA complet :

```text
development
testing
packaging
deployment
orchestration
observability
```

C5 se concentre principalement sur le modèle et sa qualité.

---

# 129. Relation avec C7

Le dataset et les features doivent respecter les exigences RGPD.

---

# 130. Relation avec C8

L'exécution IA doit respecter :

```text
sovereignty
security
model governance
data confidentiality
```

---

# 131. Décision actuelle

La baseline retenue est :

```text
SQL hard filtering
        |
        v
Explainable deterministic scoring
        |
        v
Optional ML comparison
        |
        v
Optional semantic enrichment
        |
        v
Human validation
```

---

# 132. Technologies actuelles

```text
PostgreSQL
Python
FastAPI
Airflow
MLflow
MinIO
Ollama
Prometheus
Grafana
```

Les composants optionnels tels que Qdrant doivent être adoptés uniquement après justification.

---

# 133. Statut

| Élément | Statut |
|---|---|
| Business problem | DOCUMENTÉ |
| Matching architecture | DÉFINIE |
| Hard filtering | DÉFINI |
| Deterministic scoring | BASELINE DÉFINIE |
| Explainability | DÉFINIE |
| Human-in-the-loop | DÉFINI |
| Feature candidates | IDENTIFIÉES |
| ML candidates | IDENTIFIÉS |
| Evaluation strategy | DÉFINIE |
| MLflow strategy | DÉFINIE |
| Semantic matching | CANDIDAT |
| Vector DB | À ÉVALUER |
| Dataset | À PRODUIRE |
| Baseline implementation | À PRODUIRE |
| Training | À EXÉCUTER |
| Metrics | À PRODUIRE |
| MLflow evidence | À PRODUIRE |
| Model Card | À PRODUIRE |
| API evidence | À PRODUIRE |

---

# 134. Conclusion

Le moteur de matching n'est pas conçu comme une boîte noire.

La stratégie est :

```text
Structured Data
      |
      v
SQL Filtering
      |
      v
Explainable Scoring
      |
      v
ML / Semantic Enhancement
when justified
      |
      v
Ranked Recommendations
      |
      v
Human Validation
```

Le Machine Learning devra démontrer une amélioration mesurable par rapport à une baseline plus simple avant de devenir un composant essentiel du matching.

La traçabilité sera assurée par :

```text
Git
+
Airflow
+
MLflow
+
Model Versioning
+
Runtime Metrics
```

et les résultats finaux devront être fondés sur des expérimentations réellement exécutées.

---

**BC05 / C5 — MODÈLE DE MATCHING IA — DOCUMENTATION BASELINE COMPLETE**