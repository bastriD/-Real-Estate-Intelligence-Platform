# BC01 — C2 — Stratégie SI

**Bloc de compétences :** BC01  
**Compétence :** C2 — Définir une stratégie SI à partir de la cartographie et de l’analyse de l’existant  
**Projet :** Chasse Immobilière — Real Estate Intelligence Platform  
**Statut :** EVIDENCED  
**Owner :** Bastri Murad  
**Dernière mise à jour :** 2026-09-10

---

# 1. Objectif

Ce dossier présente la stratégie d'évolution du système d'information du projet **Chasse Immobilière**.

La stratégie n'est pas construite à partir d'une liste de technologies à intégrer.

Elle est dérivée :

- du besoin métier ;
- de la cartographie du SI actuel ;
- des écarts identifiés lors de l'audit ;
- des risques ;
- des contraintes techniques et matérielles ;
- des capacités déjà disponibles ;
- des exigences de sécurité, de gouvernance et de continuité ;
- des objectifs Data et IA du projet.

La démarche suivie est :

```text
Besoin métier
     +
Cartographie du SI
     +
Audit de l'existant
     +
Risques et écarts
     +
Contraintes
     |
     v
Orientations stratégiques
     |
     v
Priorisation
     |
     v
Trajectoire SI
     |
     v
Décisions d'architecture
     |
     v
Implémentation et preuves
```

La stratégie cherche donc à **faire évoluer et fiabiliser le SI existant**, et non à le remplacer systématiquement.

---

# 2. Sources de vérité

## Audit et cartographie

```text
../C1-Audit-SI/README.md
../C1-Audit-SI/02-Cartographie-SI-Actuel.puml
```

## Vision et objectifs métier

```text
../../../00-FOUNDATION/02-Project-Vision.md
../../../00-FOUNDATION/03-Business-Objectives.md
```

Ces documents constituent des documents de vision initiaux.

Ils contiennent également des éléments de roadmap ou des ambitions futures qui ne doivent pas être confondus avec l'état actuellement implémenté.

## Roadmap d'architecture

```text
../../../95-GOVERNANCE/10-Architecture-Roadmap.md
```

## Gestion des risques

```text
../../../95-GOVERNANCE/04-Risk-Management.md
../../../95-GOVERNANCE/11-Risk-Register.md
```

## Décisions d'architecture

```text
../../../98-ADR/
```

## Documentation historique utile

```text
../supporting/Architecture-Cible/README.md
../supporting/Veille-Technologique/README.md
```

---

# 3. Contexte métier

Le projet répond au métier de la **chasse immobilière**.

Le parcours métier principal est :

```text
Client
  |
  v
Demande
  |
  v
Versions de la demande
  |
  v
Qualification / Chasseur
  |
  v
Mandat lorsque nécessaire
  |
  v
Recherche de biens
  |
  v
Matching
  |
  v
Recommandation
  |
  v
Présentation
  |
  v
Visite
  |
  v
Suite commerciale
```

L'objectif du SI est de réduire les traitements manuels, améliorer la qualité de la sélection des biens, conserver la traçabilité des opérations et fournir aux chasseurs une plateforme Data et applicative exploitable.

Le système doit également permettre une évolution progressive vers des capacités analytiques et ML sans compromettre les règles métier.

---

# 4. Situation actuelle du SI

L'audit C1 montre que le projet dispose déjà d'une infrastructure et d'une plateforme technique importantes.

Les capacités principales comprennent :

```text
Proxmox
   |
   v
Kubernetes HA
   |
   +--> Application FastAPI
   |
   +--> PostgreSQL
   |
   +--> Airflow
   |
   +--> MLflow
   |
   +--> OpenMetadata
   |
   +--> Observability
```

Le cycle de déploiement principal repose sur :

```text
Developer
   |
   v
Git
   |
   v
GitLab
   |
   v
GitLab CI
   |
   v
Container Registry
   |
   v
GitOps repository
   |
   v
Argo CD
   |
   v
Kubernetes
```

Le SI dispose donc déjà d'une base permettant son industrialisation.

La stratégie retenue n'est pas une reconstruction complète.

Elle consiste principalement à :

```text
CONSOLIDER
    +
FIABILISER
    +
GOUVERNER
    +
SÉCURISER
    +
MESURER
    +
FAIRE ÉVOLUER
```

---

# 5. Enjeux identifiés

L'analyse de l'existant fait apparaître plusieurs enjeux structurants.

## Continuité de service

