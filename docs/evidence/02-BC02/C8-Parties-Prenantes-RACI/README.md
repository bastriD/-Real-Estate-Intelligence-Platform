# BC02 — C8 — Parties prenantes & RACI

**Bloc de compétences :** BC02  
**Compétence :** C8 — Identifier, organiser et engager les parties prenantes du projet  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Baseline documentaire — responsabilités à consolider dans la preuve finale

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves démontrant que les parties prenantes du projet sont :

- identifiées ;
- classifiées ;
- associées à des responsabilités ;
- impliquées dans les décisions ;
- informées selon leur rôle ;
- reliées aux livrables ;
- reliées aux risques ;
- reliées aux validations.

Le modèle général est :

```text
Stakeholders
     |
     v
Roles
     |
     v
Responsibilities
     |
     v
RACI
     |
     v
Decisions
     |
     v
Execution
     |
     v
Validation
```

---

# 2. Documents de référence

Le principal livrable associé est :

```text
RACI.md
```

Autres documents utiles :

```text
NOTE-DE-CADRAGE.md
JOURNAL-DE-DECISIONS.md
MATRICE-DECISION.md
```

Documents de gouvernance :

```text
../../../95-GOVERNANCE/01-Governance-Architecture.md
../../../95-GOVERNANCE/02-Architecture-Governance.md
../../../95-GOVERNANCE/03-Decision-Governance.md
../../../95-GOVERNANCE/04-Risk-Management.md
```

Documents Foundation :

```text
../../../00-FOUNDATION/Project-Constitution.md
../../../00-FOUNDATION/02-Project-Vision.md
../../../00-FOUNDATION/03-Business-Objectives.md
```

---

# 3. Définition d'une partie prenante

Une partie prenante est toute personne, rôle ou groupe :

- affecté par le projet ;
- participant au projet ;
- prenant une décision ;
- fournissant des données ;
- exploitant un service ;
- validant un résultat ;
- portant un risque ;
- portant une responsabilité.

Le projet distingue les rôles de la personne physique qui les assume.

---

# 4. Parties prenantes principales

Les rôles conceptuels incluent :

```text
Business User
Business Owner
Project Owner
Architecture
Platform / DevOps
Application Engineering
Data Engineering
AI / MLOps
Security
Governance
Operations / SRE
Compliance / RGPD
```

Dans le contexte d'un projet individuel ou d'une petite équipe, plusieurs rôles peuvent être portés par la même personne.

Cela ne supprime pas la nécessité de définir clairement les responsabilités.

---

# 5. Parties prenantes métier

## Business User

Responsabilités possibles :

- exprimer le besoin ;
- utiliser l'application ;
- valider l'utilité métier ;
- remonter les problèmes ;
- participer à l'acceptation.

---

## Business Owner

Responsabilités :

- valider la finalité métier ;
- prioriser la valeur ;
- arbitrer certains besoins ;
- valider les résultats métier.

---

# 6. Architecture

Le rôle Architecture est responsable de :

- cohérence globale ;
- principes d'architecture ;
- choix technologiques ;
- ADR ;
- architecture cible ;
- évolution ;
- dette d'architecture.

Responsabilité principale :

```text
Ensure that local decisions
remain coherent
with the global platform.
```

---

# 7. Platform / DevOps

Responsabilités :

- infrastructure ;
- Kubernetes ;
- GitOps ;
- CI/CD ;
- networking ;
- ingress ;
- platform services ;
- automation ;
- runtime reliability.

Exemples :

```text
Kubernetes
Argo CD
GitLab Runner
Ingress
cert-manager
Platform configuration
```

---

# 8. Application Engineering

Responsabilités :

- business APIs ;
- frontend lorsque applicable ;
- application logic ;
- validation ;
- integration ;
- testing ;
- application observability.

---

# 9. Data Engineering

Responsabilités :

- data ingestion ;
- data model ;
- SQL ;
- Airflow ;
- dbt ;
- warehouse ;
- analytics ;
- Data Quality.

---

# 10. Data Governance

Responsabilités :

- ownership ;
- glossary ;
- classification ;
- lineage ;
- metadata ;
- Data Quality governance.

Technologie principale :

```text
OpenMetadata
```

---

# 11. AI / MLOps

Responsabilités :

- training ;
- experiments ;
- evaluation ;
- model lifecycle ;
- MLflow ;
- Ollama ;
- AI services ;
- RAG ;
- AI monitoring.

---

# 12. Security

Responsabilités :

- security architecture ;
- IAM ;
- RBAC ;
- TLS ;
- secrets ;
- network security ;
- application security ;
- Kubernetes security ;
- AI security.

---

# 13. Governance

