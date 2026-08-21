# ADR-0012 — Adopt GitLab as the Primary Source Control and CI Platform

**Status:** Accepted
**Date:** 2026-08-21
**Decision Owner:** Bastri Murad
**Domain:** DevOps / Platform / Governance / Security
**Project:** Enterprise AI Platform
**Related ADRs:** ADR-0001, ADR-0002, ADR-0010, ADR-0011
**Related Technologies:** GitLab CE, GitLab Runner, Docker, Kubernetes, Argo CD, Git
**Supersedes:** None
**Superseded By:** None

---

# 1. Context

The Enterprise AI Platform requires a central engineering platform for:

* Source control
* Branch management
* Merge requests
* Code review
* CI pipelines
* Build automation
* Automated testing
* Security scanning
* Artifact production
* Governance validation
* Change traceability

The platform already uses Git extensively for:

* Application source code
* GitOps repositories
* Airflow DAGs
* Data platform configuration
* Governance definitions
* Documentation
* Architecture artifacts

A common Git and CI platform is therefore required.

---

# 2. Problem

Without a centralized engineering workflow, platform changes could be performed through:

* Local repositories
* Manual scripts
* Direct Kubernetes changes
* Unreviewed configuration
* Ad hoc build processes
* Uncontrolled production deployment

This would create:

* Weak auditability
* Inconsistent quality
* Configuration drift
* Increased security risk
* Poor governance evidence
* Difficult rollback
* Dependence on individual workstations

The platform requires a standardized engineering control plane.

---

# 3. Decision

The platform will use **GitLab CE** as the primary source-control and Continuous Integration platform.

GitLab is responsible for:

* Git repository hosting
* Branch protection
* Merge Requests
* Code review
* CI pipeline execution
* Build automation
* Test execution
* Security and quality gates
* Artifact production
* Governance validation

GitLab CI is intentionally separated from Kubernetes continuous deployment.

**Argo CD remains responsible for GitOps deployment and runtime reconciliation.**

---

# 4. Core Delivery Model

The standard delivery architecture is:

```text
Developer
   │
   ▼
Git Branch
   │
   ▼
GitLab Merge Request
   │
   ▼
GitLab CI
   │
   ├── Validate
   ├── Test
   ├── Scan
   ├── Build
   └── Produce Artifact
            │
            ▼
         Git / Registry
            │
            ▼
          Argo CD
            │
            ▼
         Kubernetes
```

This establishes a clear separation between:

```text
CI
→ Build and Validate

CD
→ GitOps Reconciliation
```

---

# 5. Current Implementation

GitLab CE is already deployed and operational.

Current capabilities include:

* GitLab CE
* Internal repositories
* GitLab Runner
* Docker executor
* CI pipelines
* GitOps repositories
* Airflow DAG repository
* Data repositories
* Governance repositories
* Platform repositories

Current state:

```text
IMPLEMENTED
```

---

# 6. Current Repository Examples

Existing repositories include platform and workload repositories such as:

```text
lab-gitops
airflow-dags
retail-analytics-platform
retail_governance
```

These demonstrate separation between:

* Platform desired state
* Workflow definitions
* Application/data code
* Governance configuration

---

# 7. Alternatives Considered

## Option 1 — GitLab

Advantages:

* Git hosting
* Integrated CI
* Merge Requests
* Branch protection
* Self-hosting
* Container registry capabilities
* Strong DevOps integration
* Mature runner model
* Good auditability
* Good Governance as Code fit

Disadvantages:

* Requires significant infrastructure
* Upgrades and backups must be managed
* GitLab itself becomes a critical engineering dependency

Selected.

---

## Option 2 — GitHub

Advantages:

* Very mature ecosystem
* GitHub Actions
* Large integration marketplace
* Strong hosted experience

Disadvantages:

* Hosted external dependency unless GitHub Enterprise is introduced
* Reduced local sovereignty compared with current self-hosted GitLab
* Existing platform is already standardized on GitLab

Not selected as the primary internal platform.

---

## Option 3 — Gitea / Forgejo

Advantages:

* Lightweight
* Self-hosted
* Lower resource consumption
* Good Git functionality

Disadvantages:

* Less integrated enterprise CI/governance capability than GitLab
* Would require additional pipeline tooling
* Existing GitLab already satisfies requirements

Not selected.

---

## Option 4 — Jenkins + Separate Git Server

Advantages:

* Flexible
* Mature CI ecosystem

Disadvantages:

* Additional technology
* More integration work
* More plugin governance
* Separate source and CI control planes
* Higher maintenance burden

Not selected.

---

# 8. Decision Criteria

The decision considered:

| Criterion                 | Importance |
| ------------------------- | ---------: |
| Self-hosting              |   Critical |
| Git repository management |   Critical |
| CI integration            |   Critical |
| Merge Request workflow    |       High |
| Branch protection         |       High |
| Security integration      |       High |
| GitOps compatibility      |   Critical |
| Auditability              |   Critical |
| Governance automation     |   Critical |
| Operational simplicity    |       High |

GitLab provides the strongest fit with the platform architecture.

---

# 9. Git as Source of Truth

Git is a foundational architectural mechanism.

It stores authoritative versions of:

* Application source code
* Kubernetes manifests
* Helm values
* Airflow DAGs
* dbt models
* Governance definitions
* Documentation
* ADRs
* Policies
* SLO definitions

Git therefore supports both engineering delivery and governance.

---

# 10. Repository Separation

Repositories should be separated according to lifecycle and ownership where useful.

Conceptual model:

```text
Application Repository
        │
        ├── Source
        ├── Tests
        └── Dockerfile

GitOps Repository
        │
        ├── Kubernetes
        ├── Helm values
        └── Environment config

Governance Repository
        │
        ├── Risks
        ├── Policies
        ├── Controls
        └── Metadata
```

Separation should avoid unnecessary fragmentation.

---

# 11. Branch Strategy

Production-relevant repositories should use controlled branches.

Typical model:

```text
feature/*
   │
   ▼
Merge Request
   │
   ▼
main
```

Protected branches should prevent uncontrolled direct changes.

The exact branch strategy may vary by repository complexity.

---

# 12. Merge Requests

Merge Requests provide an important governance boundary.

They support:

* Review
* Discussion
* CI results
* Change history
* Approval
* Auditability

Production changes should normally enter protected branches through Merge Requests.

---

# 13. Review Governance

Review intensity should remain risk based.

Examples:

```text
Documentation typo
→ lightweight review

Application change
→ technical review + CI

Security policy
→ stronger review

Architecture standard
→ governance / architecture review
```

Not every change requires the same approval burden.

---

# 14. GitLab CI Role

GitLab CI provides automated validation before a change becomes authoritative.

Typical stages may include:

```text
lint
test
security
build
validate
publish
```

Exact pipelines vary by repository.

---

# 15. CI Pipeline Principle

The CI pipeline answers:

> Is this change acceptable to merge?

Argo CD answers:

> Does runtime match the approved Git state?

This distinction is intentional.

---

# 16. CI/CD Separation

The architecture explicitly avoids using GitLab CI as the only runtime deployment controller.

Direct pattern:

```text
GitLab CI
   │
   ▼
kubectl apply
```

may work technically, but does not provide continuous desired-state reconciliation.

The preferred model remains:

```text
GitLab CI
   │
   ▼
Approved Git State
   │
   ▼
Argo CD
   │
   ▼
Kubernetes
```

---

# 17. Build Pipelines

Application CI should typically perform:

```text
Source
  │
  ▼
Lint
  │
  ▼
Unit Tests
  │
  ▼
Security Checks
  │
  ▼
Build Image
  │
  ▼
Publish Artifact
```

Only validated artifacts should proceed toward deployment.

---

# 18. Container Image Build

Containerized workloads should produce reproducible images.

Controls should progressively include:

* Explicit base image
* Version pinning
* Dependency control
* Vulnerability scanning
* Image metadata

Mutable uncontrolled images should be avoided.

---

# 19. Artifact Identity

Deployments should be traceable to an immutable artifact.

Preferred patterns include:

* Semantic version
* Git SHA
* Immutable container digest

Example:

```text
business-api:1.4.2
```

or:

```text
business-api:git-a93f21d
```

Production should avoid ambiguous artifact identity where practical.

---

