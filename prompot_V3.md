# MASTER MIGRATION PROMPT — FIL ROUGE REAL ESTATE DATA & IA

> **Usage:** copier/importer ce document dans un nouveau chat ChatGPT du même projet.  
> Il constitue le contexte opérationnel de reprise. Le nouveau chat doit s'appuyer dessus avant de proposer toute modification.
>
> **État consolidé : 26 août 2026**

---

# 0. INSTRUCTION AU NOUVEAU CHAT

Tu reprends un projet déjà largement construit et déployé.

**Ne repars pas de zéro. Ne redessine pas l'architecture sans raison. Ne suppose pas que le projet tourne localement sur Windows.**

Avant toute réponse technique :

1. considère les informations de ce document comme l'état de référence du projet ;
2. conserve les choix d'architecture déjà validés ;
3. travaille à partir de l'existant ;
4. distingue clairement :
   - dépôt applicatif `chasse_immobiliere`,
   - dépôt GitOps `lab-gitops`,
   - cluster Kubernetes,
   - Airflow,
   - PostgreSQL,
   - dbt,
   - OpenMetadata,
   - Governance-as-Code ;
5. ne demande pas à l'utilisateur de réexpliquer l'infrastructure décrite ici ;
6. ne propose pas `kubectl` depuis Windows : l'utilisateur **n'a pas Kubernetes sur son poste Windows** ;
7. les déploiements doivent passer par **GitLab CI → lab-gitops → Argo CD → Kubernetes**, sauf commandes ponctuelles de diagnostic exécutées directement sur le control-plane ;
8. avancer **étape par étape** ;
9. après avoir donné une commande de validation, attendre son résultat avant de passer à l'étape suivante ;
10. lorsqu'un fichier doit être modifié, fournir de préférence le **fichier complet**, copy/paste ready, surtout pour YAML, Python, SQL, Dockerfile et CI ;
11. ne pas casser ce qui fonctionne déjà pour « simplifier » ;
12. documenter les décisions importantes au fur et à mesure.

---

# 1. IDENTITÉ DU PROJET

Projet de formation Diginamic :

```text
Fil Rouge EISI Data & IA
```

Dépôt principal local Windows :

```text
C:\Users\bastr\Desktop\DIGINAMIC\chasse_immobiliere
```

Dépôt starter de référence :

```text
DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack
```

Le projet vise une plateforme **Enterprise Real Estate Intelligence** permettant de couvrir les besoins Data/IA du Fil Rouge, notamment les blocs de compétences visés, avec une vraie architecture déployée dans le homelab plutôt qu'une simple démonstration locale Docker.

Le domaine fonctionnel est la **chasse immobilière**.

---

# 2. MODE DE TRAVAIL IMPÉRATIF

L'utilisateur travaille principalement avec :

```text
Windows 11
VS Code
PowerShell
Git
GitLab
```

Il ne possède **pas `kubectl` sur Windows**.

Les commandes Kubernetes de diagnostic sont exécutées en SSH sur :

```text
root@k8s-cp-01
```

Le workflow normal est :

```text
Windows
   ↓
modification repository
   ↓
git push
   ↓
GitLab CI
   ↓
publication lab-gitops
   ↓
Argo CD
   ↓
Kubernetes
```

Ne pas proposer une architecture où Windows applique directement les manifests Kubernetes.

L'utilisateur préfère :

- une seule étape à la fois ;
- commandes exactes ;
- scripts complets ;
- fichiers complets plutôt que fragments ambigus ;
- validation de la sortie avant l'étape suivante ;
- documentation Markdown ;
- compréhension du **pourquoi**, pas seulement du comment.

---

# 3. INFRASTRUCTURE HOMELAB

La plateforme est hébergée sur un homelab basé sur Proxmox.

Kubernetes :

```text
kubeadm
Kubernetes v1.30.14
Flannel CNI
NGINX Ingress
cert-manager
```

Control planes :

```text
k8s-cp-01
k8s-cp-02
k8s-cp-03
```

Workers principaux :

```text
k8s-wk-01
k8s-wk-02
k8s-wk-03
```

Workers supplémentaires :

```text
k8s-wk-04
k8s-wk-05
k8s-wk-06
```

StorageClass par défaut :

```text
local-path
```

DNS interne :

```text
*.lab.local
```

Namespaces importants :

```text
argocd
airflow
mlflow
mlops
monitoring
openmetadata
real-estate
retail-data
zammad
```

---

# 4. PLATEFORME DATA EXISTANTE

Le homelab héberge déjà une plateforme Data/MLOps utilisée comme infrastructure d'exécution.

## Argo CD

GitOps central.

Le dépôt GitOps est :

```text
https://gitlab.local/root/lab-gitops.git
```

Argo CD fonctionne en mode :

```text
automated
prune
selfHeal
```

## GitLab

GitLab CE interne :

```text
gitlab.local
```

Le registre d'images est utilisé pour les images applicatives.

Des runners existent avec notamment :

```text
docker
shell
```

Le runner Docker construit les images.

Le runner shell publie vers `lab-gitops` et peut utiliser `kubectl` pour certaines opérations nécessaires au pipeline.

## Airflow

Déployé par Helm.

Version Helm historiquement utilisée :

```text
1.15.0
```

Executor :

```text
KubernetesExecutor
```

Ingress :

```text
airflow.lab.local
```

Airflow exécute les pipelines Data du projet via Kubernetes.

## OpenMetadata

Version déployée :

```text
1.12.11
```

Services principaux :

```text
8585
8586
```

Backend :

