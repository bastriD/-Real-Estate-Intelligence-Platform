# BC02 — C1 — Étude d’opportunité

**Bloc de compétences :** BC02  
**Compétence :** C1 — Étudier l’opportunité d’un projet informatique  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Documentation baseline complete

---

# 1. Objectif

Ce dossier rassemble les preuves démontrant que le projet répond à une opportunité métier réelle et que la solution proposée est cohérente avec :

- les besoins utilisateurs ;
- les contraintes métier ;
- les contraintes techniques ;
- les risques ;
- les coûts d’exploitation ;
- la sécurité ;
- la gouvernance ;
- les bénéfices attendus.

L’étude d’opportunité répond à la question :

> Pourquoi ce projet doit-il être réalisé et quelle valeur apporte-t-il ?

---

# 2. Contexte métier

Le projet s’inscrit dans un contexte où les équipes métier doivent manipuler :

- des informations immobilières ;
- des documents ;
- des données structurées ;
- des informations métier dispersées ;
- des tâches de recherche ;
- des tâches d’analyse ;
- des processus répétitifs.

Une partie importante de ces activités peut nécessiter :

- des recherches manuelles ;
- des consolidations de données ;
- des copies entre systèmes ;
- des traitements Excel ;
- des contrôles manuels ;
- des recherches documentaires ;
- des analyses répétitives.

L’opportunité consiste à construire une plateforme permettant de centraliser, industrialiser et enrichir ces usages.

---

# 3. Problématique

Le fonctionnement manuel ou fragmenté crée plusieurs difficultés potentielles :

```text
Multiple Data Sources
        |
        v
Manual Processing
        |
        v
Duplicated Work
        |
        v
Inconsistent Information
        |
        v
Limited Traceability
        |
        v
Operational Risk
```

Les principaux problèmes adressés sont :

- dispersion de l’information ;
- répétition de tâches manuelles ;
- faible traçabilité ;
- difficulté de centralisation ;
- difficulté de réutilisation de la donnée ;
- faible automatisation ;
- absence de gouvernance homogène ;
- difficulté à exploiter l’IA de manière contrôlée.

---

# 4. Opportunité

L’opportunité consiste à transformer ces activités en une plateforme structurée.

La cible recherchée est :

```text
Sources métier
      |
      v
Centralisation
      |
      v
Transformation
      |
      v
Data Governance
      |
      v
Analytics
      |
      v
AI / RAG
      |
      v
Business Services
```

La plateforme permet de créer une base commune pour :

- automatisation ;
- Data Engineering ;
- analytics ;
- AI ;
- RAG ;
- observabilité ;
- gouvernance.

---

# 5. Bénéfices attendus

## 5.1 Réduction des tâches manuelles

La centralisation et l’automatisation permettent de réduire :

- les copies manuelles ;
- les transformations répétitives ;
- les opérations non reproductibles ;
- les contrôles manuels.

---

## 5.2 Traçabilité

Les traitements deviennent :

- versionnés ;
- observables ;
- auditables ;
- reproductibles.

Le modèle cible est :

```text
Source
  |
  v
Pipeline
  |
  v
Transformation
  |
  v
Output
  |
  v
Evidence
```

---

## 5.3 Qualité des données

La plateforme permet d’introduire :

- tests ;
- profiling ;
- lineage ;
- ownership ;
- classification ;
- Data Quality.

---

## 5.4 Exploitation de l’IA

L’IA peut être utilisée sur des données gouvernées plutôt que sur des fichiers dispersés.

```text
Governed Data
      |
      v
RAG / AI
      |
      v
Business Assistance
```

---

## 5.5 Souveraineté

L’utilisation d’une architecture local-first permet de réduire l’exposition externe des données.

```text
Enterprise Data
      |
      v
Local AI
```

est privilégié lorsque cela répond au besoin.

---

# 6. Parties prenantes

Les principales catégories de parties prenantes sont :

```text
Business Users
Management
Application Engineering
Data Engineering
AI / MLOps
Platform / DevOps
Security
Governance
Operations
```

Selon le contexte du projet, plusieurs rôles peuvent être portés par la même personne.

---

# 7. Besoins fonctionnels

Les besoins fonctionnels principaux comprennent :