Le SI dépend de composants critiques tels que PostgreSQL, Kubernetes, le stockage, le réseau et les services GitOps.

La capacité de restauration doit donc être démontrée et non simplement supposée.

## Industrialisation

Les modifications permanentes doivent rester reproductibles et traçables.

Les changements directs dans Kubernetes ne doivent pas devenir le mécanisme normal de gestion de l'état du SI.

## Données

Le projet combine :

- données sources ;
- données brutes ;
- staging ;
- données métier OLTP ;
- warehouse ;
- analytics ;
- données d'entraînement et d'évaluation ML.

La séparation des responsabilités et la traçabilité des transformations sont donc stratégiques.

## Sécurité

L'application gère des utilisateurs, des rôles et des opérations métier.

L'authentification, l'autorisation, la protection des secrets et l'audit doivent évoluer avec le niveau de criticité du SI.

## Intelligence artificielle

Le projet doit démontrer une capacité ML/IA sans transformer un besoin métier déterministe en problème ML artificiel.

## Ressources

Le projet fonctionne sur une infrastructure physique existante avec des ressources CPU, mémoire, stockage et GPU limitées.

La stratégie doit donc rester compatible avec les ressources réellement disponibles.

---

# 6. Principe stratégique général

La stratégie SI repose sur le principe :

```text
Stabiliser
    |
    v
Mesurer
    |
    v
Sécuriser
    |
    v
Gouverner
    |
    v
Automatiser
    |
    v
Faire évoluer
```

L'ajout de technologies n'est pas considéré comme un objectif en soi.

Une nouvelle technologie doit répondre à un besoin ou à un risque démontré.

---

# 7. Axe stratégique S1 — Fiabiliser le SI et assurer la continuité

## Enjeu

Les données métier et la plateforme constituent des actifs critiques.

Une architecture moderne n'est pas suffisante si le système ne peut pas être restauré après une défaillance.

## Orientation

Renforcer progressivement :

- sauvegarde ;
- restauration ;
- validation ;
- observabilité ;
- disponibilité ;
- gestion des incidents ;
- capacité de reprise.

## État actuel démontré

Le projet dispose d'un processus PostgreSQL :

```text
PostgreSQL
     |
     v
Backup
     |
     v
MinIO externe
     |
     v
Restauration isolée
     |
     v
Validation d'intégrité
```

Le backup permanent est planifié par Kubernetes et déployé via GitOps.

La restauration isolée a été testée.

## Évolutions

Les améliorations restantes comprennent notamment :

- politique de rétention / ILM ;
- alertes sur l'échec ou l'ancienneté des sauvegardes ;
- mesure plus complète du RTO ;
- exercices de reprise plus larges.

## Résultat attendu

Passer de :

```text
Nous avons des sauvegardes
```

à :

```text
Nous pouvons démontrer la reprise
```

---

# 8. Axe stratégique S2 — Industrialiser les changements et les déploiements

## Enjeu

Un SI maintenable doit être reproductible.

Les configurations permanentes ne doivent pas dépendre de manipulations manuelles non tracées.

## Orientation

Conserver Git comme source de vérité et automatiser la livraison.

Le flux stratégique est :

```text
Code
 |
 v
GitLab
 |
 v
CI
 |
 v
Artifact / Image
 |
 v
GitOps desired state
 |
 v
Argo CD
 |
 v
Kubernetes
```

## Principes

- changements versionnés ;
- validation automatisée ;
- images immuables ;
- desired state dans Git ;
- réconciliation Argo CD ;
- séparation entre inspection runtime et changement permanent.

## Résultat attendu

Réduire :

- dérive de configuration ;
- changements non reproductibles ;
- erreurs manuelles ;
- différence entre documentation et runtime.

---

# 9. Axe stratégique S3 — Structurer et gouverner la chaîne Data

## Enjeu

La donnée traverse plusieurs responsabilités différentes.

Le flux réel est :

```text
Sources
   |
   v
RAW
   |
   v
STAGING
   |
   v
REAL_ESTATE
   |
   v
WAREHOUSE
   |
   v
ANALYTICS
```

`real_estate` représente le modèle métier OLTP.

`warehouse` et `analytics` répondent aux besoins décisionnels et analytiques.

## Orientation

Maintenir une séparation explicite entre :

- ingestion ;
- nettoyage ;
- données transactionnelles ;
- données analytiques ;
- metadata ;
- qualité ;
- lineage.

## Technologies déjà mobilisées

