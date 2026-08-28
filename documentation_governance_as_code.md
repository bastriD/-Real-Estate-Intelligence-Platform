# Documentation monolithe — Gouvernance, OpenMetadata, dbt et déploiement GitOps

**Projet :** Enterprise Real Estate Intelligence Platform / `chasse_immobiliere`  
**Date de consolidation :** 26 août 2026  
**Périmètre de ce document :** état réellement implémenté et validé de la gouvernance des données, de l'intégration OpenMetadata/dbt et de son déploiement Kubernetes/GitLab CI/Argo CD.

---

# 1. Objectif du document

Ce document consolide en un seul fichier le travail réalisé autour de la gouvernance du projet immobilier. Il explique :

- ce qui a été construit ;
- pourquoi ces choix ont été faits ;
- comment les composants sont reliés ;
- comment les métadonnées arrivent dans OpenMetadata ;
- comment la gouvernance est appliquée en tant que code ;
- comment dbt enrichit le catalogue ;
- comment GitLab CI, le registre Docker, le dépôt `lab-gitops`, Argo CD et Kubernetes participent au déploiement ;
- quelles validations ont été réalisées ;
- quels problèmes ont été rencontrés et comment ils ont été corrigés ;
- quel est l'état final au 26/08/2026 ;
- quelle amélioration CI/GitOps reste à finaliser.

L'objectif est qu'un nouveau lecteur puisse comprendre le système sans devoir reconstruire l'historique de la conversation.

---

# 2. Contexte général

Le projet `chasse_immobiliere` met en œuvre une plateforme de données immobilières avec plusieurs couches :

1. une base PostgreSQL opérationnelle ;
2. des zones `raw` et `staging` pour l'ingestion ;
3. un entrepôt analytique `warehouse` ;
4. une couche `analytics` construite notamment avec dbt ;
5. OpenMetadata pour le catalogue, la gouvernance, la qualité et la traçabilité ;
6. une gouvernance déclarative stockée dans Git ;
7. GitLab CI pour valider et construire les artefacts ;
8. un registre GitLab pour les images ;
9. un dépôt GitOps séparé (`lab-gitops`) ;
10. Argo CD pour synchroniser Kubernetes.

Le principe retenu est de ne pas administrer la gouvernance manuellement dans l'interface OpenMetadata. Git constitue la source de vérité et le code de gouvernance doit pouvoir être rejoué de manière idempotente.

---

# 3. Architecture logique

```text
                    ┌─────────────────────────────┐
                    │      chasse_immobiliere     │
                    │          GitLab             │
                    └──────────────┬──────────────┘
                                   │ git push
                                   ▼
                    ┌─────────────────────────────┐
                    │          GitLab CI          │
                    │ validate / build / deploy   │
                    └───────┬───────────┬─────────┘
                            │           │
                  build image           │ publication manifests
                            │           │
                            ▼           ▼
                ┌────────────────┐   ┌──────────────────────┐
                │ GitLab Registry│   │      lab-gitops      │
                │ governance:SHA │   │ workloads/...        │
                └───────┬────────┘   └──────────┬───────────┘
                        │                       │
                        │                       ▼
                        │              ┌─────────────────────┐
                        │              │       Argo CD       │
                        │              └──────────┬──────────┘
                        │                         │ sync
                        ▼                         ▼
              ┌─────────────────────────────────────────────┐
              │                  Kubernetes                 │
              │ namespaces real-estate / openmetadata      │
              └───────────┬─────────────────────┬───────────┘
                          │                     │
                          ▼                     ▼
                ┌─────────────────┐   ┌──────────────────────┐
                │   PostgreSQL    │   │ Governance Job / dbt │
                │ real_estate DB  │   │ ingestion jobs       │
                └────────┬────────┘   └──────────┬───────────┘
                         │                       │
                         └──────────┬────────────┘
                                    ▼
                          ┌───────────────────┐
                          │   OpenMetadata    │
                          │ catalog/governance│
                          └───────────────────┘
```

---

# 4. Organisation des données

La base PostgreSQL contient plusieurs schémas ayant des responsabilités différentes.

## 4.1 `Fil_Rouge_Depart`

Schéma historique/legacy provenant du jeu de données initial.

Tables constatées :

- `mandats`
- `secteurs`
- `utilisateurs`

Cette couche est conservée pour la traçabilité de la migration mais ne représente pas le modèle cible.

## 4.2 `raw`

Zone d'atterrissage des données ingérées.

Exemples :

- `raw.annonces`
- `raw.recherches`

Les données sont conservées au plus près de leur forme d'entrée.

## 4.3 `staging`

Zone de préparation et de contrôle.

Exemples :

- `staging.annonces`
- `staging.recherches`
- `staging.v_annonces_invalides`

Cette couche permet de valider et nettoyer les données avant leur utilisation opérationnelle ou analytique.

## 4.4 `real_estate`

Modèle OLTP métier cible.

Principales entités :

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

Cette couche porte les processus opérationnels de la chasse immobilière.

## 4.5 `warehouse`

Entrepôt dimensionnel destiné à l'analyse.

Dimensions notamment créées :

- `dim_date`
- `dim_source`
- `dim_localisation`
- `dim_bien`
- `dim_chasseur`
- `dim_client`
- `dim_demande_version`
- `dim_secteur`

Tables de faits / pont :

- `bridge_mandat_secteur`
- `fact_annonce`
- `fact_mandat`
- `fact_paiement`
- `fact_presentation`
- `fact_demande`
- `fact_matching`
- `fact_bien_daily`

## 4.6 `analytics`

Couche de consommation analytique.

dbt a notamment créé et validé :

- `analytics.stg_dim_bien`
- `analytics.stg_fact_annonce`
- `analytics.mart_market_by_city`

Le mart `mart_market_by_city` fournit une vue consolidée du marché par localisation.

---

# 5. Pourquoi OLTP, Warehouse et Analytics sont séparés

Le modèle OLTP et le modèle analytique répondent à des besoins différents.

L'OLTP optimise les transactions métier et l'intégrité des processus : clients, mandats, demandes, biens, présentations, paiements, etc.