- collecte d’informations ;
- recherche de données ;
- gestion de données métier ;
- consultation d’informations consolidées ;
- automatisation de traitements ;
- génération d’indicateurs ;
- exploitation de données analytiques ;
- exploitation future d’un moteur RAG ;
- assistance IA locale ;
- gestion documentaire.

---

# 8. Besoins non fonctionnels

La plateforme doit également répondre à des exigences non fonctionnelles.

## Performance

Les traitements doivent rester compatibles avec les volumes attendus.

## Disponibilité

Les services critiques doivent être récupérables et supervisés.

## Sécurité

L’accès doit être contrôlé.

## Confidentialité

Les données sensibles doivent rester gouvernées.

## Observabilité

Les principaux services doivent fournir :

```text
Metrics
Logs
Traces
Health
```

## Maintenabilité

L’architecture doit rester exploitable avec des ressources limitées.

## Reproductibilité

Les changements doivent être versionnés.

---

# 9. Contraintes techniques

Les principales contraintes sont :

- infrastructure physique existante ;
- ressources de calcul limitées ;
- capacité GPU limitée ;
- stockage limité ;
- environnement auto-hébergé ;
- nécessité d’éviter une complexité inutile ;
- besoin de garder la maîtrise de l’infrastructure.

Le projet doit donc respecter :

```text
Useful Capability
      +
Controlled Complexity
```

---

# 10. Contraintes AI

L’infrastructure AI actuelle repose sur des GPU de génération plus ancienne avec une VRAM limitée.

Conséquences :

- choix de modèles adaptés ;
- quantification ;
- limitation de la concurrence ;
- contrôle de la taille des modèles ;
- monitoring GPU ;
- utilisation raisonnée des workloads AI.

Cette contrainte renforce la nécessité d’une architecture réaliste.

---

# 11. Solutions envisagées

Plusieurs approches générales peuvent répondre au besoin.

## Option 1 — Fonctionnement manuel

```text
Files
Excel
Manual Processes
```

### Avantages

- faible investissement initial ;
- simplicité apparente.

### Limites

- faible industrialisation ;
- difficulté de gouvernance ;
- faible traçabilité ;
- duplication ;
- scalabilité limitée.

---

## Option 2 — Solution SaaS externe

### Avantages

- mise en service rapide ;
- infrastructure gérée.

### Limites

- dépendance fournisseur ;
- souveraineté ;
- coût ;
- gouvernance ;
- dépendance réseau ;
- réversibilité.

---

## Option 3 — Plateforme interne structurée

### Avantages

- maîtrise de l’architecture ;
- intégration des données ;
- automatisation ;
- gouvernance ;
- souveraineté ;
- réutilisation ;
- évolutivité.

### Limites

- besoin de compétences ;
- besoin d’exploitation ;
- complexité supérieure au fonctionnement manuel.

---

# 12. Solution retenue

La solution retenue est une plateforme interne basée sur :

```text
Kubernetes
+
GitOps
+
PostgreSQL
+
Airflow
+
dbt
+
OpenMetadata
+
MLflow
+
Ollama / Qwen
+
Observability
+
Governance as Code
```

Elle constitue un socle réutilisable plutôt qu’une solution monolithique spécifique à un seul besoin.

---

# 13. Pourquoi Kubernetes

Kubernetes permet :

- standardisation ;
- orchestration ;
- isolation ;
- GitOps ;
- self-healing ;
- déploiement reproductible.

Il est déjà intégré à l’environnement existant.

---

# 14. Pourquoi PostgreSQL

PostgreSQL fournit :

- persistence ;
- SQL ;
- analytics ;
- maturité ;
- extensions ;
- compatibilité avec les workloads Data.

Il évite de multiplier les bases sans justification.

---

# 15. Pourquoi Airflow + dbt

La séparation permet :

```text
Airflow
=
WHEN / WORKFLOW

dbt
=
TRANSFORMATION LOGIC
```

Cette séparation facilite :

- maintenance ;
- tests ;
- traçabilité ;
- réutilisation.

---

# 16. Pourquoi OpenMetadata

OpenMetadata apporte :

- catalogue ;
- lineage ;
- ownership ;
- classification ;
- profiling ;
- Data Quality ;
- gouvernance.

Cela répond directement au besoin de centralisation et de confiance dans les données.

---

