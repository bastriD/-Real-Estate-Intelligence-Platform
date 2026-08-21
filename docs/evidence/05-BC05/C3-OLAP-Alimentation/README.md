# BC05 — C3 — OLAP & Alimentation

**Bloc de compétences :** BC05  
**Compétence :** C3 — Concevoir et alimenter une architecture décisionnelle OLAP  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Source OLTP :** PostgreSQL  
**Orchestration cible :** Apache Airflow  
**Transformation cible :** SQL / Python / dbt selon le besoin  
**Version :** 1.0  
**Statut :** Baseline documentaire — preuves d'exécution à produire

---

# 1. Objectif

Ce dossier décrit l'architecture analytique du projet et la stratégie permettant de transformer les données opérationnelles issues de l'OLTP en données exploitables pour :

- reporting ;
- analyse métier ;
- pilotage ;
- indicateurs ;
- analyse des recherches immobilières ;
- analyse des biens ;
- analyse du matching ;
- analyse des performances du service.

La chaîne cible est :

```text
Operational Data
      |
      v
PostgreSQL OLTP
      |
      v
Extraction
      |
      v
Staging
      |
      v
Transformation
      |
      v
Data Warehouse
      |
      v
Data Marts / Analytics
      |
      v
KPI / Dashboards / AI
```

---

# 2. OLTP et OLAP

L'architecture distingue explicitement :

```text
OLTP
```

et :

```text
OLAP
```

Ils répondent à des besoins différents.

---

# 3. OLTP

L'OLTP est optimisé pour les transactions opérationnelles.

Exemples :

```text
Create client
Create mandate
Update property
Create request version
Create presentation
Record feedback
```

Caractéristiques :

```text
Normalized
Transactional
Current operational state
Short queries
Strong constraints
Frequent writes
```

---

# 4. OLAP

L'OLAP est optimisé pour :

```text
Analysis
Aggregations
Historical reporting
Business intelligence
Decision support
```

Exemples :

```text
Number of mandates per month

Average property price by city

Matching success rate

Average matching score

Properties collected per source

Client rejection rate

Average number of properties presented per mandate
```

---

# 5. Pourquoi séparer OLTP et OLAP

Une requête analytique peut nécessiter :

```text
JOIN
GROUP BY
SUM
AVG
COUNT
historical scans
```

sur de nombreux enregistrements.

Exécuter systématiquement ces traitements sur le système transactionnel peut :

- augmenter la charge ;
- perturber les opérations métier ;
- augmenter la latence ;
- compliquer l'optimisation ;
- coupler analytics et application.

L'architecture cible sépare donc les responsabilités.

---

# 6. Architecture logique

```text
                     +----------------------+
                     |   FastAPI / Services |
                     +----------+-----------+
                                |
                                v
                     +----------------------+
                     |   PostgreSQL OLTP    |
                     |    real_estate       |
                     +----------+-----------+
                                |
                                |
                         Extract / Load
                                |
                                v
                     +----------------------+
                     |       Staging        |
                     +----------+-----------+
                                |
                          Transform
                                |
                                v
                     +----------------------+
                     |    Data Warehouse    |
                     +----------+-----------+
                                |
                +---------------+---------------+
                |                               |
                v                               v
        +---------------+               +---------------+
        | Analytics     |               | Data Marts    |
        +-------+-------+               +-------+-------+
                |                               |
                +---------------+---------------+
                                |
                                v
                         KPI / Dashboard
```

---

# 7. Architecture physique cible

Le MVP peut utiliser une même instance PostgreSQL tout en séparant les responsabilités par schémas.

Exemple :

```text
PostgreSQL
│
├── real_estate
│      OLTP
│
├── staging
│      ingestion / preparation
│
├── warehouse
│      dimensional model
│
└── analytics
       business views / KPI
```

Cette approche évite de déployer inutilement un second moteur de base de données pour le MVP.

---

# 8. Évolution possible

Si les volumes ou les exigences augmentent :

```text
OLTP PostgreSQL
      |
      v
Dedicated Analytical Platform
```

pourrait devenir pertinent.

Cette évolution n'est pas nécessaire pour la baseline actuelle.

---

# 9. Principe de conception

Le modèle analytique ne doit pas être une simple copie du modèle transactionnel.

Le modèle OLTP répond à :

```text
How do we operate the business?
```

Le modèle OLAP répond à :

```text
How do we analyze the business?
```