```text
PostgreSQL   -> persistence
Airflow      -> orchestration
dbt          -> transformations
OpenMetadata -> metadata / governance / lineage
```

## Résultat attendu

Obtenir une chaîne :

```text
Traçable
+
Testable
+
Documentée
+
Gouvernée
+
Exploitable
```

Cette orientation prépare directement les travaux d'architecture OLTP/OLAP de C3.

---

# 10. Axe stratégique S4 — Sécuriser, contrôler et auditer

## Enjeu

Les opérations métier doivent être attribuables et les droits doivent être maîtrisés.

## État actuel

L'application utilise :

- `real_estate.utilisateur` comme source d'identité applicative ;
- Argon2id pour le stockage des mots de passe ;
- JWT ;
- rôles applicatifs ;
- exécution backend non-root ;
- Kubernetes Secrets ;
- variables GitLab protégées ;
- journalisation métier dans `real_estate.audit_log`.

Les rôles applicatifs principaux sont :

```text
ADMIN
CLIENT
CHASSEUR
SERVICE
```

## Orientation

Faire évoluer progressivement la sécurité vers :

```text
Authentication
      +
Authorization
      +
Least Privilege
      +
Audit
      +
Secret Management
      +
Runtime Evidence
```

## Limites actuelles

Le contrôle fin de propriété des ressources reste incomplet.

La couverture de l'audit doit également être étendue progressivement à d'autres opérations sensibles.

Keycloak et HashiCorp Vault constituent des évolutions possibles, mais ne sont pas présentés comme des composants actuellement déployés du projet.

## Résultat attendu

Passer d'une sécurité principalement applicative et déclarative à une sécurité davantage :

```text
Enforced
+
Observable
+
Auditable
```

---

# 11. Axe stratégique S5 — Faire évoluer progressivement le matching vers le ML/IA

## Enjeu

Le cœur métier nécessite de sélectionner des biens compatibles avec une demande client.

Certaines règles sont déterministes et ne doivent pas être remplacées arbitrairement par un modèle probabiliste.

## Principe

Le modèle stratégique est :

```text
Demande
   |
   v
Hard Eligibility
   |
   v
Population éligible
   |
   v
Ranking
   |
   v
Recommendation
   |
   v
Presentation
```

Les critères d'éligibilité métier restent déterministes.

Le ML peut intervenir sur des fonctions adaptées telles que :

- ranking ;
- estimation de pertinence ;
- apprentissage à partir de données labellisées ;
- analyse ;
- assistance ;
- explicabilité.

## État actuel

Le projet dispose :

- d'un baseline de matching déterministe pondéré ;
- de datasets d'entraînement/validation ;
- d'un environnement MLflow ;
- de pipelines d'évaluation ;
- d'une infrastructure GPU locale ;
- d'Ollama/Qwen pour l'inférence locale expérimentale.

Le GPU et les LLM locaux ne constituent pas actuellement le moteur de matching de production.

## Orientation

La progression doit suivre :

```text
Baseline déterministe
       |
       v
Dataset contrôlé
       |
       v
Training
       |
       v
Evaluation
       |
       v
Comparaison au baseline
       |
       v
Décision
       |
       v
Intégration éventuelle
```

## Résultat attendu

L'IA doit améliorer une capacité mesurable du SI.

Elle ne doit pas être introduite uniquement pour augmenter artificiellement la complexité du projet.

---

# 12. Axe stratégique S6 — Maîtriser la complexité et les ressources

## Enjeu

Le SI fonctionne sur une infrastructure réelle et limitée.

La maturité architecturale ne doit pas être mesurée au nombre de technologies installées.

## Principe

```text
Besoin
  |
  v
Capacité existante suffisante ?
  |
  +---- OUI ----> Réutiliser
  |
  +---- NON ----> Évaluer
                    |
                    v
              Alternatives
                    |
                    v
             Décision / ADR
                    |
                    v
              Implémentation
```

## Conséquences

Les technologies suivantes ne sont pas considérées comme nécessaires sans besoin démontré :

- Kafka ;
- Service Mesh ;
- Kubeflow ;
- Qdrant ;
- Spark ;
- Iceberg ;
- Trino ;
- Databricks ;
- Snowflake ;
- RAG ;
- architecture multi-cluster.

Certaines peuvent devenir pertinentes ultérieurement.

Elles restent cependant **DEFERRED / REQUIREMENT-DRIVEN** tant qu'un besoin mesurable ne les justifie pas.

## Résultat attendu

Conserver une architecture :

```text
Compréhensible
+
Maintenable
+
Exploitable
+
Justifiable
```

