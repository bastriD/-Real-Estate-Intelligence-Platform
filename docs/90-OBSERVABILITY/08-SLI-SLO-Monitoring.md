# SLI and SLO Monitoring

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the Service Level Indicator (SLI) and Service Level Objective (SLO) Monitoring Architecture of the Enterprise AI Platform.

It establishes how service reliability is measured, evaluated, visualized, and improved using objective telemetry.

The goal is to replace vague reliability expectations with measurable service behavior.

---

# 2. Scope

This architecture applies to:

* Business applications
* APIs
* Kubernetes services
* PostgreSQL
* Airflow
* Data pipelines
* Data freshness
* MLflow
* AI inference
* RAG services
* Backup operations
* Platform services
* Critical infrastructure dependencies

---

# 3. Objectives

SLI/SLO monitoring aims to:

* Measure service reliability objectively
* Define meaningful reliability targets
* Detect degradation early
* Support error-budget management
* Improve alert quality
* Prioritize reliability work
* Support SRE practices
* Align technical monitoring with business impact
* Provide transparent service health reporting

---

# 4. Principles

The platform follows these principles:

* Measure User-Visible Behavior
* Prefer Simple SLIs
* Use Real Telemetry
* SLOs Must Be Achievable
* SLOs Are Not Automatically SLAs
* Error Budgets Balance Reliability and Delivery
* Alert on Budget Risk
* Review SLOs Regularly
* Do Not Claim Unvalidated Targets
* Reliability Targets Follow Business Criticality

---

# 5. SLI, SLO and SLA

## Service Level Indicator — SLI

An SLI is a measured reliability value.

Example:

```text
Successful API requests
-----------------------
Total API requests
```

---

## Service Level Objective — SLO

An SLO defines the desired value for an SLI.

Example:

```text
99.9% successful API requests over 30 days
```

---

## Service Level Agreement — SLA

An SLA is a formal commitment to a service consumer and may include contractual consequences.

The current platform primarily defines internal SLOs.

Formal external SLAs are outside the current scope unless business requirements later require them.

---

# 6. SLI/SLO Architecture

```text
Service
   │
   ▼
Telemetry
   │
   ▼
Prometheus
   │
   ▼
SLI Recording Rules
   │
   ▼
SLO Evaluation
   │
   ├── Grafana Dashboards
   ├── Error Budgets
   └── Burn-Rate Alerts
          │
          ▼
        SRE
```

---

# 7. Good SLI Characteristics

A good SLI should be:

* Measurable
* Stable
* Understandable
* Relevant to users
* Available from reliable telemetry
* Cheap enough to calculate continuously

Avoid defining dozens of SLIs for one service.

A small number of meaningful indicators is preferable.

---

# 8. Service Criticality

SLO strictness should depend on business criticality.

Example classification:

| Tier   | Service Type               | Reliability Expectation |
| ------ | -------------------------- | ----------------------- |
| Tier 1 | Critical business service  | Highest                 |
| Tier 2 | Important platform service | High                    |
| Tier 3 | Supporting service         | Moderate                |
| Tier 4 | Development / experimental | Best effort             |

Exact values must be validated against actual operational needs.

---

# 9. Measurement Windows

Typical SLO measurement windows include:

```text
7 days
28 days
30 days
90 days
```

A rolling 28- or 30-day window is commonly useful for operational SLOs.

The same service may use short windows for alerting and longer windows for reporting.

---

# 10. Availability SLI

Availability measures whether valid requests receive successful responses.

Example:

```text
Availability =
Good Requests
-------------
Valid Requests
```

PromQL concept:

```promql
sum(rate(http_requests_total{service="business-api",status!~"5.."}[5m]))
/
sum(rate(http_requests_total{service="business-api"}[5m]))
```

Client errors should be handled according to service semantics rather than automatically classified as platform failure.

---

# 11. Example Availability SLO

Architectural example:

```text
Business API availability target:
99.9% over 30 days
```

This is a proposed target, not a validated production commitment.

It must be tested against:

* Infrastructure capability
* Actual service performance
* Business criticality
* Maintenance strategy

---

# 12. Latency SLI

Latency should represent user-facing request performance.

Example:

```text
Percentage of requests completed
within 500 ms
```

This can be more meaningful than a simple average.

---

# 13. Latency SLO

Example:

```text
95% of API requests complete in < 500 ms
over a 30-day window
```

The exact threshold depends on application behavior.

AI endpoints require separate thresholds because inference workloads have different performance characteristics.

---

# 14. Histogram-Based Measurement

Prometheus histograms should be used where possible.

Example:

```promql
sum(rate(http_request_duration_seconds_bucket{
  service="business-api",
  le="0.5"
}[5m]))
/
sum(rate(http_request_duration_seconds_count{
  service="business-api"
}[5m]))
```

This measures the fraction of requests below the target latency.

---

# 15. Data Pipeline SLI

Data pipelines require different reliability indicators.

Recommended SLIs include:

* Successful execution rate
* Data freshness
* Pipeline duration
* Data quality success

Example:

```text
Critical DAG executions successful
-------------------------------
Total expected DAG executions
```

---

# 16. Airflow SLO

Example architectural target:

```text
99% of scheduled critical DAG executions
complete successfully
```

This should apply only to identified production-critical DAGs.

Experimental DAGs should not influence production reliability SLOs.

---

# 17. Data Freshness SLI

Data freshness measures the age of a dataset compared with its expected refresh time.

Example:

```text
Current time
-
Last successful load
```

A dataset expected every six hours may define:

```text
Good = data age <= 6 hours
```

or a controlled grace period where appropriate.

---

# 18. Data Freshness SLO

Example:

```text
99% of observation time:
analytics dataset age <= 6 hours
```

Freshness is often more meaningful to consumers than pipeline execution status.

---

# 19. Data Quality SLI

Potential SLI:

```text
Passed critical data-quality checks
-----------------------------------
Total critical data-quality checks
```

This distinguishes pipeline availability from trustworthy data.

---

# 20. PostgreSQL SLI

Potential database SLIs include:

* Connection success
* Query success
* Availability
* Transaction success
* Latency

The selected SLI should reflect how applications consume PostgreSQL.

---

# 21. Kubernetes Platform SLI

Potential platform-level indicators include:

* Kubernetes API availability
* Scheduling success
* Critical workload availability

Avoid treating every individual Pod restart as a platform SLO violation.

The SLI should represent meaningful service impact.

---

# 22. AI Inference SLI

AI inference SLIs may include:

* Successful inference rate
* Service availability
* Inference latency
* Timeout rate

Example:

```text
Successful inference requests
-----------------------------
Valid inference requests
```

---

# 23. AI Inference SLO

Example architectural target:

```text
99.5% successful AI inference requests
over 30 days
```

The lower example target relative to conventional APIs recognizes:

* Limited GPU capacity
* Model loading behavior
* Inference complexity

It remains a proposed target until measured.

---

# 24. AI Latency SLO

AI latency should be defined separately from standard APIs.

Possible indicators include:

* Time to first token
* Full response duration
* Tokens per second

Example:

```text
95% of standard inference requests
begin response within defined threshold
```

Thresholds must be model- and workload-specific.

---

# 25. AI Quality SLI

Technical service success does not guarantee useful AI output.

Future quality SLIs may include:

* Citation coverage
* Retrieval relevance
* Structured-output validity
* Human acceptance
* Evaluation success

Quality SLIs should remain separate from infrastructure availability SLIs.

---

# 26. RAG SLI

Future RAG SLIs may include:

* Retrieval success
* Retrieval latency
* Citation availability
* Vector store availability
* Embedding success

Example:

```text
RAG requests returning required source citations
------------------------------------------------
Total eligible RAG requests
```

---

# 27. Backup SLI

Backup reliability should include:

```text
Successful scheduled backups
----------------------------
Expected scheduled backups
```

However backup success alone is incomplete.

---

# 28. Restore SLI

A stronger recovery SLI may include:

```text
Successful restore tests
------------------------
Scheduled restore tests
```

This provides actual evidence of recoverability.

---

# 29. Error Budget

An error budget represents allowed failure within the SLO.

For a 99.9% availability objective:

```text
Allowed failure = 0.1%
```

For 30 days this is approximately:

```text
43 minutes
```

The budget can be consumed by:

* Outages
* Excessive errors
* Slow requests
* Failed jobs

depending on the SLI definition.

---

# 30. Error Budget Purpose

Error budgets help answer:

> Can we safely continue feature delivery?

If reliability remains healthy:

```text
Continue planned delivery
```

If reliability deteriorates:

```text
Prioritize reliability work
```

This creates an objective trade-off between speed and stability.

---

# 31. Error Budget Policy

Potential policy:

## Budget Healthy

Continue standard development and releases.

## Budget at Risk

Increase reliability review and reduce risky changes.

## Budget Exhausted

Prioritize:

* Reliability fixes
* Root Cause Analysis
* Capacity remediation
* Technical debt
* Release risk reduction

This policy should eventually be approved through governance.

---

# 32. Burn Rate

Burn rate measures how quickly the error budget is consumed.

```text
Burn Rate =
Observed Error Rate
-------------------
Allowed Error Rate
```

Example:

```text
SLO 99.9%
Allowed errors = 0.1%

Observed error rate = 1%

Burn rate = 10
```

The budget is being consumed ten times too quickly.

---

# 33. Burn Rate Interpretation

```text
Burn rate < 1
Sustainable

Burn rate ≈ 1
Budget consumed at expected maximum rate

Burn rate >> 1
Reliability risk
```

High burn-rate periods require attention even if the long-term SLO has not yet been violated.

---

# 34. Multi-Window Burn Rate

A mature alerting strategy should compare multiple windows.

Example:

```text
Fast window: 5 minutes
Slow window: 1 hour
```

Alert when both indicate excessive burn.

This helps avoid alerts caused by short-lived spikes.

---

# 35. Fast-Burn Alert

Fast-burn alerts identify severe degradation.

Example use cases:

* Major API outage
* Severe error increase
* Complete dependency failure

These should trigger rapid investigation.

---

# 36. Slow-Burn Alert

Slow-burn alerts identify sustained degradation.

Examples:

* Persistent moderate error rate
* Long-term latency degradation
* Data freshness deterioration

These may require action before the monthly SLO is actually missed.

---

# 37. Recording Rules

SLI calculations should use Prometheus recording rules.

Example:

```yaml
groups:
  - name: business-api-sli
    rules:
      - record: service:business_api_requests:rate5m
        expr: |
          sum(rate(http_requests_total{
            service="business-api"
          }[5m]))
```

Complex SLI expressions should not be duplicated across dashboards and alerts.

---

# 38. Availability Recording Rule

Conceptual example:

```yaml
- record: service:business_api_availability:ratio_rate5m
  expr: |
    sum(rate(http_requests_total{
      service="business-api",
      status!~"5.."
    }[5m]))
    /
    sum(rate(http_requests_total{
      service="business-api"
    }[5m]))
```

Naming conventions should be standardized.

---

# 39. SLO Configuration as Code

SLO definitions should eventually be maintained in Git.

Each definition should include:

* Service
* Owner
* SLI
* Target
* Window
* Business justification
* Alert policy

This makes reliability expectations auditable.

---

# 40. Example SLO Definition

```yaml
service: business-api
owner: platform
indicator:
  type: availability
objective: 99.9
window: 30d
```

The exact implementation format may evolve.

The architectural requirement is version-controlled SLO definition.

---

# 41. Grafana SLO Dashboard

A standard SLO view should display:

```text
Service
Current SLI
SLO Target
Error Budget Remaining
Burn Rate
P95 Latency
Active Alerts
Recent Deployments
```

This provides a service-level reliability view.

---

# 42. SLO Status

A simple status model may include:

```text
Healthy
At Risk
Breached
Unknown
```