---

# 10. Approche dimensionnelle

Le Data Warehouse utilisera une approche dimensionnelle.

Concepts principaux :

```text
FACT
DIMENSION
MEASURE
GRAIN
```

---

# 11. Table de faits

Une table de faits représente un événement ou une mesure métier.

Exemples candidats :

```text
fact_presentation
fact_property_collection
fact_mandate
```

Pour le MVP, la table de faits principale sera :

```text
fact_presentation
```

---

# 12. Grain

Le grain doit être défini avant la création de la table de faits.

Pour :

```text
fact_presentation
```

le grain est :

> Une ligne représente la présentation ou sélection d'un bien pour une version déterminée d'une demande client.

Donc :

```text
1 row
=
1 request version
+
1 property
```

---

# 13. Pourquoi le grain est important

Sans grain explicite, une mesure telle que :

```text
COUNT(*)
```

peut devenir ambiguë.

Le grain permet de comprendre précisément ce qu'une ligne représente.

---

# 14. Fact Presentation

Structure logique candidate :

```text
fact_presentation
│
├── presentation_key
├── date_key
├── property_key
├── client_key
├── chasseur_key
├── source_key
├── mandate_key
├── request_version_key
│
├── matching_score
├── budget_score
├── location_score
├── surface_score
├── criteria_score
│
├── property_price
├── property_surface
│
├── presented_count
├── rejected_count
├── visited_count
└── retained_count
```

La structure exacte sera validée pendant l'implémentation.

---

# 15. Dimensions candidates

Le modèle analytique peut contenir :

```text
dim_date
dim_client
dim_chasseur
dim_property
dim_source
dim_mandate
dim_location
```

---

# 16. Schéma en étoile

Architecture cible simplifiée :

```text
                    dim_date
                       |
                       |
dim_client ---- fact_presentation ---- dim_property
                       |
                       |
                 dim_chasseur
                       |
                       |
                  dim_source
                       |
                       |
                 dim_mandate
```

Il s'agit d'un :

```text
Star Schema
```

---

# 17. dim_date

La dimension date permet des analyses par :

```text
day
week
month
quarter
year
```

Structure candidate :

```text
dim_date
│
├── date_key
├── full_date
├── day
├── day_of_week
├── week
├── month
├── month_name
├── quarter
└── year
```

---

# 18. date_key

Une représentation possible est :

```text
YYYYMMDD
```

Exemple :

```text
20260821
```

Cette décision sera matérialisée pendant l'implémentation.

---

# 19. dim_client

Structure candidate :

```text
dim_client
│
├── client_key
├── client_id
├── statut
└── ...
```

Attention :

les données personnelles ne doivent pas être copiées dans le Data Warehouse sans nécessité.

---

# 20. Minimisation RGPD

Le Data Warehouse doit appliquer :

```text
Data Minimization
```

Si une analyse nécessite uniquement :

```text
client_key
client_status
```

il n'est pas nécessaire de recopier :

```text
email
telephone
full name
```

---

# 21. dim_chasseur

Structure candidate :

```text
dim_chasseur
│
├── chasseur_key
├── chasseur_id
└── statut
```

Elle permet notamment d'analyser :

```text
number of mandates
number of presentations
retention rate
matching results
```

par chasseur.

---

# 22. dim_property

Structure candidate :

```text
dim_property
│
├── property_key
├── property_id
├── external_reference
├── property_type
├── city
├── postal_code
├── price_band
├── surface_band
└── status
```

---

# 23. dim_source

Structure candidate :

```text
dim_source
│
├── source_key
├── source_id
├── source_name
├── source_type
└── confidence_level
```

Elle permet d'analyser la performance des différentes sources immobilières.

---

# 24. dim_mandate

Structure candidate :

```text
dim_mandate
│
├── mandate_key
├── mandate_id
├── mandate_reference
└── status
```

Les informations personnelles directes doivent rester limitées.

---

# 25. Dimension localisation

Selon les besoins, la localisation peut rester dans :

```text
dim_property
```

ou devenir :

```text
dim_location
```

si les analyses géographiques deviennent suffisamment importantes.

Le MVP privilégiera la simplicité tant qu'une dimension dédiée n'apporte pas de valeur démontrée.

---

# 26. Surrogate Keys

Les dimensions analytiques peuvent utiliser des :

```text
Surrogate Keys
```

différentes des identifiants OLTP.

