# OBSERVABILITY & MONITORING — REAL ESTATE DATA PLATFORM

> **Projet :** PROJECT_FIL_ROUGE — Chasse Immobilière  
> **Périmètre :** Observabilité, métriques Prometheus, Pushgateway, Grafana, PostgreSQL analytics, GitLab CI/CD et GitOps/Argo CD  
> **Statut :** Implémenté et validé — alerting avancé volontairement reporté  
> **Date de consolidation :** 27 août 2026

---

## 1. Objectif du document

Ce document décrit de manière monolithique l'implémentation de l'observabilité de la plateforme **Real Estate / Chasse Immobilière**.

L'objectif de cette partie du projet était de disposer d'une visibilité à deux niveaux :

1. **Business / analytique**
   - volume d'annonces ;
   - clients ;
   - chasseurs ;
   - mandats ;
   - prix immobilier ;
   - prix au m² ;
   - surface ;
   - répartition géographique ;
   - DPE ;
   - type de bien ;
   - évolution du marché ;
   - performance des mandats.

2. **Technique / Data Platform**
   - volumes des couches de données ;
   - état des modèles analytiques ;
   - métriques de pipeline ;
   - métriques de qualité ;
   - fraîcheur des données ;
   - exposition Prometheus ;
   - visualisation Grafana.

Cette implémentation constitue une couche transverse de la plateforme et ne remplace ni le pipeline Airflow, ni PostgreSQL, ni dbt, ni OpenMetadata.

---

## 2. Positionnement dans l'architecture globale

L'observabilité repose sur deux chemins complémentaires.

```text
                         REAL ESTATE DATA PLATFORM
                                   │
                ┌──────────────────┴──────────────────┐
                │                                     │
         BUSINESS / ANALYTICS                  OBSERVABILITY
                │                                     │
          PostgreSQL OLTP                       Airflow / scripts
                │                                     │
              RAW                                  Metrics
                │                                     │
            STAGING                             Pushgateway
                │                                     │
              OLTP                              Prometheus
                │                                     │
           WAREHOUSE                                  │
                │                                     │
              dbt                                     │
                │                                     │
         analytics.mart_*                             │
                │                                     │
        Grafana PostgreSQL                         Grafana
                │                                     │
                └──────────────────┬──────────────────┘
                                   │
                         Grafana Dashboard
```

La décision importante est de **ne pas utiliser Prometheus comme base analytique métier**.

Prometheus est utilisé pour les métriques opérationnelles et techniques.

PostgreSQL et les marts dbt sont utilisés pour les requêtes analytiques métier.

---

## 3. Principe de séparation des responsabilités

### 3.1 PostgreSQL / dbt

Les données analytiques riches restent dans PostgreSQL.

Les modèles actuellement disponibles comprennent notamment :

```text
analytics.mart_market_overview
analytics.mart_market_by_city
analytics.mart_market_by_dpe
analytics.mart_market_by_property_type
analytics.mart_market_by_source
analytics.mart_market_evolution
analytics.mart_mandat_performance
```

Ces vues sont directement interrogées par Grafana via le datasource PostgreSQL.

### 3.2 Prometheus

Prometheus est utilisé pour :

- les compteurs ;
- les gauges ;
- les volumes de tables ;
- l'état du pipeline ;
- la durée des traitements ;
- les résultats de contrôles DQ ;
- la fraîcheur ;
- les métriques destinées au monitoring.

### 3.3 Grafana

Grafana devient la couche de présentation commune :

```text
Grafana
├── Prometheus
│   └── métriques opérationnelles
│
└── Real Estate PostgreSQL
    └── KPI et analyses métier
```

Cette séparation évite de transformer Prometheus en entrepôt analytique.

---

## 4. Organisation du dépôt

Les composants développés sont répartis entre le code d'observabilité et les manifests de déploiement.

Structure logique :

```text
chasse_immobiliere/
│
├── observability/
│   ├── alerts/
│   ├── grafana/
│   │   └── dashboards/
│   ├── metrics/
│   │   ├── collect_metrics.py
│   │   └── metrics_exporter.py
│   └── prometheus/
│
├── deploy/
│   └── observability/
│       ├── application.yaml
│       ├── grafana-dashboard-configmap.yaml
│       ├── grafana-datasource.yaml.template
│       └── kustomization.yaml
│
└── .gitlab/
    └── ci/
        └── observability.yml
```

