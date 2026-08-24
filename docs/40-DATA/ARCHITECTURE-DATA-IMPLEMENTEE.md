# Architecture Data Implémentée --- Chasse Immobilière

**Projet :** Chasse Immobilière --- Fil Rouge Data & IA\
**Version :** 1.0\
**Statut :** Architecture implémentée et validée\
**Date :** 24 août 2026\
**Périmètre :** Source → MinIO → RAW → STAGING → OLTP → Warehouse → dbt
→ Analytics → OpenMetadata\
**Type :** Documentation d'architecture, d'implémentation et de
justification des choix

------------------------------------------------------------------------

## 1. Objet du document

Ce document décrit l'architecture Data réellement implémentée dans le
projet **Chasse Immobilière**.

Son objectif n'est pas uniquement de présenter les composants
techniques. Il explique :

-   ce qui a été construit ;
-   comment les composants sont connectés ;
-   pourquoi chaque couche existe ;
-   pourquoi les responsabilités ont été séparées ;
-   comment les données circulent ;
-   comment la qualité est contrôlée ;
-   comment les traitements sont orchestrés ;
-   comment les déploiements sont industrialisés ;
-   comment la traçabilité et la lineage sont assurées ;
-   quelles décisions d'architecture ont été prises ;
-   quelles alternatives ont volontairement été écartées.

Le document décrit l'état réel du projet au 24 août 2026. Certains
documents antérieurs indiquent encore `OLAP`, `dbt` ou `OpenMetadata`
comme étapes futures : ils représentent l'état du projet au moment où
ils ont été écrits. Depuis, ces composants ont été implémentés et
validés.

------------------------------------------------------------------------

# 2. Problème architectural traité

Une application de chasse immobilière manipule plusieurs catégories de
données ayant des usages différents :

-   données collectées depuis des sources immobilières ;
-   données métier transactionnelles ;
-   historique des observations ;
-   données nettoyées ;
-   données analytiques ;
-   indicateurs de marché ;
-   métadonnées ;
-   informations de gouvernance.

Mettre toutes ces données dans les mêmes tables aurait créé plusieurs
problèmes :

-   mélange entre données brutes et données validées ;
-   perte de l'historique lors des mises à jour ;
-   difficulté à rejouer un traitement ;
-   couplage entre opérations métier et analytics ;
-   requêtes analytiques complexes sur le modèle transactionnel ;
-   traçabilité insuffisante ;
-   gouvernance difficile ;
-   risques de propagation de données invalides.

L'architecture a donc été organisée en couches ayant chacune une
responsabilité précise.

------------------------------------------------------------------------

# 3. Architecture globale

``` text
SOURCE DE DONNÉES
       |
       v
+---------------+
|     MinIO     |
| Object Storage|
+---------------+
       |
       v
+---------------+
|      RAW      |
| PostgreSQL    |
+---------------+
       |
       | validation + transformation
       v
+---------------+
|    STAGING    |
| PostgreSQL    |
+---------------+
       |
       | quality gate
       +--------------------+
       |                    |
       v                    v
+---------------+     données historiques validées
|     OLTP      |             |
| real_estate   |             |
+---------------+             |
       |                      |
       | données métier       |
       +----------+-----------+
                  |
                  v
          +---------------+
          |   WAREHOUSE   |
          | PostgreSQL    |
          +---------------+
                  |
                  | dbt
                  v
          +---------------+
          |   ANALYTICS   |
          | views / marts |
          +---------------+
                  |
                  v
          +---------------+
          | OpenMetadata  |
          | catalog       |
          | lineage       |
          | governance    |
          +---------------+
```

Deux plans doivent être distingués :

### Data plane

``` text
MinIO → RAW → STAGING → OLTP/Warehouse → Analytics
```

Il transporte et transforme les données.

### Control / governance plane

``` text
Airflow
GitLab CI/CD
Argo CD
OpenMetadata
```

Il orchestre, déploie, contrôle et documente le Data plane.

Cette séparation évite qu'un outil d'orchestration, de déploiement ou de
gouvernance soit confondu avec un système de stockage de données.

------------------------------------------------------------------------

# 4. Pourquoi MinIO est placé en entrée

MinIO est utilisé comme stockage objet compatible S3.

Il ne remplace ni PostgreSQL ni OpenMetadata.

Son rôle est de conserver les artefacts de données issus de la source
avant leur intégration dans les modèles relationnels.

``` text
Source
  |
  v
MinIO
  |
  v
RAW PostgreSQL
```

## Pourquoi ne pas charger directement la source dans l'OLTP ?

Un chargement direct :

``` text
Source → OLTP
```

aurait supprimé une partie importante de la traçabilité.

Avec MinIO et RAW :

``` text
Source
  ↓
artefact source persistant
  ↓
RAW
  ↓
transformations
```

on peut :

