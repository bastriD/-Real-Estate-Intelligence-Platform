# High Availability Architecture

**Version:** 1.0  
**Status:** Draft  
**Owner:** Bastri Murad  
**Project:** Enterprise AI Platform  
**Business Application:** Real Estate Intelligence Platform  
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document defines the High Availability (HA) strategy of the Enterprise AI Platform.

It explains how the platform minimizes downtime through redundancy, orchestration, monitoring and recovery mechanisms while acknowledging the physical limitations of the current infrastructure.

The objective is to maximize service availability using the existing hardware.

---

# 2. Scope

This document covers:

- Kubernetes High Availability
- Platform services
- Stateful workloads
- Self-healing
- Failure recovery
- Rolling updates
- Monitoring
- Physical limitations

---

# 3. High Availability Objectives

The platform is designed to:

- Reduce service interruptions
- Recover automatically from common failures
- Maintain cluster control
- Protect critical workloads
- Enable maintenance with minimal downtime
- Detect failures rapidly

---

# 4. Availability Principles

The platform follows these principles:

- Automate recovery whenever possible.
- Eliminate single points of failure where feasible.
- Prefer self-healing over manual intervention.
- Separate control and workload responsibilities.
- Monitor continuously.
- Test recovery procedures regularly.

---

# 5. Availability Layers

```
Business Applications
        │
Platform Services
        │
Kubernetes
        │
Virtual Infrastructure
        │
Physical Infrastructure
```

Availability depends on every layer.

---

# 6. Kubernetes Control Plane

The cluster contains three control-plane nodes.

Responsibilities:

- Kubernetes API
- etcd
- Scheduler
- Controller Manager

Benefits:

- Control-plane redundancy
- Quorum protection
- Maintenance without full control-plane outage

The control plane represents the highest availability component of the platform.

---

# 7. Worker Node Availability

Worker nodes execute application workloads.

If a worker node becomes unavailable:

- Pods are recreated on another worker (where resources permit).
- Services remain reachable through Kubernetes networking.
- GitOps restores the desired state if necessary.

Recovery depends on available cluster capacity.

---

# 8. Pod High Availability

Production workloads should use:

- ReplicaSets
- Deployments
- Multiple replicas for stateless services
- Readiness probes
- Liveness probes
- Startup probes where appropriate

Examples:

- FastAPI
- React
- Grafana
- Argo CD components

Stateful services require additional protection.

---

# 9. Stateful Workloads

Critical stateful services include:

- PostgreSQL
- MinIO
- MLflow
- OpenMetadata

These services rely primarily on:

- Persistent Volumes
- Backups
- Restore procedures

Availability for stateful services is limited by the current storage architecture.

---

# 10. Self-Healing

Kubernetes automatically handles:

- Pod failures
- Container crashes
- Health probe failures
- Deployment reconciliation

GitOps extends self-healing by restoring the declared platform state.

---

# 11. Rolling Updates

Application updates follow rolling deployment principles.

Benefits:

- Minimal downtime
- Progressive replacement
- Automatic rollback if required
- Continuous service availability

---

# 12. GitOps Availability

Argo CD continuously compares:

Desired State

↓

Git Repository

↓

Live Cluster

Configuration drift is automatically corrected whenever possible.

Git becomes the authoritative source of truth.

---

# 13. Platform Service Availability

Critical platform services include:

| Service | Availability Strategy |
|----------|----------------------|
| Argo CD | Kubernetes + GitOps |
| Airflow | Kubernetes restart |
| MLflow | Persistent storage + restart |
| PostgreSQL | Backup and recovery |
| OpenMetadata | Persistent storage |
| Prometheus | Persistent storage |
| Grafana | Persistent storage |
| Loki | Persistent storage |
| Tempo | Persistent storage |

---

# 14. Monitoring

Availability is monitored through:

- Prometheus
- Grafana
- Alertmanager
- Kubernetes Events
- Node Exporter

Typical alerts include:

- Node Not Ready
- Pod CrashLoopBackOff
- High CPU
- High Memory
- Disk Pressure
- Certificate expiration
- Persistent Volume usage

---

# 15. Planned Maintenance

Maintenance should follow this sequence:

1. Backup
2. Validate platform health
3. Drain worker node (if applicable)
4. Perform maintenance
5. Validate workloads
6. Restore scheduling
7. Verify monitoring

Maintenance should avoid impacting critical business services.

---

# 16. Failure Scenarios

| Failure | Expected Recovery |
|----------|------------------|
| Pod crash | Kubernetes restart |
| Container failure | Automatic restart |
| Worker node failure | Pod rescheduling (capacity permitting) |
| Control-plane node failure | Remaining quorum continues |
| Application deployment failure | GitOps reconciliation or rollback |
| Certificate issue | cert-manager renewal |
| Database corruption | Restore from backup |
| Proxmox host failure | Full platform restoration procedure |

---

# 17. Physical Limitations

The platform intentionally accepts the following constraints:

- Single Proxmox host
- Single residential network
- Single primary storage platform
- Fixed compute capacity
- Fixed GPU capacity

These represent physical single points of failure that cannot currently be eliminated.

Accordingly, the platform distinguishes between:

- **Logical High Availability** (implemented)
- **Physical High Availability** (partially implemented)

---

# 18. Current Availability Model

| Layer | Status |
|--------|--------|
| Kubernetes Control Plane | High Availability |
| Worker Nodes | Partial High Availability |
| Stateless Applications | High Availability |
| Stateful Applications | Backup-based resilience |
| Virtualization | Single Host |
| Physical Infrastructure | Single Site |

---

# 19. Future Improvements

Potential improvements include:

- PostgreSQL replication
- Distributed object storage
- Additional Proxmox host
- UPS integration
- Network redundancy
- Multi-site backups

These improvements are optional and not required for the current project scope.

---

# 20. Architecture Decisions

Key decisions include:

- Three-node Kubernetes control plane
- Kubernetes self-healing
- GitOps reconciliation
- Rolling deployments
- Health probes
- Backup-first strategy for stateful services
- Acceptance of fixed physical constraints

---

# 21. Related Documents

- Infrastructure Architecture
- Kubernetes Architecture
- Compute Architecture
- Storage Architecture
- Capacity Planning
- Disaster Recovery Plan
- Observability Architecture