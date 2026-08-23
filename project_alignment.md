# Analyse d'alignement --- Projet Chasse Immobilière

**Projet :** Chasse Immobilière\
**Périmètre analysé :** Pipeline Data, architecture et besoins du
projet\
**Date :** 23 août 2026\
**Statut :** Alignement confirmé --- développement global encore en
cours\
**Milestone évalué :** Pipeline d'ingestion Real Estate end-to-end

------------------------------------------------------------------------

## 1. Objectif du document

Ce document compare les besoins définis pour le projet **Chasse
Immobilière** avec l'état réellement implémenté au 23 août 2026.

L'objectif est de vérifier que les travaux réalisés sur le pipeline :

``` text
Source
→ MinIO
→ RAW
→ STAGING
→ OLTP
```

restent cohérents avec :

-   le référentiel et la grille d'évaluation ;
-   la constitution du projet ;
-   l'Architecture Playbook ;
-   les objectifs Data / IA ;
-   les exigences DevOps, sécurité et gouvernance ;
-   la trajectoire globale du projet.

------------------------------------------------------------------------

## 2. Verdict global

> **Le travail réalisé est aligné avec les besoins du projet.**

Le pipeline d'ingestion et de qualité des données constitue désormais
une base technique solide et va au-delà d'une simple démonstration
théorique.

Cependant :

> **Le pipeline Data n'est qu'une partie du projet global et ne signifie
> pas que l'ensemble du projet ou du bloc BC05 est terminé.**

Les principaux domaines restant à construire ou compléter sont notamment
:

-   OLAP / Data Warehouse ;
-   analyse des 3V ;
-   analytics et KPI ;
-   matching / Machine Learning ;
-   architecture IA ;
-   gouvernance et lineage du nouveau domaine immobilier ;
-   RGPD opérationnel ;
-   observabilité complète ;
-   sécurité et tests associés ;
-   industrialisation et GitOps complémentaires.

------------------------------------------------------------------------

## 3. Pipeline actuellement validé

Le chemin suivant est désormais fonctionnel de bout en bout :

``` text
GitLab
   ↓
GitLab CI/CD
   ↓
GitLab Container Registry
   ↓
Airflow
   ↓
KubernetesPodOperator
   ↓
Génération dataset
   ↓
MinIO
   ↓
RAW PostgreSQL
   ↓
RAW Quality Gate
   ↓
STAGING PostgreSQL
   ↓
STAGING Quality Gate
   ↓
OLTP PostgreSQL
   ↓
OLTP Quality Gate
   ↓
SUCCESS
```

Run end-to-end de référence :

``` text
manual__2026-08-23T07:37:15+00:00
```

État :

``` text
SUCCESS
```

Durée approximative :

``` text
2 minutes 45 secondes
```

------------------------------------------------------------------------

## 4. Alignement avec les besoins Data

  Besoin                    Implémentation actuelle             État
  ------------------------- ----------------------------------- ------
  Extraction / ingestion    Génération → MinIO → PostgreSQL     ✅
  Persistance des sources   MinIO                               ✅
  Zone RAW                  `raw.recherches`, `raw.annonces`    ✅
  Transformation            RAW → STAGING                       ✅
  Normalisation             Parsing et nettoyage Python         ✅
  Data Quality RAW          Quality gate SQL                    ✅
  Data Quality STAGING      Quality gate                        ✅
  Base OLTP                 Schéma `real_estate`                ✅
  Data Quality OLTP         Quality gate SQL                    ✅
  Réconciliation            1000/1000                           ✅
  Contraintes métier        PK, FK, CHECK, UNIQUE               ✅
  Idempotence métier        UPSERT + unicité source/référence   ✅
  Orchestration             Airflow                             ✅
  Exécution Kubernetes      KubernetesPodOperator               ✅
  Conteneurisation          Image Python dédiée                 ✅
  CI/CD                     GitLab CI/CD                        ✅
  Registry privé            GitLab Container Registry           ✅
  Exécution end-to-end      DAG complet validé                  ✅
  OLAP / Warehouse          Non construit                       ❌
  Analytics / marts         Non construit                       ❌
  3V                        À formaliser/démontrer              ⚠️
  RGPD dans le pipeline     À compléter                         ⚠️

------------------------------------------------------------------------

## 5. Alignement avec BC05

Le périmètre BC05 attendu couvre plusieurs dimensions et ne doit pas
être réduit au seul ETL.

### 5.1 Analyse des 3V

État :

``` text
⚠️ À compléter
```

Le pipeline fournit désormais une base mesurable pour documenter :

-   Volume ;
-   Vélocité ;
-   Variété.

Mais une étude formelle et des preuves dédiées doivent encore être
produites.

### 5.2 ETL et qualité des données

