# BC05 — C4 — Volume, Vélocité, Variété

**Bloc de compétences :** BC05  
**Compétence :** C4 — Analyser les caractéristiques Volume, Vélocité et Variété des données afin d'adapter l'architecture  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Version :** 1.0  
**Statut :** Baseline documentaire — mesures réelles à consolider

---

# 1. Objectif

Ce dossier démontre que l'architecture Data n'est pas dimensionnée arbitrairement.

Le choix des technologies doit tenir compte des caractéristiques réelles des données.

Le modèle utilisé est celui des :

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
Data Characteristics
       |
       v
Requirements
       |
       v
Current Architecture
       |
       v
Capacity Evaluation
       |
       v
Scaling Threshold
       |
       v
Architecture Evolution
```

---

# 2. Pourquoi analyser les 3V

Toutes les plateformes Data ne nécessitent pas :

```text
Kafka
Spark
Flink
Distributed Data Lake
Massively Parallel Warehouse
```

Le choix dépend des besoins.

Exemple :

```text
10,000 structured records per day
```

ne justifie pas forcément la même architecture que :

```text
1,000,000 events per second
```

Le principe du projet est :

```text
Architecture proportional to workload
```

---

# 3. Les trois dimensions

```text
VOLUME
How much data?
```

```text
VELOCITY
How fast does data arrive or change?
```

```text
VARIETY
How many different structures and formats?
```

Ces trois dimensions doivent être analysées ensemble.

---

# 4. Volume

Le Volume correspond à la quantité de données :

- stockées ;
- ingérées ;
- transformées ;
- analysées ;
- sauvegardées ;
- répliquées.

Il peut être mesuré en :

```text
Rows
MB
GB
TB
Objects
Documents
Embeddings
```

---

# 5. Volume du projet — données structurées

Les principales entités structurées sont :

```text
CLIENT
CHASSEUR
MANDAT
DEMANDE_VERSION
SOURCE
BIEN
PRESENTATION
DOCUMENT metadata
```

Le MVP est conçu pour un volume initial limité à modéré.

---

# 6. Hypothèse de croissance

Exemple de scénario de dimensionnement :

```text
100 clients
500 mandates
2,000 request versions
100,000 properties
50,000 presentations
20,000 documents
```

Ces valeurs constituent uniquement un scénario de dimensionnement.

Les volumes réels devront être mesurés.

---

# 7. Volume BIEN

`BIEN` sera probablement l'une des tables opérationnelles les plus volumineuses.

Pourquoi :

```text
Multiple sources
+
Regular collection
+
Historical properties
```

Le volume peut croître plus rapidement que les tables :

```text
client
mandat
chasseur
```

---

# 8. Volume PRESENTATION

`PRESENTATION` peut également croître rapidement.

Si :

```text
1 request
```

est comparée à :

```text
100 candidate properties
```

alors :

```text
100 presentations/matches
```

peuvent être générées.

---

# 9. Croissance analytique

Le Data Warehouse peut augmenter le volume global car une donnée opérationnelle peut être représentée dans plusieurs couches :

```text
OLTP
 |
 v
Staging
 |
 v
Warehouse
 |
 v
Analytics
```

Le volume physique total peut donc être supérieur au volume source.

---

# 10. Duplication contrôlée

La duplication dans une architecture analytique n'est pas automatiquement mauvaise.

Elle peut être justifiée pour :

- performance ;
- historisation ;
- séparation des workloads ;
- analytics.

Elle doit cependant être maîtrisée.

---

# 11. Volume documents

Les documents peuvent représenter un volume beaucoup plus important que les données relationnelles.

Exemples :

```text
PDF
Images
Plans
Diagnostics
Brochures
```

Ils ne doivent pas nécessairement être stockés directement dans PostgreSQL.

---

# 12. Object Storage

Architecture cible :

```text
PostgreSQL
   |
   +--> document metadata

MinIO
   |
   +--> document binaries
