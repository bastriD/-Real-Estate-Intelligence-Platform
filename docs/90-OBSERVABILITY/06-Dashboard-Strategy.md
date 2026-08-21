# Dashboard Strategy

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the Dashboard Strategy of the Enterprise AI Platform.

It establishes how Grafana dashboards are designed, organized, governed, versioned, and maintained across infrastructure, Kubernetes, applications, data workloads, AI services, security, and SRE operations.

The objective is to transform raw telemetry into actionable operational views that support decision-making, troubleshooting, capacity planning, reliability management, and business oversight.

---

# 2. Scope

This strategy applies to dashboards covering:

* Infrastructure
* Kubernetes
* Networking
* Storage
* Applications
* APIs
* PostgreSQL
* Airflow
* Data pipelines
* Data quality
* MLflow
* AI inference
* Ollama
* GPU resources
* Security events
* Backup and recovery
* SLI/SLO monitoring
* Capacity management
* Executive reporting

---

# 3. Objectives

The dashboard strategy aims to:

* Provide clear operational visibility
* Reduce dashboard sprawl
* Standardize layouts
* Support progressive troubleshooting
* Expose service health
* Correlate metrics, logs, and traces
* Support SRE practices
* Support capacity planning
* Improve incident response
* Improve business understanding
* Enable dashboard reuse
* Manage dashboards as code

---

# 4. Dashboard Principles

The platform follows these principles:

* One Dashboard, One Purpose
* Start with Service Health
* Prefer Actionable Information
* Avoid Metric Dumping
* Use Consistent Naming
* Use Consistent Variables
* Correlate Metrics, Logs, and Traces
* Display SLOs Where Relevant
* Show Business Impact Where Possible
* Manage Dashboards as Code
* Assign Ownership
* Review and Retire Obsolete Dashboards

---

# 5. Dashboard Architecture

```text id="mlo3z7"
Telemetry Sources
      │
      ├── Prometheus
      ├── Loki
      └── Tempo
      │
      ▼
Grafana
      │
      ├── Executive Dashboards
      ├── Platform Dashboards
      ├── Service Dashboards
      ├── Diagnostic Dashboards
      └── SRE Dashboards
```

Grafana acts as the primary visualization layer.

---

# 6. Dashboard Hierarchy

Dashboards should follow a layered hierarchy.

```text id="y85x9a"
Level 1
Executive / Platform Overview
        │
        ▼
Level 2
Domain Dashboard
        │
        ▼
Level 3
Service Dashboard
        │
        ▼
Level 4
Diagnostic Dashboard
```

This reduces cognitive load and helps operators drill down progressively.

---

# 7. Executive Dashboards

Executive dashboards should answer high-level questions.

Examples:

* Is the platform healthy?
* Are critical services meeting SLOs?
* Are there active major incidents?
* Is capacity at risk?
* Are critical backups succeeding?
* Is AI service availability acceptable?

Executive dashboards should avoid low-level technical detail.

---

# 8. Platform Overview Dashboard

A Platform Overview dashboard should summarize:

* Kubernetes health
* Critical service availability
* Active alerts
* CPU capacity
* Memory capacity
* Storage capacity
* Database status
* AI service status
* Backup health
* SLO status

The goal is to identify where attention is required.

---

# 9. Domain Dashboards

Recommended domain dashboards include:

```text id="z1vbg2"
Infrastructure
Kubernetes
Networking
Storage
Applications
Data
AI
Security
Backup / DR
SRE
```

Each domain dashboard provides an overview of its associated services.

---

# 10. Kubernetes Dashboard

Recommended Kubernetes indicators include:

* Node readiness
* Control-plane health
* Pod status
* Pod restarts
* Pending Pods
* Deployment availability
* CPU usage
* Memory usage
* Persistent volume usage
* Namespace utilization
* Scheduling failures

The dashboard should enable filtering by:

* Namespace
* Node
* Workload

---

# 11. Infrastructure Dashboard

Infrastructure dashboards should include:

* CPU utilization
* Memory utilization
* Disk usage
* Disk I/O
* Network traffic
* System load
* Node uptime
* Filesystem pressure

These dashboards support both capacity and failure analysis.

---

# 12. Network Dashboard

Recommended network indicators include:

