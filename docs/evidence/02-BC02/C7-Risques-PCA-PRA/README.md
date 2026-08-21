# BC02 — C7 — Risques, PCA et PRA

**Bloc de compétences :** BC02  
**Compétence :** C7 — Identifier les risques projet et définir les mesures de continuité et de reprise  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Baseline documentaire — preuves de reprise à consolider

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves démontrant la capacité à :

- identifier les risques ;
- analyser leur impact ;
- définir des mesures de mitigation ;
- organiser la continuité d'activité ;
- préparer la reprise après incident ;
- définir RPO et RTO ;
- tester la restauration ;
- produire des preuves de recoverability.

Le modèle général est :

```text
Risk
 |
 v
Assessment
 |
 v
Mitigation
 |
 +------------+
 |            |
 v            v
Prevention   Recovery
               |
               v
             PCA/PRA
               |
               v
            Evidence
```

---

# 2. Documents de référence

Documents principaux :

```text
../../../95-GOVERNANCE/04-Risk-Management.md
../../../30-INFRASTRUCTURE/10-Disaster-Recovery.md
../../../80-OPERATIONS/07-Backup-and-Restore.md
../../../80-OPERATIONS/08-Business-Continuity.md
../../../80-OPERATIONS/09-Disaster-Recovery.md
```

Diagramme principal :

```text
../../../99-DIAGRAMS/14-Backup-DR-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/14-Backup-DR-Architecture.svg
```

Livrable Fil Rouge associé :

```text
PCA-PRA-MIGRATION.md
```

---

# 3. Définitions

## Risque

Événement potentiel susceptible d'affecter :

- disponibilité ;
- intégrité ;
- confidentialité ;
- performance ;
- planning ;
- conformité ;
- capacité de reprise.

## PCA

Plan de Continuité d'Activité.

Objectif :

```text
Maintain Critical Capability
during
Degraded Conditions
```

## PRA

Plan de Reprise d'Activité.

Objectif :

```text
Restore Critical Capability
after
Major Failure
```

---

# 4. Cycle de gestion des risques

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

Un risque critique peut générer :

- backlog item ;
- contrôle ;
- architecture decision ;
- test ;
- alerting ;
- procédure de reprise.

---

# 5. Critères d'évaluation

Les risques sont évalués selon :

```text
Probability
Impact
Detectability
Exposure
Recovery Complexity
```

Une matrice simple peut être utilisée :

| Probabilité | Impact | Criticité |
|---|---|---|
| Faible | Faible | Faible |
| Faible | Fort | Moyen |
| Moyen | Moyen | Moyen |
| Moyen | Fort | Élevé |
| Fort | Fort | Critique |

---

# 6. Principaux risques infrastructure

## Panne hôte physique

Impact possible :

- perte de plusieurs VMs ;
- perte de nœuds Kubernetes ;
- indisponibilité de services ;
- impact stockage.

Mitigation :

- distribution des workloads ;
- sauvegardes ;
- documentation recovery ;
- HA logique ;
- procédures de reconstruction.

---

# 7. Risque Kubernetes

## Perte control plane

Mitigation :

```text
Multiple Control Planes
+
etcd replication
+
documented recovery
```

## Perte worker

Mitigation :

```text
Multiple Workers
+
Kubernetes Rescheduling
```

---

# 8. Risque réseau

Un incident de routage peut rendre des workers injoignables.

Chaîne :

```text
Routing Failure
      |
      v
Node Connectivity Failure
      |
      v
Kubernetes Communication Failure
      |
      v
Workload / Metrics Impact
```

Mitigation :

- routes documentées ;
- surveillance reachability ;
- monitoring node health ;
- procédure diagnostic réseau.

---

# 9. Risque stockage

Risques :

- saturation ;
- corruption ;
- indisponibilité ;
- perte de volume.

Mitigation :

- capacity monitoring ;
- alerting ;
- backup ;
- retention ;
- cleanup policies ;
- restore testing.

---

# 10. Risque PostgreSQL

Risques :

- corruption ;
- erreur humaine ;
- suppression ;
- panne stockage ;
- mauvaise migration.

Mitigation :

```text
Database Backup
+
Migration Control
+
Validation
+
Restore Procedure
```

