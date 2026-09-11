# BC02 — C2 — Backlog priorisé

**Bloc de compétences :** BC02  
**Compétence :** C2 — Construire, organiser et prioriser le backlog du projet  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Backlog actualisé à partir des réalisations documentées — recette finale à consolider

---

# 1. Objectif

Ce document présente la structuration et la priorisation du backlog du projet.

Le backlog transforme :

```text
Business Needs
      |
      v
Architecture Requirements
      |
      v
Capabilities
      |
      v
Epics
      |
      v
Features
      |
      v
Tasks
      |
      v
Evidence
```

L'objectif est d'éviter une réalisation guidée uniquement par les technologies.

Chaque élément doit répondre à :

- un besoin ;
- une dépendance ;
- un risque ;
- une exigence ;
- ou une preuve attendue.

---

# 2. Sources de référence

Le backlog est dérivé notamment de :

```text
../../../00-FOUNDATION/02-Project-Vision.md
../../../00-FOUNDATION/03-Business-Objectives.md
../../../00-FOUNDATION/04-Architecture-Decisions.md
../../../00-FOUNDATION/Infrastructure-Improvement-Plan.md

../../../10-BUSINESS/01-Business-Architecture.md

../../../30-INFRASTRUCTURE/
../../../40-DATA/
../../../50-AI/
../../../60-SECURITY/
../../../70-DEVOPS/
../../../80-OPERATIONS/
../../../90-OBSERVABILITY/
../../../95-GOVERNANCE/
```

Les décisions structurantes sont tracées dans :

```text
../../../98-ADR/
```

---

# 3. Principes de priorisation

La priorité d'un élément dépend de plusieurs facteurs.

```text
Priority
   =
Business Value
   +
Risk Reduction
   +
Technical Dependency
   +
Evaluation Requirement
   +
Feasibility
```

Les travaux nécessaires à d'autres composants sont réalisés avant les fonctionnalités qui en dépendent.

---

# 4. Méthode MoSCoW

Le backlog utilise quatre niveaux.

## MUST

Élément indispensable au projet ou à la démonstration d'une compétence.

## SHOULD

Élément important mais non bloquant pour un premier incrément.

## COULD

Amélioration utile si le temps et les ressources le permettent.

## WON'T / LATER

Élément volontairement différé.

---

# 5. Niveaux de priorité

Une priorité opérationnelle est également associée aux éléments.

```text
P0 = Bloquant / fondation
P1 = Critique
P2 = Important
P3 = Amélioration
P4 = Future
```

---

# 6. Ordre des dépendances

L'ordre architectural général est :

```text
Foundation
    |
    v
Infrastructure
    |
    v
Kubernetes
    |
    v
DevOps / GitOps
    |
    v
Data
    |
    +------------+
    |            |
    v            v
Application     AI / ML
    |            |
    +------+-----+
           |
           v
Security / Governance
           |
           v
Observability / Operations
           |
           v
Evidence / Validation
```

Security, Governance et Observability sont transverses, mais certaines de leurs implémentations dépendent des composants sous-jacents.

---

# 7. Epic 1 — Foundation & Architecture

**Priorité : P0**  
**MoSCoW : MUST**

Objectif :

Construire une architecture documentée et gouvernée avant l'industrialisation.

## Backlog

- [x] Définir la vision projet
- [x] Définir les objectifs métier
- [x] Définir les principes d'architecture
- [x] Définir les choix technologiques
- [x] Documenter les décisions d'architecture
- [x] Créer les ADR
- [x] Documenter l'architecture Enterprise
- [x] Documenter l'architecture Infrastructure
- [x] Documenter l'architecture Data
- [x] Documenter l'architecture AI
- [x] Documenter l'architecture Security
- [x] Documenter l'architecture Observability
- [x] Documenter l'architecture Operations
- [x] Documenter la Governance
- [x] Générer les diagrammes PlantUML
- [x] Générer les SVG

---

# 8. Epic 2 — Infrastructure

**Priorité : P0**  
**MoSCoW : MUST**

Objectif :

Fournir la fondation d'exécution de la plateforme.

