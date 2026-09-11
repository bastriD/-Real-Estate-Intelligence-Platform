# BC01 — C1 — Audit de l'existant

**Bloc de compétences :** BC01  
**Compétence :** C1 — Auditer l'existant et identifier les écarts  
**Projet :** Real Estate Intelligence Platform — Chasse Immobilière  
**Plateforme :** Enterprise AI Platform  
**Statut :** EVIDENCED — cartographie graphique à finaliser pour la soutenance  
**Dernière mise à jour :** 2026-09-10

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves relatives à l'audit du système d'information existant.

Il démontre la capacité à :

- analyser un système existant ;
- identifier ses composants et leurs responsabilités ;
- comprendre les interactions entre infrastructure, application, données et opérations ;
- cartographier les flux ;
- identifier les limites techniques ;
- identifier et qualifier les risques ;
- documenter les écarts entre l'existant et les besoins ;
- proposer des axes d'amélioration ;
- préparer les décisions d'architecture suivantes.

Ce dossier ne duplique pas l'ensemble de la documentation du projet.

Il répond à la question :

> Quelles preuves démontrent que le SI existant a été analysé, cartographié et soumis à une analyse de risques avant de définir ses évolutions ?

La logique suivie est :

```text
Existing System
      |
      v
Observed State
      |
      v
Current-State Map
      |
      v
Strengths / Weaknesses
      |
      v
Risks
      |
      v
Gaps
      |
      v
Improvement Requirements
```

---

# 2. Périmètre de l'audit

L'audit couvre les domaines suivants :

```text
Infrastructure
    |
    +-- Physical hosts
    +-- Virtualization
    +-- Kubernetes
    +-- Network
    +-- Storage
    +-- Compute
    +-- High Availability
    +-- Capacity

Application
    |
    +-- FastAPI Business API
    +-- Authentication
    +-- RBAC
    +-- Business services
    +-- Matching / Recommendation
    +-- Audit trail
    +-- Dependencies

Data
    |
    +-- PostgreSQL
    +-- OLTP
    +-- Raw / Staging
    +-- Data Warehouse
    +-- Analytics
    +-- Airflow
    +-- dbt
    +-- Data Quality
    +-- Metadata
    +-- Lineage

AI / ML
    |
    +-- Deterministic production matching
    +-- ML experimentation
    +-- MLflow
    +-- Local GPU infrastructure
    +-- Local LLM inference
    +-- AI governance boundary

Security
    |
    +-- Application authentication
    +-- Application RBAC
    +-- Kubernetes RBAC
    +-- Secrets
    +-- Network exposure
    +-- Kubernetes controls
    +-- Auditability

Operations
    |
    +-- Backup
    +-- Restore
    +-- Availability
    +-- PRA / Disaster Recovery

Observability
    |
    +-- Metrics
    +-- Logs
    +-- Traces
    +-- Dashboards
    +-- Alerts

Governance
    |
    +-- Decisions
    +-- Risks
    +-- Technical debt
    +-- Governance as Code
    +-- Evidence
```

---

# 3. Sources documentaires utilisées

L'audit s'appuie sur la documentation d'architecture et de gouvernance existante.

## Fondation

```text
../../../00-FOUNDATION/00-Executive-Summary.md
../../../00-FOUNDATION/01-Architecture-Principles.md
../../../00-FOUNDATION/02-Project-Vision.md
../../../00-FOUNDATION/03-Business-Objectives.md
../../../00-FOUNDATION/04-Architecture-Decisions.md
../../../00-FOUNDATION/05-Technology-Stack.md
../../../00-FOUNDATION/Infrastructure-Improvement-Plan.md
```

## Infrastructure

```text
../../../30-INFRASTRUCTURE/01-Infrastructure-Architecture.md
../../../30-INFRASTRUCTURE/02-Physical-Architecture.md
../../../30-INFRASTRUCTURE/03-Virtual-Infrastructure.md
../../../30-INFRASTRUCTURE/04-Kubernetes-Architecture.md
../../../30-INFRASTRUCTURE/05-Network-Architecture.md
../../../30-INFRASTRUCTURE/06-Storage-Architecture.md
../../../30-INFRASTRUCTURE/07-Compute-Architecture.md
../../../30-INFRASTRUCTURE/08-High-Availability.md
../../../30-INFRASTRUCTURE/09-Capacity-Planning.md
../../../30-INFRASTRUCTURE/10-Disaster-Recovery.md
```