Exemple :

```text
client_id
```

identifiant source.

```text
client_key
```

identifiant dimensionnel.

---

# 27. Pourquoi des surrogate keys

Elles facilitent notamment :

- historisation ;
- indépendance du système source ;
- Slowly Changing Dimensions ;
- intégration future de plusieurs sources.

---

# 28. Slowly Changing Dimensions

Les dimensions peuvent évoluer.

Exemple :

```text
Client status:
ACTIVE
   |
   v
ARCHIVED
```

Plusieurs stratégies existent.

---

# 29. SCD Type 1

Le Type 1 remplace l'ancienne valeur.

```text
OLD
 |
 v
NEW
```

Pas d'historique.

---

# 30. SCD Type 2

Le Type 2 conserve plusieurs versions.

Exemple :

```text
client_key | client_id | status   | valid_from | valid_to
-----------------------------------------------------------
101        | 42        | ACTIVE   | ...        | ...
205        | 42        | ARCHIVED | ...        | NULL
```

---

# 31. Choix MVP

Toutes les dimensions ne nécessitent pas immédiatement SCD Type 2.

La stratégie sera appliquée uniquement lorsqu'une exigence analytique justifie l'historisation.

Il faut éviter :

```text
SCD Type 2 everywhere
```

sans besoin métier.

---

# 32. ETL

ETL signifie :

```text
Extract
Transform
Load
```

Flux :

```text
Source
 |
 v
Extract
 |
 v
Transform
 |
 v
Load
 |
 v
Warehouse
```

---

# 33. ELT

ELT signifie :

```text
Extract
Load
Transform
```

Flux :

```text
Source
 |
 v
Extract
 |
 v
Load to Staging
 |
 v
Transform inside platform
 |
 v
Warehouse
```

---

# 34. Approche du projet

Le projet privilégie une approche proche de :

```text
ELT
```

pour les données relationnelles.

Architecture :

```text
PostgreSQL OLTP
      |
      v
staging
      |
      v
SQL/dbt transformations
      |
      v
warehouse
      |
      v
analytics
```

---

# 35. Pourquoi ELT

Avantages :

- conservation d'une zone intermédiaire ;
- transformations SQL auditables ;
- possibilité de rejouer ;
- meilleure traçabilité ;
- séparation ingestion / transformation ;
- intégration avec dbt ;
- intégration avec Airflow.

---

# 36. Staging

Le schéma :

```text
staging
```

reçoit les données nécessaires provenant de l'OLTP.

Il constitue une zone technique.

Il ne doit pas être présenté directement aux utilisateurs métier comme modèle analytique final.

---

# 37. Exemple staging

Tables candidates :

```text
staging.client
staging.chasseur
staging.mandat
staging.demande_version
staging.source
staging.bien
staging.presentation
```

`document` ne doit être chargé que si son contenu analytique est réellement nécessaire.

---

# 38. Transformation

La transformation construit :

```text
dimensions
facts
business metrics
```

à partir du staging.

---

# 39. Data Warehouse

Schéma :

```text
warehouse
```

Exemple :

```text
warehouse.dim_date
warehouse.dim_client
warehouse.dim_chasseur
warehouse.dim_property
warehouse.dim_source
warehouse.dim_mandate
warehouse.fact_presentation
```

---

# 40. Analytics

Le schéma :

```text
analytics
```

peut fournir des vues orientées métier.

Exemples :

```text
analytics.presentation_kpis
analytics.source_performance
analytics.property_market_summary
analytics.matching_performance
analytics.mandate_summary
```

---

# 41. Pourquoi utiliser des vues analytics

Cela permet de masquer la complexité du warehouse aux consommateurs.

Architecture :

```text
Warehouse
    |
    v
Analytics Views
    |
    +--> Dashboard
    +--> BI
    +--> API
    +--> Analysis
```

---

# 42. Airflow

Apache Airflow est responsable de l'orchestration des workflows de données.

Airflow détermine :

```text
when
what order
dependency
retry
failure handling
```

Il ne remplace pas PostgreSQL ni le moteur SQL.

---

# 43. DAG cible

Un DAG candidat :

```text
real_estate_warehouse_etl
```

Flux :

```text
start
  |
  v
extract_oltp
  |
  v
validate_staging
  |
  v
load_dimensions
  |
  v
load_fact_presentation
  |
  v
run_data_quality
  |
  v
refresh_analytics
  |
  v
publish_metrics
  |
  v
end
```

