# ADR-0003 — Adopt Flannel as the Kubernetes Container Network Interface

**Status:** Accepted
**Date:** 2026-08-21
**Decision Owner:** Bastri Murad
**Domain:** Kubernetes / Networking / Infrastructure
**Project:** Enterprise AI Platform
**Related ADRs:** ADR-0001, ADR-0002
**Related Technologies:** Kubernetes, kubeadm, Flannel
**Supersedes:** None
**Superseded By:** None

---

# 1. Context

The Enterprise AI Platform operates a multi-node Kubernetes cluster deployed using kubeadm.

Kubernetes requires a Container Network Interface (CNI) implementation to provide network connectivity between Pods distributed across cluster nodes.

The platform requires:

* Pod-to-Pod communication
* Cross-node communication
* Kubernetes service networking
* Stable cluster networking
* Low operational complexity
* Low resource consumption
* Compatibility with kubeadm
* Predictable troubleshooting

The environment runs on private physical infrastructure with finite CPU, memory, storage, networking, and GPU capacity.

Networking therefore needs to remain reliable without introducing unnecessary infrastructure complexity.

---

# 2. Problem

Kubernetes itself does not provide the complete Pod network implementation.

A CNI must provide connectivity such as:

```text
Pod A
  │
  ▼
Node 1
  │
  ▼
Cluster Network
  │
  ▼
Node 2
  │
  ▼
Pod B
```

Several mature CNI implementations exist, including:

* Flannel
* Calico
* Cilium

The platform needs to select a solution appropriate to its actual requirements rather than selecting the most feature-rich technology by default.

---

# 3. Decision

The platform will use **Flannel** as the Kubernetes CNI for the current cluster.

Flannel is selected primarily because it provides:

* Simple Pod networking
* Stable cross-node connectivity
* Low operational complexity
* Low resource overhead
* Straightforward kubeadm integration
* Easy troubleshooting

The current requirement is reliable Kubernetes networking rather than advanced network-policy or eBPF functionality.

---

# 4. Architecture Role

Flannel provides the Pod network overlay.

Conceptually:

```text
                 Kubernetes Cluster

      Node 1                         Node 2

   ┌──────────┐                  ┌──────────┐
   │  Pod A   │                  │  Pod C   │
   └────┬─────┘                  └────┬─────┘
        │                             │
   ┌────▼─────┐                  ┌────▼─────┐
   │  Pod B   │                  │  Pod D   │
   └────┬─────┘                  └────┬─────┘
        │                             │
        └──────── Flannel ────────────┘
                     │
                     ▼
              Underlay Network
```

Flannel allows Pods on different Kubernetes nodes to communicate using the configured cluster Pod network.

---

# 5. Current Implementation

Flannel is already deployed and operational.

Current status:

```text
IMPLEMENTED
```

It supports connectivity across:

* Control-plane nodes
* Worker nodes
* Platform services
* Data workloads
* AI workloads
* Observability workloads

---

# 6. Alternatives Considered

## Option 1 — Flannel

Advantages:

* Simple architecture
* Lightweight
* Mature
* kubeadm friendly
* Easy troubleshooting
* Low resource requirements
* Appropriate for current platform scale

Disadvantages:

* Limited advanced networking capabilities
* Does not provide the same integrated policy capabilities as Calico or Cilium
* Limited advanced observability
* No eBPF-based networking architecture

Selected.

---

## Option 2 — Calico

Advantages:

* Mature Kubernetes networking
* Strong NetworkPolicy support
* Advanced routing capabilities
* Large Kubernetes adoption
* Good security capabilities

Disadvantages:

* More configuration
* More operational complexity
* Additional features are not currently required
* Migration would introduce network risk

Not selected for the current cluster.

Calico remains a valid future alternative if network-security requirements materially increase.

---

## Option 3 — Cilium

Advantages:

* eBPF-based networking
* Advanced observability
* Strong network-policy capabilities
* Identity-aware networking
* Advanced service networking
* Hubble observability ecosystem

Disadvantages:

* Greater conceptual complexity
* Additional operational knowledge required
* More features than the current platform requires
* Migration would affect a foundational cluster subsystem

Not selected for the current architecture.

Cilium remains a possible future candidate if its capabilities solve clearly identified requirements.

---

# 7. Decision Criteria

The decision considers:

| Criterion                 |      Importance |
| ------------------------- | --------------: |
| Reliability               |        Critical |
| Simplicity                |            High |
| Resource efficiency       |            High |
| kubeadm compatibility     |            High |
| Troubleshooting           |            High |
| NetworkPolicy             | Medium / Future |
| Advanced observability    |          Medium |
| eBPF functionality        |    Low / Future |
| Service mesh capabilities |             Low |