---

# 13. Priorisation stratégique

Les évolutions ne sont pas toutes de même priorité.

La stratégie utilise quatre facteurs principaux :

```text
Priorité
=
Valeur métier
+
Réduction du risque
+
Dépendances
+
Faisabilité
```

La disponibilité d'une technologie ou son intérêt pédagogique ne suffit pas à lui donner une priorité élevée.

---

# 14. Matrice de priorisation

| Priorité | Orientation | Justification |
|---|---|---|
| P1 | Fiabilité / PRA | Protection des données et continuité |
| P1 | Sécurité / audit | Protection et traçabilité des opérations |
| P1 | Data Quality / lineage | Confiance dans les données |
| P1 | CI / GitOps | Reproductibilité du SI |
| P1 | Evidence certification | Démonstration des capacités réellement acquises |
| P2 | ML de matching | Amélioration mesurable du ranking |
| P2 | Gouvernance automatisée | Réduction des contrôles manuels |
| P2 | SLO / alerting | Passage du monitoring au pilotage de fiabilité |
| P3 | Extensions IA | Selon besoin démontré |
| P3/P4 | Nouvelles plateformes | Seulement après justification |

---

# 15. Trajectoire SI

La trajectoire retenue est progressive.

## Étape 1 — Consolider

```text
Audit
Risk Register
Documentation
Tests
PRA
Security
Evidence
```

## Étape 2 — Industrialiser

```text
CI
GitOps
Automated Quality
Observability
Governance
```

## Étape 3 — Exploiter la Data

```text
OLTP
   |
   v
Warehouse
   |
   v
Analytics
   |
   v
Decision Support
```

## Étape 4 — Faire évoluer le ML

```text
Deterministic Baseline
        |
        v
Training Dataset
        |
        v
ML Experiment
        |
        v
Evaluation
        |
        v
Controlled Integration
```

## Étape 5 — Étendre uniquement sur besoin

Les nouvelles briques sont évaluées lorsqu'une limite mesurée du système existant apparaît.

---

# 16. CURRENT / SHORT TERM / TARGET / DEFERRED

La stratégie distingue explicitement les niveaux de maturité.

## CURRENT

Capacités réellement disponibles dans le projet :

- Kubernetes ;
- PostgreSQL ;
- FastAPI ;
- GitLab CI ;
- GitOps ;
- Argo CD ;
- Airflow ;
- dbt ;
- OpenMetadata ;
- MLflow ;
- MinIO ;
- Prometheus ;
- Grafana ;
- Loki ;
- Tempo ;
- OpenTelemetry ;
- matching déterministe ;
- authentification et RBAC applicatifs ;
- audit métier partiel ;
- sauvegarde PostgreSQL ;
- restauration PostgreSQL validée ;
- infrastructure GPU locale ;
- Ollama/Qwen expérimental.

## SHORT TERM

Priorités de consolidation :

- compléter les preuves de certification ;
- étendre la couverture d'audit ;
- renforcer le contrôle d'accès fin ;
- renforcer les alertes PRA ;
- formaliser rétention des backups ;
- poursuivre Data Quality et lineage ;
- entraîner et comparer le modèle ML ;
- compléter les mesures de performance.

## TARGET

Évolutions justifiées à terme :

- sécurité plus fortement automatisée ;
- gouvernance davantage machine-readable ;
- SLOs sur services critiques ;
- évaluation ML systématique ;
- promotion contrôlée des modèles ;
- recovery testing plus automatisé ;
- meilleure traçabilité exigence → contrôle → runtime.

## DEFERRED / REQUIREMENT-DRIVEN

- RAG ;
- Kafka ;
- Kubeflow ;
- Service Mesh ;
- Qdrant ;
- architecture multi-cluster ;
- lakehouse distribué ;
- Databricks/Snowflake ou équivalents.

---

# 17. Contraintes stratégiques

## Infrastructure

Le projet doit exploiter l'infrastructure disponible avant de demander davantage de ressources.

Les contraintes concernent notamment :

- CPU ;
- RAM ;
- stockage ;
- réseau ;
- GPU ;
- VRAM.

## Exploitation

Le SI doit rester administrable avec une équipe réduite.

Une solution plus sophistiquée n'est pas automatiquement une meilleure solution.

## Souveraineté

La plateforme privilégie autant que possible le contrôle local de l'infrastructure, des données et des traitements.

L'inférence locale constitue une capacité intéressante pour les cas d'usage IA nécessitant cette maîtrise.