---

# 44. Dépendances du DAG

Exemple :

```text
extract_oltp
      |
      v
validate_staging
      |
      +----------------+
      |                |
      v                v
load_dimensions   validation failure
      |
      v
load_fact
      |
      v
data_quality
      |
      v
analytics
```

---

# 45. Idempotence

Un DAG doit pouvoir être rejoué sans produire de duplication incontrôlée.

Principe :

```text
Same logical input
+
Same execution period
=
Consistent warehouse state
```

---

# 46. Incremental Loading

Il n'est pas nécessaire de recharger systématiquement toutes les données.

Une stratégie incrémentale peut exploiter :

```text
date_creation
date_version
date_collecte
date_selection
date_ajout
```

selon les entités.

---

# 47. Watermark

Une stratégie possible utilise :

```text
last_successful_timestamp
```

comme watermark.

Exemple :

```text
Previous successful run:
2026-08-20 02:00

Current run:
2026-08-21 02:00
```

Le pipeline traite la fenêtre pertinente.

---

# 48. Attention aux mises à jour

Une stratégie basée uniquement sur :

```text
created_at
```

ne détecte pas nécessairement les modifications de lignes existantes.

Une future évolution peut nécessiter :

```text
updated_at
CDC
```

ou une stratégie de comparaison.

---

# 49. CDC

CDC signifie :

```text
Change Data Capture
```

Il peut devenir utile pour des volumes ou besoins temps réel plus importants.

Le MVP n'impose pas encore CDC.

---

# 50. Kafka

Kafka n'est pas une dépendance obligatoire de cette architecture analytique.

Le pipeline MVP peut fonctionner :

```text
PostgreSQL
   |
   v
Airflow
   |
   v
Warehouse
```

Kafka ne doit être introduit que si un besoin réel de streaming ou d'event-driven data integration le justifie.

---

# 51. dbt

dbt peut être utilisé pour :

```text
SQL transformations
models
tests
documentation
lineage
```

Il complète Airflow.

---

# 52. Airflow vs dbt

Responsabilités :

```text
Airflow
   |
   +--> orchestration
   +--> scheduling
   +--> dependencies
   +--> retries
```

```text
dbt
   |
   +--> SQL transformation
   +--> model dependencies
   +--> SQL tests
   +--> transformation documentation
```

Ils ne remplissent pas exactement le même rôle.

---

# 53. Architecture Airflow + dbt

```text
Airflow DAG
    |
    +--> Extract
    |
    +--> dbt run
    |
    +--> dbt test
    |
    +--> publish metrics
```

---

# 54. Data Quality

Le pipeline analytique doit vérifier la qualité avant publication.

Contrôles candidats :

```text
not_null
unique
relationships
accepted_values
row_count
range checks
freshness
```

---

# 55. Exemple fact_presentation

Contrôles :

```text
presentation_key NOT NULL
presentation_key UNIQUE
property_key NOT NULL
date_key NOT NULL
matching_score BETWEEN 0 AND 100
```

---

# 56. Referential Quality

Chaque :

```text
property_key
```

de la fact doit correspondre à une dimension valide.

Même principe pour :

```text
client_key
chasseur_key
source_key
date_key
```

---

# 57. Row Count

Le pipeline peut comparer :

```text
source rows
staging rows
warehouse rows
```

selon les règles de transformation.

Une différence doit être explicable.

---

# 58. Freshness

Une donnée analytique peut être correcte mais obsolète.

Un contrôle de fraîcheur doit pouvoir vérifier :

```text
last successful load
```

---

# 59. Lineage

La traçabilité doit permettre :

```text
OLTP column
     |
     v
Staging column
     |
     v
Warehouse column
     |
     v
Analytics KPI
```

---

# 60. Exemple lineage

```text
real_estate.presentation.score_matching
              |
              v
staging.presentation.score_matching
              |
              v
warehouse.fact_presentation.matching_score
              |
              v
analytics.matching_performance
              |
              v
Average Matching Score KPI
```

---

# 61. OpenMetadata

OpenMetadata peut documenter :

- tables ;
- colonnes ;
- propriétaires ;
- descriptions ;
- classification ;
- lineage ;
- qualité ;
- domaines.

L'objectif est de rendre le patrimoine Data compréhensible et gouvernable.

---

# 62. Catalogue

Exemple :