## Backlog

- [x] Infrastructure physique disponible
- [x] Virtualisation disponible
- [x] Déployer les VMs Kubernetes
- [x] Configurer le réseau
- [x] Configurer le stockage
- [x] Documenter l'architecture physique
- [x] Documenter l'architecture virtuelle
- [x] Documenter le réseau
- [x] Documenter le stockage
- [x] Documenter le compute
- [x] Documenter la capacité
- [x] Documenter les principes HA
- [ ] Consolider les preuves runtime infrastructure
- [ ] Consolider les métriques de capacité

---

# 9. Epic 3 — Kubernetes

**Priorité : P0**  
**MoSCoW : MUST**

Objectif :

Disposer d'une plateforme d'orchestration stable.

## Backlog

- [x] Cluster kubeadm
- [x] Trois control planes
- [x] Workers Kubernetes
- [x] Flannel CNI
- [x] NGINX Ingress
- [x] cert-manager
- [x] CoreDNS
- [x] Metrics / monitoring integration
- [x] Corriger les problèmes de routage workers
- [x] Documenter Kubernetes
- [ ] Centraliser `kubectl get nodes`
- [ ] Centraliser `kubectl get pods -A`
- [ ] Centraliser les preuves de ressources
- [ ] Ajouter les preuves de disponibilité

---

# 10. Epic 4 — GitOps

**Priorité : P0**  
**MoSCoW : MUST**

Objectif :

Faire de Git la source de vérité du desired state.

## Backlog

- [x] GitLab disponible
- [x] Argo CD installé
- [x] Root application
- [x] Auto-sync
- [x] Self-heal
- [x] Prune
- [x] Repositories GitOps
- [x] Documentation GitOps
- [x] ADR Argo CD
- [ ] Centraliser les preuves Argo CD
- [ ] Capturer les applications synchronisées
- [ ] Démontrer une modification Git → Kubernetes

---

# 11. Epic 5 — CI/CD

**Priorité : P1**  
**MoSCoW : MUST**

Objectif :

Automatiser validation, build et intégration.

## Backlog

- [x] GitLab CI disponible
- [x] GitLab Runner disponible
- [x] Documentation CI/CD
- [x] ADR GitLab CI/CD
- [ ] Consolider une pipeline complète
- [x] Ajouter validation automatique
- [x] Ajouter tests
- [ ] Ajouter contrôles de sécurité pertinents
- [ ] Produire une preuve CI réussie

---

# 12. Epic 6 — Data Platform

**Priorité : P1**  
**MoSCoW : MUST**

Objectif :

Construire la chaîne Data principale.

## Backlog

- [x] PostgreSQL
- [x] Schéma RAW
- [x] Schéma STAGING
- [x] Schéma WAREHOUSE
- [x] Schéma ANALYTICS
- [x] Airflow
- [x] dbt
- [x] Pipelines ETL
- [x] Vues analytiques
- [x] Data Quality
- [x] Documentation Data
- [x] Consolider MCD métier
- [x] Consolider les migrations versionnées dans `database/migrations/`
- [ ] Ajouter preuves `EXPLAIN ANALYZE`
- [ ] Ajouter comparaison avant/après index
- [ ] Consolider preuve OLTP
- [ ] Consolider preuve OLAP

---

# 13. Epic 7 — Metadata & Data Governance

**Priorité : P1**  
**MoSCoW : MUST**

Objectif :

Rendre la Data Platform gouvernable.

## Backlog

- [x] OpenMetadata installé
- [x] PostgreSQL ingestion
- [x] Airflow ingestion
- [x] dbt ingestion
- [x] Profiling
- [x] Data Quality integration
- [x] Documentation metadata
- [x] ADR OpenMetadata
- [ ] Consolider screenshots / runtime evidence
- [ ] Démontrer lineage
- [ ] Démontrer ownership
- [ ] Démontrer classification
- [ ] Relier gouvernance et RGPD

---

# 14. Epic 8 — MLOps

**Priorité : P1**  
**MoSCoW : MUST**

Objectif :

Industrialiser le lifecycle ML.

