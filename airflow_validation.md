# Validation Airflow et architecture d'exécution du Data Pipeline

**Projet :** Enterprise Real Estate Intelligence Platform /
`chasse_immobiliere`\
**Date de validation :** 24 août 2026\
**Statut :** Validé

------------------------------------------------------------------------

## 1. Objectif

Ce document formalise la validation de l'orchestration du pipeline Data
Real Estate après stabilisation du modèle PostgreSQL, de dbt,
d'OpenMetadata et de la Governance-as-Code.

La validation avait quatre objectifs :

1.  confirmer qu'Airflow est bien l'orchestrateur d'exécution du
    pipeline Data ;
2.  confirmer que les traitements s'exécutent dans Kubernetes via
    `KubernetesPodOperator` ;
3.  confirmer que tous les traitements utilisent l'image Data Pipeline
    Python 3.12 publiée dans le GitLab Container Registry ;
4.  exécuter un nouveau pipeline complet et vérifier le succès de toutes
    les étapes, de la génération des données jusqu'aux tests dbt.

------------------------------------------------------------------------

## 2. Séparation des responsabilités

L'architecture retenue sépare clairement CI/CD et orchestration Data.

### GitLab CI

GitLab CI est responsable de :

-   validation des fichiers SQL, Python et configurations ;
-   validation et application des migrations PostgreSQL ;
-   tests structurels de la base ;
-   construction de l'image Data Pipeline ;
-   publication de l'image dans le GitLab Container Registry ;
-   publication des DAGs Airflow ;
-   publication des éléments GitOps/OpenMetadata lorsque nécessaire.

GitLab CI n'est pas utilisé comme orchestrateur ETL de production.

### Airflow

Airflow est responsable de l'exécution du pipeline Data :

``` text
generate_source_data
        |
        v
load_raw
        |
        v
validate_raw
        |
        v
transform_staging
        |
        v
validate_staging
        |
        v
load_oltp
        |
        v
validate_oltp
        |
        v
load_warehouse
        |
        v
validate_warehouse
        |
        v
dbt_run
        |
        v
dbt_test
```

Cette séparation évite de transformer GitLab CI en moteur ETL et permet
à Airflow de gérer les dépendances, les exécutions, les états et les
reprises du pipeline.

------------------------------------------------------------------------

## 3. État de la plateforme Airflow

Airflow est déployé dans le namespace Kubernetes :

``` text
airflow
```

Les composants observés sont :

``` text
airflow-postgresql
airflow-scheduler
airflow-statsd
airflow-triggerer
airflow-webserver
```

Tous les composants étaient en état `Running` lors de la validation.

Des compteurs de redémarrage élevés ont toutefois été observés sur le
scheduler et le webserver. Ils ne bloquent pas le pipeline validé dans
ce document, mais doivent faire l'objet d'une analyse séparée de
stabilité, ressources et probes Kubernetes.

------------------------------------------------------------------------

## 4. DAGs enregistrés

La commande :

``` bash
kubectl -n airflow exec deploy/airflow-scheduler -c scheduler -- \
  airflow dags list
```

a confirmé la présence du DAG :

``` text
real_estate_ingestion
```

Le DAG est chargé depuis :

``` text
/opt/airflow/dags/repo/dags/real_estate_ingestion_dag.py
```

Owner :

``` text
real-estate
```

Le DAG n'est pas en pause.

------------------------------------------------------------------------

## 5. Publication des DAGs

Le pipeline GitLab contient le job :

``` text
airflow:publish-dags
```

Ce job :

1.  valide la présence de
    `pipelines/airflow/real_estate_ingestion_dag.py` ;
2.  clone le dépôt GitLab `airflow-dags` ;
3.  copie les DAGs depuis `pipelines/airflow/` ;
4.  commit les changements si nécessaire ;
5.  pousse les DAGs sur la branche `main`.

Flux :

``` text
chasse_immobiliere
pipelines/airflow/*.py
        |
        v
GitLab CI
airflow:publish-dags
        |
        v
airflow-dags repository
        |
        v
Airflow DAG repository
        |
        v
Airflow scheduler
```

Le job de publication ne lance pas l'ETL. Il déploie uniquement la
définition du DAG.

------------------------------------------------------------------------

## 6. Graphe réel du DAG

La commande :

``` bash
kubectl -n airflow exec deploy/airflow-scheduler -c scheduler -- \
  airflow tasks list real_estate_ingestion --tree
```

a confirmé le graphe suivant :

``` text
start
  |
  v
generate_source_data
  |
  v
load_raw
  |
  v
validate_raw
  |
  v
transform_staging
  |
  v
validate_staging
  |
  v
load_oltp
  |
  v
validate_oltp
  |
  v
load_warehouse
  |
  v
validate_warehouse
  |
  v
dbt_run
  |
  v
dbt_test
  |
  v
end
```

