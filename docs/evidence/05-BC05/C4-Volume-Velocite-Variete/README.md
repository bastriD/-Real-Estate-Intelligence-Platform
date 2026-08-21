# BC05 — C4 — Volume, Vélocité, Variété

**Bloc de compétences :** BC05  
**Compétence :** Analyser les caractéristiques Volume, Vélocité et Variété afin d'adapter l'architecture Data  
**Projet :** Real Estate Intelligence Platform  
**Version :** 2.0  
**Statut :** Baseline documentaire corrigée — mesures runtime à produire  

---

# 1. Objectif

Cette partie démontre que l'architecture Data est dimensionnée à partir du besoin métier réel.

L'analyse repose sur les :

```text
3V
```

c'est-à-dire :

```text
Volume
Velocity
Variety
```

La démarche est :

```text
Business Projections
        |
        v
Data Characteristics
        |
        v
Current Architecture
        |
        v
Capacity Evaluation
        |
        v
Measured Threshold
        |
        v
Architecture Evolution
```

---

# 2. Pourquoi analyser les 3V

Une architecture Data ne doit pas être choisie uniquement parce qu'une technologie est populaire.

Exemple :

```text
PostgreSQL
Kafka
Spark
Flink
ClickHouse
```

ne répondent pas au même problème.

La plateforme doit commencer avec l'architecture la plus simple capable de satisfaire les besoins.

---

# 3. Contexte officiel de croissance

Le StarterPack prévoit une forte augmentation de l'activité.

Les projections parlent de :

```text
plusieurs milliers de mandats par semaine
```

avec :

```text
plusieurs centaines
voire milliers de biens
répertoriés par recherche
```

et une expansion géographique vers plusieurs pays européens.

Cette croissance concerne à la fois :

```text
business transactions
property ingestion
matching
analytics
```

---

# 4. Expansion géographique

Le futur périmètre peut couvrir :

```text
France
DROM
Espagne
Allemagne
Royaume-Uni
Irlande
BeNeLux
Italie
Suisse
```

Cela influence notamment :

```text
volume
source diversity
location formats
postal codes
languages
property formats
```

---

# 5. Volume

Le Volume représente la quantité de données :

```text
stockées
ingérées
transformées
analysées
historisées
sauvegardées
```

Il peut être exprimé en :

```text
rows
documents
objects
vectors
GB
TB
```

---

# 6. Principales sources de volume

Le modèle cible comprend notamment :

```text
CLIENT
CHASSEUR
MANDAT
DEMANDE
DEMANDE_VERSION
BIEN
PRESENTATION
COMMENTAIRE
PAIEMENT
DOCUMENT
```

Toutes ces tables ne croissent pas à la même vitesse.

---

# 7. Volume CLIENT

Le nombre de clients croît généralement avec :

```text
new business activity
```

mais il ne constitue probablement pas la plus grande table.

---

# 8. Volume MANDAT

Le StarterPack prévoit :

```text
several thousand mandates/week
```

À titre de scénario :

```text
5,000 mandates / week
```

donnerait :

```text
260,000 mandates / year
```

si ce rythme restait constant.

Cette valeur est un scénario de dimensionnement, pas une mesure réelle.

---

# 9. Volume DEMANDE_VERSION

Une demande peut être modifiée plusieurs fois.

Exemple :

```text
1 mandate
=
1 demand
+
3 versions
```

Alors :

```text
260,000 mandates/year
```

peuvent produire :

```text
780,000 demand versions/year
```

dans ce scénario.

---

# 10. Volume BIEN

Les propriétés représentent une source de croissance beaucoup plus importante.

Le StarterPack prévoit :

```text
hundreds or thousands of properties
per search
```

---

# 11. Volume matching

Le facteur de croissance principal peut devenir :

```text
DEMANDE × BIEN
```

Exemple purement dimensionnel :

```text
5,000 mandates/week
x
500 properties/search
=
2,500,000 candidate relations/week
```

---

# 12. Scénario plus élevé

Avec :

```text
5,000 mandates/week
x
1,000 properties/search
```

on obtient :

