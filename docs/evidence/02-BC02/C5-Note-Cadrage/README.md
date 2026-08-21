# BC02 — C5 — Note de cadrage

**Bloc de compétences :** BC02  
**Compétence :** C5 — Cadrer le projet, définir son périmètre, ses objectifs, ses contraintes et ses critères de réussite  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Baseline documentaire disponible

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves relatives au cadrage du projet.

La note de cadrage doit permettre de répondre clairement aux questions suivantes :

```text
Pourquoi ?
Quoi ?
Pour qui ?
Avec quelles contraintes ?
Avec quelles ressources ?
Dans quel périmètre ?
Avec quels risques ?
Avec quels livrables ?
Avec quels critères de réussite ?
```

Le cadrage transforme une idée en projet maîtrisable.

```text
Opportunity
    |
    v
Objectives
    |
    v
Scope
    |
    v
Constraints
    |
    v
Deliverables
    |
    v
Planning
    |
    v
Execution
```

---

# 2. Document principal

La source principale de preuve est :

```text
NOTE-DE-CADRAGE.md
```

Emplacement projet attendu :

```text
../../../../NOTE-DE-CADRAGE.md
```

Ce document doit rester la source de vérité pour le cadrage opérationnel.

Le présent README sert uniquement d'index de preuve.

---

# 3. Documents complémentaires

Le cadrage est également soutenu par :

```text
../../../00-FOUNDATION/00-Executive-Summary.md
../../../00-FOUNDATION/02-Project-Vision.md
../../../00-FOUNDATION/03-Business-Objectives.md
../../../00-FOUNDATION/Project-Constitution.md
../../../00-FOUNDATION/Infrastructure-Improvement-Plan.md
```

Documents de pilotage complémentaires :

```text
../../../95-GOVERNANCE/04-Risk-Management.md
../../../95-GOVERNANCE/10-Architecture-Roadmap.md
```

---

# 4. Contexte

Le projet vise à construire une plateforme permettant de structurer et d'industrialiser les capacités :

```text
Application
Data
AI / ML
Infrastructure
Security
Observability
Governance
Operations
```

dans le cadre d'un projet métier de type :

```text
Real Estate Intelligence Platform
```

La plateforme technique est conçue comme un socle réutilisable.

---

# 5. Problématique

Les environnements métier peuvent présenter :

- informations dispersées ;
- traitements manuels ;
- fichiers multiples ;
- duplication ;
- manque de traçabilité ;
- faible automatisation ;
- difficulté d'exploitation de la donnée ;
- difficulté d'intégration de l'IA ;
- gouvernance insuffisante.

Le projet cherche à réduire ces difficultés par une architecture structurée.

---

# 6. Vision

La vision cible est :

```text
Business Need
      |
      v
Application
      |
      +---------+
      |         |
      v         v
     Data      AI
      |         |
      +----+----+
           |
           v
     Platform Services
           |
           v
       Kubernetes
           |
           v
     Infrastructure
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

# 7. Objectifs du projet

Les objectifs principaux sont :

- centraliser les capacités Data ;
- automatiser les traitements ;
- améliorer la qualité ;
- améliorer la traçabilité ;
- permettre l'exploitation analytique ;
- fournir une capacité AI locale ;
- industrialiser le lifecycle ML ;
- sécuriser les traitements ;
- améliorer la gouvernance ;
- rendre la plateforme observable ;
- assurer la recoverability.

---

# 8. Objectifs métier

Les objectifs métier comprennent notamment :

```text
Reduce Manual Work
Improve Information Availability
Improve Data Quality
Improve Traceability
Enable Analytics
Enable AI Assistance
Support Business Decisions
```

Les objectifs techniques ne doivent pas remplacer les objectifs métier.

---

# 9. Objectifs techniques

Les objectifs techniques sont :

- orchestration Kubernetes ;
- GitOps ;
- Data Platform ;
- MLOps ;
- AI local-first ;
- observabilité ;
- gouvernance ;
- sécurité ;
- automation ;
- backup / restore.

---

# 10. Périmètre IN

Le périmètre du projet comprend :

```text
Architecture
Infrastructure
Kubernetes
Application Architecture
Data Architecture
AI / ML
MLOps
Security
DevOps / GitOps
Observability
Operations
Governance
Documentation
Evidence
```

---

# 11. Périmètre OUT / différé

Certains composants ne font pas partie du périmètre immédiat.

Exemples :

```text
Kafka
Dedicated Qdrant deployment
Service Mesh
KEDA
Argo Events
Argo Workflows
Feature Store
Multi-cluster Kubernetes
```

Ils sont différés jusqu'à l'apparition d'un besoin réel.

---

# 12. Technologies cible ou candidate

Certaines technologies sont volontairement distinguées de l'état actuel.

## TARGET

```text
React
Redis
RAG
Keycloak
HashiCorp Vault
```

## CANDIDATE

```text
PostgreSQL + pgvector
Qdrant
```

Elles ne doivent pas être présentées comme déjà implémentées.

---

# 13. Contraintes matérielles

Le projet utilise une infrastructure locale existante.

Contraintes principales :

- capacité CPU limitée ;
- capacité RAM limitée ;
- stockage limité ;
- GPU de génération ancienne ;
- VRAM limitée ;
- absence de cloud illimité.

Concernant l'AI :

```text
GTX 1080
8 GB VRAM
```

Cela impose :

- sélection de modèles adaptés ;
- quantification ;
- maîtrise de la concurrence ;
- optimisation des ressources.

---

# 14. Contraintes organisationnelles

Le projet est réalisé avec des ressources humaines limitées.

Cela implique :

```text
Architecture must remain operable
by a small team.
```

Le choix d'une technologie doit prendre en compte son coût d'exploitation.

---

# 15. Contraintes de délai

Le projet s'inscrit dans un cadre de formation et d'évaluation.

Le planning doit donc privilégier :

```text
Required Competencies
        +
