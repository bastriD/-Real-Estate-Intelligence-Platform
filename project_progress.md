# Projet Fil Rouge — Chasse Immobilière
## État d'avancement technique consolidé

**Date de consolidation : 27 août 2026**

## 1. Objectif du document

Ce document constitue un point de situation technique consolidé du projet **chasse_immobiliere**. Il décrit ce qui a été conçu, déployé, exécuté et effectivement validé sur l'infrastructure Kubernetes, ainsi que les décisions techniques et les points restant à traiter.

Il sert de preuve d'avancement, de support de soutenance et de référence avant la poursuite des travaux.

---

## 2. Architecture générale actuellement validée

La plateforme suit une chaîne Data complète :

```text
Git repository chasse_immobiliere
        |
        v
GitLab CI/CD
        |
        +--> validation / migrations / construction image
        +--> publication des DAG Airflow
        +--> publication GitOps OpenMetadata
        |
        v
Kubernetes
        |
        +--> PostgreSQL real-estate
        |       +--> raw
        |       +--> staging
        |       +--> real_estate (OLTP)
        |       +--> warehouse (OLAP)
        |       +--> analytics (dbt marts)
        |
        +--> Airflow
        |       +--> génération
        |       +--> ingestion RAW
        |       +--> contrôles qualité
        |       +--> STAGING
        |       +--> OLTP
        |       +--> Warehouse
        |       +--> dbt run/test
        |       +--> métriques
        |
        +--> OpenMetadata
        |       +--> ingestion PostgreSQL
        |       +--> profiler
        |       +--> ingestion dbt
        |       +--> lineage
        |       +--> Governance-as-Code
        |
        +--> Prometheus / Pushgateway / Grafana / Loki / Tempo
```

Le poste Windows n'est pas utilisé comme environnement Kubernetes local. Le code est développé dans le dépôt puis publié/déployé par GitLab CI, GitOps/Argo CD et les composants du cluster.

---

## 3. PostgreSQL et organisation des données

La base `real_estate` est organisée en couches séparées afin de distinguer ingestion, nettoyage, exploitation transactionnelle et analytique.

### 3.1 RAW

La couche `raw` conserve les données telles qu'elles arrivent de la source et leur contexte d'ingestion.

État contrôlé avant le dernier run du 27 août :

- `raw.annonces` : 7 000 lignes
- `raw.recherches` : 35 lignes

Le batch historique `generated-1000-v1` contient 1 000 annonces distinctes provenant de :

```text
database/fixtures/annonces/annonces.csv
```

Il s'agit d'un batch initial/historique qui explique l'écart entre RAW et les couches aval.

### 3.2 STAGING

La couche staging transforme les valeurs textuelles RAW vers des types métier et porte les résultats des contrôles qualité.

État contrôlé :

- `staging.annonces` : 6 000 lignes
- `staging.recherches` : 30 lignes

Contrôle qualité réalisé sur les 6 000 annonces :

```text
total_rows              = 6000
valid_rows              = 6000
invalid_rows            = 0
quality_not_evaluated   = 0
missing_reference       = 0
missing_price           = 0
invalid_price           = 0
missing_surface         = 0
invalid_surface         = 0
missing_city            = 0
missing_postal_code     = 0
distinct_references     = 6000
```

Ainsi, **100 % des 6 000 annonces staging contrôlées sont valides sur les règles testées**.

### 3.3 OLTP — schéma `real_estate`

Le modèle métier transactionnel contient notamment :

- `client`
- `chasseur`
- `secteur`
- `source`
- `mandat`
- `mandat_secteur`
- `demande`
- `demande_version`
- `bien`
- `commentaire`
- `document`
- `paiement`
- `presentation`
- `visite`
- `utilisateur`
- `piece_jointe`
- `audit_log`
- `bareme_commission`

État contrôlé :

```text
bien                6000
chasseur               6
client                 18
demande                17
demande_version        17
mandat                 17
mandat_secteur         17
secteur                10
source                  1
bareme_commission       6
```

Les tables prévues pour des événements métier futurs (`paiement`, `presentation`, `visite`, etc.) sont présentes même lorsqu'elles ne contiennent pas encore de données.

---

## 4. Warehouse / OLAP

Le schéma `warehouse` implémente le modèle analytique.

Dimensions principales :

- `dim_date`
- `dim_source`
- `dim_localisation`
- `dim_bien`
- `dim_chasseur`
- `dim_client`
- `dim_demande_version`
- `dim_secteur`

Bridge :

- `bridge_mandat_secteur`

Tables de faits :

- `fact_annonce`
- `fact_mandat`
- `fact_paiement`
- `fact_presentation`
- `fact_demande`
- `fact_matching`
- `fact_bien_daily`