```text
5,000,000 candidate relations/week
```

Cela montre pourquoi :

```text
PRESENTATION
```

ou une structure de candidats intermédiaire peut croître beaucoup plus vite que :

```text
MANDAT
```

---

# 13. Important — ne pas tout persister

Toutes les relations candidates n'ont pas nécessairement besoin d'être conservées durablement.

Exemple :

```text
1000 candidate properties
       |
       v
hard filtering
       |
       v
100 candidates
       |
       v
ranking
       |
       v
20 qualified
       |
       v
10 presented
```

Il peut être inutile de stocker durablement les 1000 relations initiales.

---

# 14. Stratégie de réduction

Le moteur doit réduire le volume le plus tôt possible.

```text
All Properties
      |
      v
SQL Hard Filters
      |
      v
Candidate Set
      |
      v
Scoring
      |
      v
Top-K
```

Cela améliore :

```text
CPU
memory
storage
latency
AI cost
```

---

# 15. Volume PRESENTATION

`PRESENTATION` devrait principalement représenter les biens réellement :

```text
identifiés
qualifiés
présentés
rejetés
visités
retenus
```

selon la stratégie d'implémentation.

---

# 16. Volume COMMENTAIRE

Le nombre de commentaires dépend :

```text
presentations
x
client interactions
x
hunter interactions
```

Cette table peut également devenir importante mais devrait rester bien inférieure au nombre brut de relations candidate-search.

---

# 17. Volume PAIEMENT

`PAIEMENT` augmente seulement avec les transactions arrivant aux étapes financières.

Son volume est donc très inférieur à celui :

```text
BIEN
PRESENTATION
```

---

# 18. Volume DOCUMENT

Les fichiers associés aux biens peuvent devenir importants.

Exemples :

```text
PDF
photos
videos
audio
diagnostics
```

Ils ne doivent pas être stockés directement dans PostgreSQL sauf raison particulière.

---

# 19. Object Storage

Architecture :

```text
PostgreSQL
    |
    +--> metadata

MinIO
    |
    +--> binary files
```

Cela permet d'éviter que la base relationnelle absorbe inutilement les gros objets binaires.

---

# 20. Volume AI / RAG

Un document peut produire :

```text
N chunks
```

et donc :

```text
N embeddings
```

Exemple :

```text
10,000 documents
x
40 chunks/document
=
400,000 embeddings
```

---

# 21. Volume vectoriel

Le volume dépend de :

```text
number of documents
chunking strategy
embedding dimension
metadata
index structure
```

Une architecture vectorielle doit donc être dimensionnée à partir de mesures réelles.

---

# 22. Volume observabilité

Le projet produit aussi :

```text
metrics
logs
traces
```

Le volume d'observabilité peut dépasser le volume métier si la rétention et la cardinalité sont mal contrôlées.

---

# 23. Loki

Les logs dépendent :

```text
request rate
log level
payload size
retention
```

---

# 24. Prometheus

Les métriques dépendent notamment :

```text
number of series
label cardinality
scrape interval
retention
```

---

# 25. Tempo

Le tracing dépend :

```text
request rate
number of spans
sampling
retention
```

---

# 26. Mesures réelles attendues

Les preuves finales devront mesurer :

```text
row counts
database size
table size
storage growth
matching relations
pipeline throughput
```

---

# 27. PostgreSQL row count

Exemple :

```sql
SELECT COUNT(*)
FROM real_estate.bien;
```

---

# 28. Table size

```sql
SELECT
    pg_size_pretty(
        pg_total_relation_size('real_estate.bien')
    );
```

---

# 29. Schema size

```sql
SELECT
    n.nspname,
    pg_size_pretty(
        SUM(pg_total_relation_size(c.oid))
    ) AS total_size
FROM pg_class c
JOIN pg_namespace n
    ON n.oid = c.relnamespace
WHERE n.nspname = 'real_estate'
GROUP BY n.nspname;
```

---

# 30. Vélocité

La vélocité représente :

```text
how fast data arrives
```

et :

```text
how quickly it must be processed
```

Ces deux notions ne doivent pas être confondues.

