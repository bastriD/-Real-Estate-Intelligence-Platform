# BC01-C4 — Analyse des composants, interactions, dépendances et performances

## Enterprise Real Estate Intelligence Platform

**Projet :** Chasse Immobilière — Fil Rouge Data & IA  
**Bloc :** BC01 — Architecture et stratégie du système d'information  
**Compétence :** analyser les composants d'une architecture, leurs fonctions, leurs interactions, leurs dépendances et leurs caractéristiques de performance  
**Date :** septembre 2026

---

# 1. Objectif

Cette preuve présente l'analyse technique de l'architecture de la plateforme **Chasse Immobilière** sous l'angle :

- des composants du système ;
- de leur responsabilité ;
- de leurs interactions ;
- des protocoles et flux utilisés ;
- de leurs dépendances ;
- de la propagation possible des défaillances ;
- des performances observées ou instrumentées ;
- des limites de capacité identifiées ;
- des possibilités d'évolution et de mise à l'échelle.

L'analyse repose prioritairement sur l'état réellement observé du système et distingue explicitement :

- **CURRENT** : composant actuellement utilisé ;
- **RUNTIME-VERIFIED** : composant ou comportement vérifié sur la plateforme ;
- **HISTORICAL-MEASUREMENT** : mesure valide obtenue lors d'une exécution antérieure, mais non revalidée sur le Pod courant ;
- **IMMEDIATE-TARGET** : évolution décidée à court terme ;
- **DEFERRED** : évolution volontairement reportée.

Cette distinction évite de présenter une architecture cible comme si elle était déjà déployée.

---

# 2. Positionnement dans l'architecture globale

L'architecture de la plateforme peut être analysée selon plusieurs plans d'interaction distincts :

1. **plan applicatif synchrone** ;
2. **plan Data / traitements batch** ;
3. **plan de déploiement et de contrôle GitOps** ;
4. **plan d'observabilité** ;
5. **plan de sauvegarde et de reprise d'activité**.

Ces plans partagent certains composants, notamment Kubernetes et PostgreSQL, mais répondent à des responsabilités différentes.

La séparation permet d'identifier plus précisément :

- les dépendances critiques ;
- les chemins d'exécution ;
- les points uniques de défaillance ;
- les impacts d'une indisponibilité ;
- les besoins de supervision ;
- les futurs besoins de scalabilité.

---

# 3. Vue synthétique des composants

| Couche | Composant | Fonction principale | État |
|---|---|---|---|
| Accès | NGINX Ingress | Point d'entrée HTTP(S) de l'API Real Estate | IMMEDIATE-TARGET |
| Application | `real-estate-backend` Service | Routage Kubernetes vers le backend | RUNTIME-VERIFIED |
| Application | FastAPI Backend | API métier, authentification, recommandations, CRUD | RUNTIME-VERIFIED |
| Sécurité applicative | JWT / RBAC applicatif | Authentification et contrôle des rôles | RUNTIME-VERIFIED |
| Matching | Moteur déterministe | Éligibilité et classement des biens | IMPLEMENTED / TESTED |
| Persistance | PostgreSQL | OLTP, staging, warehouse et analytics | RUNTIME-VERIFIED |
| Orchestration Data | Airflow | Orchestration des traitements Data | CURRENT |
| Transformation | dbt / SQL | Transformation et validation Data | CURRENT |
| Gouvernance | OpenMetadata | Catalogue, métadonnées, qualité et lineage | CURRENT |
| MLOps | MLflow | Expérimentation et suivi ML | CURRENT |
| Object Storage | MinIO | Artefacts, données objet et sauvegardes | CURRENT |
| Observabilité | Prometheus | Collecte et interrogation des métriques | RUNTIME-VERIFIED |
| Observabilité | Grafana | Visualisation des métriques | CURRENT |
| Observabilité | Alertmanager | Routage des alertes Prometheus | CURRENT |
| Observabilité | Loki | Centralisation des logs | CURRENT |
| Observabilité | Tempo | Traces distribuées | CURRENT |
| Observabilité | OpenTelemetry Collector | Collecte / transport de télémétrie | CURRENT |
| Observabilité | Pushgateway | Métriques de traitements batch | CURRENT |
| CI/CD | GitLab CI | Validation, build et publication GitOps | CURRENT |
| Registry | GitLab Container Registry | Stockage des images applicatives | RUNTIME-VERIFIED |
| GitOps | `lab-gitops` | État désiré de la plateforme | CURRENT |
| GitOps | Argo CD | Réconciliation GitOps | RUNTIME-VERIFIED |
| Orchestration | Kubernetes | Exécution et orchestration des workloads | RUNTIME-VERIFIED |
| Réseau K8s | Flannel | Réseau Pod Kubernetes | CURRENT |
| Stockage K8s | local-path | Volumes persistants locaux | CURRENT |
| TLS | cert-manager | Gestion des certificats Kubernetes | CURRENT |
| PRA | Backup CronJob PostgreSQL | Sauvegarde automatisée de PostgreSQL | RUNTIME-VERIFIED |
| PRA | MinIO externe | Copie indépendante des sauvegardes | RUNTIME-VERIFIED |
| IA expérimentale | Ollama / Qwen / GPU | Expérimentation et inférence locale | EXPERIMENTAL |

---

# 4. Plan applicatif synchrone

## 4.1 État actuel

Lors de la vérification runtime, le namespace `real-estate` exposait :

```text
real-estate-backend      ClusterIP   :8000
real-estate-postgresql   ClusterIP   :5432
```

Aucun Ingress applicatif Real Estate n'était présent.

Le chemin applicatif actuel est donc principalement interne au cluster :