## Certification

L'architecture doit également permettre de démontrer les compétences du référentiel à partir de preuves réelles.

La certification ne justifie toutefois pas de présenter comme opérationnelle une technologie qui ne l'est pas.

---

# 18. Relation avec les risques

La stratégie est directement liée au registre des risques.

Exemples :

| Risque | Réponse stratégique |
|---|---|
| Perte/corruption PostgreSQL | S1 — PRA et restauration |
| Backup non détecté ou obsolète | S1 — monitoring et alerting |
| Incohérence réseau/DNS | S1 — fiabilisation infrastructure |
| Exposition de secrets | S4 — sécurité |
| Autorisation fine incomplète | S4 — RBAC / ownership |
| Audit incomplet | S4 — extension audit trail |
| Confiance excessive dans la DQ | S3 — preuves et contrôles |
| Confusion ML expérimental / production | S5 — gouvernance ML |
| Expansion technologique excessive | S6 — contrôle de complexité |
| Preuves certification insuffisantes | pilotage evidence-driven |

La stratégie est donc **risk-driven** autant que technology-driven.

---

# 19. Relation avec les compétences BC01 suivantes

C2 définit la direction.

Les compétences suivantes démontrent les choix architecturaux nécessaires pour mettre cette direction en œuvre.

```text
C1
Audit du SI
   |
   v
C2
Stratégie SI
   |
   +----------------------+
   |          |           |
   v          v           v
C3           C4          C5
OLTP/OLAP    Composants   Décisions
                         Architecture
   \          |           /
    \         |          /
     +--------+---------+
              |
              v
             C6
        Eco-conception
```

Ainsi, C2 ne duplique pas les décisions détaillées de C3 à C6.

Il explique **pourquoi le SI doit évoluer dans ces directions**.

---

# 20. Indicateurs de réussite

La stratégie doit pouvoir être évaluée.

Les indicateurs pertinents comprennent :

| Domaine | Indicateur |
|---|---|
| Fiabilité | restauration démontrée |
| Déploiement | changements permanents via CI/GitOps |
| Data | tests, lineage et metadata disponibles |
| API | disponibilité, erreurs, latence |
| Matching | population éligible et recommandations mesurées |
| ML | métriques d'évaluation enregistrées |
| Sécurité | identité, rôle et audit vérifiables |
| PRA | backup + restore + validation |
| Gouvernance | risques et décisions traçables |
| Certification | preuve reliée à chaque compétence |

Les objectifs numériques ne doivent être annoncés comme atteints que lorsqu'ils sont effectivement mesurés et prouvés.

---

# 21. Arbitrages stratégiques

Plusieurs arbitrages structurants sont retenus.

## Kubernetes plutôt qu'une multiplication de plateformes d'exécution

La plateforme Kubernetes existante est réutilisée pour les workloads applicatifs, Data et MLOps lorsque cela est pertinent.

## PostgreSQL avant l'introduction de nouvelles bases

PostgreSQL couvre actuellement les besoins OLTP, warehouse et analytics du projet.

Une nouvelle technologie de stockage ne doit être introduite qu'en présence d'une limite démontrée.

## MLflow plutôt que Kubeflow à ce stade

MLflow répond aux besoins actuels d'expérimentation, de métriques, de paramètres et d'artefacts ML avec une complexité opérationnelle compatible avec le projet.

Kubeflow reste non requis tant qu'un besoin supplémentaire n'est pas établi.

## Matching hybride plutôt que ML intégral

Les règles métier obligatoires restent déterministes.

Le ML est réservé aux problèmes pour lesquels une approche statistique apporte une valeur mesurable.

## Infrastructure locale plutôt qu'une dépendance cloud imposée

L'infrastructure existante permet de démontrer les capacités du projet tout en conservant le contrôle sur les données, les déploiements et les ressources.

---

# 22. Ce que la stratégie ne cherche pas à faire

La stratégie SI ne cherche pas à :

- maximiser le nombre de technologies ;
- reproduire artificiellement une architecture hyperscale ;
- migrer vers le cloud sans besoin ;
- remplacer des règles métier déterministes par de l'IA ;
- multiplier les bases de données ;
- ajouter un second orchestrateur sans nécessité ;
- ajouter un second système de monitoring ;
- déployer des composants uniquement pour les citer à la soutenance.

Le principe directeur reste :

```text
Minimum Necessary Complexity
```

---

# 23. Traçabilité besoin → stratégie

