# BC01 — C3 — Architecture cible

**Bloc de compétences :** BC01  
**Compétence :** C3 — Concevoir et justifier une architecture cible  
**Projet :** Real Estate Intelligence Platform  
**Plateforme :** Enterprise AI Platform  
**Statut :** Documentation et architecture disponibles

---

# 1. Objectif

Ce dossier constitue le point d'entrée des preuves relatives à la conception de l'architecture cible.

Il démontre la transformation :

```text
Audit de l'existant
        |
        v
Identification des écarts
        |
        v
Besoins fonctionnels et non fonctionnels
        |
        v
Contraintes
        |
        v
Choix technologiques
        |
        v
Architecture cible
        |
        v
ADR
        |
        v
Implémentation
```

L'architecture cible ne constitue donc pas une collection de technologies.

Elle répond aux écarts identifiés pendant l'audit.

---

# 2. Sources de vérité

La description détaillée de l'architecture n'est pas dupliquée dans ce dossier.

Les documents de référence sont :

```text
../../../00-FOUNDATION/00-Executive-Summary.md
../../../00-FOUNDATION/01-Architecture-Principles.md
../../../00-FOUNDATION/02-Project-Vision.md
../../../00-FOUNDATION/03-Business-Objectives.md
../../../00-FOUNDATION/04-Architecture-Decisions.md
../../../00-FOUNDATION/05-Technology-Stack.md
../../../00-FOUNDATION/Enterprise-AI-Platform.md
../../../00-FOUNDATION/Architecture-Playbook.md
```

Les décisions détaillées sont conservées dans :

```text
../../../98-ADR/
```

Les diagrammes sont conservés dans :

```text
../../../99-DIAGRAMS/
```

---

# 3. Architecture cible globale

L'architecture cible est organisée en couches.

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

Les capacités transverses sont :

```text
Security
DevOps / GitOps
Operations
Observability
Governance
Backup / Disaster Recovery
```

---

# 4. Principes structurants

L'architecture cible repose sur les principes suivants :

1. Infrastructure as Code
2. GitOps
3. Documentation as Code
4. Diagrams as Code
5. Governance as Code
6. Security by Design
7. Observability by Design
8. Data Governance
9. AI Governance
10. Local-first AI
11. Reproductibilité
12. Automatisation
13. Traçabilité
14. Recoverability
15. Minimum Necessary Complexity

---

# 5. Vue Enterprise

Diagramme source :

```text
../../../99-DIAGRAMS/01-Enterprise-Context.puml
```

Diagramme rendu :

```text
../../../99-DIAGRAMS/rendered-diagrams/01-Enterprise-Context.svg
```

Cette vue positionne la plateforme dans son environnement métier et technique.

Elle permet d'identifier :

- utilisateurs ;
- systèmes ;
- plateforme ;
- dépendances ;
- frontières principales.

---

# 6. Vue plateforme

Diagramme source :

```text
../../../99-DIAGRAMS/02-Enterprise-Platform-Architecture.puml
```

Diagramme rendu :

```text
../../../99-DIAGRAMS/rendered-diagrams/02-Enterprise-Platform-Architecture.svg
```

Cette vue représente les principales capacités de la plateforme.

```text
Users / Business
       |
       v
Application Layer
       |
       +----------------+
       |                |
       v                v
   Data Platform     AI Platform
       |                |
       +-------+--------+
               |
               v
        Kubernetes Platform
               |
               v
         Infrastructure
```

---

# 7. Infrastructure cible

Références :

```text
../../../30-INFRASTRUCTURE/01-Infrastructure-Architecture.md
../../../30-INFRASTRUCTURE/02-Physical-Architecture.md
../../../30-INFRASTRUCTURE/03-Virtual-Infrastructure.md
../../../30-INFRASTRUCTURE/07-Compute-Architecture.md
../../../30-INFRASTRUCTURE/08-High-Availability.md
../../../30-INFRASTRUCTURE/09-Capacity-Planning.md
```

Diagramme :

```text
../../../99-DIAGRAMS/03-Infrastructure-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/03-Infrastructure-Architecture.svg
```

Le modèle général est :

```text
Physical Infrastructure
         |
         v
      Proxmox
         |
         v
 Virtual Machines
         |
         v
     Kubernetes
         |
         v
Platform Workloads
```

---

# 8. Kubernetes

Référence :

```text
../../../30-INFRASTRUCTURE/04-Kubernetes-Architecture.md
```