## Backlog

- [x] MLflow installé
- [x] Tracking server
- [x] Experiments
- [x] Metrics
- [x] Parameters
- [x] Artifacts
- [x] Model versions
- [x] Model registry
- [x] Airflow integration
- [x] Documentation MLOps
- [x] ADR MLflow
- [ ] Consolider preuve experiment
- [ ] Consolider preuve model registry
- [ ] Démontrer promotion modèle
- [ ] Relier modèle → artifact → version

---

# 15. Epic 9 — Local AI

**Priorité : P1**  
**MoSCoW : MUST**

Objectif :

Fournir une capacité d'inférence locale.

## Backlog

- [x] AI host disponible
- [x] NVIDIA GPU disponible
- [x] CUDA
- [x] Ollama
- [x] Qwen
- [x] API Ollama accessible
- [x] Test d'inférence distante
- [x] Documentation Local AI
- [x] ADR Ollama
- [ ] Centraliser preuve API
- [ ] Capturer consommation GPU
- [ ] Documenter benchmark minimal
- [ ] Documenter limites VRAM

---

# 16. Epic 10 — RAG

**Priorité : P4 — différé**
**MoSCoW : WON'T / LATER**

La stratégie SI C2 conserve cette extension comme `DEFERRED / REQUIREMENT-DRIVEN`. Elle ne bloque pas la consolidation du parcours immobilier actuel.

Objectif :

Construire une capacité de recherche augmentée par génération.

## Backlog

- [x] Architecture RAG documentée
- [x] AI governance documentée
- [x] AI security documentée
- [ ] Définir corpus métier
- [ ] Définir stratégie chunking
- [ ] Définir embeddings
- [ ] Comparer pgvector / Qdrant
- [ ] Implémenter ingestion
- [ ] Implémenter retrieval
- [ ] Implémenter génération
- [ ] Évaluer pertinence
- [ ] Tester sécurité documentaire

---

# 17. Epic 11 — Application

**Priorité : P1**  
**MoSCoW : MUST**

Objectif :

Exposer les capacités métier de la plateforme.

## Backlog

- [x] Architecture applicative documentée
- [ ] Formaliser cas d'usage métier
- [x] Définir API métier
- [x] Implémenter endpoints prioritaires
- [x] Ajouter validation Pydantic
- [x] Ajouter tests API
- [x] Ajouter health endpoints
- [x] Ajouter observabilité
- [x] Ajouter authentification lorsque requise
- [ ] Ajouter interface utilisateur si nécessaire

Les réalisations correspondent aux modules de `src/api/`, aux tests de `tests/backend/` et à la documentation sécurité du 9 septembre 2026.

Les compléments métier restant ouverts comprennent :

- [ ] Consolider le contrôle de propriété des ressources et des auteurs de demandes
- [ ] Réaliser le calcul de rémunération et ses règles d'éligibilité
- [ ] Formaliser le renouvellement des mandats et les règles temporelles associées
- [ ] Démontrer le parcours complet avec PostgreSQL

Sources :

```text
../../../95-GOVERNANCE/STARTERPACK-GAP-REVIEW-2026-09-09.md
../../../95-GOVERNANCE/SCRIPT-REVIEW-2026-09-09.md
../../../60-SECURITY/SECURITY-RBAC-AUDIT-IMPLEMENTATION-EVIDENCE.md
```

---

# 18. Epic 12 — Security

**Priorité : P1**  
**MoSCoW : MUST**

Objectif :

Sécuriser la plateforme progressivement.

## Backlog

- [x] Kubernetes RBAC
- [x] TLS / cert-manager
- [x] Security architecture
- [x] Kubernetes security documentation
- [x] Secrets architecture
- [x] Zero Trust principles
- [ ] Consolider matrice RBAC
- [ ] Consolider preuves TLS
- [ ] Auditer secrets
- [ ] Ajouter contrôles CI pertinents
- [ ] Définir politiques runtime prioritaires
- [ ] Étudier Keycloak lorsque requis
- [ ] Étudier Vault lorsque requis

---

# 19. Epic 13 — Observability