-   conserver l'entrée du pipeline ;
-   auditer un batch ;
-   rejouer une ingestion ;
-   distinguer erreur source et erreur de transformation ;
-   conserver une frontière claire entre acquisition et données métier.

MinIO joue donc le rôle de zone de persistance objet et non celui de
catalogue ou de base transactionnelle.

------------------------------------------------------------------------

# 5. Couche RAW

La couche RAW constitue la première représentation relationnelle des
données ingérées.

Elle conserve les données au plus proche de leur forme d'entrée.

Exemples de tables utilisées :

``` text
raw.annonces
raw.recherches
```

## Responsabilités

RAW doit :

-   accepter les données provenant de l'ingestion ;
-   conserver les informations nécessaires à la traçabilité ;
-   éviter les transformations métier prématurées ;
-   permettre des contrôles avant promotion vers STAGING.

## Pourquoi RAW est séparé de STAGING

RAW répond à la question :

> Qu'avons-nous réellement reçu ?

STAGING répond à :

> Quelles données pouvons-nous utiliser après normalisation et
> validation ?

Ces questions sont différentes et nécessitent donc deux états distincts.

------------------------------------------------------------------------

# 6. Data Quality RAW

La qualité est intégrée au pipeline et n'est pas exécutée manuellement
après coup.

``` text
load_raw
   |
   v
validate_raw
   |
   v
transform_staging
```

Une erreur RAW doit empêcher la progression normale vers la couche
suivante.

Cette stratégie transforme la qualité en **quality gate**.

Un cas réel a déjà permis de détecter des dates invalides. Le parseur a
ensuite été corrigé jusqu'à obtenir des données valides.

Cela démontre que la couche de qualité n'est pas décorative : elle
protège réellement les traitements suivants.

------------------------------------------------------------------------

# 7. Couche STAGING

STAGING contient les données :

-   parsées ;
-   normalisées ;
-   typées ;
-   nettoyées ;
-   enrichies techniquement ;
-   évaluées par les règles de qualité.

La couche conserve notamment des informations de pipeline telles que :

``` text
ingestion_batch
source_file
staged_at
quality_valid
```

## Rôle architectural

STAGING est la frontière entre :

``` text
données reçues
```

et :

``` text
données utilisables
```

Seules les observations respectant :

``` text
quality_valid = TRUE
```

peuvent alimenter les modèles analytiques.

## Pourquoi ne pas supprimer STAGING après création de l'OLTP ?

Parce que l'OLTP et STAGING n'ont pas le même rôle.

L'OLTP conserve l'état métier courant et applique notamment des
opérations d'UPSERT.

STAGING conserve l'observation du pipeline et son contexte de batch.

Cette différence devient essentielle pour construire l'historique
analytique.

------------------------------------------------------------------------

# 8. OLTP --- modèle transactionnel métier

Le schéma OLTP principal est :

``` text
real_estate
```

Il représente le domaine métier.

Il contient notamment des concepts tels que :

``` text
client
chasseur
secteur
source
mandat
demande
bien
visite
utilisateur
piece_jointe
audit_log
```

Le modèle est normalisé et utilise :

-   clés primaires ;
-   clés étrangères ;
-   contraintes ;
-   règles d'unicité ;
-   indexes ;
-   relations métier.

## Objectif

L'OLTP répond principalement à :

> Quel est l'état opérationnel actuel du système métier ?

Par exemple, l'identité logique d'un bien est fondée sur :

``` text
id_source + reference_externe
```

Les UPSERT permettent de mettre à jour l'état courant sans créer
artificiellement un nouveau bien à chaque ingestion.

------------------------------------------------------------------------

# 9. Pourquoi OLTP et OLAP sont séparés

Cette séparation constitue une décision architecturale fondamentale.

``` text
OLTP != OLAP
```

### OLTP

Optimisé pour :

-   opérations métier ;
-   cohérence transactionnelle ;
-   relations normalisées ;
-   INSERT / UPDATE ;
-   état courant.

### OLAP / Warehouse

Optimisé pour :

-   historique ;
-   agrégations ;
-   analyses ;
-   tendances ;
-   KPI ;
-   lecture intensive ;
-   BI et futurs traitements Data/IA.

Utiliser l'OLTP directement pour toutes les analyses aurait :

-   complexifié les requêtes ;
-   couplé analytics et métier ;
-   augmenté la charge analytique sur le modèle opérationnel ;
-   rendu l'historisation difficile ;
-   mélangé les grains métier.

Le Warehouse n'est donc pas une copie de l'OLTP.

------------------------------------------------------------------------

# 10. Pourquoi STAGING alimente une partie du Warehouse

Un point important de cette architecture est que le Warehouse n'est pas
alimenté exclusivement depuis l'OLTP.

Le contrat retenu est :

