# BC02 — C6 — Planning & jalons

**Bloc de compétences :** BC02  
**Compétence :** C6 — Construire et piloter un planning projet avec jalons, dépendances et livrables  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Baseline documentaire — planning détaillé à aligner avec les dates réelles du projet

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves démontrant que le projet est planifié de manière structurée.

Le planning doit permettre de représenter :

- les phases ;
- les dépendances ;
- les priorités ;
- les jalons ;
- les livrables ;
- les risques ;
- les preuves attendues ;
- les points de décision.

Le modèle général est :

```text
Scope
  |
  v
Backlog
  |
  v
Dependencies
  |
  v
Planning
  |
  v
Milestones
  |
  v
Deliverables
  |
  v
Evidence
```

---

# 2. Sources de référence

Les documents principaux sont :

```text
../C2-Backlog-Priorise/README.md
../C5-Note-Cadrage/README.md

../../../00-FOUNDATION/Project-Constitution.md
../../../00-FOUNDATION/Infrastructure-Improvement-Plan.md
../../../95-GOVERNANCE/10-Architecture-Roadmap.md
```

Les éléments de pilotage complémentaires comprennent :

```text
NOTE-DE-CADRAGE.md
RACI.md
JOURNAL-DE-DECISIONS.md
MATRICE-DECISION.md
```

---

# 3. Principes de planification

Le planning respecte les principes suivants :

```text
Dependencies before Features
Foundations before Enhancements
Evidence before Final Delivery
Risk Reduction before Optional Complexity
```

Le projet évite :

```text
Build Everything in Parallel
```

car cela augmente :

- les dépendances bloquantes ;
- le risque ;
- la complexité ;
- la difficulté de validation.

---

# 4. Ordre général du projet

La séquence générale est :

```text
1. Cadrage
2. Audit
3. Architecture
4. Infrastructure
5. Kubernetes
6. GitOps / CI
7. Data Platform
8. Data Governance
9. MLOps / AI
10. Application
11. Security
12. Observability
13. Operations / DR
14. Governance as Code
15. Evidence
16. Soutenance
```

Certaines activités transverses sont menées en parallèle, mais l'ordre des dépendances reste respecté.

---

# 5. Phases du projet

## Phase 0 — Cadrage

Objectifs :

- comprendre le besoin ;
- définir le scope ;
- identifier les parties prenantes ;
- identifier les risques ;
- définir les livrables.

Livrables :

```text
NOTE-DE-CADRAGE
Project Constitution
Business Objectives
RACI
Risk Register
```

---

# 6. Phase 1 — Audit de l'existant

Objectifs :

- inventorier l'existant ;
- analyser infrastructure ;
- analyser réseau ;
- analyser Data ;
- analyser AI ;
- identifier limites ;
- identifier dette ;
- identifier risques.

Livrables :

```text
Audit documentation
Gap analysis
Infrastructure assessment
Risk assessment
```

---

# 7. Phase 2 — Architecture cible

Objectifs :

- définir les principes ;
- définir les technologies ;
- comparer les options ;
- formaliser les décisions ;
- produire les diagrammes.

Livrables :

```text
Architecture Principles
Technology Stack
Architecture Decisions
ADR
PlantUML Diagrams
```

---

# 8. Phase 3 — Infrastructure

Objectifs :

- préparer l'environnement d'exécution ;
- valider compute ;
- valider stockage ;
- valider réseau ;
- valider virtualisation.

Dépendances :

```text
Phase 0
Phase 1
Phase 2
```

Livrables :

```text
Infrastructure Architecture
Network Architecture
Storage Architecture
Capacity Planning
```

---

# 9. Phase 4 — Kubernetes

Objectifs :

- cluster stable ;
- control planes ;
- workers ;
- CNI ;
- DNS ;
- ingress ;
- TLS.

Jalon :

```text
M1 — Kubernetes Platform Ready
```

Critère :

```text
Expected nodes report Ready
and required cluster services are operational.
```

---

# 10. Phase 5 — GitOps / CI

Objectifs :

- GitLab ;
- GitLab Runner ;
- Argo CD ;
- root application ;
- automated reconciliation.

Jalon :

```text
M2 — GitOps Operational
```

Critère :

```text
A committed desired-state change
is reconciled automatically into Kubernetes.
```

---

# 11. Phase 6 — Data Platform