Demonstrable Evidence
        +
Business Value
```

avant les améliorations optionnelles.

---

# 16. Contraintes de souveraineté

Les données métier doivent pouvoir rester sous contrôle local.

Principe :

```text
Local AI
=
Default
```

et :

```text
External AI
=
Explicitly Governed Exception
```

---

# 17. Contraintes RGPD

Le projet doit identifier :

- données personnelles ;
- finalités ;
- base légale ;
- rétention ;
- droits ;
- destinataires ;
- mesures de sécurité.

Référence :

```text
../../../../REGISTRE-RGPD.md
```

---

# 18. Contraintes d'accessibilité

Les interfaces utilisateur doivent prendre en compte les besoins des personnes en situation de handicap lorsque applicable.

Les points incluent :

- navigation clavier ;
- structure sémantique ;
- labels ;
- contrastes ;
- erreurs compréhensibles ;
- alternatives textuelles.

---

# 19. Contraintes de sécurité

Le projet doit prendre en compte :

```text
Authentication
Authorization
RBAC
TLS
Secrets
Network Security
Container Security
Kubernetes Security
Data Security
AI Security
Auditability
```

---

# 20. Contraintes d'exploitation

La plateforme doit pouvoir être :

```text
Observed
Maintained
Updated
Recovered
Audited
```

Les outils d'exploitation ne doivent pas être ajoutés uniquement pour satisfaire une architecture théorique.

---

# 21. Architecture existante

L'environnement possède déjà plusieurs briques opérationnelles.

Exemples :

```text
Proxmox
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

La démarche du projet consiste donc également à industrialiser et gouverner un environnement existant.

---

# 22. Architecture cible

La cible est documentée dans :

```text
../../../00-FOUNDATION/Enterprise-AI-Platform.md
```

ainsi que dans :

```text
../../../99-DIAGRAMS/
```

Les diagrammes principaux incluent :

```text
01 Enterprise Context
02 Enterprise Platform
03 Infrastructure
04 Kubernetes
05 Network
06 Application
07 Data
08 AI
09 MLOps
10 DevOps / GitOps
11 Observability
12 Security
13 Governance as Code
14 Backup / DR
```

---

# 23. Livrables principaux

Le projet doit produire plusieurs catégories de livrables.

## Architecture

```text
Architecture documentation
ADR
PlantUML diagrams
```

## Pilotage

```text
Note de cadrage
Planning
RACI
Risk register
Decision matrix
Decision journal
```

## Data

```text
MCD
SQL migration
OLTP
OLAP
Data Quality
Optimization evidence
```

## AI

```text
Model lifecycle
AI architecture
AI governance
AI security
Program / prototype
```

## Compliance

```text
RGPD
Eco-conception
Accessibility
Security
```

## Evidence