```text
Client interne / test / workload
        |
        v
real-estate-backend Service :8000
        |
        v
FastAPI Backend
        |
        v
real-estate-postgresql Service :5432
        |
        v
PostgreSQL
```

Le Service Kubernetes découple le consommateur de l'adresse IP du Pod backend.

---

# 5. Évolution immédiate — NGINX Ingress

La plateforme Kubernetes dispose déjà de NGINX Ingress au niveau infrastructure.

L'API Real Estate ne possède cependant pas encore son propre objet Ingress.

L'évolution immédiate retenue est :

```text
Utilisateur / Client API
        |
        | HTTPS
        v
NGINX Ingress
        |
        v
real-estate-backend Service :8000
        |
        v
FastAPI Backend
```

**État : IMMEDIATE-TARGET**

L'Ingress devra permettre :

- un point d'entrée stable ;
- une exposition HTTP(S) contrôlée ;
- une intégration avec le DNS du homelab ;
- une terminaison TLS ;
- la conservation du Service backend en `ClusterIP` ;
- la centralisation des règles d'entrée vers l'API.

Cette évolution ne doit être reclassée **RUNTIME-VERIFIED** qu'après :

1. création de l'objet Ingress ;
2. synchronisation GitOps ;
3. validation Argo CD ;
4. résolution DNS ;
5. test HTTP(S) ;
6. validation du certificat TLS.

---

# 6. Backend FastAPI

Le backend Real Estate est déployé sous forme d'un `Deployment` Kubernetes.

L'état runtime observé était :

```text
Deployment : real-estate-backend
Replicas   : 1/1
Pod        : Running
Restarts   : 0
Node       : k8s-wk-02
Image      : gitlab.local:4567/root/chasse_immobiliere/backend:875ade5c
```

Cette image permet également de relier le runtime au GitLab Container Registry.

Le backend expose notamment :

- authentification ;
- clients ;
- mandats ;
- demandes ;
- biens ;
- présentations ;
- recommandations ;
- visites ;
- santé ;
- disponibilité ;
- métriques Prometheus.

Les endpoints techniques comprennent :

```text
/health
/ready
/metrics
```

---

# 7. Ressources et limites du backend

Les ressources runtime ont été vérifiées :

| Ressource | Request | Limit |
|---|---:|---:|
| CPU | 100m | 500m |
| Mémoire | 128 MiB | 512 MiB |

Les probes sont :

```text
Liveness  : /health
Readiness : /ready
```

Ces mécanismes permettent à Kubernetes :

- de détecter un processus non sain ;
- d'éviter de router vers un Pod non prêt ;
- de redémarrer un conteneur en cas de défaillance détectée.

Ils ne constituent cependant pas une haute disponibilité applicative complète.

Le backend utilise actuellement :

```text
replicas = 1
```

La perte du Pod provoque donc une période d'indisponibilité jusqu'à son redémarrage ou son remplacement.

Le passage à plusieurs replicas reste une possibilité d'évolution après mesure des besoins réels.

---

# 8. Authentification et dépendance de sécurité

L'API utilise une authentification applicative.

Le système repose actuellement sur :

- `real_estate.utilisateur` ;
- mots de passe protégés par Argon2id ;
- JWT ;
- signature HS256 ;
- rôles applicatifs.

Les rôles actuellement définis sont :

```text
ADMIN
CLIENT
CHASSEUR
SERVICE
```

L'endpoint de recommandation a été testé sans authentification et a retourné :

```text
HTTP 401 Unauthorized
Authentication required
```

Le chemin réel devient donc :

```text
Client
  |
  v
Authentification / JWT
  |
  v
Autorisation applicative
  |
  v
Endpoint métier
  |
  v
Service métier
```

L'authentification est ainsi une dépendance fonctionnelle du chemin de recommandation.

---

# 9. Moteur de recommandation

Le moteur de recommandation actuellement utilisé en production est **déterministe**.

Il ne dépend pas du GPU, d'Ollama ou d'un LLM pour produire une recommandation.

Le chemin logique est :

```text
Demande versionnée
        |
        v
Chargement des candidats
        |
        v
Règles d'éligibilité métier
        |
        v
Population éligible
        |
        v
Construction des features
        |
        v
Score pondéré déterministe
        |
        v
Classement
        |
        v
Top-N
        |
        v
Présentation
```

Les poids de référence sont :

| Critère | Poids |
|---|---:|
| Localisation | 0,30 |
| Budget | 0,30 |
| Type de bien | 0,10 |
| Surface | 0,10 |
| Nombre de pièces | 0,07 |
| Nombre de chambres | 0,07 |
| DPE | 0,06 |

La logique conserve ainsi une séparation importante entre :

```text
éligibilité métier
        ↓
classement
```

Un futur modèle ML pourra améliorer le classement sans remplacer silencieusement les règles métier obligatoires.

---

# 10. Interaction du RecommendationService

Le service de recommandation réalise plusieurs opérations.

```text
API Recommendation
       |
       v
RecommendationService
       |
       +--> Validation des paramètres
       |
       +--> Chargement demande + biens
       |
       +--> Construction des features
       |
       +--> Calcul des scores
       |
       +--> Tri et Top-N
       |
       +--> Recherche Presentation existante
       |
       +--> Création si nécessaire
       |
       +--> Audit INSERT
       |
       v
Commit transactionnel
```

Le `limit` de recommandation est borné :

```text
1 <= limit <= 100
```

Cette limite protège l'API contre des demandes Top-N non bornées.

---

# 11. Dépendances PostgreSQL du moteur de recommandation

Le service de recommandation utilise PostgreSQL de deux manières :