## Application

```text
../../../20-APPLICATION/01-Application-Architecture.md
```

## Data

```text
../../../40-DATA/01-Data-Architecture.md
../../../40-DATA/02-Data-Model.md
../../../40-DATA/03-Data-Warehouse.md
../../../40-DATA/04-Data-Governance.md
../../../40-DATA/05-Data-Quality.md
../../../40-DATA/06-Data-Lineage.md
../../../40-DATA/07-Metadata-Management.md
../../../40-DATA/09-Data-Lifecycle.md
../../../40-DATA/10-Data-Security.md
```

## AI

```text
../../../50-AI/01-AI-Platform-Architecture.md
../../../50-AI/02-LLM-Architecture.md
../../../50-AI/03-MLOps-Architecture.md
../../../50-AI/04-RAG-Architecture.md
../../../50-AI/07-AI-Governance.md
../../../50-AI/08-AI-Security.md
../../../50-AI/09-AI-Observability.md
```

## Security

```text
../../../60-SECURITY/01-Security-Architecture.md
../../../60-SECURITY/02-Identity-and-Access-Management.md
../../../60-SECURITY/03-Zero-Trust-Architecture.md
../../../60-SECURITY/04-Secret-Management.md
../../../60-SECURITY/05-Network-Security.md
../../../60-SECURITY/08-Kubernetes-Security.md
../../../60-SECURITY/09-Compliance-and-Risk.md
```

## Operations

```text
../../../80-OPERATIONS/05-Capacity-Management.md
../../../80-OPERATIONS/06-Availability-Management.md
../../../80-OPERATIONS/07-Backup-and-Restore.md
../../../80-OPERATIONS/08-Business-Continuity.md
../../../80-OPERATIONS/09-Disaster-Recovery.md
```

## Observability

```text
../../../90-OBSERVABILITY/01-Observability-Architecture.md
../../../90-OBSERVABILITY/02-Metrics-Architecture.md
../../../90-OBSERVABILITY/03-Logging-Architecture.md
../../../90-OBSERVABILITY/04-Distributed-Tracing.md
../../../90-OBSERVABILITY/07-Alerting-Strategy.md
```

## Governance

```text
../../../95-GOVERNANCE/01-Governance-Architecture.md
../../../95-GOVERNANCE/03-Decision-Governance.md
../../../95-GOVERNANCE/04-Risk-Management.md
../../../95-GOVERNANCE/08-Technical-Debt-Management.md
../../../95-GOVERNANCE/10-Architecture-Roadmap.md
../../../95-GOVERNANCE/11-Risk-Register.md
```

## ADR

```text
../../../98-ADR/
```

## Diagrammes

```text
../../../99-DIAGRAMS/
```

---

# 4. Cartographie du SI actuel

La cartographie de l'état actuel est maintenue sous forme d'Architecture as Code.

Source :

```text
02-Cartographie-SI-Actuel.puml
```

Sortie destinée à la documentation et à la soutenance :

```text
02-Cartographie-SI-Actuel.svg
```

Le diagramme représente notamment :

```text
Users
  |
  v
FastAPI
  |
  +-- Authentication / JWT
  +-- RBAC
  +-- Matching / Recommendation
  |
  v
PostgreSQL

Engineering
  |
  v
GitLab
  |
  v
GitLab CI
  |
  v
lab-gitops
  |
  v
Argo CD
  |
  v
Kubernetes

Data Platform
  |
  +-- Airflow
  +-- dbt
  +-- OpenMetadata
  +-- MLflow

Observability
  |
  +-- Prometheus
  +-- Grafana
  +-- Loki
  +-- Tempo
  +-- OpenTelemetry

External / Dedicated
  |
  +-- MinIO
  +-- AI Node / NVIDIA GPU
```

Le contenu architectural de cette cartographie est établi.

La disposition graphique du diagramme reste à optimiser pour la version finale de la soutenance.

---

# 5. Synthèse de l'existant

Le SI repose sur une infrastructure locale et auto-hébergée.

Architecture générale :

```text
Physical Infrastructure
        |
        v
Proxmox VE
        |
        v
Virtual Machines
        |
        v
Kubernetes kubeadm HA
        |
        +-- Business Application
        +-- Data Platform
        +-- MLOps
        +-- Metadata / Governance
        +-- Observability
        +-- Operations
```