---

# 11. Risque Data Quality

Une pipeline techniquement réussie peut produire des données incorrectes.

```text
Pipeline Success
       !=
Data Validity
```

Mitigation :

- dbt tests ;
- OpenMetadata tests ;
- row counts ;
- uniqueness ;
- referential checks ;
- business rules.

---

# 12. Risque MLflow / artifacts

Risques :

- perte metadata ;
- perte artifacts ;
- modèle non reproductible ;
- version active inconnue.

Mitigation :

- backup DB metadata ;
- backup MinIO ;
- Git SHA ;
- model versioning ;
- promotion controls.

---

# 13. Risque AI

Risques :

- saturation GPU ;
- VRAM insuffisante ;
- modèle trop lourd ;
- indisponibilité Ollama ;
- réponse incorrecte ;
- exposition de données.

Mitigation :

- modèles adaptés ;
- quantification ;
- monitoring GPU ;
- local-first ;
- AI governance ;
- human oversight.

---

# 14. Risque secrets

Risques :

- secret dans Git ;
- secret dans logs ;
- fuite CI ;
- mauvaise permission.

Mitigation actuelle :

```text
Kubernetes Secrets
GitLab Protected Variables
Least Privilege
```

Cible :

```text
HashiCorp Vault
```

si le niveau de maturité le justifie.

---

# 15. Risque GitOps

Risques :

- mauvaise configuration versionnée ;
- suppression automatique ;
- sync incorrect ;
- drift manuel.

Mitigation :

- Merge Requests ;
- CI validation ;
- protected branches ;
- Argo CD health ;
- rollback via Git.

---

# 16. Risque observabilité

Risques :

- absence de métriques ;
- logs inutilisables ;
- alert fatigue ;
- absence de traces ;
- cardinalité excessive.

Mitigation :

- standards telemetry ;
- alert strategy ;
- SLO ;
- retention ;
- structured logging.

---

# 17. Risque projet

Risques :

```text
Scope Creep
Too Many Technologies
Insufficient Evidence
Late Testing
Late Defense Preparation
```

Mitigation :

```text
Prioritized Backlog
MoSCoW
Milestones
Evidence Phase
Scope Deferment
```

---

# 18. Registre synthétique

| ID | Risque | Probabilité | Impact | Traitement |
|---|---|---|---|---|
| R-01 | Panne hôte | Moyen | Fort | Backup + HA |
| R-02 | Saturation stockage | Moyen | Fort | Monitoring + cleanup |
| R-03 | Routage défaillant | Moyen | Fort | Routes + monitoring |
| R-04 | Perte PostgreSQL | Faible/Moyen | Critique | Backup + restore |
| R-05 | Data Quality | Moyen | Fort | Tests |
| R-06 | GPU saturation | Moyen | Moyen/Fort | Capacity controls |
| R-07 | Secret exposé | Faible/Moyen | Critique | Secret controls |
| R-08 | GitOps misconfig | Moyen | Fort | MR + CI + rollback |
| R-09 | Restore non testé | Moyen | Critique | Restore exercise |
| R-10 | Scope trop large | Fort | Fort | Priorisation |
| R-11 | Preuves insuffisantes | Moyen | Fort | Evidence plan |
| R-12 | AI data exposure | Faible/Moyen | Critique | Local-first + governance |

---

# 19. PCA — principe

Le PCA définit comment maintenir les fonctions essentielles.

Exemple :

```text
Normal Service
      |
      v
Failure
      |
      v
Degraded Mode
      |
      v
Critical Functions Maintained
```

La continuité n'implique pas forcément un fonctionnement nominal complet.

---

# 20. Fonctions critiques

Exemples de capacités critiques :

```text
Kubernetes Control Plane
Data Access
PostgreSQL
Git / GitOps
Core Application
Authentication
Observability
Backup Access
```

L'AI peut être classée comme non critique pour certains cas d'usage.

---

# 21. Graceful Degradation AI

Principe :

```text
AI unavailable
      |
      v
Core business functionality
should remain available
where possible.
```

Cela réduit la criticité de certains services AI.

---

# 22. PCA Data

En cas de dégradation :

```text
Analytics unavailable
```

peut être acceptable temporairement si :