# 17. Pourquoi Local AI

La stratégie local-first permet de :

- garder le contrôle des données ;
- limiter les transferts externes ;
- maîtriser les coûts ;
- expérimenter avec les modèles ;
- intégrer l’IA à la plateforme.

```text
Local AI
=
Default

External AI
=
Governed Exception
```

---

# 18. Analyse des risques

Les principaux risques comprennent :

| Risque | Impact |
|---|---|
| Complexité excessive | Difficulté d’exploitation |
| Saturation stockage | Dégradation plateforme |
| Saturation GPU | Dégradation AI |
| Mauvaise qualité de données | Résultats incorrects |
| Absence de gouvernance | Risques de conformité |
| Mauvaise gestion des secrets | Risque sécurité |
| Perte de données | Impact métier |
| Absence de restauration testée | Risque de reprise |
| Mauvais routage réseau | Interruption Kubernetes |
| Scope trop large | Risque projet |

---

# 19. Mesures de réduction des risques

Les principales mesures sont :

```text
GitOps
Governance as Code
Observability
Backup / Restore
Data Quality
Architecture Decision Records
Capacity Planning
Security Controls
Documentation as Code
```

---

# 20. Valeur métier

La plateforme vise à produire de la valeur par :

- automatisation ;
- réduction des erreurs ;
- accélération de recherche ;
- centralisation ;
- Data Quality ;
- réutilisation de la donnée ;
- meilleure traçabilité ;
- intégration future de l’IA ;
- aide à la décision.

---

# 21. Valeur technique

La valeur technique comprend :

- réduction du drift ;
- infrastructure reproductible ;
- monitoring ;
- gestion des versions ;
- meilleure reprise ;
- architecture modulaire ;
- standardisation ;
- capacité d’évolution.

---

# 22. Valeur Data

La plateforme permet :

```text
Source
  |
  v
RAW
  |
  v
STAGING
  |
  v
WAREHOUSE
  |
  v
ANALYTICS
```

Cela améliore :

- cohérence ;
- gouvernance ;
- qualité ;
- réutilisation.

---

# 23. Valeur AI

Le socle AI permet de construire progressivement :

- assistance métier ;
- recherche documentaire ;
- RAG ;
- classification ;
- extraction ;
- automatisation ;
- aide à la décision.

L’IA reste cependant soumise aux règles :

- sécurité ;
- Data Governance ;
- AI Governance ;
- humain dans la boucle lorsque nécessaire.

---

# 24. Faisabilité

La faisabilité technique est renforcée par le fait que plusieurs composants sont déjà opérationnels :

```text
Kubernetes
GitLab
Argo CD
PostgreSQL
Airflow
MLflow
OpenMetadata
Prometheus
Grafana
Loki
Tempo
Ollama
```

Le projet ne part donc pas d’une architecture théorique pure.

---

# 25. Architecture de référence

La cible globale est :

```text
                    BUSINESS
                       |
                       v
                  APPLICATION
                       |
             +---------+---------+
             |                   |
             v                   v
            DATA                 AI
             |                   |
             +---------+---------+
                       |
                       v
                PLATFORM SERVICES
                       |
                       v
                  KUBERNETES
                       |
                       v
                INFRASTRUCTURE
```

Capacités transverses :

```text
Security
DevOps / GitOps
Operations
Observability
Governance
Backup / DR
```

---

# 26. Sources documentaires

Références principales :

```text
../../../00-FOUNDATION/00-Executive-Summary.md
../../../00-FOUNDATION/02-Project-Vision.md
../../../00-FOUNDATION/03-Business-Objectives.md
../../../00-FOUNDATION/04-Architecture-Decisions.md
../../../10-BUSINESS/01-Business-Architecture.md
../../../20-APPLICATION/01-Application-Architecture.md
../../../40-DATA/01-Data-Architecture.md
../../../50-AI/01-AI-Platform-Architecture.md
../../../95-GOVERNANCE/04-Risk-Management.md
```

---

# 27. Diagrammes

Les vues principales sont :

```text
../../../99-DIAGRAMS/01-Enterprise-Context.puml
../../../99-DIAGRAMS/02-Enterprise-Platform-Architecture.puml
../../../99-DIAGRAMS/06-Application-Architecture.puml
../../../99-DIAGRAMS/07-Data-Architecture.puml
../../../99-DIAGRAMS/08-AI-Architecture.puml
```