```text
PostgreSQL Service
   |
   +--> real_estate
   |
   +--> staging
   |
   +--> warehouse
   |
   +--> analytics
```

---

# 63. KPI candidat — nombre de présentations

```sql
COUNT(*)
```

sur le grain de :

```text
fact_presentation
```

---

# 64. KPI candidat — score moyen

```sql
AVG(matching_score)
```

---

# 65. KPI candidat — taux de rejet

Conceptuellement :

```text
Rejected Presentations
----------------------
Total Presentations
```

---

# 66. KPI candidat — taux de visite

```text
Visited
-------
Presented
```

La définition exacte du dénominateur doit être documentée pour éviter des KPI ambigus.

---

# 67. KPI candidat — taux de rétention

```text
Retained
--------
Presented
```

---

# 68. KPI candidat — performance source

Analyse par :

```text
source
```

de :

- nombre de biens ;
- biens qualifiés ;
- biens présentés ;
- score moyen ;
- taux de rétention.

---

# 69. KPI candidat — prix moyen

```sql
AVG(property_price)
```

par :

```text
city
property_type
month
```

---

# 70. KPI candidat — surface moyenne

```sql
AVG(property_surface)
```

par segment.

---

# 71. KPI candidat — activité mandat

Exemples :

```text
number of active mandates
presentations per mandate
average request versions per mandate
```

---

# 72. KPI et gouvernance

Chaque KPI important doit avoir :

```text
Name
Definition
Formula
Source
Owner
Refresh frequency
Quality rule
```

---

# 73. Exemple de définition KPI

```text
KPI:
Average Matching Score

Definition:
Average score_matching for presentations
where matching_score is not null.

Source:
warehouse.fact_presentation

Refresh:
After successful warehouse pipeline
```

---

# 74. Agrégations

Les agrégations doivent être calculées dans le système analytique plutôt que dans le frontend lorsque cela est pertinent.

À éviter :

```text
Download 1,000,000 rows
        |
        v
Browser
        |
        v
SUM()
```

Préférer :

```text
Database aggregation
        |
        v
Small result
        |
        v
Dashboard
```

---

# 75. Performance OLAP

Les optimisations OLAP peuvent être différentes des optimisations OLTP.

Exemples :

```text
indexes
partitioning
materialized views
pre-aggregation
columnar systems
```

Elles doivent être introduites selon les besoins mesurés.

---

# 76. Materialized Views

Une vue matérialisée peut devenir pertinente pour des calculs coûteux et fréquemment consultés.

Exemple futur :

```text
monthly_market_summary
```

Mais elle introduit un problème de fraîcheur et de rafraîchissement.

Elle n'est pas automatiquement nécessaire au MVP.

---

# 77. Partitioning

Une table de faits importante peut éventuellement être partitionnée par :

```text
date
```

Mais le partitionnement ne doit pas être introduit uniquement pour afficher une architecture complexe.

Il doit répondre à un volume ou workload réel.

---

# 78. Volume initial

Le MVP peut fonctionner avec PostgreSQL standard.

L'architecture doit néanmoins permettre de démontrer les concepts OLAP sur un dataset suffisamment représentatif.

---

# 79. Données synthétiques

Comme pour les benchmarks OLTP, des données synthétiques peuvent être générées pour démontrer :

- agrégations ;
- alimentation ;
- qualité ;
- historique ;
- performance.

Elles doivent être clairement identifiées comme synthétiques.

---

# 80. Reproductibilité

La construction du warehouse devra être automatisable.

Exemple :

```text
Create schemas
   |
   v
Load source data
   |
   v
Run Airflow
   |
   v
Build warehouse
   |
   v
Run quality tests
   |
   v
Query KPIs
```

---

# 81. GitOps

Les définitions de déploiement Airflow doivent être versionnées.

Exemples :

```text
Helm values
Kubernetes manifests
DAG repository configuration
```

---

# 82. DAG as Code

Les DAG Airflow sont stockés dans Git.

Cela permet :

```text
Versioning
Review
Rollback
Audit
```

---

# 83. SQL as Code

Les transformations SQL sont également versionnées.

Le Data Warehouse ne doit pas dépendre uniquement de modifications manuelles exécutées directement dans PostgreSQL.

---

# 84. Secrets

Les credentials PostgreSQL ne doivent pas être codés dans :

```text
DAG
SQL
Git repository
```

