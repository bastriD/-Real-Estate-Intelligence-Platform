# ADR-0014 — Adopt Governance as Code as a Core Enterprise Architecture Principle

**Status:** Accepted
**Date:** 2026-08-21
**Decision Owner:** Bastri Murad
**Domain:** Governance / Architecture / DevOps / Security / Data / AI
**Project:** Enterprise AI Platform
**Related ADRs:** ADR-0002, ADR-0008, ADR-0010, ADR-0012, ADR-0013
**Related Technologies:** GitLab, Argo CD, Kubernetes, OpenMetadata, Prometheus, Grafana, CI/CD, Policy Engines
**Supersedes:** None
**Superseded By:** None

---

# 1. Context

The Enterprise AI Platform already uses a strongly declarative and automated architecture.

Important platform capabilities are already managed through:

* Git
* GitLab
* CI/CD
* Argo CD
* Kubernetes
* OpenMetadata
* Prometheus
* Grafana
* Airflow
* MLflow
* Structured architecture documentation

However, governance itself can easily become fragmented across:

* Markdown documents
* Spreadsheets
* Meeting decisions
* Manual reviews
* UI-only configuration
* Informal approvals
* Human memory

This creates a gap between:

```text
Governance Documentation
```

and:

```text
Actual Runtime Enforcement
```

The architecture therefore requires a formal decision on how governance should operate.

---

# 2. Problem

Traditional governance models often follow:

```text
Policy
  │
  ▼
Document
  │
  ▼
Human Review
  │
  ▼
Manual Approval
```

This approach creates several risks:

* Policy drift
* Inconsistent enforcement
* Slow reviews
* Missing evidence
* Forgotten exceptions
* Undocumented risk acceptance
* Manual compliance checks
* Configuration drift
* Governance becoming disconnected from engineering

The platform requires a governance model that operates at engineering speed.

---

# 3. Decision

The Enterprise AI Platform will adopt **Governance as Code** as a core architecture principle.

Governance requirements should progressively become:

* Version controlled
* Structured
* Machine readable
* Testable
* Traceable
* Reviewable
* Automatically validated
* Automatically enforced where appropriate
* Continuously evidenced

The target model is:

```text
Governance Requirement
        │
        ▼
Machine-Readable Definition
        │
        ▼
Git
        │
        ▼
CI Validation
        │
        ▼
Approval
        │
        ▼
GitOps / Policy Enforcement
        │
        ▼
Runtime Evidence
        │
        ▼
Continuous Governance
```

---

# 4. Governance as Code Is an Architecture Standard

Governance as Code is not treated as:

```text
Optional future automation
```

It is adopted as:

```text
Enterprise Architecture Standard
```

Manual governance may still exist where human judgment is necessary.

However, repeatable technical controls should progressively become automated.

---

# 5. Scope

Governance as Code applies to:

* Architecture governance
* Security governance
* Data governance
* AI governance
* Risk management
* Compliance
* Technology governance
* Documentation governance
* Technical debt
* SLI/SLO governance
* Kubernetes policies
* Operational controls
* Exceptions
* Evidence generation

---

# 6. Governance Domains as Code

The target governance architecture includes:

```text
Governance as Code
│
├── Policy as Code
├── Risk as Code
├── Compliance as Code
├── Architecture Fitness Functions
├── Decision Metadata as Code
├── Data Governance as Code
├── Data Quality as Code
├── AI Governance as Code
├── SLO as Code
├── Technology Radar as Code
├── Documentation as Code
├── Technical Debt as Code
├── Exception as Code
└── Roadmap as Code
```

---

# 7. Git as the Governance System of Record

Git is selected as the authoritative version-control layer for governance artifacts.

Governance assets may include:

```text
governance/
├── requirements/
├── controls/
├── risks/
├── technologies/
├── debt/
├── exceptions/
├── policies/
├── slo/
├── ai/
└── schemas/
```

Git provides:

* History
* Attribution
* Review
* Branching
* Rollback
* Auditability

---

# 8. Structured Governance

Governance definitions should progressively move from only Markdown into structured data where automation provides value.

Preferred machine-readable formats include:

```text
YAML
JSON
Markdown Front Matter
```

Example:

```yaml
id: RISK-AI-002
title: GPU capacity exhaustion
owner: ai-platform
status: monitoring
likelihood: 4
impact: 4
```

---

# 9. Schema Validation

Machine-readable governance artifacts should be validated through formal schemas.

Schema validation may enforce:

* Required fields
* Valid IDs
* Valid statuses
* Ownership
* Review dates
* References
* Enumerated values

This prevents structurally invalid governance records from becoming authoritative.

---

# 10. GitLab CI as Governance Gate

GitLab CI is selected as a primary validation point.

Target:

```text
Governance Change
      │
      ▼
GitLab CI
      │
      ├── Schema Validation
      ├── Reference Validation
      ├── Ownership Validation
      ├── Policy Validation
      ├── Security Validation
      └── Documentation Validation
      │
      ▼
Merge Allowed / Blocked
```

---

# 11. Shift-Left Governance

Governance violations should preferably be detected before deployment.

Example:

```text
Developer submits workload
        │
        ▼
CI detects privileged container
        │
        ▼
Merge blocked
```

This is preferable to discovering the violation later in production.

---

# 12. Runtime Governance

Some controls must also operate at runtime.

Target architecture:

```text
Git / CI
   │
   ▼
Pre-Deployment Validation
   │
   ▼
Kubernetes
   │
   ▼
Admission Policy
   │
   ▼
Runtime Enforcement
```

This provides defense in depth.

---

# 13. Policy as Code

Policy as Code covers repeatable technical controls.

Potential policies include:

* Disallow privileged containers
* Require non-root execution
* Require resource limits
* Require ownership labels
* Restrict hostPath
* Restrict host networking
* Require approved registries
* Require TLS
* Require NetworkPolicies where applicable

---

# 14. Policy Engine

A Kubernetes policy engine should be introduced when implementation reaches the relevant roadmap phase.

Candidates include:

* Kyverno
* OPA Gatekeeper

Only one should normally be selected.

The final selection requires its own architecture evaluation or ADR if materially significant.

---

# 15. GitOps as Governance Enforcement

Argo CD provides ongoing desired-state governance.

Architecture:

```text
Approved Git State
       │
       ▼
Argo CD
       │
       ▼
Runtime State
       │
       ▼
Drift Detected
       │
       ▼
Reconciliation
```

This turns configuration drift management into a governance control.

---

# 16. Architecture Governance as Code

Architecture standards should progressively become measurable.

Examples:

```text
All production workloads have:
- owner
- resources
- observability
- security context
```

These become architecture fitness functions.

---

# 17. Architecture Fitness Functions

A fitness function continuously evaluates an architectural property.

Example:

```text
All production deployments must define resource limits.
```

Possible enforcement:

```text
CI
+
Kubernetes Admission Policy
```

---

# 18. Decision Metadata as Code

ADRs should progressively include structured metadata.

Example:

```yaml
id: ADR-0014
status: accepted
domain: governance
owner: platform
```

This supports:

* ADR indexing
* Decision reporting
* Supersession tracking
* Technology mapping
* Risk mapping

---

# 19. Risk as Code

Risk records should become machine-readable.

Example:

```yaml
id: RISK-INFRA-002
title: Storage exhaustion
owner: platform

inherent:
  likelihood: 4
  impact: 4

status: monitoring
```

Automation can calculate:

```text
Risk Score
Risk Level
Review Status
```

---

# 20. Dynamic Risk Evidence

Risk governance should progressively consume operational evidence.

Example:

```text
RISK-INFRA-STORAGE
        │
        ▼
Prometheus
        │
        ▼
Filesystem Usage
        │
        ▼
Key Risk Indicator
```

This enables continuous risk monitoring.

---

# 21. Compliance as Code

Compliance requirements should be represented through:

```text
Requirement
      │
      ▼
Control
      │
      ▼
Implementation
      │
      ▼
Evidence
```

Example:

```yaml
requirement: REQ-SEC-001
control: CTRL-SEC-001
implementation: kyverno
```

---

# 22. Continuous Compliance

Target model:

```text
Control
   │
   ▼
Runtime Evidence
   │
   ▼
Automated Evaluation
   │
   ▼
Compliance Status
```

Compliance becomes continuous rather than purely periodic.

---

# 23. Data Governance as Code

OpenMetadata is selected as a runtime governance target.

Governance definitions may include:

* Owners
* Domains
* Tags
* Classifications
* Glossary terms
* Data Quality tests
* Criticality

Target:

```text
Git
 ↓
Governance Job
 ↓
OpenMetadata API
 ↓
Governed Metadata
```

---

# 24. Data Quality as Code

Critical Data Quality rules should remain version controlled.

Examples include:

* Not null
* Unique
* Referential integrity
* Freshness
* Accepted values
* Row-count expectations

Test results become governance evidence.

---

# 25. AI Governance as Code

AI assets should progressively define machine-readable governance metadata.

Examples:

```text
Model
Prompt
Embedding Model
RAG Application
Agent
AI Tool
```

Required metadata may include:

```text
Owner
Risk Level
Model Version
Evaluation Status
Data Classification
Human Oversight
Approval State
```

---

# 26. AI Promotion Gates

Future model deployment may follow:

```text
Candidate
   │
   ▼
Evaluation
   │
   ▼
Risk Validation
   │
   ▼
Security Validation
   │
   ▼
Governance Approval
   │
   ▼
Promotion
```

Mandatory checks should be automated where practical.

---

# 27. Prompt Governance as Code

Prompts should eventually have stable identity.

Example:

```yaml
id: PROMPT-REAL-ESTATE-001
version: "3.1"
owner: ai-platform
model: qwen3
risk_level: medium
evaluation_required: true
```

This supports regression testing and traceability.

---

# 28. SLO as Code

Service Level Objectives should progressively be machine readable.

Example:

```yaml
service: business-api
owner: platform
sli: availability
objective: 99.9
window: 30d
```

These definitions may generate or validate:

* Prometheus rules
* Burn-rate alerts
* Grafana dashboards

---

# 29. Technology Radar as Code

The Technology Catalog should become structured.

Example:

```yaml
id: TECH-OBS-001
name: Prometheus
status: adopt
owner: platform
```

Generated outputs may include:

* Technology Catalog
* Technology Radar
* EOL reports

---

# 30. Documentation as Code

Architecture documentation remains stored in Git using Markdown.

Automation should progressively validate:

* Metadata
* Links
* Naming
* IDs
* References
* Secrets
* Stale documents

Documentation becomes part of the engineering lifecycle.

---

# 31. Technical Debt as Code

Technical Debt should be explicitly recorded.

Example:

```yaml
id: DEBT-K8S-001
title: Missing NetworkPolicies
severity: high
owner: platform
status: planned
```

This allows automated reporting and expiry/review checks.

---

# 32. Exception as Code

Governance exceptions should be structured.

Example:

```yaml
id: EXC-SEC-003
policy: require-network-policy
owner: platform
reason: legacy-workload
expires: 2026-12-31
```

Expired exceptions should trigger governance failure.

---

# 33. Temporary Exceptions

Exceptions must not become permanent undocumented bypasses.

Target flow:

```text
Exception
   │
   ▼
Expiration Date
   │
   ▼
Automatic Validation
   │
   ├── Active
   └── Expired → Fail / Review
```

---

# 34. Roadmap as Code

Architecture roadmap items may also become structured.

Example:

```yaml
id: ROADMAP-GOV-001
title: Implement Policy as Code
priority: P2
owner: platform
status: planned
```

This supports dependency and maturity reporting.

---

# 35. Governance IDs

Stable identifiers should be used.

Examples:

```text
ADR-0001
RISK-AI-002
CTRL-SEC-004
REQ-GDPR-001
TECH-DATA-003
DEBT-K8S-001
EXC-SEC-002
```

Stable IDs enable cross-reference automation.

---

# 36. Cross-Domain Traceability

Target relationship:

```text
Requirement
   │
   ▼
Control
   │
   ▼
Policy
   │
   ▼
Risk
   │
   ▼
ADR
   │
   ▼
Technology
   │
   ▼
Implementation
   │
   ▼
Evidence
```

This is a key Governance as Code objective.

---

# 37. Governance Graph

Future reporting may create a governance graph.

Example:

```text
REQ-SEC-001
    │
    ▼
CTRL-SEC-004
    │
    ▼
POL-K8S-003
    │
    ▼
Kubernetes
    │
    ▼
Compliance Evidence
```

This improves auditability and impact analysis.

---

# 38. Evidence as Code

Controls should identify evidence sources.

Example:

```yaml
control: CTRL-OPS-004

evidence:
  source: prometheus
  metric: backup_success
```

Other evidence may come from:

* Git
* Argo CD
* OpenMetadata
* MLflow
* Kubernetes policy reports
* CI pipelines
* Restore tests

---

# 39. Automated Evidence

The architecture prefers automatically generated evidence over manual declarations where possible.

Example:

```text
Claim:
Backups are working

Weak evidence:
Person confirms backup exists

Strong evidence:
Backup metrics + restore-test result
```