```text
Runtime outputs
Tests
Screenshots
Reports
Metrics
```

---

# 24. Hypothèses

Le cadrage s'appuie sur plusieurs hypothèses.

Exemples :

- l'infrastructure existante reste disponible ;
- Kubernetes reste la plateforme principale ;
- PostgreSQL reste la base relationnelle principale ;
- GitLab reste disponible ;
- l'AI locale reste techniquement exploitable ;
- les volumes restent compatibles avec l'infrastructure actuelle.

Une hypothèse invalidée peut entraîner une révision du cadrage.

---

# 25. Dépendances

Le projet possède des dépendances fortes.

```text
Infrastructure
    |
    v
Kubernetes
    |
    v
Platform Services
    |
    +-------------+
    |             |
    v             v
   Data          AI
    |             |
    +------+------+
           |
           v
      Application
```

---

# 26. Dépendances Data

```text
PostgreSQL
    |
    v
Data Model
    |
    v
Airflow / dbt
    |
    v
Data Quality
    |
    v
OpenMetadata
    |
    v
Analytics / AI
```

---

# 27. Dépendances AI

```text
Governed Data
     |
     v
Training / Context
     |
     v
MLflow / RAG
     |
     v
Ollama
     |
     v
Qwen
```

---

# 28. Dépendances GitOps

```text
GitLab
  |
  v
Repository
  |
  v
Argo CD
  |
  v
Kubernetes
```

---

# 29. Risques principaux

Les risques principaux comprennent :

| Risque | Conséquence |
|---|---|
| Scope trop large | Retard |
| Complexité excessive | Difficulté d'exploitation |
| Stockage saturé | Interruption |
| GPU saturé | Dégradation AI |
| Routage incorrect | Perte workers Kubernetes |
| Données incorrectes | Décisions erronées |
| Secrets exposés | Incident sécurité |
| Backup non restaurable | Perte de service |
| Manque de preuves | Compétence non démontrée |
| Documentation divergente | Architecture incohérente |

---

# 30. Gestion des risques

Référence principale :

```text
../../../95-GOVERNANCE/04-Risk-Management.md
```

Cycle :

```text
Identify
  |
  v
Assess
  |
  v
Treat
  |
  v
Monitor
  |
  v
Review
```

---

# 31. Gouvernance des décisions

Les décisions importantes doivent être tracées.

```text
Problem
  |
  v
Alternatives
  |
  v
Decision
  |
  v
ADR
```

Répertoire :

```text
../../../98-ADR/
```

---

# 32. Méthode de réalisation

Le projet utilise une démarche incrémentale.

```text
Foundation
    |
    v
Architecture
    |
    v
Implementation
    |
    v
Validation
    |
    v
Evidence
    |
    v
Improvement
```

---

# 33. Backlog

La priorisation détaillée est décrite dans :

```text
../C2-Backlog-Priorise/README.md
```

Les priorités sont :

```text
P0
Foundation / blockers

P1
Critical delivery

P2
Important enhancement

P3
Optimization

P4
Future
```

---

# 34. Méthode MoSCoW

Le projet distingue :

```text
MUST
SHOULD
COULD
WON'T / LATER
```

Cette méthode permet de limiter le scope et de protéger les livrables critiques.

---

# 35. Critères de réussite

Le projet est considéré comme réussi si les principaux objectifs sont :

```text
Documented
+
Implemented
+
Tested
+
Evidenced
```

selon la portée de chaque fonctionnalité.

---

# 36. Critères techniques

Les critères comprennent notamment :

- workloads opérationnels ;
- pipelines exécutables ;
- données exploitables ;
- qualité vérifiée ;
- modèles traçables ;
- AI inference fonctionnelle ;
- métriques disponibles ;
- logs disponibles ;
- restauration démontrée ;
- sécurité documentée et testée selon périmètre.

---

# 37. Critères Data

La partie Data doit permettre de démontrer :

```text
Model
Migration
OLTP
Optimization
OLAP
Quality
Metadata
Lineage
```

---

# 38. Critères AI

La partie AI doit permettre de démontrer :

```text
Data
  |
  v
Training / Model
  |
  v
Evaluation
  |
  v
Lifecycle
  |
  v
Inference
  |
  v
Governance
```

---

# 39. Critères sécurité

Le projet doit pouvoir démontrer les principaux mécanismes pertinents :