```text
Core Operational Data
```

reste disponible.

La criticité doit être définie par service.

---

# 23. PRA — ordre de reprise

L'ordre de reprise retenu est :

```text
1. Infrastructure
        |
        v
2. Network / DNS
        |
        v
3. Kubernetes
        |
        v
4. Git / GitOps
        |
        v
5. Data
        |
        v
6. Platform Services
        |
        v
7. Applications
        |
        v
8. AI
        |
        v
9. Validation
```

---

# 24. Pourquoi cet ordre

Les couches hautes dépendent des couches basses.

```text
Application
   depends on
Data / Platform

Platform
   depends on
Kubernetes

Kubernetes
   depends on
Infrastructure / Network
```

Restaurer dans le mauvais ordre augmente le temps de reprise.

---

# 25. Sources de reconstruction

Certaines données sont reconstructibles depuis Git.

Exemples :

```text
Kubernetes manifests
Helm values
Argo CD applications
Documentation
ADR
Governance definitions
```

D'autres ne le sont pas.

Exemples :

```text
Database state
ML artifacts
User-generated data
Metadata state
```

---

# 26. Git comme recovery source

Git protège notamment :

```text
Code
Configuration
Desired State
Architecture
Governance Definitions
```

Mais :

```text
Git
!=
Database Backup
```

---

# 27. Backup PostgreSQL

Le backup doit protéger :

- schémas ;
- tables ;
- data ;
- metadata critique.

Une stratégie peut inclure :

```text
Logical Backup
+
Scheduled Backup
+
Retention
+
Restore Validation
```

---

# 28. Velero

Velero protège les ressources Kubernetes et certains états persistants selon la configuration.

Rôle :

```text
Kubernetes Objects
     |
     v
Velero
     |
     v
Backup Repository
```

Velero ne remplace pas automatiquement les backups applicatifs.

---

# 29. MinIO / artifact backup

Les artifacts ML doivent être protégés si nécessaires à la reproductibilité.

```text
MLflow
  |
  v
MinIO
  |
  v
Artifact Backup
```

---

# 30. OpenMetadata recovery

OpenMetadata contient un état de gouvernance.

Peuvent devoir être restaurés :

- metadata DB ;
- ownership ;
- glossary ;
- classification ;
- quality definitions ;
- relationships.

Les définitions Governance as Code peuvent contribuer à la reconstruction.

---

# 31. RPO

Recovery Point Objective :

```text
Maximum Acceptable Data Loss
```

Exemple :

```text
RPO = 24h
```

signifie qu'une perte maximale de 24 heures de données peut être tolérée.

Les valeurs réelles doivent être définies selon la criticité.

---

# 32. RTO

Recovery Time Objective :

```text
Maximum Acceptable Recovery Time
```

Les objectifs réels doivent être comparés au temps mesuré pendant les tests de restauration.

---

# 33. RPO / RTO par criticité

Exemple de modèle :

| Niveau | RPO | RTO |
|---|---|---|
| Critique | Faible | Faible |
| Important | Moyen | Moyen |
| Standard | Plus large | Plus large |

Les valeurs définitives ne doivent pas être inventées.

---

# 34. Test de restauration

Le test minimum suit :

```text
Create Known State
       |
       v
Backup
       |
       v
Modify / Remove
       |
       v
Restore
       |
       v
Validate
```

---

# 35. Validation

La validation doit vérifier :

- objet restauré ;
- contenu ;
- schéma ;
- intégrité ;
- accessibilité ;
- dépendances ;
- fonctionnalité.

---

# 36. Mesures de preuve

Un test de reprise doit produire :

```text
Start Time
Backup ID
Restore Start
Restore End
Validation Result
Observed RPO
Observed RTO
Errors
Corrective Actions
```

---

# 37. Exemple de preuve

```text
Backup:
velero backup create ...

Restore:
velero restore create ...

Validation:
kubectl get ...
SQL query ...
Application smoke test ...
```

Les commandes réelles seront enregistrées lorsqu'elles sont exécutées.

---

# 38. Scénario — Perte namespace

Exemple :

```text
Namespace Lost
     |
     v
Velero Restore
     |
     v
Resources Recreated
     |
     v
Application Validation
```

---

# 39. Scénario — Perte database