Les principales technologies actuellement utilisées comprennent :

- Kubernetes ;
- PostgreSQL ;
- GitLab ;
- GitLab CI ;
- Argo CD ;
- Airflow ;
- dbt ;
- OpenMetadata ;
- MLflow ;
- Prometheus ;
- Grafana ;
- Loki ;
- Tempo ;
- OpenTelemetry ;
- MinIO.

Une capacité IA locale séparée existe également :

```text
AI Node
   |
   +-- NVIDIA GTX 1080
   +-- 8 GB VRAM
   +-- CUDA
   +-- Ollama
   +-- Qwen3 8B
```

Cette capacité IA ne doit pas être confondue avec le moteur de matching actuellement utilisé en production par l'application immobilière.

---

# 6. Infrastructure et Kubernetes

## Points forts

- infrastructure virtualisée ;
- Kubernetes kubeadm HA opérationnel ;
- plusieurs control planes ;
- plusieurs workers ;
- GitOps avec Argo CD ;
- NGINX Ingress ;
- cert-manager ;
- observabilité centralisée ;
- workloads Data / AI / MLOps ;
- capacité de calcul GPU locale.

## Limites observées

- ressources physiques finies ;
- certains failure domains restent liés au homelab ;
- HA logique et HA physique ne sont pas équivalentes ;
- stockage local à considérer comme une contrainte structurante ;
- capacité GPU limitée ;
- dépendance au réseau sous-jacent.

## Incident réseau observé

Des nœuds Kubernetes ont rencontré des problèmes de communication à la suite d'une incohérence de routage.

La dépendance identifiée est :

```text
Underlay Routing
      |
      v
Node Connectivity
      |
      v
Flannel
      |
      v
Pod Network
      |
      v
Kubernetes Services
```

L'incident a démontré qu'un cluster Kubernetes fonctionnel reste dépendant de la cohérence du routage sous-jacent.

Il a également conduit à identifier le risque réseau comme un risque formel du SI.

---

# 7. Architecture applicative

L'application métier est une API FastAPI exposant les principales capacités du domaine immobilier.

Les domaines fonctionnels comprennent notamment :

- clients ;
- demandes ;
- mandats ;
- biens ;
- présentations ;
- recommandations ;
- visites ;
- authentification.

Architecture simplifiée :

```text
User
  |
  v
FastAPI
  |
  +-- Authentication
  +-- RBAC
  +-- Business Services
  +-- Matching / Recommendation
  +-- Audit
  |
  v
PostgreSQL
```

L'application constitue désormais une composante réelle du SI et pas uniquement une architecture cible.

---

# 8. Architecture Data

L'architecture Data actuelle distingue plusieurs couches ayant des responsabilités différentes.

Le flux logique principal est :

```text
Sources / Generated Data
          |
          v
RAW
Bronze
          |
          v
STAGING
Silver
          |
          v
REAL_ESTATE
OLTP métier
          |
          v
WAREHOUSE
Gold
          |
          v
ANALYTICS
Marts
```

Les responsabilités sont séparées :

```text
Airflow      = orchestration

dbt          = transformation / tests

PostgreSQL   = persistence OLTP + analytical schemas

OpenMetadata = catalog / lineage / profiling / governance
```

## Points forts

- séparation des couches ;
- modèle OLTP métier ;
- Data Warehouse ;
- marts analytiques ;
- orchestration Airflow ;
- transformations dbt ;
- Data Quality ;
- metadata management ;
- profiling ;
- lineage ;
- gouvernance OpenMetadata.

## Écarts restant à traiter

Pour les compétences suivantes du référentiel, certaines preuves devront encore être consolidées :

- performances SQL ;
- indexation ;
- `EXPLAIN` / `EXPLAIN ANALYZE` ;
- justification OLTP / OLAP ;
- stratégie de partitionnement ;
- justification de l'absence ou de la pertinence du sharding.

Ces éléments ne bloquent pas l'audit C1 mais alimentent les compétences d'architecture et Data suivantes.

---

# 9. Matching, AI et ML

Une distinction importante est maintenue entre :

1. le moteur de matching utilisé actuellement par l'application ;
2. l'expérimentation Machine Learning ;
3. l'infrastructure IA locale.