Le warehouse optimise l'analyse historique et multidimensionnelle. Les clés de substitution, dimensions et faits permettent de découpler les analyses du modèle transactionnel.

La couche `analytics` fournit des modèles directement exploitables par les usages BI, les indicateurs métier et, à terme, certains cas d'usage IA.

Cette séparation évite d'utiliser directement les tables opérationnelles comme couche décisionnelle et facilite la gouvernance des usages.

---

# 6. dbt

## 6.1 Rôle

dbt intervient entre le warehouse PostgreSQL et les modèles analytiques. Il apporte :

- transformation SQL versionnée ;
- documentation des modèles ;
- documentation des colonnes ;
- tests de qualité ;
- génération du `manifest.json` ;
- génération du `catalog.json` ;
- traçabilité des dépendances ;
- enrichissement d'OpenMetadata.

## 6.2 Sources dbt

Le projet contient une source `warehouse` décrivant les objets analytiques PostgreSQL.

Il contient également une source OLTP `real_estate_oltp` utilisée pour documenter les tables opérationnelles dans les artefacts dbt.

Un contrôle du `manifest.json` a confirmé par exemple :

```text
source.real_estate_analytics.real_estate_oltp.client
DATABASE: real_estate
SCHEMA: real_estate
RELATION_NAME: "real_estate"."real_estate"."client"
```

avec les descriptions des colonnes :

- `id_client`
- `nom`
- `prenom`
- `email`
- `telephone`
- `ville`
- `date_creation`
- `statut`
- `consentement_contact`

## 6.3 Exécution dbt validée dans Kubernetes

Un Job Kubernetes de génération des artefacts a exécuté :

```text
dbt 1.9.0
postgres adapter 1.9.0
```

Résultat des modèles :

```text
PASS=3
WARN=0
ERROR=0
SKIP=0
TOTAL=3
```

Résultat des tests :

```text
PASS=20
WARN=0
ERROR=0
SKIP=0
TOTAL=20
```

Artefacts générés :

- `catalog.json`
- `manifest.json`
- `run_results.json`
- `index.html`
- `graph.gpickle`
- `graph_summary.json`
- `semantic_manifest.json`

Cela confirme que la documentation et les tests dbt sont produits directement dans l'environnement Kubernetes, sans dépendre de Python/PyYAML installé sur le poste Windows.

---

# 7. OpenMetadata

OpenMetadata constitue le catalogue central de la plateforme.

Il reçoit plusieurs catégories de métadonnées :

```text
PostgreSQL ───────────────► métadonnées techniques
dbt ──────────────────────► modèles + descriptions + lineage
Governance-as-Code ───────► domaines + ownership + tags + qualité + privacy
```

Le service PostgreSQL utilisé dans OpenMetadata est :

```text
real-estate-postgresql
```

Les FQN observés suivent par exemple :

```text
real-estate-postgresql.real_estate.real_estate.client
real-estate-postgresql.real_estate.warehouse.fact_annonce
real-estate-postgresql.real_estate.analytics.mart_market_by_city
```

---

# 8. Gouvernance-as-Code

## 8.1 Principe

La gouvernance est stockée dans le dépôt `chasse_immobiliere`.

Structure principale :

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
    └── ...
```

Le moteur Python lit les fichiers déclaratifs et utilise l'API OpenMetadata.

Les secrets ne sont pas intégrés au code. Le token OpenMetadata est injecté depuis Kubernetes.

---

# 9. Pipeline de gouvernance validé

La version validée est :

```text
Governance version: 1.5.0
```

Le moteur comporte neuf étapes :

```text
1/9 Domains
2/9 Business Glossary
3/9 Classifications
4/9 Data Layer governance
5/9 Ownership
6/9 Data Quality
7/9 Glossary Assignments
8/9 Privacy Assignments
9/9 Data Products
```

L'exécution finale s'est terminée par :

```text
Governance-as-Code execution completed successfully
Governance apply completed successfully
```

---

# 10. Domaines

La gouvernance organise les actifs dans une structure de domaines.

Le domaine analytique validé est :

```text
RealEstateIntelligence.RealEstateAnalytics
```

Description :

> Domaine analytique couvrant les modèles warehouse, les vues dbt, les marts et les indicateurs utilisés pour l'analyse du marché immobilier et des performances métier.

Cette organisation distingue la responsabilité métier de la simple organisation physique des tables.

---

# 11. Glossaire métier

Un glossaire Real Estate est géré par le code de gouvernance.

Il permet de rattacher les colonnes techniques à des concepts métier compréhensibles par les utilisateurs non techniques.

Sur `analytics.mart_market_by_city`, les associations ont notamment été confirmées pour :

- prix moyen ;
- prix minimum ;
- prix maximum ;
- surface moyenne ;
- prix au m² moyen.

Le catalogue devient ainsi un point de jonction entre modèle physique et vocabulaire métier.

---

# 12. Classifications et Data Layers

La gouvernance crée plusieurs classifications.

Les logs ont notamment confirmé :

```text
RealEstateDataQuality.DerivedData
RealEstateTechnicalMetadata.LineageMetadata
RealEstateTechnicalMetadata.IngestionMetadata
RealEstateTechnicalMetadata.AuditMetadata
```

Au total, l'étape de classification a indiqué :

```text
5 classifications
23 tags
```

Une classification spécifique `RealEstateDataLayer` permet également d'identifier les couches telles que :

- Legacy ;
- Raw ;
- Staging ;
- Operational ;
- Warehouse ;
- Analytics.

Le moteur garantit qu'une table ne conserve pas plusieurs tags contradictoires de couche.

---

# 13. Ownership

Des équipes OpenMetadata portent la responsabilité des actifs.

Pour le Data Product analytique, l'équipe validée est :

```text
RealEstateAnalytics
```

avec le display name :

```text
Real Estate Analytics
```

L'ownership est géré par la gouvernance et non laissé à une configuration manuelle isolée dans l'interface.

---

# 14. Data Quality

La qualité est intégrée à plusieurs niveaux :

```text
SQL / migrations
        ↓
tests de données
        ↓
dbt tests
        ↓
OpenMetadata Data Quality
        ↓