``` text
dim_date
    <- calendrier généré

dim_source
    <- real_estate.source

dim_localisation
    <- staging.annonces validées

dim_bien
    <- staging.annonces validées
     + lineage real_estate.bien

fact_annonce
    <- staging.annonces validées
     + lookups dimensions
```

## Justification

`real_estate.bien` représente un état métier mis à jour.

`staging.annonces` représente une observation issue d'un batch.

Pour l'analyse historique, nous devons conserver l'observation et non
uniquement l'état final.

Exemple :

``` text
Bien ANN-0042

01/08 : 280 000 €
10/08 : 275 000 €
20/08 : 265 000 €
```

Un OLTP basé sur l'état courant pourrait finir avec :

``` text
265 000 €
```

Le Warehouse doit pouvoir conserver :

``` text
280 000
275 000
265 000
```

comme observations distinctes.

------------------------------------------------------------------------

# 11. Source logique, bien et observation

Trois identités différentes ont volontairement été conservées.

## Source logique

``` text
real_estate.source.id_source
```

Elle représente le système ou fournisseur logique.

## Bien

``` text
id_source + reference_externe
```

Il s'agit de l'identité métier du bien provenant d'une source.

## Observation

``` text
source + reference + ingestion_batch
```

Une observation représente l'état observé d'un bien pendant une
exécution donnée.

Cette distinction permet :

``` text
1 bien
+
N observations
=
historique analytique
```

------------------------------------------------------------------------

# 12. Source et ingestion_batch ne sont pas la même chose

Décision importante :

``` text
source != ingestion_batch
```

La source répond à :

> D'où provient la donnée ?

Le batch répond à :

> Pendant quelle exécution a-t-elle été collectée et traitée ?

Deux observations issues de la même source peuvent appartenir à deux
batches différents.

Conserver ces deux concepts est indispensable pour la traçabilité.

------------------------------------------------------------------------

# 13. Data Warehouse

Le premier modèle Warehouse implémenté est centré sur l'observation du
marché immobilier.

``` text
warehouse
├── dim_date
├── dim_source
├── dim_localisation
├── dim_bien
└── fact_annonce
```

Le premier processus analytique est :

> **PROPERTY MARKET OBSERVATION --- Observation du marché immobilier**

------------------------------------------------------------------------

# 14. Grain de fact_annonce

Le grain a été explicitement défini avant l'implémentation.

> Une ligne de `fact_annonce` représente une observation d'une annonce /
> d'un bien provenant d'une source donnée à un instant/batch de collecte
> donné.

Conceptuellement :

``` text
source
+
reference_externe
+
observation/batch
=
1 ligne de fait
```

Définir le grain avant les colonnes évite de mélanger plusieurs
processus métier dans une seule table de faits.

------------------------------------------------------------------------

# 15. Mesures de fact_annonce

Le fait contient notamment :

``` text
prix
surface
prix_m2
nb_pieces
nb_chambres
annonce_count
```

avec :

``` text
annonce_count = 1
```

Cela permet notamment :

``` sql
SUM(annonce_count)
```

pour calculer explicitement les volumes.

`prix_m2` est dérivé défensivement :

``` sql
CASE
    WHEN surface > 0
    THEN prix / surface
    ELSE NULL
END
```

Même si les données validées actuelles n'ont pas de surface nulle ou
égale à zéro, le pipeline reste défensif.

------------------------------------------------------------------------

# 16. Dimensions

## dim_date

Dimension calendrier.

Utilisée notamment pour :

``` text
publication_date_key
collection_date_key
```

Elle évite de répéter des transformations temporelles dans chaque
requête analytique.

## dim_source

Représente les sources de données.

Historisation :

``` text
SCD Type 2
```

## dim_localisation

Représente les axes géographiques analytiques.

Historisation :

``` text
SCD Type 1
```

Une dimension géographique plus complexe n'a pas été créée immédiatement
afin de respecter KISS/YAGNI.

## dim_bien

Représente la version descriptive analytique d'un bien.

Historisation :

``` text
SCD Type 2
```

Attributs descriptifs pouvant être suivis :

``` text
titre
type_bien
adresse
latitude
longitude
dpe
statut
```

Une modification du prix ne crée pas une nouvelle version de `dim_bien`,
car le prix est une observation portée par le fait.

------------------------------------------------------------------------

# 17. Pourquoi SCD Type 2 uniquement sur certaines dimensions

L'historisation SCD2 n'a pas été appliquée partout.

Elle a été ciblée là où la conservation des versions apporte une valeur
analytique.

``` text
dim_date           immutable
dim_source         SCD2
dim_localisation   SCD1
dim_bien           SCD2
```

Une généralisation du SCD2 aurait augmenté :

-   le volume ;
-   la complexité ETL ;
-   les conditions de lookup ;
-   les risques d'erreur.

La stratégie retenue privilégie donc l'historisation utile plutôt que
l'historisation systématique.

