# Kubernetes Architecture

**Version:** 1.0  
**Status:** Draft  
**Owner:** Bastri Murad  
**Project:** Enterprise AI Platform  
**Business Application:** Real Estate Intelligence Platform  
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document defines the Kubernetes architecture of the Enterprise AI Platform.

It describes how Kubernetes provides orchestration, workload scheduling, networking, storage, security, observability and GitOps capabilities for all applications deployed on the platform.

This document represents the current production architecture of the platform.

---

# 2. Scope

This document covers:

- Kubernetes Cluster
- Control Plane
- Worker Nodes
- Networking
- Storage
- Scheduling
- Security
- GitOps
- Platform Services
- Data Platform
- AI Platform
- Monitoring
- Disaster Recovery

---

# 3. Kubernetes Overview

The Enterprise AI Platform is deployed on a self-managed Kubernetes cluster hosted on Proxmox VE.

The cluster provides a production-like environment implementing cloud-native best practices including:

- Declarative deployments
- GitOps
- Infrastructure as Code
- Self-healing workloads
- Rolling updates
- Namespace isolation
- RBAC
- Persistent storage
- Observability

---

# 4. Cluster Topology

Current architecture

```text
                    Kubernetes Cluster

                    3 Control Plane Nodes
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
       CP-01              CP-02              CP-03

                             │

──────────────────────────────────────────────────────────────

        Worker Nodes

        WK-01
        WK-02
        WK-03
        WK-04
        WK-05
        WK-06

──────────────────────────────────────────────────────────────

Hosted Platform Services

Argo CD

Airflow

MLflow

OpenMetadata

Monitoring

GitLab

PostgreSQL

MinIO

Ollama

Business Applications
```

---

# 5. Control Plane Architecture

The control plane consists of three dedicated virtual machines.

Responsibilities:

- Kubernetes API Server
- etcd
- Scheduler
- Controller Manager

Objectives:

- Cluster management
- High availability
- Cluster state
- Scheduling decisions

Application workloads are never intentionally deployed on the control plane.

---

# 6. Worker Node Architecture

Worker nodes execute platform workloads.

Current workload categories include:

- Platform Services
- Data Platform
- AI Platform
- Monitoring
- Logging
- Tracing
- Business Applications

Workers are responsible for:

- Pod execution
- Resource isolation
- Horizontal scaling
- Service availability

---

# 7. Container Runtime

The Kubernetes cluster uses a standard OCI-compatible container runtime.

Containers are built through GitLab CI and deployed using Argo CD.

Images are versioned and stored in the GitLab Container Registry.

---

# 8. Namespace Strategy

Namespaces isolate workloads by responsibility.

Current namespaces include:

| Namespace | Purpose |
|------------|---------|
| argocd | GitOps |
| airflow | Workflow orchestration |
| mlflow | Machine learning lifecycle |
| monitoring | Monitoring and observability |
| retail-data | Data platform |
| openmetadata | Metadata management |
| tempo | Distributed tracing |
| promtail | Log collection |
| velero | Backup |
| zammad | Helpdesk |
| default | Temporary workloads only |

Future namespaces may include:

- keycloak
- vault
- kafka
- qdrant

---

# 9. Networking

Networking is provided by:

- Flannel CNI

Responsibilities:

- Pod networking
- Service communication
- Internal routing

Objectives:

- Flat cluster networking
- Reliable service communication
- Low operational complexity

---

# 10. Service Discovery

Internal communication uses Kubernetes DNS.

Services communicate using native service names.

Example:

```
postgresql.namespace.svc.cluster.local
```

Internal DNS is automatically managed by CoreDNS.

---

# 11. Ingress Architecture

Ingress traffic is managed through:

- NGINX Ingress Controller

Responsibilities:

- HTTPS termination
- Routing
- Host-based routing
- Load balancing

Typical exposed services include:

- GitLab
- Argo CD
- Airflow
- MLflow
- OpenMetadata
- Grafana

---

# 12. DNS

The platform uses the internal domain:

```
*.lab.local
```

Examples:

```
gitlab.lab.local

argocd.lab.local

airflow.lab.local

grafana.lab.local

mlflow.lab.local
```

DNS simplifies platform administration and service discovery.

---

# 13. Certificate Management

TLS certificates are managed through:

- cert-manager

Responsibilities:

- Certificate issuance
- Certificate renewal
- Secret generation

All externally exposed services should use HTTPS.

---

# 14. Storage Architecture

Persistent workloads use Kubernetes Persistent Volumes.