```text
MySQL
OpenSearch
```

OpenMetadata est déjà fonctionnel pour :

- PostgreSQL ingestion ;
- dbt ingestion ;
- profiler ;
- Data Quality ;
- glossary ;
- ownership ;
- tags ;
- domains ;
- privacy ;
- Data Products ;
- Governance-as-Code.

## Observabilité existante

La plateforme possède notamment :

```text
kube-prometheus-stack
Loki
Promtail
Tempo
OpenTelemetry Collector
Pushgateway
```

---

# 5. ARCHITECTURE DU PROJET REAL ESTATE

Architecture logique :

```text
Sources / fixtures / générateur
            │
            ▼
          RAW
            │
            ▼
        STAGING
            │
            ▼
     REAL_ESTATE OLTP
            │
            ▼
        WAREHOUSE
            │
            ▼
           dbt
            │
            ▼
        ANALYTICS
            │
            ├──────────────► usages BI
            │
            └──────────────► futurs usages IA

PostgreSQL ────────────────► OpenMetadata
dbt ───────────────────────► OpenMetadata
Governance-as-Code ────────► OpenMetadata

GitLab CI
   │
   ▼
lab-gitops
   │
   ▼
Argo CD
   │
   ▼
Kubernetes
```

---

# 6. POSTGRESQL REAL ESTATE

Namespace :

```text
real-estate
```

Workload :

```text
real-estate-postgresql
```

État validé :

```text
READY 1/1
Running
```

PVC :

```text
5Gi
local-path
```

Variables utilisées :

```text
POSTGRES_HOST
POSTGRES_USER
POSTGRES_DB
POSTGRES_PORT
POSTGRES_PASSWORD
```

Base :

```text
real_estate
```

Service PostgreSQL accessible depuis le cluster.

---

# 7. SCHÉMAS POSTGRESQL

Schémas constatés :

```text
Fil_Rouge_Depart
analytics
migration_control
public
raw
real_estate
staging
warehouse
```

---

# 8. LEGACY — `Fil_Rouge_Depart`

Schéma historique provenant du starter / ancien modèle.

Tables constatées :

```text
mandats
secteurs
utilisateurs
```

Il est conservé pour démontrer :

- migration ;
- héritage ;
- transformation ;
- traçabilité.

Il ne représente pas le modèle métier cible.

---

# 9. RAW

Tables :

```text
raw.annonces
raw.recherches
```

Les données générées sont associées à des `ingestion_batch`.

Une source a été enregistrée dans le modèle métier :

```text
GENERATEUR_ANNONCES
```

Type :

```text
AUTRE
```

URL logique de provenance :

```text
s3://real-estate/raw/generated/...
```

---

# 10. STAGING

Tables / vues principales :

```text
staging.annonces
staging.recherches
staging.v_annonces_invalides
```

Validation réalisée :

```text
annonces valides = 2000
références distinctes = 2000
matching vers real_estate.bien = 2000
unmatched = 0
```

Anomalies zéro sur :

```text
surface
prix
```

Certaines colonnes optionnelles contiennent naturellement des NULL :

```text
nb_pieces
nb_chambres
dpe
latitude
longitude
```

Cela a été identifié et accepté selon le modèle.

---

# 11. MODÈLE OLTP CIBLE — `real_estate`

Le modèle métier cible comprend notamment :

```text
bareme_commission
bien
chasseur
client
commentaire
demande
demande_version
document
mandat
mandat_secteur
paiement
presentation
secteur
source
visite
utilisateur
piece_jointe
audit_log
```

Le modèle a été construit pour remplacer la logique legacy par un modèle normalisé, exploitable et gouvernable.

---

# 12. MIGRATIONS DATABASE

Répertoire :

```text
database/migrations
```

Migrations importantes :

```text
001_initial_schema.sql
002_migrate_legacy_data.sql
003_warehouse_schema.sql
003_add_visite_audit.sql
```

Le dernier nom est historiquement conservé même si le numéro `003` existe déjà ; ne pas renommer sans analyser les dépendances CI/migration.

`migration_control.schema_version` permet de suivre les migrations appliquées.

Migrations validées :

```text
001 Initial schema
002 Legacy data migration
003 Create analytical warehouse...
```

---

# 13. WAREHOUSE

Schéma :

```text
warehouse
```

Dimensions :

```text
dim_date
dim_source
dim_localisation
dim_bien
dim_chasseur
dim_client
dim_demande_version
dim_secteur
```

Bridge :

```text
bridge_mandat_secteur
```

Facts :

```text
fact_annonce
fact_mandat
fact_paiement
fact_presentation
fact_demande
fact_matching
fact_bien_daily
```

Le warehouse sert aux analyses :

- marché ;
- métier ;
- matching ;
- financier ;
- historique.

---

# 14. DBT / ANALYTICS

dbt est utilisé pour transformer et documenter les données analytiques.

Modèles actuellement validés :

```text
analytics.stg_dim_bien
analytics.stg_fact_annonce
analytics.mart_market_by_city
```

`mart_market_by_city` est un mart de marché par localisation.

dbt documente également des sources OLTP, notamment :

```text
source.real_estate_analytics.real_estate_oltp.client
```

Le `manifest.json` contient les descriptions des colonnes de `client`.

Exemple :

```text
email => Primary customer email address used for business communications.
telephone => Customer telephone number.
ville => Customer city of residence or business attachment.
date_creation => Timestamp when the customer record was created.
statut => Current business status of the customer.
consentement_contact => Indicates whether the customer has consented to being contacted.
```

---