---

# 28. Critères Go / No-Go

Le projet est pertinent si :

```text
Business Value > Operational Cost
```

et si :

- le besoin est réel ;
- la solution est exploitable ;
- la sécurité est maîtrisée ;
- les données peuvent être gouvernées ;
- la plateforme reste maintenable ;
- les bénéfices sont mesurables.

Un besoin ne justifiant pas la complexité doit être refusé ou simplifié.

---

# 29. Décision

La décision est :

```text
GO
```

pour la construction progressive de la plateforme, avec une approche incrémentale.

La cible ne doit pas être déployée entièrement en une seule étape.

Le modèle est :

```text
Foundation
    |
    v
Data
    |
    v
Applications
    |
    v
AI
    |
    v
Governance / Industrialisation
```

avec des capacités transverses présentes tout au long du cycle.

---

# 30. Preuves complémentaires à joindre

## État disponible dans le projet

L'opportunité est désormais reliée à des réalisations concrètes.

| Besoin | Réalisation | Preuve disponible |
|---|---|---|
| Conserver les critères du client | Demandes et versions de demande | Services et modèles FastAPI |
| Sélectionner des biens compatibles | Matching déterministe et recommandations persistées | Rapport de vérification des recommandations du 9 septembre 2026 |
| Centraliser les traitements Data | Chaîne RAW / STAGING / OLTP / Warehouse / analytics | Architecture Data implémentée et DAG Airflow |
| Attribuer les opérations | Identité applicative, RBAC et audit métier | Documentation sécurité et résultats de tests |
| Protéger les données | Sauvegarde MinIO et restauration PostgreSQL isolée | Rapport PRA |

Sources complémentaires :

```text
../../../40-DATA/ARCHITECTURE-DATA-IMPLEMENTEE.md
../../../60-SECURITY/RECOMMENDATION-AUDIT-RUNTIME-EVIDENCE.md
../../../60-SECURITY/SECURITY-RBAC-AUDIT-IMPLEMENTATION-EVIDENCE.md
../../../PCA PRA/PCA-PRA-POSTGRESQL.md
../../01-BC01/C2-Strategie-SI/README.md
```

## Bénéfices restant à mesurer

Les réalisations démontrent la faisabilité technique de la solution. Le gain de temps des chasseurs, le taux de conversion et le retour sur investissement restent des bénéfices attendus. Aucun montant économisé ni pourcentage d'amélioration métier n'est déduit de la seule présence de l'API ou des pipelines.

Pour la soutenance, les preuves complémentaires pertinentes peuvent inclure :

```text
Architecture diagrams
Project vision
Business objectives
Decision matrix
Risk register
Technology choices
Prototype screenshots
Runtime evidence
```

---

# 31. Critère de réussite

La compétence est démontrée si le jury peut comprendre :

```text
Business Problem
       |
       v
Opportunity
       |
       v
Alternatives
       |
       v
Constraints
       |
       v
Benefits / Risks
       |
       v
Decision
```

---

# 32. Statut

| Élément | Statut |
|---|---|
| Contexte | DOCUMENTÉ |
| Problématique | DOCUMENTÉE |
| Besoins | DOCUMENTÉS |
| Contraintes | DOCUMENTÉES |
| Alternatives | DOCUMENTÉES |
| Risques | DOCUMENTÉS |
| Bénéfices | DOCUMENTÉS |
| Faisabilité | DOCUMENTÉE |
| Architecture cible | DISPONIBLE |
| Décision Go / No-Go | GO |
| Preuves runtime | À CONSOLIDER |

---

# 33. Conclusion

L’opportunité ne repose pas sur l’introduction de technologies pour elles-mêmes.

Elle repose sur le passage :

```text
Manual / Fragmented Processes
            |
            v
Governed Data Platform
            |
            v
Automation
            |
            v
Analytics
            |
            v
AI-enabled Business Services
```

La plateforme représente donc une opportunité d’amélioration :

```text
Business
+
Data
+
Automation
+
AI
+
Governance
```

tout en conservant une architecture réaliste et exploitable.

---

**BC02 / C1 — Étude d’opportunité : DOCUMENTATION BASELINE COMPLETE**