```text
RBAC
TLS
Secrets
Data Security
AI Security
Security Monitoring
```

---

# 40. Critères de gouvernance

Le projet doit permettre de relier :

```text
Requirement
    |
    v
Control
    |
    v
Implementation
    |
    v
Evidence
```

---

# 41. Critères de preuve

Le principe d'évaluation retenu est :

```text
Claim
without
Evidence
=
Weak Demonstration
```

Une preuve peut être :

- commande ;
- capture ;
- rapport de test ;
- fichier SQL ;
- métrique ;
- dashboard ;
- CI output ;
- Data Quality result ;
- restore report ;
- ADR ;
- diagramme.

---

# 42. Architecture et scope

La documentation d'architecture est volontairement plus large que le minimum d'implémentation.

Le cadrage doit donc distinguer :

```text
Architecture Target
```

de :

```text
Implemented Scope
```

Cette distinction évite de déclarer comme terminées des fonctionnalités uniquement documentées.

---

# 43. Technologies différées

Les technologies suivantes ne sont pas nécessaires au premier scope :

```text
Kafka
Qdrant dedicated deployment
Service Mesh
KEDA
Argo Events
Feature Store
Multi-cluster
```

Elles restent disponibles comme évolutions possibles.

---

# 44. Organisation du projet

Les responsabilités conceptuelles sont séparées entre :

```text
Business
Architecture
Platform / DevOps
Data
AI
Security
Operations
Governance
```

Même lorsque plusieurs responsabilités sont assumées par une seule personne.

---

# 45. Communication

Le projet doit conserver une documentation suffisamment claire pour permettre :

- revue ;
- transmission ;
- soutenance ;
- maintenance ;
- évolution.

Les décisions importantes doivent rester accessibles via Git et ADR.

---

# 46. Documentation

Le projet utilise :

```text
Markdown
PlantUML
Git
```

afin de rendre la documentation :

- versionnable ;
- diffable ;
- reproductible ;
- reviewable.

---

# 47. Pilotage par preuves

Le projet évolue progressivement vers :

```text
Task
 |
 v
Implementation
 |
 v
Test
 |
 v
Evidence
 |
 v
Competency
```

La structure :

```text
docs/evidence/
```

centralise cette traçabilité.

---

# 48. Go / No-Go

La décision de cadrage est :

```text
GO
```

pour une réalisation progressive.

La décision ne signifie pas :

```text
Implement all target technologies immediately
```

Elle signifie :

```text
Implement the minimum validated architecture
required to provide business value
and demonstrate required competencies.
```

---

# 49. Points à surveiller

Les points de surveillance comprennent :

- scope ;
- temps ;
- stockage ;
- GPU ;
- complexité ;
- sécurité ;
- RGPD ;
- tests ;
- preuves ;
- qualité documentaire.

---

# 50. Statut actuel

| Élément | Statut |
|---|---|
| Contexte | DOCUMENTÉ |
| Vision | DOCUMENTÉE |
| Objectifs | DOCUMENTÉS |
| Scope | DOCUMENTÉ |
| Contraintes | DOCUMENTÉES |
| Architecture | DOCUMENTÉE |
| Risques | DOCUMENTÉS |
| Backlog | DOCUMENTÉ |
| Technologies différées | DOCUMENTÉES |
| Critères de réussite | DOCUMENTÉS |
| Note de cadrage principale | EXISTANTE |
| Planning détaillé | À CENTRALISER |
| RACI | À CENTRALISER |
| Runtime evidence | À COMPLÉTER |

---

# 51. Critère de réussite de la compétence

La compétence est démontrée si le jury peut comprendre :

```text
Context
  |
  v
Problem
  |
  v
Objectives
  |
  v
Scope
  |
  v
Constraints
  |
  v
Risks
  |
  v
Deliverables
  |
  v
Planning
  |
  v
Success Criteria
```

sans ambiguïté sur ce que le projet cherche réellement à produire.

---

# 52. Conclusion

La note de cadrage transforme le projet :

```text
Idea
```

en :

```text
Controlled Project
```

en définissant explicitement :

```text
Why
What
Who
Scope
Constraints
Risks
Deliverables
Success Criteria
```

Elle constitue la base du backlog, du planning, du RACI, de l'architecture et du suivi du projet.

---

**BC02 / C5 — Note de cadrage : DOCUMENTATION BASELINE COMPLETE**