Governance-as-Code
```

Les tests dbt exécutés dans Kubernetes ont donné :

```text
20 / 20 PASS
```

Les contrôles portent notamment sur :

- `not_null` ;
- `unique` ;
- cohérence des clés ;
- présence des attributs analytiques nécessaires.

Cette approche permet de considérer la qualité comme un composant du pipeline et non comme une vérification manuelle ponctuelle.

---

# 15. Gouvernance RGPD / Privacy

Une étape dédiée applique les classifications de confidentialité au niveau colonne.

La validation finale a traité :

```text
27 colonnes
```

et une réexécution idempotente a donné :

```text
27 processed
0 changed
27 already correct
0 missing
```

Cela démontre que le moteur ne réapplique pas inutilement des modifications déjà conformes.

## 15.1 Données client

Exemples :

```text
client.id_client
  PersonalData
  IndirectIdentifier
  RequiresPseudonymisation
  AIRestricted
  Confidential

client.nom
client.prenom
client.email
client.telephone
  PersonalData
  DirectIdentifier
  RequiresPseudonymisation
  AIRestricted
  Restricted
```

`client.ville` est classée comme donnée personnelle / identifiant indirect.

`client.consentement_contact` est également traité comme donnée personnelle confidentielle.

## 15.2 Chasseurs

Les colonnes d'identité et de contact des chasseurs reçoivent des protections similaires.

## 15.3 Critères de recherche

Les budgets et critères de recherche sont protégés :

```text
demande_version.budget_min
demande_version.budget_max
  PersonalData
  FinancialData
  AIRestricted
  Confidential
```

## 15.4 Paiements

Les montants financiers sont classifiés :

```text
paiement.montant_achat
paiement.montant_honoraires
paiement.montant_chasseur
  FinancialData
  Confidential
```

Les mêmes principes sont propagés aux données financières du warehouse.

## 15.5 Documents

Les chemins de stockage et indicateurs d'indexabilité IA sont également gouvernés, notamment avec `AIRestricted`.

Cette gouvernance est cohérente avec l'objectif de maîtriser l'utilisation des données personnelles dans les traitements analytiques et futurs usages IA.

---

# 16. Data Product

## 16.1 Produit créé

La version 1.5.0 a ajouté le Data Product :

```text
RealEstateMarketIntelligence
```

Display name :

```text
Real Estate Market Intelligence
```

Description fonctionnelle :

> Produit de données analytique fournissant une vision consolidée du marché immobilier par localisation. Il expose les volumes d'annonces, les prix moyens, les prix au mètre carré, les surfaces moyennes et les périodes de publication afin de supporter les usages BI, pilotage métier et futurs cas d'usage IA.

## 16.2 Domaine

```text
RealEstateIntelligence.RealEstateAnalytics
```

## 16.3 Owner

```text
RealEstateAnalytics
```

## 16.4 Lifecycle

```text
DEVELOPMENT
```

## 16.5 Assets

L'exécution finale a ajouté sept actifs :

```text
analytics.mart_market_by_city
analytics.stg_fact_annonce
analytics.stg_dim_bien
warehouse.fact_annonce
warehouse.dim_localisation
warehouse.dim_bien
warehouse.dim_source
```

Résultat :

```text
1 products processed
7 assets added
0 assets already assigned
```

---

# 17. Validation du Data Product via API

Le Data Product a été retrouvé par :

```text
GET /api/v1/dataProducts/name/RealEstateMarketIntelligence
```

avec :

- son ID ;
- son owner ;
- son domaine ;
- sa description ;
- son lifecycle.

L'API Data Product n'a pas retourné directement `assets` dans la représentation testée malgré `fields=owners,domains,assets`.

La relation a donc été validée depuis l'actif lui-même.

Sur :

```text
real-estate-postgresql.real_estate.analytics.mart_market_by_city
```

la réponse OpenMetadata contient bien :

```text
dataProducts:
  RealEstateMarketIntelligence
```

La relation Data Product ↔ Asset est donc persistée et confirmée.

---

# 18. Lineage analytique

La validation OpenMetadata/dbt montre notamment la dépendance du mart analytique :

```text
warehouse.dim_localisation
          \
           ───► analytics.mart_market_by_city
          /
analytics.stg_fact_annonce
```

dbt apporte ainsi une information que la simple introspection PostgreSQL ne peut pas fournir de manière équivalente : le graphe logique des transformations.

---

# 19. Kubernetes

## 19.1 Namespace de gouvernance

Les composants OpenMetadata et Governance s'exécutent dans :

```text
openmetadata
```

La base applicative s'exécute dans :

```text
real-estate
```

## 19.2 Image de gouvernance

Image historique utilisée pendant les tests :

```text
gitlab.local:4567/root/chasse_immobiliere/real-estate-governance:latest
```

Le pipeline construit également une image immutable :

```text
gitlab.local:4567/root/chasse_immobiliere/real-estate-governance:<CI_COMMIT_SHORT_SHA>
```

C'est cette seconde forme qui doit devenir la référence GitOps.

## 19.3 Secret OpenMetadata

Le Job reçoit :

```text
OM_URL=http://openmetadata:8585/api
```

et le JWT via :

```text
secret: om-admin-token
key: jwtToken
```

## 19.4 Registry

Le pull de l'image utilise :

```text
gitlab-registry-auth
```

---

# 20. GitLab CI — gouvernance

Le fichier :

```text
.gitlab/ci/governance.yml
```

contient deux jobs principaux.

## 20.1 `governance:validate`

Responsabilités :

- utiliser Python 3.12 ;
- installer les requirements ;
- compiler `governance/scripts/main.py` ;
- valider les fichiers JSON ;
- empêcher la construction d'une image contenant une erreur de syntaxe Python ou JSON.

## 20.2 `governance:build-image`

Le build produit deux tags :

```text
real-estate-governance:$CI_COMMIT_SHORT_SHA
real-estate-governance:latest
```

puis les pousse dans le registre GitLab.

Une amélioration en cours ajoute un artefact dotenv :

```text
GOVERNANCE_IMAGE_TAG=$CI_COMMIT_SHORT_SHA
```

afin que le job GitOps sache précisément quelle image immutable publier.

---

# 21. Publication GitOps OpenMetadata

Le fichier :

```text
.gitlab/ci/openmetadata.yml
```

publie dans le dépôt :

```text
https://gitlab.local/root/lab-gitops.git
```

Le job :

```text
openmetadata:publish-gitops
```

utilise un runner `shell`.

Il récupère les credentials depuis :

```text
openmetadata/lab-gitops-git-credentials
```

puis clone temporairement le dépôt dans :

```text
/tmp/chasse-lab-gitops
```

Il publie trois ensembles :

```text
PostgreSQL metadata ingestion
dbt OpenMetadata ingestion
Governance-as-Code
```

Chemins GitOps :

```text
workloads/openmetadata/ingestions/real-estate-postgresql
workloads/openmetadata/ingestions/real-estate-dbt
workloads/openmetadata-governance/real-estate
```

Le job configure ensuite Git, stage les modifications et ne commit que lorsqu'un diff existe.

---

# 22. Pourquoi le Job devait être supprimé manuellement auparavant

Le Job initial utilisait :

```yaml
image: .../real-estate-governance:latest
```

Le problème était le suivant :

```text
nouveau code
   ↓