`start` et `end` sont des `EmptyOperator`.

Toutes les étapes de traitement sont des `KubernetesPodOperator`.

------------------------------------------------------------------------

## 7. Runtime Kubernetes

Une inspection directe du `DagBag` Airflow a confirmé l'image utilisée
par chaque tâche.

Image :

``` text
gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
```

Résultat :

``` text
start: None
generate_source_data: gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
load_raw: gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
validate_raw: gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
transform_staging: gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
validate_staging: gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
load_oltp: gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
validate_oltp: gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
load_warehouse: gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
validate_warehouse: gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
dbt_run: gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
dbt_test: gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
end: None
```

`None` pour `start` et `end` est normal : ces tâches n'exécutent aucun
conteneur applicatif.

Cette vérification prouve que le runtime Data n'utilise pas le Python du
GitLab shell runner.

------------------------------------------------------------------------

## 8. Image Data Pipeline

L'image Data Pipeline est construite sur :

``` dockerfile
FROM python:3.12-slim
```

Elle contient notamment :

``` text
postgresql-client
git
```

et les dépendances Python du projet.

Le `requirements.txt` principal contient :

``` text
psycopg[binary]==3.2.10
python-dotenv==1.0.1
boto3==1.35.95
dbt-core==1.9.0
dbt-postgres==1.9.0
```

L'image embarque également les scripts nécessaires aux différentes
étapes :

``` text
database/seeds/generer_annonces.py
database/seeds/load_raw_generated_data.py
database/seeds/upload_generated_to_s3.py
database/seeds/download_generated_from_s3.py
database/seeds/transform_raw_to_staging.py
database/seeds/load_staging_to_oltp.py
database/olap/load_warehouse.py
database/tests/004_raw_data_quality.sql
database/tests/005_staging_data_quality.sql
database/tests/006_oltp_data_quality.sql
database/tests/007_warehouse_data_quality.sql
pipelines/dbt
```

------------------------------------------------------------------------

## 9. Correction de l'architecture CI

Un job GitLab CI nommé :

``` text
database:load-raw-generated
```

exécutait une partie du traitement Data directement sur un shell runner.

Le runner utilisait :

``` text
Python 3.8.10
```

alors que le projet dépend notamment de :

``` text
dbt-core==1.9.0
dbt-postgres==1.9.0
```

Cette combinaison provoquait un échec d'installation de dépendances.

La cause architecturale était plus importante que la simple
incompatibilité Python : le job dupliquait une responsabilité déjà prise
en charge par Airflow.

Le job `database:load-raw-generated` a donc été supprimé de
`database.yml`.

Le chargement RAW reste assuré par :

``` text
Airflow
  |
  v
load_raw
  |
  v
KubernetesPodOperator
  |
  v
data-pipeline:latest
```

Cette correction supprime la dépendance du runtime ETL envers le Python
3.8 du shell runner.

------------------------------------------------------------------------

## 10. Exécution de validation

Un nouveau run manuel a été déclenché :

``` bash
kubectl -n airflow exec deploy/airflow-scheduler -c scheduler -- \
  airflow dags trigger real_estate_ingestion
```

Run ID :

``` text
manual__2026-08-24T14:23:34+00:00
```

Le run est passé de :

``` text
queued
```

à :

``` text
running
```

puis toutes les tâches se sont terminées avec succès.

------------------------------------------------------------------------

## 11. Résultat détaillé du run

État final observé :

  Tâche                    Résultat
  ------------------------ ----------
  `start`                  success
  `generate_source_data`   success
  `load_raw`               success
  `validate_raw`           success
  `transform_staging`      success
  `validate_staging`       success
  `load_oltp`              success
  `validate_oltp`          success
  `load_warehouse`         success
  `validate_warehouse`     success
  `dbt_run`                success
  `dbt_test`               success
  `end`                    success

Le run a commencé à environ :

``` text
2026-08-24 14:23:35 UTC
```

et la tâche `end` s'est terminée à :

``` text
2026-08-24 14:27:52 UTC
```

Le pipeline complet a donc été exécuté en environ quatre minutes et
demie.

------------------------------------------------------------------------

## 12. Chaîne Data validée

Le chemin complet validé est :

``` text
Source / génération
        |
        v
      RAW
        |
        v
Raw Data Quality
        |
        v
    STAGING
        |
        v
Staging Data Quality
        |
        v
      OLTP
        |
        v
OLTP Data Quality
        |
        v
   WAREHOUSE
        |
        v
Warehouse Data Quality
        |
        v
      dbt
        |
        +--> dbt run
        |
        +--> dbt test
        |
        v
   ANALYTICS
```