### 4.1 Volumétrie contrôlée

```text
bridge_mandat_secteur   17
dim_bien              6001
dim_chasseur             7
dim_client              19
dim_date              5844
dim_demande_version     18
dim_localisation        18
dim_secteur             11
dim_source               2
fact_annonce           6000
fact_mandat              17
```

Les dimensions utilisent une ligne technique/inconnue, ce qui explique les différences `6000 -> 6001`, `18 -> 19`, etc.

### 4.2 Réconciliation OLTP / Warehouse

La cohérence a été contrôlée explicitement :

```text
entity            OLTP    Warehouse
bien              6000    6000
chasseur             6       6
client              18      18
demande_version     17      17
mandat              17      17
secteur             10      10
```

La réconciliation est donc correcte pour les entités contrôlées.

### 4.3 Intégrité de `fact_annonce`

Sur les 6 000 faits :

```text
total_fact_rows             = 6000
missing_dim_bien            = 0
missing_dim_source          = 0
missing_dim_localisation    = 0
missing_publication_date    = 0
missing_collection_date     = 0
```

Aucune clé dimensionnelle manquante n'a été détectée dans ce contrôle.

---

## 5. Analyse des batches d'ingestion

Six batches applicatifs ont été retrouvés simultanément dans RAW, STAGING et Warehouse :

```text
generated-20260822T000000
generated-20260823T073715
generated-20260823T194031
generated-20260823T205547
generated-20260824T065752
generated-20260824T142334
```

Chaque batch contient :

```text
1000 lignes
1000 références distinctes
```

Cela donne :

```text
6000 observations
6000 biens/références uniques
```

L'impression initiale de « multiplication » des annonces a donc été expliquée : les exécutions successives du générateur ont produit des références différentes et non plusieurs observations du même ensemble de 1 000 biens.

Le batch `generated-1000-v1` existe uniquement dans RAW et correspond aux fixtures historiques.

---

## 6. dbt et couche Analytics

Le projet dbt transforme les données du Warehouse en modèles analytiques utilisables pour les KPI, dashboards et usages métier.

Staging dbt notamment :

- `stg_fact_annonce`
- `stg_dim_bien`

Marts créés :

- `mart_market_overview`
- `mart_market_by_city`
- `mart_market_by_dpe`
- `mart_market_by_property_type`
- `mart_market_by_source`
- `mart_market_evolution`
- `mart_mandat_performance`

### 6.1 Couverture des annonces

Contrôle effectué :

```text
mart_market_by_city             6000
mart_market_by_property_type    6000
mart_market_by_source           6000
mart_market_evolution           6000
warehouse.fact_annonce          6000
```

`mart_market_by_dpe` couvre 3 577 biens. Ce résultat a été expliqué par la donnée source et non par une perte du pipeline :

```text
total_biens   = 6000
dpe_present   = 3577
dpe_missing   = 2423
```

### 6.2 KPI marché contrôlés

```text
total_annonces          6000
total_biens_uniques     6000
total_batches              6
prix_moyen          192460.22
prix_median         188832.50
prix_min             20335.00
prix_max            458060.00
surface_moyenne         231.49
surface_mediane         237.00
prix_m2_moyen          1058.47
prix_m2_median          780.87
```

### 6.3 Mart performance des mandats

`analytics.mart_mandat_performance` expose :

- statut
- type_mandat
- est_exclusif
- nb_mandats
- nb_clients
- nb_chasseurs
- duree_moyenne_jours
- duree_min_jours
- duree_max_jours

Réconciliation :

```text
oltp_mandats     = 17
mart_mandats     = 17
oltp_clients     = 17 (clients représentés dans les mandats)
oltp_chasseurs   = 6
```

Les six groupes métier observés incluent ACTIF, EXPIRE, SUSPENDU et TERMINE, ainsi que les mandats EXCLUSIF / NON_EXCLUSIF.

---

## 7. Orchestration Airflow

Le DAG principal est :

```text
real_estate_ingestion
```

Il est publié dans le dépôt `airflow-dags` par le job GitLab CI `airflow:publish-dags`. Le scheduler utilise un conteneur `git-sync` qui synchronise ce dépôt dans un worktree monté dans Airflow.

La chaîne actuelle est :

```text
start
  -> generate_source_data
  -> load_raw
  -> validate_raw
  -> transform_staging
  -> validate_staging
  -> load_oltp
  -> validate_oltp
  -> load_warehouse
  -> validate_warehouse
  -> dbt_run
  -> dbt_test
  -> collect_metrics
  -> end
```

### 7.1 Validation historique

Les runs observés des 22, 23 et 24 août étaient tous en `success`.

### 7.2 Validation complète du 27 août 2026

Run :