---

# 40. Governance Dashboard

A future governance dashboard should expose:

```text
Risks
Policies
Controls
Compliance
Exceptions
Technology Lifecycle
Technical Debt
SLO Coverage
Documentation Status
Backup Evidence
AI Governance
```

The dashboard is a visualization layer.

It is not the source of truth.

---

# 41. Human Governance Remains Necessary

Governance as Code does not eliminate human decision-making.

Human judgment remains required for:

* Business impact
* Risk acceptance
* Architecture trade-offs
* Ethical AI decisions
* Legal interpretation
* High-impact exceptions
* Strategic decisions

Automation handles deterministic checks.

Humans retain responsibility for judgment.

---

# 42. Automation Boundary

Good automation candidate:

```text
Does every production workload define resource limits?
```

Poor automation candidate:

```text
Is this architectural trade-off strategically correct?
```

The distinction must remain explicit.

---

# 43. Governance Should Enable Delivery

The governance architecture deliberately rejects excessive bureaucracy.

Preferred:

```text
Standard Path
→ Automatically validated
→ Automatically approved when safe
```

rather than:

```text
Every change
→ Manual committee
→ Long delay
```

Automation allows strong governance with lower friction.

---

# 44. Golden Paths

Governance requirements should increasingly be embedded into reusable platform templates.

Example:

```text
New Application Template
      │
      ├── Security Context
      ├── Resource Limits
      ├── Metrics
      ├── Logs
      ├── Ownership
      ├── CI
      └── GitOps
```

The correct path becomes the easiest path.

---

# 45. Governance and Platform Engineering

Platform Engineering should provide reusable capabilities that automatically satisfy governance requirements.

Examples:

* Service templates
* CI templates
* Kubernetes manifests
* Observability templates
* Security defaults

This reduces repeated manual compliance work.

---

# 46. Current Implementation

Governance as Code is already partially implemented.

Current evidence includes:

* Git-managed architecture
* GitOps
* Argo CD reconciliation
* OpenMetadata governance jobs
* Data Quality automation
* Prometheus rules
* GitLab CI
* Structured governance documentation
* ADR framework

Current state:

```text
PARTIALLY IMPLEMENTED
```

The ADR formally establishes the complete target model.

---

# 47. Current Maturity

Current approximate maturity:

```text
Level 2–3
```

because governance is:

* Strongly documented
* Version controlled
* Partially automated

Target:

```text
Level 4 — Automated
```

through machine-readable governance and enforcement.

---

# 48. Implementation Phases

Recommended sequence:

```text
1. Governance definitions
2. Stable IDs
3. YAML schemas
4. CI validation
5. Generated indexes
6. Policy as Code
7. Runtime enforcement
8. Continuous evidence
9. Governance dashboards
10. Continuous governance
```

---

# 49. Governance Repository

Target:

```text
governance/
├── schemas/
├── requirements/
├── controls/
├── risks/
├── policies/
├── technologies/
├── debt/
├── exceptions/
├── slo/
├── ai/
└── reports/
```

Generated reports should not become the authoritative source if structured definitions already exist.

---

# 50. Resource Consequences

Governance automation should remain lightweight.

The platform should avoid deploying large governance products when existing tools can provide the required controls.

Preferred order:

```text
Git / CI
    ↓
Existing APIs
    ↓
Kubernetes Policy
    ↓
Observability
```

before adding more infrastructure.

---

# 51. Security Consequences

Governance repositories contain sensitive architecture and policy information.

Controls include:

* Protected repositories
* RBAC
* Merge Request review
* Secret scanning
* Protected branches

Governance automation credentials should follow least privilege.

---

# 52. Availability Consequences

Governance validation failure may temporarily block changes.

This is intentional when mandatory controls fail.

However already-running business workloads should not depend synchronously on governance CI systems.

Governance is primarily a control-plane capability.

---

# 53. Failure Mode

If governance automation becomes unavailable:

```text
Runtime
→ continues where safe

New Changes
→ may be blocked or require controlled exception
```

The platform should fail safely rather than silently bypass mandatory controls.

---

# 54. Auditability

Governance as Code provides evidence through:

* Git history
* Merge Requests
* CI results
* Argo CD history
* Policy reports
* OpenMetadata
* Prometheus
* MLflow
* Restore reports

This creates an auditable control chain.

---

# 55. Risk Reduction

Governance as Code reduces risks associated with:

* Manual drift
* Policy inconsistency
* Missing ownership
* Forgotten exceptions
* Undocumented decisions
* Unvalidated configuration
* Weak audit evidence

It does not eliminate all governance risk.

---

# 56. Technical Debt Consequences

Governance gaps can themselves become technical debt.

Examples:

* Policy still only documented
* Manual risk register
* UI-only Data Governance
* Missing governance schemas

These should be tracked until automation reaches the target state.

---

# 57. Compliance Consequences

Governance as Code provides the technical foundation for Continuous Compliance.

However:

> Automation does not determine legal interpretation.

Legal and regulatory applicability still requires appropriate human/legal review.

---

# 58. AI Governance Consequences

The architecture enables AI controls to be integrated with the same governance framework used for infrastructure and data.

This avoids creating an isolated AI governance model.

AI remains a specialized governance domain inside the enterprise governance architecture.

---

# 59. Positive Consequences

The platform gains:

* Stronger consistency
* Better traceability
* Faster governance
* Automated validation
* Reduced drift
* Better compliance evidence
* Better risk visibility
* Expiring exceptions
* Better architecture conformity
* Strong foundation for continuous governance

---

# 60. Negative Consequences

The platform accepts:

* Governance schema maintenance
* CI complexity
* Policy maintenance
* Potential false-positive governance failures
* Need for careful exception handling
* Additional engineering effort

These costs are accepted because governance becomes repeatable and scalable.

---

# 61. Alternatives Considered

## Option 1 — Governance as Code

Advantages:

* Automated
* Version controlled
* Repeatable
* Auditable
* Integrated with engineering
* Supports continuous governance

Selected.

---

## Option 2 — Documentation-Only Governance

Advantages:

* Simple
* Low technical implementation effort

Disadvantages:

* Weak enforcement
* Drift
* Manual auditing
* Poor scalability

Not selected as the target state.

---

## Option 3 — Dedicated Enterprise Governance Suite

Advantages:

* Broad packaged capabilities
* Vendor support

Disadvantages:

* Cost
* Complexity
* Resource footprint
* Potential overlap with existing stack
* Vendor lock-in

Not selected for current platform requirements.

---

# 62. Decision Criteria

The decision considered:

| Criterion               | Importance |
| ----------------------- | ---------: |
| Automation              |   Critical |
| Auditability            |   Critical |
| Git integration         |   Critical |
| CI/CD integration       |   Critical |
| Policy enforcement      |       High |
| Resource efficiency     |       High |
| Open architecture       |       High |
| Local control           |       High |
| Cross-domain governance |   Critical |
| Scalability of process  |       High |

Governance as Code provides the strongest fit.

---

# 63. Success Criteria

The decision is successful when:

* Critical governance artifacts are version controlled
* Important governance definitions are machine-readable
* CI validates governance changes
* Repeatable policies are automatically enforced
* Exceptions expire automatically
* Runtime evidence supports controls
* Governance status is measurable
* Manual review is focused on judgment rather than repetitive checks

---

# 64. Review Triggers

Review this ADR if:

* Governance automation creates excessive delivery friction
* Platform architecture changes fundamentally
* Regulatory requirements demand different controls
* Existing tools cannot support required governance
* A dedicated governance technology provides clear measurable benefit

---

# 65. Governance as Code Metadata

Machine-readable representation:

```yaml
id: ADR-0014
title: Adopt Governance as Code as a Core Enterprise Architecture Principle
status: accepted

domain:
  - governance
  - architecture
  - devops
  - security
  - data
  - ai

owner: architecture-governance

implementation_status: partial

principles:
  - governance-as-code
  - policy-as-code
  - continuous-compliance
  - evidence-over-declaration
  - git-source-of-truth
  - automation-before-manual-repetition

capabilities:
  - risk-as-code
  - compliance-as-code
  - technology-radar-as-code
  - documentation-as-code
  - technical-debt-as-code
  - slo-as-code
  - ai-governance-as-code
  - data-governance-as-code

related_adrs:
  - ADR-0002
  - ADR-0008
  - ADR-0010
  - ADR-0012
  - ADR-0013

supersedes: null
superseded_by: null
```

---

# 66. Related Documents

* Governance Architecture
* Architecture Governance
* Decision Governance
* Risk Management
* Compliance Governance
* Technology Governance
* Documentation Governance
* Technical Debt Management
* Architecture Maturity Model
* Architecture Roadmap
* GitOps Architecture
* Data Governance
* AI Governance
* Observability Governance
* `98-ADR/`