# 15. VALIDATION DBT DANS KUBERNETES

Une exécution dbt dans Kubernetes a validé :

```text
dbt 1.9.0
postgres adapter 1.9.0
```

Modèles :

```text
PASS=3
WARN=0
ERROR=0
SKIP=0
TOTAL=3
```

Tests :

```text
PASS=20
WARN=0
ERROR=0
SKIP=0
TOTAL=20
```

Artefacts générés :

```text
catalog.json
manifest.json
run_results.json
index.html
graph.gpickle
graph_summary.json
semantic_manifest.json
```

Cela permet à OpenMetadata de récupérer :

- documentation ;
- modèles ;
- colonnes ;
- tests ;
- lineage dbt.

---

# 16. AIRFLOW

Airflow est utilisé comme orchestrateur.

Le projet possède notamment un DAG :

```text
real_estate_ingestion
```

Le déploiement Airflow passe par GitLab CI et GitOps, pas par un Airflow local Windows.

Le pipeline utilise l'image Data Pipeline :

```text
$CI_REGISTRY_IMAGE/data-pipeline
```

Le Dockerfile associé :

```text
deploy/docker/Dockerfile.data-pipeline
```

a été enrichi pour disposer notamment de :

```text
psql
git
```

Les pods Airflow accèdent à PostgreSQL via les variables `POSTGRES_*`.

---

# 17. OPENMETADATA — OBJECTIF

OpenMetadata est le catalogue et point central de gouvernance.

Il ne remplace pas PostgreSQL, dbt ou Airflow.

Répartition :

```text
PostgreSQL
    = données et structures physiques

Airflow
    = orchestration

dbt
    = transformations analytiques + tests + documentation + lineage

OpenMetadata
    = catalogue + gouvernance + ownership + qualité + glossaire

Governance-as-Code
    = définition versionnée de la gouvernance OpenMetadata
```

---

# 18. OPENMETADATA — INGESTION POSTGRESQL

Fichiers sources :

```text
deploy/openmetadata/configmap.yaml
deploy/openmetadata/cronjob.yaml
deploy/openmetadata/kustomization.yaml
```

Publication GitOps cible :

```text
workloads/openmetadata/ingestions/real-estate-postgresql
```

Service OpenMetadata :

```text
real-estate-postgresql
```

Exemple de FQN :

```text
real-estate-postgresql.real_estate.real_estate.client
```

---

# 19. OPENMETADATA — DBT

Fichiers :

```text
deploy/openmetadata/dbt/cronjob.yaml
deploy/openmetadata/dbt/kustomization.yaml
```

Publication GitOps :

```text
workloads/openmetadata/ingestions/real-estate-dbt
```

dbt apporte à OpenMetadata :

```text
documentation
tests
lineage
modèles analytiques
relations sources → modèles
```

---

# 20. GOVERNANCE-AS-CODE

Répertoire :

```text
governance/
```

Structure :

```text
governance/
├── Dockerfile
├── README.md
├── requirements.txt
├── scripts/
│   └── main.py
├── docs/
│   └── governance-config.json
├── glossary/
│   └── real_estate_glossary.json
├── ownership/
│   └── real_estate_ownership.json
├── quality/
│   └── real_estate_quality.json
├── tagging/
│   └── real_estate_tags.json
└── data-products/
```

La gouvernance est volontairement stockée dans Git.

**Ne pas revenir à une gouvernance configurée manuellement uniquement dans l'UI OpenMetadata.**

---

# 21. GOVERNANCE ENGINE

Fichier :

```text
governance/scripts/main.py
```

Version actuellement validée :

```text
Governance version: 1.5.0
```

Architecture Python importante :

```text
OpenMetadataClient
    = appels API / helpers techniques

GovernanceEngine
    = orchestration de la gouvernance
```

Cette séparation a été source de bugs pendant le développement. Ne pas déplacer arbitrairement les méthodes entre ces classes.

---

# 22. ÉTAPES GOVERNANCE 1.5.0

Le moteur exécute :

```text
Step 1/9 - Domains
Step 2/9 - Business Glossary
Step 3/9 - Classifications
Step 4/9 - Data Layer governance
Step 5/9 - Ownership
Step 6/9 - Data Quality
Step 7/9 - Glossary Assignments
Step 8/9 - Privacy Assignments
Step 9/9 - Data Products
```

Dernière exécution complète :

```text
Governance-as-Code execution completed successfully
Governance apply completed successfully
```

---

# 23. DOMAINS

Domaine racine / organisation logique :

```text
RealEstateIntelligence
```

Sous-domaine analytique validé :

```text
RealEstateIntelligence.RealEstateAnalytics
```

Description :

```text
Domaine analytique couvrant les modèles warehouse,
les vues dbt, les marts et les indicateurs utilisés
pour l'analyse du marché immobilier et des performances métier.
```

---

# 24. GLOSSAIRE

Le glossaire Real Estate définit le vocabulaire métier et l'associe aux données physiques.

Les assignments ont notamment été vérifiés sur :

```text
analytics.mart_market_by_city
```

pour des concepts tels que :

```text
prix moyen
prix minimum
prix maximum
surface moyenne
prix au m² moyen
```

L'objectif est de relier :

```text
colonne technique
        ↓
concept métier
```

---

# 25. CLASSIFICATIONS

La gouvernance a créé :

```text
5 classifications
23 tags
```

Exemples :

```text
RealEstateDataQuality.DerivedData
RealEstateTechnicalMetadata.LineageMetadata
RealEstateTechnicalMetadata.IngestionMetadata
RealEstateTechnicalMetadata.AuditMetadata
```

