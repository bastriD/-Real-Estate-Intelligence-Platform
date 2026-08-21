# BC01 — C1 — Audit de l'existant

**Bloc de compétences :** BC01  
**Compétence :** C1 — Auditer l'existant et identifier les écarts  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** En cours de constitution des preuves

---

# 1. Objectif

Ce dossier regroupe les éléments de preuve démontrant la capacité à :

- analyser un système existant ;
- identifier ses composants ;
- comprendre son fonctionnement ;
- relever les limites techniques ;
- identifier les risques ;
- documenter les écarts ;
- proposer des axes d'amélioration ;
- préparer une architecture cible cohérente avec les besoins.

Le but n'est pas de dupliquer toute la documentation du projet.

Ce dossier sert de **point d'entrée pour le jury**.

Il répond à la question :

> Quelles preuves démontrent que l'existant a été audité avant de proposer la cible ?

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
    +-- Business services
    +-- APIs
    +-- Configuration
    +-- Dependencies

Data
    |
    +-- PostgreSQL
    +-- Data flows
    +-- ETL / ELT
    +-- Data Quality
    +-- Metadata

AI
    |
    +-- Local inference
    +-- ML lifecycle
    +-- RAG readiness
    +-- GPU constraints

Security
    |
    +-- IAM
    +-- Secrets
    +-- Network exposure
    +-- Kubernetes controls

Operations
    |
    +-- Backup
    +-- Restore
    +-- Availability
    +-- DR

Observability
    |
    +-- Metrics
    +-- Logs
    +-- Traces
    +-- Alerts

Governance
    |
    +-- Decisions
    +-- Risks
    +-- Technical debt
    +-- Governance as Code
```

---

# 3. Sources documentaires utilisées

Les principaux documents existants utilisés comme preuves d'audit sont les suivants.

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

# 4. Synthèse de l'existant

L'existant étudié repose sur une infrastructure locale et auto-hébergée.

Les principales briques sont :

```text
Proxmox VE
    |
    v
Virtual Machines
    |
    v
Kubernetes
    |
    +-- Argo CD
    +-- Airflow
    +-- MLflow
    +-- OpenMetadata
    +-- Prometheus
    +-- Grafana
    +-- Loki
    +-- Tempo
    +-- OpenTelemetry
    +-- Data workloads
```

La plateforme dispose également d'une capacité IA locale :

```text
AI Hosts
   |
   +-- NVIDIA GTX 1080
   +-- Ollama
   +-- Qwen
```

La plateforme s'appuie principalement sur :

- Kubernetes ;
- PostgreSQL ;
- GitLab ;
- Argo CD ;
- Airflow ;
- dbt ;
- OpenMetadata ;
- MLflow ;
- Ollama ;
- Prometheus ;
- Grafana ;
- Loki ;
- Tempo ;
- OpenTelemetry.

---

# 5. Constats principaux

## 5.1 Infrastructure

### Points forts

- Kubernetes déjà opérationnel.
- Plusieurs nœuds de contrôle.
- Plusieurs workers.
- GitOps avec Argo CD.
- Infrastructure virtualisée.
- Capacité de calcul IA locale.
- Architecture extensible.

### Limites observées

- Les ressources physiques restent limitées.
- Certaines capacités sont concentrées sur un même hôte physique.
- La haute disponibilité logique ne garantit pas automatiquement une haute disponibilité physique.
- Les GPU disponibles sont limités à 8 Go de VRAM chacun.
- Le stockage reste une contrainte structurante.
- La capacité doit être surveillée activement.

---

# 6. Kubernetes

### Points forts

- Cluster kubeadm HA.
- Plusieurs control planes.
- Plusieurs workers.
- GitOps.
- Ingress.
- cert-manager.
- Observabilité.
- Workloads Data / AI.

### Limites observées

- Flannel reste un CNI simple.
- La politique réseau avancée n'est pas encore le point fort de l'architecture.
- Une rupture de routage sous-jacente peut casser la communication des workers.
- Les ressources Kubernetes restent dépendantes du matériel disponible.

### Exemple d'incident observé

Des workers supplémentaires ont déjà rencontré un problème de connectivité lié au routage réseau.

L'incident a montré que :

```text
Kubernetes Overlay
       |
       v
depends on
       |
       v
Correct Underlay Routing
```

La correction du routage a rétabli les communications kubelet / metrics.

Cet incident constitue une preuve concrète de compréhension de l'infrastructure réseau Kubernetes.

---

# 7. Réseau

### Points forts

- Réseau interne fonctionnel.
- DNS interne.
- Ingress centralisé.
- Communication avec les hôtes IA locaux.

### Risques / limites

- Les communications inter-sous-réseaux doivent être correctement routées.
- Le réseau sous-jacent reste un point critique de disponibilité.
- La sécurité réseau doit évoluer avec les besoins.

Principe retenu :

```text
Underlay Network
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
Services
```

---

# 8. Data

### Points forts

L'architecture Data dispose déjà d'un découpage structuré :

```text
raw
  |
  v
