# BC02 — C4 — Processus métier

**Bloc de compétences :** BC02  
**Compétence :** C4 — Modéliser et formaliser les processus métier soutenus par le système d'information  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Baseline documentaire — processus détaillés à consolider avec les cas d'usage réels

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves démontrant que les processus métier ont été identifiés et reliés :

- aux utilisateurs ;
- aux données ;
- aux applications ;
- aux traitements ;
- aux contrôles ;
- aux décisions ;
- aux services AI ;
- aux preuves attendues.

Le modèle général est :

```text
Actor
  |
  v
Business Need
  |
  v
Business Process
  |
  v
Information / Data
  |
  v
Application Service
  |
  v
Automation
  |
  v
Business Outcome
```

L'objectif n'est pas uniquement de représenter les composants techniques.

Il faut montrer :

> Comment le système soutient réellement un processus métier.

---

# 2. Sources de référence

Les documents principaux sont :

```text
../../../10-BUSINESS/01-Business-Architecture.md
../../../20-APPLICATION/01-Application-Architecture.md
../../../40-DATA/01-Data-Architecture.md
../../../40-DATA/02-Data-Model.md
../../../50-AI/01-AI-Platform-Architecture.md
../../../50-AI/04-RAG-Architecture.md
```

Sources Foundation :

```text
../../../00-FOUNDATION/02-Project-Vision.md
../../../00-FOUNDATION/03-Business-Objectives.md
../../../00-FOUNDATION/Enterprise-AI-Platform.md
```

Diagrammes utiles :

```text
../../../99-DIAGRAMS/01-Enterprise-Context.puml
../../../99-DIAGRAMS/02-Enterprise-Platform-Architecture.puml
../../../99-DIAGRAMS/06-Application-Architecture.puml
../../../99-DIAGRAMS/07-Data-Architecture.puml
../../../99-DIAGRAMS/08-AI-Architecture.puml
```

---

# 3. Principe de modélisation

Le projet distingue :

```text
BUSINESS PROCESS
       !=
TECHNICAL WORKFLOW
```

Exemple :

```text
Business Process:
Analyser une opportunité immobilière
```

n'est pas équivalent à :

```text
Technical Workflow:
Airflow DAG -> PostgreSQL -> dbt
```

Le second soutient le premier.

---

# 4. Niveaux de processus

Les processus peuvent être représentés à plusieurs niveaux.

## Niveau 0 — Value Stream

Exemple :

```text
Identifier une opportunité
        |
        v
Collecter l'information
        |
        v
Analyser
        |
        v
Qualifier
        |
        v
Décider
```

## Niveau 1 — Processus métier

Exemple :

```text
Collecter les données immobilières
```

## Niveau 2 — Activités

Exemple :

```text
Recherche
Extraction
Validation
Enrichissement
Classification
```

## Niveau 3 — Tâches techniques

Exemple :

```text
API Call
SQL Query
ETL
RAG Retrieval
Model Inference
```

---

# 5. Acteurs principaux

Les rôles métier et techniques concernés peuvent inclure :

```text
Business User
Analyst
Administrator
Data Engineer
AI / MLOps Engineer
Platform / DevOps Engineer
Security
Governance
```

Les rôles ne doivent pas être confondus avec des personnes physiques uniques.

Une même personne peut exercer plusieurs responsabilités dans le contexte du projet.

---

# 6. Processus métier principal

Un processus cible générique du projet est :

```text
Need
 |
 v
Search / Acquire Information
 |
 v
Validate Information
 |
 v
Store / Centralize
 |
 v
Enrich
 |
 v
Analyse
 |
 v
AI Assistance
 |
 v
Business Decision
```

Ce processus permet de relier les capacités :

```text
Application
Data
AI
Governance
```

---

# 7. Processus — Collecte de données

## Objectif

Acquérir des données nécessaires au traitement métier.

## Entrées

```text
Business Sources
Files
APIs
Operational Sources
Documents
```

## Processus