Une classification importante :

```text
RealEstateDataLayer
```

sert à distinguer :

```text
Legacy
Raw
Staging
Operational
Warehouse
Analytics
```

---

# 26. OWNERSHIP

Une équipe OpenMetadata importante :

```text
RealEstateAnalytics
```

Display name :

```text
Real Estate Analytics
```

Elle est notamment owner du Data Product analytique.

L'ownership doit rester déclaratif et versionné.

---

# 27. PRIVACY / RGPD

La gouvernance applique des tags au niveau colonne.

Dernière validation idempotente :

```text
27 processed
0 changed
27 already correct
0 missing
```

Exemples de tags :

```text
PersonalData
DirectIdentifier
IndirectIdentifier
FinancialData
RequiresPseudonymisation
AIRestricted
Confidential
Restricted
```

Exemples :

```text
client.nom
client.prenom
client.email
client.telephone
```

sont traités comme identifiants personnels directs et données à protéger.

Budgets :

```text
demande_version.budget_min
demande_version.budget_max
```

sont traités comme données personnelles/financières.

Paiements :

```text
paiement.montant_achat
paiement.montant_honoraires
paiement.montant_chasseur
```

sont classifiés comme données financières/confidentielles.

Cette couche doit être conservée pour les futurs usages IA.

---

# 28. DATA PRODUCT

Data Product validé :

```text
RealEstateMarketIntelligence
```

Display name :

```text
Real Estate Market Intelligence
```

Description :

```text
Produit de données analytique fournissant une vision consolidée
du marché immobilier par localisation. Il expose les volumes
d'annonces, les prix moyens, les prix au mètre carré, les surfaces
moyennes et les périodes de publication afin de supporter les
usages BI, pilotage métier et futurs cas d'usage IA.
```

Domaine :

```text
RealEstateIntelligence.RealEstateAnalytics
```

Owner :

```text
RealEstateAnalytics
```

Lifecycle :

```text
DEVELOPMENT
```

Assets ajoutés :

```text
real-estate-postgresql.real_estate.analytics.mart_market_by_city
real-estate-postgresql.real_estate.analytics.stg_fact_annonce
real-estate-postgresql.real_estate.analytics.stg_dim_bien
real-estate-postgresql.real_estate.warehouse.fact_annonce
real-estate-postgresql.real_estate.warehouse.dim_localisation
real-estate-postgresql.real_estate.warehouse.dim_bien
real-estate-postgresql.real_estate.warehouse.dim_source
```

Résultat final :

```text
Data Product governance completed:
1 products processed,
7 assets added,
0 assets already assigned
```

La relation Data Product ↔ Asset a été confirmée depuis l'API de l'actif.

---

# 29. LINEAGE

Le lineage dbt/OpenMetadata a été validé.

Exemple logique :

```text
warehouse.dim_localisation
            \
             ───► analytics.mart_market_by_city
            /
analytics.stg_fact_annonce
```

Ne pas confondre :

```text
lineage physique PostgreSQL
```

et :

```text
lineage logique dbt
```

dbt est nécessaire pour obtenir la seconde information correctement.

---

# 30. INCIDENTS GOVERNANCE DÉJÀ RÉSOLUS

Ne pas réintroduire ces erreurs.

## Mauvaise classe

Erreur rencontrée :

```text
'GovernanceEngine' object has no attribute 'apply_data_products'
```

Cause : méthode dans la mauvaise classe.

## Data Product `domain`

Erreur :

```text
Unrecognized field "domain"
```

OpenMetadata 1.12.11 attend :

```text
domains
```

## Format `domains`

OpenMetadata attend dans ce payload une liste compatible avec son schéma API, pas un objet arbitraire.

## BulkAssets

L'endpoint :

```text
/v1/dataProducts/<name>/assets/add
```

attend un payload BulkAssets, pas un tableau JSON brut.

## Endpoint Data Product

Pendant les tests, l'ajout d'assets a fonctionné avec le **nom du Data Product** dans le chemin, contrairement à l'UUID qui provoquait un 404 dans ce contexte.

## Méthodes supprimées/dupliquées

Des éditions successives avaient momentanément cassé :

```text
upsert_data_product
add_assets_to_data_product
apply_data_layer_to_table
```

La version finale a été restructurée et fonctionne.

Avant tout changement majeur de `main.py`, valider :

```powershell
python -m py_compile .\governance\scripts\main.py
git diff --check
```

---

# 31. GITLAB CI GLOBAL

Le `.gitlab-ci.yml` utilise les stages :

```text
validate
database
build
deploy
```

et inclut notamment :

```text
.gitlab/ci/database.yml
.gitlab/ci/airflow.yml
.gitlab/ci/data-pipeline-image.yml
.gitlab/ci/warehouse.yml
.gitlab/ci/openmetadata.yml
.gitlab/ci/governance.yml
```

Toujours vérifier les stages réellement présents dans `.gitlab-ci.yml` avant d'ajouter un job.

---

# 32. GOVERNANCE CI

Fichier :

```text
.gitlab/ci/governance.yml
```

Jobs :

```text
governance:validate
governance:build-image
```

`governance:validate` vérifie :

```text
Python syntax
governance-config.json
real_estate_glossary.json
real_estate_ownership.json
real_estate_quality.json
real_estate_tags.json
```

`governance:build-image` construit :

```text
$CI_REGISTRY_IMAGE/real-estate-governance:$CI_COMMIT_SHORT_SHA
$CI_REGISTRY_IMAGE/real-estate-governance:latest
```