Le dashboard final est déployé depuis :

```text
deploy/observability/grafana-dashboard-configmap.yaml
```

---

## 5. Intégration dans l'image Data Pipeline

L'image utilisée par les traitements de données contient les scripts d'observabilité.

L'image est construite depuis :

```text
Dockerfile.data-pipeline
```

Les scripts présents dans l'image ont été vérifiés dans Kubernetes.

Commande de validation utilisée :

```bash
kubectl -n airflow run real-estate-observability-check \
  --restart=Never \
  --image=gitlab.local:4567/root/chasse_immobiliere/data-pipeline:latest \
  --overrides='
{
  "spec": {
    "imagePullSecrets": [
      {
        "name": "gitlab-registry"
      }
    ]
  }
}' \
  --command -- \
  /bin/sh -c 'echo "=== OBSERVABILITY FILES ==="; ls -l /app/observability/metrics; echo "=== PYTHON VALIDATION ==="; python -m py_compile /app/observability/metrics/*.py; echo "VALIDATION_OK"'
```

Résultat validé :

```text
=== OBSERVABILITY FILES ===
collect_metrics.py
metrics_exporter.py

=== PYTHON VALIDATION ===
VALIDATION_OK
```

Cela confirme que les scripts sont bien embarqués dans l'image utilisée dans Kubernetes.

---

## 6. Collecte des métriques

Le script principal de collecte est :

```text
observability/metrics/collect_metrics.py
```

Il se connecte à PostgreSQL et produit des métriques correspondant à plusieurs domaines.

Exemples de métriques validées :

```text
real_estate_market_listings_total
real_estate_market_average_price
real_estate_market_average_price_m2
real_estate_market_average_surface

real_estate_clients_total
real_estate_chasseurs_total
real_estate_mandats_total
real_estate_active_mandats
real_estate_paiements_total

real_estate_oltp_table_rows
real_estate_analytics_table_rows

real_estate_dq_checks_total
real_estate_dq_checks_passed
real_estate_dq_checks_failed
real_estate_dq_success_ratio
real_estate_dq_last_run_timestamp

real_estate_pipeline_duration_seconds
```

---

## 7. Incident rencontré : marts analytics absents

Lors du premier test du collecteur, l'exécution a échoué avec :

```text
relation "analytics.mart_market_overview" does not exist
```

La vérification PostgreSQL montrait initialement seulement :

```text
analytics.mart_market_by_city
analytics.stg_dim_bien
analytics.stg_fact_annonce
```

Cependant, les fichiers dbt étaient bien présents dans l'image :

```text
mart_mandat_performance.sql
mart_market_by_city.sql
mart_market_by_dpe.sql
mart_market_by_property_type.sql
mart_market_by_source.sql
mart_market_evolution.sql
mart_market_overview.sql
schema.yml
```

Un test dbt a ensuite révélé :

```text
Compilation Error

dbt found two schema.yml entries for the same resource named
mart_mandat_performance
```

La cause était une double déclaration de :

```yaml
- name: mart_mandat_performance
```

dans :

```text
pipelines/dbt/models/marts/schema.yml
```

Après correction et redéploiement, les marts nécessaires ont été créés et la collecte des métriques a réussi.

Résultat final :

```text
Collecting Real Estate observability metrics...
Real Estate observability metrics pushed successfully.
```

---

## 8. Pushgateway

La plateforme disposait déjà d'un Pushgateway dans le namespace :

```text
monitoring
```

Service utilisé :

```text
retail-pushgateway
```

Adresse interne :

```text
http://retail-pushgateway.monitoring.svc.cluster.local:9091
```

Même si son nom historique contient `retail`, il est utilisé comme composant partagé de la plateforme de monitoring.

Les métriques Real Estate ont été vérifiées directement :

```bash
kubectl -n monitoring exec deploy/retail-pushgateway -- \
  wget -qO- http://localhost:9091/metrics \
  | grep '^real_estate_' \
  | head -50
```

Exemples de valeurs observées :

```text
real_estate_active_mandats 10
real_estate_biens_total 6000
real_estate_chasseurs_total 6
real_estate_clients_total 18
real_estate_mandats_total 17

real_estate_market_average_price 192460.2215
real_estate_market_average_price_m2 1058.465865
real_estate_market_average_surface 231.4935
real_estate_market_listings_total 6000
```