Objectifs :

- PostgreSQL ;
- schemas ;
- Airflow ;
- dbt ;
- transformations ;
- Data Quality.

Jalon :

```text
M3 — Data Pipeline Operational
```

Critère :

```text
Source data
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

avec preuves de transformation et de qualité.

---

# 12. Phase 7 — Data Governance

Objectifs :

- OpenMetadata ;
- metadata ingestion ;
- ownership ;
- profiling ;
- lineage ;
- Data Quality visibility.

Jalon :

```text
M4 — Governed Data Asset Available
```

Critère :

Un asset critique est :

- catalogué ;
- profilé ;
- relié à sa source ;
- associé à une gouvernance identifiable.

---

# 13. Phase 8 — MLOps

Objectifs :

- MLflow ;
- tracking ;
- artifacts ;
- registry ;
- model lifecycle.

Jalon :

```text
M5 — ML Lifecycle Demonstrated
```

Critère :

```text
Training
  |
  v
Experiment
  |
  v
Metrics
  |
  v
Artifact
  |
  v
Model Version
```

visible et traçable.

---

# 14. Phase 9 — Local AI

Objectifs :

- Ollama ;
- Qwen ;
- GPU local ;
- API inference ;
- monitoring de base.

Jalon :

```text
M6 — Local AI Inference Operational
```

Critère :

Une requête depuis un service distant atteint Ollama et retourne une réponse valide.

---

# 15. Phase 10 — Application

Objectifs :

- cas d'usage métier ;
- API ;
- validation ;
- tests ;
- intégration Data ;
- intégration AI.

Jalon :

```text
M7 — Business Application MVP
```

Critère :

Le cas d'usage principal est démontrable de bout en bout.

---

# 16. Phase 11 — Security

Objectifs :

- RBAC ;
- TLS ;
- secrets ;
- sécurité Kubernetes ;
- contrôles applicatifs ;
- sécurité Data ;
- sécurité AI.

Jalon :

```text
M8 — Security Baseline Validated
```

Critère :

Les contrôles prioritaires sont implémentés et démontrables.

---

# 17. Phase 12 — Observability

Objectifs :

- metrics ;
- logs ;
- traces ;
- dashboards ;
- alerts ;
- SLI / SLO.

Jalon :

```text
M9 — Observability Baseline Operational
```

Critère :

Un service critique peut être observé via :

```text
Metrics
Logs
Traces
```

selon les capacités réellement instrumentées.

---

# 18. Phase 13 — Backup / DR

Objectifs :

- backup ;
- restore ;
- validation ;
- mesure RPO / RTO.

Jalon :

```text
M10 — Restore Demonstrated
```

Critère :

```text
Backup
  |
  v
Restore
  |
  v
Functional Validation
```

exécuté avec preuve.

---

# 19. Phase 14 — Governance as Code

Objectifs :

- formaliser controls ;
- versionner policies ;
- CI validation ;
- application ;
- evidence.

Jalon :

```text
M11 — Governance Rule Applied from Git
```

Critère :

Une règle de gouvernance versionnée produit un changement ou un contrôle observable.

---

# 20. Phase 15 — Evidence Consolidation

Objectifs :

- centraliser outputs ;
- captures ;
- tests ;
- SQL ;
- metrics ;
- reports ;
- traceability.

Jalon :

```text
M12 — Competency Evidence Complete
```

Critère :

Chaque compétence possède :

```text
Claim
+
Artifact
+
Evidence
+
Status
```

---

# 21. Phase 16 — Soutenance

Objectifs :

- sélectionner les preuves ;
- construire scénario ;
- préparer démonstration ;
- préparer questions ;
- répéter.

Jalon final :

```text
M13 — Defense Ready
```

---

# 22. Jalons principaux

| ID | Jalon | Résultat attendu |
|---|---|---|
| M0 | Cadrage validé | Scope et objectifs définis |
| M1 | Kubernetes Ready | Cluster opérationnel |
| M2 | GitOps Operational | Reconciliation automatique |
| M3 | Data Pipeline Operational | Pipeline Data complet |
| M4 | Data Governance Ready | Metadata / lineage disponibles |
| M5 | ML Lifecycle Demonstrated | MLflow evidence |
| M6 | Local AI Operational | Inference locale |
| M7 | Application MVP | Cas métier démontrable |
| M8 | Security Baseline | Contrôles prioritaires |
| M9 | Observability Baseline | Metrics/logs/traces |
| M10 | Restore Demonstrated | Recovery proof |
| M11 | Governance as Code | Rule → runtime |
| M12 | Evidence Complete | Référentiel couvert |
| M13 | Defense Ready | Soutenance prête |

---

# 23. Dépendances principales

```text
M0
 |
 v