Diagramme :

```text
../../../99-DIAGRAMS/04-Kubernetes-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/04-Kubernetes-Architecture.svg
```

Architecture actuelle :

```text
Control Plane
├── k8s-cp-01
├── k8s-cp-02
└── k8s-cp-03

Workers
├── k8s-wk-01
├── k8s-wk-02
├── k8s-wk-03
├── k8s-wk-04
├── k8s-wk-05
└── k8s-wk-06
```

Principales capacités :

- scheduling ;
- service discovery ;
- self-healing ;
- configuration déclarative ;
- secrets ;
- ingress ;
- scaling ;
- workload isolation.

---

# 9. Architecture réseau

Référence :

```text
../../../30-INFRASTRUCTURE/05-Network-Architecture.md
```

Diagramme :

```text
../../../99-DIAGRAMS/05-Network-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/05-Network-Architecture.svg
```

Modèle :

```text
Physical / LAN Network
          |
          v
    Kubernetes Nodes
          |
          v
       Flannel
          |
          v
      Pod Network
          |
          v
 Kubernetes Services
          |
          v
    NGINX Ingress
```

Le routage sous-jacent constitue une dépendance explicite du fonctionnement Kubernetes.

---

# 10. Architecture applicative

Référence :

```text
../../../20-APPLICATION/01-Application-Architecture.md
```

Diagramme :

```text
../../../99-DIAGRAMS/06-Application-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/06-Application-Architecture.svg
```

Principes :

- API-first ;
- séparation des responsabilités ;
- services conteneurisés ;
- configuration externalisée ;
- observabilité ;
- sécurité ;
- déploiement GitOps.

FastAPI constitue le framework API Python privilégié.

React constitue une technologie cible pour les interfaces nécessitant une application web dédiée.

---

# 11. Architecture Data

Références :

```text
../../../40-DATA/01-Data-Architecture.md
../../../40-DATA/02-Data-Model.md
../../../40-DATA/03-Data-Warehouse.md
../../../40-DATA/04-Data-Governance.md
../../../40-DATA/05-Data-Quality.md
../../../40-DATA/06-Data-Lineage.md
../../../40-DATA/07-Metadata-Management.md
```

Diagramme :

```text
../../../99-DIAGRAMS/07-Data-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/07-Data-Architecture.svg
```

Le flux logique cible est :

```text
Sources
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

Répartition des responsabilités :

```text
PostgreSQL   = persistence
Airflow      = orchestration
dbt          = transformation
OpenMetadata = metadata / governance
```

---

# 12. Architecture AI

Références :

```text
../../../50-AI/01-AI-Platform-Architecture.md
../../../50-AI/02-LLM-Architecture.md
../../../50-AI/04-RAG-Architecture.md
../../../50-AI/07-AI-Governance.md
../../../50-AI/08-AI-Security.md
```

Diagramme :

```text
../../../99-DIAGRAMS/08-AI-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/08-AI-Architecture.svg
```

Principe :

```text
Enterprise Data
       |
       v
Internal AI Layer
       |
       v
Ollama
       |
       v
Qwen
       |
       v
Local GPU
```

La plateforme adopte une approche :

```text
LOCAL AI
   =
DEFAULT

EXTERNAL AI
   =
GOVERNED EXCEPTION
```

---

# 13. Architecture MLOps

Référence :

```text
../../../50-AI/03-MLOps-Architecture.md
```

Diagramme :

```text
../../../99-DIAGRAMS/09-MLOps-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/09-MLOps-Architecture.svg
```

Séparation des responsabilités :

```text
Airflow
   |
   v
Workflow Orchestration
   |
   v
Training / Evaluation
   |
   v
MLflow
   |
   +-- Experiments
   +-- Metrics
   +-- Parameters
   +-- Artifacts
   +-- Model Registry
```

MinIO fournit le stockage objet des artifacts lorsque nécessaire.

---

# 14. Architecture DevOps / GitOps

Références :

```text
../../../70-DEVOPS/01-DevOps-Architecture.md
../../../70-DEVOPS/02-GitOps-Architecture.md
../../../70-DEVOPS/03-CI-CD-Architecture.md
```

Diagramme :

```text
../../../99-DIAGRAMS/10-DevOps-GitOps-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/10-DevOps-GitOps-Architecture.svg
```

Modèle cible :

```text
Developer
    |
    v
GitLab
    |
    v
CI
    |
    v