nouvelle image :latest
   ↓
digest registry différent
   ↓
manifest Kubernetes identique
   ↓
aucun changement GitOps
   ↓
Argo CD n'a rien à synchroniser
```

En plus, le template d'un Job Kubernetes est immutable.

Pendant le développement, il fallait donc régulièrement :

```text
kubectl delete job
+
forcer une synchronisation Argo CD
```

Ce fonctionnement était acceptable pour le diagnostic mais ne constitue pas un workflow GitOps final.

---

# 23. Conversion du Job en hook Argo CD

Le Job a été transformé en hook de synchronisation :

```yaml
annotations:
  argocd.argoproj.io/hook: Sync
  argocd.argoproj.io/hook-delete-policy: BeforeHookCreation,HookSucceeded
```

Conséquences :

### `Sync`

Le Job participe à l'opération de synchronisation Argo CD.

### `BeforeHookCreation`

Avant une nouvelle exécution, Argo CD peut supprimer l'ancien hook afin d'éviter le conflit avec le nom fixe du Job.

### `HookSucceeded`

Une fois l'exécution réussie, Argo CD supprime le Job.

C'est pourquoi :

```bash
kubectl -n openmetadata logs job/real-estate-governance-apply
```

peut retourner :

```text
NotFound
```

après une exécution réussie.

Ce comportement est volontaire.

---

# 24. Validation du hook Argo CD

L'application :

```text
openmetadata-governance
```

a retourné :

```text
SYNC     = Synced
HEALTH   = Healthy
```

L'état de l'opération :

```text
Succeeded
successfully synced (all tasks run)
```

et le résultat du hook :

```text
Job | openmetadata | real-estate-governance-apply
hookPhase=Succeeded
status=Pruned
```

Cela valide le cycle :

```text
Argo CD
   ↓
création du hook
   ↓
Job Governance
   ↓
succès
   ↓
HookSucceeded
   ↓
suppression automatique
```

Le Job `retail-governance-apply` visible dans le même Application Argo CD appartient à un autre workload et n'est pas le Job Real Estate.

---

# 25. Workflow GitOps cible

Le workflow final recherché est :

```text
Developer
   │
   │ git push
   ▼
GitLab
   │
   ├── governance:validate
   │
   ▼
governance:build-image
   │
   ├── governance:<COMMIT_SHA>
   │
   └── dotenv GOVERNANCE_IMAGE_TAG
   │
   ▼
openmetadata:publish-gitops
   │
   ├── injecte le SHA dans le manifest
   │
   └── commit lab-gitops
   ▼
lab-gitops
   │
   ▼
Argo CD
   │
   ▼
Sync Hook
   │
   ▼
real-estate-governance-apply
   │
   ▼
OpenMetadata
   │
   ├── Domains
   ├── Glossary
   ├── Classifications
   ├── Data Layers
   ├── Ownership
   ├── Data Quality
   ├── Glossary assignments
   ├── Privacy
   └── Data Products
```

L'objectif opérationnel est qu'un simple :

```bash
git push
```

suffise.

---

# 26. État exact de l'automatisation au moment de cette documentation

## Validé

- image Governance construite par GitLab CI ;
- image SHA + `latest` poussées dans le registre ;
- publication vers `lab-gitops` existante ;
- Argo CD `openmetadata-governance` opérationnel ;
- hook `Sync` fonctionnel ;
- `BeforeHookCreation` fonctionnel ;
- `HookSucceeded` fonctionnel ;
- exécution Governance 1.5.0 réussie ;
- Data Product réussi ;
- Data Product ↔ asset confirmé ;
- dbt exécuté et testé dans Kubernetes ;
- OpenMetadata enrichi par PostgreSQL, dbt et Governance-as-Code.

## À finaliser

Le dernier raccord CI/GitOps consiste à utiliser l'artefact :

```text
GOVERNANCE_IMAGE_TAG=$CI_COMMIT_SHORT_SHA
```

dans `openmetadata:publish-gitops`, afin de remplacer le placeholder du manifest :

```text
__GOVERNANCE_IMAGE_TAG__
```

avant publication dans `lab-gitops`.

Cette étape garantit qu'un changement de gouvernance modifie réellement le dépôt GitOps et provoque une nouvelle synchronisation Argo CD.

---

# 27. Incidents rencontrés et enseignements

## 27.1 `apply_data_products` dans la mauvaise classe

Erreur :

```text
'GovernanceEngine' object has no attribute 'apply_data_products'
```

Cause : méthode positionnée dans la mauvaise classe.

Correction : séparation stricte :

```text
OpenMetadataClient
    API helpers

GovernanceEngine
    orchestration des étapes