------------------------------------------------------------------------

# 18. Membres UNKNOWN

Le Warehouse prévoit des membres techniques `UNKNOWN` lorsque
nécessaire.

Exemple :

``` text
localisation_key = 0
pays             = INCONNU
ville            = INCONNUE
```

Objectif :

-   éviter les faits orphelins ;
-   conserver l'observation ;
-   éviter une FK dimensionnelle nulle ;
-   rendre la donnée manquante explicitement identifiable.

Les valeurs métier manquantes ne sont toutefois pas remplacées
artificiellement par `0`.

------------------------------------------------------------------------

# 19. Traçabilité du Warehouse

La table de faits conserve notamment :

``` text
reference_externe
ingestion_batch
source_file
date_collecte_exacte
date_publication_exacte
dw_loaded_at
```

Les dimensions SCD2 disposent de métadonnées telles que :

``` text
valid_from
valid_to
is_current
dw_created_at
dw_updated_at
```

La chaîne de traçabilité est donc :

``` text
Source
  ↓
fichier / objet
  ↓
batch
  ↓
RAW
  ↓
STAGING
  ↓
OLTP / Warehouse
  ↓
Analytics
```

------------------------------------------------------------------------

# 20. Pourquoi le timestamp STAGING est utilisé pour l'observation

Le loader OLTP met à jour `bien.date_collecte` pendant les
INSERT/UPSERT.

Ce timestamp peut donc représenter le dernier chargement de l'état
courant.

Pour l'historique analytique :

``` text
fact_annonce.date_collecte_exacte
    <- staging.annonces.staged_at
```

Cette décision évite qu'une ancienne observation soit réinterprétée avec
le timestamp d'un UPSERT plus récent.

------------------------------------------------------------------------

# 21. Processus métier volontairement exclus du premier fait

`fact_annonce` ne doit pas devenir une table universelle.

Les éléments suivants ont été volontairement exclus :

``` text
honoraires
commission_chasseur
nb_visites
mandat_exclusif
delai_achat
performance_chasseur
```

Ils correspondent à d'autres processus et donc à d'autres grains.

Des faits futurs pourront être créés :

``` text
fact_mandat
fact_presentation
fact_visite
fact_vente
```

Cette décision évite de fabriquer des données ou des processus métier
non encore disponibles uniquement pour remplir le Warehouse.

------------------------------------------------------------------------

# 22. dbt

dbt intervient **après la création du Warehouse**.

Il ne remplace ni Airflow ni le loader Warehouse.

Responsabilité :

``` text
Warehouse
   |
   v
transformations analytiques versionnées
   |
   v
Analytics / marts
```

Projet :

``` text
pipelines/dbt
```

Modèles actuels :

``` text
analytics.stg_dim_bien
analytics.stg_fact_annonce
analytics.mart_market_by_city
```

------------------------------------------------------------------------

# 23. Pourquoi dbt après le Warehouse

Le Warehouse fournit un modèle dimensionnel stable.

dbt construit ensuite une couche analytique orientée consommation.

Cette séparation permet :

-   de conserver le Warehouse comme couche analytique de référence ;
-   de versionner les transformations SQL ;
-   de tester les modèles ;
-   de documenter les colonnes ;
-   de créer des marts sans modifier l'OLTP ;
-   de produire des artefacts de lineage ;
-   de faciliter BI et futurs usages Data/IA.

------------------------------------------------------------------------

# 24. mart_market_by_city

Le premier mart agrège le marché par :

``` text
pays
ville
code_postal
```

Il fournit notamment :

``` text
nb_annonces
prix_moyen
prix_min
prix_max
surface_moyenne
prix_m2_moyen
premiere_publication
derniere_publication
```

Il matérialise le passage entre un Warehouse générique et un produit
analytique directement exploitable.

------------------------------------------------------------------------

# 25. Tests dbt

dbt n'est pas uniquement utilisé pour créer des vues.

Les modèles disposent de tests tels que :

``` text
not_null
unique
```

Validation obtenue :

``` text
dbt run  : 3/3 PASS
dbt test : 19/19 PASS
```

Cela constitue un nouveau quality gate après le Warehouse.

------------------------------------------------------------------------

# 26. Stratégie globale de qualité

La qualité est contrôlée à plusieurs niveaux.

``` text
RAW
 |
 +--> validate_raw
 |
 v
STAGING
 |
 +--> validate_staging
 |
 v
OLTP
 |
 +--> validate_oltp
 |
 v
WAREHOUSE
 |
 +--> validate_warehouse
 |
 v
dbt
 |
 +--> dbt_test
 |
 v
ANALYTICS
```

## Pourquoi plusieurs quality gates ?

Une seule validation finale ne permettrait pas d'identifier précisément
l'origine d'une erreur.

Avec plusieurs gates :

``` text
RAW failure
```

signifie que le problème est proche de l'ingestion.