| Besoin / constat | Orientation stratégique |
|---|---|
| Processus métier de chasse immobilière | SI centré Client / Demande / Matching / Présentation / Visite |
| Données issues de plusieurs étapes | S3 — chaîne Data structurée |
| Besoin de recommandations | S5 — matching déterministe puis ML contrôlé |
| Besoin de traçabilité | S4 — audit et identité |
| Risque de perte de données | S1 — PRA |
| Déploiements reproductibles | S2 — CI/GitOps |
| Infrastructure limitée | S6 — maîtrise de la complexité |
| Besoin analytique | S3 — OLTP → Warehouse → Analytics |
| Besoin de disponibilité | S1 — observabilité et reprise |
| Besoin d'évolution IA | S5 — expérimentation et évaluation avant intégration |

---

# 24. Traçabilité stratégie → architecture

| Axe | Architecture / mécanisme principal |
|---|---|
| S1 — Fiabilité | Kubernetes, Prometheus, Grafana, PRA PostgreSQL/MinIO |
| S2 — Industrialisation | GitLab CI, registry, GitOps, Argo CD |
| S3 — Data | PostgreSQL, Airflow, dbt, OpenMetadata |
| S4 — Sécurité | Auth applicative, RBAC, audit_log, Secrets |
| S5 — ML/IA | Matching baseline, MLflow, datasets, GPU local |
| S6 — Complexité | ADR, réutilisation, technology gate |

Les décisions détaillées et leurs alternatives seront consolidées dans les compétences suivantes.

---

# 25. État de la stratégie

| Élément | Statut |
|---|---|
| Audit SI source | EVIDENCED |
| Besoin métier | DOCUMENTED |
| Risques | IMPLEMENTED / DOCUMENTED |
| Axes stratégiques | DOCUMENTED |
| Priorisation | DOCUMENTED |
| Trajectoire SI | DOCUMENTED |
| Architecture actuelle | IMPLEMENTED |
| GitOps / CI | DEPLOYED |
| PRA PostgreSQL | RUNTIME-VERIFIED |
| Sécurité applicative | IMPLEMENTED / TESTED |
| Audit métier | IMPLEMENTED / PARTIAL COVERAGE |
| Matching déterministe | IMPLEMENTED / TESTED |
| ML expérimental | IMPLEMENTED / EVALUATION PATH |
| GPU / LLM local | RUNTIME-VALIDATED / EXPERIMENTAL |
| Technologies différées | DEFERRED |

---

# 26. Preuves pour le jury

La démonstration de C2 s'appuie sur :

```text
C1 Audit SI
     +
Risk Register
     +
Business Objectives
     +
Architecture Roadmap
     +
Architecture Decisions
     +
Runtime Evidence
```

Le jury doit pouvoir comprendre :

1. d'où part le SI ;
2. quels problèmes et risques ont été identifiés ;
3. pourquoi certaines évolutions sont prioritaires ;
4. pourquoi certaines technologies sont retenues ;
5. pourquoi d'autres sont différées ;
6. comment la trajectoire reste cohérente avec les besoins métier ;
7. comment les choix peuvent être vérifiés dans le projet réel.

---

# 27. Critère de réussite

La compétence C2 est démontrée si la chaîne suivante est explicite :

```text
Audit du SI
    |
    v
Constats
    |
    v
Risques / écarts
    |
    v
Enjeux
    |
    v
Orientations stratégiques
    |
    v
Priorités
    |
    v
Trajectoire
    |
    v
Architecture
```

et si cette trajectoire est cohérente avec :

```text
Business
+
Data
+
Security
+
Operations
+
AI
+
Infrastructure Constraints
```

---

# 28. Conclusion

La stratégie SI du projet **Chasse Immobilière** ne repose pas sur une refonte complète du système existant.

Le projet dispose déjà d'une base technique importante.

La stratégie consiste donc à faire évoluer cette base de manière contrôlée :

```text
SI EXISTANT
    |
    v
CONSOLIDER
    |
    v
FIABILISER
    |
    v
SÉCURISER
    |
    v
GOUVERNER
    |
    v
INDUSTRIALISER
    |
    v
MESURER
    |
    v
FAIRE ÉVOLUER
```

Cette trajectoire permet de construire progressivement un SI :

```text
Fiable
+
Reproductible
+
Gouverné
+
Sécurisé
+
Observable
+
Recoverable
+
Data-driven
+
AI-ready
```

sans confondre maturité architecturale et accumulation technologique.

---

**BC01 / C2 — Stratégie SI : EVIDENCED**