# 20. Git Commit Traceability

A deployed artifact should ideally be traceable to:

```text
Runtime
  │
  ▼
Container Image
  │
  ▼
Git SHA
  │
  ▼
Merge Request
```

This significantly improves incident investigation.

---

# 21. CI Runner Architecture

GitLab Runner executes CI jobs.

The current environment uses a Docker executor.

This provides:

* Job isolation
* Reproducible execution environments
* Container-based CI tooling

Runner access should be governed carefully because CI jobs can execute arbitrary commands.

---

# 22. Runner Security

Runners represent a privileged engineering capability.

Controls should include:

* Restricted registration
* Protected runners where appropriate
* Controlled Docker privileges
* Secret protection
* Minimal host access
* Patch management

Untrusted workloads should not automatically receive privileged runner access.

---

# 23. CI Secrets

Secrets required by pipelines must not be committed into Git.

Potential sources include:

* GitLab CI/CD variables
* Kubernetes secret systems
* Future external secret manager

Sensitive values should be masked and protected where supported.

---

# 24. Protected Variables

Production credentials should be restricted to appropriate protected branches/tags and pipeline contexts.

This helps prevent feature branches from accessing sensitive credentials.

---

# 25. Security Scanning

CI should progressively implement:

* Secret scanning
* Dependency scanning
* Container scanning
* Static analysis
* Infrastructure/configuration validation

Security should move earlier into the development lifecycle.

---

# 26. Shift-Left Security

Target flow:

```text
Developer Change
      │
      ▼
CI Security Checks
      │
      ├── PASS
      │
      └── FAIL
```

Preventing insecure configuration before deployment is preferable to discovering it afterward.

---

# 27. Governance as Code

GitLab CI is one of the primary enforcement layers for Governance as Code.

It can validate:

* Policies
* Risks
* Controls
* Compliance definitions
* Technology catalog
* ADR metadata
* Documentation
* SLO definitions
* Technical debt records

Conceptually:

```text
Governance Definition
        │
        ▼
Git
        │
        ▼
GitLab CI
        │
        ├── Schema Validation
        ├── Reference Validation
        ├── Policy Validation
        └── Compliance Validation
```

---

# 28. Policy as Code

CI should eventually evaluate Kubernetes manifests against approved policies before merge.

Example:

```text
Manifest
   │
   ▼
CI Policy Engine
   │
   ├── Privileged?
   ├── Resources?
   ├── Labels?
   ├── Approved Registry?
   └── Security Context?
```

This complements runtime admission enforcement.

---

# 29. Documentation as Code

GitLab CI should progressively validate documentation.

Checks may include:

* Markdown lint
* Broken links
* Metadata schema
* File naming
* ADR IDs
* Risk references
* Secret leakage

This keeps the architecture repository governable.

---

# 30. Risk as Code

Future risk records may be validated by CI.

Example:

```yaml
id: RISK-AI-002
likelihood: 4
impact: 4
owner: ai-platform
```

CI can validate structure and automatically calculate classification.

---

# 31. Compliance as Code

Compliance artifacts may be validated for:

* Requirement IDs
* Control mappings
* Owners
* Evidence definitions
* Exception expiry

GitLab CI becomes part of the continuous compliance chain.

---

# 32. Technology Governance

CI can validate machine-readable technology definitions such as:

```yaml
technology: kubernetes
status: adopt
owner: platform
```

It may also detect:

* Missing owners
* Invalid lifecycle state
* Expired review date

---

# 33. SLO as Code

Future SLO definitions may be checked in GitLab CI before producing Prometheus/Grafana configuration.

Example:

```text
SLO YAML
   │
   ▼
Schema Validation
   │
   ▼
Generate / Validate Rules
```

This reduces inconsistent manually created SLOs.

---

# 34. Data CI

Data repositories should validate:

* SQL/dbt syntax
* dbt tests
* Data contracts where introduced
* Documentation
* Governance metadata

Data pipelines should be treated as production software.

---

# 35. Airflow DAG CI

DAG repositories should progressively validate:

* Python syntax
* DAG imports
* Unit tests
* Naming
* Owners
* Forbidden patterns

A broken DAG should be caught before reaching Airflow.

---