```text
Source
  |
  v
Acquire
  |
  v
Validate
  |
  v
Load
```

## Sortie

```text
RAW data
```

## Support technique

```text
Apache Airflow
PostgreSQL
```

---

# 8. Processus — Standardisation

## Objectif

Transformer les données collectées en représentation exploitable.

Processus :

```text
RAW
 |
 v
Type validation
 |
 v
Cleaning
 |
 v
Normalization
 |
 v
Deduplication
 |
 v
STAGING
```

Support :

```text
dbt
PostgreSQL
Data Quality
```

---

# 9. Processus — Intégration métier

## Objectif

Construire une représentation cohérente pour l'analyse.

Processus :

```text
STAGING
   |
   v
Business Rules
   |
   v
Integration
   |
   v
Facts / Dimensions
   |
   v
WAREHOUSE
```

Cette étape transforme des données techniques en données métier intégrées.

---

# 10. Processus — Production analytique

## Objectif

Produire des données directement consommables.

```text
WAREHOUSE
    |
    v
Aggregation
    |
    v
KPI
    |
    v
ANALYTICS
```

Consommateurs :

```text
Business Application
Dashboard
Analyst
AI / ML
```

---

# 11. Processus — Recherche métier

Un utilisateur peut rechercher une information.

```text
User
 |
 v
Search Request
 |
 v
Business Application
 |
 v
Structured / Document Search
 |
 v
Results
 |
 v
Business Decision
```

Le système doit fournir une information :

- pertinente ;
- traçable ;
- accessible selon les droits ;
- issue de sources gouvernées.

---

# 12. Processus — Assistance AI

L'AI intervient comme capacité d'assistance.

```text
User Request
     |
     v
Application
     |
     v
AI Service
     |
     +------------------+
     |                  |
     v                  v
Direct Inference      RAG
     |                  |
     +--------+---------+
              |
              v
         Local LLM
              |
              v
           Response
```

Le traitement AI n'est pas considéré comme une source de vérité autonome.

---

# 13. Processus RAG

Lorsque le besoin nécessite un contexte documentaire :

```text
User
 |
 v
Question
 |
 v
Authorization
 |
 v
Retrieve Allowed Knowledge
 |
 v
Build Context
 |
 v
LLM
 |
 v
Response
 |
 v
Validation / User Review
```

Principe important :

```text
Vector Access
must respect
Business Authorization
```

---

# 14. Processus — Gouvernance Data

Chaque asset important suit progressivement un cycle de gouvernance.

```text
Dataset
  |
  v
Discover
  |
  v
Catalog
  |
  v
Assign Owner
  |
  v
Classify
  |
  v
Profile
  |
  v
Validate Quality
  |
  v
Publish / Consume
```

Support :

```text
OpenMetadata
Git
Governance as Code
```

---

# 15. Processus — Data Quality

Le processus de Data Quality est :

```text
Define Rule
   |
   v
Version Rule
   |
   v
Execute Test
   |
   v
Collect Result
   |
   +--------+
   |        |
 PASS      FAIL
   |        |
   v        v
Publish   Investigate
            |
            v
         Correct
```

Le succès technique d'un pipeline ne signifie pas automatiquement que les données sont valides.

---

# 16. Processus — Model Lifecycle

Pour les modèles ML :

```text
Dataset
  |
  v
Training
  |
  v
Experiment
  |
  v
Evaluation
  |
  v
Model Candidate
  |
  v
Governance Gate
  |
  v
Registry
  |
  v
Deployment
  |
  v
Monitoring
```

Support :

```text
Airflow
MLflow
Git
Observability
```

---

# 17. Processus — Déploiement applicatif

Le processus de livraison suit :

```text
Developer
   |
   v
Git Commit
   |
   v
Merge Request
   |
   v
CI
   |
   v
Validation
   |
   v
GitOps Repository
   |
   v
Argo CD
   |
   v
Kubernetes
```

Le processus technique contribue au processus métier en garantissant des services reproductibles.

---

# 18. Processus — Changement

Les changements structurants suivent :