---

# 31. Ingestion rate vs business freshness

Exemple :

```text
Source changes every minute
```

ne signifie pas automatiquement :

```text
User needs sub-second refresh
```

---

# 32. Vélocité métier

Le parcours futur prévoit notamment que les chasseurs reçoivent :

```text
daily
or several times per day
```

des sélections de biens dans les zones tendues.

Cela correspond davantage à :

```text
batch
micro-batch
scheduled processing
```

qu'à un besoin strict de streaming sub-seconde.

---

# 33. Airflow fit

Airflow est adapté lorsque le besoin est :

```text
every few minutes
hourly
daily
event-triggered batch
```

avec :

```text
dependency management
retry
monitoring
```

---

# 34. Airflow limitation

Airflow n'est pas un moteur de streaming continu à haute fréquence.

Si le besoin évolue vers :

```text
continuous high-rate event processing
```

il faudra évaluer d'autres technologies.

---

# 35. Kafka

Kafka devient candidat lorsque nous avons :

```text
large event rate
many independent consumers
event replay
durable event log
continuous event processing
```

---

# 36. Kafka status

Actuellement :

```text
FUTURE
```

Il ne fait pas partie des dépendances obligatoires du projet.

---

# 37. Pourquoi ne pas déployer Kafka maintenant

Kafka implique :

```text
brokers
topics
partitioning
replication
retention
monitoring
operations
```

Cette complexité doit être justifiée par un besoin mesuré.

---

# 38. Condition d'adoption Kafka

Avant adoption :

```text
Measured Event Rate
       |
       v
Latency Requirement
       |
       v
Current Batch Insufficient?
       |
       v
Kafka Benchmark / Architecture Study
       |
       v
ADR
```

---

# 39. Vélocité du matching

La plateforme doit traiter :

```text
new search
new property
updated search criteria
client feedback
```

et potentiellement recalculer un ranking.

---

# 40. Batch matching

Approche candidate :

```text
New properties imported
       |
       v
Airflow
       |
       v
Matching batch
       |
       v
New presentations
```

---

# 41. Interactive matching

Le backend peut aussi déclencher :

```text
matching on demand
```

pour une demande donnée.

Cela nécessite un temps de réponse différent du batch.

---

# 42. AI latency

L'inférence LLM locale peut être beaucoup plus lente que :

```text
SQL filters
```

et :

```text
deterministic scoring
```

Le pipeline doit donc éviter d'appeler un LLM sur chaque propriété lorsque ce n'est pas nécessaire.

---

# 43. Example optimization

Incorrect :

```text
1000 properties
      |
      v
1000 LLM calls
```

Preferred:

```text
1000 properties
      |
      v
SQL filters
      |
      v
50 candidates
      |
      v
structured ranking
      |
      v
Top 10
      |
      v
optional AI enrichment
```

---

# 44. GPU throughput

La plateforme locale possède une capacité GPU limitée.

La vélocité AI dépend :

```text
model size
quantization
prompt length
output length
concurrent requests
```

---

# 45. Queueing

Si le nombre de requêtes AI dépasse la capacité disponible, une file de traitement pourra être nécessaire.

Cela devra être déclenché par des métriques telles que :

```text
queue depth
waiting time
GPU utilization
inference duration
```

---

# 46. Variété

La variété représente la diversité :

```text
formats
schemas
sources
languages
structures
```

---

# 47. Structured Data

Exemples :

```text
CLIENT
MANDAT
DEMANDE_VERSION
BIEN
PAIEMENT
```

---

# 48. Semi-Structured Data

Exemples :

```text
JSON announcements
JSONB preferences
API responses
metadata
```

---

# 49. Unstructured Data

Exemples :

```text
PDF
images
audio
video
free text descriptions
```

---

# 50. StarterPack Generator and Variety

Le générateur simule volontairement plusieurs problèmes :

```text
fields absent
fields renamed
different date representations
optional coordinates
nested objects
CSV
JSON
```

Cela constitue une vraie justification pour :

```text
RAW
+
STAGING
+
CANONICAL MODEL
```