```

Cette séparation permet de mieux gérer :

- taille ;
- rétention ;
- sauvegarde ;
- accès.

---

# 13. Volume RAG

Un système RAG peut multiplier les objets logiques.

Exemple :

```text
1 PDF
```

peut devenir :

```text
50 chunks
```

puis :

```text
50 embeddings
```

Donc :

```text
1,000 documents
```

peuvent devenir :

```text
50,000 vectors
```

selon le chunking.

---

# 14. Importance du chunking

Le choix du chunk size influence directement :

```text
Number of chunks
Storage
Embedding computation
Retrieval cost
LLM context
```

Un chunking trop fin augmente fortement le volume vectoriel.

---

# 15. Volume observabilité

Les données d'observabilité peuvent également devenir importantes.

Exemples :

```text
Prometheus metrics
Loki logs
Tempo traces
```

Ces données peuvent croître plus rapidement que les données métier.

---

# 16. Volume logs

Le volume de logs dépend notamment :

```text
Request rate
Log level
Payload size
Retention
Number of services
```

Un mode :

```text
DEBUG
```

permanent peut multiplier inutilement le stockage.

---

# 17. Volume metrics

Prometheus dépend :

```text
number of metrics
number of labels
cardinality
scrape interval
retention
```

Une cardinalité élevée peut fortement augmenter le stockage.

---

# 18. Volume traces

Le tracing distribué peut produire une quantité importante de données.

Une stratégie de sampling peut être envisagée si la charge augmente.

---

# 19. Mesure du volume

Les mesures réelles pourront inclure :

```sql
SELECT COUNT(*) FROM real_estate.bien;
```

```sql
SELECT COUNT(*) FROM real_estate.presentation;
```

et :

```sql
SELECT
    pg_size_pretty(
        pg_total_relation_size('real_estate.bien')
    );
```

---

# 20. Taille d'un schéma

Une requête peut permettre d'estimer la taille :

```sql
SELECT
    nspname AS schema_name,
    pg_size_pretty(
        SUM(pg_total_relation_size(c.oid))
    ) AS total_size
FROM pg_class c
JOIN pg_namespace n
  ON n.oid = c.relnamespace
WHERE nspname = 'real_estate'
GROUP BY nspname;
```

---

# 21. Storage Growth

Une métrique utile est :

```text
GB / day
```

ou :

```text
GB / month
```

pour les principales catégories :

```text
PostgreSQL
MinIO
Loki
Prometheus
Tempo
ML artifacts
```

---

# 22. Vélocité

La Vélocité représente la vitesse à laquelle les données :

- arrivent ;
- changent ;
- doivent être traitées ;
- doivent être disponibles.

Elle ne signifie pas automatiquement :

```text
real-time
```

---

# 23. Questions de vélocité

Il faut distinguer :

```text
How often does data arrive?
```

de :

```text
How quickly must users see it?
```

Exemple :

une source peut être mise à jour toutes les minutes, mais le métier peut n'avoir besoin d'une actualisation que toutes les heures.

---

# 24. Vélocité du projet

Les données immobilières sont généralement moins rapides que :

```text
financial market ticks
IoT telemetry
telecommunications events
```

Le MVP peut donc fonctionner avec des traitements batch ou micro-batch.

---

# 25. Exemple de fréquence

Sources possibles :

```text
Manual import
Hourly collection
Daily batch
API polling
Event-driven future source
```

La fréquence doit correspondre au besoin métier réel.

---

# 26. Airflow

Airflow est adapté aux traitements :

```text
Batch
Scheduled
Dependency-driven
```

Exemple :

```text
Every hour
```

ou :

```text
Every day
```

selon le besoin.

---

# 27. Pourquoi Airflow est suffisant actuellement

Le workload actuel ne nécessite pas nécessairement :

```text
sub-second event processing
```

Airflow permet :

- orchestration ;
- retry ;
- scheduling ;
- dependency management ;
- observability.

---

# 28. Limite Airflow

Airflow n'est pas conçu comme moteur principal de streaming temps réel.

Si l'exigence devient :

```text
continuous event processing
```

alors d'autres technologies peuvent devenir pertinentes.

---

# 29. Kafka

Kafka devient potentiellement utile lorsque le projet nécessite :

```text
High event rate
Multiple consumers
Replay
Decoupling
Event-driven integration
Durable event log
```

---

# 30. Kafka n'est pas adopté actuellement

Statut :

```text
FUTURE
```

Le projet ne dispose pas actuellement d'un besoin suffisant pour justifier :

- brokers ;
- topics ;
- replication ;
- retention ;
- monitoring ;
- operational complexity.

---

# 31. Condition d'adoption Kafka

Un ADR dédié devra répondre à :

```text
What event volume?
What latency?
How many consumers?
Why database/batch is insufficient?
What replay requirement?
```

avant adoption.

---

# 32. Streaming

Architecture future possible :

```text
Sources
   |
   v