* Interface throughput
* Packet errors
* Packet drops
* Ingress traffic
* DNS health
* Request latency
* Network saturation

Network dashboards should help distinguish application failures from connectivity problems.

---

# 13. Storage Dashboard

Storage dashboards should include:

* Filesystem utilization
* Persistent volume utilization
* Storage growth
* I/O latency
* Storage errors
* Backup storage capacity

Capacity thresholds should be visible before resources become critical.

---

# 14. Application Dashboard

A standard service dashboard should use the RED method.

```text id="21tx0h"
Rate
Errors
Duration
```

Recommended indicators include:

* Request rate
* Error rate
* P50 latency
* P95 latency
* P99 latency
* Active requests
* Deployment version
* Availability

---

# 15. API Dashboard

API dashboards may add:

* HTTP status distribution
* Requests by route
* Authentication failures
* Dependency latency
* Request throughput
* Timeout rate

Routes should use stable route templates rather than dynamic URLs.

---

# 16. PostgreSQL Dashboard

Recommended indicators include:

* Availability
* Active connections
* Connection utilization
* Transaction rate
* Query latency
* Locks
* Deadlocks
* Database size
* Storage growth

Database dashboards should complement query-level investigation rather than expose every internal metric.

---

# 17. Airflow Dashboard

Recommended Airflow indicators include:

* DAG success rate
* DAG failure rate
* Task failures
* Retry count
* DAG duration
* Scheduler health
* Queue depth
* Critical DAG status

Business-critical DAGs should be clearly separated from experimental pipelines.

---

# 18. Data Pipeline Dashboard

Data dashboards should answer:

* Did the pipeline run?
* Did it succeed?
* How long did it take?
* How many rows were processed?
* Is the data fresh?
* Did quality checks pass?

Example indicators:

```text id="x3i9dl"
ETL Last Success
ETL Duration
Rows Processed
Data Freshness
DQ Pass Rate
```

---

# 19. Data Quality Dashboard

Recommended indicators include:

* Total checks
* Passed checks
* Failed checks
* Null violations
* Duplicate violations
* Referential failures
* Freshness failures
* Quality score trend

A successful pipeline with failed quality checks should remain visibly degraded.

---

# 20. MLflow Dashboard

Operational MLflow dashboards should include:

* Service availability
* API latency
* API errors
* Backend database connectivity
* Artifact storage connectivity

Model performance information remains primarily in MLflow itself.

---

# 21. AI Platform Dashboard

Recommended AI operational indicators include:

* Inference availability
* Request volume
* Failure rate
* Latency
* Active requests
* Model
* Token throughput
* Queue depth
* GPU utilization
* VRAM utilization

The dashboard should clearly separate infrastructure health from AI response quality.

---

# 22. GPU Dashboard

Recommended GPU indicators include:

* GPU utilization
* Memory utilization
* Temperature
* Power usage where supported
* Active processes
* Model workload
* Saturation

Because GPU capacity is constrained, the dashboard should make bottlenecks immediately visible.

---

# 23. RAG Dashboard

Future RAG dashboards may include:

* Retrieval latency
* Embedding latency
* Search latency
* Reranking latency
* Retrieved chunk count
* Retrieval failures
* Citation coverage
* AI response latency

RAG dashboards should correlate retrieval and generation stages.

---

# 24. Security Dashboard

Security-oriented dashboards may include:

* Failed authentication
* Authorization failures
* RBAC changes
* Suspicious API activity
* Deployment changes
* Secret access failures
* Security alerts

Grafana provides operational security visibility but does not replace a full SIEM.

---

# 25. Backup Dashboard

Backup dashboards should show:

* Last backup status
* Last successful backup
* Backup duration
* Backup size
* Backup storage usage
* Restore test result
* RPO compliance
* Failed backups

Backup success alone is not sufficient.

Restore test status should be visible.

---

# 26. Disaster Recovery Dashboard

A future DR dashboard may include:

* Backup coverage
* Restore test coverage
* RTO test result
* RPO test result
* Last DR exercise
* Failed recovery tests
* Critical dependency readiness

This provides measurable DR maturity.

---

# 27. SRE Dashboard

A SRE dashboard should focus on reliability.

Recommended panels include:

* SLI
* SLO target
* Error budget
* Burn rate
* Incident frequency
* MTTR
* Change failure rate
* Capacity risk
* Backup health