staging
  |
  v
warehouse
  |
  v
analytics
```

Les responsabilités sont séparées :

```text
Airflow      = orchestration
dbt          = transformation
PostgreSQL   = persistence
OpenMetadata = governance
```

### Points forts supplémentaires

- Data Quality.
- Metadata.
- Profiling.
- Lineage.
- OpenMetadata.
- PostgreSQL.
- dbt.
- Airflow.

### Limites / axes d'amélioration

- Besoin de consolider les preuves de performance SQL.
- Besoin de preuves d'optimisation par index.
- Besoin de démonstration formelle OLTP / OLAP.
- Besoin de consolider la traçabilité entre modèle de données, SQL et résultats.

---

# 9. AI / ML

### Points forts

- Inférence locale.
- Ollama.
- Qwen.
- GPU local.
- MLflow.
- Airflow.
- MLOps documenté.
- Gouvernance IA documentée.

### Contraintes

La capacité GPU est limitée.

```text
GTX 1080
8 GB VRAM
```

Conséquences :

- modèle limité en taille ;
- nécessité de quantification ;
- concurrence limitée ;
- besoin de monitoring ;
- nécessité de contrôler les ressources.

### Décision importante

Le modèle retenu est :

```text
Local AI
  =
Default

External AI
  =
Governed Exception
```

---

# 10. Sécurité

### État actuel

Les mécanismes actuellement adoptés incluent notamment :

- Kubernetes RBAC ;
- Kubernetes Secrets ;
- GitLab protected variables ;
- TLS ;
- cert-manager ;
- contrôle d'accès réseau ;
- sécurité Kubernetes ;
- contrôle des images et CI selon maturité.

### État cible

Certaines technologies restent des cibles :

```text
Keycloak
HashiCorp Vault
```

Elles ne doivent pas être présentées comme déjà déployées.

### Constats

La sécurité est déjà intégrée à l'architecture mais plusieurs contrôles doivent évoluer progressivement vers :

```text
Policy as Code
       |
       v
CI Validation
       |
       v
Runtime Enforcement
```

---

# 11. Observabilité

### Points forts

La plateforme possède les trois piliers principaux :

```text
Metrics -> Prometheus
Logs    -> Loki
Traces  -> Tempo
```

Avec :

```text
OpenTelemetry
Grafana
Alertmanager
```

### Limites

La présence d'outils d'observabilité ne prouve pas automatiquement :

- une couverture complète ;
- des SLO définis ;
- des alertes pertinentes ;
- une corrélation systématique ;
- une gouvernance complète des métriques.

Ces points sont traités dans le domaine Observability.

---

# 12. Backup / Disaster Recovery

### Points forts

- Velero présent dans l'architecture.
- Stratégie backup / restore documentée.
- RPO / RTO documentés comme objectifs.
- Processus de validation défini.

### Point critique

```text
Backup Success
     !=
Recoverability
```

La preuve la plus forte reste :

```text
Backup
  |
  v
Restore
  |
  v
Validation
```

La restauration doit donc être démontrée par des tests.

---

# 13. Gouvernance

### État initial

L'architecture comportait de nombreux éléments documentés mais plusieurs contrôles restaient principalement humains ou documentaires.

### Cible

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
Enforcement
       |
       v
Evidence
```

Le passage vers Governance as Code constitue une amélioration majeure de maturité.

---

# 14. Principaux écarts identifiés

| Domaine | Existant | Écart / Limite | Cible |
|---|---|---|---|
| Infrastructure | Kubernetes opérationnel | Contraintes matérielles | Optimisation et gouvernance |
| HA | HA logique Kubernetes | Failure domains physiques | Réduction du risque |
| Réseau | Flannel + LAN | Dépendance au routage | Routage documenté et surveillé |
| Data | PostgreSQL + dbt + Airflow | Preuves d'optimisation à consolider | SQL mesuré et optimisé |
| Metadata | OpenMetadata | Automatisation partielle | Governance as Code |
| AI | Ollama + Qwen | GPU limité | Modèles adaptés / quantification |
| IAM | Contrôles distribués | Pas d'IAM central cible | Keycloak cible |
| Secrets | K8s Secrets / CI variables | Pas de gestion centralisée avancée | Vault cible |
| Observability | Stack complète | SLO et preuves à renforcer | Observability Governance |
| Backup | Backup architecture | Restore proof required | Tests de restauration |
| Governance | Documentation riche | Automatisation partielle | Governance as Code |

---

# 15. Risques issus de l'audit

Les principaux risques identifiés sont notamment :