Kafka
   |
   +--> Consumer A
   +--> Consumer B
   +--> Stream Processor
   +--> Data Lake / Warehouse
```

Cette architecture reste hors MVP.

---

# 33. Vélocité AI

L'AI possède également des contraintes de vélocité.

Exemple :

```text
interactive inference
```

doit répondre plus rapidement qu'un :

```text
overnight batch training
```

Les exigences doivent être séparées.

---

# 34. Inference latency

Une interface utilisateur peut nécessiter :

```text
seconds
```

de latence acceptable.

Un traitement batch peut accepter :

```text
minutes
```

ou davantage.

---

# 35. GPU throughput

La GTX 1080 impose une capacité d'inférence limitée.

La vélocité AI dépend :

- modèle ;
- quantification ;
- longueur du prompt ;
- longueur de génération ;
- concurrence.

---

# 36. Queue future

Si plusieurs utilisateurs utilisent simultanément l'AI, un mécanisme de queue pourrait devenir nécessaire.

Mais il ne doit pas être introduit avant observation d'un problème réel.

---

# 37. Variété

La Variété représente la diversité des données.

Le projet manipule plusieurs catégories.

---

# 38. Données structurées

Exemples :

```text
PostgreSQL rows
clients
mandates
properties
matching scores
```

Ces données ont un schéma clairement défini.

---

# 39. Données semi-structurées

Exemples :

```text
JSON API responses
metadata
external source payloads
AI responses
```

Elles possèdent une structure mais peuvent évoluer.

---

# 40. Données non structurées

Exemples :

```text
PDF
Images
Text documents
Property descriptions
Reports
```

Ces données nécessitent des traitements différents.

---

# 41. Variété des sources

Le projet peut recevoir des données depuis :

```text
Manual entry
CSV
REST API
Property portal
Open Data
Partner feed
Document upload
```

Chaque source peut avoir son propre format.

---

# 42. Canonical Model

La plateforme doit normaliser les différentes sources vers un modèle commun.

```text
Source A
   |
Source B
   |
Source C
   |
   v
Normalization
   |
   v
Canonical Property Model
```

Le modèle `BIEN` joue ce rôle pour les propriétés.

---

# 43. Raw preservation

Pour certaines intégrations, conserver les données sources dans une zone RAW peut faciliter :

- audit ;
- reprocessing ;
- debugging ;
- schema evolution.

---

# 44. JSONB

PostgreSQL fournit :

```text
JSONB
```

pour certains cas semi-structurés.

Cela peut être utile lorsque des attributs source évoluent fréquemment.

Mais JSONB ne doit pas remplacer un modèle relationnel clair pour les informations métier stables.

---

# 45. Schéma flexible

Exemple approprié :

```text
source_payload JSONB
```

pour conserver un payload brut.

Exemple moins approprié :

```text
all business data in one JSON column
```

sans raison.

---

# 46. Documents

Les documents peuvent nécessiter :

```text
text extraction
metadata extraction
classification
chunking
embedding
```

avant exploitation AI.

---

# 47. Images

Les images immobilières constituent une autre variété.

Le MVP ne nécessite pas nécessairement :

```text
Computer Vision
```

mais l'architecture peut évoluer si un besoin apparaît.

---

# 48. Data contracts

Avec plusieurs sources, des Data Contracts peuvent devenir utiles.

Ils peuvent définir :

```text
Schema
Required fields
Types
Quality expectations
Version
Owner
```

---

# 49. Schema drift

Une source externe peut modifier :

```text
field name
type
structure
```

Cela constitue un :

```text
Schema Drift
```

Les pipelines doivent détecter ce type de changement.

---

# 50. Validation à l'ingestion

Le pipeline peut contrôler :

```text
required fields
types
accepted values
schema version
```

avant intégration.

---

# 51. Gestion de la variété

Architecture :

```text
Heterogeneous Sources
        |
        v
Ingestion Adapters
        |
        v
Validation
        |
        v
Canonical Model
        |
        v
Data Platform
```

---

# 52. Adapter Pattern

Chaque source peut disposer d'un adaptateur.

Exemple :

```text
PortalAAdapter
PortalBAdapter
CsvAdapter
ManualAdapter
```

Ils produisent tous un modèle normalisé.

---

# 53. 3V et architecture actuelle

Le profil actuel est approximativement :

```text
Volume:
Low / Moderate