```text
RecommendationService
       |
       +--> psycopg
       |      |
       |      +--> chargement des données de matching
       |
       +--> SQLAlchemy Session
              |
              +--> PresentationRepository
              |
              +--> AuditLogService
              |
              +--> transaction
```

La base est donc une dépendance critique du moteur de recommandation.

Une indisponibilité PostgreSQL peut empêcher :

- le chargement des candidats ;
- le classement ;
- la création des présentations ;
- la récupération des présentations existantes ;
- l'écriture de l'audit.

---

# 12. Cohérence transactionnelle

Lorsqu'une nouvelle présentation est créée par le moteur de recommandation :

```text
Création Presentation
        |
        v
Création AuditLog
        |
        v
COMMIT
```

Ces opérations participent à la même logique transactionnelle.

En cas d'erreur de persistance :

```text
erreur
  |
  v
ROLLBACK
```

Cette conception réduit le risque d'obtenir :

```text
Presentation créée
mais
Audit absent
```

ou une transaction métier partiellement persistée.

---

# 13. PostgreSQL comme composant central

PostgreSQL assure plusieurs responsabilités logiques :

```text
PostgreSQL
├── raw
├── staging
├── real_estate
├── warehouse
├── analytics
└── migration_control
```

Les responsabilités sont séparées par schéma et modèle de données même si elles utilisent actuellement la même technologie PostgreSQL.

Cette architecture a été retenue pour :

- limiter la complexité d'exploitation ;
- rester adaptée au volume actuel ;
- conserver SQL comme langage commun ;
- faciliter la traçabilité ;
- permettre une évolution ultérieure si les mesures le justifient.

Cette mutualisation implique néanmoins une dépendance technique commune.

Une saturation ou une indisponibilité de l'instance PostgreSQL peut affecter plusieurs plans du SI simultanément.

---

# 14. Limitation actuelle de PostgreSQL

L'architecture PostgreSQL observée utilise :

```text
Replicas     : 1
PVC          : 5 GiB
AccessMode   : RWO
StorageClass : local-path
```

Aucun mécanisme PostgreSQL de réplication ou de failover automatique n'a été démontré.

Il faut donc distinguer :

```text
Persistance Kubernetes
        !=
Haute disponibilité PostgreSQL
```

Le PVC permet la persistance lors de certains redémarrages de Pod.

Il ne protège pas à lui seul contre :

- la perte du stockage local ;
- la corruption ;
- la destruction du volume ;
- une défaillance nécessitant une reconstruction indépendante.

Cette dépendance est traitée en partie par le PRA.

---

# 15. Plan Data / batch

Le traitement Data suit la chaîne logique :

```text
Sources / génération
        |
        v
raw
        |
        v
staging
        |
        v
real_estate OLTP
        |
        v
warehouse OLAP
        |
        v
analytics
```

Airflow orchestre les traitements.

dbt / SQL assurent les transformations, tests et constructions analytiques.

La séparation OLTP / OLAP est logique et modélisée, mais repose actuellement sur une même technologie PostgreSQL.

Le plan batch n'est donc pas indépendant de la disponibilité de PostgreSQL.

---

# 16. Airflow

Airflow est utilisé comme orchestrateur de pipelines.

Ses responsabilités comprennent notamment :

- planification ;
- dépendances entre tâches ;
- exécution des traitements ;
- validation de pipelines ;
- déclenchement de traitements dbt ;
- collecte de métriques selon les workflows.

Le principe est :

```text
Airflow
   |
   +--> ingestion
   |
   +--> validation
   |
   +--> dbt
   |
   +--> métriques
```

Airflow est une dépendance d'orchestration des traitements batch, mais il n'est pas sur le chemin synchrone d'une requête API de recommandation.

Une panne Airflow peut donc interrompre ou retarder les traitements Data sans nécessairement rendre immédiatement indisponible l'API FastAPI.

---

# 17. OpenMetadata

OpenMetadata assure la gouvernance technique des données.

Il est utilisé pour :

- cataloguer les assets ;
- décrire les schémas ;
- centraliser les métadonnées ;
- gérer des éléments de qualité ;
- visualiser le lineage ;
- associer tags et gouvernance.

Les sources intégrées comprennent notamment des éléments PostgreSQL, Airflow et dbt.

OpenMetadata n'est pas le stockage métier et n'est pas un lakehouse.

Son indisponibilité affecte principalement :

- la gouvernance ;
- la découvrabilité ;
- la documentation technique ;
- la visualisation du lineage.

Elle ne doit pas interrompre directement le chemin synchrone de recommandation.

---

# 18. MLflow

MLflow est utilisé pour les activités MLOps et expérimentales :

- suivi des expériences ;
- paramètres ;
- métriques ;
- artefacts ;
- comparaison d'exécutions.

Le moteur de recommandation actuellement utilisé en production ne dépend pas d'un modèle MLflow servi en ligne.

La dépendance est donc actuellement :

```text
ML / expérimentation
       |
       v
MLflow
```

et non :

```text
API production
       |
       v
MLflow obligatoire
```

Cette distinction empêche une indisponibilité MLflow de devenir inutilement un point de panne du moteur déterministe.

---

# 19. GPU / Ollama / Qwen

La plateforme dispose d'une capacité IA locale expérimentale utilisant notamment :

```text
GPU GTX 1080 8 GB
Ollama
Qwen
```

L'inférence GPU a été validée dans le homelab.

Cependant :

```text
GPU / Ollama / Qwen
        !=
dépendance production du matching
```

Ces composants sont utilisés pour l'expérimentation et constituent une possibilité d'évolution.

Ils ne sont pas placés sur le chemin critique du moteur de recommandation déterministe.

Cette séparation améliore la résilience de l'application actuelle et évite qu'une panne GPU bloque le service métier principal.

---

# 20. Plan d'observabilité