## 9.1 Matching de production

Le chemin actuel repose sur des règles métier déterministes.

```text
Demande Version
      |
      v
Hard Business Eligibility
      |
      v
Eligible Population
      |
      v
Weighted Ranking
      |
      v
Recommendation
      |
      v
Presentation
```

Les règles d'éligibilité métier restent déterministes.

Un modèle ML ne doit pas supprimer silencieusement les contraintes métier obligatoires.

## 9.2 Expérimentation ML

Le projet dispose de composants permettant :

- construction de datasets d'entraînement ;
- génération de labels à partir du ground truth ;
- évaluation ;
- expérimentation ;
- suivi dans MLflow.

Ces capacités constituent une base MLOps.

Elles ne doivent pas être présentées comme un modèle ML déjà promu en production.

## 9.3 Infrastructure IA locale

Une infrastructure GPU dédiée existe :

```text
NVIDIA GTX 1080
8 GB VRAM
      |
      v
Ollama
      |
      v
Qwen3 8B
```

L'inférence GPU locale a été validée.

Cependant :

> le GPU local n'est pas actuellement le moteur de matching de production de l'application Real Estate.

Cette distinction évite de confondre capacité technique disponible et usage métier réellement industrialisé.

---

# 10. Sécurité applicative

L'état actuel comprend désormais une authentification applicative propre à l'application Real Estate.

La source d'identité applicative est :

```text
real_estate.utilisateur
```

Le mécanisme d'authentification repose notamment sur :

```text
Credentials
    |
    v
Argon2id
    |
    v
JWT
    |
    v
Role-Based Access Control
```

Les rôles applicatifs sont :

```text
ADMIN
CLIENT
CHASSEUR
SERVICE
```

Des restrictions par rôle sont appliquées aux routes métier.

La plateforme utilise également :

- Kubernetes RBAC ;
- Kubernetes Secrets ;
- GitLab CI variables ;
- TLS ;
- cert-manager ;
- contrôles de sécurité au niveau des images et des workloads selon leur maturité.

## Limites actuelles

Le RBAC par rôle est opérationnel, mais l'autorisation fine basée sur la propriété des ressources métier reste à renforcer.

Exemples :

```text
CLIENT
  |
  +-- access only own business resources

CHASSEUR
  |
  +-- access only assigned business resources
```

Cette granularité constitue une évolution de sécurité et non une capacité à présenter comme totalement finalisée.

## Technologies cibles non déployées

Les technologies suivantes restent des possibilités d'évolution :

```text
Keycloak
HashiCorp Vault
```

Elles ne font pas partie de l'état courant démontré.

---

# 11. Auditabilité métier

L'application dispose d'un mécanisme d'audit reposant sur :

```text
real_estate.audit_log
```

L'audit est intégré au traitement applicatif afin de conserver la traçabilité des opérations métier concernées.

La couverture démontrée comprend notamment des opérations sur :

- présentations ;
- recommandations créant des présentations ;
- visites ;
- mandats.

Le mécanisme permet de conserver des informations telles que :

- table concernée ;
- opération ;
- identifiant de l'enregistrement ;
- utilisateur ;
- ancienne valeur ;
- nouvelle valeur ;
- contexte ;
- date de l'événement.

La couverture d'audit n'est pas considérée comme universelle.

Des domaines supplémentaires peuvent encore être intégrés selon les besoins de conformité et de traçabilité.

---

# 12. Observabilité

La plateforme dispose des principaux piliers d'observabilité :

```text
Metrics -> Prometheus

Logs    -> Loki

Traces  -> Tempo
```

complétés par :

```text
OpenTelemetry
Grafana
Alertmanager
```

L'API FastAPI expose également des métriques techniques et métier.

Les métriques métier couvrent notamment le fonctionnement du moteur de recommandation.

Cette instrumentation permet d'observer :

- requêtes ;
- erreurs ;
- durée ;
- candidats éligibles ;
- candidats sélectionnés ;
- présentations créées ;
- présentations déjà existantes.

## Limites

La présence des outils ne signifie pas automatiquement :

- couverture exhaustive ;
- SLO complets ;
- alertes parfaites ;
- corrélation totale logs / metrics / traces ;
- gouvernance exhaustive des métriques.