**Priorité : P1**  
**MoSCoW : MUST**

Objectif :

Rendre les services observables.

## Backlog

- [x] Prometheus
- [x] Grafana
- [x] Loki
- [x] Tempo
- [x] OpenTelemetry
- [x] Alerting architecture
- [x] Documentation complète
- [ ] Consolider dashboards
- [ ] Consolider alertes
- [ ] Définir SLI prioritaires
- [ ] Définir SLO prioritaires
- [ ] Produire preuves métriques
- [ ] Produire preuves logs
- [ ] Produire preuves traces

---

# 20. Epic 14 — Backup & Disaster Recovery

**Priorité : P1**  
**MoSCoW : MUST**

Objectif :

Démontrer la capacité de reprise.

## Backlog

- [x] Architecture DR documentée
- [x] Backup strategy documentée
- [x] Velero présent
- [x] RPO / RTO conceptualisés
- [x] Exécuter backup PostgreSQL contrôlé
- [x] Exécuter restore PostgreSQL isolé
- [x] Comparer les volumes métier sélectionnés avant et après restauration
- [x] Mesurer la durée de `pg_restore`
- [x] Documenter la preuve et le résultat de restauration
- [x] Définir le CronJob permanent et sa publication GitOps
- [ ] Consolider la preuve d'exécution du CronJob permanent
- [ ] Formaliser et appliquer la rétention / ILM
- [ ] Superviser les échecs et l'ancienneté des sauvegardes
- [ ] Mesurer le RTO applicatif complet

Ces cases s'appuient sur le rapport existant `../../../PCA PRA/PCA-PRA-POSTGRESQL.md`. Le temps d'environ six secondes concerne uniquement la restauration PostgreSQL testée.

Principe :

```text
Backup
without
Restore Test
=
Incomplete Evidence
```

---

# 21. Epic 15 — Governance as Code

**Priorité : P1**  
**MoSCoW : MUST**

Objectif :

Transformer les règles documentaires en contrôles automatisables.

## Backlog

- [x] Governance architecture
- [x] Governance as Code repository
- [x] Kubernetes governance job
- [x] Decision governance
- [x] Risk management
- [x] Technical debt management
- [x] Architecture roadmap
- [x] ADR Governance as Code
- [ ] Consolider preuves d'exécution
- [ ] Relier policies → controls → evidence
- [ ] Ajouter validation CI

---

# 22. Epic 16 — RGPD

**Priorité : P1**  
**MoSCoW : MUST**

Objectif :

Démontrer la prise en compte des données personnelles.

## Backlog

- [x] Data Governance documentée
- [x] Data Security documentée
- [x] Compliance documentée
- [ ] Identifier données personnelles
- [ ] Documenter finalités
- [ ] Documenter base légale
- [ ] Documenter rétention
- [ ] Documenter droits des personnes
- [ ] Consolider registre RGPD
- [ ] Relier RGPD à OpenMetadata
- [ ] Documenter anonymisation / pseudonymisation si applicable

---

# 23. Epic 17 — Eco-conception

**Priorité : P2**  
**MoSCoW : SHOULD**

Objectif :

Limiter l'empreinte inutile de la plateforme.

## Backlog

- [x] Eco-conception identifiée
- [ ] Consolider note d'éco-conception
- [ ] Documenter choix de modèles AI adaptés
- [ ] Documenter consommation des ressources
- [ ] Documenter optimisation stockage
- [ ] Documenter rétention des logs
- [ ] Documenter scaling raisonné

---

# 24. Epic 18 — Accessibility

**Priorité : P2**  
**MoSCoW : MUST pour les livrables concernés**

Objectif :

Prendre en compte l'accessibilité dans les interfaces et livrables.

## Backlog

- [ ] Identifier exigences applicables
- [ ] Définir critères d'accessibilité
- [ ] Appliquer aux interfaces développées
- [ ] Tester les composants concernés
- [ ] Documenter les résultats

---

# 25. Epic 19 — Evidence & Evaluation

**Priorité : P0**  
**MoSCoW : MUST**

Objectif :