Responsabilités :

- architecture governance ;
- decision governance ;
- risk management ;
- compliance ;
- technical debt ;
- governance as code ;
- evidence.

---

# 14. Operations / SRE

Responsabilités :

- incidents ;
- problems ;
- availability ;
- capacity ;
- backup ;
- restore ;
- DR ;
- SLO ;
- operational monitoring.

---

# 15. Compliance / RGPD

Responsabilités :

- processing register ;
- purpose ;
- legal basis ;
- retention ;
- personal data classification ;
- rights of persons ;
- compliance evidence.

---

# 16. Matrice pouvoir / intérêt

Les parties prenantes peuvent être analysées selon deux axes :

```text
Power
+
Interest
```

Matrice :

```text
                    HIGH INTEREST
                          |
          Keep Informed   |   Manage Closely
                          |
LOW POWER ----------------+---------------- HIGH POWER
                          |
           Monitor        |   Keep Satisfied
                          |
                    LOW INTEREST
```

---

# 17. Exemple de classification

| Partie prenante | Pouvoir | Intérêt | Stratégie |
|---|---|---|---|
| Business Owner | Élevé | Élevé | Manage closely |
| Business User | Moyen | Élevé | Keep informed |
| Architecture | Élevé | Élevé | Manage closely |
| Platform | Élevé | Élevé | Manage closely |
| Data | Moyen/Élevé | Élevé | Manage closely |
| Security | Élevé | Moyen/Élevé | Keep satisfied / consult |
| Governance | Élevé | Moyen/Élevé | Consult |
| Operations | Moyen | Élevé | Keep informed / consult |

Cette matrice doit être adaptée au contexte réel.

---

# 18. RACI

Le projet utilise le modèle :

```text
R = Responsible
A = Accountable
C = Consulted
I = Informed
```

---

# 19. Responsible

Le rôle `R` réalise le travail.

Exemple :

```text
Data Pipeline
R = Data Engineering
```

---

# 20. Accountable

Le rôle `A` porte la responsabilité finale de la décision ou du résultat.

Il doit idéalement n'y avoir qu'un `A` principal par activité critique.

---

# 21. Consulted

Le rôle `C` participe à la décision ou apporte son expertise.

Exemple :

```text
AI data usage
AI / MLOps = R
Security = C
Data Governance = C
```

---

# 22. Informed

Le rôle `I` doit recevoir l'information mais n'est pas nécessairement impliqué dans l'exécution.

---

# 23. RACI — Architecture

| Activité | Business | Architecture | Platform | Data | AI | Security | Governance |
|---|---|---|---|---|---|---|---|
| Architecture globale | C | R/A | C | C | C | C | C |
| Architecture Infrastructure | I | A | R | I | I | C | I |
| Architecture Data | C | A | C | R | C | C | C |
| Architecture AI | C | A | C | C | R | C | C |
| Architecture Security | I | C | C | C | C | R/A | C |
| Governance Architecture | I | C | C | C | C | C | R/A |

---

# 24. RACI — Infrastructure

| Activité | Platform | Security | Operations | Architecture |
|---|---|---|---|---|
| Proxmox | R/A | C | C | I |
| Kubernetes | R/A | C | C | C |
| Networking | R/A | C | C | C |
| Ingress | R | C | C | A |
| TLS | R | A/C | I | C |
| Capacity | R | I | A/C | C |

---

# 25. RACI — Data

| Activité | Data | Business | Platform | Governance | Security |
|---|---|---|---|---|---|
| Data Model | R/A | C | I | C | I |
| Ingestion | R | I | C | I | I |
| Transformation | R/A | C | I | C | I |
| Data Quality | R | C | I | A/C | I |
| Metadata | R | I | C | A | I |
| Classification | C | C | I | R/A | C |
| Data Security | C | I | C | C | R/A |

---

# 26. RACI — AI / ML

| Activité | AI/MLOps | Data | Platform | Security | Governance | Business |
|---|---|---|---|---|---|---|
| Training | R/A | C | C | I | I | I |
| Evaluation | R | C | I | C | A/C | C |
| Model Registry | R/A | I | C | I | C | I |
| Local Inference | R | I | C | C | I | I |
| AI Security | C | C | C | R/A | C | I |
| AI Governance | R | C | I | C | A | C |
| Human Validation | C | I | I | I | C | R/A |

---

# 27. RACI — DevOps / GitOps

| Activité | Platform | Developer | Security | Architecture | Governance |
|---|---|---|---|---|---|
| Git repository | A | R | I | I | I |
| CI pipeline | R/A | C | C | C | I |
| GitOps | R/A | C | I | C | I |
| Deployment | R | C | I | A | I |
| Rollback | R | C | I | A | I |
| Policy validation | R | I | C | C | A/C |