L'audit distingue donc :

```text
Tool deployed
      !=
Operational maturity complete
```

---

# 13. Backup, Restore et PRA

La situation actuelle ne se limite plus à une stratégie documentaire.

Un chemin de restauration PostgreSQL a été effectivement validé.

Le flux démontré est :

```text
PostgreSQL
     |
     v
Backup
     |
     v
External MinIO
     |
     v
Isolated Restore
     |
     v
Integrity Validation
```

Le stockage de sauvegarde est externalisé vers MinIO.

Un CronJob Kubernetes permanent permet l'exécution périodique du backup PostgreSQL via le processus GitOps.

La capacité de restauration a été testée dans un environnement isolé afin de ne pas confondre :

```text
Backup Created
      !=
Data Recoverable
```

Le projet dispose donc désormais d'une preuve de recoverability pour ce périmètre.

## Limites résiduelles

Les améliorations possibles comprennent notamment :

- politique de rétention / ILM ;
- détection des sauvegardes trop anciennes ;
- alerting spécifique backup ;
- mesure plus complète du RTO ;
- tests périodiques automatisés ;
- amélioration des failure domains ;
- gestion plus avancée des secrets.

Le RPO déduit de la planification quotidienne constitue un objectif de conception et non un SLA métier mesuré.

---

# 14. Gouvernance et risques

Le projet utilise une approche de gouvernance versionnée dans Git.

La logique cible est :

```text
Governance Definition
        |
        v
Git
        |
        v
CI
        |
        v
GitOps / Automation
        |
        v
Runtime
        |
        v
Evidence
```

La méthodologie de gestion des risques est décrite dans :

```text
../../../95-GOVERNANCE/04-Risk-Management.md
```

Le registre de risques formel est maintenu dans :

```text
../../../95-GOVERNANCE/11-Risk-Register.md
```

Le registre constitue la source de vérité pour :

- identifiant du risque ;
- domaine ;
- description ;
- probabilité ;
- impact ;
- score ;
- traitement ;
- risque résiduel ;
- responsable ;
- statut ;
- date de revue.

Les risques identifiés couvrent notamment :

- défaillance d'hôte physique ;
- saturation ou défaillance du stockage ;
- indisponibilité d'un nœud Kubernetes ;
- incohérence réseau / DNS ;
- perte ou corruption PostgreSQL ;
- échec ou vieillissement des sauvegardes ;
- dépassement des objectifs de restauration ;
- perte d'observabilité ;
- faux sentiment de confiance lié à la Data Quality ;
- ambiguïté de lineage ;
- exposition de secrets ;
- autorisation fine incomplète ;
- couverture d'audit incomplète ;
- cycle métier mandat incomplet ;
- rémunération chasseur incomplète ;
- dérive documentation / architecture ;
- indisponibilité du nœud IA ;
- confusion entre expérimentation ML et production ;
- expansion excessive du périmètre ;
- preuves de certification insuffisantes ou incohérentes.

---

# 15. Principaux écarts identifiés

| Domaine | État actuel | Écart / risque résiduel | Orientation |
|---|---|---|---|
| Infrastructure | Kubernetes HA logique | Failure domains physiques | Réduire le risque et surveiller la capacité |
| Réseau | LAN + routage + Flannel | Sensibilité aux incohérences de routage | Baseline réseau cohérente et surveillée |
| Stockage | local-path + stockage externe ciblé | Capacité / failure domains | Capacity management et externalisation ciblée |
| Application | FastAPI opérationnel | Certaines règles métier restent à compléter | Compléter uniquement les besoins métier réels |
| Auth | Argon2id + JWT + RBAC | Ownership fine-grained incomplète | Renforcer l'autorisation métier |
| Audit | audit_log opérationnel sur périmètre défini | Couverture non universelle | Étendre selon risque / conformité |
| Data | OLTP + Warehouse + Analytics | Preuves SQL avancées à consolider | EXPLAIN, indexation et justification architecture |
| Metadata | OpenMetadata | Gouvernance encore perfectible | Automatisation ciblée |
| Matching | Moteur déterministe opérationnel | ML non encore production | Évaluer ML sans casser l'éligibilité métier |
| AI | GPU + Ollama disponibles | GPU limité à 8 GB VRAM | Modèles adaptés et quantification |
| Observability | Stack complète | SLO / alerting à renforcer | Observability governance |
| Backup | PostgreSQL → MinIO | Retention / alerting / automatisation des restore tests | Industrialiser le PRA |
| Restore | Restore isolé validé | Tests périodiques à industrialiser | Recovery testing continu |
| Secrets | K8s Secrets / CI variables | Pas de gestion centralisée avancée | Vault éventuellement à terme |
| IAM cible | RBAC applicatif local | Pas d'IAM central | Keycloak uniquement si besoin justifié |
| Governance | Documentation + GitOps + risk register | Automatisation partielle | Governance as Code progressive |