L'architecture d'observabilité peut être représentée comme suit :

```text
FastAPI /metrics
       |
       v
real-estate-backend Service
       |
       v
ServiceMonitor
       |
       v
Prometheus
       |
       +--> Grafana
       |
       +--> Alertmanager
```

D'autres flux de télémétrie de la plateforme utilisent également :

```text
Logs       --> Loki
Traces     --> Tempo
Telemetry  --> OpenTelemetry Collector
Batch      --> Pushgateway
```

---

# 21. ServiceMonitor backend

Le backend possède un `ServiceMonitor`.

Configuration :

```text
namespace source : real-estate
selector         : app=real-estate-backend
port             : http
path             : /metrics
interval         : 30s
```

La chaîne est donc :

```text
Prometheus
    |
    | toutes les 30 secondes
    v
ServiceMonitor
    |
    v
Service real-estate-backend
    |
    v
FastAPI /metrics
```

Une interrogation runtime de Prometheus a retourné les métriques du Pod backend courant.

La collecte est donc **RUNTIME-VERIFIED**.

---

# 22. Métriques API

Le backend instrumente notamment :

```text
real_estate_api_requests_total
real_estate_api_request_duration_seconds
real_estate_api_errors_total
```

Ces métriques permettent une approche de type RED :

- **Rate** : volume de requêtes ;
- **Errors** : erreurs ;
- **Duration** : latence.

Les labels utilisent notamment :

```text
method
path
status_code
```

Le chemin FastAPI est normalisé à partir de la route.

Cela évite de transformer des identifiants métier variables en labels Prometheus et limite ainsi la cardinalité.

---

# 23. Métriques du moteur de recommandation

Le service de recommandation instrumente :

```text
real_estate_recommendation_requests_total
real_estate_recommendation_failures_total
real_estate_recommendation_duration_seconds
real_estate_recommendation_eligible_candidates
real_estate_recommendation_selected_candidates
real_estate_recommendation_presentations_created
real_estate_recommendation_presentations_existing
```

Les types d'erreur sont catégorisés, notamment pour distinguer :

- validation ;
- persistance ;
- erreur inattendue.

Les identifiants de demande ou de bien ne sont volontairement pas utilisés comme labels Prometheus.

Cette décision réduit le risque de forte cardinalité.

---

# 24. Mesures de recommandation

Une mesure historique validée sur une exécution antérieure a observé :

```text
demande_version       : 55
eligible_candidates   : 400
selected_candidates   : 10
failures              : 0
P95 duration          : ~0.2425 s
```

Cette mesure constitue une **HISTORICAL-MEASUREMENT**.

Elle ne doit pas être présentée comme la mesure du Pod actuellement déployé.

Lors de la vérification runtime la plus récente, le Pod courant exposait bien les séries Prometheus, mais les compteurs de recommandation étaient encore à :

```text
0 observation
```

La conclusion correcte est donc :

```text
Instrumentation actuelle : RUNTIME-VERIFIED
Mesure P95 ~0.2425 s      : HISTORICAL-MEASUREMENT
Benchmark courant         : non réalisé
```

Cette distinction garantit la traçabilité de la preuve de performance.

---

# 25. Métriques batch

Les traitements batch peuvent publier des métriques via Pushgateway.

Le principe architectural est :

```text
Job / pipeline
      |
      | push metrics
      v
Pushgateway
      |
      v
Prometheus
      |
      v
Grafana / Alertmanager
```

Cette approche est adaptée aux traitements qui ne restent pas actifs suffisamment longtemps pour être scrappés comme un service HTTP permanent.

---

# 26. Plan de déploiement et de contrôle

Le chemin de déploiement suit le principe :

```text
Développeur
    |
    | git push
    v
chasse_immobiliere
    |
    v
GitLab CI
    |
    +--> tests / validation
    |
    +--> build image
    |
    +--> GitLab Container Registry
    |
    +--> publication état désiré
             |
             v
         lab-gitops
             |
             v
          Argo CD
             |
             v
        Kubernetes
```

Le repository applicatif et le repository GitOps ont des responsabilités différentes :

```text
chasse_immobiliere
        =
source applicative + manifests sources + CI

lab-gitops
        =
état désiré réellement réconcilié par Argo CD
```

Cette séparation évite de confondre code source et état de déploiement.

---

# 27. Argo CD

L'application backend utilise notamment :

```text
Repository :
https://gitlab.local/root/lab-gitops.git

Branch :
main

Path :
workloads/real-estate/backend

Namespace :
real-estate
```

La politique automatique inclut :

```text
prune    : true
selfHeal : true
```

Argo CD assure donc la convergence entre :

```text
état désiré Git
        |
        v
état Kubernetes
```

Une modification manuelle du runtime peut être corrigée par la réconciliation GitOps.

---

# 28. Différence entre GitOps et chemin métier

Le plan de contrôle ne doit pas être confondu avec le plan applicatif.

Une requête utilisateur normale ne traverse pas :

```text
GitLab
Argo CD
Registry
```

Le chemin utilisateur est :

```text
Client
  |
  v
API
  |
  v
PostgreSQL
```

alors que le chemin de déploiement est :

```text
Git
  |
  v
CI
  |
  v
Registry / GitOps
  |
  v
Argo CD
  |
  v
Kubernetes
```

Cette séparation permet de comprendre qu'une panne GitLab n'arrête pas nécessairement immédiatement un backend déjà déployé, mais empêche ou complique les nouvelles livraisons.

---

# 29. Plan PRA

La base PostgreSQL utilise un stockage `local-path`.

Une copie externe indépendante a donc été mise en place.

Le chemin PRA est :