État :

``` text
✅ ACQUIS pour le périmètre actuel
```

Éléments démontrés :

-   ingestion ;
-   persistance des sources ;
-   RAW ;
-   transformations ;
-   STAGING ;
-   normalisation ;
-   contrôles qualité ;
-   réconciliation ;
-   chargement OLTP ;
-   validation finale ;
-   orchestration complète.

### 5.3 RGPD

État :

``` text
⚠️ PARTIEL
```

Le projet possède des documents RGPD et une approche de gouvernance,
mais leur application opérationnelle au pipeline immobilier doit encore
être explicitement démontrée.

Points à traiter :

-   classification des données ;
-   données personnelles ;
-   minimisation ;
-   rétention ;
-   droit d'accès/suppression si applicable ;
-   traçabilité ;
-   règles de conservation MinIO/RAW/STAGING/OLTP.

### 5.4 Base de données pour analytics / IA

État actuel :

``` text
OLTP         ✅
Contraintes  ✅
Index        ✅
OLAP         ❌
```

La partie transactionnelle est maintenant crédible.

Le principal élément manquant est le modèle analytique.

### 5.5 Matching / Machine Learning

État :

``` text
❌ NON COMMENCÉ sur cette chaîne
```

Le futur travail devra définir :

-   features ;
-   règles métier ;
-   scoring ;
-   modèle éventuel ;
-   métriques ;
-   entraînement ;
-   validation ;
-   versioning MLflow.

### 5.6 Architecture IA

État :

``` text
❌ PHASE FUTURE
```

Les briques prévues du projet pourront notamment inclure :

``` text
OLTP / OLAP
   ↓
features
   ↓
matching / ML
   ↓
MLflow
   ↓
Qdrant
   ↓
LLM local / Ollama
```

Cette couche ne doit pas être construite avant d'avoir stabilisé la
fondation Data.

------------------------------------------------------------------------

## 6. Alignement avec l'Architecture Playbook

### Database

  Exigence                        État
  ------------------------------- -----------------------
  OLTP normalisé                  ✅
  PK / FK                         ✅
  CHECK constraints               ✅
  UNIQUE constraints              ✅
  Index                           ✅
  Migrations / schéma versionné   ✅ / en consolidation
  OLAP                            ❌

### DevOps

  Exigence             État
  -------------------- ------------
  Docker               ✅
  Kubernetes           ✅
  CI/CD                ✅
  Tests automatisés    ✅
  Registry privé       ✅
  GitOps               ⚠️ partiel
  Rollback formalisé   ❌

### Testing

  Niveau           État
  ---------------- ----------------
  Data Quality     ✅
  Integration      ✅
  End-to-end       ✅
  Unit tests       ⚠️ à renforcer
  Performance      ❌
  Security tests   ❌

### Observability

  Élément             État
  ------------------- ---------------------
  Logs Airflow        ✅
  Logs des pods       ✅
  Métriques dédiées   ⚠️
  Dashboards          ❌ pour ce pipeline
  Alerting            ❌ pour ce pipeline
  Traces              ❌

------------------------------------------------------------------------

## 7. Choix d'orchestration

Le projet disposait déjà d'Airflow pour les workflows Data.

Le choix retenu est :

``` text
Airflow
   ↓
KubernetesPodOperator
   ↓
Jobs conteneurisés Kubernetes
```

Ce choix est cohérent avec l'architecture existante et évite
d'introduire inutilement un second orchestrateur.

Il apporte :

-   orchestration centralisée ;
-   exécution isolée par pod ;
-   images reproductibles ;
-   logs par tâche ;
-   gestion des dépendances ;
-   retry Airflow ;
-   séparation entre orchestration et logique métier.

------------------------------------------------------------------------

## 8. Points particulièrement solides

### 8.1 La documentation correspond à une implémentation réelle

Le pipeline n'existe pas seulement dans les documents.

Il a été :

``` text
codé
→ buildé
→ publié
→ déployé
→ exécuté
→ testé
→ corrigé
→ validé
→ documenté
```

### 8.2 Les quality gates sont intégrés au workflow

La qualité n'est pas un contrôle manuel effectué après le pipeline.

Elle fait partie de la chaîne :

``` text
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
```

Une validation échouée doit donc bloquer la progression vers l'étape
suivante.

### 8.3 Les erreurs réelles ont été diagnostiquées

Exemple :

``` text
261 invalid annonces
```

L'analyse a identifié :

``` text
date_publication
→ invalid datetime format
```

Le parseur a ensuite été corrigé jusqu'à :

``` text
invalid recherches = 0
invalid annonces   = 0
```

Cela fournit une preuve concrète de traitement de la qualité des
données.

### 8.4 Réconciliation complète

Résultat final :