SRE dashboards should support reliability decisions rather than simply display infrastructure metrics.

---

# 28. SLO Dashboard

Example service view:

```text id="0peb46"
Service: Business API

Availability SLI     99.94%
SLO Target           99.90%
Error Budget         43 min
Budget Remaining     61%
P95 Latency          182 ms
Active Incidents     0
```

This gives operators a concise reliability summary.

---

# 29. Dashboard Variables

Variables improve dashboard reuse.

Common variables include:

```text id="y3qkha"
environment
namespace
service
node
pod
database
model
```

Variables should remain meaningful and bounded.

---

# 30. Variable Design

Avoid creating dashboards with dozens of dependent variables.

A dashboard should remain understandable without requiring complex configuration before use.

Defaults should show the most useful operational scope.

---

# 31. Time Range

Dashboards should support useful time windows.

Common ranges include:

```text id="mjcakw"
15 minutes
1 hour
6 hours
24 hours
7 days
30 days
```

Diagnostic dashboards often need short windows.

Capacity dashboards require longer historical views.

---

# 32. Refresh Intervals

Refresh frequency should match the dashboard purpose.

Example:

```text id="62jiie"
Incident dashboard      10–30 seconds
Platform dashboard      30–60 seconds
Capacity dashboard      5 minutes
Executive dashboard     1–5 minutes
```

Excessive refresh rates increase backend load unnecessarily.

---

# 33. Panel Design

Each panel should answer a clear question.

Good:

```text id="m4x8dz"
What is the API P95 latency?
```

Poor:

```text id="5yylmn"
Various HTTP Metrics
```

Panel titles should communicate meaning immediately.

---

# 34. Units

Correct units improve readability.

Examples:

* seconds
* milliseconds
* bytes
* percentage
* requests/sec
* tokens/sec

Grafana units should match the underlying metric semantics.

---

# 35. Thresholds

Thresholds should reflect meaningful operational conditions.

Example:

```text id="ng50zy"
Disk usage
< 70%   healthy
70–85%  warning
> 85%   critical
```

Thresholds should not be chosen arbitrarily.

They should align with alerting and capacity policies.

---

# 36. Color Use

Colors should communicate state consistently.

Recommended meaning:

```text id="z5c14n"
Normal      → neutral/healthy
Warning     → warning
Critical    → critical
Unknown     → neutral
```

Dashboards should avoid unnecessary decorative color.

---

# 37. Tables

Tables are useful for:

* Top failing services
* Highest resource consumers
* Failed pipelines
* Active alerts
* Backup status
* SLO status

Large raw datasets should not be displayed unnecessarily.

---

# 38. Heatmaps

Heatmaps may be useful for:

* Latency distributions
* Request duration
* Query performance
* AI inference duration

They should be used when distribution matters more than a single average.

---

# 39. Histograms and Percentiles

Latency dashboards should prefer:

```text id="zhah2z"
P50
P95
P99
```

rather than only average latency.

Averages can hide poor user experiences affecting a subset of requests.

---

# 40. Logs in Dashboards

Grafana dashboards may include targeted Loki panels.

Examples:

* Recent errors
* Failed authentication
* Recent deployment failures

Avoid flooding dashboards with entire log streams.

Logs should support the question being answered.

---

# 41. Trace Integration

Dashboards should provide links to Tempo where possible.

Example:

```text id="32ssgc"
High P95 latency
        │
        ▼
Relevant Trace
        │
        ▼
Slow Span
```

Metrics should lead to deeper investigation.

---

# 42. Exemplars

Where supported, exemplars may connect histogram observations to trace IDs.

This enables:

```text id="6romdm"
Prometheus latency point
        │
        ▼
Tempo trace
```

This is particularly valuable for application and AI latency investigations.

---

# 43. Deployment Annotations

Grafana dashboards should eventually display deployment events.

Sources may include:

* GitLab
* Argo CD
* Kubernetes rollouts
* MLflow model promotions

Example:

```text id="ffw8ka"
14:00 Deployment v1.4
14:04 Error increase
```

This improves change correlation.

---

# 44. Incident Annotations

Major incidents may also be marked on dashboards.

This provides historical context during reliability reviews.

---

# 45. Dashboard Naming