```text
Need for Change
      |
      v
Impact Analysis
      |
      v
Decision
      |
      v
Implementation
      |
      v
Test
      |
      v
Deployment
      |
      v
Observation
```

Les changements d'architecture importants doivent également produire ou mettre à jour un ADR.

---

# 19. Processus — Incident

```text
Incident
   |
   v
Detect
   |
   v
Alert
   |
   v
Diagnose
   |
   v
Mitigate
   |
   v
Recover
   |
   v
Analyse Root Cause
   |
   v
Improve
```

Ce processus est supporté par :

```text
Prometheus
Grafana
Loki
Tempo
OpenTelemetry
Runbooks
```

---

# 20. Processus — Backup

```text
Protected State
      |
      v
Backup
      |
      v
Backup Storage
      |
      v
Verification
```

Le backup seul ne clôt pas le processus.

---

# 21. Processus — Restore

```text
Recovery Need
      |
      v
Select Recovery Point
      |
      v
Restore
      |
      v
Validate
      |
      v
Measure RPO / RTO
      |
      v
Evidence
```

Il s'agit d'un processus métier/opérationnel critique.

---

# 22. Processus — Gestion des risques

```text
Identify
  |
  v
Assess
  |
  v
Prioritize
  |
  v
Treat
  |
  v
Monitor
  |
  v
Reassess
```

Les risques peuvent générer des éléments de backlog.

---

# 23. Processus — Décision architecture

```text
Problem
  |
  v
Options
  |
  v
Evaluation
  |
  v
Decision
  |
  v
ADR
  |
  v
Implementation
  |
  v
Review
```

Ce processus empêche les décisions implicites.

---

# 24. Processus — Governance as Code

```text
Governance Requirement
        |
        v
Control
        |
        v
Machine-Readable Definition
        |
        v
Git
        |
        v
CI
        |
        v
Runtime Enforcement
        |
        v
Evidence
```

Il transforme progressivement les processus de gouvernance manuels en contrôles industrialisés.

---

# 25. Entrées / sorties des processus

Chaque processus doit pouvoir préciser :

```text
Input
Process
Output
Actor
System
Control
Evidence
```

Exemple :

| Élément | Valeur |
|---|---|
| Input | Source dataset |
| Process | Data ingestion |
| Output | RAW table |
| Actor | Data Engineer |
| System | Airflow/PostgreSQL |
| Control | Schema validation |
| Evidence | DAG + row count |

---

# 26. Exemple complet — Pipeline Data

```text
Business Source
      |
      v
Airflow Ingestion
      |
      v
RAW
      |
      v
dbt Staging
      |
      v
STAGING
      |
      v
dbt Warehouse
      |
      v
WAREHOUSE
      |
      v
Quality Tests
      |
      v
ANALYTICS
      |
      v
Business Consumer
```

Contrôles transverses :

```text
OpenMetadata
Data Quality
Observability
Security
```

---

# 27. Exemple complet — Processus AI

```text
Business User
     |
     v
Application
     |
     v
AI Request
     |
     v
Data Classification
     |
     v
Permitted Data
     |
     v
RAG / Prompt
     |
     v
Ollama / Qwen
     |
     v
Response
     |
     v
Human / Business Decision
```

---

# 28. Automatisation des processus

L'objectif d'automatisation n'est pas :

```text
Automate Everything
```

mais :

```text
Automate Repeatable
Deterministic
High-Value Steps
```

Les décisions nécessitant du jugement humain restent humaines.

---

# 29. Points de contrôle

Les processus peuvent comporter des contrôles tels que :

```text
Authentication
Authorization
Data Quality
Schema Validation
Approval
Policy Validation
Risk Review
Human Oversight
```

---

# 30. Points de décision

Les processus ne sont pas nécessairement linéaires.

Exemple :

```text
Data Quality
    |
    v
Passed?
 +--+--+
 |     |
YES    NO
 |     |
 v     v
Publish Correct
```

---

# 31. Traçabilité données