``` text
staging_valid_annonces = 1000
oltp_matched_biens     = 1000
```

Avec :

``` text
0 duplicate source/reference pairs
```

------------------------------------------------------------------------

## 9. Ce que nous ne devons pas considérer comme terminé

Le succès du pipeline ne signifie pas :

``` text
BC05 complet
```

ni :

``` text
projet complet
```

Les domaines suivants restent ouverts :

``` text
OLAP
Analytics
3V
RGPD opérationnel
Matching
Machine Learning
MLflow pour ce use case
Qdrant
IA / LLM
Lineage / OpenMetadata
Observabilité
Alerting
Security testing
Performance testing
PCA/PRA spécifique
Documentation finale
Soutenance
```

------------------------------------------------------------------------

## 10. Priorité recommandée

La prochaine grande étape doit être le **Data Warehouse / OLAP**.

Nous avons actuellement :

``` text
SOURCE
   ↓
MinIO
   ↓
RAW
   ↓
STAGING
   ↓
OLTP
   ↓
QUALITY
   ✅
```

La prochaine extension logique est :

``` text
OLTP / STAGING
      ↓
  dbt / ETL
      ↓
 DATA WAREHOUSE
      ↓
 DIMENSIONS
      +
    FACTS
      ↓
    MARTS
      ↓
Analytics / BI
```

Cela permettra de compléter la séparation :

``` text
OLTP ≠ OLAP
```

qui est centrale dans l'architecture Data du projet.

------------------------------------------------------------------------

## 11. Ordre de développement recommandé

``` text
1. Source / MinIO                 ✅
2. RAW                            ✅
3. STAGING                        ✅
4. OLTP                           ✅
5. Data Quality                   ✅

6. OLAP / Data Warehouse          ← NEXT
7. dbt transformations
8. KPI / analytical marts
9. OpenMetadata / lineage
10. Analyse 3V
11. RGPD opérationnel
12. Matching features
13. Matching / ML
14. MLflow
15. Qdrant
16. Ollama / IA souveraine
17. Observabilité / alerting
18. Tests performance / sécurité
```

L'objectif est d'éviter de construire la couche IA sur une architecture
Data incomplète.

------------------------------------------------------------------------

## 12. Points documentaires à normaliser

Les documents d'architecture du projet doivent progressivement utiliser
des métadonnées homogènes :

``` text
Version
Status
Owner
Last Updated
Related ADRs
Related Components
RNCP Competencies
```

Le document :

``` text
REAL-ESTATE-INGESTION-PIPELINE.md
```

devra donc être relié explicitement :

-   aux compétences RNCP concernées ;
-   aux ADR applicables ;
-   aux composants Airflow, PostgreSQL, MinIO, GitLab et Kubernetes ;
-   au futur document OLAP.

------------------------------------------------------------------------

## 13. Conclusion

L'analyse confirme que les développements réalisés sont **alignés avec
le projet et son architecture cible**.

Nous n'avons pas créé une chaîne parallèle ou hors périmètre.

Au contraire, le milestone actuel fournit la fondation nécessaire pour
les prochaines couches :

``` text
Data acquisition
      ✅
       ↓
Data quality
      ✅
       ↓
OLTP
      ✅
       ↓
OLAP
      NEXT
       ↓
Analytics
       ↓
Matching / ML
       ↓
IA
```

Le pipeline actuel peut être considéré comme un **milestone Data
validé**, mais pas comme la fin du projet.

### Décision

> **Continuer sur l'architecture Data en construisant maintenant la
> couche OLAP / Data Warehouse avant de démarrer les composants IA
> avancés.**

------------------------------------------------------------------------

## 14. Synthèse

``` text
ALIGNEMENT PROJET                         ✅ CONFIRMÉ
PIPELINE INGESTION END-TO-END            ✅ VALIDÉ
RAW                                      ✅ VALIDÉ
STAGING                                  ✅ VALIDÉ
OLTP                                     ✅ VALIDÉ
DATA QUALITY                             ✅ VALIDÉ
CI/CD + KUBERNETES + AIRFLOW             ✅ VALIDÉ

OLAP / WAREHOUSE                         ❌ NEXT
ANALYTICS                                ❌ À FAIRE
3V                                       ⚠️ À FORMALISER
RGPD OPÉRATIONNEL                        ⚠️ À COMPLÉTER
MATCHING / ML                            ❌ À FAIRE
ARCHITECTURE IA                          ❌ À FAIRE
OBSERVABILITÉ COMPLÈTE                   ⚠️ À COMPLÉTER
SECURITY / PERFORMANCE TESTING           ❌ À FAIRE
```

> **Conclusion : la trajectoire est correcte. La prochaine étape
> structurante est OLAP / Data Warehouse.**