Validated Artifact / Configuration
    |
    v
Git
    |
    v
Argo CD
    |
    v
Kubernetes
```

Git représente la source de vérité du desired state.

---

# 15. Architecture Observability

Références :

```text
../../../90-OBSERVABILITY/
```

Diagramme :

```text
../../../99-DIAGRAMS/11-Observability-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/11-Observability-Architecture.svg
```

Architecture :

```text
Metrics ----> Prometheus ---+
                            |
Logs ------> Loki ----------+----> Grafana
                            |
Traces ----> Tempo ---------+
             ^
             |
       OpenTelemetry
```

Alertmanager assure le routage des alertes Prometheus.

---

# 16. Architecture sécurité

Références :

```text
../../../60-SECURITY/
```

Diagramme :

```text
../../../99-DIAGRAMS/12-Security-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/12-Security-Architecture.svg
```

Les principes comprennent :

```text
Identity
Least Privilege
RBAC
Secrets
TLS
Network Security
Container Security
Kubernetes Security
Audit
Monitoring
```

L'architecture distingue explicitement :

```text
CURRENT
Kubernetes Secrets
GitLab protected variables

TARGET
Keycloak
HashiCorp Vault
```

---

# 17. Architecture Governance as Code

Références :

```text
../../../95-GOVERNANCE/
```

Diagramme :

```text
../../../99-DIAGRAMS/13-Governance-as-Code.puml
../../../99-DIAGRAMS/rendered-diagrams/13-Governance-as-Code.svg
```

Modèle :

```text
Requirement
    |
    v
Control
    |
    v
Policy
    |
    v
Git
    |
    v
CI Validation
    |
    v
Runtime Enforcement
    |
    v
Evidence
```

L'objectif est de réduire les contrôles exclusivement documentaires ou manuels.

---

# 18. Backup et Disaster Recovery

Références :

```text
../../../30-INFRASTRUCTURE/10-Disaster-Recovery.md
../../../80-OPERATIONS/07-Backup-and-Restore.md
../../../80-OPERATIONS/08-Business-Continuity.md
../../../80-OPERATIONS/09-Disaster-Recovery.md
```

Diagramme :

```text
../../../99-DIAGRAMS/14-Backup-DR-Architecture.puml
../../../99-DIAGRAMS/rendered-diagrams/14-Backup-DR-Architecture.svg
```

Principe :

```text
Backup
   |
   v
Restore
   |
   v
Validate
   |
   v