Ils doivent être injectés via la stratégie de secrets de la plateforme.

---

# 85. Airflow Connection

La connexion Airflow vers PostgreSQL devra être fournie par un mécanisme sécurisé.

Architecture logique :

```text
Airflow
   |
   | credential reference
   v
Secret Management
   |
   v
PostgreSQL
```

---

# 86. Failure Handling

Un pipeline peut échouer.

Exemples :

```text
database unavailable
invalid data
constraint failure
transformation error
network failure
```

Le DAG doit rendre l'échec visible.

---

# 87. Retry

Certaines erreurs temporaires peuvent être retentées.

Exemple :

```text
temporary database connection failure
```

Mais une erreur de données ne doit pas être retentée indéfiniment sans diagnostic.

---

# 88. Alerting

Un échec critique du pipeline doit pouvoir produire :

```text
Airflow task failure
        |
        v
Metric / Event
        |
        v
Alerting
```

---

# 89. Observabilité

Le pipeline doit être observable via :

```text
Airflow UI
logs
metrics
Prometheus
Grafana
```

selon l'intégration disponible.

---

# 90. Métriques candidates

```text
pipeline_success
pipeline_failure
pipeline_duration
rows_extracted
rows_loaded
quality_checks_failed
warehouse_freshness
```

---

# 91. Audit

Une exécution doit permettre de répondre :

```text
When did the pipeline run?
Did it succeed?
How many rows were processed?
Which version of the code was used?
Were quality checks successful?
```

---

# 92. Rejeu

Le pipeline doit permettre un rejeu contrôlé.

Cela est particulièrement important après :

- correction d'un bug ;
- restauration ;
- changement de transformation ;
- incident.

---

# 93. Backfill

Airflow peut permettre de recalculer des périodes historiques.

Exemple :

```text
2026-07-01
...
2026-07-31
```

Le pipeline doit être conçu pour éviter les doublons lors de ces opérations.

---

# 94. OLAP et IA

Le Data Warehouse peut également fournir des features ou indicateurs utiles à l'IA.

Architecture :

```text
Operational Data
      |
      v
Warehouse
      |
      +--> BI
      |
      +--> Analytics
      |
      +--> ML / AI
```

---

# 95. Séparation analytique / RAG

Le Data Warehouse n'est pas la même chose qu'une base vectorielle.

```text
Warehouse
   |
   +--> structured analytics
```

```text
Vector store
   |
   +--> semantic retrieval
```

Ces responsabilités ne doivent pas être confondues.

---

# 96. Preuves runtime attendues

La compétence devra être démontrée avec des preuves réelles.

Exemples :

```text
PostgreSQL schemas
Airflow DAG
successful DAG run
staging tables
warehouse tables
fact table
dimension tables
analytics views
data quality tests
KPI query results
lineage
```

---

# 97. Structure future des preuves

Le dossier pourra devenir :

```text
C3-OLAP-Alimentation/
│
├── README.md
├── sql/
│   ├── create-staging.sql
│   ├── create-warehouse.sql
│   └── create-analytics.sql
│
├── airflow/
│   └── real_estate_warehouse_etl.py
│
├── dbt/
│   └── ...
│
├── tests/
│   └── ...
│
├── evidence/
│   ├── airflow-success.png
│   ├── warehouse-tables.txt
│   ├── quality-results.txt
│   └── kpi-results.txt
│
└── EXECUTION-REPORT.md
```

Ces fichiers seront produits pendant l'implémentation.

---

# 98. Ce qui constitue une preuve forte

```text
Source OLTP populated
        |
        v
Airflow DAG executed
        |
        v
Staging populated
        |
        v
Dimensions populated
        |
        v
Fact populated
        |
        v
Quality tests PASS
        |
        v
KPI query returns expected results
```

---

# 99. Ce qui ne suffit pas

Les affirmations suivantes ne constituent pas seules une preuve :

```text
"We use a Data Warehouse."

"We use Airflow."

"We use OLAP."

"We have fact and dimension tables."
```

Il faut montrer leur existence et leur exécution.

---

# 100. Matrice de preuve

| Élément | Baseline documentaire | Preuve future |
|---|---|---|
| Séparation OLTP/OLAP | README | Schemas PostgreSQL |
| Staging | Défini | Tables |
| Star schema | Défini | DDL |
| Dimensions | Définies | Tables + rows |
| Fact | Définie | Table + rows |
| ETL/ELT | Défini | DAG |
| Orchestration | Airflow | Successful run |
| Data Quality | Règles définies | Test results |
| KPI | Candidats définis | SQL results |
| Lineage | Défini | OpenMetadata / evidence |
| Observabilité | Définie | Metrics / logs |