```text
PostgreSQL
     |
     | pg_dump
     v
Backup CronJob
     |
     | validation pg_restore --list
     | SHA-256
     v
MinIO externe
minio.lab.local:9000
     |
     v
real-estate-backups
```

La restauration testée suit :

```text
real-estate-backups
        |
        | download
        v
PostgreSQL 16 isolé
        |
        | pg_restore
        v
Base restaurée
        |
        | contrôles SQL
        v
Validation d'intégrité
```

---

# 30. Dépendance MinIO du PRA

Le MinIO utilisé pour le PRA est externe au PVC PostgreSQL Kubernetes.

Cette séparation permet de protéger la sauvegarde contre une perte du stockage local PostgreSQL.

Le bucket dédié est :

```text
real-estate-backups
```

avec versioning activé.

Une identité dédiée et une politique de moindre privilège ont également été validées.

Le compte de sauvegarde peut accéder au bucket de backup mais son accès au bucket Data `real-estate` a été refusé lors du test.

MinIO devient ainsi une dépendance du **processus de sauvegarde/reprise**, mais pas du chemin synchrone normal de l'API de recommandation.

---

# 31. Performance de restauration PostgreSQL

La base de production mesurée lors du test représentait environ :

```text
47 MB
```

Le dump compressé représentait environ :

```text
4.3 MiB
```

Le dump a été validé avec :

```text
pg_restore --list
```

et contenait :

```text
394 entries
```

La restauration PostgreSQL dans un environnement isolé a été mesurée à :

```text
6 secondes
```

Les comptes métier sélectionnés ont ensuite correspondu aux valeurs de production.

Exemples :

| Entité | Production | Restauré |
|---|---:|---:|
| `bien` | 14 000 | 14 000 |
| `client` | 18 | 18 |
| `demande` | 87 | 87 |
| `demande_version` | 88 | 88 |
| `mandat` | 17 | 17 |
| `presentation` | 12 | 12 |
| `visite` | 1 | 1 |
| `audit_log` | 10 | 10 |

Le résultat valide le composant de restauration de la base.

Cependant :

```text
pg_restore = 6 secondes
```

ne signifie pas :

```text
RTO plateforme = 6 secondes
```

Le RTO complet doit aussi prendre en compte :

- provisioning ;
- récupération du backup ;
- restauration ;
- contrôles ;
- reconnexion applicative ;
- validation de l'API ;
- éventuel basculement réseau/DNS.

Le RTO opérationnel complet n'est donc pas encore mesuré.

---

# 32. RPO et sauvegarde quotidienne

Le CronJob permanent est configuré sur une fréquence quotidienne :

```text
0 2 * * *
```

avec :

```text
concurrencyPolicy: Forbid
```

Cette fréquence permet de définir un objectif théorique :

```text
RPO cible <= 24 heures
```

Il faut distinguer cet objectif de planification d'un SLA mesuré sur une longue période.

---

# 33. Dépendances critiques

## 33.1 PostgreSQL

Criticité :

**TRÈS ÉLEVÉE**

Dépendants :

- API ;
- recommandations ;
- présentations ;
- audit ;
- pipelines Data ;
- warehouse ;
- analytics ;
- certaines fonctions de gouvernance.

Défaillance :

```text
PostgreSQL indisponible
        |
        +--> API métier dégradée / indisponible
        +--> recommandations indisponibles
        +--> persistance impossible
        +--> pipelines Data affectés
```

---

## 33.2 Backend FastAPI

Criticité :

**ÉLEVÉE pour le plan applicatif**

Défaillance :

```text
Backend indisponible
       |
       v
API indisponible
```

Le backend n'a actuellement qu'un replica.

---

## 33.3 Kubernetes

Criticité :

**ÉLEVÉE**

Kubernetes fournit :

- scheduling ;
- Services ;
- restart ;
- probes ;
- Secrets ;
- workloads ;
- orchestration.

Une dégradation importante du cluster peut affecter plusieurs composants simultanément.

Le control plane est distribué sur plusieurs nœuds, mais cela ne transforme pas automatiquement tous les workloads en services hautement disponibles.

---

## 33.4 GitLab / Argo CD

Criticité :

**ÉLEVÉE pour les changements et déploiements**

Une panne de GitLab ou du chemin GitOps n'implique pas nécessairement l'arrêt immédiat d'un backend déjà en cours d'exécution.

Elle affecte principalement :

- nouvelles versions ;
- corrections ;
- publication des manifests ;
- convergence après certains changements.

---

## 33.5 MinIO externe

Criticité :

**ÉLEVÉE pour le PRA**

Une indisponibilité MinIO peut empêcher :

- l'upload d'une nouvelle sauvegarde ;
- la récupération d'un backup au moment d'une reprise.

Elle ne bloque pas directement le moteur de recommandation en fonctionnement normal.

---

## 33.6 Airflow

Criticité :

**ÉLEVÉE pour les traitements batch**

Une panne Airflow affecte principalement :

- planification ;
- ingestion ;
- transformations orchestrées ;
- traitements programmés.

Elle n'est pas une dépendance directe du chemin synchrone de l'API.

---

## 33.7 OpenMetadata

Criticité :

**MOYENNE pour l'exploitation / gouvernance**

Son indisponibilité dégrade :

- catalogue ;
- lineage ;
- gouvernance ;
- consultation des métadonnées.

Elle ne bloque pas directement l'exécution du backend métier.

---

## 33.8 MLflow / GPU / Ollama

Criticité actuelle :

**FAIBLE pour le chemin métier de production**

Ces composants concernent principalement les expérimentations ML/IA.

Le moteur de recommandation déterministe reste indépendant de leur disponibilité.

---

# 34. Matrice de dépendances