---

# 51. Source Diversity

Les données peuvent provenir de :

```text
agencies
individual sellers
platforms
APIs
manual import
open data
```

---

# 52. Canonical Model

La variété est maîtrisée grâce à :

```text
Source-specific format
       |
       v
Adapter / Parser
       |
       v
STAGING
       |
       v
Canonical BIEN
```

---

# 53. Adapter Pattern

Exemple :

```text
CsvAdapter
JsonAdapter
ApiAdapter
```

Ils convergent vers le même schéma canonique.

---

# 54. Schema Drift

Une source peut modifier :

```text
field name
field type
nested structure
date format
```

Le pipeline doit pouvoir détecter ce changement.

---

# 55. Data Contract

Une future source stable peut être associée à un Data Contract.

Il peut définir :

```text
schema
required fields
types
quality expectations
version
owner
```

---

# 56. Languages

L'expansion internationale augmente également la variété linguistique.

Exemples :

```text
French
Spanish
German
English
Italian
Dutch
```

Cela affecte :

```text
descriptions
criteria
semantic matching
LLM prompts
```

---

# 57. Postal Codes

Les formats postaux varient selon les pays.

Ils doivent rester :

```text
VARCHAR
```

et non être traités comme des entiers.

---

# 58. Currency

Une expansion internationale peut également introduire plusieurs devises.

Le modèle actuel suppose implicitement des montants comparables.

Une extension future peut nécessiter :

```text
currency_code
exchange rates
```

si le business dépasse la zone euro.

---

# 59. International Property Types

Les types de biens peuvent également varier.

Une taxonomie canonique pourra être nécessaire.

Exemple :

```text
source-specific property type
       |
       v
canonical property type
```

---

# 60. Profil 3V actuel

La baseline peut être résumée ainsi :

```text
Volume:
Moderate today
Potentially large matching volume

Velocity:
Batch / micro-batch
with interactive requests

Variety:
High and increasing
```

---

# 61. Current Architecture Fit

La baseline actuelle reste :

```text
PostgreSQL
+
Airflow
+
MinIO
+
OpenMetadata
```

avec :

```text
RAW
STAGING
OLTP
OLAP
```

---

# 62. PostgreSQL Capacity

PostgreSQL peut supporter des volumes très importants lorsqu'il est correctement conçu.

Il n'existe pas de règle :

```text
1 million rows
=
need Spark
```

---

# 63. Factors that actually matter

Il faut mesurer :

```text
query latency
concurrency
index size
working set
I/O
pipeline duration
CPU
RAM
storage
```

---

# 64. Scaling Vertical

Première évolution possible :

```text
more CPU
more RAM
faster storage
```

---

# 65. Scaling Query Design

Avant de changer de technologie :

```text
indexes
query optimization
filtering
data model
partitioning
```

doivent être évalués.

---

# 66. Connection Pooling

Une forte concurrence applicative peut nécessiter :

```text
PgBouncer
```

ou un autre mécanisme de pooling.

Ce besoin doit être mesuré.

---

# 67. Read Replicas

Si les lectures deviennent importantes :

```text
primary
   |
   +--> replica
```

peut permettre de séparer certains workloads.

---

# 68. Partitioning

Tables candidates :

```text
bien
presentation
commentaire
fact_presentation
```

si leur taille et leurs patterns de requêtes le justifient.

---

# 69. Dedicated OLAP Engine

Un moteur spécialisé peut être étudié lorsque :

```text
analytical latency
```

ou :

```text
warehouse size
```

dépasse ce que PostgreSQL peut fournir raisonnablement dans l'environnement cible.

---

# 70. Technologies candidates

Exemples futurs :

```text
ClickHouse
DuckDB
Trino
cloud warehouse
```

selon le besoin réel.

---

# 71. Spark

Spark devient pertinent lorsque :

```text
distributed processing
```

est réellement nécessaire.

Ce n'est pas une exigence du projet actuel.

---

# 72. Data Lake

Le stockage objet peut progressivement prendre le rôle d'une zone Data Lake.

Exemple :

