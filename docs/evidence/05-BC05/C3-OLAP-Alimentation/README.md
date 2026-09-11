# BC05 — C3 — OLAP & Alimentation

**Bloc de compétences :** BC05  
**Compétence :** Concevoir et alimenter une architecture décisionnelle adaptée aux traitements analytiques  
**Projet :** Real Estate Intelligence Platform  
**Version :** 2.0  
**Statut :** Warehouse, chargement et dbt implémentés — preuves historiques disponibles et état courant à consolider
**Source OLTP :** PostgreSQL / `real_estate`  
**Orchestration cible :** Apache Airflow  
**Transformation :** SQL / Python / dbt lorsque justifié  
**Metadata & lineage :** OpenMetadata  

---

# 1. Objectif

Cette partie décrit la transformation des données opérationnelles du projet vers une architecture analytique.

Le système doit permettre :

```text
Operational Transactions
        |
        v
Structured OLTP
        |
        v
Extraction / Load
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
Analytics / KPI
```

L'objectif est de séparer :

```text
le fonctionnement opérationnel
```

de :

```text
l'analyse et le pilotage
```

---

# 2. Contexte métier

Le StarterPack prévoit une croissance importante de l'activité :

```text
plusieurs milliers de mandats par semaine
```

et potentiellement :

```text
plusieurs centaines
voire milliers de biens
par recherche
```

avec extension progressive à plusieurs pays européens. 

Le système analytique doit donc être conçu pour évoluer sans transformer la base transactionnelle en moteur de reporting généraliste.

---

# 3. Modèle OLTP source V2

Le modèle transactionnel cible comprend notamment :

```text
CLIENT
CHASSEUR
SECTEUR
MANDAT
MANDAT_SECTEUR
DEMANDE
DEMANDE_VERSION
SOURCE
BIEN
PRESENTATION
COMMENTAIRE
DOCUMENT
BAREME_COMMISSION
PAIEMENT
```

Schéma PostgreSQL :

```text
real_estate
```

---

# 4. Pourquoi séparer OLTP et OLAP

L'OLTP est optimisé pour :

```text
INSERT
UPDATE
DELETE
targeted SELECT
short transactions
referential integrity
```

L'OLAP est optimisé pour :

```text
aggregation
historical analysis
GROUP BY
large scans
business KPI
reporting
```

---

# 5. Exemple

Une requête opérationnelle :

```text
Afficher le mandat n°123
```

est très différente d'une requête analytique :

```text
Calculer le taux moyen de conversion
par chasseur, par secteur,
sur les 12 derniers mois
```

Les deux workloads ne doivent pas être optimisés de la même manière.

---

# 6. Architecture cible

```text
                    PostgreSQL
              +---------------------+
              |     real_estate     |
              |       OLTP          |
              +----------+----------+
                         |
                         v
              +---------------------+
              |       staging       |
              +----------+----------+
                         |
                         v
              +---------------------+
              |      warehouse      |
              +----------+----------+
                         |
                         v
              +---------------------+
              |      analytics      |
              +----------+----------+
                         |
          +--------------+--------------+
          |                             |
          v                             v
      Dashboard                     AI / ML
```

---

# 7. Schémas PostgreSQL

La première architecture analytique utilise la même instance PostgreSQL avec séparation logique :

```text
real_estate
staging
warehouse
analytics
```

Cela limite la complexité du MVP.

---

# 8. Pourquoi PostgreSQL reste suffisant

Le projet n'a pas besoin immédiatement :

```text
Snowflake
BigQuery
Spark
ClickHouse
Kafka
```

simplement parce que des volumes futurs sont annoncés.

La décision doit être prise à partir :

```text
des volumes réellement mesurés
de la latence
du temps de traitement
de la concurrence
des SLO
```

---

# 9. ELT privilégié

L'architecture privilégie :

```text
Extract
Load
Transform
```

Flux :

```text
real_estate
     |
     v
staging
     |
     v
SQL / dbt
     |
     v
warehouse
```

---

# 10. Pourquoi ELT

Avantages :

```text
rejouabilité
auditabilité
SQL versionné
lineage
séparation ingestion/transformation
data quality
```

---

# 11. Staging

Le schéma :

```text
staging
```

est une zone technique.

Il permet notamment :