---

# 28. RACI — Backup / PRA

| Activité | Platform | Data | AI | Operations | Business | Security |
|---|---|---|---|---|---|---|
| Kubernetes backup | R | I | I | A | I | C |
| Database backup | C | R | I | A | I | C |
| ML artifacts backup | C | I | R | A | I | C |
| Restore infrastructure | R | I | I | A | I | C |
| Restore database | C | R | I | A | I | C |
| Technical validation | R | R | R | A | I | C |
| Business validation | I | C | C | C | R/A | I |

---

# 29. RACI — Incident

| Activité | Operations | Platform | Data | AI | Security | Business |
|---|---|---|---|---|---|---|
| Detection | R/A | C | C | C | C | I |
| Technical diagnosis | A | R | R | R | C | I |
| Security incident | C | C | C | C | R/A | I |
| Mitigation | A | R | R | R | C | I |
| Business validation | C | I | C | C | I | R/A |
| Postmortem | R | C | C | C | C | I |

---

# 30. RACI — RGPD

| Activité | Business | Data | Security | Governance / Compliance | Platform |
|---|---|---|---|---|---|
| Define purpose | R/A | C | I | C | I |
| Identify personal data | C | R | C | A | I |
| Security measures | I | C | R | A/C | C |
| Retention | C | R | I | A | I |
| Rights process | R | C | I | A | I |
| Evidence | I | C | C | R/A | C |

---

# 31. Processus de décision

Le processus recommandé est :

```text
Issue
 |
 v
Responsible prepares proposal
 |
 v
Consulted stakeholders review
 |
 v
Accountable decides
 |
 v
Informed stakeholders notified
 |
 v
Decision recorded
```

Pour les décisions d'architecture :

```text
+
ADR
```

---

# 32. Engagement des parties prenantes

L'engagement ne signifie pas envoyer toutes les informations à tout le monde.

Il faut adapter la communication.

```text
Stakeholder
     |
     v
Information Need
     |
     v
Communication Method
     |
     v
Frequency
```

---

# 33. Plan de communication

Exemple :

| Partie prenante | Information | Fréquence / événement |
|---|---|---|
| Business | Progress / decisions | Milestones |
| Architecture | Architecture changes | As needed |
| Platform | Technical changes | Continuous |
| Data | Data changes | Sprint / change |
| Security | Security-impacting changes | Before release |
| Governance | Risks / decisions | Review cycles |
| Operations | Operational readiness | Before deployment |

---

# 34. Types de communication

La communication peut utiliser :

```text
Documentation
Git
Merge Requests
Issue Tracker
Meetings
Decision Journal
ADR
Dashboards
Reports
```

La communication importante doit rester traçable.

---

# 35. Git comme outil de collaboration

Git permet de tracer :

- auteur ;
- date ;
- changement ;
- review ;
- historique.

Les Merge Requests permettent :

```text
Proposal
  |
  v
Review
  |
  v
Discussion
  |
  v
Approval
  |
  v
Merge
```

---

# 36. ADR et parties prenantes

Un ADR doit permettre de comprendre :

- le problème ;
- les alternatives ;
- la décision ;
- les conséquences.

Selon la décision, différents rôles doivent être consultés.

Exemple :

```text
Change CNI
    |
    +--> Platform
    +--> Security
    +--> Architecture
    +--> Operations
```

---

# 37. Risques et parties prenantes

Chaque risque important doit avoir un responsable.

```text
Risk
 |
 v
Owner
 |
 v
Treatment
 |
 v
Monitoring
```

Un risque sans propriétaire a une forte probabilité de rester sans traitement.

---

# 38. Data Ownership

Les datasets importants doivent progressivement disposer d'un ownership.

Exemple :

```text
Data Asset
   |
   +-- Business Owner
   |
   +-- Technical Owner
   |
   +-- Steward
```

OpenMetadata peut matérialiser ces responsabilités.

---

# 39. Service Ownership

Les services importants doivent également avoir un propriétaire.

Exemples :

```text
Kubernetes       -> Platform
Airflow          -> Data / Platform
MLflow           -> AI / MLOps
OpenMetadata     -> Data Governance
Prometheus       -> Platform / SRE
Ollama           -> AI / MLOps
```

---

# 40. Escalade

Un processus d'escalade doit exister pour les incidents ou décisions bloquantes.

```text
Issue
 |
 v
Responsible
 |
 v
Cannot Resolve?
 +---+---+
 |       |
NO      YES
 |       |
 v       v
Close   Escalate to Accountable
```

---

# 41. Conflits de priorité