---

# 16. État actuel, cible et éléments différés

L'audit distingue explicitement trois catégories.

## CURRENT

Capacités actuellement implémentées ou démontrées :

```text
Kubernetes kubeadm HA
GitLab / GitLab CI
GitOps / Argo CD
FastAPI
PostgreSQL
Application Authentication
JWT / RBAC
Audit Log
Airflow
dbt
OpenMetadata
MLflow experimentation
Prometheus
Grafana
Loki
Tempo
OpenTelemetry
MinIO backup
PostgreSQL restore validation
Local NVIDIA GPU
Ollama / Qwen inference capability
```

## TARGET / IMPROVEMENT

Évolutions pouvant être justifiées par les écarts :

```text
Fine-grained authorization
Extended audit coverage
Backup retention
Backup staleness alerting
Automated recovery tests
SQL performance evidence
Index optimization
SLO consolidation
Security automation
Governance automation
Production ML evaluation
```

## DEFERRED / OUT OF CURRENT ARCHITECTURE

Les technologies suivantes ne doivent pas être présentées comme déployées dans le SI actuel :

```text
RAG
MCP
Qdrant
Keycloak
Vault integration
Kafka
Spark
Iceberg
Trino
JupyterHub
Lakehouse
Databricks
Snowflake
Kubeflow
React frontend
```

Elles ne seront introduites que si un besoin fonctionnel, architectural ou de certification le justifie.

---

# 17. Axes d'amélioration issus de l'audit

Les améliorations retenues ne consistent pas à ajouter le maximum de technologies.

Le principe est :

```text
Observed Gap
     |
     v
Risk / Requirement
     |
     v
Justified Improvement
     |
     v
Implementation
     |
     v
Evidence
```

Les axes principaux sont :

- consolidation de la sécurité applicative ;
- autorisation fine ;
- couverture d'audit ;
- amélioration du PRA ;
- gouvernance des sauvegardes ;
- SQL performance evidence ;
- architecture OLTP / OLAP ;
- gouvernance Data ;
- gouvernance AI ;
- industrialisation MLOps ;
- SLO / alerting ;
- Architecture as Code ;
- Documentation as Code ;
- Diagrams as Code ;
- Governance as Code ;
- Evidence as Code lorsque pertinent.

---

# 18. Preuves techniques disponibles

L'audit ne repose pas uniquement sur de la documentation déclarative.

Des preuves runtime et techniques ont été utilisées au cours du projet.

Elles comprennent notamment des vérifications relatives à :

```text
Kubernetes nodes
Kubernetes workloads
Argo CD applications
GitLab CI deployments
PostgreSQL schemas and migrations
Business API
Authentication
RBAC
Audit trail
Matching / recommendations
Airflow
dbt
OpenMetadata
MLflow
Prometheus metrics
Grafana dashboards
Backup jobs
MinIO backup storage
Isolated PostgreSQL restore
Integrity validation
```

La hiérarchie de confiance utilisée est :

```text
Runtime
   >
Repository / Source
   >
CI
   >
GitOps Desired State
   >
Documentation
   >
Historical Assumption
```

Une capacité n'est donc pas considérée comme runtime-verified uniquement parce qu'elle apparaît dans un document d'architecture.

---

# 19. Gestion des preuves

Les preuves de certification doivent correspondre à des résultats réellement produits par le projet.

Exemples de preuves acceptables :

```text
kubectl get nodes
kubectl get pods -A
kubectl top nodes
kubectl top pods -A
Argo CD application status
GitLab CI logs
PostgreSQL queries
Migration history
API responses
Authentication tests
RBAC tests
Audit records
Airflow DAG status
MLflow runs
OpenMetadata ingestion / lineage
Prometheus queries
Grafana dashboards
Backup job status
Restore validation
EXPLAIN ANALYZE
Data Quality results
```

