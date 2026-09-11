# BC01 — C4 — Pilotage projet

**Bloc de compétences :** BC01  
**Compétence :** C4 — Piloter le projet, organiser les responsabilités et maîtriser les risques  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Documentation disponible, preuves opérationnelles à consolider

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves démontrant la capacité à piloter le projet de manière structurée.

Le pilotage couvre :

- cadrage ;
- objectifs ;
- planning ;
- responsabilités ;
- risques ;
- décisions ;
- changements ;
- suivi ;
- priorisation ;
- amélioration continue ;
- traçabilité.

Le modèle retenu est :

```text
Vision
  |
  v
Objectives
  |
  v
Scope
  |
  v
Planning
  |
  v
Responsibilities
  |
  v
Risks
  |
  v
Execution
  |
  v
Monitoring
  |
  v
Decisions
  |
  v
Improvement
```

---

# 2. Sources de vérité

Les principaux documents de pilotage sont :

```text
../../../00-FOUNDATION/Project-Constitution.md
../../../00-FOUNDATION/Master-Prompt.md
../../../00-FOUNDATION/02-Project-Vision.md
../../../00-FOUNDATION/03-Business-Objectives.md
../../../00-FOUNDATION/Infrastructure-Improvement-Plan.md
```

Documents de gouvernance :

```text
../../../95-GOVERNANCE/03-Decision-Governance.md
../../../95-GOVERNANCE/04-Risk-Management.md
../../../95-GOVERNANCE/08-Technical-Debt-Management.md
../../../95-GOVERNANCE/10-Architecture-Roadmap.md
```

Documents opérationnels :

```text
../../../80-OPERATIONS/04-Change-Management.md
../../../80-OPERATIONS/05-Capacity-Management.md
../../../80-OPERATIONS/06-Availability-Management.md
../../../80-OPERATIONS/10-SRE-Practices.md
```

Les ADR sont conservés dans :

```text
../../../98-ADR/
```

---

# 3. Cadrage du projet

Le projet vise à construire une plateforme d'entreprise capable de supporter :

- applications métier ;
- plateforme Data ;
- plateforme AI / ML ;
- MLOps ;
- observabilité ;
- sécurité ;
- gouvernance ;
- GitOps ;
- disaster recovery.

La cible n'est pas uniquement technique.

Elle cherche à répondre à :

```text
Business Needs
      +
Data Needs
      +
AI Needs
      +
Operational Needs
      +
Governance Needs
```

---

# 4. Vision

La vision du projet est documentée dans :

```text
../../../00-FOUNDATION/02-Project-Vision.md
```

Elle sert à aligner :

- business ;
- architecture ;
- data ;
- AI ;
- infrastructure ;
- sécurité ;
- opérations.

Le principe de pilotage est :

```text
Architecture
must support
Business Objectives
```

et non :

```text
Business
must adapt to
arbitrary technologies
```

---

# 5. Objectifs

Les objectifs sont formalisés dans :

```text
../../../00-FOUNDATION/03-Business-Objectives.md
```

Ils permettent de rattacher les travaux techniques à des finalités mesurables.

Exemples :

- automatisation ;
- centralisation ;
- traçabilité ;
- fiabilité ;
- sécurité ;
- qualité des données ;
- capacité AI ;
- réduction des tâches manuelles ;
- amélioration de la gouvernance.

---

# 6. Constitution du projet

Le document :

```text
../../../00-FOUNDATION/Project-Constitution.md
```

définit les règles de fonctionnement du projet.

Il constitue une base de gouvernance pour :

- périmètre ;
- architecture ;
- standards ;
- contraintes ;
- qualité ;
- sécurité ;
- documentation ;
- décisions ;
- responsabilités.

---

# 7. Planning et roadmap

La roadmap est documentée dans :

```text
../../../95-GOVERNANCE/10-Architecture-Roadmap.md
```

Le principe est :

```text
Current State
     |
     v
Gap
     |
     v
Priority
     |
     v
Roadmap Item
     |
     v
Implementation
     |
     v
Validation
```

La roadmap doit distinguer :

```text
ADOPTED
TARGET
CANDIDATE
FUTURE
```

afin de ne pas confondre état actuel et cible.

---

# 8. Priorisation

La priorisation est guidée par :

- valeur métier ;
- risque ;
- dépendances ;
- sécurité ;
- stabilité ;
- effort ;
- urgence ;
- impact ;
- contraintes techniques.

Le principe est :