```text
type normalization
deduplication
preparation
business validation
```

---

# 12. Tables staging candidates

```text
staging.client
staging.chasseur
staging.secteur
staging.mandat
staging.demande
staging.demande_version
staging.source
staging.bien
staging.presentation
staging.commentaire
staging.bareme_commission
staging.paiement
```

Toutes les tables OLTP ne doivent pas obligatoirement être recopiées si aucune analyse ne les utilise.

---

# 13. Minimisation

Le staging analytique ne doit pas devenir une copie intégrale incontrôlée de toutes les données.

Principe :

```text
Extract only what is needed
for defined analytical purposes
```

---

# 14. Modèle dimensionnel

Le warehouse adopte une approche dimensionnelle.

Concepts :

```text
FACT
DIMENSION
GRAIN
MEASURE
```

---

# 15. Faits principaux candidats

Le modèle V2 fait apparaître plusieurs événements analytiques pertinents.

Tables de faits candidates :

```text
fact_presentation
fact_mandate
fact_payment
```

et éventuellement plus tard :

```text
fact_visit
fact_offer
```

si les entités correspondantes sont implémentées.

---

# 16. Fact principale — fact_presentation

Pour la première version analytique, la table principale est :

```text
fact_presentation
```

Elle permet d'analyser :

```text
matching
sélections
présentations
rejets
visites
rétentions
```

---

# 17. Grain de fact_presentation

Le grain est :

> Une ligne représente un bien associé à une version précise d'une demande.

Donc :

```text
1 row
=
1 DEMANDE_VERSION
+
1 BIEN
```

---

# 18. Structure candidate

```text
fact_presentation
│
├── presentation_key
├── date_selection_key
├── date_presentation_key
│
├── demande_key
├── demande_version_key
├── mandate_key
├── client_key
├── chasseur_key
├── property_key
├── source_key
├── sector_key
│
├── matching_score
├── property_price
├── property_surface
│
├── presented_count
├── rejected_count
├── retained_count
└── visited_count
```

---

# 19. fact_mandate

Une seconde table de faits peut représenter le cycle de vie des mandats.

Grain :

```text
1 row
=
1 mandate
```

Mesures possibles :

```text
mandate_duration_days
number_of_request_versions
number_of_presentations
successful_purchase
```

---

# 20. fact_payment

La nouvelle entité `PAIEMENT` permet une analyse financière réelle.

Grain :

```text
1 row
=
1 payment event
```

Mesures :

```text
purchase_amount
company_fee
hunter_payment
payment_delay
```

---

# 21. Dimensions principales

Dimensions candidates :

```text
dim_date
dim_client
dim_chasseur
dim_sector
dim_property
dim_source
dim_mandate
dim_request
```

---

# 22. dim_date

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

# 23. dim_client

La dimension client doit être minimisée.

Elle peut contenir :

```text
client_key
source_client_id
status
city
```

mais ne nécessite pas automatiquement :

```text
email
telephone
full identity
```

---

# 24. dim_chasseur

```text
dim_chasseur
│
├── chasseur_key
├── source_chasseur_id
├── status
└── seniority_band
```

Les indicateurs de performance ne doivent pas être stockés comme vérités statiques si leur calcul dépend d'événements.

---

# 25. dim_sector

```text
dim_sector
│
├── sector_key
├── country
├── city
├── district
└── postal_code
```

Cette dimension devient particulièrement importante avec l'expansion internationale.

---

# 26. dim_property

```text
dim_property
│
├── property_key
├── source_property_id
├── property_type
├── city
├── postal_code
├── dpe
├── price_band
└── surface_band
```

---

# 27. dim_source

```text
dim_source
│
├── source_key
├── source_name
├── source_type
└── confidence_level
```

Elle permet d'analyser les performances des différentes sources d'annonces.

---

# 28. dim_mandate

```text
dim_mandate
│
├── mandate_key
├── mandate_reference
├── mandate_type
├── status
└── signature_mode
```

---

# 29. dim_request

La demande et sa version peuvent être représentées selon deux stratégies :

```text
dimension unique
```

ou :

```text
dim_request
+
request version fields in fact
```

La stratégie finale sera choisie lors de l'implémentation du warehouse.

---

# 30. Slowly Changing Dimensions