Transformer les réalisations en preuves vérifiables.

## Backlog

- [x] Structure `docs/evidence/`
- [x] BC01 evidence structure
- [x] BC02 evidence structure
- [x] BC03 evidence structure
- [x] BC05 evidence structure
- [x] Cross-cutting evidence structure
- [ ] Runtime commands
- [ ] Screenshots utiles
- [ ] SQL evidence
- [x] Rapports locaux de tests du 9 septembre 2026 dans BC03 / C6
- [ ] CI evidence
- [ ] Data Quality evidence
- [ ] ML evidence
- [ ] Backup / Restore evidence
- [ ] Final traceability matrix

---

# 26. Epic 20 — Soutenance

**Priorité : P1**  
**MoSCoW : MUST**

Objectif :

Préparer une démonstration cohérente du projet.

## Backlog

- [ ] Construire trame soutenance
- [ ] Sélectionner diagrammes
- [ ] Sélectionner preuves
- [ ] Préparer scénario de démonstration
- [ ] Préparer questions architecture
- [ ] Préparer questions Data
- [ ] Préparer questions AI
- [ ] Préparer questions sécurité
- [ ] Préparer questions RGPD
- [ ] Préparer questions PCA / PRA
- [ ] Préparer démonstration technique
- [ ] Répéter soutenance

---

# 27. Backlog consolidé par priorité

La présence d'une implémentation ne clôt pas automatiquement sa recette. Les cases cochées ci-dessus distinguent explicitement code, tests locaux et expérience runtime documentée.

Les modules d'entraînement et de comparaison ML existent dans `src/ai/matching/`. Leur intégration éventuelle au classement de l'API reste distincte du matching déterministe actuellement utilisé. Les extensions ML ne remplacent pas les travaux métier de rémunération identifiés dans la revue StarterPack.

## P0 — Fondation / bloquant

```text
Architecture
Infrastructure
Kubernetes
GitOps
Evidence structure
```

## P1 — Critique

```text
CI/CD
Data Platform
Data Governance
MLOps
Local AI
Application
Security
Observability
Backup / DR
Governance as Code
RGPD
Soutenance
```

## P2 — Important

```text
Eco-conception
Accessibility
Advanced optimization
```

## P3 — Améliorations

```text
Advanced automation
Extended dashboards
Additional integrations
Developer experience
```

## P4 — Future

```text
RAG
Kafka
Dedicated Vector DB if justified
Service Mesh
KEDA
Argo Events
Argo Workflows
Feature Store
AI Gateway
Multi-cluster Kubernetes
```

---

# 28. Technologies volontairement différées

Le backlog contient également des décisions de **ne pas implémenter immédiatement**.

## Kafka

```text
Status: FUTURE
```

Pas de besoin streaming suffisant actuellement.

## Qdrant

```text
Status: CANDIDATE
```

Doit être comparé à PostgreSQL + pgvector.

## Keycloak

```text
Status: TARGET
```

À introduire lorsqu'un IAM central devient nécessaire.

## Vault

```text
Status: TARGET
```

À introduire lorsque le besoin de secrets dynamiques / centralisés le justifie.

---

# 29. Dépendances majeures

Exemple Data :

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
Warehouse
    |
    v
OpenMetadata
    |
    v
Analytics / AI
```

Exemple MLOps :

```text
Data
 |
 v
Training
 |
 v
MLflow
 |
 v
Model Registry
 |
 v
Deployment
 |
 v
Monitoring
```

Exemple RAG :

```text
Governed Documents
       |
       v
Chunking
       |
       v
Embeddings
       |
       v
Vector Storage
       |
       v
Retrieval
       |
       v