```text
Priority
=
Business Value
+
Risk Reduction
+
Dependency Order
+
Feasibility
```

---

# 9. RACI

Le projet dispose d'un modèle RACI permettant de clarifier les responsabilités.

Les rôles conceptuels incluent :

```text
Business
Architecture
Platform / DevOps
Data Engineering
AI / MLOps
Security
Governance
Operations
```

Dans un projet individuel ou de petite équipe, plusieurs rôles peuvent être portés par la même personne.

Cela ne supprime pas la nécessité de distinguer les responsabilités.

---

# 10. Modèle de responsabilité

Le modèle conceptuel est :

```text
R = Responsible
A = Accountable
C = Consulted
I = Informed
```

Exemple :

| Activité | Platform | Data | AI | Security | Governance |
|---|---|---|---|---|---|
| Kubernetes | R/A | I | I | C | I |
| Data pipeline | C | R/A | C | I | C |
| Model lifecycle | C | C | R/A | C | C |
| Security policy | C | I | I | R | A |
| Governance rule | C | C | C | C | R/A |

---

# 11. Gestion des risques

Le registre de risques est documenté dans :

```text
../../../95-GOVERNANCE/04-Risk-Management.md
```

Le cycle de gestion est :

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
Mitigate
  |
  v
Monitor
  |
  v
Reassess
```

---

# 12. Risques principaux

Exemples de risques du projet :

- saturation stockage ;
- saturation GPU ;
- panne d'hôte ;
- défaillance Kubernetes ;
- perte de base ;
- problème de routage ;
- mauvaise configuration ;
- exposition de secrets ;
- qualité de données insuffisante ;
- perte de traçabilité ;
- dérive GitOps ;
- défaut de restauration ;
- modèle IA non gouverné ;
- dépendance à une technologie inutilement complexe.

---

# 13. Gestion des décisions

Les décisions importantes sont tracées via ADR.

Répertoire :

```text
../../../98-ADR/
```

Cycle :

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
   |
   v
Implementation
   |
   v
Evidence
```

Cette méthode réduit les décisions implicites ou perdues.

---

# 14. Gestion des changements

Référence :

```text
../../../80-OPERATIONS/04-Change-Management.md
```

Le modèle cible est :

```text
Change
  |
  v
Git
  |
  v
Merge Request
  |
  v
CI
  |
  v
Approval
  |
  v
GitOps
  |
  v
Runtime
```

Les changements directs non tracés ne doivent pas devenir l'état permanent.

---

# 15. Gestion de la dette technique

Référence :

```text
../../../95-GOVERNANCE/08-Technical-Debt-Management.md
```

Une dette technique doit être :

- identifiée ;
- documentée ;
- priorisée ;
- attribuée ;
- suivie ;
- réévaluée.

Exemples :

```text
Missing policy enforcement
Manual governance
Incomplete restore testing
Unstructured logs
Missing ownership
```

---

# 16. Capacité et ressources

La gestion de capacité est documentée dans :

```text
../../../30-INFRASTRUCTURE/09-Capacity-Planning.md
../../../80-OPERATIONS/05-Capacity-Management.md
```

Les principales ressources surveillées sont :

- CPU ;
- mémoire ;
- stockage ;
- réseau ;
- base de données ;
- GPU ;
- VRAM ;
- pipelines ;
- observabilité.

---

# 17. Disponibilité

Références :

```text
../../../30-INFRASTRUCTURE/08-High-Availability.md
../../../80-OPERATIONS/06-Availability-Management.md
```

Le pilotage distingue :

```text
Logical HA
```

et :

```text
Physical HA
```

Une architecture peut être logiquement redondée tout en conservant un point de défaillance physique.

---

# 18. Gouvernance du scope

Le scope doit rester cohérent avec :

- objectifs ;
- temps disponible ;
- référentiel ;
- infrastructure ;
- capacité d'exploitation.

Principe :

```text
More Technology
       !=
More Value
```

Le projet doit éviter :

- scope creep ;
- technologies inutiles ;
- implémentations sans preuve ;
- documentation non alignée.

---

# 19. Gestion des dépendances

Exemples de dépendances :

```text
Infrastructure
    |
    v
Kubernetes
    |
    v
Platform Services
    |
    v
Applications / Data / AI
```

Pour le DR :

```text
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
Platform Services
    |
    v
Applications
    |
    v
AI
```

Le planning doit respecter cet ordre.

---

# 20. Pilotage Data