Certaines dimensions évoluent dans le temps.

Exemple :

```text
CHASSEUR
status changes

CLIENT
status changes

SECTOR
active/inactive
```

---

# 31. SCD Type 1

Type 1 :

```text
old value
    |
    v
new value
```

L'historique est perdu.

---

# 32. SCD Type 2

Type 2 conserve les versions :

```text
key
business_id
valid_from
valid_to
is_current
```

---

# 33. Usage SCD

Le projet ne doit pas appliquer SCD2 partout.

SCD2 doit être utilisé uniquement lorsque l'historique de la dimension est nécessaire au besoin analytique.

---

# 34. Historique des demandes

`DEMANDE_VERSION` est déjà historisée dans l'OLTP.

Il n'est donc pas nécessaire de recréer artificiellement cet historique avec une autre technique si la source contient déjà toutes les versions.

---

# 35. Historique des commissions

Même principe pour :

```text
BAREME_COMMISSION
```

Le modèle opérationnel contient déjà :

```text
date_debut_validite
date_fin_validite
```

---

# 36. Airflow

Airflow orchestre l'alimentation du warehouse.

Nom de DAG candidat :

```text
real_estate_warehouse_etl
```

---

# 37. DAG cible

```text
start
  |
  v
extract_operational_data
  |
  v
load_staging
  |
  v
validate_staging
  |
  v
load_dimensions
  |
  v
load_fact_mandate
  |
  v
load_fact_presentation
  |
  v
load_fact_payment
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

# 38. Dépendances

```text
load_staging
      |
      v
validate_staging
      |
      v
load_dimensions
      |
      +--------------------+
      |         |          |
      v         v          v
 mandate    presentation payment
      |         |          |
      +---------+----------+
                |
                v
         data_quality
                |
                v
            analytics
```

---

# 39. dbt

dbt peut assurer :

```text
dimension models
fact models
business views
tests
documentation
lineage
```

Airflow reste responsable de l'orchestration globale.

---

# 40. Idempotence

Un pipeline rejoué ne doit pas dupliquer les données.

Principe :

```text
same source state
+
same transformation
=
consistent warehouse state
```

---

# 41. Incremental Loads

Les chargements pourront utiliser :

```text
date_creation
date_version
date_collecte
date_selection
date_commentaire
date_debut_validite
date_reception_honoraires
```

comme points de repère.

---

# 42. updated_at

Une amélioration future du modèle opérationnel peut introduire :

```text
updated_at
```

sur certaines entités afin de faciliter les chargements incrémentaux.

---

# 43. CDC

Change Data Capture n'est pas nécessaire pour le MVP.

Il pourrait devenir pertinent si la fraîcheur attendue devient :

```text
near-real-time
```

et que le batch n'est plus suffisant.

---

# 44. Data Quality — staging

Exemples :

```text
valid data types
required business columns
non-negative amounts
valid dates
known statuses
```

---

# 45. Data Quality — warehouse

Exemples :

```text
fact primary key unique
dimension keys not null
foreign dimension references valid
scores within expected range
financial values non-negative
```

---

# 46. Data Quality — fact_presentation

```text
presentation_key NOT NULL
presentation_key UNIQUE
property_key NOT NULL
request_version_key NOT NULL
matching_score BETWEEN 0 AND 100
```

lorsque `matching_score` est renseigné.

---

# 47. Data Quality — fact_payment

```text
purchase_amount >= 0
company_fee >= 0
hunter_payment >= 0
```

et :

```text
hunter_payment <= company_fee
```

si cette règle correspond au modèle métier final.

---

# 48. Referential Quality

Une fact ne doit pas référencer une dimension inexistante.

Exemple :

```text
fact_presentation.property_key
```

doit correspondre à :

```text
dim_property.property_key
```

---

# 49. Row Count Controls

Contrôles possibles :

```text
source rows
staging rows
warehouse rows
```

Les écarts doivent être explicables.

---

# 50. Freshness

Mesure :

```text
last_successful_load
```

Le warehouse doit permettre de savoir quand les données ont été actualisées.

---

# 51. OpenMetadata

OpenMetadata doit permettre de visualiser :

```text
OLTP
 |
 v
STAGING
 |
 v
WAREHOUSE
 |
 v