```text
manual__2026-08-27T20:50:02+00:00
```

Toutes les tâches ont terminé avec succès :

```text
start                 success
generate_source_data  success
load_raw              success
validate_raw          success
transform_staging     success
validate_staging      success
load_oltp             success
validate_oltp         success
load_warehouse        success
validate_warehouse    success
dbt_run               success
dbt_test              success
collect_metrics       success
end                   success
```

Ceci valide désormais la chaîne Data complète **jusqu'à la collecte des métriques**.

---

## 8. Observabilité

Une structure dédiée `observability/` a été mise en place avec notamment :

```text
observability/
├── alerts/
├── grafana/
│   └── dashboards/
├── metrics/
└── prometheus/
```

La plateforme de monitoring Kubernetes existante comprend notamment :

- Prometheus / kube-prometheus-stack
- Alertmanager
- Grafana
- Loki
- Promtail
- Tempo
- OpenTelemetry Collector
- Pushgateway

Le Pushgateway utilisé est :

```text
retail-pushgateway.monitoring.svc.cluster.local:9091
```

Le DAG Airflow exécute maintenant `collect_metrics`, utilisant l'image data-pipeline et le code sous `/app/observability/metrics`.

Le run du 27 août confirme :

```text
collect_metrics = success
```

La collecte des métriques est donc intégrée à l'orchestration. La finalisation des dashboards/alertes peut être traitée séparément sans bloquer le cœur du pipeline.

---

## 9. OpenMetadata

Version actuellement utilisée :

```text
OpenMetadata Server 1.12.11
OpenMetadata ingestion image 1.12.11
```

Les composants principaux OpenMetadata/MySQL/OpenSearch sont opérationnels.

Trois workflows Real Estate sont déployés sous forme de CronJobs Kubernetes :

```text
real-estate-postgresql-ingestion
real-estate-postgresql-profiler
real-estate-dbt-ingestion
```

Ils sont actuellement configurés avec `suspend: true`, ce qui permet leur déclenchement contrôlé/manuellement pour validation.

Planification définie :

```text
PostgreSQL ingestion : 10 2 * * *
Profiler             : 45 2 * * *
dbt ingestion        : 30 3 * * *
```

### 9.1 PostgreSQL metadata ingestion

Un Job d'audit a été créé depuis le CronJob :

```text
real-estate-postgresql-ingestion-audit
```

Résultat :

```text
Complete 1/1
```

L'ingestion PostgreSQL vers OpenMetadata est donc validée.

### 9.2 PostgreSQL profiler

Job :

```text
real-estate-postgresql-profiler-audit
```

Résultat :

```text
Complete 1/1
```

Le profiler a indiqué notamment :

```text
Profiler: Processed 231 records
found 0 errors
```

Un avertissement existe pour `pg_stat_statements` : l'extension n'est pas présente et OpenMetadata ne peut donc pas récupérer les requêtes PostgreSQL via cette fonctionnalité optionnelle.

Ce point n'empêche pas le profiler de terminer avec succès.

### 9.3 dbt ingestion

Job :

```text
real-estate-dbt-ingestion-audit
```

Résultat Kubernetes :

```text
Complete 1/1
```

Les artifacts dbt sont bien générés :

```text
catalog.json
manifest.json
run_results.json
semantic_manifest.json
compiled/
run/
```

Configuration OpenMetadata effective :

```text
update_descriptions: true
update_owners: false
include_tags: true
service: real-estate-postgresql
```

Résumé final :

```text
Workflow dbt:
  Processed records: 108
  Errors: 0
  Success: 100%

Workflow OpenMetadata:
  Processed records: 126
  Errors: 0
  Success: 100%

Workflow Success: 100%
```

Le traitement de lineage est également visible dans les logs (`GetLineageByQuery`).

### 9.4 Points non bloquants détectés

Plusieurs descriptions de marts ont produit :

```text
Failed to update Table [...]
Reason: Invalid name ...
```

Les modèles concernés incluent notamment :

- `mart_mandat_performance`
- `mart_market_overview`
- `mart_market_by_source`
- `mart_market_by_property_type`
- `mart_market_by_dpe`
- `mart_market_evolution`

Le workflow global reste à 100 % et sans erreur déclarée, mais ces PATCH de métadonnées ont été ignorés. Ce point doit être nettoyé ultérieurement afin d'obtenir une publication de descriptions totalement propre.

OpenMetadata signale également l'absence d'un utilisateur/équipe `real_estate_user` lors de tentatives de résolution d'owner dbt. La configuration actuelle demande néanmoins `update_owners: false`; ce point n'est donc pas bloquant pour l'ingestion actuelle.

---

## 10. Governance-as-Code

Une couche Governance-as-Code dédiée est intégrée au projet avec :

