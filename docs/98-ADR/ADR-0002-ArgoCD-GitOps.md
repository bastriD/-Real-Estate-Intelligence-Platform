# ADR-0002 — Adopt Argo CD and GitOps as the Primary Deployment and Desired-State Management Model

**Status:** Accepted
**Date:** 2026-08-21
**Decision Owner:** Bastri Murad
**Domain:** DevOps / Platform / Governance
**Project:** Enterprise AI Platform
**Related Risks:** RISK-OPS-001, RISK-K8S-002, RISK-SEC-004
**Related Technologies:** GitLab, Argo CD, Kubernetes, Helm, Kustomize
**Supersedes:** None
**Superseded By:** None

---

# 1. Context

The Enterprise AI Platform runs a growing number of services on Kubernetes.

These services include:

* Business applications
* Airflow
* MLflow
* OpenMetadata
* Monitoring
* Logging
* Tracing
* Governance automation
* Data workloads
* AI workloads

Manual deployment using direct `kubectl`, shell scripts, or locally executed Helm commands would create several risks:

* Configuration drift
* Undocumented production changes
* Difficult rollback
* Weak auditability
* Environment inconsistencies
* Increased operational toil
* Reduced recoverability

A standardized mechanism is required to manage Kubernetes desired state.

---

# 2. Problem

The platform requires a deployment model that provides:

* Declarative configuration
* Git-based source of truth
* Version history
* Peer review
* Automated reconciliation
* Drift detection
* Rollback
* Environment reproducibility
* Disaster recovery support
* Governance integration

Traditional CI pipelines that directly execute deployment commands can deploy applications successfully but do not continuously guarantee that runtime state remains aligned with approved configuration.

---

# 3. Decision

The platform will adopt **GitOps** as the primary Kubernetes deployment and desired-state management model.

**Argo CD** is selected as the primary GitOps controller.

The operational model is:

```text
Engineering Change
       │
       ▼
Git Repository
       │
       ▼
Merge Request / Review
       │
       ▼
Approved Desired State
       │
       ▼
Argo CD
       │
       ▼
Kubernetes
       │
       ▼
Continuous Reconciliation
```

Git becomes the authoritative desired-state source for Kubernetes-managed platform configuration.

---

# 4. Architecture Role

Argo CD provides:

* Git repository integration
* Kubernetes desired-state comparison
* Synchronization
* Drift detection
* Automated reconciliation
* Deployment history
* Application health visibility
* Rollback support
* Multi-namespace application management

GitOps becomes a core platform operating principle rather than only a deployment mechanism.

---

# 5. Current Implementation

The current platform already implements:

* Argo CD
* Git-based Kubernetes manifests
* Root application pattern
* Automated synchronization
* Auto-prune
* Self-heal
* Multiple Git-managed services
* Deployment history

Current state:

```text
IMPLEMENTED
```

---

# 6. Root Application Pattern

The platform uses a root-application approach.

Conceptually:

```text
Argo CD
   │
   ▼
Root Application
   │
   ├── Monitoring
   ├── Airflow
   ├── MLflow
   ├── Data Services
   ├── Governance
   └── Additional Applications
```

This enables the platform state to be reconstructed from a relatively small GitOps bootstrap configuration.

---

# 7. Alternatives Considered

## Option 1 — Argo CD

Advantages:

* Kubernetes-native
* Strong GitOps model
* Declarative
* Mature UI
* Drift detection
* Self-healing
* Application health
* Large community
* Strong Helm/Kustomize support

Disadvantages:

* Additional platform component
* Requires repository credential management
* Incorrect auto-sync configuration can propagate mistakes rapidly

Selected.

---

## Option 2 — Flux CD

Advantages:

* Mature GitOps platform
* Kubernetes-native
* Strong automation
* Lightweight architecture

Disadvantages:

* Existing platform already uses Argo CD
* Migration would provide limited additional value
* Would introduce unnecessary operational change

Not selected.

---

## Option 3 — GitLab CI Direct Deployment

Example:

```text
GitLab CI
   │
   ▼
kubectl / helm
   │
   ▼
Kubernetes
```

Advantages:

* Simple deployment flow
* Existing GitLab integration
* No separate GitOps controller required

Disadvantages:

* CI acts only when pipeline runs
* Runtime drift can remain undetected
* Reduced continuous reconciliation
* Deployment credentials embedded into CI model
* Weaker disaster-reconstruction model

Not selected as the primary Kubernetes deployment mechanism.

GitLab CI remains responsible for build, testing, validation, and artifact production.

---

## Option 4 — Manual Deployment

Examples:

```bash
kubectl apply
helm install
helm upgrade
```

Advantages:

* Simple for initial experimentation
* Fast for debugging

Disadvantages:

* Poor auditability
* Configuration drift
* Weak reproducibility
* High operational toil
* Increased human-error risk

Not accepted as the standard production model.

---

# 8. CI vs GitOps Responsibility

The platform intentionally separates CI and CD responsibilities.

```text
GitLab CI
     │
     ├── Build
     ├── Test
     ├── Scan
     ├── Validate
     └── Produce Artifact
              │
              ▼
             Git
              │
              ▼
           Argo CD
              │
              ▼
          Kubernetes
```

GitLab CI should not routinely bypass Argo CD for production changes.

---

# 9. Git as Source of Truth

The authoritative state should be represented in Git through artifacts such as:

* Kubernetes manifests
* Helm values
* Kustomize overlays
* Argo CD Applications
* ConfigMaps where appropriate
* Monitoring configuration
* Governance configuration

Runtime state should not become an alternative uncontrolled source of truth.

---

# 10. Manual Change Policy

Manual cluster changes may occasionally be required during emergency recovery or troubleshooting.

However:

```text
Manual change
     │
     ▼
Temporary Runtime State
     │
     ▼
Git Must Be Updated
     │
     ▼
Desired State Restored
```

Permanent manual configuration is considered architecture drift.

---

# 11. Self-Healing

Argo CD self-healing is used to reconcile runtime state with Git.

Example:

```text
Approved Git State
       │
       ▼
Manual Runtime Modification
       │
       ▼
Drift Detected
       │
       ▼
Argo CD Reconciliation
```

This provides a continuous governance mechanism.

---

# 12. Auto-Prune

Auto-pruning allows resources removed from Git to be removed from Kubernetes.

Benefit:

* Prevents orphaned resources
* Maintains desired-state consistency

Risk:

An incorrect Git deletion may remove valid production resources.

Therefore Git review quality is critical.

---

# 13. Change Governance

The GitOps model integrates directly with Change Management.

Standard change path:

```text
Change
  │
  ▼
Branch
  │
  ▼
Merge Request
  │
  ▼
CI Validation
  │
  ▼
Approval
  │
  ▼
Merge
  │
  ▼
Argo CD
  │
  ▼
Deployment
```

Git history provides change evidence.

---

# 14. Governance as Code

GitOps is a primary runtime enforcement mechanism for Governance as Code.

The broader governance model becomes:

```text
Policy / Standard
       │
       ▼
Machine-Readable Configuration
       │
       ▼
Git
       │
       ▼
CI Validation
       │
       ▼
Argo CD
       │
       ▼
Kubernetes
       │
       ▼
Continuous Reconciliation
```

This turns GitOps into part of the platform governance architecture.

---

# 15. Policy as Code Integration

Future Policy as Code can operate alongside Argo CD.

Example:

```text
Git
 │
 ▼
CI Policy Check
 │
 ▼
Argo CD
 │
 ▼
Kubernetes Admission Policy
 │
 ├── Compliant → Accepted
 │
 └── Non-Compliant → Rejected
```

This provides both pre-deployment and runtime enforcement.

---

# 16. Security Consequences

Argo CD becomes a high-value platform service.

Security controls must include:

* RBAC
* Restricted administrative access
* Secure Git credentials
* TLS
* Repository access control
* Secret protection
* Network controls where appropriate

Compromise of Argo CD could allow broad platform modification.

---

# 17. Repository Security

GitOps repositories contain sensitive architecture information.

They may reveal:

* Internal service names
* Network structure
* Application configuration
* Deployment topology

Actual credentials must not be stored in plaintext Git.

---

# 18. Secrets

GitOps does not imply that plaintext secrets belong in Git.

Secrets should be handled using approved mechanisms.

Future options may include:

* Sealed Secrets
* External Secrets Operator
* HashiCorp Vault integration

Selection should follow ADR and Technology Governance when introduced.

---

# 19. Availability Consequences

If Argo CD becomes unavailable:

* Existing Kubernetes workloads generally continue running
* New GitOps deployments stop
* Drift reconciliation stops
* GitOps visibility is lost temporarily

Therefore Argo CD is operationally important but should not become a runtime dependency for normal application requests.

---

# 20. Disaster Recovery Consequences

GitOps significantly improves recovery.

Recovery model:

```text
Recovered Kubernetes
       │
       ▼
Install Argo CD
       │
       ▼
Connect Git Repository
       │
       ▼
Apply Root Application
       │
       ▼
Reconcile Platform
```

This reduces manual reconstruction effort.

---

# 21. Backup Consequences

Git repositories become critical recovery assets.

They must therefore be protected separately from the active GitLab instance.

Recovery should not assume that GitLab and its repositories are always simultaneously available.

---

# 22. Observability Consequences

Argo CD should be monitored for:

* Application health
* Sync status
* Repository connectivity
* Reconciliation failures
* Controller health