ANALYTICS
```

avec lineage lorsque l'intégration est disponible.

---

# 52. Lineage exemple matching

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
```

---

# 53. Lineage financier

```text
real_estate.paiement.montant_honoraires
           |
           v
staging.paiement
           |
           v
warehouse.fact_payment.company_fee
           |
           v
analytics.revenue_summary
```

---

# 54. KPI Matching

Exemples :

```text
average matching score
number of properties presented
rejection rate
retention rate
visit rate
```

---

# 55. KPI Demand

Exemples :

```text
average number of versions per demand
requalification frequency
average candidate properties per demand
```

---

# 56. KPI Mandat

Exemples :

```text
active mandates
completed mandates
expired mandates
average mandate duration
exclusive vs non-exclusive distribution
```

---

# 57. KPI Chasseur

Exemples :

```text
mandates managed
successful transactions
average completion time
presentations per mandate
revenue generated
```

---

# 58. KPI Source

Exemples :

```text
properties collected
properties qualified
properties presented
properties retained
average matching score
```

---

# 59. KPI Financial

Grâce au modèle V2 :

```text
total purchase value
total company fees
total hunter payments
average fee per transaction
payment delays
```

peuvent maintenant être calculés.

---

# 60. KPI Sector

Avec `SECTEUR` :

```text
mandates per sector
properties per sector
success rate per sector
average property price
```

---

# 61. International Analytics

Le modèle doit pouvoir grouper par :

```text
country
city
sector
```

sans dépendre uniquement d'un code postal français.

---

# 62. Business KPI Definition

Chaque KPI important doit être documenté avec :

```text
Name
Business definition
Formula
Source
Refresh frequency
Owner
Quality rule
```

---

# 63. Exemple KPI

```text
Name:
Retention Rate

Definition:
Percentage of presented properties
that reach RETENU status.

Numerator:
retained presentations

Denominator:
presented properties

Source:
fact_presentation
```

---

# 64. Attention aux définitions

Un taux n'est utile que si le dénominateur est clairement défini.

Exemple :

```text
RETENU / IDENTIFIE
```

n'est pas nécessairement équivalent à :

```text
RETENU / PRESENTE
```

---

# 65. Performance

Le warehouse peut nécessiter :

```text
indexes
materialized views
partitioning
pre-aggregation
```

mais uniquement après mesure.

---

# 66. Materialized Views

Une vue matérialisée peut être utile pour :

```text
monthly_matching_summary
```

ou :

```text
monthly_revenue_summary
```

si les agrégations deviennent coûteuses.

---

# 67. Partitioning

Avec la croissance officielle du projet, les facts historiques peuvent devenir candidates au partitionnement.

Exemples :

```text
fact_presentation
fact_payment
```

partitionnées par date.

Cela reste une évolution mesurée.

---

# 68. Growth Scenario

La capacité doit être testée à partir du contexte officiel :

```text
thousands of mandates / week
```

multiplié par :

```text
hundreds / thousands
of properties / search
```

Le nombre potentiel de relations de matching peut devenir très supérieur au nombre de mandats.

---

# 69. Exemple conceptuel

Si :

```text
5,000 mandates / week
```

et :

```text
500 candidate properties / mandate
```

alors :

```text
2,500,000
candidate relations / week
```

peuvent être considérées.

Cette valeur est un scénario de calcul, pas une mesure du système réel.

---

# 70. Pourquoi fact_presentation peut croître vite

La table de faits liée au matching peut devenir beaucoup plus volumineuse que :

```text
CLIENT
MANDAT
DEMANDE
```

car elle représente les relations :

```text
search x property
```

---

# 71. Data Retention

Toutes les relations candidates de matching ne doivent pas nécessairement être conservées indéfiniment.

Une politique pourra distinguer :

```text
candidate
qualified
presented
retained
```

selon la valeur analytique et les besoins d'audit.

---

# 72. Eco-conception

Le stockage analytique doit appliquer :

```text
store useful data
avoid unnecessary duplication
control retention
aggregate where justified
```

---

# 73. RGPD

Les données personnelles doivent être minimisées.

Exemple :

```text
CLIENT.email
```

n'est normalement pas nécessaire dans :

```text
fact_presentation
```

---

# 74. Pseudonymisation analytique