`Unknown` is important when required telemetry is missing.

Missing metrics should not be displayed as healthy service behavior.

---

# 43. Missing Telemetry

SLO monitoring must detect absent telemetry.

Example:

```text
No requests
```

can mean:

* Service has no traffic
* Metrics disappeared
* Service is unavailable
* Scraping failed

SLI logic must distinguish these cases where practical.

---

# 44. Maintenance Windows

Planned maintenance should be addressed explicitly in SLO definitions.

Options include:

* Count maintenance as downtime
* Exclude approved maintenance
* Define separate internal targets

The chosen policy must remain consistent and documented.

---

# 45. Low-Traffic Services

Request-based SLIs can be misleading for very low traffic.

A service receiving only a few requests may require:

* Synthetic monitoring
* Availability probes
* Longer windows

The measurement model should reflect actual traffic patterns.

---

# 46. Synthetic SLI

Future synthetic checks may test:

* HTTP availability
* Authentication
* Business workflow
* AI inference
* Database-backed request

Synthetic probes provide an external user-oriented perspective.

---

# 47. SLO Ownership

Every SLO requires an owner.

Example:

| Service               | Owner                  |
| --------------------- | ---------------------- |
| Kubernetes            | Platform               |
| Business API          | Application / Platform |
| PostgreSQL            | Data / Platform        |
| Airflow Critical DAGs | Data Engineering       |
| MLflow                | MLOps                  |
| AI Inference          | AI / Platform          |

Ownership includes reviewing the objective and responding to breaches.

---

# 48. Business Ownership

Technical teams should not define critical production reliability requirements completely independently.

Business owners should help determine:

* Business impact
* Maximum acceptable disruption
* Service criticality

This keeps SLOs aligned with real requirements.

---

# 49. SLO Review

SLOs should be reviewed periodically.

Review questions include:

* Is the SLI still meaningful?
* Is the target realistic?
* Is the target too weak?
* Is the target unnecessarily strict?
* Has architecture changed?
* Is the service more critical now?
* Are users experiencing issues not represented by the SLI?

SLOs are operational agreements, not permanent constants.

---

# 50. SLO and Incident Management

SLO breaches and fast burn-rate alerts may create incidents.

Example:

```text
High burn rate
    │
    ▼
Critical alert
    │
    ▼
Incident
```

A single failed request should not automatically create an incident.

---

# 51. SLO and Problem Management

Repeated SLO degradation should trigger Problem Management.

Examples:

* Weekly latency degradation
* Frequent data freshness breach
* Persistent AI timeout rate

Reliability patterns should produce engineering improvements.

---

# 52. SLO and Change Management

Deployment decisions may consider error-budget health.

Example:

```text
Error budget healthy
→ normal release

Error budget nearly exhausted
→ high-risk release deferred
```

This connects SRE and Change Management objectively.

---

# 53. SLO and Capacity Management

SLO degradation may indicate resource constraints.

Examples:

* Latency increase caused by CPU saturation
* AI latency caused by GPU queueing
* Data freshness caused by insufficient ETL capacity

Capacity and reliability should therefore be analyzed together.

---

# 54. SLO and AI Capacity

The AI platform operates with two GTX 1080 GPUs with 8 GB VRAM each.

This physical constraint must influence realistic AI objectives.

AI SLOs should not assume:

* Unlimited concurrency
* Automatic GPU scaling
* Multi-region failover
* Unlimited model size

Objectives must reflect actual infrastructure.

---

# 55. Service Dependency SLOs

A service SLO depends on multiple components.

Example:

```text
Business API
    │
    ├── Kubernetes
    ├── Network
    └── PostgreSQL
```

The business API should still have its own user-facing SLO.

Dependency metrics support diagnosis but should not replace the service-level objective.

---

# 56. Composite SLOs

Complex business workflows may require composite indicators.

Example:

```text
Successful Property Analysis =
API success
AND
Database success
AND
Required AI operation success
```

Composite SLIs should only be introduced where they clearly reflect real user outcomes.

---