| Composant | Dépendance principale | Impact en cas de perte |
|---|---|---|
| NGINX Ingress | Service backend | Accès externe API impossible |
| Backend | PostgreSQL | Fonctions métier fortement dégradées |
| Auth | PostgreSQL + secret JWT | Authentification impossible |
| RecommendationService | PostgreSQL + moteur déterministe | Recommandations impossibles |
| PresentationRepository | PostgreSQL | Persistance impossible |
| AuditLogService | PostgreSQL | Audit métier impossible |
| Airflow | K8s + sources Data + PostgreSQL | Pipelines retardés/interrompus |
| dbt | PostgreSQL | Transformations impossibles |
| OpenMetadata | Sources de métadonnées | Gouvernance/lineage dégradés |
| Prometheus | Targets / ServiceMonitor | Perte de visibilité métrique |
| Grafana | Prometheus et autres datasources | Visualisation dégradée |
| GitLab CI | GitLab/runner/registry/GitOps | Livraison impossible |
| Argo CD | `lab-gitops` + Kubernetes | Réconciliation impossible |
| Backup CronJob | PostgreSQL + MinIO | Nouvelle sauvegarde impossible |
| Restore PRA | MinIO + PostgreSQL cible | Reprise impossible |
| MLflow | backend MLflow + stockage artefacts | Expérimentation ML affectée |
| Ollama | GPU / nœud IA | Expérimentation IA indisponible |

---

# 35. Propagation des défaillances

Toutes les dépendances n'ont pas le même effet.

## PostgreSQL

```text
PostgreSQL DOWN
    |
    +--> Backend métier
    +--> Matching
    +--> Présentations
    +--> Audit
    +--> dbt
    +--> pipelines dépendants
```

Impact transversal important.

## Airflow

```text
Airflow DOWN
    |
    +--> Batch retardé
    +--> ingestion retardée
    +--> transformations retardées

mais

API déjà déployée
    |
    +--> peut continuer si ses données et PostgreSQL restent disponibles
```

## MLflow

```text
MLflow DOWN
    |
    +--> Expérimentation ML affectée

mais

Matching déterministe
    |
    +--> reste indépendant
```

## MinIO PRA

```text
MinIO DOWN
    |
    +--> nouveau backup impossible
    +--> récupération backup impossible

mais

API courante
    |
    +--> pas nécessairement interrompue
```

Cette analyse permet de différencier les dépendances de **runtime métier**, de **Data**, de **contrôle**, d'**observabilité** et de **reprise**.

---

# 36. Points de performance observés

| Élément | Valeur | Qualification |
|---|---:|---|
| Backend replicas | 1 | RUNTIME-VERIFIED |
| Backend CPU request | 100m | RUNTIME-VERIFIED |
| Backend CPU limit | 500m | RUNTIME-VERIFIED |
| Backend memory request | 128 MiB | RUNTIME-VERIFIED |
| Backend memory limit | 512 MiB | RUNTIME-VERIFIED |
| Prometheus scrape | 30 s | IMPLEMENTED / RUNTIME-VERIFIED |
| Recommendation eligible | 400 | HISTORICAL-MEASUREMENT |
| Recommendation selected | 10 | HISTORICAL-MEASUREMENT |
| Recommendation failures | 0 | HISTORICAL-MEASUREMENT |
| Recommendation P95 | ~0,2425 s | HISTORICAL-MEASUREMENT |
| Recommendation Top-N max | 100 | IMPLEMENTED |
| Production DB size during PRA | ~47 MB | MEASURED |
| Compressed PRA dump | ~4,3 MiB | MEASURED |
| Restore catalogue | 394 entries | MEASURED |
| `pg_restore` component | 6 s | MEASURED |
| Full operational RTO | Non mesuré | NOT EVIDENCED |
| RPO target | <= 24 h | TARGET derived from daily schedule |

---

# 37. Performance observable mais non benchmarkée

Certains composants sont instrumentés sans disposer encore d'un benchmark formel actuel.

Cela concerne notamment :

- latence API courante ;
- débit maximum du backend ;
- saturation CPU ;
- saturation mémoire ;
- nombre maximal de requêtes concurrentes ;
- capacité PostgreSQL ;
- contention OLTP / OLAP ;
- durée complète des pipelines ;
- performance du warehouse sous charge ;
- capacité maximale du stockage ;
- RTO complet ;
- capacité maximale du GPU.

Ces éléments doivent être mesurés avant toute décision de surdimensionnement ou de migration technologique.

---

# 38. Bottlenecks potentiels

Les éléments suivants sont identifiés comme **risques ou bottlenecks potentiels**, et non comme des saturations actuellement démontrées.

## 38.1 Backend mono-replica

```text
replicas = 1
```

Conséquences possibles :

- interruption lors d'un redémarrage ;
- absence de répartition horizontale ;
- capacité limitée à un Pod.

Évolution possible :

```text
plusieurs replicas
+
Ingress / Service
+
mesures de charge
```

---

## 38.2 PostgreSQL mono-instance

Le même moteur PostgreSQL porte plusieurs responsabilités logiques.

Risque potentiel :

- contention OLTP / OLAP ;
- point de panne commun ;
- limite de montée en charge verticale ;
- maintenance affectant plusieurs usages.

La séparation physique ne sera envisagée que si les mesures la justifient.

---

## 38.3 Stockage `local-path`

Le stockage PostgreSQL est :

```text
RWO
local-path
```

Il est simple et adapté au homelab actuel mais n'offre pas à lui seul une architecture de stockage distribuée.

Le PRA externe réduit le risque de perte définitive mais ne fournit pas de failover instantané.

---

## 38.4 Traitements batch

Les traitements Data peuvent concurrencer PostgreSQL avec les usages transactionnels.