---

# 101. Relation avec C1

```text
C1
MCD
 |
 v
MLD
 |
 v
MPD
 |
 v
OLTP
```

alimente :

```text
C3
Staging
 |
 v
Warehouse
 |
 v
Analytics
```

---

# 102. Relation avec C2

C2 optimise les transactions opérationnelles.

C3 évite notamment de transformer l'OLTP en moteur analytique général.

```text
OLTP
transaction workload

OLAP
analytical workload
```

---

# 103. Relation avec C4

C4 analysera :

```text
Volume
Velocity
Variety
```

afin de déterminer si l'architecture actuelle reste adaptée lorsque les caractéristiques des données évoluent.

---

# 104. Relation avec C5/C6

Les données préparées peuvent contribuer aux traitements :

```text
Matching
Machine Learning
AI
```

mais la logique analytique ne doit pas être confondue avec le modèle IA lui-même.

---

# 105. Relation avec C7

La duplication de données depuis OLTP vers OLAP augmente les responsabilités RGPD.

Il faut donc contrôler :

```text
What is copied?
Why?
How long?
Who can access it?
```

---

# 106. Relation avec C8

Les données utilisées par l'IA et l'analytics doivent respecter les exigences de :

```text
sovereignty
security
confidentiality
governance
```

---

# 107. Décisions retenues

Pour le MVP :

```text
OLTP:
PostgreSQL / real_estate

Staging:
PostgreSQL / staging

Warehouse:
PostgreSQL / warehouse

Analytics:
PostgreSQL / analytics

Orchestration:
Airflow

Transformation:
SQL + Python
dbt where justified

Metadata:
OpenMetadata
```

---

# 108. Technologies non obligatoires

Le MVP n'impose pas :

```text
Kafka
Spark
Flink
Dedicated cloud warehouse
Dedicated columnar database
```

Ces technologies doivent être introduites uniquement si le besoin les justifie.

---

# 109. Principe architectural

La plateforme suit :

```text
Use the simplest architecture
that satisfies the requirement
and remains evolvable.
```

---

# 110. Critères de réussite

C3 sera considérée démontrée lorsque nous disposerons de :

```text
Working OLTP source
+
Working staging
+
Working dimensional warehouse
+
Working fact/dimensions
+
Automated alimentation
+
Successful Airflow execution
+
Data quality validation
+
Business KPI result
+
Traceability
```

---

# 111. Statut actuel

| Élément | Statut |
|---|---|
| OLTP/OLAP separation | DOCUMENTÉE |
| OLAP architecture | DOCUMENTÉE |
| Staging strategy | DÉFINIE |
| Warehouse strategy | DÉFINIE |
| Star schema | BASELINE DÉFINIE |
| Fact grain | DÉFINI |
| Dimensions | IDENTIFIÉES |
| ETL/ELT strategy | DÉFINIE |
| Airflow orchestration | DÉFINIE |
| dbt integration | CANDIDATE / SELON BESOIN |
| Data Quality strategy | DÉFINIE |
| KPI candidates | DÉFINIS |
| Lineage strategy | DÉFINIE |
| Runtime warehouse | À IMPLÉMENTER |
| DAG execution | À PRODUIRE |
| Quality evidence | À PRODUIRE |
| KPI evidence | À PRODUIRE |

---

# 112. Conclusion

L'architecture analytique du Real Estate Intelligence Platform sépare clairement :

```text
Operational Processing
```

de :

```text
Analytical Processing
```

La chaîne cible est :

```text
PostgreSQL OLTP
      |
      v
Staging
      |
      v
Transformation
      |
      v
Dimensional Warehouse
      |
      v
Analytics
      |
      +--> KPI
      +--> Dashboards
      +--> Data Analysis
      +--> AI
```

Airflow assure l'orchestration, PostgreSQL fournit le stockage relationnel, et OpenMetadata contribue à la gouvernance et à la traçabilité.

Les preuves finales devront provenir de l'exécution réelle du pipeline et non uniquement de cette conception documentaire.

---

**BC05 / C3 — OLAP & ALIMENTATION — DOCUMENTATION BASELINE COMPLETE**