Velocity:
Batch / Moderate

Variety:
Moderate / Growing
```

Ce profil justifie actuellement :

```text
PostgreSQL
+
Airflow
+
Object Storage
```

sans architecture Big Data distribuée obligatoire.

---

# 54. Pourquoi PostgreSQL est suffisant

PostgreSQL supporte largement :

- millions de lignes ;
- index ;
- joins ;
- transactions ;
- analytics modérés ;
- JSONB ;
- extensions.

Le seuil réel dépend du workload, pas d'un nombre universel de lignes.

---

# 55. Mauvaise règle

À éviter :

```text
More than 1 million rows
=
Need Spark
```

Cette règle est fausse.

Il faut analyser :

```text
Query complexity
Latency target
Concurrent users
Dataset size
Growth rate
Hardware
```

---

# 56. Spark

Apache Spark devient potentiellement pertinent lorsque :

- les datasets dépassent la capacité pratique d'un seul moteur ;
- les transformations nécessitent un traitement distribué ;
- les workloads batch deviennent massifs ;
- plusieurs nœuds doivent partager le calcul.

Il n'est pas nécessaire actuellement.

---

# 57. Dedicated analytical engine

Des technologies telles que :

```text
ClickHouse
DuckDB
Trino
BigQuery
Snowflake
Redshift
```

peuvent devenir pertinentes pour certains workloads.

Le MVP n'en a pas besoin tant que PostgreSQL satisfait les SLO.

---

# 58. DuckDB

Pour certaines analyses locales ou fichiers Parquet, DuckDB pourrait être étudié sans déployer une infrastructure distribuée.

Cela représente un exemple d'évolution légère avant de passer à une plateforme plus complexe.

---

# 59. Data Lake

Un Data Lake peut devenir utile si le volume de données brutes et non structurées augmente fortement.

Architecture future :

```text
Sources
 |
 v
Object Storage
 |
 +--> Raw
 +--> Curated
 +--> ML
```

Le MVP ne nécessite pas encore une architecture Data Lake complète.

---

# 60. MinIO

MinIO peut déjà fournir une base de stockage objet utile pour :

- artifacts ML ;
- documents ;
- futurs datasets ;
- fichiers bruts.

Il facilite donc une évolution progressive.

---

# 61. Parquet

Pour des volumes analytiques plus importants, un format colonnaire tel que :

```text
Parquet
```

peut réduire :

- stockage ;
- I/O ;
- coût de certaines analyses.

Il n'est pas obligatoire dans la baseline relationnelle.

---

# 62. Compression

Les formats analytiques peuvent utiliser de la compression pour réduire le volume physique.

Il faut cependant considérer le compromis :

```text
Storage
vs
CPU
```

---

# 63. Vector data

Les embeddings introduisent un nouveau type de donnée :

```text
high-dimensional vectors
```

Leur volume dépend :

```text
Documents
x
Chunks
x
Embedding dimension
```

---

# 64. pgvector

PostgreSQL + pgvector peut être adapté à un volume modéré de vecteurs et réduit le nombre de composants de la plateforme.

---

# 65. Qdrant

Qdrant peut devenir intéressant lorsque :

- le volume vectoriel augmente ;
- les exigences de latence augmentent ;
- les recherches vectorielles deviennent critiques ;
- les capacités spécifiques dépassent pgvector.

Statut actuel :

```text
CANDIDATE
```

---

# 66. Décision vectorielle

Le cycle sera :

```text
RAG Requirement
      |
      v
Create benchmark
      |
      v
pgvector
vs
Qdrant
      |
      v
Measure
      |
      v