Il faut donc surveiller :

- durée des jobs ;
- horaires d'exécution ;
- CPU ;
- mémoire ;
- I/O ;
- verrous ;
- requêtes lentes.

---

## 38.5 GPU expérimental

Le GPU GTX 1080 dispose de ressources limitées par rapport aux plateformes IA modernes.

Cette contrainte peut affecter :

- taille des modèles ;
- contexte ;
- concurrence ;
- temps d'inférence.

Elle n'affecte pas actuellement le matching déterministe de production.

---

# 39. Principes de scalabilité retenus

La stratégie n'est pas de distribuer tous les composants immédiatement.

Elle suit :

```text
Observer
   ↓
Mesurer
   ↓
Identifier le bottleneck
   ↓
Optimiser
   ↓
Scaler uniquement si nécessaire
```

Exemples :

### Backend

```text
1 replica
   ↓
mesure charge / latence
   ↓
plusieurs replicas si nécessaire
```

### PostgreSQL

```text
instance actuelle
   ↓
EXPLAIN / métriques / charge
   ↓
index / requêtes / tuning
   ↓
réplication ou séparation si justifiée
```

### OLAP

```text
warehouse PostgreSQL
   ↓
mesure volume / latence
   ↓
partitionnement
ou
moteur analytique spécialisé
si nécessaire
```

### IA

```text
baseline déterministe
   ↓
évaluation ML
   ↓
gain mesuré
   ↓
intégration production éventuelle
```

Cette approche évite une complexité distribuée prématurée.

---

# 40. Architecture CURRENT vs IMMEDIATE TARGET

## CURRENT

```text
Client interne
      |
      v
ClusterIP Backend :8000
      |
      v
FastAPI
      |
      v
PostgreSQL :5432
```

## IMMEDIATE TARGET

```text
Client
   |
   | HTTPS
   v
NGINX Ingress
   |
   v
ClusterIP Backend :8000
   |
   v
FastAPI
   |
   v
PostgreSQL :5432
```

Le changement ne modifie pas la responsabilité du backend ou de PostgreSQL.

Il ajoute une couche d'accès externe contrôlée.

---

# 41. Composants volontairement non placés dans le chemin critique

Les composants suivants ne doivent pas être présentés comme des dépendances obligatoires de l'API de recommandation actuelle :

```text
MLflow
Ollama
Qwen
GPU
OpenMetadata
Airflow
Grafana
```

Ils remplissent des fonctions importantes mais appartiennent à d'autres plans.

Cette séparation réduit le couplage.

---

# 42. Technologies non retenues actuellement

Les technologies suivantes ne font pas partie du runtime actuel de la plateforme Real Estate :

- Databricks ;
- Snowflake ;
- Kafka ;
- Qdrant ;
- Kubeflow comme remplacement de MLflow ;
- architecture RAG de production ;
- service mesh ;
- moteur lakehouse distribué ;
- réplication PostgreSQL automatique démontrée.

Certaines peuvent constituer des options futures.

Elles ne doivent pas être ajoutées simplement pour augmenter le nombre de technologies du projet.

Toute introduction devra répondre à :

```text
problème mesuré
        +
bénéfice démontrable
        +
coût d'exploitation acceptable
```

---

# 43. Relation avec les risques du SI

L'analyse des dépendances rejoint directement le registre des risques.

Les principaux liens sont :

| Risque | Relation avec C4 |
|---|---|
| RISK-INFRA-002 | Saturation / perte stockage |
| RISK-K8S-001 | Indisponibilité d'un nœud |
| RISK-NET-001 | Routage / DNS |
| RISK-DATA-001 | Perte / corruption PostgreSQL |
| RISK-OPS-001 | Sauvegarde absente ou obsolète |
| RISK-OPS-002 | Durée de reprise |
| RISK-OPS-003 | Perte d'observabilité |
| RISK-DATA-002 | Fausse confiance dans la qualité |
| RISK-SEC-001 | Exposition de secrets |
| RISK-SEC-002 | Autorisation fine incomplète |
| RISK-SEC-003 | Couverture d'audit incomplète |
| RISK-ARCH-001 | Dérive documentation / runtime |
| RISK-AI-001 | Indisponibilité nœud GPU |
| RISK-AI-002 | Confusion ML expérimental / production |
| RISK-PROJ-001 | Expansion excessive du périmètre |

C4 permet donc de transformer la cartographie technique en analyse d'impact.

---

# 44. Arbitrages architecturaux

Plusieurs décisions ressortent de l'analyse.

## 44.1 Conserver PostgreSQL comme socle actuel

Justification :

- volumes actuels maîtrisables ;
- expertise SQL ;
- architecture déjà opérationnelle ;
- simplification d'exploitation ;
- absence de preuve nécessitant immédiatement un moteur distribué.

## 44.2 Conserver le matching déterministe en production

Justification :

- explicabilité ;
- règles métier fortes ;
- reproductibilité ;
- indépendance GPU ;
- faible complexité opérationnelle.

## 44.3 Utiliser ML/IA comme évolution mesurée

Le ML doit démontrer un gain avant de devenir une dépendance de production.

## 44.4 Ajouter l'Ingress

Le backend doit disposer d'un point d'entrée HTTP(S) propre et contrôlé.

Cette évolution est la prochaine modification d'architecture prévue.

## 44.5 Ne pas confondre Kubernetes et HA PostgreSQL

Le restart d'un Pod ne remplace ni la réplication ni le PRA.

## 44.6 Maintenir une sauvegarde externe

Le backup MinIO indépendant du PVC local réduit le risque de perte définitive.

---

# 45. Architecture orientée mesure

La plateforme possède maintenant plusieurs points permettant de prendre des décisions à partir de données :