M1
 |
 v
M2
 |
 +----------------------+
 |                      |
 v                      v
M3                     Platform Services
 |
 v
M4
 |
 +-------------+
 |             |
 v             v
M5            M7
 |
 v
M6
```

Puis :

```text
Security
Observability
DR
Governance
Evidence
```

sont consolidés autour des composants réellement implémentés.

---

# 24. Chemin critique

Un chemin critique probable est :

```text
Cadrage
  |
  v
Infrastructure
  |
  v
Kubernetes
  |
  v
GitOps
  |
  v
Data
  |
  v
Application / AI
  |
  v
Tests
  |
  v
Evidence
  |
  v
Soutenance
```

Un retard sur ces étapes peut bloquer plusieurs livrables.

---

# 25. Activités parallélisables

Certaines activités peuvent se dérouler en parallèle.

Exemples :

```text
Architecture Documentation
Security Documentation
Governance Documentation
Observability Documentation
```

pendant que l'infrastructure est développée.

Cependant :

```text
Documentation
does not replace
Implementation
```

---

# 26. Planning par priorité

## P0

```text
Cadrage
Architecture
Infrastructure
Kubernetes
GitOps
Evidence structure
```

## P1

```text
Data
Application
MLOps
Local AI
Security
Observability
Backup / DR
Governance
RGPD
```

## P2

```text
RAG
Eco-conception
Accessibility improvements
Advanced automation
```

---

# 27. Gestion des buffers

Le planning doit conserver des marges pour :

- incidents ;
- debugging ;
- changements de scope ;
- dépendances externes ;
- soutenance ;
- correction des preuves.

Principe :

```text
100% Planned Capacity
=
No Capacity for Problems
```

Une partie de la capacité doit rester disponible pour l'imprévu.

---

# 28. Gestion des risques planning

Exemples :

| Risque | Impact planning |
|---|---|
| Problème Kubernetes | Bloque workloads |
| Problème stockage | Bloque Data/AI |
| GPU insuffisant | Retarde AI |
| Data incorrecte | Retarde analytics/ML |
| Scope creep | Retarde tout |
| RAG trop complexe | Retarde application |
| Restore non fonctionnel | Retarde preuve DR |
| Documentation divergente | Retarde soutenance |

---

# 29. Stratégie de réduction des risques

Le planning protège les livrables critiques avec :

```text
Must Have First
Optional Later
```

et :

```text
Simple Working Solution
before
Complex Future Architecture
```

---

# 30. Gantt — représentation logique

Le Gantt détaillé peut être construit à partir de cette séquence :

```text
Phase 0  Cadrage
Phase 1  Audit
Phase 2  Architecture
Phase 3  Infrastructure
Phase 4  Kubernetes
Phase 5  GitOps
Phase 6  Data
Phase 7  Governance Data
Phase 8  MLOps
Phase 9  AI
Phase 10 Application
Phase 11 Security
Phase 12 Observability
Phase 13 DR
Phase 14 Governance as Code
Phase 15 Evidence
Phase 16 Soutenance
```

Les dates réelles doivent être basées sur le calendrier réel du projet et non inventées dans ce document.

---

# 31. Structure Gantt recommandée

Le Gantt final doit contenir au minimum :

```text
Task
Start
End
Duration
Dependency
Owner
Milestone
Status
```

Exemple :

| Task | Dependency | Milestone |
|---|---|---|
| Kubernetes cluster | Infrastructure | M1 |
| Argo CD | Kubernetes | M2 |
| PostgreSQL platform | Kubernetes | M3 |
| OpenMetadata | Data Platform | M4 |
| MLflow | Data Platform | M5 |
| Ollama | AI Host | M6 |

---

# 32. Suivi d'avancement

Les statuts possibles sont :

```text
NOT STARTED
IN PROGRESS
BLOCKED
DONE
VALIDATED
EVIDENCED
```

Important :

```text
DONE
!=
EVIDENCED
```

Un élément peut fonctionner sans encore disposer de preuve exploitable pour le jury.

---

# 33. Critères de sortie d'une phase

Une phase peut être considérée terminée lorsque :

```text
Deliverable exists
+
Acceptance criteria met
+
Critical tests passed
+
Evidence available
```

selon la nature de la phase.

---

# 34. Suivi des jalons

Pour chaque jalon, le projet doit pouvoir enregistrer :

```text
Planned Date
Actual Date
Status
Blocking Issues
Evidence
Decision
```

---

# 35. Gestion des retards

En cas de retard :

```text
Delay
 |
 v