Les conflits sont arbitrés selon :

```text
Business Value
Risk
Architecture Constraints
Deadline
Dependencies
```

Une technologie attractive ne doit pas prendre automatiquement la priorité sur un besoin critique.

---

# 42. Validation métier

Les fonctions métier doivent être validées par le rôle métier approprié.

```text
Technical Success
       !=
Business Acceptance
```

Exemple :

Une API peut retourner HTTP 200 mais fournir un résultat métier incorrect.

---

# 43. Validation Data

La validation Data combine :

```text
Technical Validation
+
Data Quality
+
Business Rules
```

---

# 44. Validation AI

La validation AI peut combiner :

```text
Technical Evaluation
+
Quality Evaluation
+
Security Review
+
Governance
+
Human Review
```

selon le niveau de risque.

---

# 45. Validation sécurité

Les changements avec impact sécurité doivent impliquer le rôle sécurité.

Exemples :

- IAM ;
- secrets ;
- exposition réseau ;
- nouvelles données sensibles ;
- external AI ;
- permissions.

---

# 46. Validation PRA

Une restauration ne doit pas être considérée réussie uniquement parce que la commande s'est terminée.

Elle doit être validée :

```text
Technically
+
Functionally
```

avec participation des rôles concernés.

---

# 47. RACI et petite équipe

Le projet peut être réalisé par une seule personne.

Le RACI reste pertinent car il documente :

```text
Which responsibility is being exercised?
```

et non uniquement :

```text
Which human is doing it?
```

Exemple :

```text
Same Person
   |
   +-- Platform Role
   +-- Data Role
   +-- AI Role
   +-- Architecture Role
```

Les responsabilités restent distinctes.

---

# 48. Preuves disponibles

| Élément | Statut |
|---|---|
| RACI source | EXISTANT |
| Roles architecture | DOCUMENTÉS |
| Roles Data | DOCUMENTÉS |
| Roles AI | DOCUMENTÉS |
| Roles Security | DOCUMENTÉS |
| Roles Operations | DOCUMENTÉS |
| Governance roles | DOCUMENTÉS |
| Data ownership model | DOCUMENTÉ |
| Decision process | DOCUMENTÉ |
| Communication model | DOCUMENTÉ |
| Stakeholder evidence | À CONSOLIDER |

---

# 49. Preuves complémentaires

Les preuves pertinentes peuvent inclure :

```text
RACI.md
Decision journal
Merge Requests
Git history
Meeting notes
Architecture reviews
Risk ownership
OpenMetadata ownership
Approval records
```

Il n'est pas nécessaire de produire artificiellement des réunions ou validations qui n'ont pas eu lieu.

---

# 50. Matrice livrable → propriétaire

| Livrable | Responsable principal |
|---|---|
| Architecture | Architecture |
| Infrastructure | Platform |
| Data Model | Data |
| Data Pipeline | Data |
| ML Lifecycle | AI/MLOps |
| Security Architecture | Security |
| Risk Register | Governance |
| Backup / Restore | Operations |
| Application | Application |
| Business Acceptance | Business |

---

# 51. Matrice décision → parties prenantes

| Décision | Parties consultées |
|---|---|
| Kubernetes | Architecture / Platform |
| GitOps | Architecture / Platform |
| PostgreSQL | Architecture / Data |
| OpenMetadata | Data / Governance |
| Ollama | AI / Security / Architecture |
| Keycloak target | Security / Architecture / Application |
| Vault target | Security / Platform |
| Vector DB | Data / AI / Architecture |

---

# 52. Critère de réussite

La compétence est démontrée si le jury peut comprendre :

```text
Who
 |
 v
Is responsible for what
 |
 v
Who decides
 |
 v
Who is consulted
 |
 v
Who is informed
 |
 v
How the decision is traced
```

---

# 53. État actuel

```text
Stakeholders identified      COMPLETE
Roles defined                COMPLETE
RACI model                   COMPLETE
Architecture ownership       COMPLETE
Data ownership model         COMPLETE
Decision governance          COMPLETE
Risk ownership concept       COMPLETE
Communication model          COMPLETE
Runtime ownership evidence   TO CONSOLIDATE
Stakeholder proof            TO CONSOLIDATE
```

---

# 54. Conclusion

La gestion des parties prenantes repose sur :

```text
Clear Roles
    +
Explicit Responsibilities
    +
RACI
    +
Traceable Decisions
    +
Appropriate Communication
```

L'objectif est d'éviter :

```text
Everyone is responsible
```

qui signifie souvent :

```text
No one is accountable.
```

---

**BC02 / C8 — Parties prenantes & RACI : DOCUMENTATION BASELINE COMPLETE**