ADR
```

---

# 67. Seuils d'évolution

Les seuils doivent être basés sur des métriques.

Exemples :

```text
Database size
Query latency
Pipeline duration
Ingestion rate
Storage growth
CPU
RAM
GPU
Queue depth
```

---

# 68. Exemple seuil PostgreSQL

Une évolution peut être étudiée lorsque :

```text
Critical query latency
>
SLO
```

malgré :

```text
appropriate indexing
query optimization
schema optimization
hardware right-sizing
```

---

# 69. Exemple seuil Airflow

Une architecture streaming peut être étudiée lorsque :

```text
Required freshness
<
Practical batch interval
```

et que la donnée arrive continuellement.

---

# 70. Exemple seuil AI

Une évolution matérielle ou de serving peut être étudiée lorsque :

```text
Queue time
+
Inference time
```

dépasse durablement le besoin métier.

---

# 71. Scaling vertical

Première possibilité :

```text
More CPU
More RAM
Faster Storage
```

Le scaling vertical peut être plus simple qu'un système distribué.

---

# 72. Scaling horizontal

Kubernetes permet de scaler certains services horizontalement.

```text
Replica 1
Replica 2
Replica 3
```

Mais les composants stateful nécessitent une stratégie spécifique.

---

# 73. PostgreSQL scaling

Les options peuvent inclure :

```text
better indexes
better queries
more resources
connection pooling
read replicas
partitioning
separation OLTP/OLAP
```

avant de remplacer complètement la technologie.

---

# 74. Partitioning

Le partitionnement peut devenir pertinent pour une grande table historique.

Exemple :

```text
fact_presentation
```

partitionnée par date.

Il doit être justifié par les volumes et les requêtes.

---

# 75. Retention

La croissance doit également être contrôlée par la rétention.

Exemples :

```text
logs
traces
metrics
raw files
obsolete documents
AI artifacts
```

---

# 76. Archiving

Certaines données peuvent passer de :

```text
hot
```

à :

```text
archive
```

selon leur fréquence d'accès.

---

# 77. Lifecycle

Cycle :

```text
Create
 |
 v
Active
 |
 v
Historical
 |
 v
Archive
 |
 v
Delete
```

selon les règles métier et réglementaires.

---

# 78. RGPD

La croissance du volume de données personnelles augmente :

- surface d'exposition ;
- coût de gestion ;
- coût de suppression ;
- responsabilité réglementaire.

La minimisation est donc également une stratégie de gestion du volume.

---

# 79. Observabilité des 3V

Les 3V doivent être mesurables.

Exemples :

```text
rows/day
GB/month
events/minute
pipeline duration
documents/day
chunks/document
vectors
```

---

# 80. Métriques Volume

```text
row count
database size
table size
object storage size
log volume
artifact size
```

---

# 81. Métriques Velocity

```text
rows ingested/minute
API requests/sec
pipeline frequency
pipeline duration
data freshness
AI requests/minute
```

---

# 82. Métriques Variety

La variété peut être suivie par :

```text
number of source types
number of schemas
number of document formats
number of ingestion adapters
```

---

# 83. Tableau 3V

| Dimension | MVP actuel | Risque futur | Réponse actuelle |
|---|---|---|---|
| Volume | Faible/modéré | Croissance biens/docs | PostgreSQL + MinIO |
| Vélocité | Batch/modérée | Besoin temps réel | Airflow |
| Variété | Structuré + docs + JSON | Multiplication sources | Adapters + canonical model |

---

# 84. Évolution potentielle

| Besoin futur | Technologie à évaluer |
|---|---|
| Streaming important | Kafka |
| Processing distribué | Spark |
| Analytics très volumineux | Dedicated OLAP engine |
| Large Data Lake | MinIO + Parquet + query engine |
| Large vector search | Qdrant |
| Moderate vectors | pgvector |
| High concurrency DB | Pooling / replicas |

---

# 85. Matrice de décision

Une technologie est introduite lorsque :

```text
Measured Requirement
      |
      v
Current Architecture insufficient
      |
      v
Alternatives benchmarked
      |
      v
Operational cost understood
      |
      v
ADR
```

---

# 86. Anti-pattern

À éviter :

```text
"We may have big data someday,
therefore deploy Kafka + Spark now."
```

Cela introduit :

- coût ;
- maintenance ;
- consommation ;
- surface d'attaque ;
- complexité.

---

# 87. Eco-conception

La gestion des 3V rejoint l'éco-conception.

Principe :

```text
Store what is necessary
Process when necessary
Retain as long as necessary
```

---

# 88. Performance vs complexité

Le projet recherche :

```text
Sufficient Performance
+
Controlled Complexity
```

et non :

```text
Maximum Possible Scalability
```

---

# 89. Tests futurs — volume

Créer un dataset synthétique.

Exemples :

```text
10,000 properties
100,000 properties
1,000,000 properties
```

selon les capacités disponibles.

Mesurer :

```text
storage
query latency
load time
```

---

# 90. Tests futurs — vélocité

Mesurer :

```text
rows/second
```

pendant une ingestion.

Puis comparer au besoin métier.

---

# 91. Tests futurs — variété

Tester plusieurs formats :

```text
SQL
CSV
JSON
PDF metadata
```

et vérifier la normalisation.

---

# 92. Benchmark progressif

Le benchmark peut suivre :

```text
Dataset size
      |
      v