```text
governance/
├── Dockerfile
├── apply-governance.sh
├── requirements.txt
├── scripts/main.py
├── docs/governance-config.json
├── glossary/real_estate_glossary.json
├── ownership/real_estate_ownership.json
├── quality/real_estate_quality.json
└── tagging/
    ├── real_estate_tags.json
    └── real_estate_data_layers.json
```

Le déploiement est piloté par GitLab CI et GitOps/Argo CD, et non par des opérations Kubernetes locales depuis Windows.

Le Job Kubernetes :

```text
real-estate-governance-apply
```

avait été validé avec :

```text
Complete 1/1
Governance-as-Code execution completed
```

Le tagging `DataLayer` a notamment été vérifié sur les dimensions et facts du Warehouse.

---

## 11. CI/CD et GitOps

Le projet utilise GitLab CI comme point d'entrée d'automatisation.

Les responsabilités sont séparées :

```text
Code source
    |
    v
GitLab CI
    |
    +--> validation DB / migrations
    +--> build image data-pipeline
    +--> publication DAG -> airflow-dags
    +--> publication manifests -> lab-gitops
    |
    v
Argo CD / git-sync / Kubernetes
```

Pour Airflow, le job `airflow:publish-dags` :

1. valide la présence du DAG ;
2. clone `https://gitlab.local/root/airflow-dags.git` ;
3. copie `pipelines/airflow/*.py` vers `dags/` ;
4. commit les changements ;
5. pousse sur `main`.

Le `git-sync` du scheduler récupère ensuite le dépôt. Cette architecture explique pourquoi modifier uniquement un fichier local Windows sans le sauvegarder/committer/publier ne modifie pas immédiatement le DAG Kubernetes.

Ce comportement a été vérifié lors de l'ajout de `collect_metrics`.

---

## 12. Validation de bout en bout obtenue

À ce stade, les composants suivants ont été réellement testés :

```text
Source/générateur             VALIDÉ
        |
RAW                           VALIDÉ
        |
Data Quality RAW              VALIDÉ
        |
STAGING                       VALIDÉ
        |
Data Quality STAGING          VALIDÉ
        |
OLTP real_estate              VALIDÉ
        |
Validation OLTP               VALIDÉ
        |
Warehouse                     VALIDÉ
        |
Validation Warehouse          VALIDÉ
        |
dbt run                       VALIDÉ
        |
dbt test                      VALIDÉ
        |
Analytics marts               VALIDÉ
        |
Metrics collection            VALIDÉ

PostgreSQL -> OpenMetadata    VALIDÉ
Profiler -> OpenMetadata      VALIDÉ
dbt -> OpenMetadata           VALIDÉ
Governance-as-Code            VALIDÉ
```

Le projet n'est donc plus au stade d'une architecture théorique : la chaîne a été déployée et exécutée sur Kubernetes avec des résultats observables.

---

## 13. Points restant à traiter

Les éléments suivants ne remettent pas en cause les validations précédentes mais restent à finaliser :

1. Corriger les descriptions dbt rejetées par OpenMetadata (`Invalid name`).
2. Décider si `pg_stat_statements` doit être activé pour enrichir OpenMetadata avec les statistiques/requêtes PostgreSQL.
3. Nettoyer si nécessaire les avertissements de résolution de l'owner `real_estate_user`.
4. Finaliser les dashboards Grafana/KPI et les alertes Prometheus comme volet observabilité.
5. Décider du passage des CronJobs OpenMetadata de `suspend: true` vers une exécution planifiée automatique lorsque la phase de validation manuelle sera terminée.
6. Continuer à enrichir les preuves, tests et documentation nécessaires au référentiel/à la soutenance.

---

## 14. Conclusion au 27 août 2026

La plateforme dispose maintenant d'une chaîne Data cohérente et effectivement opérationnelle :

```text
GitLab CI/CD
    -> Kubernetes
    -> Airflow
    -> RAW
    -> Data Quality
    -> STAGING
    -> OLTP
    -> Warehouse
    -> dbt
    -> Analytics
    -> Metrics
    -> OpenMetadata
    -> Governance
```

Les contrôles effectués ont confirmé la qualité des 6 000 annonces staging, la réconciliation des principales entités OLTP/Warehouse, l'intégrité des clés de `fact_annonce`, l'exécution complète du DAG Airflow avec `collect_metrics`, ainsi que les trois workflows OpenMetadata (metadata ingestion, profiler et dbt ingestion).

Le socle Data Engineering, analytique, gouvernance et observabilité est donc suffisamment avancé pour poursuivre les travaux à partir d'une base validée et documentée, plutôt que de reconstruire ou réexpliquer l'infrastructure à chaque étape.