Impact Analysis
 |
 v
Critical Path?
 +---+---+
 |       |
NO      YES
 |       |
 v       v
Adjust  Replan Priority
```

La première action n'est pas nécessairement d'ajouter des ressources.

Il faut d'abord réduire le scope optionnel.

---

# 36. Scope de délestage

Les premiers éléments à différer sont :

```text
Kafka
Dedicated Qdrant
Service Mesh
KEDA
Argo Events
Feature Store
Multi-cluster
```

Ils ne doivent jamais bloquer la livraison des compétences principales.

---

# 37. Planning et référentiel

Le planning doit garantir du temps pour les preuves exigées :

```text
MCD
migration.sql
EXPLAIN before / after
OLTP
OLAP
3V
AI model
AI program
Application
Tests
RGPD
Eco-design
Accessibility
AI sovereignty
PCA / PRA
```

Une réalisation technique non préparée pour la démonstration peut réduire la valeur du projet lors de l'évaluation.

---

# 38. Planning des preuves

Une phase dédiée est donc prévue.

```text
Implementation
     |
     v
Validation
     |
     v
Evidence Capture
     |
     v
Evidence Review
     |
     v
Soutenance
```

---

# 39. Planning soutenance

Le planning final doit réserver du temps pour :

- sélection des preuves ;
- construction des slides ;
- vérification des liens ;
- tests de démonstration ;
- scénario de secours ;
- répétition ;
- Q&A.

La soutenance ne doit pas être préparée uniquement après la fin de l'implémentation.

---

# 40. Documentation du planning

Le planning peut être maintenu sous plusieurs formes :

```text
Markdown
Jira
Gantt
Git issues
Project board
```

La source utilisée doit rester cohérente avec la réalité du projet.

---

# 41. Gouvernance du planning

Les modifications significatives du planning doivent pouvoir être expliquées.

Exemples :

```text
Technical Incident
Scope Change
Requirement Change
Risk Materialization
Dependency Delay
```

Le journal de décisions peut être utilisé pour les changements importants.

---

# 42. Critères de réussite

La compétence est démontrée si le jury peut comprendre :

```text
What was planned?
      |
      v
In what order?
      |
      v
Why this order?
      |
      v
What were the milestones?
      |
      v
What changed?
      |
      v
What was delivered?
```

---

# 43. Preuves attendues

Les preuves pertinentes comprennent :

```text
Gantt
Architecture roadmap
Backlog
Milestones
Project journal
Git history
Implementation evidence
Decision journal
```

---

# 44. Preuves à consolider

Ce dossier doit progressivement référencer :

```text
01-gantt.*
02-milestones.md
03-progress-status.md
04-critical-path.md
```

uniquement si ces artifacts sont effectivement créés et utilisés.

---

# 45. État actuel

| Élément | Statut |
|---|---|
| Phases | DOCUMENTÉES |
| Dépendances | DOCUMENTÉES |
| Backlog | DOCUMENTÉ |
| Priorités | DOCUMENTÉES |
| Jalons | DÉFINIS |
| Chemin critique | IDENTIFIÉ |
| Scope de délestage | DÉFINI |
| Planning evidence | PARTIEL |
| Gantt daté | À PRODUIRE / CENTRALISER |
| Dates réelles | À RENSEIGNER |
| Actual vs planned | À CONSOLIDER |

---

# 46. Conclusion

Le planning du projet est structuré autour de :

```text
Dependencies
+
Priorities
+
Milestones
+
Risk
+
Evidence
```

Le but n'est pas de suivre un calendrier figé.

Le but est de maintenir :

```text
A controlled path
from
scope
to
validated deliverables.
```

---

**BC02 / C6 — Planning & jalons : DOCUMENTATION BASELINE COMPLETE**