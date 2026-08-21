# Risk Management

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the Risk Management framework of the Enterprise AI Platform.

It establishes how business, architectural, technical, security, data, AI, operational, compliance, and infrastructure risks are:

* Identified
* Classified
* Assessed
* Prioritized
* Assigned
* Treated
* Monitored
* Reviewed
* Accepted or closed

Risk Management is integrated with the broader **Governance as Code** strategy.

Where practical, risk definitions, controls, thresholds, evidence, and compliance status should progressively become machine-readable and automatically evaluated.

---

# 2. Scope

Risk Management applies to:

* Business Architecture
* Applications
* Infrastructure
* Kubernetes
* Networking
* Data
* Databases
* Artificial Intelligence
* MLOps
* Security
* DevOps
* CI/CD
* GitOps
* Observability
* Operations
* Backup
* Disaster Recovery
* Compliance
* Privacy
* Third-party technologies

---

# 3. Objectives

Risk Management aims to:

* Identify threats before they become incidents
* Quantify risk consistently
* Prioritize remediation
* Assign clear ownership
* Track mitigation
* Document accepted risks
* Identify residual risk
* Connect risks with architecture decisions
* Connect risks with controls
* Generate governance evidence
* Support continuous risk monitoring
* Progressively implement Risk as Code

---

# 4. Risk Management Principles

The platform follows these principles:

* Risk Must Be Explicit
* Risk Has an Owner
* Risk Is Evaluated Consistently
* Critical Risks Require Treatment
* Residual Risk Must Be Visible
* Risk Acceptance Must Be Explicit
* Controls Must Be Traceable
* Evidence Over Assumption
* Risks Must Be Reviewed
* Architecture Decisions Must Consider Risk
* Automation Should Detect Risk Where Practical
* Risk Management Is Continuous

---

# 5. Risk Management Lifecycle

```text
Identify
   │
   ▼
Classify
   │
   ▼
Assess
   │
   ▼
Prioritize
   │
   ▼
Treat
   │
   ▼
Monitor
   │
   ▼
Review
   │
   ├── Accept
   ├── Continue Treatment
   ├── Escalate
   └── Close
```

Risk Management is not a one-time project activity.

---

# 6. Risk Definition

A risk represents an uncertain event or condition that may negatively affect platform objectives.

Conceptually:

```text
Threat
   +
Vulnerability / Exposure
   │
   ▼
Risk Event
   │
   ▼
Impact
```

Example:

```text
Single GPU host
+
Hardware failure
        │
        ▼
AI inference unavailable
```

---

# 7. Risk Categories

The platform uses several risk domains.

```text
Business Risk
Architecture Risk
Infrastructure Risk
Application Risk
Data Risk
AI Risk
Security Risk
Operational Risk
Compliance Risk
Third-Party Risk
```

This classification supports ownership and reporting.

---

# 8. Business Risk

Examples include:

* Critical business function unavailable
* Incorrect analytical results
* Inability to deliver required service
* Excessive dependency on technical specialists
* Business requirements not represented in architecture

Business risk should influence technical prioritization.

---

# 9. Architecture Risk

Examples include:

* Excessive complexity
* Architecture drift
* Unsupported technology
* Undocumented dependencies
* Single points of failure
* Technology duplication
* Vendor lock-in
* Poor interoperability

Architecture Governance should identify these risks during design review.

---

# 10. Infrastructure Risk

Examples include:

* Physical host failure
* Disk failure
* Network failure
* Power failure
* Resource exhaustion
* Storage exhaustion
* Insufficient redundancy

The platform's fixed physical infrastructure makes explicit capacity and availability risk management particularly important.

---

# 11. Kubernetes Risk

Examples include:

* Control-plane failure
* Node failure
* CNI failure
* DNS failure
* Storage failure
* Misconfigured RBAC
* Privileged workload
* Resource starvation
* Configuration drift

Many Kubernetes risks can eventually be continuously evaluated through Policy as Code.

---

# 12. Application Risk

Examples include:

* API failure
* Dependency failure
* Poor error handling
* Missing authentication
* Uncontrolled configuration
* Missing health checks
* Missing observability