``` text
STAGING failure
```

signifie qu'une normalisation ou règle de qualité a échoué.

``` text
OLTP failure
```

signale un problème de cohérence métier.

``` text
Warehouse failure
```

signale un problème dimensionnel/analytique.

``` text
dbt failure
```

signale un problème dans les modèles analytiques.

Cette localisation réduit fortement le temps de diagnostic.

------------------------------------------------------------------------

# 27. Airflow --- orchestration

Airflow orchestre le pipeline.

DAG :

``` text
real_estate_ingestion
```

Chaîne validée :

``` text
start
  ↓
generate_source_data
  ↓
load_raw
  ↓
validate_raw
  ↓
transform_staging
  ↓
validate_staging
  ↓
load_oltp
  ↓
validate_oltp
  ↓
load_warehouse
  ↓
validate_warehouse
  ↓
dbt_run
  ↓
dbt_test
  ↓
end
```

Une exécution complète a atteint `success` sur toutes ces tâches.

------------------------------------------------------------------------

# 28. Pourquoi Airflow ne remplace pas dbt

Airflow répond à :

> Quand et dans quel ordre les traitements doivent-ils être exécutés ?

dbt répond à :

> Comment les données analytiques SQL doivent-elles être transformées,
> testées et documentées ?

Les responsabilités sont donc complémentaires.

``` text
Airflow
  |
  +--> lance le loader
  +--> lance les quality gates
  +--> lance dbt
```

mais :

``` text
dbt
  |
  +--> définit les modèles SQL analytiques
  +--> gère leurs dépendances
  +--> exécute leurs tests
  +--> génère les artefacts de documentation
```

------------------------------------------------------------------------

# 29. Kubernetes --- isolation de l'exécution

Les traitements sont exécutés sur Kubernetes.

Cela apporte :

-   isolation des tâches ;
-   environnement reproductible ;
-   images versionnées ;
-   logs séparés ;
-   dépendances explicites ;
-   exécution distribuable ;
-   intégration avec Airflow.

Le poste Windows sert au développement et au Git.

Il n'est pas le runtime de production du pipeline.

------------------------------------------------------------------------

# 30. GitLab CI/CD

GitLab CI est responsable de l'intégration et de la livraison.

Il intervient notamment pour :

-   valider le dépôt ;
-   construire les images ;
-   publier les images dans le registry ;
-   publier les DAGs Airflow ;
-   publier certains manifests dans `lab-gitops`.

GitLab CI n'est pas le moteur d'orchestration quotidien des données.

Cette responsabilité appartient à Airflow.

------------------------------------------------------------------------

# 31. GitOps et Argo CD

Les ressources Kubernetes persistantes sont gérées via GitOps.

``` text
Git
 ↓
lab-gitops
 ↓
Argo CD
 ↓
Kubernetes
```

Argo CD fournit :

-   état désiré versionné ;
-   réconciliation ;
-   self-heal ;
-   possibilité de prune ;
-   audit Git ;
-   reproductibilité.

Cette architecture évite que le cluster devienne une collection de
modifications manuelles impossibles à reproduire.

------------------------------------------------------------------------

# 32. Séparation CI/CD et runtime

Trois responsabilités sont séparées.

``` text
GitLab CI
    = construire et publier

Argo CD
    = déployer/réconcilier l'état Kubernetes

Airflow
    = orchestrer les traitements Data
```

Cette séparation est volontaire.

Elle réduit le couplage et donne à chaque outil une responsabilité
claire.

------------------------------------------------------------------------

# 33. OpenMetadata

OpenMetadata est la plateforme de :

-   catalogue ;
-   documentation ;
-   métadonnées ;
-   lineage ;
-   profiling ;
-   qualité/gouvernance.

OpenMetadata **n'est pas le Data Lake**.

Les données restent dans :

``` text
MinIO
PostgreSQL
```

OpenMetadata décrit et gouverne ces actifs.

------------------------------------------------------------------------

# 34. Ingestion PostgreSQL vers OpenMetadata

OpenMetadata ingère le service PostgreSQL Real Estate.

Cela permet de cataloguer :

``` text
RAW
STAGING
real_estate / OLTP
warehouse
analytics
```

Les objets PostgreSQL doivent exister dans le catalogue avant que la
lineage dbt puisse être correctement attachée.

------------------------------------------------------------------------

# 35. Ingestion dbt vers OpenMetadata

Le workflow dbt/OpenMetadata génère d'abord les artefacts :

``` text
dbt run
dbt test
dbt docs generate
```

puis exécute l'ingestion dbt.

Ordre opérationnel important :

``` text
dbt crée les vues
        ↓
ingestion PostgreSQL
        ↓
OpenMetadata connaît les vues
        ↓
ingestion dbt
        ↓
lineage attachée aux entités
```

Cet ordre a été découvert et validé pendant l'implémentation réelle.