```

## 27.2 Champ Data Product `domain`

Erreur API :

```text
Unrecognized field "domain"
```

OpenMetadata attendait :

```text
domains
```

et non :

```text
domain
```

## 27.3 Format de `domains`

Deuxième erreur :

```text
Cannot deserialize value of type java.lang.String from Object value
```

La version OpenMetadata utilisée attendait une liste de chaînes/FQN, pas des objets complexes.

## 27.4 BulkAssets

Erreur :

```text
Cannot deserialize BulkAssets from Array
```

L'endpoint `/assets/add` attendait un objet de type :

```json
{
  "assets": [...]
}
```

et non un tableau brut.

## 27.5 Endpoint assets avec ID

Erreur :

```text
dataProduct instance for <UUID> not found
```

Le test API a démontré que l'endpoint d'ajout fonctionnait avec le nom du Data Product dans le chemin.

## 27.6 Méthodes Python perdues pendant les corrections

Des éditions successives avaient créé :

- méthodes dupliquées ;
- méthode `upsert_data_product` absente ;
- méthode `apply_data_layer_to_table` supprimée ;
- appel avec une signature incompatible.

Le fichier `main.py` a finalement été restructuré et validé syntaxiquement avant redéploiement.

### Leçon

Pour ce type de moteur, les modifications doivent être suivies au minimum par :

```bash
python -m py_compile governance/scripts/main.py
git diff --check
```

et idéalement par des tests unitaires ciblant la structure et les payloads API.

---

# 28. Idempotence

L'un des critères importants du moteur est sa capacité à être rejoué.

La réexécution des privacy assignments a montré :

```text
27 processed
0 changed
27 already correct
0 missing
```

Le moteur distingue donc :

```text
changed
already correct
missing
```

Cette propriété est essentielle dans un environnement GitOps : une synchronisation répétée ne doit pas détériorer ou dupliquer l'état.

---

# 29. Sécurité

Les principes appliqués sont :

- aucun JWT OpenMetadata en clair dans Git ;
- secrets injectés via Kubernetes ;
- credentials GitOps stockés dans un Secret ;
- registry authentifié via `imagePullSecrets` ;
- données sensibles classifiées au niveau colonne ;
- séparation des données opérationnelles et analytiques ;
- restriction explicite de certaines données pour les usages IA ;
- pseudonymisation identifiée comme exigence pour certains identifiants ;
- traçabilité par Git, CI et OpenMetadata.

---

# 30. Gouvernance et IA

La gouvernance prépare directement les futurs usages IA.

Le principe n'est pas :

```text
toutes les données OpenMetadata → IA
```

mais plutôt :

```text
catalogue
   ↓
classification
   ↓
ownership
   ↓
privacy
   ↓
quality
   ↓
sélection des données autorisées
   ↓
usage analytique / IA
```

Les tags tels que :

```text
AIRestricted
RequiresPseudonymisation
PersonalData
FinancialData
Restricted
Confidential
```

permettent de construire ultérieurement des contrôles automatisés avant exposition à un modèle ou à un pipeline IA.

---

# 31. Responsabilités des composants

| Composant | Responsabilité |
|---|---|
| PostgreSQL | stockage opérationnel et analytique |
| raw | données ingérées |
| staging | préparation / validation |
| real_estate | OLTP métier |
| warehouse | modèle dimensionnel |
| analytics | consommation analytique |
| dbt | transformation, tests, documentation, lineage |
| OpenMetadata | catalogue central et gouvernance |
| Governance-as-Code | état déclaratif métier/RGPD/qualité |
| GitLab | source du code |
| GitLab CI | validation, build et publication |
| GitLab Registry | images container |
| lab-gitops | source de vérité de déploiement Kubernetes |
| Argo CD | réconciliation Git → Kubernetes |
| Kubernetes | environnement d'exécution |

---

# 32. Séparation des responsabilités Git et GitOps

Deux dépôts ont des responsabilités différentes.

## `chasse_immobiliere`

Contient l'intention :

```text
code
SQL
dbt
governance
Dockerfiles
manifests sources
CI
documentation
```

## `lab-gitops`

Contient l'état à déployer :

```text
workloads/
applications/
Kubernetes manifests
```

Cette séparation est volontaire.

Le dépôt applicatif produit un état déployable ; le dépôt GitOps constitue ensuite la source de vérité observée par Argo CD.

---

# 33. Commandes de diagnostic utiles

## État Argo CD

```bash
kubectl -n argocd get application openmetadata-governance \
  -o custom-columns=NAME:.metadata.name,SYNC:.status.sync.status,HEALTH:.status.health.status,REVISION:.status.sync.revision
```

## Dernière opération Argo CD

```bash
kubectl -n argocd get application openmetadata-governance \
  -o jsonpath='{.status.operationState.phase}{"\n"}{.status.operationState.message}{"\n"}'
```

## Résultats des hooks

```bash
kubectl -n argocd get application openmetadata-governance \
  -o jsonpath='{range .status.operationState.syncResult.resources[*]}{.kind}{" | "}{.namespace}{" | "}{.name}{" | hookPhase="}{.hookPhase}{" | status="}{.status}{" | "}{.message}{"\n"}{end}'
```

## Job pendant son exécution

```bash
kubectl -n openmetadata get job,pod \
  -l app=real-estate-governance-apply
```

## Logs pendant que le Job existe

```bash
kubectl -n openmetadata logs \
  job/real-estate-governance-apply
```

Avec `HookSucceeded`, il est normal que cette dernière commande retourne `NotFound` après un succès.

---

# 34. Résultat final

Au 26 août 2026, la chaîne fonctionnelle validée est :

```text
PostgreSQL
    │
    ├────────► OpenMetadata technical metadata
    │
    ▼
Warehouse
    │
    ▼
dbt
    │
    ├────────► tests : 20/20 PASS
    ├────────► documentation
    ├────────► manifest/catalog
    └────────► lineage
    │
    ▼
Analytics
    │
    ▼
OpenMetadata
    ▲
    │
Governance-as-Code v1.5.0
    │
    ├── Domains
    ├── Glossary
    ├── Classifications
    ├── Data Layers
    ├── Ownership
    ├── Data Quality
    ├── Glossary Assignments
    ├── Privacy / RGPD
    └── Data Products
```

La dernière exécution complète a terminé avec :

```text
Data Product governance completed:
1 products processed,
7 assets added,
0 assets already assigned

Governance-as-Code execution completed successfully