Application risk should be addressed through engineering standards and automated controls.

---

# 13. Data Risk

Examples include:

* Data corruption
* Data loss
* Poor data quality
* Missing lineage
* Incorrect classification
* Unauthorized access
* Excessive retention
* Stale analytics data

Data Governance and OpenMetadata provide controls for several of these risks.

---

# 14. AI Risk

AI-specific risks include:

* Hallucination
* Incorrect model output
* Prompt injection
* Sensitive-data exposure
* Model degradation
* Inappropriate model use
* Bias
* Missing explainability
* Excessive automation without human oversight
* Model dependency failure

AI risk must remain distinct from conventional application availability risk.

---

# 15. Security Risk

Examples include:

* Credential exposure
* Unauthorized access
* Privilege escalation
* Vulnerable container image
* Exposed service
* Missing encryption
* Insecure dependency
* Secret leakage
* Supply-chain compromise

Security controls should increasingly provide automated risk evidence.

---

# 16. Operational Risk

Examples include:

* Missing runbooks
* Manual deployment
* Missing monitoring
* Inadequate backup
* Untested restore
* Poor incident response
* Knowledge concentration
* Alert fatigue

Operational maturity directly reduces operational risk.

---

# 17. Compliance Risk

Examples include:

* GDPR violation
* Excessive personal-data retention
* Missing processing record
* Missing access control
* Inadequate traceability
* AI regulatory non-conformity
* Missing evidence

Compliance Governance defines the associated controls.

---

# 18. Third-Party Risk

Third-party dependencies may include:

* Container images
* Open-source libraries
* SaaS providers
* External APIs
* AI providers
* Package repositories

Risks include:

* Vulnerability
* Service discontinuation
* Licensing
* Vendor lock-in
* Supply-chain compromise

---

# 19. Risk Identification

Risks may be identified through:

* Architecture review
* Security review
* Incident analysis
* Problem Management
* Monitoring
* Vulnerability scanning
* Data-quality monitoring
* AI evaluation
* Capacity review
* Change review
* Compliance review

Risk identification should be continuous.

---

# 20. Risk Statement

A useful risk statement should describe:

```text
Cause
  ↓
Risk Event
  ↓
Impact
```

Example:

> Because AI inference currently depends on limited local GPU capacity, simultaneous heavy inference workloads may exhaust VRAM, resulting in increased latency or service unavailability.

This is more actionable than:

```text
GPU risk
```

---

# 21. Risk Register

The platform should maintain a centralized Risk Register.

Each risk should contain:

```text
Risk ID
Title
Domain
Description
Cause
Impact
Likelihood
Impact Score
Risk Score
Owner
Treatment
Controls
Residual Risk
Status
Review Date
```

---

# 22. Risk Identifier

Recommended format:

```text
RISK-<DOMAIN>-<NUMBER>
```

Examples:

```text
RISK-INFRA-001
RISK-SEC-003
RISK-DATA-005
RISK-AI-002
RISK-OPS-004
```

Stable IDs improve traceability.

---

# 23. Likelihood Scale

Recommended five-level scale:

| Score | Likelihood     | Description           |
| ----: | -------------- | --------------------- |
|     1 | Rare           | Unlikely              |
|     2 | Unlikely       | Could occur           |
|     3 | Possible       | Realistic             |
|     4 | Likely         | Expected periodically |
|     5 | Almost Certain | Expected frequently   |

Scoring should be evidence-based where possible.

---

# 24. Impact Scale

Recommended scale:

| Score | Impact     | Description                                |
| ----: | ---------- | ------------------------------------------ |
|     1 | Negligible | Minimal effect                             |
|     2 | Minor      | Limited disruption                         |
|     3 | Moderate   | Meaningful service impact                  |
|     4 | Major      | Significant business impact                |
|     5 | Critical   | Severe business/security/compliance impact |

---

# 25. Risk Score

Initial risk score:

```text
Risk Score =
Likelihood × Impact
```

Range:

```text
1 → 25
```

Example:

```text
Likelihood = 4
Impact     = 5

Risk Score = 20
```

---

# 26. Risk Classification

Recommended classification:

| Score | Level    |
| ----: | -------- |
|   1–4 | Low      |
|   5–9 | Moderate |
| 10–16 | High     |
| 17–25 | Critical |

Thresholds may later be adjusted based on governance experience.

---

# 27. Risk Matrix

```text
                 IMPACT
             1   2   3   4   5

Likelihood 5  5  10  15  20  25
Likelihood 4  4   8  12  16  20
Likelihood 3  3   6   9  12  15
Likelihood 2  2   4   6   8  10
Likelihood 1  1   2   3   4   5
```

The matrix supports prioritization rather than replacing engineering judgment.

---

# 28. Inherent Risk

Inherent risk represents risk before controls are considered.

Example:

```text
Host failure
Likelihood = 3
Impact = 5

Inherent Risk = 15
```

Controls are then applied.

---

# 29. Controls

Controls reduce likelihood or impact.

Examples:

* Kubernetes HA
* Backup
* RBAC
* NetworkPolicy
* Monitoring
* GitOps
* Data quality tests
* Human AI review
* Vulnerability scanning

Controls should be traceable to risks.

---

# 30. Residual Risk

Residual risk is the remaining risk after controls.

Conceptually:

```text
Inherent Risk
     │
     ▼
Controls
     │
     ▼
Residual Risk
```

Residual risk must remain visible.

A control does not automatically eliminate the underlying risk.

---

# 31. Risk Treatment

Four primary strategies are supported.

## Avoid

Remove the activity causing the risk.

## Reduce

Introduce controls.

## Transfer

Transfer part of the risk through contractual or service arrangements where appropriate.

## Accept

Explicitly accept the remaining risk.

---

# 32. Risk Reduction

Example:

```text
Risk:
Loss of PostgreSQL data

Controls:
- Scheduled backup
- Backup validation
- Restore tests
- Persistent storage monitoring
```

The residual risk is then reassessed.

---

# 33. Risk Acceptance

Risk acceptance is a governance decision.

It should document:

* Risk
* Residual score
* Reason
* Owner
* Acceptance date
* Review date

Acceptance must never mean that the risk simply disappeared from documentation.

---

# 34. Risk Appetite

Risk appetite defines the amount of risk the platform is prepared to tolerate.

General principle:

```text
Low appetite:
Security breach
Personal-data loss
Irrecoverable data loss

Moderate appetite:
Temporary development-service outage

Higher appetite:
Experimental workload failure
```

Risk appetite should reflect business context.

---

# 35. Risk Tolerance

Risk tolerance provides practical boundaries.

Example:

```text
Experimental AI model unavailable
→ acceptable temporarily

Production database data loss
→ unacceptable
```

This helps prioritize engineering investment.

---

# 36. Critical Risks

Critical risks should normally require:

* Explicit owner
* Immediate treatment plan
* Controls
* Monitoring
* Review
* Escalation where necessary

Critical risk acceptance requires strong justification.

---

# 37. Risk Ownership

Every risk requires an owner.

Possible owners include:

* Platform
* Security
* Data
* AI
* Application
* Operations
* Business

The owner is accountable for ensuring the risk is reviewed and treated.

---

# 38. Control Ownership

Risk owner and control owner may differ.

Example:

```text
Risk:
Data loss

Risk Owner:
Data / Platform

Control:
Velero backup

Control Owner:
Platform Operations
```

This distinction becomes important as governance matures.

---

# 39. Risk Status

Recommended statuses:

```text
Identified
Under Assessment
Open
Treatment In Progress
Accepted
Monitoring
Closed
```

Closed risks should retain historical records.

---

# 40. Risk Review

Risk review should consider:

* Has likelihood changed?
* Has impact changed?
* Are controls working?
* Has architecture changed?
* Has an incident occurred?
* Has the risk materialized?
* Is the risk still relevant?
* Is residual risk acceptable?

---

# 41. Risk Review Triggers

Review may be triggered by:

* Architecture changes
* Major deployments
* Security incidents
* Data incidents
* AI incidents
* New vulnerabilities
* Infrastructure changes
* Regulatory changes
* Capacity changes

---

# 42. Key Risk Indicators

Key Risk Indicators provide measurable evidence that risk is increasing.