```text
Backend
   |
   +--> requêtes
   +--> erreurs
   +--> durée
   +--> recommandations
   +--> candidats
   +--> persistance

Kubernetes
   |
   +--> CPU
   +--> mémoire
   +--> état des Pods
   +--> disponibilité

PostgreSQL
   |
   +--> taille
   +--> requêtes
   +--> EXPLAIN
   +--> durée des traitements

PRA
   |
   +--> taille backup
   +--> succès/échec
   +--> durée restore
```

L'objectif architectural est donc :

> **mesurer avant de distribuer ou de remplacer une technologie.**

---

# 46. Diagramme composant

Le diagramme PlantUML associé à cette preuve doit représenter les cinq plans :

```text
1. Application / Request Plane
2. Data / Batch Plane
3. Deployment / Control Plane
4. Observability Plane
5. Backup / Recovery Plane
```

Il doit également différencier visuellement :

- CURRENT / RUNTIME-VERIFIED ;
- IMMEDIATE-TARGET ;
- EXPERIMENTAL / DEFERRED.

Fichier associé :

```text
01-Composants-Interactions.puml
```

L'Ingress NGINX devra apparaître comme :

```text
IMMEDIATE-TARGET
```

jusqu'à son déploiement.

---

# 47. Synthèse pour le jury

L'architecture n'est pas analysée uniquement comme une liste de technologies.

Chaque composant est associé à :

1. une responsabilité ;
2. un plan d'interaction ;
3. des dépendances ;
4. un impact en cas de panne ;
5. des métriques ou possibilités de mesure ;
6. une stratégie d'évolution.

Le chemin métier principal est volontairement court :

```text
Client
   ↓
Ingress [IMMEDIATE-TARGET]
   ↓
FastAPI
   ↓
PostgreSQL
```

Le moteur de recommandation conserve également un chemin déterministe :

```text
Demande
   ↓
Éligibilité
   ↓
Scoring
   ↓
Top-N
   ↓
Presentation
   ↓
Audit
```

Les composants Data, MLOps, observabilité, GitOps et PRA sont connectés à la plateforme sans être artificiellement placés dans le chemin synchrone de chaque requête.

Les principales limites actuelles sont identifiées :

- backend mono-replica ;
- PostgreSQL mono-instance ;
- stockage `local-path` RWO ;
- absence actuelle d'Ingress applicatif ;
- absence de HA PostgreSQL démontrée ;
- benchmark de charge complet encore à réaliser ;
- RTO opérationnel complet non mesuré.

En parallèle, plusieurs mécanismes réduisent déjà les risques :

- probes Kubernetes ;
- limites de ressources ;
- GitOps ;
- métriques Prometheus ;
- audit applicatif ;
- transactions ;
- sauvegarde PostgreSQL externe ;
- restauration isolée validée ;
- séparation entre production déterministe et expérimentation ML/IA.

---

# 48. Statut de la preuve

| Élément | Statut |
|---|---|
| Inventaire des composants | EVIDENCED |
| Fonctions des composants | EVIDENCED |
| Plan applicatif | RUNTIME-VERIFIED |
| Dépendance Backend → PostgreSQL | EVIDENCED |
| RecommendationService | IMPLEMENTED / TESTED |
| Authentification API | RUNTIME-VERIFIED |
| Ressources backend | RUNTIME-VERIFIED |
| Probes backend | RUNTIME-VERIFIED |
| Prometheus → Backend | RUNTIME-VERIFIED |
| Métriques recommendation | RUNTIME-VERIFIED |
| P95 ~0,2425 s | HISTORICAL-MEASUREMENT |
| PRA PostgreSQL → MinIO → Restore | RUNTIME-VERIFIED |
| `pg_restore` 6 s | MEASURED |
| RTO complet | NOT EVIDENCED |
| GitOps backend | RUNTIME-VERIFIED |
| GitOps PRA | RUNTIME-VERIFIED |
| NGINX Ingress Real Estate | IMMEDIATE-TARGET |
| ML/GPU production matching | NOT APPLICABLE — experimental only |
| Diagramme composant final | TO BE GENERATED |

---

# 49. Conclusion

L'analyse des composants montre une architecture volontairement structurée en plans fonctionnels distincts.

Le chemin synchrone métier reste simple et limite les dépendances obligatoires.

PostgreSQL constitue actuellement le composant technique le plus critique car plusieurs fonctions applicatives et Data en dépendent.

Le backend est observable, limité en ressources et supervisé par Kubernetes, mais son déploiement mono-replica constitue une limite de disponibilité.

Le moteur de recommandation reste déterministe, explicable et indépendant de l'infrastructure GPU expérimentale.

L'observabilité permet de mesurer les performances avant de prendre des décisions de scaling.

Le PRA fournit une copie externe et une restauration PostgreSQL réellement testée, ce qui réduit le risque associé au stockage `local-path`.

L'évolution immédiate consiste à introduire un **Ingress NGINX Real Estate** afin d'offrir un point d'entrée HTTP(S) contrôlé tout en conservant le backend sous forme de Service `ClusterIP`.

Les évolutions de scalabilité — plusieurs replicas backend, réplication PostgreSQL, séparation physique OLTP/OLAP, moteur analytique spécialisé ou intégration ML en production — restent conditionnées à des mesures démontrant leur nécessité.

---

**BC01-C4 — Composants, interactions et dépendances : EVIDENCED**

**Analyse des performances : EVIDENCED avec distinction entre mesures actuelles, historiques et non mesurées**

**Ingress Real Estate : IMMEDIATE-TARGET — validation runtime après déploiement**

**Prochaine preuve BC01 : C5 — Matrice de décision d'architecture**