Governance apply completed successfully
```

Le Data Product `RealEstateMarketIntelligence` est présent dans OpenMetadata, rattaché au domaine analytique et à l'équipe `RealEstateAnalytics`, et sa relation avec `analytics.mart_market_by_city` a été confirmée via l'API OpenMetadata.

Argo CD a ensuite validé le nouveau mécanisme de hook :

```text
Application: Synced / Healthy
Operation: Succeeded
Hook: real-estate-governance-apply
hookPhase=Succeeded
status=Pruned
```

La gouvernance fonctionnelle est donc validée.

---

# 35. Prochaine action

La prochaine action technique est limitée et clairement identifiée :

> Finaliser la propagation du tag immutable `GOVERNANCE_IMAGE_TAG=$CI_COMMIT_SHORT_SHA` depuis `governance:build-image` vers `openmetadata:publish-gitops`, remplacer `__GOVERNANCE_IMAGE_TAG__` dans le manifest publié, puis effectuer un test complet à partir d'un simple `git push`.

Le critère d'acceptation sera :

```text
git push
   ↓
CI validation
   ↓
image SHA
   ↓
commit automatique lab-gitops
   ↓
Argo CD sync
   ↓
Governance hook
   ↓
OpenMetadata
   ↓
Succeeded
```

sans :

```text
kubectl delete job
```

et sans :

```text
kubectl patch application ...
```

---

# 36. Conclusion

La gouvernance du projet n'est plus une série d'opérations manuelles dans OpenMetadata. Elle est devenue une couche d'ingénierie versionnée et reproductible, intégrée à la plateforme de données.

Le système relie désormais :

```text
modélisation métier
+
OLTP
+
warehouse
+
dbt
+
qualité
+
catalogue
+
RGPD
+
ownership
+
Data Products
+
CI/CD
+
GitOps
+
Kubernetes
```

Le résultat fournit à la fois une plateforme techniquement exploitable et une démonstration cohérente des choix d'architecture, de qualité, de sécurité, de gouvernance et d'industrialisation du projet.


# OpenMetadata Governance-as-Code --- Metrics & Deployment Validation

**Project:** Projet Fil Rouge --- Service de chasse immobilière\
**Component:** Data Governance / OpenMetadata\
**Platform:** GitLab CI → GitOps → Argo CD → Kubernetes → OpenMetadata\
**OpenMetadata version:** 1.12.11\
**Validated governance image:** `b0736293`\
**Validation date:** 28 August 2026

------------------------------------------------------------------------

## 1. Purpose

This document records the implementation and validation of the
**OpenMetadata Governance-as-Code metrics layer** for the real-estate
data platform.

The objective was not merely to display KPIs in OpenMetadata, but to
make their metadata **declarative, version-controlled, reproducible and
automatically deployed**. Each business metric is now governed with its
definition, semantic metadata, ownership, analytical domain, unit,
granularity, SQL expression and business glossary relationships.

The implementation extends the existing governance chain without
introducing manual OpenMetadata configuration.

------------------------------------------------------------------------

## 2. Context

The project already had a working Governance-as-Code framework
responsible for:

1.  Domains
2.  Business glossary
3.  Classifications and tags
4.  Data Layer governance
5.  Ownership
6.  Data Quality governance
7.  Glossary assignments
8.  Privacy assignments
9.  Data Products

The Metrics definitions existed conceptually, but the deployed
governance execution stopped at **Step 9/9**. Although an
`upsert_metric()` function was present in `main.py`, no governance
method called it from the main execution flow.

Consequently, the Metrics feature was not part of the effective
automated deployment.

------------------------------------------------------------------------

## 3. Problem Identified

Inspection of `governance/scripts/main.py` identified three principal
issues.

### 3.1 Metrics were not executed

The governance engine ended with:

``` text
Step 9/9 - Applying Data Products
```

There was no `apply_metrics()` method connected to
`GovernanceEngine.run()`.

Therefore, the existence of `upsert_metric()` alone was insufficient:
the metrics configuration was never processed during a governance
deployment.

### 3.2 Metric expression payload did not match the OpenMetadata API model

The former implementation used separate fields equivalent to:

``` text
metricExpressionLanguage
metricExpressionCode
```

For the OpenMetadata version used by the platform, the metric creation
model expects a structured expression:

``` json
{
  "metricExpression": {
    "language": "SQL",
    "code": "..."
  }
}
```

The implementation was corrected to use this API representation.

### 3.3 Semantic relationships were incomplete

The initial metric upsert logic did not attach business glossary terms
directly to Metric entities.

The target governance model required metrics to be semantically
connected to concepts such as:

-   Bien immobilier
-   Prix du bien
-   Prix au mètre carré
-   Surface
-   Annonce immobilière
-   Secteur géographique
-   DPE
-   Source de données
-   Mandat de recherche

------------------------------------------------------------------------

## 4. Target Architecture

The deployment remains fully GitOps-driven.

``` text
Developer workstation
        |
        | git push
        v
GitLab repository
        |
        | CI validation + image build
        v
GitLab Container Registry
        |
        | immutable governance image :<commit-SHA>
        v
lab-gitops repository
        |
        | manifest updated with immutable SHA
        v
Argo CD
        |
        | reconcile desired state
        v
Kubernetes / openmetadata namespace
        |
        | Governance Job
        v
OpenMetadata REST API
        |
        v