Flannel provides the best balance for the current environment.

---

# 8. Simplicity as an Architecture Requirement

The platform deliberately treats simplicity as a positive architecture characteristic.

A more advanced CNI does not automatically provide a better architecture.

For the current requirements:

```text
Reliable Pod Networking
        +
Low Operational Complexity
        +
Low Resource Consumption
        =
Appropriate Architecture
```

Technology selection should remain requirement-driven.

---

# 9. Resource Consequences

The physical platform has finite resources.

A lightweight CNI helps preserve capacity for:

* Applications
* Data workloads
* Airflow
* MLflow
* OpenMetadata
* Observability
* AI inference

Networking functionality should not consume resources for capabilities that are not currently required.

---

# 10. Security Limitation

The principal architectural limitation is advanced network-policy enforcement.

The desired future security model includes:

```text
Default Deny
     │
     ▼
Explicit Allowed Communication
```

The current Flannel architecture does not independently provide the complete target policy model.

This is an explicit architectural limitation rather than an undocumented gap.

---

# 11. Security Strategy

Security remains layered.

Current and planned controls include:

* Kubernetes RBAC
* Namespace separation
* TLS
* Ingress controls
* Application authentication
* Secret management
* Policy as Code
* Host firewall controls where appropriate
* Network-policy evolution

The CNI is only one part of the security architecture.

---

# 12. NetworkPolicy Requirement

If strong Kubernetes-native NetworkPolicy enforcement becomes mandatory, the architecture must be reviewed.

Possible options include:

```text
Option A
Flannel + compatible policy component

Option B
Migrate to Calico

Option C
Migrate to Cilium
```

The final choice must be based on actual requirements and testing.

---

# 13. Migration Is Not Currently Justified

The platform should not replace Flannel merely because another CNI provides more capabilities.

Migration would introduce:

* Cluster network disruption risk
* Additional testing requirements
* New operational procedures
* New troubleshooting patterns
* Potential workload interruption
* Additional technical complexity

Without a concrete requirement, these costs provide insufficient value.

---

# 14. Networking Dependency

The Kubernetes platform depends critically on CNI availability.

Failure may affect:

* Pod communication
* DNS access
* Service communication
* Observability
* Data pipelines
* AI services

CNI health must therefore be observable.

---

# 15. Observability

The networking layer should be monitored through:

* Node health
* Pod connectivity
* CNI Pod status
* Kubernetes networking metrics
* DNS availability
* Synthetic connectivity tests where appropriate

The platform does not require a second observability platform solely for CNI monitoring.

---

# 16. DNS Relationship

Flannel provides Pod networking but does not replace Kubernetes DNS.

The relationship is:

```text
Application
    │
    ▼
CoreDNS
    │
    ▼
Service Resolution
    │
    ▼
Kubernetes Networking
    │
    ▼
Flannel Pod Network
```

DNS failures and CNI failures must therefore be diagnosed separately.

---

# 17. Underlay Dependency

Flannel depends on the physical/virtual network between Kubernetes nodes.

Therefore:

```text
Pod Network Health
       │
       ▼
Depends On
       │
       ▼
Node-to-Node Network Health
```

A failure in the underlay network can appear as a Kubernetes networking failure.

---

# 18. Routing Lessons

The current environment has already demonstrated the importance of correct routing between Kubernetes node networks.

Static routing has been required in parts of the infrastructure to restore communication with worker nodes.

This confirms that CNI troubleshooting must consider both:

```text
Kubernetes Overlay
+
Physical / VM Underlay
```

rather than examining Flannel in isolation.

---

# 19. Failure Domains

Possible networking failures include:

```text
Physical Network
      │
      ▼
VM Network
      │
      ▼
Node Routing
      │
      ▼
Flannel
      │
      ▼
CoreDNS
      │
      ▼
Service
      │
      ▼
Application
```

Troubleshooting should follow the dependency chain systematically.

---

# 20. GitOps Consequences

Flannel configuration should be documented and, where practical, managed declaratively.

Changes to the CNI are high-impact infrastructure changes.

They must not be treated like normal application deployments.

---

# 21. Change Management

Changes affecting Flannel require elevated review because networking failure can affect the complete Kubernetes platform.

Examples:

* Pod CIDR changes
* Backend changes
* Interface configuration
* CNI upgrades
* CNI migration

These changes require:

* Backup/recovery planning
* Validation
* Rollback strategy
* Maintenance consideration

---

# 22. Upgrade Governance

Flannel upgrades should consider:

* Kubernetes compatibility
* Release notes
* Security fixes
* Configuration changes
* Existing routing
* Rollback procedure

Automatic uncontrolled major-version upgrades are not appropriate.

---

# 23. High Availability Consequences

Flannel runs across Kubernetes nodes.

This avoids dependence on a single centralized networking service.

However, cluster networking still depends on:

* Physical switches
* Routers
* Node interfaces
* Proxmox networking
* Correct routing

Kubernetes overlay redundancy cannot remove physical infrastructure failure domains.

---

# 24. Disaster Recovery

Cluster reconstruction requires restoration of compatible networking before application workloads can operate correctly.

Simplified recovery order:

```text
Infrastructure
      │
      ▼
Linux Nodes
      │
      ▼
Kubernetes Control Plane
      │
      ▼
CNI / Flannel
      │
      ▼
CoreDNS
      │
      ▼
Platform Services
      │
      ▼
Applications
```

The CNI is therefore an early-stage recovery dependency.

---

# 25. Risks

## Risk — Limited Network Policy Capability

Mitigation:

* Layered security
* Policy evaluation
* Future CNI review if requirements change

---

## Risk — Underlay Routing Failure

Mitigation:

* Network documentation
* Static-route management where required
* Connectivity monitoring
* Troubleshooting procedures

---

## Risk — CNI Failure Impacts Cluster Communication

Mitigation:

* CNI monitoring
* Kubernetes monitoring
* Runbooks
* Controlled upgrades

---

## Risk — Future Requirements Outgrow Flannel

Mitigation:

* Technology Governance
* Architecture review
* ADR-based migration decision

---

# 26. Technical Debt Consideration

Using Flannel is **not currently classified as technical debt**.

It satisfies the current networking requirements.

It becomes a technical-debt candidate only if:

```text
Required Capability
      >
Flannel Capability
```

and the platform continues using Flannel without an appropriate mitigation or migration plan.

---

# 27. Technology Governance Status

Recommended Technology Radar classification:

```text
Technology: Flannel
Category: Kubernetes Networking
Lifecycle: ADOPT
```

This status should be reviewed if network-security requirements change.

---

# 28. Future Review Criteria

Flannel should be reconsidered if the platform requires:

* Strong native NetworkPolicy enforcement
* Advanced network observability
* eBPF networking
* Identity-aware network security
* Advanced multi-cluster networking
* Significant Kubernetes scale increase
* Service-mesh-like network functionality

These are review triggers, not current requirements.

---

# 29. Possible Future Migration

If migration becomes necessary:

```text
Requirements
     │
     ▼
Technology Evaluation
     │
     ├── Flannel + Policy
     ├── Calico
     └── Cilium
     │
     ▼
Lab Testing
     │
     ▼
Decision Matrix
     │
     ▼
ADR
     │
     ▼
Migration Plan
```

No migration should occur directly in the operational cluster without controlled validation.

---

# 30. Success Criteria

The Flannel decision remains successful while:

* Pods communicate reliably across nodes
* Network performance satisfies workloads
* Operational complexity remains low
* CNI resource consumption remains appropriate
* Current security requirements can be met through the overall architecture
* No critical required feature is blocked

---

# 31. Implementation Evidence

Current evidence includes:

* Operational multi-node Kubernetes cluster
* Cross-node workload communication
* Platform services operating across workers
* Airflow workloads
* MLflow workloads
* OpenMetadata
* Monitoring
* GitOps-controlled applications

This confirms that Flannel fulfills the current core networking requirement.

---

# 32. Decision Outcome

The architecture deliberately chooses:

```text
Flannel
+
Simplicity
+
Low Resource Cost
+
Known Operational Model
```

instead of introducing a more complex CNI without a demonstrated requirement.

This is an intentional architecture decision, not a temporary workaround.

---

# 33. Governance as Code Metadata

Future machine-readable representation:

```yaml
id: ADR-0003
title: Adopt Flannel as Kubernetes CNI
status: accepted

domain:
  - kubernetes
  - networking
  - infrastructure

technologies:
  - flannel
  - kubernetes

owner: platform
implementation_status: implemented

alternatives:
  - calico
  - cilium

review_triggers:
  - advanced-network-policy-required
  - ebpf-required
  - advanced-network-observability-required
  - multi-cluster-networking-required

supersedes: null
superseded_by: null
```

---

# 34. Related Documents

* ADR-0001-Kubernetes
* ADR-0002-ArgoCD-GitOps
* Kubernetes Architecture
* Network Architecture
* Security Architecture
* High Availability
* Disaster Recovery
* Technology Governance
* Technical Debt Management
* Architecture Roadmap