Un processus métier doit pouvoir remonter jusqu'à ses données.

```text
Business Output
       |
       v
Analytics Dataset
       |
       v
Warehouse
       |
       v
Staging
       |
       v
Raw
       |
       v
Source
```

Cette traçabilité est supportée par OpenMetadata.

---

# 32. Traçabilité décisions

Pour les décisions significatives :

```text
Business Need
      |
      v
Requirement
      |
      v
Architecture Decision
      |
      v
ADR
      |
      v
Implementation
```

---

# 33. Traçabilité technique

```text
Process Step
    |
    v
Technical Component
    |
    v
Implementation
    |
    v
Runtime Evidence
```

Exemple :

```text
Transform Data
     |
     v
dbt
     |
     v
dbt Model
     |
     v
Test Result
```

---

# 34. Données manipulées

Les processus doivent identifier les catégories de données qu'ils manipulent.

Exemples :

- données immobilières ;
- données de référence ;
- données utilisateur ;
- documents ;
- données analytiques ;
- métadonnées ;
- données techniques ;
- logs ;
- métriques ;
- données ML.

---

# 35. RGPD dans les processus

Lorsqu'un processus manipule des données personnelles :

```text
Process
  |
  v
Personal Data?
 +---+---+
 |       |
NO      YES
 |       |
 v       v
Continue RGPD Controls
```

Les contrôles peuvent inclure :

- finalité ;
- minimisation ;
- rétention ;
- accès ;
- suppression ;
- sécurité.

---

# 36. Accessibilité dans les processus

Les processus impliquant une interface utilisateur doivent considérer les utilisateurs en situation de handicap.

Exemples :

```text
Search
Forms
Navigation
Results
Error Messages
```

Le processus ne doit pas dépendre exclusivement :

- de la souris ;
- de la couleur ;
- d'une représentation visuelle non expliquée.

---

# 37. Diagrammes associés

Les diagrammes déjà disponibles fournissent plusieurs vues des processus.

```text
../../../99-DIAGRAMS/01-Enterprise-Context.puml
../../../99-DIAGRAMS/06-Application-Architecture.puml
../../../99-DIAGRAMS/07-Data-Architecture.puml
../../../99-DIAGRAMS/08-AI-Architecture.puml
../../../99-DIAGRAMS/09-MLOps-Architecture.puml
../../../99-DIAGRAMS/10-DevOps-GitOps-Architecture.puml
../../../99-DIAGRAMS/14-Backup-DR-Architecture.puml
```

---

# 38. Processus à détailler pendant l'implémentation métier

## Parcours immobilier actuellement soutenu

```text
Client
  |
  v
Demande / DemandeVersion
  |
  v
Mandat lorsque nécessaire
  |
  v
Recherche de biens actifs
  |
  v
Matching déterministe
  |
  v
Présentation
  |
  v
Visite / compte rendu
```

La demande peut précéder la signature du mandat. La migration 005 rend `demande.id_mandat` facultatif ; elle ne démontre pas à elle seule un workflow complet de rattachement ultérieur.

| Étape | Acteur / déclencheur | Donnée produite | Contrôle |
|---|---|---|---|
| Formaliser le besoin | Utilisateur autorisé de l'API | Demande et version des critères | Schémas et validations du service |
| Recommander | ADMIN, CHASSEUR ou SERVICE | Présentation liée à une version et un bien | Candidats actifs, score, gestion des présentations existantes |
| Suivre la visite | ADMIN ou CHASSEUR | Visite et compte rendu | Présentation existante, validations et audit |
| Auditer | Mutation métier | `audit_log` | Acteur authentifié et contexte de l'opération |

## Preuve métier disponible

Le rapport du 9 septembre 2026 décrit une recommandation sur la version 56 : 200 candidats éligibles, un candidat sélectionné, une présentation créée et une ligne d'audit correspondante. Il relie la requête API, la présentation 31 et l'audit 7.