Les marts étaient également exposés sous forme de métriques de volume :

```text
mart_mandat_performance       6
mart_market_by_city          17
mart_market_by_dpe            7
mart_market_by_property_type 10
mart_market_by_source         1
mart_market_evolution         2
mart_market_overview          1
```

---

## 9. Prometheus

Le service Prometheus est :

```text
monitoring-kube-prometheus-prometheus
```

dans :

```text
namespace: monitoring
```

La récupération effective d'une métrique a été validée directement via l'API Prometheus :

```bash
kubectl -n monitoring exec prometheus-monitoring-kube-prometheus-prometheus-0 -- \
  wget -qO- \
  'http://localhost:9090/api/v1/query?query=real_estate_market_listings_total'
```

Résultat :

```text
status: success
value: 6000
```

Les labels observés confirmaient le chemin :

```text
service="retail-pushgateway"
job="retail-pushgateway"
exported_job="real_estate_data_platform_test"
```

Le dashboard final accepte le job de test et le job cible avec un sélecteur compatible :

```promql
exported_job=~"real_estate_data_platform(_test)?"
```

---

## 10. Grafana existant

Grafana est fourni par :

```text
kube-prometheus-stack
```

Version observée :

```text
Grafana 12.4.3
```

Le déploiement est :

```text
monitoring-grafana
```

dans :

```text
namespace: monitoring
```

L'instance possède deux sidecars importants :

```text
grafana-sc-dashboard
grafana-sc-datasources
```

---

## 11. Provisioning automatique des dashboards

Le sidecar dashboard est configuré avec :

```text
METHOD=WATCH
LABEL=grafana_dashboard
LABEL_VALUE=1
FOLDER=/tmp/dashboards
RESOURCE=both
NAMESPACE=ALL
```

Ainsi, un ConfigMap ou Secret portant :

```yaml
grafana_dashboard: "1"
```

est détecté automatiquement.

Le dashboard Real Estate est donc publié sous forme de ConfigMap :

```yaml
apiVersion: v1
kind: ConfigMap

metadata:
  name: real-estate-platform-dashboard
  namespace: monitoring

  labels:
    grafana_dashboard: "1"
    app.kubernetes.io/name: real-estate-platform
    app.kubernetes.io/component: observability
```

La présence dans Kubernetes a été validée :

```bash
kubectl -n monitoring get configmap real-estate-platform-dashboard -o wide
```

Résultat :

```text
NAME                             DATA   AGE
real-estate-platform-dashboard   1      ...
```

Le sidecar a ensuite créé :

```text
/tmp/dashboards/real-estate-platform.json
```

dans le pod Grafana.

Commande :

```bash
kubectl -n monitoring exec deploy/monitoring-grafana \
  -c grafana-sc-dashboard -- \
  ls -l /tmp/dashboards | grep -i real-estate
```

Résultat :

```text
real-estate-platform.json
```

Le dashboard est ensuite apparu automatiquement dans l'interface Grafana.

---

## 12. Premier dashboard Prometheus

La première version contenait les KPI :

```text
Listings
Clients
Chasseurs
Mandates
Active Mandates
```

Valeurs validées :

```text
Listings         6000
Clients            18
Chasseurs            6
Mandates            17
Active Mandates     10
```

Un détail de présentation a été corrigé :

```json
"unit": "short"
```

affichait :

```text
6k
```

Pour obtenir :

```text
6000
```

le panel Listings utilise :

```json
"unit": "none"
```

---

## 13. Besoin d'un datasource PostgreSQL

Le dashboard initial était principalement alimenté par Prometheus.

Pour produire un vrai dashboard décisionnel, il était nécessaire d'interroger directement les marts dbt.

L'architecture cible est devenue :

```text
                         GRAFANA
                            │
               ┌────────────┴────────────┐
               │                         │
          PROMETHEUS                POSTGRESQL
               │                         │
     Operational Monitoring         Business Analytics
               │                         │
     real_estate_* metrics          analytics.mart_*
```

Prometheus reste utilisé pour :

```text
Pipeline
Data volumes
Data quality
Freshness
Health
```

PostgreSQL est utilisé pour :

```text
Market overview
City
Property type
DPE
Source
Evolution
Mandates
```

---