Recommended naming convention:

```text id="qriib3"
<Domain> / <Service> / <Purpose>
```

Examples:

```text id="5eomdq"
Kubernetes / Cluster / Overview
Data / Airflow / Operations
AI / Ollama / Inference
SRE / Business API / SLO
```

Consistent naming improves discoverability.

---

# 46. Folder Strategy

Grafana folders should reflect architecture domains.

Suggested folders:

```text id="4bb1rw"
00-Overview
10-Infrastructure
20-Kubernetes
30-Applications
40-Data
50-AI
60-Security
70-Operations
80-SRE
90-Diagnostics
```

The exact names may be adjusted to align with repository conventions.

---

# 47. Dashboard Ownership

Every critical dashboard should define an owner.

Examples:

| Dashboard     | Owner               |
| ------------- | ------------------- |
| Kubernetes    | Platform            |
| Airflow       | Data Engineering    |
| MLflow        | MLOps               |
| AI Inference  | AI / Platform       |
| SLO Dashboard | SRE / Service Owner |

Ownership includes maintenance responsibility.

---

# 48. Dashboard Lifecycle

Dashboards should follow:

```text id="b9rn0z"
Create
 ↓
Review
 ↓
Publish
 ↓
Use
 ↓
Improve
 ↓
Deprecate
 ↓
Remove
```

Unused dashboards should not remain indefinitely.

---

# 49. Dashboard Review

Periodic reviews should identify:

* Broken queries
* Obsolete panels
* Missing metrics
* Unused dashboards
* Duplicate dashboards
* Incorrect thresholds
* New operational requirements

This prevents dashboard sprawl.

---

# 50. Dashboard as Code

Critical dashboards should be version controlled.

Possible formats include:

* Grafana JSON
* ConfigMaps
* Helm values
* Grafana provisioning definitions

Workflow:

```text id="mun741"
Git
 ↓
Merge Request
 ↓
Review
 ↓
Argo CD
 ↓
Grafana
```

This provides reproducibility and rollback.

---

# 51. Manual Dashboards

Temporary exploratory dashboards may be created manually.

If they become operationally critical, they should be promoted into version-controlled configuration.

This balances experimentation with governance.

---

# 52. Dashboard Validation

A dashboard should be validated before being considered operational.

Validation includes:

* Queries return data
* Variables work
* Units are correct
* Thresholds are meaningful
* Links work
* Logs/traces correlate
* Empty-state behavior is understandable
* Dashboard performs acceptably

---

# 53. Query Performance

Poor dashboard queries can overload Prometheus or Loki.

Common causes include:

* Huge time ranges
* Broad LogQL queries
* Unbounded regex
* Repeated expensive PromQL
* Excessive panels

Recording rules should be used for frequently repeated complex calculations.

---

# 54. Dashboard Performance

Dashboards should avoid:

* Excessive panels
* Very short refresh intervals
* Duplicate queries
* Huge default time ranges
* High-cardinality variable queries

Dashboard usability and backend efficiency should be considered together.

---

# 55. Executive vs Diagnostic Views

Executive dashboards should remain simple.

Diagnostic dashboards may contain technical depth.

Example:

```text id="00iyig"
Executive:
Platform Availability = 99.9%

Diagnostic:
Pod restarts
Node pressure
API P95
PostgreSQL connection saturation
Trace latency
```

Mixing both audiences in one dashboard reduces usability.

---

# 56. Dashboard Anti-Patterns

Avoid:

* One dashboard containing everything
* Hundreds of unrelated panels
* No clear owner
* Duplicate dashboards
* Static screenshots used operationally
* Unexplained thresholds
* Unbounded variables
* Dashboard-only alerts
* Dashboards without service context

Dashboards should solve operational problems, not showcase every metric.

---

# 57. Dashboard and Alert Separation

Dashboards provide exploration.

Alerts trigger action.

A red panel does not replace an alert.

Likewise, not every panel requires an alert.

These concerns should remain intentionally separate.

---

# 58. Dashboard and SLO Integration

SLO dashboards should be considered first-class operational dashboards.

They should display:

* Current SLI
* Target
* Error budget
* Burn rate
* Relevant latency
* Relevant errors

This connects observability directly to reliability engineering.

---

# 59. Dashboard and Business Context