Evidence
```

Un backup non testé ne constitue pas une garantie de reprise.

---

# 19. Architecture actuelle et architecture cible

Une distinction explicite est maintenue.

## ADOPTED

```text
Proxmox
Kubernetes
kubeadm
Flannel
NGINX Ingress
cert-manager
GitLab
GitLab CI
Argo CD
PostgreSQL
Airflow
dbt
OpenMetadata
MLflow
MinIO
Ollama
Qwen
Prometheus
Grafana
Loki
Tempo
OpenTelemetry
Velero
PlantUML
```

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

## FUTURE / REQUIREMENT-DRIVEN

```text
Kafka
KEDA
Service Mesh
Argo Events
Argo Workflows
Feature Store
AI Gateway
Multi-cluster Kubernetes
```

Cela empêche de présenter une roadmap comme un état réellement déployé.

---

# 20. Décisions d'architecture

Les choix importants sont tracés dans :

```text
../../../98-ADR/
```

Baseline actuelle :

```text
ADR-0001 Kubernetes
ADR-0002 Argo CD / GitOps
ADR-0003 Flannel CNI
ADR-0004 NGINX Ingress
ADR-0005 PostgreSQL
ADR-0006 Airflow
ADR-0007 MLflow
ADR-0008 OpenMetadata
ADR-0009 Ollama Local AI
ADR-0010 Prometheus / Grafana
ADR-0011 Loki / Tempo / OpenTelemetry
ADR-0012 GitLab CI/CD
ADR-0013 Data Architecture
ADR-0014 Governance as Code
```

---

# 21. Traçabilité besoin → architecture

| Besoin / contrainte | Réponse architecturale |
|---|---|
| Reproductibilité | Git + GitOps |
| Orchestration | Kubernetes |
| Automatisation | CI/CD + GitOps |
| Persistence relationnelle | PostgreSQL |
| Data workflows | Airflow |
| Transformation | dbt |
| Metadata | OpenMetadata |
| Data Quality | dbt + OpenMetadata + pipelines |
| ML lifecycle | MLflow |
| Artifacts | MinIO |
| IA locale | Ollama + Qwen |
| Souveraineté IA | Local-first AI |
| Metrics | Prometheus |
| Dashboards | Grafana |
| Logs | Loki |
| Traces | Tempo |
| Telemetry | OpenTelemetry |
| Recovery Kubernetes | Velero |
| Architecture traceability | ADR |
| Architecture diagrams | PlantUML |
| Governance automation | Governance as Code |

---

# 22. Contraintes prises en compte

L'architecture cible tient compte de contraintes réelles.

## Matériel

```text
Infrastructure physique existante
GPU GTX 1080
8 GB VRAM par GPU
Capacité de stockage limitée
```

La cible ne suppose pas un datacenter ou un cloud illimité.

---

## Exploitation

La plateforme doit rester exploitable avec une équipe limitée.

Cela justifie :

```text
Avoid unnecessary complexity
```

et explique notamment pourquoi Kafka, Qdrant ou un Service Mesh ne deviennent pas automatiquement des dépendances.

---

## Souveraineté

Les données sensibles et les traitements IA doivent pouvoir rester sous contrôle local.

Cela motive :

```text
Ollama
+
Local Models
```

---

# 23. Qualités architecturales

La cible cherche à améliorer :

| Qualité | Mécanisme |
|---|---|
| Disponibilité | Kubernetes / HA |
| Scalabilité | Kubernetes |
| Maintenabilité | Git / Documentation as Code |
| Reproductibilité | GitOps / IaC |
| Observabilité | Prometheus/Loki/Tempo |
| Sécurité | Security architecture |
| Gouvernance | OpenMetadata / Governance as Code |
| Recoverability | Backup / Restore / Velero |
| Traçabilité | Git / ADR / CI |
| Portabilité | Containers / Kubernetes |
| Souveraineté | Local AI |

---

# 24. Diagrammes disponibles

Les 14 vues principales sont :

```text
01 Enterprise Context
02 Enterprise Platform Architecture
03 Infrastructure Architecture
04 Kubernetes Architecture
05 Network Architecture
06 Application Architecture
07 Data Architecture
08 AI Architecture
09 MLOps Architecture
10 DevOps / GitOps Architecture
11 Observability Architecture
12 Security Architecture
13 Governance as Code
14 Backup / Disaster Recovery
```

Chaque diagramme possède :

```text
PlantUML source
+
SVG rendered artifact
```

---

# 25. Preuves attendues pour le jury

L'architecture cible peut être démontrée avec :

```text
Architecture documentation
        +
PlantUML diagrams
        +
ADR
        +
Technology decisions
        +
Runtime evidence
```

Les preuves runtime seront centralisées progressivement dans les dossiers de compétences concernés.

---

# 26. Critère de réussite

La compétence est démontrée si le jury peut suivre :

```text
Business Need
     |
     v
Existing System
     |
     v
Gap Analysis
     |
     v
Architecture Requirements
     |
     v
Alternatives
     |
     v
Decisions
     |
     v
Target Architecture
     |
     v
Implementation
```

---

# 27. Statut

| Élément | Statut |
|---|---|
| Architecture globale | COMPLETE |
| Infrastructure | COMPLETE |
| Kubernetes | COMPLETE |
| Network | COMPLETE |
| Application | DOCUMENTED |
| Data | COMPLETE |
| AI | COMPLETE |
| MLOps | COMPLETE |
| DevOps / GitOps | COMPLETE |
| Observability | COMPLETE |
| Security | COMPLETE |
| Governance | COMPLETE |
| Backup / DR | COMPLETE |
| ADR | 14 AVAILABLE |
| PlantUML diagrams | 14 AVAILABLE |
| SVG diagrams | 14 AVAILABLE |
| Runtime evidence | TO BE CONSOLIDATED |

---

# 28. Conclusion

L'architecture cible résulte directement :

```text
Audit
 +
Business Requirements
 +
Technical Constraints
 +
Technology Watch
 +
Risk Analysis
 +
Architecture Principles
        |
        v
Enterprise AI Platform
```

La plateforme cible ne cherche pas à accumuler les technologies.

Elle cherche à construire une architecture :

```text
Governed
Observable
Secure
Recoverable
Automated
Traceable
Maintainable
```

---

**BC01 / C3 — Architecture cible : DOCUMENTATION BASELINE COMPLETE**