Le warehouse peut utiliser :

```text
surrogate keys
```

sans propager l'identité directe.

---

# 75. Documents

Les fichiers binaires ne doivent pas être chargés dans le warehouse.

Seules les métadonnées analytiquement utiles peuvent être intégrées.

---

# 76. AI and Warehouse

Le warehouse peut fournir :

```text
historical outcomes
aggregated behavior
matching statistics
```

aux workflows IA.

---

# 77. Attention ML

Le StarterPack demande principalement de concevoir les données et features nécessaires au modèle de matching ; l'entraînement n'est pas une exigence obligatoire. 

Le warehouse doit donc être utile même sans modèle ML entraîné.

---

# 78. Matching Features

Données possibles :

```text
budget difference
surface difference
city match
property type match
room difference
DPE match
preference matches
historical feedback
```

---

# 79. Streaming

Kafka n'est pas nécessaire à cette architecture.

Le besoin officiel décrit surtout :

```text
large volume
repeated matching
daily / multiple daily selection
```

mais pas une obligation de traitement événementiel sub-seconde. 

---

# 80. Batch Architecture

La baseline reste :

```text
PostgreSQL
+
Airflow
+
dbt/SQL
```

pour l'analytique.

---

# 81. Future Architecture

Si les mesures montrent que PostgreSQL ne satisfait plus les objectifs :

```text
Dedicated OLAP engine
Data Lake
distributed processing
streaming platform
```

pourront être évalués via une nouvelle décision d'architecture.

---

# 82. Evidence Runtime

## Chaîne documentée et état du code

Le rapport `ARCHITECTURE-DATA-IMPLEMENTEE.md` décrit la validation du 24 août 2026 : chaîne Data, warehouse marché, trois modèles dbt exécutés et dix-neuf tests dbt réussis, ainsi que l'ingestion et la lineage OpenMetadata.

Ces résultats sont ceux du périmètre décrit à cette date. Ils ne doivent pas être appliqués automatiquement aux modèles ajoutés depuis.

Le code actuel comporte les dimensions et faits suivants :

```text
warehouse
   |
   +--> dim_date / dim_source / dim_localisation / dim_bien
   +--> dim_client / dim_chasseur / dim_secteur
   +--> dim_demande_version
   +--> fact_annonce
   +--> fact_mandat
   +--> bridge_mandat_secteur
   +--> fact_presentation
   +--> fact_paiement
```

La migration 003 définit ces objets et `load_warehouse.py` contient leur alimentation depuis les tables `real_estate`. Le code actuel étend donc le périmètre marché décrit dans le rapport initial. La présence du chargement d'un fait ne démontre pas qu'il contient déjà des observations métier suffisantes.

## Sources de preuve

```text
../../../40-DATA/ARCHITECTURE-DATA-IMPLEMENTEE.md
../../../../database/migrations/003_warehouse_schema.sql
../../../../database/olap/load_warehouse.py
../../../../database/tests/007_warehouse_data_quality.sql
../../../../pipelines/airflow/real_estate_ingestion_dag.py
../../../../pipelines/dbt/models/
../../../../.gitlab/ci/warehouse.yml
```

Les preuves de peuplement, de qualité et de lineage des faits métier étendus restent à rattacher à leur exécution. Le modèle de rémunération ne devient pas opérationnel du seul fait que `fact_paiement` existe.

Les preuves finales devront inclure :

```text
warehouse DDL
Airflow DAG
successful DAG run
dimension rows
fact rows
quality tests
analytics queries
lineage evidence
```

---

# 83. Structure d'implémentation

Les artifacts réels seront stockés hors documentation :

```text
database/olap/
pipelines/airflow/
pipelines/dbt/
database/tests/
```

Ce dossier :

```text
docs/evidence/05-BC05/C3-OLAP-Alimentation/
```

reste un dossier documentaire et d'index des preuves.

---

# 84. Structure cible implementation

```text
database/olap/
│
├── 001_create_staging.sql
├── 002_create_dimensions.sql
├── 003_create_facts.sql
└── 004_create_analytics.sql
```

et :

```text
pipelines/airflow/
└── real_estate_warehouse_etl.py
```

---

# 85. Evidence References

Les preuves pourront être référencées depuis ce README sous forme :