et pousse les deux tags.

---

# 33. ÉTAT ACTUEL DE `governance.yml`

Une amélioration vient d'être ajoutée :

```yaml
- echo "GOVERNANCE_IMAGE_TAG=$CI_COMMIT_SHORT_SHA" > governance-image.env

artifacts:
  reports:
    dotenv: governance-image.env
  expire_in: 1 hour
```

But :

```text
governance:build-image
       ↓
GOVERNANCE_IMAGE_TAG=<commit-short-sha>
       ↓
openmetadata:publish-gitops
```

Cette amélioration est **en cours de finalisation**.

---

# 34. OPENMETADATA GITOPS CI

Job :

```text
openmetadata:publish-gitops
```

Fichier :

```text
.gitlab/ci/openmetadata.yml
```

Runner :

```text
shell
```

Il :

1. valide les manifests ;
2. vérifie le Secret GitOps ;
3. lit `GIT_USERNAME` / `GIT_TOKEN` ;
4. clone `lab-gitops` ;
5. copie les manifests PostgreSQL ;
6. copie les manifests dbt ;
7. copie les manifests Governance ;
8. enregistre les bundles dans les `kustomization.yaml` parents ;
9. configure Git ;
10. commit seulement si un diff existe ;
11. push vers `main`.

Secret :

```text
lab-gitops-git-credentials
```

Namespace :

```text
openmetadata
```

---

# 35. STRUCTURE GITOPS OPENMETADATA

Publication :

```text
workloads/openmetadata/ingestions/real-estate-postgresql
workloads/openmetadata/ingestions/real-estate-dbt
workloads/openmetadata-governance/real-estate
```

Application Argo CD de gouvernance :

```text
openmetadata-governance
```

Repo :

```text
https://gitlab.local/root/lab-gitops
```

Target revision :

```text
main
```

Path :

```text
workloads/openmetadata-governance
```

Automatisation :

```text
prune
selfHeal
```

---

# 36. PROBLÈME `:latest` IDENTIFIÉ

Ancien manifest :

```yaml
image: gitlab.local:4567/root/chasse_immobiliere/real-estate-governance:latest
imagePullPolicy: Always
```

Problème :

```text
nouveau commit
    ↓
nouvelle image latest
    ↓
manifest GitOps inchangé
    ↓
pas de nouveau commit lab-gitops
    ↓
Argo CD ne voit aucun changement
```

Cela obligeait à faire manuellement :

```bash
kubectl -n openmetadata delete job real-estate-governance-apply
```

puis forcer une sync Argo.

Ce workflow manuel est en cours de suppression.

---

# 37. NOUVEAU JOB ARGO CD HOOK

Le manifest Governance a été converti en hook.

Fichier :

```text
deploy/openmetadata/governance/governance-apply-job.yaml
```

Concept :

```yaml
annotations:
  argocd.argoproj.io/hook: Sync
  argocd.argoproj.io/hook-delete-policy: BeforeHookCreation,HookSucceeded
```

L'image source doit utiliser :

```text
__GOVERNANCE_IMAGE_TAG__
```

au lieu de `latest`.

Exemple cible :

```yaml
image: gitlab.local:4567/root/chasse_immobiliere/real-estate-governance:__GOVERNANCE_IMAGE_TAG__
```

et :

```yaml
imagePullPolicy: IfNotPresent
```

---

# 38. COMPORTEMENT DU HOOK VALIDÉ

Argo CD a retourné :

```text
NAME                      SYNC     HEALTH
openmetadata-governance   Synced   Healthy
```

Operation state :

```text
Succeeded
successfully synced (all tasks run)
```

Résultat hook :

```text
Job | openmetadata | real-estate-governance-apply
hookPhase=Succeeded
status=Pruned
```

Donc :

```bash
kubectl -n openmetadata logs job/real-estate-governance-apply
```

retourne ensuite éventuellement :

```text
NotFound
```

**C'est normal.**

`HookSucceeded` supprime automatiquement le Job réussi.

Pour diagnostiquer après suppression, utiliser l'état Argo CD.

---

# 39. COMMANDES ARGO CD DE RÉFÉRENCE

État :

```bash
kubectl -n argocd get application openmetadata-governance \
  -o custom-columns=NAME:.metadata.name,SYNC:.status.sync.status,HEALTH:.status.health.status,REVISION:.status.sync.revision
```

Dernière opération :

```bash
kubectl -n argocd get application openmetadata-governance \
  -o jsonpath='{.status.operationState.phase}{"\n"}{.status.operationState.message}{"\n"}'
```

Hooks :

```bash
kubectl -n argocd get application openmetadata-governance \
  -o jsonpath='{range .status.operationState.syncResult.resources[*]}{.kind}{" | "}{.namespace}{" | "}{.name}{" | hookPhase="}{.hookPhase}{" | status="}{.status}{" | "}{.message}{"\n"}{end}'
```

---

# 40. ATTENTION AU PROJET RETAIL

Le cluster possède aussi un ancien projet Retail Governance.

Il existe notamment :

```text
retail-governance-apply
```

dans la même application/zone GitOps.

Ne pas confondre :

```text
retail-governance-apply
```

avec :

```text
real-estate-governance-apply
```

Le projet courant est **Real Estate**.

---

# 41. ÉTAT DE LA GOVERNANCE — VALIDÉ

La gouvernance fonctionnelle est terminée pour son périmètre actuel.

Validation finale :