Examples:

```text
Disk utilization
Failed backups
Critical vulnerabilities
Authentication failures
SLO burn rate
GPU saturation
Data-quality failures
Open policy violations
```

KRIs connect Risk Management with observability.

---

# 43. Example KRI

Risk:

```text
RISK-INFRA-004
Storage exhaustion
```

KRI:

```text
Filesystem utilization > 80%
```

Escalation:

```text
Filesystem utilization > 90%
```

The exact thresholds should be operationally validated.

---

# 44. Risk and Observability

Observability provides evidence for dynamic risk assessment.

```text
Metrics / Logs / Alerts
          │
          ▼
Key Risk Indicators
          │
          ▼
Risk Status
```

This allows risk governance to evolve beyond static spreadsheets.

---

# 45. Risk and Incident Management

When a risk materializes:

```text
Known Risk
   │
   ▼
Risk Event
   │
   ▼
Incident
   │
   ▼
Recovery
   │
   ▼
Risk Reassessment
```

The associated risk record should be reviewed after the incident.

---

# 46. Risk and Problem Management

Repeated incidents may indicate:

* Incorrect risk score
* Weak controls
* Missing risk
* Ineffective treatment

Problem Management findings should update the Risk Register.

---

# 47. Risk and Change Management

High-risk changes should trigger stronger review.

Example:

```text
Change
  │
  ▼
Risk Evaluation
  │
  ├── Low → Standard process
  └── High → Additional review / validation
```

---

# 48. Risk and Architecture Decisions

ADRs should reference important risks.

Example:

```text
ADR-0009
Adopt local Ollama inference

Related:
RISK-AI-002
RISK-INFRA-007
```

Likewise, the Risk Register may reference the ADR that introduced or mitigated the risk.

---

# 49. Risk and Data Governance

Data risks should connect with:

* OpenMetadata
* Data ownership
* Data classification
* Data quality
* Lineage
* Retention

Governance metadata provides risk evidence.

---

# 50. Risk and AI Governance

AI risks should connect with:

* Model Registry
* Evaluation
* Model ownership
* Prompt governance
* Human oversight
* AI monitoring

AI risk controls should be defined throughout the AI lifecycle.

---

# 51. Risk and Security Governance

Security risks should connect with controls such as:

* RBAC
* TLS
* Secret management
* NetworkPolicy
* Image scanning
* Admission policies
* Audit logs

Security findings should be traceable to risk records where significant.

---

# 52. Risk as Code

Risk as Code is the machine-readable representation of risk governance.

Example:

```yaml
id: RISK-AI-002
title: GPU capacity exhaustion
domain: ai
owner: ai-platform

inherent:
  likelihood: 4
  impact: 4

controls:
  - gpu-monitoring
  - resource-limits
  - inference-queue

residual:
  likelihood: 3
  impact: 3

status: monitoring
```

This enables automation.

---

# 53. Risk as Code Architecture

```text
Risk Definition
      │
      ▼
Git
      │
      ▼
CI Validation
      │
      ▼
Risk Engine / Scripts
      │
      ├── Validate
      ├── Calculate
      ├── Report
      └── Correlate
      │
      ▼
Governance Dashboard
```

This is part of the wider Governance as Code architecture.

---

# 54. Automated Risk Score

Risk scores can be calculated automatically.

Example:

```text
likelihood = 4
impact = 5

risk_score = 20
risk_level = Critical
```

Humans define likelihood and impact.

Automation calculates and validates the resulting classification.

---

# 55. Risk Schema Validation

Future CI checks may ensure:

* Risk ID exists
* Risk ID is unique
* Owner exists
* Likelihood is valid
* Impact is valid
* Treatment exists
* Critical risks have controls
* Review date is present
* Accepted risks contain justification

---

# 56. Risk CI Pipeline

```text
Risk YAML
   │
   ▼
Git Commit
   │
   ▼
CI
   │
   ├── Schema Validation
   ├── Score Calculation
   ├── Ownership Validation
   ├── Control Validation
   └── Review-Date Validation
   │
   ▼
Governance Repository
```

---

# 57. Automated Control Evidence

Risk as Code becomes more powerful when controls provide automatic evidence.