# 36. AI / MLOps CI

ML/AI repositories may validate:

* Unit tests
* Evaluation scripts
* Model metadata
* Prompt definitions
* Security policies
* Container images

The exact governance gates should depend on AI risk.

---

# 37. Prompt CI

Future governed prompts may be tested for:

* Required metadata
* Schema compatibility
* Evaluation cases
* Security rules

This supports Prompt Governance as Code.

---

# 38. Build vs Runtime Configuration

Application code and deployment configuration should remain distinguishable.

Example:

```text
Application Repository
→ Builds image

GitOps Repository
→ Selects image version and deployment config
```

This provides clearer auditability.

---

# 39. GitOps Update Pattern

A validated application build may update a GitOps repository through a controlled process.

Possible flow:

```text
Build Image
   │
   ▼
Publish Image
   │
   ▼
Update GitOps Version
   │
   ▼
Merge
   │
   ▼
Argo CD
```

The exact automation level may evolve.

---

# 40. Automatic Production Deployment

Fully automatic promotion to production should only be enabled where risk is understood.

A successful build alone does not always mean:

```text
Deploy immediately to production
```

Release governance should depend on service criticality.

---

# 41. Rollback

Code rollback generally follows:

```text
Git Revert
   │
   ▼
New CI
   │
   ▼
Artifact / GitOps Change
   │
   ▼
Argo CD Reconcile
```

Stateful database changes require separate migration rollback procedures.

---

# 42. Pipeline Failure

A failed CI pipeline should block merge where the failed control is mandatory.

Examples:

* Unit tests
* Policy validation
* Security gate
* Governance schema validation

Optional informational checks should be clearly identified.

---

# 43. Failing Governance Checks

Governance rules should not be routinely bypassed simply to deliver faster.

If a rule cannot be satisfied:

```text
Governance Failure
      │
      ▼
Fix
or
Documented Exception
```

This makes exceptions explicit.

---

# 44. Exception Workflow

A future machine-readable exception may allow CI to recognize approved temporary deviations.

Example:

```yaml
exception: EXC-K8S-004
policy: require-network-policy
expires: 2026-12-01
```

Expired exceptions should fail governance checks.

---

# 45. Artifact Retention

CI artifacts should have explicit retention.

Not every temporary build artifact needs indefinite storage.

Important release artifacts should remain reconstructable.

---

# 46. GitLab Backup

GitLab is a critical engineering system.

Important assets include:

* Repositories
* Database
* Configuration
* CI variables
* Project metadata

Backup and restore procedures are mandatory.

---

# 47. Git Repository Recovery

Repositories should be protected independently where justified because they contain:

* Source code
* Infrastructure configuration
* Governance state
* Architecture documentation

Losing Git could significantly increase platform recovery difficulty.

---

# 48. Disaster Recovery Importance

GitLab should be restored early enough to regain:

* Source code
* GitOps repositories
* Governance definitions
* Engineering workflows

However existing Kubernetes workloads can continue temporarily if GitLab is unavailable.

---

# 49. GitLab Availability

GitLab outage impacts:

* Development
* Merge Requests
* CI
* GitOps source availability
* New deployments

It does not necessarily immediately stop running applications.

This distinction affects availability classification.

---

# 50. Observability

GitLab should be monitored for:

* Availability
* CPU
* Memory
* Storage
* Repository storage
* Runner availability
* Job failures
* Pipeline queue time

A healthy GitLab UI does not guarantee healthy CI execution.

---

# 51. Runner Observability

Important indicators include:

* Runner online/offline
* Job queue
* Job duration
* Failed jobs
* Resource saturation

Runner saturation may delay all engineering workflows.

---

# 52. Storage Governance

GitLab can consume significant storage through:

* Git repositories
* Container images
* CI artifacts
* Job logs
* Packages

Retention policies are required.

---

# 53. Resource Constraints

GitLab is relatively resource-intensive.

Because physical infrastructure is fixed, the platform should:

* Monitor GitLab resources
* Control artifact retention
* Avoid unnecessary duplicated CI tools
* Scale only when metrics justify it

---

# 54. Local Sovereignty

Self-hosted GitLab supports the broader platform principle of local control.