```text
MinIO
 |
 +--> raw
 +--> curated
 +--> ML
```

---

# 73. Parquet

Pour de gros datasets analytiques :

```text
Parquet
```

peut améliorer :

```text
compression
columnar reads
analytics
```

mais il n'est pas obligatoire pour le MVP.

---

# 74. Vector Database

La variété AI introduit :

```text
vector data
```

Les options incluent :

```text
pgvector
```

et :

```text
Qdrant
```

---

# 75. pgvector

Avantages possibles :

```text
fewer platform components
same PostgreSQL governance
simpler backup
```

pour un volume vectoriel modéré.

---

# 76. Qdrant

Qdrant devient candidat si :

```text
vector volume
latency
specialized retrieval
```

justifient un moteur dédié.

Statut :

```text
CANDIDATE
```

---

# 77. Benchmark Before Adoption

```text
Dataset
   |
   +--> pgvector
   |
   +--> Qdrant
   |
   v
Performance / Complexity Comparison
   |
   v
ADR
```

---

# 78. Architecture Evolution Thresholds

Les seuils doivent être liés à des métriques.

Exemples :

```text
query latency
pipeline duration
database size
ingestion throughput
GPU latency
queue depth
warehouse growth
```

---

# 79. PostgreSQL Threshold Example

Une évolution est étudiée lorsque :

```text
critical query latency > SLO
```

après :

```text
query tuning
indexing
schema optimization
right-sizing
```

---

# 80. Airflow Threshold Example

Une architecture streaming est étudiée lorsque :

```text
required freshness
<
achievable batch interval
```

de manière durable.

---

# 81. AI Threshold Example

Une évolution du serving devient nécessaire lorsque :

```text
queue wait
+
inference duration
>
business latency target
```

---

# 82. Data Retention

La croissance doit être contrôlée.

Données concernées :

```text
raw files
candidate matches
logs
metrics
traces
documents
model artifacts
```

---

# 83. Candidate Matching Retention

Une question importante est :

```text
Do we retain all rejected candidates?
```

Il faut arbitrer entre :

```text
analytics value
auditability
storage
privacy
```

---

# 84. Hot vs Historical Data

Le lifecycle peut être :

```text
HOT
 |
 v
HISTORICAL
 |
 v
ARCHIVE
 |
 v
DELETE
```

---

# 85. RGPD Impact

Le volume n'est pas uniquement une problématique technique.

Plus de données personnelles signifie également :

```text
greater exposure
larger deletion scope
higher backup impact
higher governance cost
```

---

# 86. Eco-conception

Principe :

```text
Store what creates value.
Process what is needed.
Retain only as long as justified.
```

---

# 87. Observability of 3V

Les métriques doivent rendre les 3V mesurables.

---

# 88. Volume Metrics

```text
rows_total
database_bytes
table_bytes
object_storage_bytes
logs_bytes
vectors_total
```

---

# 89. Velocity Metrics

```text
rows_ingested_per_second
pipeline_duration
matching_requests_per_second
matching_duration
AI_requests
data_freshness
```

---

# 90. Variety Metrics

```text
source_count
schema_count
format_count
adapter_count
document_type_count
```

---

# 91. Benchmark Datasets

Le générateur StarterPack peut être utilisé pour produire des tailles progressives.

Exemples :

```text
100 searches
100 properties/search

1000 searches
500 properties/search

5000 searches
1000 properties/search
```

selon les capacités disponibles.

---

# 92. Important

Un benchmark ne doit pas saturer inutilement l'environnement.

La taille doit augmenter progressivement.

---

# 93. Progressive Benchmark

```text
small
 |
 v
medium
 |
 v
large
 |
 v
observe threshold
```

---

# 94. Volume Test

Mesurer :

```text
generation duration
raw file size
ingestion duration
database size
```

---

# 95. Velocity Test

Mesurer :

```text
rows loaded / second
properties normalized / second
matching operations / second
```

---

# 96. Matching Benchmark

Mesurer au minimum :

```text
number of properties
number after SQL filtering
ranking duration
number persisted
```

---

# 97. Variety Test

Vérifier la normalisation de :