Where possible, technical dashboards should expose business impact.

Example:

Better:

```text id="qqu3mi"
ETL failure
Analytics data stale by 8 hours
```

Instead of only:

```text id="cfjmbt"
airflow_job_status=0
```

Operational telemetry becomes more valuable when connected to business consequences.

---

# 60. Dashboard and AI Context

AI dashboards should distinguish:

```text id="p8wz5k"
Infrastructure Health
Model Service Health
AI Quality
```

Example:

```text id="i68msp"
GPU healthy
Ollama healthy
Inference latency healthy
RAG retrieval quality degraded
```

Technical availability alone does not represent AI service quality.

---

# 61. Dashboard and Capacity Planning

Long-range dashboards should support:

* CPU growth
* Memory growth
* Storage growth
* Database growth
* Log growth
* GPU utilization trend

These dashboards should use longer periods than incident dashboards.

---

# 62. Dashboard and Backup Operations

Backup dashboards should explicitly include restore validation.

Example:

```text id="1vwn5a"
Backup succeeded      YES
Last restore test     14 days ago
Restore test result   PASS
```

This avoids the false assumption that a successful backup guarantees recoverability.

---

# 63. Dashboard Security

Grafana access should follow:

* Authentication
* RBAC
* Least privilege
* Network restrictions
* TLS

Sensitive dashboards may require stricter access than general operational dashboards.

---

# 64. Public Dashboards

Public or anonymous access should not be enabled for internal operational dashboards unless there is a specific justified requirement.

Dashboards may expose:

* Internal hostnames
* Service topology
* Resource usage
* Security events

This information has security value.

---

# 65. Dashboard Privacy

Panels should avoid exposing:

* Personal data
* Raw prompts
* Authentication information
* Sensitive business records

Aggregated operational metrics should be preferred.

---

# 66. Current Implementation

Current capabilities include:

* Grafana
* Prometheus
* Loki
* Tempo
* Kubernetes dashboards
* Application monitoring
* Airflow monitoring
* Data pipeline metrics
* MLflow metrics
* ETL and row-count alerts

This provides a strong foundation for a structured enterprise dashboard strategy.

---

# 67. Current Maturity

```text id="2psukq"
Grafana                    → Strong
Infrastructure Dashboards  → Strong
Kubernetes Dashboards      → Strong
Application Dashboards     → Developing
Data Dashboards            → Developing
AI Dashboards              → Developing
Security Dashboards        → Developing
SLO Dashboards             → To Implement
Dashboard-as-Code          → Developing
Dashboard Governance       → To Formalize
```

---

# 68. Resource Constraints

Dashboards must respect backend capacity.

Because the platform runs on fixed resources:

* Expensive PromQL should be minimized
* Broad Loki queries should be avoided
* Dashboard refresh rates should be controlled
* Excessive panel counts should be avoided
* Recording rules should optimize repeated calculations

Visualization must not destabilize observability backends.

---

# 69. Future Evolution

Planned improvements include:

* Standard dashboard templates
* Platform Overview dashboard
* Standard application RED dashboard
* Data Quality dashboard
* AI Inference dashboard
* GPU dashboard
* SLO dashboards
* Backup/DR dashboard
* Deployment annotations
* Trace links
* Dashboard ownership metadata
* Dashboard review process
* Dashboard linting/validation
* Full dashboard-as-code adoption

---

# 70. Architecture Decisions

Key decisions include:

* Grafana remains the primary dashboard platform
* Dashboards follow a layered hierarchy
* Executive and diagnostic dashboards remain separate
* Critical dashboards are managed as code
* RED is preferred for application dashboards
* USE is preferred for infrastructure dashboards
* SLO dashboards are first-class operational views
* Metrics, logs, and traces should be cross-linked
* Dashboard variables must remain bounded
* Dashboard queries must respect backend capacity
* Dashboards must have defined ownership
* Obsolete dashboards should be retired
* Dashboards support alerting but do not replace alerting

---

# 71. Related Documents

* Observability Architecture
* Metrics Architecture
* Logging Architecture
* Distributed Tracing
* OpenTelemetry Architecture
* Alerting Strategy
* SLI/SLO Monitoring
* Observability Governance
* Observability Operations
* AI Observability
* Capacity Management
* Availability Management
* SRE Practices