Engineering assets remain inside the managed environment by default.

This includes:

* Source code
* Infrastructure
* Governance
* Documentation

---

# 55. Auditability

GitLab provides important evidence through:

* Commit history
* Merge Requests
* Pipeline history
* Review comments
* Approval records

These become part of the Governance as Code evidence model.

---

# 56. Change Management Integration

A significant platform change can be traced as:

```text
Change Request / Requirement
        │
        ▼
Git Branch
        │
        ▼
Merge Request
        │
        ▼
CI Evidence
        │
        ▼
Approval
        │
        ▼
Merge
        │
        ▼
Argo CD Deployment
```

This provides strong end-to-end change traceability.

---

# 57. ADR Integration

Architecture changes requiring ADRs should ideally update:

* ADR
* Architecture documentation
* Implementation

within the same or linked change process.

This reduces architecture drift.

---

# 58. Technical Debt Integration

CI findings may identify debt such as:

* Deprecated dependency
* Missing test
* Deprecated Kubernetes API
* Security issue
* Documentation gap

Not every finding should automatically become a debt record, but repeated or significant issues should.

---

# 59. Technology Governance Status

Recommended classifications:

```text
Technology: GitLab CE
Category: DevOps / SCM / CI
Lifecycle: ADOPT

Technology: GitLab Runner
Category: DevOps / CI Execution
Lifecycle: ADOPT
```

---

# 60. When GitLab CI Should NOT Be Used

GitLab CI should not replace:

* Argo CD continuous reconciliation
* Airflow business/data workflow orchestration
* Application runtime
* Kubernetes scheduling
* OpenMetadata governance catalog

The CI system remains an engineering validation and build platform.

---

# 61. Risks

## Risk — GitLab Failure

Mitigation:

* Backup
* Monitoring
* Recovery procedures

## Risk — Compromised CI Runner

Mitigation:

* Runner isolation
* Least privilege
* Controlled secrets

## Risk — Secret Leakage in CI

Mitigation:

* Protected variables
* Secret scanning
* Log hygiene

## Risk — CI Bypass

Mitigation:

* Protected branches
* Merge requirements

## Risk — Artifact Storage Growth

Mitigation:

* Retention
* Capacity monitoring

---

# 62. Positive Consequences

The platform gains:

* Centralized Git
* Standard CI
* Review workflow
* Auditability
* Security gates
* Governance gates
* Artifact traceability
* Strong GitOps integration
* Local engineering sovereignty

---

# 63. Negative Consequences

The platform accepts:

* GitLab operational responsibility
* Resource usage
* Backup requirements
* Runner security requirements
* CI pipeline maintenance

These costs are justified by the engineering and governance capabilities gained.

---

# 64. Success Criteria

The decision remains successful while:

* Source and configuration remain version controlled
* Production-relevant changes use review workflows
* CI catches defects before merge
* Builds remain reproducible
* GitOps remains separated from CI
* Governance validation can be integrated
* GitLab remains recoverable

---

# 65. Review Triggers

Review this ADR if:

* GitLab becomes operationally unsustainable
* Security requirements materially change
* CI scale exceeds current architecture
* A replacement provides significant measurable benefit
* Repository or runner architecture changes fundamentally

---

# 66. Governance as Code Metadata

Future machine-readable representation:

```yaml
id: ADR-0012
title: Adopt GitLab as Primary Source Control and CI Platform
status: accepted

domain:
  - devops
  - platform
  - governance
  - security

technologies:
  - gitlab
  - gitlab-runner

owner: platform-devops
implementation_status: implemented

related_adrs:
  - ADR-0001
  - ADR-0002
  - ADR-0010
  - ADR-0011

principles:
  - git-source-of-truth
  - ci-cd-separation
  - governance-as-code
  - protected-production-change

alternatives:
  - github
  - gitea
  - jenkins

supersedes: null
superseded_by: null
```

---

# 67. Related Documents

* ADR-0001-Kubernetes
* ADR-0002-ArgoCD-GitOps
* CI/CD Architecture
* GitOps Architecture
* Platform Engineering
* Security Architecture
* Change Management
* Governance Architecture
* Compliance Governance
* Documentation Governance
* Disaster Recovery