## 14. Provisioning du datasource PostgreSQL

Le datasource cible est :

```text
Name: Real Estate PostgreSQL
UID: real-estate-postgresql
Host: real-estate-postgresql.real-estate.svc.cluster.local:5432
Database: real_estate
User: real_estate_user
```

Le sidecar datasource Grafana est configuré avec :

```text
METHOD=WATCH
LABEL=grafana_datasource
LABEL_VALUE=1
FOLDER=/etc/grafana/provisioning/datasources
RESOURCE=both
```

Le point important est :

```text
RESOURCE=both
```

Le sidecar accepte donc les **ConfigMaps et Secrets**.

---

## 15. Gestion sécurisée du mot de passe PostgreSQL

Le mot de passe n'est volontairement pas stocké dans le ConfigMap du dashboard ni dans un manifest Git contenant une valeur en clair.

Le Secret PostgreSQL existant est :

```text
real-estate-postgresql-secret
```

dans :

```text
namespace: real-estate
```

Clés disponibles :

```text
POSTGRES_DB
POSTGRES_HOST
POSTGRES_PASSWORD
POSTGRES_PORT
POSTGRES_USER
```

Le datasource Grafana est généré à partir de ce Secret.

---

## 16. Template du datasource

Le dépôt contient :

```text
deploy/observability/grafana-datasource.yaml.template
```

Principe :

```yaml
apiVersion: 1

datasources:
  - name: Real Estate PostgreSQL
    type: postgres
    uid: real-estate-postgresql
    access: proxy

    url: ${POSTGRES_HOST}:${POSTGRES_PORT}

    user: ${POSTGRES_USER}
    database: ${POSTGRES_DB}

    jsonData:
      database: ${POSTGRES_DB}
      sslmode: disable
      postgresVersion: 1600
      timescaledb: false

    secureJsonData:
      password: ${POSTGRES_PASSWORD}

    editable: false
```

Le repository ne contient donc que :

```text
${POSTGRES_PASSWORD}
```

et non la valeur réelle.

---

## 17. Provisioning CI du datasource

Un job dédié a été ajouté :

```text
observability:provision-grafana-datasource
```

Le job utilise un runner :

```text
tags:
  - shell
```

Il :

1. lit le Secret PostgreSQL ;
2. exporte les variables ;
3. rend le template ;
4. crée un Secret dans `monitoring` ;
5. applique le label Grafana ;
6. supprime le fichier temporaire.

Flux :

```text
real-estate-postgresql-secret
        │
        ▼
GitLab Shell Runner
        │
        ├── POSTGRES_DB
        ├── POSTGRES_HOST
        ├── POSTGRES_PORT
        ├── POSTGRES_USER
        └── POSTGRES_PASSWORD
        │
        ▼
envsubst
        │
        ▼
/tmp/real-estate-grafana-datasource.yaml
        │
        ▼
Kubernetes Secret
real-estate-grafana-datasource
        │
        ▼
grafana_datasource=1
        │
        ▼
Grafana sidecar
```

---

## 18. Incident CI : Python absent sur le shell runner

La première implémentation utilisait Python pour rendre le template.

Le pipeline a échoué avec :

```text
bash: python: command not found
```

Le runner concerné utilisait :

```text
Shell (bash) executor
```

La présence de `envsubst` a été vérifiée :

```bash
command -v envsubst
```

Résultat :

```text
/usr/bin/envsubst
```

La génération a donc été remplacée par :

```bash
envsubst \
  < deploy/observability/grafana-datasource.yaml.template \
  > /tmp/real-estate-grafana-datasource.yaml
```

Cette solution est plus simple et évite une dépendance Python inutile sur le runner shell.

---

## 19. Création du Secret datasource

Le Secret est créé avec :

```bash
kubectl -n monitoring create secret generic \
  real-estate-grafana-datasource \
  --from-file=datasource.yaml=/tmp/real-estate-grafana-datasource.yaml \
  --dry-run=client \
  -o yaml \
| kubectl apply -f -
```

Puis labellisé :

```bash
kubectl -n monitoring label secret \
  real-estate-grafana-datasource \
  grafana_datasource=1 \
  --overwrite
```

Validation :

```bash
kubectl -n monitoring get secret real-estate-grafana-datasource
```

Résultat :

```text
NAME                             TYPE     DATA
real-estate-grafana-datasource   Opaque   1
```