```text
Database Failure
     |
     v
Recreate Service
     |
     v
Restore Database
     |
     v
Integrity Check
     |
     v
Application Validation
```

---

# 40. Scénario — Perte GitOps

```text
Cluster State Lost
      |
      v
Restore Kubernetes
      |
      v
Restore / Access Git
      |
      v
Install Argo CD
      |
      v
Root Application
      |
      v
Reconciliation
```

---

# 41. Scénario — Perte AI host

```text
AI Host Lost
    |
    v
Reinstall OS / Drivers
    |
    v
Install Ollama
    |
    v
Restore Model Definitions
    |
    v
Pull / Restore Models
    |
    v
Inference Test
```

Le core business peut rester disponible si AI est non critique.

---

# 42. Business Continuity

Pendant la reprise, certaines capacités peuvent fonctionner en mode dégradé.

Exemples :

```text
No AI
but
Core API available

No analytics
but
Operational data available

No dashboards
but
services running
```

---

# 43. Communication incident

Un PRA doit également prévoir :

```text
Incident Detected
      |
      v
Assess Severity
      |
      v
Notify Stakeholders
      |
      v
Recovery
      |
      v
Status Updates
      |
      v
Closure
```

---

# 44. Responsabilités PRA

Rôles conceptuels :

| Rôle | Responsabilité |
|---|---|
| Platform | Infrastructure/Kubernetes |
| Data | Database restore |
| AI | Model / AI restore |
| Security | Security validation |
| Business | Business validation |
| Governance | Evidence / risk update |

---

# 45. Retour d'expérience

Après incident ou exercice :

```text
Recovery Exercise
      |
      v
Results
      |
      v
Gaps
      |
      v
Corrective Actions
      |
      v
Risk Register Update
```

---

# 46. Observabilité du PRA

Les systèmes de monitoring contribuent à déterminer :

- heure de panne ;
- impact ;
- disponibilité ;
- retour à la normale.

Sources :

```text
Prometheus
Grafana
Loki
Tempo
```

---

# 47. Governance as Code et PRA

Certaines règles de reprise peuvent être versionnées.

Exemples :

```text
RPO targets
RTO targets
Backup requirements
Criticality
Ownership
Restore-test frequency
```

---

# 48. Preuves disponibles

| Élément | Statut |
|---|---|
| Risk Management | DOCUMENTÉ |
| Backup architecture | DOCUMENTÉE |
| DR architecture | DOCUMENTÉE |
| Business Continuity | DOCUMENTÉE |
| Velero | DISPONIBLE |
| RPO/RTO model | DOCUMENTÉ |
| Recovery order | DOCUMENTÉ |
| PlantUML DR | DISPONIBLE |
| Real restore test | À CONSOLIDER |
| Measured RTO | À PRODUIRE |
| Measured RPO | À PRODUIRE |

---

# 49. Preuves à créer

Ce dossier devra progressivement recevoir des preuves réelles telles que :

```text
01-risk-register.md
02-backup-output.txt
03-restore-output.txt
04-restore-validation.txt
05-rpo-rto-measurement.md
06-pra-test-report.md
```

Seulement après exécution réelle.

---

# 50. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Risk
 |
 v
Impact
 |
 v
Mitigation
 |
 v
Continuity
 |
 v
Recovery Plan
 |
 v
Restore Test
 |
 v
Measured Evidence
```

---

# 51. État actuel

```text
Risk identification        COMPLETE
Risk documentation         COMPLETE
Mitigation architecture    COMPLETE
PCA documentation          COMPLETE
PRA documentation          COMPLETE
Backup architecture        COMPLETE
Recovery sequence          COMPLETE
Restore execution          TO COMPLETE
Measured RPO/RTO           TO COMPLETE
Recovery evidence          TO COMPLETE
```

---

# 52. Conclusion

La stratégie du projet repose sur :

```text
Prevent
   +
Detect
   +
Backup
   +
Restore
   +
Validate
   +
Measure
   +
Improve
```

Le principe fondamental est :

```text
Backup
without
Restore Validation
=
Unproven Recovery Capability
```

---

**BC02 / C7 — Risques, PCA et PRA : DOCUMENTATION BASELINE COMPLETE**