Logs and metrics should integrate with the platform observability stack.

---

# 23. Drift Detection

Drift is one of the primary reasons for adopting GitOps.

Examples include:

* Manual edits
* Modified resource values
* Deleted resources
* Unauthorized configuration

Argo CD exposes differences between desired and actual state.

---

# 24. Drift Governance

Repeated drift may indicate:

* Manual operational habits
* Missing Git configuration
* Incorrect automation
* Emergency changes not reconciled

Persistent drift should enter Problem Management or Technical Debt Management where appropriate.

---

# 25. Deployment Rollback

Rollback can occur through:

```text
Git Revert
    │
    ▼
Argo CD Reconciliation
```

or through controlled synchronization to a previous desired state.

Git revert is preferred because it preserves the desired-state audit history.

---

# 26. Rollback Limitations

Git rollback alone may not fully reverse:

* Database migrations
* External side effects
* Destructive state changes

Applications with stateful changes require dedicated rollback or recovery strategies.

GitOps does not eliminate application-level deployment risk.

---

# 27. Deployment Ordering

Some services have dependencies.

Argo CD may use controlled synchronization ordering where required.

Examples include:

```text
Namespace
   ↓
CRDs
   ↓
Operator
   ↓
Application
```

Dependency ordering should remain explicit and limited to actual needs.

---

# 28. Environment Strategy

GitOps should support environment-specific configuration without uncontrolled duplication.

Potential approaches include:

* Helm values
* Kustomize overlays
* Separate environment directories

The exact model should remain consistent across repositories.

---

# 29. Application Ownership

Argo CD Applications should expose enough metadata to identify:

* Service
* Namespace
* Repository
* Owner
* Environment

Ownership metadata will support future Governance as Code controls.

---

# 30. Resource Constraints

Argo CD consumes platform resources but provides substantial operational value.

The platform should avoid unnecessary duplication such as running multiple GitOps controllers without a demonstrated need.

Current scale does not require highly complex multi-Argo-CD topology.

---

# 31. Risks

## Risk — Incorrect Git Change Propagates Automatically

Mitigation:

* Merge Request review
* CI validation
* Policy as Code
* Controlled synchronization for sensitive services

---

## Risk — Argo CD Compromise

Mitigation:

* RBAC
* Restricted credentials
* Security monitoring
* Network controls
* Least privilege

---

## Risk — Git Repository Unavailable

Mitigation:

* Repository backup
* GitLab recovery
* Local or independent mirror strategy where justified

---

## Risk — Accidental Prune

Mitigation:

* Peer review
* Change validation
* Protected branches
* Appropriate sync policy

---

# 32. Benefits

The decision provides:

* Reduced configuration drift
* Improved deployment reproducibility
* Strong audit trail
* Easier rollback
* Better disaster recovery
* Continuous reconciliation
* Lower manual operational effort
* Strong foundation for Governance as Code

---

# 33. Negative Consequences

The platform accepts:

* Dependency on Argo CD for deployment automation
* Need to protect GitOps credentials
* Requirement for disciplined Git workflows
* Potential impact of incorrect automated changes
* Additional operational service to maintain

These costs are accepted.

---

# 34. Implementation Evidence

Current evidence includes:

* Running Argo CD platform
* Root application
* Self-healing
* Auto-prune
* Git-managed workloads
* Deployment history
* GitOps-controlled platform components

This confirms that the decision has already been implemented successfully.

---

# 35. Success Criteria

The GitOps architecture is successful when:

* Production desired state exists in Git
* Argo CD reports expected Applications healthy
* Manual drift is detected
* Platform reconstruction from Git is possible
* Deployment history is auditable
* Production changes normally follow review workflow

---

# 36. Review Triggers

Review this ADR if:

* Argo CD no longer meets platform requirements
* Operational overhead becomes excessive
* Another GitOps technology offers substantial measurable benefit
* GitOps architecture changes fundamentally
* Multi-cluster architecture creates new requirements

No current review is required.

---

# 37. Governance as Code Metadata

Future machine-readable representation:

```yaml
id: ADR-0002

title: Adopt Argo CD and GitOps

status: accepted

domain:
  - devops
  - platform
  - governance

technologies:
  - argocd
  - gitlab
  - kubernetes

owner: platform

implementation_status: implemented

related_risks:
  - RISK-OPS-001
  - RISK-K8S-002
  - RISK-SEC-004

supersedes: null
superseded_by: null
```

---

# 38. Related Documents

* ADR-0001-Kubernetes
* GitOps Architecture
* CI/CD Architecture
* Platform Engineering
* Change Management
* Disaster Recovery
* Backup and Restore
* Governance Architecture
* Architecture Governance
* Security Architecture
* Technology Governance