---

## 20. Validation du sidecar datasource

La présence du fichier dans Grafana a été vérifiée :

```bash
kubectl -n monitoring exec deploy/monitoring-grafana \
  -c grafana-sc-datasources -- \
  ls -l /etc/grafana/provisioning/datasources
```

Résultat :

```text
datasource.yaml
```

Le datasource :

```text
Real Estate PostgreSQL
```

est également visible dans l'interface Grafana.

Le test de l'API Grafana avec BusyBox `wget` a retourné `401 Unauthorized` sans authentification.

Une tentative avec :

```text
--user
--password
```

a également échoué car le `wget` BusyBox de l'image Grafana ne supporte pas ces options.

Ce comportement ne constitue pas un incident du datasource : celui-ci était déjà visible et opérationnel dans l'interface Grafana.

---

## 21. GitOps

L'objectif était de ne pas effectuer le déploiement applicatif manuellement depuis Windows.

Le dépôt projet publie les manifests vers :

```text
lab-gitops
```

via GitLab CI.

Le flux est :

```text
chasse_immobiliere
       │
       ▼
GitLab CI
       │
       │ PAT
       ▼
lab-gitops
       │
       ▼
root-app
       │
       ▼
real-estate-observability
       │
       ▼
namespace monitoring
```

---

## 22. Pourquoi une Application Argo CD dédiée ?

L'application historique :

```text
monitoring
```

n'est pas une Application Git basée sur :

```text
workloads/monitoring
```

Elle pointe directement vers le chart Helm :

```text
repoURL: https://prometheus-community.github.io/helm-charts
chart: kube-prometheus-stack
targetRevision: 83.7.0
```

Par conséquent, ajouter :

```text
workloads/monitoring/real-estate
```

au dépôt GitOps ne suffisait pas pour que l'Application `monitoring` le déploie.

Une Application dédiée a donc été créée :

```text
real-estate-observability
```

qui suit le dépôt Git :

```text
https://gitlab.local/root/lab-gitops.git
```

sur :

```text
targetRevision: main
```

et déploie le bundle Real Estate dans :

```text
namespace: monitoring
```

Cette séparation évite de modifier la source Helm de l'Application `monitoring`.

---

## 23. Root Application / App-of-Apps

Le dépôt `lab-gitops` utilise un root app qui surveille :

```text
path: apps
```

avec récursion activée.

Configuration logique :

```text
Application Name: root-app
Repository: lab-gitops
Revision: main
Path: apps
Namespace: argocd
Prune: enabled
Self Heal: enabled
```

L'ajout de :

```text
apps/real-estate-observability/application.yaml
```

permet donc au root app de créer automatiquement l'Application dédiée.

Validation :

```bash
kubectl -n argocd get application real-estate-observability
```

Résultat :

```text
NAME                        SYNC STATUS   HEALTH STATUS
real-estate-observability   Synced        Healthy
```

---

## 24. GitLab PAT et publication GitOps

La publication vers `lab-gitops` utilise les credentials stockés dans :

```text
namespace: openmetadata
secret: lab-gitops-git-credentials
```

Clés utilisées :

```text
GIT_USERNAME
GIT_TOKEN
```

Le runner construit temporairement :

```text
/tmp/.netrc
```

avec :

```text
machine gitlab.local
login ${LAB_GITOPS_GIT_USER}
password ${LAB_GITOPS_GIT_TOKEN}
```

Puis clone :

```text
https://gitlab.local/root/lab-gitops.git
```

Le PAT n'est donc pas écrit directement dans `.gitlab-ci.yml`.

Le fichier `/tmp/.netrc` est supprimé dans `after_script`.

---

## 25. Jobs GitLab CI

Le pipeline observabilité comprend trois responsabilités principales.

### Validation

```text
observability:validate
```

Il vérifie notamment :

```text
deploy/observability/application.yaml
deploy/observability/grafana-dashboard-configmap.yaml
deploy/observability/grafana-datasource.yaml.template
deploy/observability/kustomization.yaml
```

Il valide également le JSON Grafana embarqué dans le ConfigMap.

### Publication GitOps

```text
observability:publish-gitops
```

Il :

- récupère le PAT ;
- clone `lab-gitops` ;
- publie les manifests ;
- ajoute l'Application si nécessaire ;
- commit ;
- push sur `main`.