------------------------------------------------------------------------

# 36. Lineage réellement validée

La lineage a été vérifiée directement via l'API OpenMetadata.

Chaîne validée :

``` text
warehouse.fact_annonce
        |
        v
analytics.stg_fact_annonce
        |
        v
analytics.mart_market_by_city
        ^
        |
warehouse.dim_localisation
```

OpenMetadata conserve :

``` text
table-level lineage
column-level lineage
SQL lineage
```

Exemples :

``` text
warehouse.fact_annonce.prix
    ->
analytics.stg_fact_annonce.prix
```

puis :

``` text
analytics.stg_fact_annonce.prix
    ->
analytics.mart_market_by_city.prix_moyen
```

et :

``` text
warehouse.dim_localisation.ville
    ->
analytics.mart_market_by_city.ville
```

La lineage n'est donc pas une simple représentation dessinée : elle est
persistée dans le catalogue.

------------------------------------------------------------------------

# 37. Pourquoi la lineage est importante

Elle permet de répondre à :

> D'où vient ce KPI ?

Exemple :

``` text
prix_moyen
   ↓
mart_market_by_city
   ↓
stg_fact_annonce.prix
   ↓
warehouse.fact_annonce.prix
   ↓
STAGING
   ↓
batch/source
```

Elle facilite :

-   audit ;
-   analyse d'impact ;
-   diagnostic ;
-   gouvernance ;
-   confiance dans les KPI ;
-   justification lors de la soutenance ;
-   futurs usages IA.

------------------------------------------------------------------------

# 38. Gouvernance --- prochaine extension logique

La prochaine étape est Governance-as-Code.

Elle doit ajouter dans OpenMetadata :

``` text
Glossary
Tags / classifications
Ownership
Data Quality governance
RGPD/PII
```

Elle s'appuiera sur la structure déjà éprouvée dans le projet Retail.

L'objectif n'est pas de remplacer les tests existants mais de relier les
actifs techniques à leur contexte métier et réglementaire.

------------------------------------------------------------------------

# 39. Pourquoi le propriétaire PostgreSQL n'est pas le Data Owner

PostgreSQL peut indiquer :

``` text
real_estate_user
```

comme propriétaire technique.

Cela signifie :

> ce compte possède techniquement l'objet SQL.

Cela ne signifie pas :

> cette identité est responsable métier de la donnée.

La gouvernance doit distinguer :

``` text
technical owner
data owner
business owner
```

Cette distinction sera appliquée via Governance-as-Code.

------------------------------------------------------------------------

# 40. Sécurité des secrets

Les mots de passe et tokens ne doivent pas être stockés dans les
manifests Git.

Ils sont injectés via des Kubernetes Secrets.

Exemples :

``` text
openmetadata-ingestion-secrets
lab-gitops-git-credentials
airflow-git-credentials
om-admin-token
```

Le principe est :

``` text
code/configuration versionnée
        +
secret injecté au runtime
```

et non :

``` text
mot de passe dans Git
```

------------------------------------------------------------------------

# 41. Architecture end-to-end actuelle

``` text
                         GITLAB
                           |
              +------------+------------+
              |                         |
              v                         v
      Container Registry          Git repositories
              |                         |
              |                +--------+--------+
              |                |                 |
              |                v                 v
              |          airflow-dags        lab-gitops
              |                |                 |
              |                v                 v
              |          Airflow GitSync      Argo CD
              |                |                 |
              +----------------+-----------------+
                               |
                               v
                          KUBERNETES
                               |
                               v
                            AIRFLOW
                               |
                               v
                      Generate source data
                               |
                               v
                             MINIO
                               |
                               v
                              RAW
                               |
                         Quality Gate
                               |
                               v
                            STAGING
                               |
                         Quality Gate
                               |
                   +-----------+-----------+
                   |                       |
                   v                       v
                 OLTP                 WAREHOUSE
                   |                       |
             Quality Gate             Quality Gate
                                           |
                                           v
                                          dbt
                                           |
                                      dbt tests
                                           |
                                           v
                                      ANALYTICS
                                           |
                                           v
                                      OpenMetadata
                                           |
                          +----------------+---------------+
                          |                |               |
                          v                v               v
                       Catalog          Lineage        Governance
```

------------------------------------------------------------------------

# 42. Choix de PostgreSQL pour plusieurs couches

RAW, STAGING, OLTP, Warehouse et Analytics peuvent être hébergés dans le
même moteur PostgreSQL tout en restant logiquement séparés par schémas.

Cela est adapté à l'échelle actuelle du projet parce que :

-   PostgreSQL couvre correctement les besoins transactionnels ;
-   il supporte les contraintes relationnelles ;
-   il permet les vues analytiques ;
-   il simplifie l'exploitation ;
-   il évite d'ajouter une technologie distribuée sans besoin démontré ;
-   il reste compatible avec Airflow, dbt et OpenMetadata.

