# Virtual Infrastructure Architecture

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document describes the virtualization layer supporting the Enterprise AI Platform.

The virtualization platform abstracts the physical infrastructure and provides isolated virtual machines used to host the Kubernetes cluster and supporting enterprise services.

It is the foundation upon which the cloud-native platform is deployed.

---

# 2. Objectives

The virtualization layer is designed to provide:

- Isolation
- Flexibility
- Resource management
- Snapshot capability
- Simplified maintenance
- Hardware abstraction
- Reproducible infrastructure

---

# 3. Platform Overview

Virtualization is provided by Proxmox VE.

Responsibilities include:

- Virtual machine lifecycle
- CPU allocation
- Memory allocation
- Virtual networking
- Storage attachment
- Snapshots
- Backup integration

The Kubernetes cluster is entirely hosted on virtual machines managed by Proxmox.

---

# 4. Logical Architecture

```text
Physical Server
       │
       ▼
Proxmox VE
       │
──────────────────────────────

Virtual Machines

Control Plane 01

Control Plane 02

Control Plane 03

Worker 01

Worker 02

Worker 03

Additional Workers (optional)

Infrastructure Services
```

---

# 5. Virtual Machine Roles

## Control Plane Nodes

Responsibilities:

- Kubernetes API
- Scheduler
- Controller Manager
- etcd

Characteristics:

- Stable
- Low workload variation
- High availability

---

## Worker Nodes

Responsibilities:

- Application workloads
- Platform services
- Data platform
- AI platform
- Monitoring

Characteristics:

- Horizontally scalable
- Workload isolation
- Resource scheduling

---

# 6. Resource Allocation Strategy

Virtual resources are allocated according to workload characteristics.

Examples:

| Workload | CPU | RAM | Priority |
|----------|----:|----:|----------|
| Control Plane | Stable | Stable | High |
| PostgreSQL | High | High | Critical |
| Airflow | Medium | Medium | High |
| MLflow | Medium | Medium | High |
| Monitoring | Medium | Medium | High |
| Ollama | High | High | GPU |
| GitLab | Medium | Medium | High |

Exact allocations may evolve as workloads change.

---

# 7. Virtual Networking

Virtual machines communicate through Proxmox virtual networking.

Responsibilities:

- VM connectivity
- Kubernetes traffic
- Management access
- Storage communication

Network segmentation is enforced at the Kubernetes layer where appropriate.

---

# 8. Storage Integration

Each VM uses virtual disks managed by Proxmox.

Persistent Kubernetes workloads rely on Persistent Volumes rather than VM disks whenever possible.

Snapshots are used for:

- Maintenance
- Testing
- Rollback
- Recovery

Snapshots are not a replacement for backups.

---

# 9. Backup Strategy

The virtualization layer supports:

- VM backups
- Snapshot creation
- Restore testing

Critical platform data is backed up using application-aware procedures in addition to VM-level protection.

---

# 10. Availability

Virtualization contributes to availability by:

- Isolating workloads
- Simplifying recovery
- Supporting snapshots
- Allowing controlled maintenance

High availability at the virtualization layer is limited by the current single Proxmox host architecture.

---

# 11. Failure Scenarios

| Scenario | Expected Behavior |
|----------|-------------------|
| VM crash | Restart VM |
| Kubernetes node failure | Reschedule workloads where possible |
| Storage issue | Restore from backup |
| Snapshot rollback | Controlled recovery |
| Proxmox host failure | Restore platform from documented procedures |

---

# 12. Maintenance Strategy

Routine maintenance includes:

- Proxmox updates
- VM template updates
- Snapshot cleanup
- Storage monitoring
- Backup verification
- Resource review

Maintenance windows should minimize disruption to production workloads.

---

# 13. Constraints

Current limitations include:

- Single Proxmox host
- Fixed hardware capacity
- Shared physical resources
- Residential environment

These constraints are accepted as part of the platform architecture.

---

# 14. Design Principles

The virtualization layer follows these principles:

- One responsibility per VM where practical
- Clear separation between control plane and workloads
- Infrastructure reproducibility
- Resource efficiency
- Minimal operational complexity

---

# 15. Related Documents

- Physical Architecture
- Infrastructure Architecture
- Kubernetes Architecture
- Capacity Planning
- Disaster Recovery Plan
- Backup Strategy