### Provisioning datasource

```text
observability:provision-grafana-datasource
```

Il :

- récupère les credentials PostgreSQL ;
- rend le template ;
- crée/met à jour le Secret datasource ;
- applique `grafana_datasource=1`.

---

## 26. Kustomize

Le bundle local utilise :

```text
deploy/observability/kustomization.yaml
```

avec notamment :

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - grafana-dashboard-configmap.yaml
```

Le datasource contenant un secret réel n'est pas stocké comme ressource GitOps en clair.

---

## 27. Dashboard final

Le dashboard final est :

```text
Real Estate — Business KPIs & Platform
```

UID :

```text
real-estate-platform
```

Refresh :

```text
30s
```

Il combine :

```text
Prometheus
+
Real Estate PostgreSQL
```

---

## 28. KPI exécutifs

La première ligne fournit les indicateurs de synthèse :

```text
Listings
Clients
Chasseurs
Mandates
Active Mandates
Analytics Models
```

Les métriques sont issues de Prometheus.

---

## 29. Market Overview

Les indicateurs de marché comprennent :

```text
Average Property Price
Median Property Price
Average Price / m²
Average Surface
```

Selon l'indicateur, les données viennent de Prometheus ou de :

```text
analytics.mart_market_overview
```

---

## 30. Analyse géographique

Deux visualisations principales utilisent :

```text
analytics.mart_market_by_city
```

### Listings by City

Exemple de requête :

```sql
SELECT
    ville,
    nb_annonces
FROM analytics.mart_market_by_city
ORDER BY nb_annonces DESC;
```

### Average Price by City

```sql
SELECT
    ville,
    prix_moyen
FROM analytics.mart_market_by_city
ORDER BY prix_moyen DESC;
```

---

## 31. Analyse par type de bien

Le mart utilisé est :

```text
analytics.mart_market_by_property_type
```

Le dashboard permet notamment de représenter :

```text
Listings by Property Type
Average Price / m² by Property Type
```

---

## 32. Analyse DPE

Le mart utilisé est :

```text
analytics.mart_market_by_dpe
```

Visualisations :

```text
Listings by DPE
Average Price by DPE
```

Cette vue permet de rapprocher performance énergétique et caractéristiques du marché.

---

## 33. Évolution du marché

Le mart :

```text
analytics.mart_market_evolution
```

alimente les séries temporelles :

```text
Market Price Evolution
Listings Collected Over Time
```

Le dashboard peut ainsi suivre l'évolution des observations au fil des collectes.

---

## 34. Mandats

Le mart :

```text
analytics.mart_mandat_performance
```

alimente notamment :

```text
Mandates by Status
Exclusive vs Non-Exclusive Mandates
```

Cette partie rapproche l'activité métier de la chasse immobilière de la couche décisionnelle.

---

## 35. Sources de données

Le mart :

```text
analytics.mart_market_by_source
```

permet de suivre :

```text
Listings by Source
Last Data Collection
```

Il permet donc d'ajouter une dimension de provenance et de fraîcheur.

---

## 36. Volumétrie technique

Le dashboard comprend également des panels techniques :

```text
RAW Layer Volume
STAGING Layer Volume
OLTP Table Row Counts
Warehouse Table Row Counts
Analytics Model Row Counts
```

Ils permettent de vérifier rapidement la cohérence des volumes entre les couches.

---

## 37. Pipeline et qualité

Les métriques prévues/présentes couvrent notamment :

```text
Pipeline Status
Last Successful Metrics Collection