```text
Governance version: 1.5.0

Step 9/9 - Applying Data Products

Data Product applied:
RealEstateMarketIntelligence

7 Data Product assets assigned

Data Product governance completed:
1 products processed,
7 assets added,
0 assets already assigned

Governance-as-Code execution completed successfully

Governance apply completed successfully
```

Ne pas refaire la Governance depuis zéro.

---

# 42. ÉTAT OPENMETADATA — VALIDÉ

Validé :

```text
PostgreSQL ingestion
dbt metadata
dbt documentation
dbt lineage
profiler
Data Quality
Domains
Glossary
Classifications
Data Layers
Ownership
Privacy
Data Products
```

Le Data Product existe réellement dans OpenMetadata.

---

# 43. DERNIÈRE TÂCHE TECHNIQUE EN COURS

**C'est ici qu'il faut reprendre dans le nouveau chat.**

Nous sommes en train de finaliser l'automatisation :

```text
git push
   ↓
governance:validate
   ↓
governance:build-image
   ↓
image governance:<CI_COMMIT_SHORT_SHA>
   ↓
dotenv GOVERNANCE_IMAGE_TAG
   ↓
openmetadata:publish-gitops
   ↓
remplacement __GOVERNANCE_IMAGE_TAG__
   ↓
commit lab-gitops
   ↓
Argo CD détecte la révision
   ↓
Sync Hook
   ↓
real-estate-governance-apply
   ↓
OpenMetadata
   ↓
HookSucceeded
```

Le but final est de ne plus exécuter :

```text
kubectl delete job
kubectl patch application
```

pour chaque nouvelle version Governance.

---

# 44. PREMIÈRE ACTION À FAIRE DANS LE NOUVEAU CHAT

Ne commence pas un autre chantier avant de terminer ce point.

Le fichier `governance.yml` vient d'être modifié pour produire :

```text
governance-image.env
```

avec :

```text
GOVERNANCE_IMAGE_TAG=$CI_COMMIT_SHORT_SHA
```

La prochaine étape est de modifier :

```text
.gitlab/ci/openmetadata.yml
```

afin que `openmetadata:publish-gitops` :

1. récupère `GOVERNANCE_IMAGE_TAG` quand `governance:build-image` a réellement tourné ;
2. ne référence jamais un SHA d'image inexistant ;
3. copie `governance-apply-job.yaml` ;
4. remplace :

```text
__GOVERNANCE_IMAGE_TAG__
```

par le SHA construit ;
5. crée un vrai diff dans `lab-gitops` ;
6. pousse ce diff ;
7. laisse Argo CD exécuter automatiquement le hook.

**Attention :** `governance:build-image` est optionnel dans certains chemins du pipeline. Ne pas injecter aveuglément `$CI_COMMIT_SHORT_SHA` lorsqu'aucune image Governance n'a été construite.

Il faut concevoir correctement cette condition.

---

# 45. VALIDATION ATTENDUE APRÈS CETTE MODIFICATION

Le test de bout en bout devra être :

```text
1. modification governance
2. git push
3. governance:validate = PASS
4. governance:build-image = PASS
5. image :<SHA> existe
6. openmetadata:publish-gitops = PASS
7. lab-gitops contient ce SHA
8. Argo CD = Synced / Healthy
9. hook real-estate-governance-apply = Succeeded
10. OpenMetadata contient l'état attendu
```

Aucune suppression manuelle du Job.

Aucun patch manuel de l'Application.

---

# 46. DOCUMENTATION EXISTANTE À CONSULTER

Le projet contient déjà de nombreux documents. Ne pas les ignorer.

Documents structurants disponibles :

```text
00-project-constitution.md
Readme.md
README(1).md
architecture-playbook(1).md
prompt.md
NOTE-DE-CADRAGE.md
CAHIER-DES-CHARGES-TECHNIQUE.md
MCD-MERISE.md
FICHE-COURS-OLTP-OLAP.md
OLTP.md
OLAP.md
GLOSSAIRE-METIER.md
RACI.md
MATRICE-DECISION.md
JOURNAL-DE-DECISIONS.md
MODELE-SWOT.md
PLAN-DE-TESTS.md
REGISTRE-RGPD.md
SOUVERAINETE-SECURITE-IA.md
NOTE-ECO-CONCEPTION.md
PCA-PRA-MIGRATION.md
GRILLE-EVALUATION.md
TRACABILITE-COMPETENCES.md
TRAME-SOUTENANCE.md
ORGANISATION-DEPOT.md
```

Une documentation monolithe spécifique à la gouvernance/OpenMetadata vient également d'être produite :

```text
DOCUMENTATION-MONOLITHE-GOUVERNANCE-OPENMETADATA.md
```

Lorsqu'une décision doit être comparée au référentiel Diginamic, utiliser ces documents comme source de vérité avant d'inventer une nouvelle exigence.

---

# 47. ORGANISATION APPROXIMATIVE DU REPOSITORY

Éléments importants :

```text
chasse_immobiliere/
│
├── .gitlab-ci.yml
│
├── .gitlab/
│   └── ci/
│       ├── airflow.yml
│       ├── database.yml
│       ├── data-pipeline-image.yml
│       ├── warehouse.yml
│       ├── openmetadata.yml
│       └── governance.yml
│
├── database/
│   ├── legacy/
│   ├── migrations/
│   ├── olap/
│   ├── oltp/
│   └── tests/
│
├── dbt/
│   └── ...
│
├── deploy/
│   ├── docker/
│   │   └── Dockerfile.data-pipeline
│   └── openmetadata/
│       ├── configmap.yaml
│       ├── cronjob.yaml
│       ├── kustomization.yaml
│       ├── dbt/
│       │   ├── cronjob.yaml
│       │   └── kustomization.yaml
│       └── governance/
│           ├── governance-apply-job.yaml
│           └── kustomization.yaml
│
├── governance/
│   ├── Dockerfile
│   ├── README.md
│   ├── requirements.txt
│   ├── scripts/
│   ├── docs/
│   ├── glossary/
│   ├── ownership/
│   ├── quality/
│   ├── tagging/
│   └── data-products/
│
├── outils/
│   └── generer_annonces.py
│
└── docs/
    └── ...
```