- saturation du stockage ;
- saturation GPU ;
- perte d'un hôte physique ;
- problème de routage ;
- perte de base de données ;
- perte d'artifacts ML ;
- mauvaise gestion des secrets ;
- erreurs de configuration Kubernetes ;
- drift de configuration ;
- données de mauvaise qualité ;
- modèles IA mal gouvernés ;
- absence de preuve de restauration ;
- dépendance excessive à des changements manuels.

Ces risques sont détaillés dans :

```text
../../../95-GOVERNANCE/04-Risk-Management.md
```

---

# 16. Axes d'amélioration identifiés

L'audit conduit aux améliorations principales suivantes :

```text
GitOps
Governance as Code
Policy as Code
Data Governance
Data Quality
AI Governance
SLOs
Backup Validation
Architecture as Code
Documentation as Code
Diagrams as Code
Security Automation
CI Validation
```

---

# 17. Architecture cible issue de l'audit

L'audit conduit vers une architecture cible reposant sur :

```text
Business
   |
   v
Application
   |
   +--------+
   |        |
   v        v
 Data      AI
   |        |
   +---+----+
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

Avec des capacités transverses :

```text
Security
DevOps / GitOps
Operations
Observability
Governance as Code
Backup / Disaster Recovery
```

---

# 18. Preuves disponibles

## Documentation

```text
00-FOUNDATION/
30-INFRASTRUCTURE/
40-DATA/
50-AI/
60-SECURITY/
80-OPERATIONS/
90-OBSERVABILITY/
95-GOVERNANCE/
98-ADR/
99-DIAGRAMS/
```

## Diagrammes

Les diagrammes d'architecture permettent de visualiser :

- contexte ;
- infrastructure ;
- Kubernetes ;
- réseau ;
- Data ;
- AI ;
- MLOps ;
- DevOps ;
- observabilité ;
- sécurité ;
- gouvernance ;
- disaster recovery.

Répertoire :

```text
../../../99-DIAGRAMS/
```

---

# 19. Preuves techniques déjà identifiées

Des preuves techniques pourront être jointes dans ce dossier ou référencées depuis celui-ci.

Exemples :

```text
kubectl get nodes
kubectl get pods -A
kubectl top nodes
kubectl top pods -A

argocd app list

docker ps

airflow DAG status

MLflow model versions

OpenMetadata ingestion status

Prometheus targets

Grafana dashboards

PostgreSQL queries

EXPLAIN ANALYZE

Data Quality results

Backup status

Restore-test results
```

---

# 20. Éléments de preuve à ajouter

Ce dossier doit progressivement recevoir les preuves techniques les plus pertinentes.

Exemples futurs :

```text
01-infrastructure-before.txt
02-kubernetes-nodes.txt
03-kubernetes-workloads.txt
04-network-routing.txt
05-storage-capacity.txt
06-data-platform.txt
07-openmetadata.txt
08-mlflow.txt
09-observability.txt
10-backup-status.txt
11-restore-test.txt
```

Les fichiers ne doivent pas être créés artificiellement.

Ils doivent contenir des résultats réellement exécutés sur la plateforme.

---

# 21. Critère de réussite

La compétence est démontrée si le jury peut reconstruire le raisonnement suivant :

```text
Existing System
      |
      v
Observed State
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
      |
      v
Target Architecture
```

L'architecture cible ne doit donc pas apparaître comme une solution choisie arbitrairement.

Elle doit être la conséquence de l'audit.

---

# 22. Statut actuel

| Élément | Statut |
|---|---|
| Audit documentaire | COMPLET |
| Audit infrastructure | DOCUMENTÉ |
| Audit Kubernetes | DOCUMENTÉ |
| Audit Data | DOCUMENTÉ |
| Audit AI | DOCUMENTÉ |
| Audit sécurité | DOCUMENTÉ |
| Audit observabilité | DOCUMENTÉ |
| Audit gouvernance | DOCUMENTÉ |
| Identification des écarts | COMPLET |
| Architecture cible | DOCUMENTÉE |
| Preuves runtime centralisées | À COMPLÉTER |
| Captures / commandes jury | À COMPLÉTER |
| Restore test evidence | À COMPLÉTER |

---

# 23. Conclusion

L'audit montre que la plateforme possède déjà une base technique avancée :

```text
Kubernetes
GitOps
Data Platform
AI / MLOps
Observability
Governance
```

Les principaux enjeux ne sont plus uniquement l'installation de technologies.

Ils concernent désormais :

```text
Industrialisation
Governance
Security
Evidence
Recoverability
Traceability
Automation
```

La cible proposée vise donc à transformer une infrastructure technique fonctionnelle en une **plateforme d'entreprise gouvernée, observable, sécurisée et reproductible**.

---

**BC01 / C1 — Audit de l'existant : DOCUMENTATION BASELINE COMPLETE**