DQ Checks Total
DQ Checks Passed
DQ Checks Failed
DQ Success Ratio
DQ Last Run Timestamp
```

Au moment des tests observés, certaines métriques DQ avaient encore des valeurs nulles ou égales à zéro :

```text
real_estate_dq_checks_total 0
real_estate_dq_checks_passed 0
real_estate_dq_checks_failed 0
real_estate_dq_success_ratio 0
```

Cela ne signifie pas que la couche DQ n'existe pas ; cela indique que la remontée de ces résultats dans le collecteur Prometheus devra être finalisée ou reliée à l'exécution effective des contrôles.

---

## 38. Sécurité

Les choix suivants ont été appliqués :

### Pas de mot de passe DB dans le dashboard

Le dashboard ne contient aucun credential PostgreSQL.

### Pas de mot de passe DB en clair dans le dépôt

Le template utilise :

```text
${POSTGRES_PASSWORD}
```

### Source de vérité du secret

Le credential provient de :

```text
real-estate/real-estate-postgresql-secret
```

### Secret Grafana

Le datasource rendu est stocké dans :

```text
monitoring/real-estate-grafana-datasource
```

### PAT GitLab

Le PAT est lu depuis :

```text
openmetadata/lab-gitops-git-credentials
```

et injecté temporairement dans `.netrc`.

---

## 39. Attention : dette de sécurité historique

L'inspection de la configuration Grafana existante a montré que le datasource Retail historique contenait un mot de passe directement dans un ConfigMap Helm.

Cette configuration n'a pas été reproduite pour Real Estate.

Le modèle Real Estate constitue donc une amélioration :

```text
Retail historique
ConfigMap → mot de passe présent

Real Estate
Kubernetes Secret → CI → Secret Grafana
```

Une amélioration future pourra consister à migrer également le datasource Retail vers le même modèle.

---

## 40. Absence d'External Secrets / Sealed Secrets

La vérification suivante a été effectuée :

```bash
kubectl get crd | \
  grep -Ei 'externalsecret|secretstore|clustersecretstore|sealedsecret'
```

Aucun résultat.

Le cluster ne dispose donc actuellement ni de :

```text
External Secrets Operator
Sealed Secrets
```

Le mécanisme CI + Kubernetes Secret a été retenu pour éviter d'élargir inutilement le périmètre.

À terme, une solution dédiée de gestion GitOps des secrets pourra être étudiée.

---

## 41. Validation finale de la chaîne

La chaîne suivante a été validée :

```text
                        SOURCE REPOSITORY
                     chasse_immobiliere
                              │
                              ▼
                          GitLab CI
                              │
                  ┌───────────┴───────────┐
                  │                       │
                  ▼                       ▼
             lab-gitops           PostgreSQL Secret
                  │                       │
                  ▼                       ▼
               root-app              CI rendering
                  │                       │
                  ▼                       ▼
      real-estate-observability   Grafana datasource Secret
                  │                       │
                  └───────────┬───────────┘
                              ▼
                      namespace monitoring
                              │
                  ┌───────────┴───────────┐
                  │                       │
                  ▼                       ▼
          Dashboard ConfigMap       Datasource Secret
                  │                       │
                  ▼                       ▼
          Grafana dashboard         Grafana datasource
             sidecar                   sidecar
                  │                       │
                  └───────────┬───────────┘
                              ▼
                            Grafana
                  ┌───────────┴───────────┐
                  │                       │
                  ▼                       ▼
             Prometheus             PostgreSQL
                  │                       │
                  ▼                       ▼
          Technical metrics        Business marts
```

---

## 42. État validé

Les éléments suivants sont opérationnels :

| Composant | État |
|---|---|
| Scripts observabilité dans l'image Data Pipeline | Validé |
| Compilation Python des scripts | Validée |
| Collecte PostgreSQL | Validée |
| Push métriques vers Pushgateway | Validé |
| Scraping Prometheus | Validé |
| Requête Prometheus `real_estate_market_listings_total` | Validée |
| Dashboard ConfigMap | Déployé |
| Grafana dashboard sidecar | Validé |
| Dashboard visible dans Grafana | Validé |
| Application Argo CD dédiée | Synced / Healthy |
| Datasource PostgreSQL | Provisionné |
| Secret datasource Grafana | Créé |
| Grafana datasource sidecar | Validé |
| Datasource visible dans Grafana | Validé |
| KPI Prometheus | Validés |
| KPI PostgreSQL/dbt | Fonctionnels |
| Dashboard business complet | Déployé / fonctionnel |
| Alerting avancé | Reporté |

---

## 43. Éléments volontairement reportés

La partie observabilité est considérée suffisamment avancée pour revenir au cœur du Fil Rouge.

Les éléments suivants sont volontairement laissés pour une itération ultérieure :

```text
PrometheusRule spécifiques Real Estate
Alertes pipeline
Alertes de fraîcheur
Alertes Data Quality
Seuils de volumétrie
Alertmanager
Intégration Zammad Real Estate
SLO / SLI
Alertes Grafana
Notification d'échec Airflow
```

La plateforme dispose déjà d'Alertmanager et d'une intégration Zammad dans l'infrastructure générale, mais l'extension spécifique Real Estate n'a pas été réalisée dans cette itération.

---

## 44. Améliorations futures possibles

### Alerting

Créer des règles telles que :

```text
RealEstatePipelineFailed
RealEstateDataStale
RealEstateDQFailure
RealEstateWarehouseEmpty
RealEstateNoListings
RealEstateMetricsMissing
```

### Freshness

Suivre précisément :

```text
NOW - last_successful_ingestion
```

### Airflow

Exposer :

```text
DAG success
DAG failure
task duration
last successful run
```

### Data Quality

Faire remonter les résultats réels des tests SQL/dbt vers :

```text
real_estate_dq_checks_total
real_estate_dq_checks_passed
real_estate_dq_checks_failed
```

### Secrets

Introduire éventuellement :

```text
External Secrets Operator
```

ou :

```text
Sealed Secrets
```

pour une gestion GitOps native des secrets.

---

## 45. Commandes de diagnostic utiles

### Application Argo CD

```bash
kubectl -n argocd get application real-estate-observability
```

### Dashboard ConfigMap

```bash
kubectl -n monitoring get configmap \
  real-estate-platform-dashboard