Avant de supposer qu'un fichier n'existe pas, demander une commande PowerShell ciblée ou consulter les fichiers disponibles.

---

# 48. PRINCIPES D'ARCHITECTURE À CONSERVER

## Git comme source de vérité

```text
code
configuration
governance
infrastructure déclarative
documentation
```

doivent être versionnés.

## CI pour produire

GitLab CI :

```text
validate
test
build
publish
```

## GitOps pour déployer

```text
application repo
    ↓
lab-gitops
    ↓
Argo CD
    ↓
cluster
```

## Airflow pour orchestrer les pipelines

Ne pas remplacer Airflow par des scripts manuels cron sans justification.

## dbt pour la transformation analytique

Ne pas déplacer les transformations analytiques dans OpenMetadata.

## OpenMetadata pour gouverner

Ne pas utiliser OpenMetadata comme moteur ETL.

## Kubernetes comme runtime

Les jobs de pipeline et de gouvernance doivent s'exécuter dans l'environnement cluster lorsqu'ils font partie du fonctionnement de la plateforme.

---

# 49. OBJECTIFS PÉDAGOGIQUES DU FIL ROUGE

Le projet doit rester démontrable devant un jury.

Chaque composant doit pouvoir être expliqué selon :

```text
Besoin
  ↓
Choix
  ↓
Implémentation
  ↓
Test
  ↓
Preuve
  ↓
Compétence couverte
```

Il faut éviter les composants « décoratifs ».

Tout ce qui est ajouté doit avoir :

- une utilité métier ;
- une utilité technique ;
- un lien avec le référentiel ;
- une preuve d'exécution.

Le projet doit couvrir au maximum le référentiel prévu, notamment les compétences Data et IA ciblées, sans inventer artificiellement des éléments uniquement pour cocher des cases.

---

# 50. LOGIQUE MÉTIER

Le cœur fonctionnel est :

```text
Client
   ↓
Mandat
   ↓
Demande
   ↓
Version de demande
   ↓
Critères
   ↓
Biens
   ↓
Matching
   ↓
Présentation / Visite
   ↓
Paiement / Commission
```

Les annonces immobilières alimentent l'analyse du marché et le matching.

Le warehouse et les marts doivent découler de cette logique métier, pas être des tables analytiques arbitraires.

---

# 51. FUTURS USAGES IA

Le projet doit progressivement aller vers les parties IA du Fil Rouge.

La gouvernance a volontairement préparé ce terrain avec :

```text
AIRestricted
RequiresPseudonymisation
PersonalData
FinancialData
```

Principe :

```text
donnée
  ↓
cataloguée
  ↓
qualifiée
  ↓
classifiée
  ↓
contrôlée
  ↓
autorisée pour usage IA
  ↓
feature / training / inference
```

Ne pas entraîner un modèle sur des données sensibles simplement parce qu'elles existent dans PostgreSQL.

Les futurs choix IA devront être justifiés par un vrai cas métier.

---

# 52. SÉCURITÉ

Ne jamais committer :

```text
JWT
passwords
GitLab tokens
database passwords
registry passwords
```

Les secrets passent par Kubernetes/GitLab CI.

OpenMetadata utilise :

```text
om-admin-token
```

avec clé :

```text
jwtToken
```

Le Job Governance reçoit :

```text
OM_URL=http://openmetadata:8585/api
OM_JWT_TOKEN=<secret>
```

Registry pull secret :

```text
gitlab-registry-auth
```

---

# 53. QUALITÉ ET VALIDATION

Toujours valider avant déploiement.

Python :

```powershell
python -m py_compile .\governance\scripts\main.py
```

JSON :

```powershell
python -m json.tool <file> > $null
```

Git whitespace :

```powershell
git diff --check
```

Repository :

```powershell
git status --short
```

Pour SQL/dbt/Kubernetes, utiliser les validations adaptées déjà intégrées au pipeline plutôt que d'inventer des validations locales indisponibles.

---

# 54. NE PAS CONFONDRE LES TYPES DE DÉPLOIEMENT

Trois concepts :

## Source manifests

Dans :

```text
chasse_immobiliere/deploy/...
```

## GitOps manifests

Dans :

```text
lab-gitops/workloads/...
```

## Resources runtime

Dans :

```text
Kubernetes API
```

Le bon flux est :

```text
source manifest
      ↓ CI
GitOps manifest
      ↓ Argo
Kubernetes resource
```

Ne pas modifier directement le runtime pour faire une modification permanente.

---

# 55. POURQUOI OPENMETADATA ET GOVERNANCE SONT SÉPARÉS

`deploy/openmetadata` décrit **comment exécuter les ingestions et Jobs**.

`governance/` décrit **ce que la gouvernance doit être**.

Exemple :

```text
deploy/openmetadata/governance/governance-apply-job.yaml
```

dit :

> lance cette image dans Kubernetes.

Alors que :

```text
governance/docs/governance-config.json
governance/tagging/...
governance/ownership/...
```

disent :

> voici les règles de gouvernance à appliquer.