Le modèle OLTP utilisé par cette chaîne correspond au modèle courant à
16 tables, incluant :

``` text
real_estate.visite
real_estate.audit_log
```

------------------------------------------------------------------------

## 13. Architecture finale validée

``` text
                    GITLAB
                       |
       +---------------+---------------+
       |               |               |
       v               v               v
 Validation       Build Image      Publish DAG
 SQL / Python         |               |
 Migrations           v               v
 DB Tests       GitLab Registry   airflow-dags
                       |               |
                       +-------+-------+
                               |
                               v
                           KUBERNETES
                               |
                               v
                            AIRFLOW
                               |
                               v
                    real_estate_ingestion
                               |
        +----------------------+----------------------+
        |                      |                      |
        v                      v                      v
       RAW                  STAGING                  OLTP
        |                      |                      |
        v                      v                      v
     DQ RAW              DQ STAGING               DQ OLTP
                                                       |
                                                       v
                                                   WAREHOUSE
                                                       |
                                                       v
                                                 DQ WAREHOUSE
                                                       |
                                                       v
                                                      dbt
                                                       |
                                                       v
                                                  ANALYTICS
                                                       |
                                                       v
                                                 OpenMetadata
                                                       |
                                                       v
                                              Governance-as-Code
```

------------------------------------------------------------------------

## 14. Principes retenus

### GitLab CI n'est pas l'orchestrateur ETL

GitLab CI construit, valide et publie.

Airflow orchestre.

Cette séparation réduit les dépendances aux runners CI et centralise la
supervision des traitements Data dans l'outil prévu pour cela.

### Les workloads Data s'exécutent dans Kubernetes

Chaque étape métier du DAG utilise `KubernetesPodOperator`.

Cela apporte :

-   isolation des tâches ;
-   runtime reproductible ;
-   dépendances maîtrisées ;
-   logs par tâche ;
-   exécution homogène ;
-   indépendance vis-à-vis du système du runner GitLab.

### Une image unique garantit le runtime

Toutes les tâches utilisent :

``` text
gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest
```

Le runtime est donc contrôlé par le Dockerfile du projet.

### Les contrôles qualité font partie du pipeline

Les validations ne sont pas exécutées uniquement en fin de traitement.

Elles sont placées entre les couches :

``` text
RAW -> validation
STAGING -> validation
OLTP -> validation
WAREHOUSE -> validation
dbt -> tests
```

Une couche incorrecte doit empêcher la propagation silencieuse des
données vers les couches suivantes.

------------------------------------------------------------------------

## 15. État du socle Data

À l'issue de cette validation :

``` text
GitLab CI                    OK
Image Data Pipeline          OK
GitLab Container Registry    OK
Kubernetes runtime           OK
Airflow                      OK
KubernetesPodOperator        OK
RAW                          OK
RAW Data Quality             OK
STAGING                      OK
STAGING Data Quality         OK
OLTP                         OK
OLTP Data Quality            OK
WAREHOUSE                    OK
Warehouse Data Quality       OK
dbt run                      OK
dbt test                     OK
Analytics                    OK
OpenMetadata ingestion       OK
Governance-as-Code           OK
Argo CD / GitOps             OK
```

------------------------------------------------------------------------

## 16. Point d'attention opérationnel

Les pods Airflow `scheduler` et `webserver` présentaient des nombres de
redémarrages élevés lors de la vérification.

Cela n'a pas empêché plusieurs exécutions réussies du DAG
`real_estate_ingestion`, dont le run de validation du 24 août 2026.

Cependant, ce point doit rester dans le backlog opérationnel afin
d'identifier la cause :

-   limites CPU/mémoire ;
-   probes de liveness/readiness ;
-   dépendances Airflow ;
-   connectivité PostgreSQL ;
-   comportement du scheduler ;
-   éventuels OOMKills ou timeouts.

Ce sujet est séparé de la validation fonctionnelle du pipeline.

------------------------------------------------------------------------

## 17. Conclusion

Le pipeline Data Real Estate est maintenant validé de bout en bout sous
Airflow et Kubernetes.

La séparation des responsabilités est claire :

``` text
GitLab CI
    =
Build + Test + Migration + Publication

Airflow
    =
Orchestration Data

Kubernetes
    =
Runtime

GitLab Registry
    =
Image reproductible

PostgreSQL
    =
RAW + STAGING + OLTP + WAREHOUSE + ANALYTICS

dbt
    =
Transformation analytique + tests

OpenMetadata
    =
Catalogue + lineage + qualité + gouvernance

Argo CD
    =
GitOps
```

Le run `manual__2026-08-24T14:23:34+00:00` constitue le checkpoint de
validation de cette architecture.

Le socle Data peut désormais servir de base stable pour la phase
suivante du projet.