La séparation importante est d'abord **logique et fonctionnelle**.

Si les volumes futurs l'exigent, le Warehouse pourra être déplacé vers
une plateforme analytique spécialisée sans remettre en cause le contrat
architectural.

------------------------------------------------------------------------

# 43. Pourquoi ne pas introduire immédiatement Spark/Kafka

L'architecture suit KISS et YAGNI.

Les données et fréquences actuelles ne justifient pas encore :

``` text
Kafka
Spark
Data Warehouse cloud distribué
```

Les ajouter uniquement pour afficher davantage de technologies aurait :

-   augmenté la complexité ;
-   augmenté l'exploitation ;
-   compliqué le diagnostic ;
-   ajouté des coûts ;
-   réduit la lisibilité pédagogique.

Une technologie distribuée devra être introduite lorsqu'un besoin de
volume, vélocité ou traitement le justifiera.

------------------------------------------------------------------------

# 44. Pourquoi ne pas construire l'IA avant la Data Platform

Le projet a volontairement stabilisé :

``` text
ingestion
quality
OLTP
Warehouse
analytics
metadata
lineage
```

avant de construire les fonctions IA avancées.

Une IA construite directement sur des données non gouvernées aurait posé
des problèmes de :

-   reproductibilité ;
-   provenance ;
-   qualité ;
-   explicabilité ;
-   conformité ;
-   maintien en production.

L'architecture Data constitue donc la fondation de l'architecture IA
future.

------------------------------------------------------------------------

# 45. Validation technique obtenue

État réel :

``` text
Source generation                           VALIDÉ
MinIO                                       VALIDÉ
RAW                                         VALIDÉ
RAW Quality                                 VALIDÉ
STAGING                                     VALIDÉ
STAGING Quality                             VALIDÉ
OLTP                                        VALIDÉ
OLTP Quality                                VALIDÉ
Warehouse                                   VALIDÉ
Warehouse Quality                           VALIDÉ
Airflow orchestration                       VALIDÉ
Kubernetes execution                        VALIDÉ
GitLab CI/CD                                VALIDÉ
GitLab Registry                             VALIDÉ
dbt                                         VALIDÉ
dbt run                                     3/3 PASS
dbt test                                    19/19 PASS
Analytics                                   VALIDÉ
OpenMetadata PostgreSQL ingestion           VALIDÉ
OpenMetadata dbt ingestion                  VALIDÉ
Table lineage                               VALIDÉ
Column lineage                              VALIDÉ
SQL lineage                                 VALIDÉ
Argo CD / GitOps OpenMetadata               VALIDÉ
Governance-as-Code                          PROCHAINE ÉTAPE
```

------------------------------------------------------------------------

# 46. Limites connues

## pg_stat_statements

OpenMetadata signale l'absence de `pg_stat_statements`.

Cela affecte l'ingestion optionnelle de certaines requêtes PostgreSQL,
pas le catalogue principal ni la lineage dbt déjà validée.

## Ownership technique

`real_estate_user` apparaît comme propriétaire PostgreSQL mais ne doit
pas devenir automatiquement propriétaire métier.

## Gouvernance

Glossaire, classifications, ownership métier et règles de gouvernance
restent à industrialiser.

## Domaines analytiques futurs

Le Warehouse v1 couvre d'abord le marché immobilier.

Les domaines suivants restent futurs :

``` text
mandats
présentations
visites
ventes
commissions
performance chasseur
matching
ML
```

Ils doivent être ajoutés lorsque les données réelles correspondantes
existent.

------------------------------------------------------------------------

# 47. Principales décisions d'architecture

  -----------------------------------------------------------------------
  Décision                            Justification
  ----------------------------------- -----------------------------------
  MinIO avant PostgreSQL              conserver l'artefact source et
                                      permettre le replay

  RAW séparé                          préserver l'état reçu

  STAGING séparé                      normaliser et qualifier avant
                                      promotion

  OLTP normalisé                      représenter correctement le domaine
                                      métier

  OLTP != OLAP                        séparer transactionnel et
                                      analytique

  STAGING alimente `fact_annonce`     préserver l'historique
                                      d'observation

  OLTP contribue aux                  conserver l'identité métier
  dimensions/lineage                  

  Warehouse en étoile                 simplifier les analyses

  SCD2 ciblé                          historiser uniquement là où cela
                                      apporte une valeur

  `fact_annonce` limité à un grain    éviter le mélange de processus

  dbt après Warehouse                 séparer modèle dimensionnel et
                                      produits analytiques

  Airflow pour orchestration          dépendances, retry, logs et
                                      exécution centralisée

  Kubernetes pour runtime             isolation et reproductibilité

  GitLab CI pour build/publish        séparation intégration/livraison et
                                      runtime

  Argo CD pour déploiement            GitOps et état désiré

  OpenMetadata hors Data path         gouverner sans devenir le stockage

  Quality gates multiples             bloquer tôt et localiser les
                                      erreurs

  Lineage persistée                   audit et analyse d'impact

  IA après fondation Data             qualité, provenance et gouvernance
                                      avant ML
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 48. Relation logique entre les bases et schémas