```text
Implementation:
../../../../database/olap/

Pipeline:
../../../../pipelines/airflow/

Tests:
../../../../database/tests/
```

Ces répertoires existent. La section 82 référence les fichiers effectivement utilisés ; les résultats d'exécution complémentaires restent à rattacher.

---

# 86. Minimum Runtime Demonstration

```text
1. Populate real_estate
2. Execute staging load
3. Populate dimensions
4. Populate facts
5. Execute Data Quality
6. Query analytics
7. Show successful Airflow run
```

---

# 87. Ce qui ne suffit pas

Ne constituent pas seules une preuve :

```text
"We use OLAP"

"We have Airflow"

"We designed a star schema"

"We use PostgreSQL"
```

Il faut montrer l'alimentation réelle.

---

# 88. Matrice de preuve

| Élément | Documentation | Runtime |
|---|---|---|
| OLTP/OLAP separation | COMPLETE | PostgreSQL schemas |
| Staging | DEFINED | SQL tables |
| Dimensions | DEFINED | populated dimensions |
| fact_presentation | DEFINED | populated fact |
| fact_mandate | DEFINED | populated fact |
| fact_payment | DEFINED | populated fact |
| Airflow | DEFINED | successful DAG |
| dbt/SQL transformations | DEFINED | executed transformations |
| Data Quality | DEFINED | test report |
| KPI | DEFINED | query results |
| Lineage | DEFINED | OpenMetadata evidence |
| Growth strategy | DEFINED | benchmark |

---

# 89. Relations avec C1

```text
MCD / MLD / MPD
       |
       v
real_estate OLTP
       |
       v
C3 OLAP
```

---

# 90. Relation avec C2

C2 optimise :

```text
transactional queries
```

C3 isole :

```text
analytical workloads
```

pour éviter que les analyses perturbent l'OLTP.

---

# 91. Relation avec C4

C4 mesure :

```text
Volume
Velocity
Variety
```

et permet de déterminer quand cette architecture doit évoluer.

---

# 92. Relation avec C5

Les résultats analytiques peuvent alimenter la conception des features et l'évaluation du matching.

---

# 93. Relation avec C7

Le warehouse applique :

```text
data minimization
retention
controlled access
```

aux données personnelles.

---

# 94. Statut actuel

| Élément | Statut |
|---|---|
| OLTP source model V2 | COMPLETE |
| OLAP architecture | UPDATED |
| Staging strategy | UPDATED |
| Dimensions | UPDATED |
| fact_presentation | DDL / CHARGEMENT IMPLÉMENTÉS |
| fact_mandat | DDL / CHARGEMENT IMPLÉMENTÉS |
| fact_paiement | DDL / CHARGEMENT IMPLÉMENTÉS |
| Airflow design | COMPLETE |
| dbt strategy | COMPLETE |
| Data Quality | COMPLETE |
| KPI model | UPDATED |
| Growth assumptions | ALIGNED WITH STARTERPACK |
| Runtime warehouse | PÉRIMÈTRE INITIAL VALIDÉ DANS LE RAPPORT DU 24 AOÛT |
| Airflow execution | DOCUMENTÉE / RUN COURANT À RATTACHER |
| Data Quality execution | RÉSULTATS HISTORIQUES DISPONIBLES / EXTENSIONS À VALIDER |
| Runtime evidence | RAPPORT DATA RÉFÉRENCÉ / FAITS ÉTENDUS À CONSOLIDER |

---

# 95. Conclusion

L'architecture OLAP est maintenant alignée avec le modèle métier V2.

Elle permet d'analyser :

```text
MANDATS
DEMANDES
MATCHING
SOURCES
CHASSEURS
SECTEURS
PAIEMENTS
```

sans dégrader la base transactionnelle.

La chaîne cible devient :

```text
real_estate OLTP
       |
       v
staging
       |
       v
warehouse
       |
       +--> fact_mandate
       +--> fact_presentation
       +--> fact_payment
       |
       v
analytics
       |
       +--> KPI
       +--> dashboards
       +--> decision support
       +--> AI features
```

Les preuves finales devront provenir de l'exécution réelle de cette chaîne.

---

**BC05 / C3 — OLAP & ALIMENTATION V2 — ALIGNED WITH STARTERPACK**