Example:

```text
Risk:
Privileged Kubernetes workload

Control:
Policy prohibits privileged containers

Evidence:
Admission policy report
```

The risk system can verify that the control is active.

---

# 58. Continuous Risk Monitoring

Target architecture:

```text
Risk Definition
      │
      ▼
Control
      │
      ▼
Runtime Evidence
      │
      ▼
KRI
      │
      ▼
Risk Dashboard
```

This transforms Risk Management from periodic documentation into continuous governance.

---

# 59. Policy Violation as Risk Signal

Example:

```text
Kyverno Policy
      │
      ▼
Violation
      │
      ▼
Governance Event
      │
      ▼
Risk Indicator
```

Repeated violations may increase risk or trigger remediation.

---

# 60. Backup Risk Evidence

Example:

```text
Risk:
Data loss

Controls:
Backup + Restore Test

Evidence:
Last backup success
Last restore success
Backup age
```

This provides measurable control effectiveness.

---

# 61. Data Risk Evidence

Example:

```text
Risk:
Poor analytics reliability

Controls:
Data Quality Rules

Evidence:
51 / 51 checks passed
```

Data quality results become governance evidence.

---

# 62. AI Risk Evidence

Future AI evidence may include:

* Evaluation score
* Hallucination test results
* Prompt-injection test results
* Model version
* Human approval
* Latency
* Failure rate

This enables continuous AI governance.

---

# 63. Risk Dashboard

A future Governance dashboard may display:

```text
Total Risks
Critical Risks
High Risks
Accepted Risks
Overdue Reviews
Failed Controls
Top KRIs
Policy Violations
Risk Trend
```

---

# 64. Risk Heatmap

A risk heatmap can visualize:

```text
Likelihood
    │
    ▼
Impact
```

and show distribution across:

* Security
* Data
* AI
* Infrastructure
* Operations

---

# 65. Risk Trend

Risk reporting should eventually track whether exposure is:

```text
Increasing ↑
Stable →
Decreasing ↓
```

Trend provides more useful information than a static score alone.

---

# 66. Example Platform Risks

Initial risks may include:

```text
RISK-INFRA-001
Physical host failure

RISK-INFRA-002
Storage exhaustion

RISK-K8S-001
Worker node unavailable

RISK-DATA-001
PostgreSQL data loss

RISK-DATA-002
Data quality degradation

RISK-AI-001
AI hallucination

RISK-AI-002
GPU capacity exhaustion

RISK-SEC-001
Credential exposure

RISK-OPS-001
Backup restoration failure

RISK-OPS-002
Loss of observability
```

These should be validated before becoming the authoritative Risk Register.

---

# 67. Physical Infrastructure Risk

The platform intentionally operates on fixed hardware.

This creates known constraints including:

* Limited redundancy
* Limited GPU capacity
* Limited storage
* Hardware failure exposure

These risks are accepted only where mitigated to an appropriate level through:

* Kubernetes resilience
* Backup
* Monitoring
* Recovery procedures
* Capacity management

---

# 68. Risk Prioritization

Risk treatment priority should consider more than score alone.

Also consider:

* Regulatory impact
* Security implications
* Business criticality
* Cost of treatment
* Dependency relationships
* Immediacy

A score supports judgment rather than replacing it.

---

# 69. Risk Dependencies

Risks may be related.

Example:

```text
Storage Pressure
      │
      ▼
Prometheus Failure
      │
      ▼
Loss of Monitoring
      │
      ▼
Delayed Incident Detection
```

Risk analysis should identify important chains.

---

# 70. Systemic Risk

Some risks affect multiple services.

Examples:

* Kubernetes control plane
* Core networking
* Shared PostgreSQL
* Shared storage
* GitLab
* Argo CD

These require particular attention because their blast radius is larger.

---

# 71. Risk Reporting

Governance reporting should summarize:

* Current critical risks
* Newly identified risks
* Risk changes
* Treatment progress
* Accepted risks
* Overdue reviews
* Failed controls

Reports should increasingly be generated automatically from the Risk as Code repository.

---

# 72. Risk Review Cadence

Recommended:

## Continuous