```text
CSV
JSON
different dates
missing coordinates
renamed fields
```

---

# 98. Benchmark Report

Chaque benchmark doit indiquer :

```text
hardware
dataset size
configuration
start time
end time
throughput
errors
resource usage
interpretation
```

---

# 99. Evidence Files

Les preuves runtime seront stockées hors documentation.

Exemples :

```text
database/tests/
pipelines/
scripts/
```

Ce dossier reste l'index documentaire.

---

# 100. Future Evidence

Exemples :

```text
volume-measurements.txt
ingestion-benchmark.json
matching-benchmark.json
storage-growth.csv
3v-analysis-report.md
```

---

# 101. Decision Matrix

Une technologie supplémentaire n'est adoptée que si :

```text
Measured Problem
      |
      v
Current Solution Insufficient
      |
      v
Alternatives Compared
      |
      v
Operational Cost Evaluated
      |
      v
Decision
```

---

# 102. Anti-Pattern

À éviter :

```text
"Big Data project"
=
"deploy everything"
```

Le projet doit démontrer la capacité à choisir la bonne technologie, y compris lorsqu'il est préférable de ne pas l'ajouter.

---

# 103. Architecture Today

```text
Generated / External Data
       |
       v
RAW
       |
       v
STAGING
       |
       v
PostgreSQL OLTP
       |
       v
PostgreSQL OLAP
```

avec :

```text
Airflow
MinIO
OpenMetadata
```

---

# 104. Potential Future

```text
PostgreSQL
   |
   +--> replicas
   +--> partitioning
   +--> pgvector
```

puis éventuellement :

```text
Kafka
Dedicated OLAP
Spark
Qdrant
Data Lake architecture
```

si les mesures le justifient.

---

# 105. Relation with C2

C2 mesure et optimise :

```text
OLTP query performance
```

---

# 106. Relation with C3

C3 sépare :

```text
analytical workloads
```

de l'OLTP.

---

# 107. Relation with C5

Le matching crée potentiellement le plus gros multiplicateur de volume :

```text
DEMANDE
x
BIEN
```

Il doit donc filtrer efficacement.

---

# 108. Relation with C6

Le programme IA doit mesurer :

```text
latency
throughput
resource consumption
```

---

# 109. Relation with C7

Les politiques de rétention doivent prendre en compte :

```text
privacy
```

en plus de la capacité technique.

---

# 110. Current Status

| Élément | Statut |
|---|---|
| Official growth scenario | INTEGRATED |
| Mandate growth model | DEFINED |
| Demand-version growth | DEFINED |
| Property growth | DEFINED |
| Matching multiplication | DEFINED |
| Volume strategy | UPDATED |
| Velocity strategy | UPDATED |
| Variety strategy | UPDATED |
| Kafka criteria | DEFINED |
| Spark criteria | DEFINED |
| Vector strategy | DEFINED |
| Scaling thresholds | DEFINED |
| Retention strategy | DEFINED |
| Real measurements | PENDING |
| Ingestion benchmark | PENDING |
| Matching benchmark | PENDING |
| Final capacity thresholds | PENDING |

---

# 111. Conclusion

Le risque principal de croissance du projet n'est pas uniquement :

```text
number of clients
```

ou :

```text
number of mandates
```

mais surtout la relation :

```text
DEMANDE
    x
BIEN
```

qui peut produire des millions de candidats de matching.

La stratégie cible est donc :

```text
Filter Early
   |
   v
Reduce Candidates
   |
   v
Rank Efficiently
   |
   v
Persist Only Valuable State
```

tout en conservant :

```text
PostgreSQL
+
Airflow
+
MinIO
```

comme architecture de base tant que les mesures démontrent qu'elle satisfait les besoins.

Les évolutions vers Kafka, Spark, un moteur OLAP spécialisé ou une base vectorielle dédiée ne seront adoptées qu'à partir de preuves mesurées.

---

**BC05 / C4 — VOLUME, VÉLOCITÉ, VARIÉTÉ V2 — ALIGNED WITH OFFICIAL GROWTH SCENARIO**