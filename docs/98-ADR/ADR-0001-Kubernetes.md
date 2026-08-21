# ADR-0001 — Adopt Kubernetes as the Primary Container Orchestration Platform

**Status:** Accepted
**Date:** 2026-08-21
**Decision Owner:** Bastri Murad
**Domain:** Infrastructure / Platform / DevOps
**Project:** Enterprise AI Platform
**Related Risks:** RISK-INFRA-001, RISK-K8S-001
**Related Technologies:** Kubernetes, kubeadm, Flannel, NGINX Ingress, cert-manager
**Supersedes:** None
**Superseded By:** None

---

# 1. Context

The Enterprise AI Platform requires a standardized runtime environment capable of hosting:

* Business applications
* Data services
* AI services
* MLOps workloads
* Observability services
* GitOps components
* Governance automation
* Supporting platform services

The platform must support:

* Containerized workloads
* Multi-service deployments
* Declarative configuration
* Automated reconciliation
* Horizontal workload distribution
* Rolling updates
* Service discovery
* Persistent workloads
* Observability
* GitOps
* High availability where practical

The physical infrastructure is resource constrained and based on the existing private environment.

The architecture must therefore provide strong automation and reproducibility without requiring large-scale cloud infrastructure.

---

# 2. Problem

Running every application directly on individual virtual machines or manually managed Docker hosts would create several long-term problems:

* Configuration drift
* Manual deployment
* Difficult service discovery
* Inconsistent runtime configuration
* Higher operational toil
* Limited workload scheduling
* More difficult GitOps adoption
* More difficult platform standardization

A common orchestration layer is therefore required.

---

# 3. Decision

The platform will use **Kubernetes** as the primary orchestration platform for containerized workloads.

The Kubernetes environment will use:

```text
kubeadm
```

for cluster bootstrap and management.

The current architecture uses:

* Multiple control-plane nodes
* Multiple worker nodes
* Flannel CNI
* NGINX Ingress
* cert-manager
* Argo CD
* Kubernetes-native monitoring

Kubernetes becomes the default runtime target for platform services unless a documented exception exists.

---

# 4. Architecture Role

Kubernetes provides:

* Container orchestration
* Workload scheduling
* Service discovery
* Declarative desired state
* Health management
* Replica management
* Rolling deployments
* Stateful workload support
* Configuration management
* Secret integration
* Resource management
* Namespace isolation

It also provides the runtime foundation for GitOps and Governance as Code.

---

# 5. High-Level Architecture

```text
Physical Infrastructure
        │
        ▼
Proxmox
        │
        ▼
Linux Virtual Machines
        │
        ▼
Kubernetes
        │
        ├── Control Plane
        ├── Worker Nodes
        ├── Networking
        ├── Storage
        └── Platform Services
```

Applications are deployed declaratively on Kubernetes.

---

# 6. Alternatives Considered

## Option 1 — Kubernetes

Advantages:

* Industry-standard orchestration
* Strong ecosystem
* Declarative configuration
* GitOps support
* Workload scheduling
* High availability capabilities
* Large community
* Strong observability ecosystem
* Good alignment with enterprise DevOps

Disadvantages:

* Operational complexity
* Requires learning and maintenance
* Higher baseline resource consumption than simple Docker

---

## Option 2 — Docker Compose

Advantages:

* Simple
* Lightweight
* Easy local development
* Low operational overhead

Disadvantages:

* Limited orchestration
* Limited self-healing
* No native multi-node scheduling
* Limited enterprise GitOps model
* More difficult platform governance

Docker Compose remains useful for development and small isolated workloads but is not selected as the primary enterprise runtime.

---

## Option 3 — Nomad

Advantages:

* Simpler than Kubernetes in some environments
* Lightweight
* Good scheduler

Disadvantages:

* Smaller ecosystem
* Less alignment with existing project skills and tooling
* Weaker integration with the chosen Kubernetes-native platform stack
* Additional technology to govern

Not selected.

---

## Option 4 — Direct VM Deployment

Advantages:

* Simple conceptual model
* Low orchestration overhead

Disadvantages:

* Manual configuration
* Configuration drift
* Poor workload portability
* Limited self-healing
* Difficult GitOps adoption
* Higher long-term operational toil

Not selected.

---

# 7. Decision Criteria

The decision was evaluated against:

* Automation
* Reproducibility
* GitOps compatibility
* Enterprise relevance
* Observability integration
* Multi-service support
* Workload scheduling
* Platform standardization
* Community support
* Operational resilience

Kubernetes provides the best overall fit.

---

# 8. Consequences

## Positive Consequences

The platform gains:

* Standardized runtime
* Declarative deployments
* Self-healing workloads
* Centralized resource management
* GitOps compatibility
* Better observability
* Improved workload isolation
* Scalable service deployment
* Stronger enterprise architecture alignment

---

## Negative Consequences

The platform must accept:

* Increased operational complexity
* More networking complexity
* More platform components
* Higher baseline resource consumption
* Kubernetes lifecycle management responsibility

These costs are accepted because Kubernetes provides substantial long-term platform value.

---

# 9. Operational Consequences

Platform operations must maintain:

* Control-plane health
* Worker health
* CNI
* DNS
* Ingress
* Storage
* Kubernetes upgrades
* Certificates
* Monitoring

Operational runbooks are therefore required.

---

# 10. Security Consequences

Kubernetes introduces a significant security boundary.

Required controls include:

* RBAC
* TLS
* Namespace isolation
* Secret management
* Container security
* NetworkPolicies
* Admission policies
* Auditability

Policy as Code is planned as a future maturity improvement.

---

# 11. Resource Consequences

Kubernetes requires:

* Control-plane CPU and memory
* Worker resources
* Networking overhead
* Observability resources

Because the physical platform is fixed, workload scheduling and resource governance are mandatory.

Kubernetes should not be expanded unnecessarily.

---

# 12. GitOps Consequences

Kubernetes enables the selected GitOps architecture.

Target deployment model:

```text
Git
 ↓
Argo CD
 ↓
Kubernetes
```

Production Kubernetes resources should progressively become Git-managed.

Manual runtime configuration is treated as exceptional.

---

# 13. Governance Consequences

Kubernetes becomes a primary enforcement point for Governance as Code.

Future governance mechanisms may include:

* Kyverno
* OPA Gatekeeper
* Admission policies
* Resource standards
* Security standards
* Ownership labels
* Policy reports

This turns Kubernetes into both a runtime platform and a governance enforcement layer.

---

# 14. Availability Consequences

Kubernetes improves logical availability through:

* ReplicaSets
* Pod restart
* Rescheduling
* Multiple workers
* Multiple control-plane nodes

However:

> Kubernetes logical redundancy does not eliminate physical infrastructure failure domains.

This limitation remains explicitly accepted.

---

# 15. Recovery Consequences

Kubernetes workloads should be recoverable through:

* GitOps
* Argo CD
* Helm
* Kubernetes manifests
* Velero where appropriate
* Application-level backups

Git is the primary source of truth for declarative state.

---

# 16. Observability Consequences

Kubernetes integrates with:

* Prometheus
* Grafana
* Loki
* Tempo
* OpenTelemetry
* kube-state-metrics
* node-exporter

This provides comprehensive operational visibility.

---

# 17. Risks

Key risks include:

## Cluster Complexity

Mitigation:

* Documentation
* Standardized deployment
* GitOps
* Runbooks
* Monitoring

## Resource Saturation

Mitigation:

* Requests and limits
* Capacity monitoring
* Workload prioritization

## Network Failure

Mitigation:

* CNI monitoring
* DNS monitoring
* Recovery procedures

## Configuration Drift

Mitigation:

* GitOps
* Argo CD reconciliation

---

# 18. Constraints

The decision must respect:

* Existing physical hardware
* Existing Proxmox platform
* Limited spare compute capacity
* Limited GPU resources
* Single primary physical environment

Kubernetes is selected to improve platform maturity, not to simulate unlimited cloud-scale infrastructure.

---

# 19. Implementation Status

Status:

```text
IMPLEMENTED
```

Current capabilities include:

* HA kubeadm control plane
* Multiple workers
* Flannel
* NGINX Ingress
* cert-manager
* Argo CD
* Prometheus-based monitoring
* Multiple production-style namespaces and workloads

---

# 20. Validation

The decision is validated by existing operational use.

Evidence includes:

* Running Kubernetes cluster
* Multi-node scheduling
* Argo CD GitOps
* Airflow
* MLflow
* OpenMetadata
* Observability platform
* Data platform workloads

Kubernetes has successfully become the central runtime platform.

---

# 21. Review Triggers

This decision should be reviewed if:

* Kubernetes becomes unsupported for project requirements
* Physical resource overhead becomes unacceptable
* Operational complexity exceeds platform value
* A replacement platform provides substantial measurable benefits
* The infrastructure architecture changes fundamentally

No review is currently required.

---

# 22. Governance as Code Metadata

Future structured representation:

```yaml
id: ADR-0001
title: Adopt Kubernetes as Primary Container Orchestration Platform
status: accepted
domain:
  - infrastructure
  - platform
  - devops

technology:
  - kubernetes

owner: platform

related_risks:
  - RISK-INFRA-001
  - RISK-K8S-001

implementation_status: implemented

decision_date: 2026-08-21
```

This metadata can later support automated ADR indexing and governance validation.

---

# 23. Related Documents

* Kubernetes Architecture
* Infrastructure Architecture
* Platform Engineering
* GitOps Architecture
* High Availability
* Availability Management
* Disaster Recovery
* Governance Architecture
* Architecture Governance
* Technology Governance
* Risk Management