KRIs and automated controls.

## Monthly

High and critical risk review.

## Quarterly

Full Risk Register review.

## Event Driven

After:

* Major incident
* Major architecture change
* Security finding
* Regulatory change

---

# 73. Risk Register Version Control

The Risk Register should be maintained in Git.

Benefits:

* History
* Ownership
* Review
* Traceability
* Automation
* Audit evidence

Risk state changes become visible through commits.

---

# 74. Governance Repository Structure

A future structure could include:

```text
governance/
├── risks/
│   ├── infrastructure/
│   ├── security/
│   ├── data/
│   ├── ai/
│   └── operations/
│
├── controls/
├── policies/
├── exceptions/
└── schemas/
```

This supports Governance as Code.

---

# 75. Risk Exception Relationship

Governance exceptions may create or increase risk.

Example:

```text
Exception:
Allow workload without NetworkPolicy

        │
        ▼

Associated Risk:
RISK-SEC-012
```

Exceptions should therefore reference related risks.

---

# 76. Risk Acceptance as Code

Accepted risk may be represented as:

```yaml
status: accepted

acceptance:
  owner: platform
  reason: >
    Risk accepted temporarily because the service
    is development-only.
  review_date: 2026-11-01
```

CI can detect expired acceptance.

---

# 77. Expired Risk Acceptance

Target behavior:

```text
Accepted Risk
     │
     ▼
Review Date Reached
     │
     ▼
Governance Check Fails
     │
     ▼
Review Required
```

This prevents permanent forgotten risk acceptance.

---

# 78. Risk Management Anti-Patterns

Avoid:

* Risk register created only for audit
* Every risk scored identically
* Risks without owners
* Risks without treatment
* Permanent accepted risks without review
* Closing risks without evidence
* Treating controls as proof that risk is zero
* Hundreds of meaningless risks
* Static spreadsheet never updated

Risk Management must support engineering decisions.

---

# 79. Current Foundations

Existing project capabilities supporting Risk Management include:

* Governance documentation
* Security architecture
* AI governance
* Data governance
* GDPR register
* Decision Matrix
* Decision Journal
* RACI
* Backup architecture
* PCA/PRA
* Observability
* Alerting
* SLI/SLO framework
* OpenMetadata
* Data quality controls
* GitOps

These provide inputs for a formal Risk Register.

---

# 80. Current Maturity

```text
Risk Awareness             → Strong
Risk Documentation         → Developing
Security Risk Controls     → Strong / Developing
Data Risk Controls         → Strong
AI Risk Governance         → Developing
Operational Risk Controls  → Strong / Developing
Formal Risk Register       → To Formalize
Risk as Code               → Target
Automated KRIs             → Developing
Continuous Risk Monitoring → Future
```

---

# 81. Implementation Roadmap

Recommended sequence:

```text
1. Define risk taxonomy
2. Create Risk Register
3. Assign stable IDs
4. Assign owners
5. Score risks
6. Map controls
7. Calculate residual risk
8. Link risks to ADRs
9. Move Risk Register to YAML
10. Define JSON/YAML schema
11. Add CI validation
12. Connect KRIs
13. Build Governance Dashboard
14. Automate control evidence
```

---

# 82. Architecture Decisions

Key decisions include:

* Risk Management is integrated with Governance as Code
* Risk records should progressively become machine-readable
* Git is the Risk Register system of record
* Risks use stable identifiers
* Risk score uses likelihood × impact as the initial model
* Both inherent and residual risk are recorded
* Risk acceptance requires explicit ownership and review
* Critical risks require treatment and monitoring
* Risks link to controls, ADRs, exceptions, and incidents
* KRIs connect operational telemetry with governance
* Automated control evidence is the target state
* Risk scoring supports human judgment rather than replacing it

---

# 83. Related Documents

* Governance Architecture
* Architecture Governance
* Decision Governance
* Compliance Governance
* Technology Governance
* Security Architecture
* Data Governance
* AI Governance
* Incident Management
* Problem Management
* Change Management
* Capacity Management
* PCA/PRA
* GDPR Register
* Decision Matrix
* Decision Journal
* RACI
* `98-ADR/`