# 57. SLO Anti-Patterns

Avoid:

* One SLO for every metric
* 100% reliability targets without justification
* Targets based on guesswork presented as commitments
* Infrastructure-only SLOs for business applications
* Constantly changing objectives
* SLOs nobody reviews
* SLOs without owners
* SLO dashboards without alerts
* Alerts based on metrics unrelated to the SLO

---

# 58. Why Not 100%

A 100% SLO effectively provides no error budget.

This makes:

* Maintenance
* Deployments
* Controlled failures
* Experimentation

operationally impossible without violating the objective.

Extremely high reliability should only be required where business value justifies the cost.

---

# 59. Current Proposed SLO Catalog

Initial architectural examples:

| Service                 | Indicator         |  Proposed Objective |
| ----------------------- | ----------------- | ------------------: |
| Business API            | Availability      |               99.9% |
| PostgreSQL              | Availability      |               99.9% |
| AI Inference            | Request Success   |               99.5% |
| Critical Airflow DAGs   | Execution Success |                 99% |
| Critical Analytics Data | Freshness         | Defined per dataset |
| Backups                 | Scheduled Success |         100% target |
| Restore Tests           | Scheduled Success |         100% target |

These are candidate objectives for later validation.

---

# 60. Backup Objective Clarification

Although scheduled backup success may target 100%, one failed backup does not necessarily mean irreversible data loss if prior recovery points remain valid.

Operational response should consider:

* RPO
* Existing backups
* Failure duration
* Restore readiness

The objective remains strict because backup failure creates hidden future risk.

---

# 61. Current Implementation

Current capabilities supporting SLI/SLO monitoring include:

* Prometheus
* Grafana
* kube-prometheus-stack
* Alertmanager
* Application metrics
* ETL metrics
* Data quality monitoring
* AI/API monitoring
* Kubernetes monitoring

The required technical foundation already exists.

---

# 62. Current Maturity

```text
Metrics Collection        → Strong
Service Monitoring        → Strong / Developing
Availability Metrics      → Implemented / Developing
Latency Metrics           → Implemented / Developing
Data Freshness Metrics    → Developing
AI Service Metrics        → Developing
Formal SLI Definitions    → To Implement
Formal SLO Catalog        → To Implement
Error Budgets             → To Implement
Burn-Rate Alerts          → To Implement
SLO Governance            → To Formalize
```

---

# 63. Implementation Roadmap

Recommended sequence:

```text
1. Identify critical services
2. Assign owners
3. Define one or two SLIs per service
4. Validate Prometheus metrics
5. Create recording rules
6. Establish initial targets
7. Build Grafana dashboards
8. Measure actual performance
9. Adjust unrealistic targets
10. Introduce error budgets
11. Add burn-rate alerts
```

Measurement should precede aggressive enforcement.

---

# 64. Governance

Every production SLO should eventually document:

* Service
* Owner
* Criticality
* SLI definition
* Objective
* Measurement window
* Data source
* Exclusions
* Alert policy
* Review date

This prevents ambiguous reliability expectations.

---

# 65. Architecture Decisions

Key decisions include:

* SLIs measure user-relevant service behavior
* SLOs remain internal objectives unless explicitly converted into SLAs
* Proposed targets are not presented as validated production commitments
* Prometheus is the primary measurement source
* Recording rules standardize SLI calculations
* Grafana provides SLO visualization
* Error budgets balance reliability and delivery velocity
* Burn-rate alerting is the target alert model for critical services
* Data freshness is a first-class reliability indicator
* AI availability and AI quality remain separate concerns
* SLO targets must respect physical infrastructure constraints
* SLOs require ownership and periodic review
* Missing telemetry must never be silently interpreted as healthy service state

---

# 66. Related Documents

* Observability Architecture
* Metrics Architecture
* Dashboard Strategy
* Alerting Strategy
* Observability Governance
* Observability Operations
* SRE Practices
* Availability Management
* Capacity Management
* Incident Management
* Problem Management
* Change Management
* Data Quality
* AI Observability