La relation n'est pas simplement :

``` text
base A copie base B
```

Elle est :

``` text
RAW
= vérité d’ingestion

STAGING
= vérité technique validée

OLTP
= vérité métier opérationnelle

WAREHOUSE
= vérité analytique historisée

ANALYTICS
= produits de consommation / KPI

OPENMETADATA
= vérité de métadonnées et gouvernance
```

Ces responsabilités évitent qu'un même modèle doive satisfaire
simultanément toutes les contraintes.

------------------------------------------------------------------------

# 49. Lecture simplifiée pour la soutenance

Si la question est :

> Pourquoi autant de couches ?

Réponse :

> Parce qu'une donnée n'a pas le même statut lorsqu'elle vient d'être
> reçue, lorsqu'elle a été validée, lorsqu'elle représente l'état métier
> courant et lorsqu'elle doit servir à analyser l'historique. Nous
> séparons donc RAW, STAGING, OLTP et Warehouse afin de conserver la
> provenance, contrôler la qualité et éviter de charger les usages
> analytiques directement sur le modèle transactionnel.

Si la question est :

> Pourquoi Airflow et dbt ?

Réponse :

> Airflow orchestre le processus complet et dbt gère les transformations
> analytiques SQL. Ils ne remplissent pas la même responsabilité.

Si la question est :

> Pourquoi OpenMetadata ?

Réponse :

> Les données étaient techniquement disponibles, mais il fallait aussi
> savoir ce qu'elles signifient, d'où elles viennent et quelles
> transformations produisent les KPI. OpenMetadata apporte le catalogue,
> la documentation, la lineage et la future gouvernance.

Si la question est :

> Pourquoi ne pas mettre directement de l'IA ?

Réponse :

> Une IA fiable nécessite des données contrôlées, historisées, traçables
> et gouvernées. Nous avons donc construit la fondation Data avant les
> modèles IA.

------------------------------------------------------------------------

# 50. Conclusion

L'architecture actuellement déployée constitue une chaîne Data cohérente
:

``` text
SOURCE
  ↓
MINIO
  ↓
RAW
  ↓
QUALITY
  ↓
STAGING
  ↓
QUALITY
  ↓
OLTP
  ↓
WAREHOUSE
  ↓
QUALITY
  ↓
dbt
  ↓
ANALYTICS
  ↓
OPENMETADATA
```

Elle est complétée transversalement par :

``` text
Airflow      -> orchestration
Kubernetes   -> runtime
GitLab CI    -> build / validation / publication
Argo CD      -> GitOps / déploiement
OpenMetadata -> catalog / lineage / governance
```

Le choix essentiel n'est pas la quantité d'outils mais la **séparation
des responsabilités**.

Chaque couche répond à une question différente :

``` text
MinIO       : qu’avons-nous reçu et conservé ?
RAW         : qu’avons-nous ingéré ?
STAGING     : qu’avons-nous nettoyé et validé ?
OLTP        : quel est l’état métier ?
Warehouse   : quel historique pouvons-nous analyser ?
dbt         : quels modèles analytiques voulons-nous exposer ?
Analytics   : quels KPI voulons-nous consommer ?
OpenMetadata: que signifient les données et d’où viennent-elles ?
Airflow     : dans quel ordre exécuter les traitements ?
GitLab      : comment construire et publier ?
Argo CD     : comment garantir l’état déployé ?
```

Cette architecture fournit désormais une base solide pour la prochaine
phase :

``` text
Governance-as-Code
        ↓
RGPD / classifications / ownership
        ↓
features de matching
        ↓
Machine Learning
        ↓
IA
```

------------------------------------------------------------------------

# Références projet

Ce document consolide et actualise les décisions et travaux décrits
notamment dans :

``` text
NOTE-DE-CADRAGE.md
CAHIER-DES-CHARGES-TECHNIQUE.md
MCD-MERISE.md
OLTP.md
OLAP.md
OLAP-DATA-WAREHOUSE-DESIGN-V1.md
OLAP-MAPPING-OLTP-STAGING-TO-OLAP-V1.md
PROJECT-ALIGNMENT-REVIEW-2026-08-23.md
REAL-ESTATE-INGESTION-PIPELINE.md
JOURNAL-DE-DECISIONS.md
architecture-playbook.md
```

Les états `NEXT` présents dans certains documents historiques doivent
être lus comme des snapshots du projet à leur date de rédaction. Le
présent document décrit l'état implémenté et validé au 24 août 2026.