10k
      |
      v
100k
      |
      v
1M
```

jusqu'à observer un changement significatif.

---

# 93. Ne pas inventer des seuils

Les limites réelles dépendent de :

- hardware ;
- configuration PostgreSQL ;
- indexes ;
- queries ;
- concurrency ;
- storage.

Les seuils finaux doivent provenir de l'environnement réel.

---

# 94. Capacity Planning

Les résultats pourront alimenter :

```text
../../../30-INFRASTRUCTURE/09-Capacity-Planning.md
```

ainsi que :

```text
../../../80-OPERATIONS/05-Capacity-Management.md
```

---

# 95. Data Architecture Roadmap

Les observations 3V peuvent déclencher une évolution architecturale.

Exemple :

```text
Current:
PostgreSQL

Observed:
Analytical workload exceeds SLO

Decision:
Evaluate dedicated analytics engine
```

---

# 96. Evidence directory

Ce dossier pourra plus tard contenir :

```text
C4-Volume-Velocite-Variete/
│
├── README.md
├── volume-measurements.txt
├── velocity-benchmark.txt
├── variety-inventory.md
├── scalability-tests.md
└── architecture-thresholds.md
```

Ces artifacts seront créés à partir de données réelles.

---

# 97. Preuves attendues

Minimum recommandé :

```text
real table counts
real database sizes
real ingestion rate
source-format inventory
capacity interpretation
architecture decision
```

---

# 98. Exemple de preuve Volume

```sql
SELECT COUNT(*)
FROM real_estate.bien;
```

et :

```sql
SELECT pg_size_pretty(
    pg_total_relation_size('real_estate.bien')
);
```

---

# 99. Exemple de preuve Velocity

Un script d'ingestion peut enregistrer :

```text
Start time
Rows loaded
End time
Rows/second
```

---

# 100. Exemple de preuve Variety

Inventaire :

```text
PostgreSQL
CSV
JSON
PDF
Images
Metrics
Logs
Traces
```

avec leur stratégie de traitement.

---

# 101. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Data Characteristics
      |
      v
Measured 3V
      |
      v
Architecture Choice
      |
      v
Capacity Limits
      |
      v
Evolution Criteria
```

---

# 102. Ce qui ne suffit pas

Les affirmations suivantes seules sont insuffisantes :

```text
"We have Big Data."

"We use Kubernetes."

"We may use Kafka."

"We have many different data types."
```

Il faut relier les technologies aux caractéristiques mesurées.

---

# 103. Statut actuel

| Élément | Statut |
|---|---|
| 3V methodology | DOCUMENTÉE |
| Volume sources | IDENTIFIÉES |
| Velocity profile | IDENTIFIÉ |
| Variety profile | IDENTIFIÉ |
| Current architecture fit | JUSTIFIÉ |
| PostgreSQL rationale | DOCUMENTÉE |
| Airflow rationale | DOCUMENTÉE |
| Kafka threshold logic | DOCUMENTÉE |
| Spark threshold logic | DOCUMENTÉE |
| Vector DB evolution | DOCUMENTÉE |
| Real volume measurement | À PRODUIRE |
| Real ingestion benchmark | À PRODUIRE |
| Scalability tests | À PRODUIRE |
| Final architecture thresholds | À MESURER |

---

# 104. Conclusion

Le profil actuel du projet est :

```text
Volume
=
Low to Moderate

Velocity
=
Batch / Moderate

Variety
=
Moderate and Growing
```

Cette situation justifie actuellement une architecture relativement simple :

```text
PostgreSQL
+
Airflow
+
MinIO
+
OpenMetadata
```

Les technologies distribuées telles que :

```text
Kafka
Spark
Dedicated OLAP engine
Dedicated Vector Database
```

restent des évolutions conditionnelles.

Elles ne seront adoptées que lorsque des mesures démontreront que l'architecture actuelle ne satisfait plus les besoins.

---

**BC05 / C4 — VOLUME, VÉLOCITÉ, VARIÉTÉ — DOCUMENTATION BASELINE COMPLETE**