Les fichiers de preuve ne doivent jamais être créés artificiellement pour donner l'impression qu'une vérification a été réalisée.

Chaque preuve doit être rattachable à :

```text
Requirement
    |
    v
Implementation
    |
    v
Execution
    |
    v
Observed Result
    |
    v
Evidence
```

---

# 20. Architecture cible issue de l'audit

L'audit ne conduit pas à remplacer l'ensemble du SI.

L'objectif est de faire évoluer progressivement l'existant.

```text
Business
   |
   v
Application
   |
   +-------------+
   |             |
   v             v
 Data        AI / ML
   |             |
   +------+------+
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

Les capacités transverses restent :

```text
Security
GitOps
Operations
Observability
Governance
Backup / PRA
Evidence
```

L'architecture cible sera détaillée dans les compétences BC01 suivantes.

---

# 21. Critère de réussite

La compétence C1 est démontrée si le jury peut reconstruire le raisonnement suivant :

```text
Existing SI
    |
    v
Current-State Cartography
    |
    v
Observed Components
    |
    v
Observed Interactions
    |
    v
Strengths / Weaknesses
    |
    v
Formal Risks
    |
    v
Architecture / Business Gaps
    |
    v
Prioritized Improvements
```

La suite du dossier BC01 doit donc être une conséquence de cet audit et non une accumulation arbitraire de technologies.

---

# 22. Statut des éléments de preuve

| Élément | Statut |
|---|---|
| Audit documentaire | EVIDENCED |
| Audit infrastructure | EVIDENCED |
| Audit Kubernetes | EVIDENCED |
| Audit réseau | EVIDENCED |
| Audit application | EVIDENCED |
| Audit Data | EVIDENCED |
| Audit AI / ML | EVIDENCED |
| Audit sécurité | EVIDENCED |
| Audit observabilité | EVIDENCED |
| Audit gouvernance | EVIDENCED |
| Identification des écarts | EVIDENCED |
| Registre formel des risques | IMPLEMENTED |
| Authentification / RBAC | RUNTIME-VERIFIED |
| Audit métier sur périmètre couvert | RUNTIME-VERIFIED |
| Matching déterministe | RUNTIME-VERIFIED |
| Backup PostgreSQL → MinIO | RUNTIME-VERIFIED |
| Restore PostgreSQL isolé | RUNTIME-VERIFIED |
| Validation d'intégrité après restore | RUNTIME-VERIFIED |
| CronJob backup GitOps | DEPLOYED / RUNTIME-VERIFIED |
| Cartographie SI actuelle — contenu | IMPLEMENTED |
| Cartographie SI actuelle — rendu jury | À FINALISER |
| Matrice risques / anomalies | EVIDENCED |
| Captures finales pour soutenance | À FINALISER |

---

# 23. Conclusion

L'audit montre que le projet dispose déjà d'un SI fonctionnel et intégré combinant :

```text
Infrastructure
      +
Kubernetes
      +
GitOps
      +
Business Application
      +
Data Platform
      +
MLOps
      +
Observability
      +
Security
      +
Governance
      +
Backup / PRA
```

Les enjeux identifiés ne consistent donc plus principalement à installer de nouvelles technologies.

Ils concernent désormais :

```text
Business completeness
Security maturity
Recoverability
Performance evidence
Data governance
AI industrialization
Traceability
Risk management
Automation
Certification evidence
```

Le système actuel constitue ainsi le point de départ mesuré des décisions d'architecture suivantes.

Les évolutions futures devront être justifiées par :

1. un besoin métier ;
2. un écart observé ;
3. un risque identifié ;
4. une exigence du référentiel ;
5. ou une amélioration mesurable de la plateforme.

---

## État BC01-C1

```text
Audit SI                  : EVIDENCED
Cartographie actuelle     : IMPLEMENTED
Analyse des écarts        : EVIDENCED
Registre des risques      : IMPLEMENTED
PRA / Restore             : RUNTIME-VERIFIED
Documentation             : EVIDENCED
Rendu graphique jury      : À FINALISER
```

**BC01 / C1 — Audit de l'existant : EVIDENCED**

La cartographie graphique sera retravaillée pour la soutenance sans bloquer la poursuite de BC01.