```

### Datasource Secret

```bash
kubectl -n monitoring get secret \
  real-estate-grafana-datasource
```

### Dashboard chargé par le sidecar

```bash
kubectl -n monitoring exec deploy/monitoring-grafana \
  -c grafana-sc-dashboard -- \
  ls -l /tmp/dashboards
```

### Datasource chargé par le sidecar

```bash
kubectl -n monitoring exec deploy/monitoring-grafana \
  -c grafana-sc-datasources -- \
  ls -l /etc/grafana/provisioning/datasources
```

### Métriques Pushgateway

```bash
kubectl -n monitoring exec deploy/retail-pushgateway -- \
  wget -qO- http://localhost:9091/metrics \
  | grep '^real_estate_'
```

### Prometheus

```bash
kubectl -n monitoring exec \
  prometheus-monitoring-kube-prometheus-prometheus-0 -- \
  wget -qO- \
  'http://localhost:9090/api/v1/query?query=real_estate_market_listings_total'
```

### Tables analytics

```bash
kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql -U real_estate_user -d real_estate -c "
SELECT
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'analytics'
ORDER BY table_name;
"
```

---

## 46. Justification architecturale

Cette architecture a été choisie pour conserver une séparation claire :

```text
PostgreSQL
    = données métier et analytiques

dbt
    = transformation et modèles décisionnels

Prometheus
    = métriques opérationnelles

Pushgateway
    = exposition des métriques de traitements batch

Grafana
    = visualisation unifiée

GitLab CI
    = validation + publication + provisioning

lab-gitops
    = source de vérité des manifests déployés

Argo CD
    = réconciliation Kubernetes

Kubernetes Secrets
    = stockage runtime des credentials
```

Cette séparation permet d'éviter :

- les requêtes analytiques complexes dans Prometheus ;
- les secrets dans les dashboards ;
- les déploiements manuels depuis le poste Windows ;
- la modification directe des ressources gérées par Helm ;
- le couplage entre le projet Real Estate et le chart global de monitoring.

---

## 47. Conclusion

La side quest Observabilité a permis de transformer la plateforme Real Estate en une plateforme mesurable et visualisable.

La solution couvre désormais le chemin complet :

```text
Data
 ↓
PostgreSQL
 ↓
Warehouse
 ↓
dbt marts
 ↓
Business KPIs
 ↓
Grafana
```

et parallèlement :

```text
Pipeline
 ↓
Metrics collector
 ↓
Pushgateway
 ↓
Prometheus
 ↓
Technical KPIs
 ↓
Grafana
```

Le tout est intégré au mécanisme de déploiement :

```text
Git
 ↓
GitLab CI
 ↓
lab-gitops
 ↓
Argo CD
 ↓
Kubernetes
```

Le résultat est un dashboard Real Estate combinant **indicateurs métier** et **observabilité de la Data Platform**, provisionné automatiquement et reproductible.

La partie avancée d'alerting est volontairement reportée afin de revenir aux livrables principaux du **Fil Rouge**.

---

**Fin du document — Observability & Monitoring / Real Estate Data Platform**
