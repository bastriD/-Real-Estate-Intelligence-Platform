# Physical Architecture

**Version:** 1.1
**Status:** Approved Baseline
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document describes the fixed physical infrastructure supporting the Enterprise AI Platform.

It defines the available compute, GPU, storage, networking and physical resources used to host the Kubernetes platform and its associated services.

The current hardware constitutes the baseline infrastructure for the project. No significant physical infrastructure upgrade is planned in the short or medium term.

The architecture must therefore prioritize efficient use of existing resources.

---

# 2. Scope

This document covers:

* Physical compute resources
* GPU resources
* Local storage
* Network equipment
* Physical connectivity
* Hardware constraints
* Capacity limitations
* Resource optimization principles

Virtual machines, Kubernetes workloads and platform services are documented separately.

---

# 3. Architectural Context

The Enterprise AI Platform operates within a resource-constrained homelab environment.

The infrastructure is designed to reproduce enterprise architecture practices using the available hardware rather than attempting to reproduce enterprise-scale capacity.

The primary objective is to demonstrate:

* Architecture design
* Kubernetes administration
* GitOps
* Data engineering
* AI and MLOps
* Observability
* Security
* Governance
* Disaster recovery
* Resource optimization

The value of the platform is based on its architecture, automation and operational maturity rather than its physical size.

---

# 4. Physical Architecture Objectives

The physical infrastructure must support:

* A highly available Kubernetes control plane
* Multiple Kubernetes worker nodes
* Data engineering workloads
* AI inference workloads
* CI/CD and GitOps services
* Monitoring and observability
* Persistent data services
* Controlled experimentation
* Production-like operating practices

The infrastructure must remain stable without requiring major hardware expansion.

---

# 5. Physical Topology

```text
                         Internet
                            │
                      ISP Router
                            │
                     Local LAN Router
                            │
                       Network Switch
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
  Proxmox Platform       AI Node 1           AI Node 2
        │              GTX 1080 8 GB       GTX 1080 8 GB
        │
  Virtual Machines
        │
 Kubernetes Control Planes
 Kubernetes Workers
 Platform Services
```

The exact allocation of the two GPUs may evolve, but the physical GPU capacity remains fixed at two NVIDIA GTX 1080 cards.

---

# 6. Compute Infrastructure

## 6.1 Virtualization Platform

Proxmox VE provides the primary virtualization layer.

Responsibilities include:

* Virtual machine hosting
* CPU and memory allocation
* Virtual networking
* VM lifecycle management
* Snapshots
* Infrastructure isolation

The Proxmox environment hosts the virtual machines required by the Kubernetes platform and supporting services.

---

## 6.2 Kubernetes Control Plane

The Kubernetes cluster contains three control-plane nodes.

Responsibilities include:

* Kubernetes API Server
* Scheduler
* Controller Manager
* etcd
* Cluster state management

The three-node control plane provides a production-like high-availability architecture.

---

## 6.3 Kubernetes Workers

Multiple worker nodes execute the platform workloads.

Workloads include:

* Airflow
* MLflow
* OpenMetadata
* PostgreSQL
* Monitoring
* Logging
* Tracing
* Data pipelines
* Business applications
* Supporting platform services

Worker capacity is finite and must be governed using resource requests, limits, quotas and scheduling rules.

---

# 7. GPU Infrastructure

## 7.1 Hardware Baseline

The platform has two GPU accelerators:

| GPU             |    Memory | Primary Purpose                  |
| --------------- | --------: | -------------------------------- |
| NVIDIA GTX 1080 | 8 GB VRAM | AI inference and experimentation |
| NVIDIA GTX 1080 | 8 GB VRAM | AI inference and experimentation |

Total installed GPU memory:

```text
2 × 8 GB = 16 GB VRAM
```

However, the two GPUs must normally be treated as separate 8 GB execution devices.

Their memory is not automatically combined into a single shared 16 GB memory space.

---

## 7.2 GPU Responsibilities

The GPU infrastructure supports:

* Local LLM inference
* Ollama workloads
* Embedding generation
* Computer vision experimentation
* Model evaluation
* Lightweight model training
* AI demonstrations
* MLOps validation

---

## 7.3 GPU Constraints

The NVIDIA GTX 1080 has limited memory compared with modern AI accelerators.

The following constraints apply:

* Large models may not fit into 8 GB VRAM.
* Concurrent inference workloads must be limited.
* Model quantization may be required.
* Large training workloads are outside the target scope.
* Multi-GPU memory aggregation must not be assumed.
* GPU workloads must be scheduled intentionally.
* CPU and RAM offloading may reduce performance.

---

## 7.4 GPU Optimization Strategy

Because additional GPUs are not planned, the platform must optimize existing capacity through:

* Quantized models
* Smaller language models
* Controlled context windows
* Batch-size limitation
* Model unloading
* Request queues
* Resource-aware scheduling
* Separate workloads per GPU
* CPU offloading where acceptable
* Performance benchmarking
* Usage monitoring

One GPU may be dedicated to stable inference while the second is used for experimentation, evaluation or secondary workloads.

---

# 8. Storage Architecture

The current storage infrastructure supports:

* Virtual machine disks
* Kubernetes persistent volumes
* PostgreSQL data
* MinIO objects
* MLflow artifacts
* Airflow metadata
* OpenMetadata data
* Monitoring data
* Backup files

The storage architecture must use existing capacity efficiently.

No major storage platform expansion is currently planned.

---

# 9. Storage Constraints

The following constraints must be considered:

* Finite disk capacity
* Shared storage contention
* Stateful workload growth
* Log accumulation
* Metrics retention
* Container image accumulation
* Database growth
* Backup storage consumption

Storage usage must be actively monitored.

---

# 10. Storage Optimization

The platform should implement:

* Log retention policies
* Metrics retention policies
* Image cleanup
* Database maintenance
* Backup rotation
* Artifact lifecycle management
* Persistent volume monitoring
* Storage alerts
* Capacity thresholds

Data retention must be based on actual business, educational and operational value.

---

# 11. Network Infrastructure

The infrastructure uses the existing local network.

Core components include:

* ISP router
* Local router
* Network switch
* Ethernet connections
* Wi-Fi-connected worker nodes where required
* Internal DNS using the `lab.local` domain

The network supports:

* Kubernetes node communication
* Service exposure
* Internal DNS
* GitOps access
* Administrative access
* AI inference access
* Monitoring traffic
* Data transfers

No major physical network upgrade is planned.

---

# 12. Network Constraints

The platform must account for:

* Mixed Ethernet and Wi-Fi connectivity
* Finite LAN bandwidth
* Possible latency variation
* Single local network dependencies
* Router or switch failure
* Temporary node disconnection

Workloads requiring stable throughput should preferably run on wired nodes.

---

# 13. Power and Environmental Constraints

The infrastructure operates in a residential environment.

Constraints include:

* Standard residential electrical supply
* No enterprise power redundancy
* No datacenter cooling
* Possible power interruptions
* Heat generated by two GPUs
* Noise and energy consumption

The platform must avoid unnecessary continuous high-load GPU usage.

---

# 14. Fixed-Capacity Architecture

The physical infrastructure is considered fixed for the current project roadmap.

Consequently, scalability is primarily achieved through:

* Better resource allocation
* Improved workload scheduling
* Horizontal pod scaling within available capacity
* Reduced idle consumption
* Controlled service deployment
* Workload prioritization
* Retention management
* Model optimization
* Graceful degradation

Scalability must not be documented as unlimited hardware expansion.

---

# 15. Resource Governance

All Kubernetes workloads should define:

* CPU requests
* CPU limits
* Memory requests
* Memory limits
* Persistent storage requirements
* Scheduling constraints
* Priority where appropriate

Namespaces should use:

* ResourceQuota
* LimitRange
* RBAC
* NetworkPolicy

GPU workloads should additionally define:

* Explicit GPU allocation
* Node affinity
* Taints and tolerations where required
* Concurrency limits
* Workload priority

---

# 16. Capacity Management

Capacity management must focus on continuous measurement.

Key indicators include:

* CPU utilization
* RAM utilization
* Disk utilization
* Persistent volume growth
* GPU utilization
* GPU memory usage
* GPU temperature
* Network throughput
* Pod scheduling failures
* Evictions
* Node pressure
* Database growth
* Backup size

Capacity reviews should determine whether workloads need optimization, rescheduling, reduced retention or temporary deactivation.

---

# 17. Availability Model

The Kubernetes control plane provides logical high availability.

However, the physical environment may still contain shared failure domains.

Potential shared failure domains include:

* Electrical supply
* Router
* Network switch
* Proxmox host
* Local storage
* Internet connection

The platform should therefore distinguish between:

* Kubernetes-level high availability
* Virtual machine-level availability
* Physical infrastructure availability
* External connectivity availability

A highly available Kubernetes control plane does not eliminate physical single points of failure.

---

# 18. Physical Infrastructure Risks

| Risk                      | Impact | Mitigation                                     |
| ------------------------- | ------ | ---------------------------------------------- |
| Proxmox host failure      | High   | Backups, documented restoration                |
| Disk saturation           | High   | Alerts, retention and cleanup policies         |
| Disk failure              | High   | Backups and recovery procedures                |
| GPU failure               | Medium | Use remaining GPU or CPU fallback              |
| GPU memory exhaustion     | Medium | Quantization and workload limits               |
| Excessive GPU temperature | High   | Temperature monitoring and controlled usage    |
| Power outage              | High   | Graceful recovery and persistent backups       |
| Router failure            | High   | Configuration backup and replacement procedure |
| Switch failure            | High   | Replacement procedure                          |
| Wi-Fi instability         | Medium | Prefer wired nodes for critical workloads      |
| Capacity exhaustion       | High   | Quotas, limits and workload prioritization     |

---

# 19. Operational Principles

The physical infrastructure must be operated according to the following rules:

* Do not deploy services without identified value.
* Do not allocate resources without requests and limits.
* Do not assume unlimited horizontal scaling.
* Do not retain logs and metrics indefinitely.
* Do not run large AI models solely for demonstration.
* Prefer smaller, efficient and reproducible workloads.
* Measure capacity before introducing new services.
* Maintain recovery procedures for every critical stateful service.
* Treat both GTX 1080 GPUs as constrained shared resources.

---

# 20. Current State and Target State

For the physical infrastructure, the current state and target state are substantially identical.

The target is not a larger hardware environment.

The target is a better-governed and better-operated use of the current environment.

```text
Current Physical Capacity
          │
          ▼
Improved Monitoring
          │
          ▼
Resource Governance
          │
          ▼
Workload Optimization
          │
          ▼
Reliable Fixed-Capacity Platform
```

---

# 21. Architecture Decision

The project adopts a fixed-capacity infrastructure strategy.

Major hardware expansion is excluded from the current roadmap.

All platform and application designs must demonstrate that they can operate within the available compute, memory, storage, network and GPU constraints.

Any future service must therefore be evaluated against:

* Business value
* Educational value
* CPU cost
* Memory cost
* Storage cost
* GPU cost
* Operational complexity
* Availability impact

---

# 22. Related Documents

* Infrastructure Architecture
* Virtual Infrastructure Architecture
* Kubernetes Architecture
* Network Architecture
* Storage Architecture
* Capacity Planning
* AI Architecture
* Disaster Recovery Plan
* Observability Architecture
* Architecture Decision Register