```text
../../../60-SECURITY/RECOMMENDATION-AUDIT-RUNTIME-EVIDENCE.md
../../03-BC03/C6-Tests-Executes/visite-audit-2026-09-09/README.md
```

## Processus restant à consolider

La rémunération, la validité/renouvellement des mandats et la recette intégrée restent des travaux métier identifiés dans la revue StarterPack du 9 septembre. Les processus AI/RAG décrits plus haut conservent leur statut de cible lorsqu'ils ne correspondent pas au matching actuellement exécuté.

Exemples complémentaires :

Exemples :

```text
Property Search
Property Qualification
Document Analysis
Opportunity Scoring
Business Validation
AI-assisted Search
```

Ils ne doivent pas être déclarés implémentés tant que l'application correspondante n'est pas disponible.

---

# 39. Artefacts complémentaires possibles

Selon les besoins, ce dossier pourra recevoir :

```text
01-business-process.puml
02-data-process.puml
03-ai-assisted-process.puml
04-deployment-process.puml
05-incident-process.puml
```

Cependant, les diagrammes doivent apporter une preuve supplémentaire et ne pas simplement reproduire les 14 diagrammes existants.

---

# 40. Critères de qualité d'un processus

Un processus est correctement défini s'il précise :

- objectif ;
- acteur ;
- déclencheur ;
- entrée ;
- activités ;
- contrôles ;
- décisions ;
- sortie ;
- systèmes utilisés ;
- donnée manipulée ;
- preuve.

---

# 41. Matrice processus → architecture

| Processus | Application | Data | AI | Platform |
|---|---|---|---|---|
| Collecte | API / Jobs | Airflow / RAW | - | Kubernetes |
| Transformation | - | dbt | - | Kubernetes |
| Analytics | API | Warehouse | Possible | Kubernetes |
| Recherche | API | PostgreSQL | RAG possible | Kubernetes |
| AI assistance | API | Governed data | Ollama/Qwen | AI host |
| Model lifecycle | - | Dataset | MLflow | Kubernetes |
| Deployment | Service | - | - | GitLab/Argo CD |
| Monitoring | - | - | - | Observability |
| Recovery | Services | Data restore | AI restore | Platform |

---

# 42. Matrice processus → contrôle

| Processus | Contrôle principal |
|---|---|
| Ingestion | Validation |
| Transformation | Data Quality |
| Analytics | Ownership |
| AI | AI Governance |
| RAG | Authorization |
| Deployment | CI / GitOps |
| Runtime | Observability |
| Backup | Backup validation |
| Restore | Functional validation |
| Governance | Audit evidence |

---

# 43. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Actor
 |
 v
Need
 |
 v
Business Process
 |
 v
Data / Information
 |
 v
Application / Platform
 |
 v
Control
 |
 v
Output
```

et comprendre comment la solution informatique soutient le processus métier.

---

# 44. Statut actuel

| Élément | Statut |
|---|---|
| Processus généraux | DOCUMENTÉS |
| Processus Data | DOCUMENTÉS |
| Processus AI | DOCUMENTÉS |
| Processus MLOps | DOCUMENTÉS |
| Processus GitOps | DOCUMENTÉS |
| Processus Incident | DOCUMENTÉS |
| Processus Backup/Restore | DOCUMENTÉS |
| Governance process | DOCUMENTÉ |
| Processus immobilier détaillé | PARCOURS ACTUEL DOCUMENTÉ / SUITE COMMERCIALE À COMPLÉTER |
| BPMN métier spécifique | À PRODUIRE SI REQUIS |
| Preuves application métier | RECOMMANDATION AUDITÉE DOCUMENTÉE / RECETTE GLOBALE À CONSOLIDER |

---

# 45. Conclusion

La modélisation des processus permet de relier :

```text
Business
   |
   v
Process
   |
   v
Data
   |
   v
Application
   |
   v
Platform
   |
   v
Evidence
```

Cette approche évite de construire une plateforme déconnectée du fonctionnement métier.

---

**BC02 / C4 — Processus métier : DOCUMENTATION BASELINE COMPLETE**