Primary consumers include:

- PostgreSQL
- MinIO
- MLflow
- Airflow
- OpenMetadata

Objectives:

- Data persistence
- Stateful workloads
- Recovery support

---

# 15. Scheduling Strategy

Kubernetes schedules workloads based on:

- Resource requests
- Resource limits
- Node availability

Future improvements may include:

- Node Affinity
- Taints
- Tolerations
- Topology constraints

GPU workloads will be explicitly scheduled.

---

# 16. Resource Governance

Every production workload should define:

CPU Request

CPU Limit

Memory Request

Memory Limit

Storage Requirements

Health Probes

Production namespaces should implement:

- ResourceQuota
- LimitRange

---

# 17. GitOps Architecture

Platform deployments follow GitOps.

Workflow:

```
Git Repository

↓

GitLab CI

↓

Container Registry

↓

Argo CD

↓

Kubernetes Cluster
```

Git becomes the single source of truth.

---

# 18. Platform Services

Current shared platform services include:

| Service | Purpose |
|----------|---------|
| Argo CD | GitOps |
| Airflow | Workflow orchestration |
| MLflow | ML lifecycle |
| OpenMetadata | Metadata |
| PostgreSQL | Relational database |
| MinIO | Object storage |
| GitLab | SCM / CI |
| Velero | Backup |

---

# 19. Data Platform

The Kubernetes cluster hosts:

- PostgreSQL
- Airflow
- OpenMetadata
- Analytics workloads

Responsibilities:

- Data ingestion
- ETL
- Metadata
- Warehousing
- Analytics

---

# 20. AI Platform

Current AI services include:

- Ollama
- MLflow

Future services:

- Qdrant
- AI Gateway
- RAG APIs

Responsibilities:

- Model serving
- Model registry
- Embeddings
- Semantic search

---

# 21. Observability

The platform provides complete observability through:

| Component | Purpose |
|-----------|---------|
| Prometheus | Metrics |
| Grafana | Dashboards |
| Loki | Logs |
| Tempo | Traces |
| Promtail | Log collection |
| OpenTelemetry | Telemetry |

Every workload should expose:

- Metrics
- Logs
- Health checks

---

# 22. Backup Strategy

Platform protection includes:

- Velero backups
- Persistent Volume backups
- Git repository backup
- Database backup
- Application recovery procedures

Backups are documented separately.

---

# 23. Upgrade Strategy

Cluster upgrades follow a controlled process:

1. Backup
2. Validation
3. Control Plane upgrade
4. Worker upgrade
5. Platform validation
6. GitOps verification
7. Production monitoring

---

# 24. Failure Scenarios

| Failure | Recovery |
|----------|----------|
| Pod failure | Kubernetes restart |
| Node failure | Reschedule workloads |
| Application failure | GitOps reconciliation |
| Database issue | Restore from backup |
| Certificate issue | cert-manager renewal |
| Ingress issue | Controller recovery |

---

# 25. Capacity Management

Capacity is continuously monitored.

Key indicators:

- CPU
- Memory
- Storage
- GPU utilization
- Pod density
- Node pressure
- Scheduling failures
- Persistent Volume growth

Scaling decisions are based on measured usage rather than assumptions.

---

# 26. Current State

Current platform characteristics:

- Kubernetes v1.30.x
- Three control-plane nodes
- Multiple worker nodes
- Flannel networking
- NGINX Ingress
- cert-manager
- Argo CD
- Airflow
- MLflow
- OpenMetadata
- PostgreSQL
- MinIO
- Grafana
- Prometheus
- Loki
- Tempo
- Velero
- GitLab
- Ollama

The platform is operational and managed through GitOps.

---

# 27. Target State

Planned platform evolution:

- Keycloak
- Vault
- Kafka
- Qdrant
- KEDA
- AI Gateway
- Enhanced GPU scheduling
- Improved workload isolation
- Expanded automation

These additions extend platform capabilities without changing the core Kubernetes architecture.

---

# 28. Architecture Decisions

Key decisions include:

- Kubernetes as the orchestration platform
- GitOps as the deployment model
- Namespace-based isolation
- Declarative infrastructure
- Self-healing workloads
- Observability by default
- API-first services
- Persistent storage for stateful applications

---

# 29. Related Documents

- Infrastructure Architecture
- Physical Architecture
- Virtual Infrastructure
- Network Architecture
- Storage Architecture
- Security Architecture
- GitOps Strategy
- Observability Architecture
- Disaster Recovery Plan
- Capacity Planning