LLM
```

---

# 30. Definition of Ready

Une tâche est prête lorsque :

- le besoin est compris ;
- son objectif est défini ;
- ses dépendances sont connues ;
- ses contraintes sont identifiées ;
- son résultat attendu est défini.

```text
Requirement
+
Dependencies
+
Acceptance Criteria
=
READY
```

---

# 31. Definition of Done

Une tâche technique n'est pas considérée terminée uniquement parce qu'elle fonctionne.

Elle doit, selon sa nature, disposer de :

```text
Implementation
+
Test
+
Documentation
+
Observability
+
Security
+
Evidence
```

Pour les décisions structurantes :

```text
+
ADR
```

---

# 32. Critères d'acceptation

Les critères d'acceptation doivent être vérifiables.

Exemple incorrect :

```text
Kubernetes works.
```

Exemple correct :

```text
All expected Kubernetes nodes report Ready
and required platform workloads are running.
```

Autre exemple :

```text
Restore works.
```

devient :

```text
A controlled restore is executed,
the restored object is verified,
and the result is recorded as evidence.
```

---

# 33. Gestion du changement de priorité

La priorité peut évoluer si :

- un incident apparaît ;
- un risque augmente ;
- une dépendance est découverte ;
- un besoin métier change ;
- une exigence d'évaluation manque ;
- une contrainte technique bloque le projet.

Cycle :

```text
New Information
      |
      v
Impact Analysis
      |
      v
Reprioritize
      |
      v
Update Backlog
```

---

# 34. Backlog et dette technique

La dette technique ne doit pas être cachée.

Une limitation connue peut devenir :

```text
Technical Debt
      |
      v
Backlog Item
      |
      v
Priority
      |
      v
Resolution
```

Référence :

```text
../../../95-GOVERNANCE/08-Technical-Debt-Management.md
```

---

# 35. Backlog et risques

Les risques élevés peuvent générer directement des tâches.

Exemple :

```text
Risk:
Backup exists but restore is unverified
             |
             v
Backlog:
Execute controlled restore test
             |
             v
Evidence:
Restore report
```

---

# 36. Backlog et référentiel

Une partie du backlog est directement liée aux preuves attendues pour l'évaluation.

Cela inclut notamment :

```text
Audit
Veille
Architecture
Project Management
MCD
Migration SQL
SQL Optimization
OLAP
3V
AI Model
AI Program
Application
Tests
RGPD
Eco-conception
Accessibility
AI Sovereignty / Security
```

L'objectif est d'éviter :

```text
Implemented
but
Not Demonstrated
```

---

# 37. État synthétique

| Epic | Priorité | Statut global |
|---|---:|---|
| Foundation | P0 | AVANCÉ |
| Infrastructure | P0 | AVANCÉ |
| Kubernetes | P0 | OPÉRATIONNEL |
| GitOps | P0 | OPÉRATIONNEL |
| CI/CD | P1 | PARTIEL / À PROUVER |
| Data Platform | P1 | AVANCÉ |
| Metadata | P1 | OPÉRATIONNEL |
| MLOps | P1 | OPÉRATIONNEL |
| Local AI | P1 | OPÉRATIONNEL |
| RAG | P2 | PARTIEL / TARGET |
| Application | P1 | À CONSOLIDER |
| Security | P1 | PARTIEL |
| Observability | P1 | OPÉRATIONNEL |
| Backup / DR | P1 | À PROUVER |
| Governance as Code | P1 | AVANCÉ |
| RGPD | P1 | À CONSOLIDER |
| Eco-conception | P2 | À CONSOLIDER |
| Accessibility | P2 | À TRAITER |
| Evidence | P0 | EN COURS |
| Soutenance | P1 | À FAIRE |

---

# 38. Critère de réussite

La compétence est démontrée si le jury peut comprendre :

```text
Requirements
      |
      v
Backlog
      |
      v
Priorities
      |
      v
Dependencies
      |
      v
Implementation
      |
      v
Validation
```

et constater que le projet a été piloté selon des priorités explicites.

---

# 39. Conclusion

Le backlog constitue le lien opérationnel entre :

```text
Business
Architecture
Risk
Implementation
Evaluation
```

La priorisation vise d'abord :

```text
Foundations
    |
    v
Critical Capabilities
    |
    v
Evidence
    |
    v
Enhancements
```

Les technologies futures ne sont introduites que lorsqu'un besoin réel justifie leur coût et leur complexité.

---

**BC02 / C2 — Backlog priorisé : DOCUMENTATION BASELINE COMPLETE**