Les travaux Data sont organisés autour de :

```text
Model
  |
  v
Ingestion
  |
  v
Transformation
  |
  v
Quality
  |
  v
Metadata
  |
  v
Consumption
```

L'objectif n'est pas uniquement de charger des données mais de construire une chaîne démontrable.

---

# 21. Pilotage AI / ML

Le lifecycle ML suit :

```text
Code
 |
 v
Training
 |
 v
Evaluation
 |
 v
MLflow
 |
 v
Approval
 |
 v
Deployment
 |
 v
Monitoring
```

Les étapes de gouvernance doivent être séparées des étapes purement techniques.

---

# 22. Pilotage de la qualité

La qualité du projet est évaluée à plusieurs niveaux.

```text
Code Quality
Data Quality
Architecture Quality
Security Quality
Operational Quality
Documentation Quality
```

Les preuves proviennent de :

- tests ;
- CI ;
- métriques ;
- Data Quality ;
- documentation ;
- ADR ;
- observabilité.

---

# 23. Gestion des incidents comme retour projet

Les incidents techniques sont utilisés comme sources d'amélioration.

Cycle :

```text
Incident
  |
  v
Diagnosis
  |
  v
Correction
  |
  v
Root Cause
  |
  v
Documentation
  |
  v
Architecture Improvement
```

Les incidents ne sont donc pas uniquement des interruptions.

Ils génèrent du feedback.

---

# 24. Boucle d'amélioration continue

Le modèle de pilotage complet est :

```text
PLAN
 |
 v
IMPLEMENT
 |
 v
MEASURE
 |
 v
EVALUATE
 |
 v
DECIDE
 |
 v
IMPROVE
 |
 +--------> PLAN
```

---

# 25. Artefacts de pilotage

Les principales preuves du pilotage sont :

```text
Project Constitution
Project Vision
Business Objectives
Architecture Roadmap
Risk Register
ADR
Technical Debt Register
Change Management
RACI
Planning
Decision Matrix
Documentation
```

---

# 26. Preuves disponibles

| Preuve | Statut |
|---|---|
| Project Constitution | DISPONIBLE |
| Vision | DISPONIBLE |
| Business Objectives | DISPONIBLE |
| Architecture Roadmap | DISPONIBLE |
| Risk Management | DISPONIBLE |
| Decision Governance | DISPONIBLE |
| ADR | DISPONIBLES |
| Technical Debt Management | DISPONIBLE |
| Change Management | DISPONIBLE |
| RACI | À CENTRALISER DANS LES PREUVES |
| Planning détaillé | À CENTRALISER |
| Journal de décisions | À RÉFÉRENCER |
| Matrice de décision | À RÉFÉRENCER |

---

# 27. Preuves complémentaires à intégrer

Les preuves existantes du projet devront être référencées ou copiées dans la structure de preuve si nécessaire :

```text
RACI.md
NOTE-DE-CADRAGE.md
JOURNAL-DE-DECISIONS.md
MATRICE-DECISION.md
```

Ces éléments sont particulièrement importants pour la soutenance.

---

# 28. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Objectives
   |
   v
Scope
   |
   v
Planning
   |
   v
Responsibilities
   |
   v
Risks
   |
   v
Decisions
   |
   v
Execution
   |
   v
Evidence
```

et constater que les choix du projet ont été pilotés et non improvisés.

---

# 29. Statut actuel

| Domaine | Statut |
|---|---|
| Cadrage | DOCUMENTÉ |
| Vision | DOCUMENTÉE |
| Objectifs | DOCUMENTÉS |
| Architecture Roadmap | DOCUMENTÉE |
| Risques | DOCUMENTÉS |
| Décisions | DOCUMENTÉES |
| ADR | DISPONIBLES |
| Dette technique | DOCUMENTÉE |
| Change management | DOCUMENTÉ |
| RACI | EXISTANT / À CENTRALISER |
| Planning | À CENTRALISER |
| Evidence runtime | À COMPLÉTER |

---

# 30. Conclusion

Le pilotage du projet repose sur une combinaison de :

```text
Business Objectives
        +
Architecture
        +
Risk Management
        +
Decision Governance
        +
Roadmap
        +
Change Management
        +
Evidence
```

La cible est un pilotage :

```text
Traceable
Risk-aware
Architecture-driven
Evidence-based
Iterative
```

---

**BC01 / C4 — Pilotage projet : DOCUMENTATION BASELINE COMPLETE**