Governed metadata
```

There is no requirement to run Kubernetes locally on the Windows
workstation. Deployment continues through GitLab CI and GitOps, with
Kubernetes used as the execution platform.

------------------------------------------------------------------------

## 5. Immutable Kubernetes Job Lifecycle

The Governance Job uses the Git commit SHA in both its Kubernetes name
and container image.

Validated deployment:

``` text
job.batch/real-estate-governance-apply-b0736293
pod/real-estate-governance-apply-b0736293-72qgj
```

Result:

``` text
STATUS: Complete
COMPLETIONS: 1/1
DURATION: 17s
```

Image model:

``` text
gitlab.local:4567/root/chasse_immobiliere/real-estate-governance:<SHA>
```

This design gives each governance revision an immutable execution
identity.

When a new governance commit is published:

``` text
SHA A -> Job real-estate-governance-apply-SHA-A
SHA B -> desired Job real-estate-governance-apply-SHA-B
```

Argo CD creates the new Job and prunes the previous revision according
to the GitOps desired state.

### Important lifecycle decision

The Job intentionally uses:

-   no Argo CD Sync hook;
-   no `ttlSecondsAfterFinished`;
-   no manual deletion requirement.

A TTL on a normal Argo-managed Job would delete the resource after
completion and cause Argo self-heal to recreate it repeatedly. Keeping
the completed Job in desired state prevents this loop.

------------------------------------------------------------------------

## 6. Metrics Governance Configuration

Nine business metrics are governed.

  Metric                      Type      Unit         Granularity
  --------------------------- --------- ------------ -------------
  Market Listings             COUNT     COUNT        DAY
  Average Property Price      AVERAGE   EUR          DAY
  Average Price per m²        AVERAGE   EUR_PER_M2   DAY
  Average Property Surface    AVERAGE   M2           DAY
  Active Mandates             COUNT     COUNT        DAY
  Listings by City            COUNT     COUNT        DAY
  Listings by DPE             COUNT     COUNT        DAY
  Listings by Property Type   COUNT     COUNT        DAY
  Listings by Source          COUNT     COUNT        DAY

The definitions are maintained declaratively in:

``` text
governance/metrics/real_estate_metrics.json
```

Each definition can contain:

``` text
name
display_name
description
metric_type
unit
granularity
expression_language
expression
source
owner
domain
dimensions
glossary_terms
```

`source` and `dimensions` are governance configuration metadata used by
the automation; they are not blindly sent as unsupported CreateMetric
fields.

------------------------------------------------------------------------

## 7. Governance Engine Changes

### 7.1 Correct OpenMetadata expression model

Metric payloads now use:

``` python
"metricExpression": {
    "language": metric.get("expression_language", "SQL"),
    "code": metric["expression"],
}
```

This preserves the SQL definition directly in OpenMetadata.

### 7.2 Standard and custom units

The engine distinguishes OpenMetadata standard units from
project-specific units.

Standard units include:

``` text
COUNT
DOLLARS
PERCENTAGE
TIMESTAMP
SIZE
REQUESTS
EVENTS
TRANSACTIONS
OTHER
```

Project units such as:

``` text
EUR
EUR_PER_M2
M2
```

are represented using:

``` text
unitOfMeasurement = OTHER
customUnitOfMeasurement = <project unit>
```

The OpenMetadata UI consequently displays the intended business unit.

### 7.3 Owner assignment

Metric definitions reference the governance team:

``` text
RealEstateAnalytics
```

The engine resolves the team in OpenMetadata and sends its entity ID as
the metric owner.

This avoids hard-coded UUIDs and keeps the configuration portable.

### 7.4 Domain assignment

Metrics are associated with:

``` text
RealEstateIntelligence.RealEstateAnalytics
```

The engine validates that the domain exists before applying the metric.

### 7.5 Glossary relationships

Glossary terms are validated before metric creation and attached as
confirmed manual Glossary relationships.

Conceptually:

``` json
{
  "tagFQN": "RealEstateBusinessGlossary.PrixM2",
  "source": "Glossary",
  "labelType": "Manual",
  "state": "Confirmed"
}
```

This links technical KPI definitions to governed business vocabulary.

### 7.6 Source validation

When a metric declares an analytical source table, the governance engine
checks that the table exists in OpenMetadata.

For example:

``` text
real-estate-postgresql.real_estate.analytics.mart_market_overview
```

or:

``` text
real-estate-postgresql.real_estate.analytics.mart_market_by_city
```

A missing source produces a warning rather than inventing a catalog
entity.

### 7.7 Dedicated `apply_metrics()` stage

A dedicated governance stage now:

1.  loads the metric configuration;
2.  checks the source asset;
3.  resolves the owner;
4.  resolves the domain;
5.  validates glossary terms;
6.  calls the Metric upsert;
7.  counts processed metrics.

The governance execution now contains **10 stages**.

------------------------------------------------------------------------

## 8. Final Governance Execution

The validated execution order is:

``` text
Step 1/10  - Applying domains
Step 2/10  - Applying business glossary
Step 3/10  - Applying classifications and tags
Step 4/10  - Applying Data Layer governance
Step 5/10  - Applying ownership
Step 6/10  - Applying Data Quality governance
Step 7/10  - Applying glossary assignments
Step 8/10  - Applying privacy assignments
Step 9/10  - Applying Data Products
Step 10/10 - Applying Metrics
```

The final Job successfully reached Step 10.

------------------------------------------------------------------------

## 9. Deployment Validation Results

### 9.1 Data Layer governance

The deployment reported:

``` text
47 processed
0 changed
47 already correct
0 missing
```

This confirms idempotency: already-correct metadata was detected instead
of unnecessarily modified.

### 9.2 Ownership

The existing teams were successfully resolved:

``` text
RealEstateDataTeam
RealEstateBusiness
RealEstateAnalytics
```

Existing ownership assignments remained correct.

### 9.3 Data Quality governance

Required tags remained present and required lineage was successfully
verified for the tested analytical assets.

### 9.4 Glossary assignments

Result:

``` text
18 processed
0 changed
18 already correct
0 missing
```

### 9.5 Privacy assignments

Result:

``` text
27 processed
0 changed
27 already correct
0 missing
```

### 9.6 Data Product

The following Data Product was successfully applied:

``` text
RealEstateMarketIntelligence
```

Its governed assets were also associated successfully.

### 9.7 Metrics

The new final stage reported:

``` text
Step 10/10 - Applying Metrics

Metric applied: marketListingsTotal
Metric applied: averagePropertyPrice
Metric applied: averagePricePerM2
Metric applied: averagePropertySurface
Metric applied: activeMandates
Metric applied: listingsByCity
Metric applied: listingsByDpe
Metric applied: listingsByPropertyType
Metric applied: listingsBySource