Ne pas fusionner ces responsabilités.

---

# 56. POURQUOI UN DATA PRODUCT

Le Data Product ne sert pas à remplacer les tables.

Il fournit une vue métier gouvernée regroupant des assets utiles à un usage.

Ici :

```text
RealEstateMarketIntelligence
```

regroupe les assets nécessaires à l'intelligence marché.

C'est plus compréhensible pour un consommateur que de lui demander de découvrir lui-même quelles tables warehouse/dbt sont pertinentes.

---

# 57. POURQUOI LE TAG IMAGE SHA

Ne pas revenir définitivement à `:latest`.

Avec :

```text
governance:<SHA>
```

on obtient :

```text
code Git précis
      ↕
image précise
      ↕
manifest GitOps précis
      ↕
déploiement précis
```

Cela améliore :

- reproductibilité ;
- audit ;
- rollback ;
- traçabilité ;
- détection des changements par Argo CD.

`latest` peut éventuellement rester poussé pour commodité, mais le manifest GitOps doit référencer un tag immutable.

---

# 58. POURQUOI ARGO CD HOOK

Governance est une opération d'application, pas un service long-running.

Un Job est donc approprié.

Le hook permet :

```text
nouvelle révision GitOps
       ↓
nouvelle opération
       ↓
exécution governance
       ↓
succès
       ↓
cleanup
```

Il évite de conserver indéfiniment des Jobs `Completed` et supprime le besoin de `kubectl delete job` avant chaque exécution.

---

# 59. CRITÈRE DE FIN DE LA PARTIE GOVERNANCE/GITOPS

Cette partie pourra être considérée complètement terminée lorsque le test suivant réussira :

```text
modifier governance
git commit
git push
```

puis automatiquement :

```text
GitLab validate PASS
GitLab image build PASS
image SHA pushed
GitOps publication PASS
lab-gitops updated
Argo CD sync PASS
governance hook PASS
OpenMetadata updated
```

sans intervention Kubernetes manuelle.

---

# 60. APRÈS LA FINALISATION GITOPS

Une fois le raccord SHA terminé et validé, **ne pas continuer à enrichir la gouvernance sans besoin**.

Revenir au plan global du Fil Rouge.

Avant de choisir le prochain chantier :

1. relire les documents de cadrage ;
2. comparer l'état implémenté au référentiel ;
3. identifier les compétences/deliverables encore réellement manquants ;
4. choisir la prochaine brique ayant la meilleure valeur pédagogique et métier ;
5. continuer étape par étape.

Les futurs domaines possibles comprennent notamment :

```text
matching
IA / ML
industrialisation ML
observabilité
sécurité
PCA/PRA
documentation finale
preuves de tests
soutenance
traçabilité des compétences
```

mais **ne pas supposer automatiquement lequel est le prochain** : faire d'abord le gap analysis à partir des documents du projet.

---

# 61. RÈGLE POUR LES DOCUMENTS DU PROJET

L'utilisateur veut une documentation sérieuse et cohérente.

Lorsqu'une partie est terminée :

```text
implémenter
    ↓
tester
    ↓
valider
    ↓
documenter
```

Ne pas documenter comme « terminé » un composant qui n'a pas été exécuté et vérifié.

Les preuves de commandes, résultats CI, tests et états Argo/OpenMetadata sont importantes pour la soutenance.

---

# 62. RÉSUMÉ DE REPRISE EN 30 SECONDES

Si tu dois comprendre le projet très rapidement :

```text
Le projet est une plateforme Data/IA immobilière réellement
déployée sur un cluster Kubernetes homelab.

Windows sert au développement.
GitLab CI construit et valide.
lab-gitops contient l'état de déploiement.
Argo CD déploie Kubernetes.
Airflow orchestre.
PostgreSQL contient legacy/raw/staging/OLTP/warehouse/analytics.
dbt construit/documente analytics et apporte le lineage.
OpenMetadata catalogue et gouverne.
Governance-as-Code v1.5.0 applique 9 étapes de gouvernance.
Le Data Product RealEstateMarketIntelligence fonctionne.
Le hook Argo CD Governance fonctionne.

Le travail en cours consiste UNIQUEMENT à terminer la propagation
du tag immutable de l'image Governance depuis GitLab CI vers
le manifest publié dans lab-gitops.

Après validation de ce flux entièrement automatique,
il faudra revenir au référentiel du Fil Rouge et choisir
le prochain chantier manquant.
```

---

# 63. PREMIER MESSAGE ATTENDU DU NOUVEAU CHAT

Après lecture de ce document, ne réponds pas par une longue réexplication du projet.

Commence par confirmer brièvement que le contexte est compris, puis reprends **exactement au point suivant** :

```text
Finaliser openmetadata:publish-gitops pour consommer
GOVERNANCE_IMAGE_TAG et remplacer __GOVERNANCE_IMAGE_TAG__
uniquement lorsqu'une nouvelle image Governance a été construite.
```

Demande ou utilise le contenu actuel de :

```text
.gitlab/ci/openmetadata.yml
```

s'il n'est pas déjà disponible dans le contexte du nouveau chat.

Ensuite travaille **une étape à la fois** et attends la sortie de validation avant de continuer.

---

# FIN DU MASTER MIGRATION PROMPT

**État de référence : 26 août 2026**

Le projet ne doit pas être reconstruit depuis zéro.  
La prochaine conversation doit reprendre directement à la finalisation du workflow Governance GitOps immutable, puis poursuivre le Fil Rouge à partir d'un gap analysis documenté.