Metric governance completed: 9 metrics processed
```

The complete governance execution then ended with:

``` text
Governance-as-Code execution completed successfully
```

Therefore:

``` text
Metrics processed: 9
Metrics successfully applied: 9
Governance Job result: SUCCESS
```

------------------------------------------------------------------------

## 10. OpenMetadata UI Validation

The API success was complemented by visual validation in OpenMetadata.

### Average Price per m²

For:

``` text
averagePricePerM2
```

OpenMetadata displays:

``` text
Display Name      Average Price per m²
Domain            Real Estate Analytics
Owner             Real Estate Analytics
Metric Type       AVERAGE
Measurement Unit  EUR_PER_M2
Granularity       DAY
```

The description is also correctly persisted.

### SQL expression

The Expression tab displays:

``` sql
AVG(prix / NULLIF(surface, 0))
```

This proves the corrected nested `metricExpression` payload is persisted
and exposed by OpenMetadata.

------------------------------------------------------------------------

## 11. Business Glossary Validation

The Metrics catalog also shows the expected glossary relationships.

  -----------------------------------------------------------------------
  Metric                              Governed glossary concepts
  ----------------------------------- -----------------------------------
  Active Mandates                     Mandat de recherche

  Average Price per m²                Bien immobilier; Prix au mètre
                                      carré

  Average Property Price              Bien immobilier; Prix du bien

  Average Property Surface            Bien immobilier; Surface

  Listings by City                    Annonce immobilière; Secteur
                                      géographique

  Listings by DPE                     Annonce immobilière; Diagnostic de
                                      performance énergétique

  Listings by Property Type           Annonce immobilière; Bien
                                      immobilier

  Listings by Source                  Annonce immobilière; Source de
                                      données

  Market Listings                     Annonce immobilière
  -----------------------------------------------------------------------

This is important because the Metrics catalog is no longer only a
technical list of calculations. It is connected to the same controlled
vocabulary used elsewhere in the data governance model.

------------------------------------------------------------------------

## 12. Example: Average Price per m²

This KPI demonstrates the complete governance chain.

### Business purpose

The metric normalizes property valuation by surface and allows
comparison between properties and markets independently of property
size.

### Technical definition

``` sql
AVG(prix / NULLIF(surface, 0))
```

### Governance metadata

``` text
Metric Type:       AVERAGE
Unit:              EUR_PER_M2
Granularity:       DAY
Owner:             RealEstateAnalytics
Domain:            RealEstateIntelligence.RealEstateAnalytics
Glossary:          Bien + PrixM2
```

### Result

The definition is:

-   stored in Git;
-   validated by CI;
-   packaged in the governance image;
-   deployed through GitOps;
-   executed by Kubernetes;
-   applied through the OpenMetadata API;
-   visible and searchable in the OpenMetadata catalog.

------------------------------------------------------------------------

## 13. Why This Design Matters

### Reproducibility

The governance state is derived from version-controlled configuration
rather than manual UI operations.

### Traceability

A Git commit produces an immutable governance image and an identifiable
Kubernetes Job.

For the validated revision:

``` text
SHA: b0736293
Job: real-estate-governance-apply-b0736293
```

### Idempotency

Reapplying governance does not duplicate correctly configured metadata.
Existing correct assignments are detected.

### Separation of responsibilities

The architecture keeps distinct concerns:

``` text
dbt / SQL marts
    -> compute analytical datasets

Prometheus / Grafana
    -> operational and technical observability

OpenMetadata Metrics
    -> business KPI definition and semantic governance
```

OpenMetadata is therefore used as the **catalog and governance layer**,
not as a replacement for the analytical engine or monitoring platform.

### Semantic consistency

Metrics, tables and columns share the same business glossary. This gives
the project a common language between technical implementation and
business interpretation.

### Automation

No manual OpenMetadata editing is required to recreate the governed
Metrics state.

------------------------------------------------------------------------

## 14. Evidence for Project / Jury

This implementation provides concrete evidence for several architecture
and governance capabilities:

-   Governance-as-Code;
-   metadata cataloguing;
-   business glossary;
-   data ownership;
-   domain-oriented governance;
-   semantic KPI definitions;
-   Data Product governance;
-   Data Quality metadata;
-   privacy classification;
-   lineage verification;
-   Git-based traceability;
-   CI/CD;
-   immutable container deployment;
-   GitOps;
-   Kubernetes automation;
-   reproducible configuration;
-   separation between operational, analytical and governance concerns.

The implementation is therefore not simply a list of KPIs: it
demonstrates how business indicators are integrated into an
industrialized data governance lifecycle.

------------------------------------------------------------------------

## 15. Current Validated State

At the end of this implementation:

``` text
OpenMetadata connectivity        OK
Domains                          OK
Business glossary                OK
Classifications / tags           OK
Data Layer governance            OK
Ownership                        OK
Data Quality governance          OK
Glossary assignments             OK
Privacy assignments              OK
Data Product                     OK
Metrics                          9/9 OK
Metric owner                     Verified
Metric domain                    Verified
Metric unit                      Verified
Metric granularity               Verified
Metric SQL expression            Verified
Metric glossary relationships    Verified
GitLab deployment                OK
GitOps publication               OK
Argo CD reconciliation           OK
Kubernetes Job                   Complete 1/1
```

------------------------------------------------------------------------

## 16. Remaining Enhancement: Certification

The OpenMetadata Metric UI currently shows no Certification value.

The project already has a Bronze / Silver / Gold certification concept
available. A possible future governance enhancement is to formalize
certification rules such as:

``` text
RAW                  -> Bronze
STAGING / OLTP       -> Silver
WAREHOUSE / ANALYTICS -> Gold
```

Certification was **not part of the Metrics correction described in this
document** and should be implemented as a separate controlled governance
change rather than mixed into the now-validated Metrics deployment.

------------------------------------------------------------------------

## 17. Conclusion

The OpenMetadata Metrics implementation is now operational and validated
end-to-end.

The project moved from a situation where metric-upsert code existed but
was never executed to a complete automated governance workflow
containing a dedicated tenth stage.

The final architecture guarantees that business KPI metadata is:

**defined in code → versioned → validated → containerized → published
through GitOps → reconciled by Argo CD → executed in Kubernetes →
persisted in OpenMetadata.**

All nine intended real-estate metrics are now governed and visible with
their semantic and organizational context.

**Status: Metrics Governance-as-Code implementation COMPLETE and
VALIDATED.**
