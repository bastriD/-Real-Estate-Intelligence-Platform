# Alerting Strategy

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the Alerting Strategy of the Enterprise AI Platform.

It establishes how alerts are designed, evaluated, routed, grouped, prioritized, documented, tested, reviewed, and retired across infrastructure, Kubernetes, applications, data services, AI workloads, security monitoring, backup, and SRE operations.

The objective is to ensure that alerts trigger meaningful action without overwhelming operators with noise.

---

# 2. Scope

This strategy applies to:

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
* OpenMetadata
* AI inference
* GPU resources
* Security monitoring
* Backup and restore
* Disaster recovery
* SLI/SLO monitoring
* Platform services

---

# 3. Objectives

The alerting platform aims to:

* Detect service degradation quickly
* Detect availability failures
* Detect reliability risks
* Detect capacity risks
* Detect data pipeline failures
* Detect AI service failures
* Detect backup failures
* Detect security-relevant events
* Reduce Mean Time to Detect
* Support Incident Management
* Avoid alert fatigue
* Route alerts to the correct owner
* Link alerts to actionable runbooks

---

# 4. Alerting Principles

The platform follows these principles:

* Alert on Symptoms That Require Action
* Prefer Service Impact Over Raw Infrastructure Thresholds
* Every Alert Requires Ownership
* Every Critical Alert Requires a Runbook
* Avoid Duplicate Alerts
* Group Related Failures
* Suppress Downstream Noise
* Use Appropriate `for` Durations
* Prefer SLO-Based Alerts for Critical Services
* Test Alerts Before Production
* Review Alert Quality Regularly
* Retire Alerts That No Longer Provide Value

---

# 5. Alerting Architecture

```text id="ast720"
Telemetry
   │
   ▼
Prometheus
   │
   ▼
PrometheusRule
   │
   ▼
Alert Evaluation
   │
   ▼
Alertmanager
   │
   ├── Grouping
   ├── Routing
   ├── Inhibition
   ├── Deduplication
   └── Notification
           │
           ▼
      Operations
           │
           ▼
   Incident Management
```

---

# 6. PrometheusRule

Alert rules should be defined declaratively through `PrometheusRule` resources.

Conceptual example:

```yaml id="4rc8ll"
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: business-api-alerts
  namespace: monitoring
spec:
  groups:
    - name: business-api
      rules:
        - alert: BusinessAPIHighErrorRate
          expr: |
            (
              sum(rate(http_requests_total{
                service="business-api",
                status=~"5.."
              }[5m]))
              /
              sum(rate(http_requests_total{
                service="business-api"
              }[5m]))
            ) > 0.05
          for: 10m
          labels:
            severity: warning
            service: business-api
          annotations:
            summary: "Business API error rate is above 5%"
            description: "The Business API has exceeded the acceptable error threshold for 10 minutes."
            runbook_url: "docs/runbooks/business-api-high-error-rate.md"
```

Alert rules should be version-controlled.

---

# 7. Alert Lifecycle

Every alert should follow a lifecycle.

```text id="7ee9v9"
Need Identified
      │
      ▼
Rule Designed
      │
      ▼
Tested
      │
      ▼
Reviewed
      │
      ▼
Deployed
      │
      ▼
Observed
      │
      ▼
Tuned
      │
      ▼
Retired
```

Alerts should not remain indefinitely without review.

---

# 8. Alert Categories

Recommended alert domains include:

```text id="du7a9v"
Infrastructure
Kubernetes
Application
Data
AI
Security
Backup / DR
Observability
SRE / SLO
```

This supports consistent routing and ownership.

---

# 9. Severity Model

The platform should use a small and consistent severity model.

## Critical

Immediate or imminent major business impact.

Examples:

* Core business API unavailable
* PostgreSQL unavailable
* Kubernetes control plane unavailable
* Critical data corruption detected
* Critical backup coverage lost

Expected response:

Immediate investigation.

---

## Warning

Service degradation or a condition likely to become significant if ignored.

Examples:

* High API latency
* Storage approaching capacity
* Data freshness risk
* Elevated failure rate
* GPU saturation

Expected response:

Timely investigation.

---

## Informational

Operational state that may be useful but does not require urgent action.

Examples:

* Planned maintenance
* Non-critical job completion
* Configuration event

Informational events should generally not produce disruptive notifications.

---

# 10. Severity vs Priority

Severity describes technical or business impact.

Priority describes response urgency.

They are related but not always identical.

Example:

```text id="a9i3yq"
Severity = Warning

but

Priority = High

because a business deadline is approaching.
```

Incident Management may adjust operational priority after an alert fires.

---

# 11. Actionable Alerts

An alert is actionable when the recipient can reasonably do something about it.

Bad alert:

```text id="o7foko"
CPU = 82%
```

Better alert:

```text id="3yv1xl"
Business API P95 latency is above its target
and worker CPU has remained saturated for 15 minutes.
```

The second alert explains impact and likely cause.

---

# 12. Symptom vs Cause Alerts

Critical services should preferably alert on symptoms.

Example symptom:

```text id="uwmevt"
API availability below target
```

Potential cause:

```text id="v7fn7f"
Worker CPU high
```

Infrastructure cause alerts remain useful, but should not create redundant incidents for the same service failure.

---

# 13. Alert Content Standard

Every important alert should contain:

```text id="8vi419"
Alert Name
Severity
Service
Environment
Summary
Description
Current Condition
Potential Impact
Runbook
Owner
```

Where relevant, include:

* Dashboard URL
* Logs URL
* Trace search
* Related SLO

---

# 14. Naming Convention

Recommended alert naming:

```text id="qkpawo"
<Service><Condition>
```

Examples:

```text id="fqzs1f"
BusinessAPIUnavailable
BusinessAPIHighErrorRate
PostgreSQLConnectionSaturation
AirflowCriticalDAGFailed
OllamaInferenceUnavailable
BackupJobFailed
```

Names should remain stable and descriptive.

---

# 15. `for` Duration

Prometheus alerts should use a `for` duration where appropriate.

Example:

```yaml id="tyxtgr"
for: 10m
```

This prevents alerts from firing because of short-lived fluctuations.

Duration should match the condition.

Example:

```text id="5he8zp"
Service Down        → short duration
CPU High            → longer duration
Disk Growth Risk    → longer duration
```

---

# 16. Flapping

An alert that repeatedly transitions between firing and resolved creates operational noise.

Possible mitigations include:

* Appropriate thresholds
* Appropriate `for` duration
* Hysteresis-like design
* Better aggregation
* Service-level conditions

Flapping alerts should be reviewed.

---

# 17. Alertmanager

Alertmanager handles notification logic after Prometheus evaluates alerts.

Responsibilities include:

* Grouping
* Routing
* Deduplication
* Inhibition
* Silences
* Notification delivery

Prometheus determines **whether an alert is true**.

Alertmanager determines **what happens with that alert**.

---

# 18. Grouping

Related alerts should be grouped.

Possible grouping dimensions:

```text id="514x1d"
alertname
service
namespace
cluster
severity
```

Grouping prevents hundreds of individual notifications during one failure.

---

# 19. Example Grouping

Without grouping:

```text id="pl09yk"
Pod 1 unavailable
Pod 2 unavailable
Pod 3 unavailable
API unavailable
Service unavailable
```

Potentially five notifications.

With service-aware grouping:

```text id="wp5q19"
Business API degraded
5 related alerts
```

This provides better operational context.

---

# 20. Deduplication

Alertmanager automatically deduplicates matching alerts.

This prevents repeated notification of the same active condition.

Deduplication should not hide genuinely distinct service failures.

---

# 21. Inhibition

Inhibition suppresses lower-level alerts when a higher-level condition explains them.

Example:

```text id="ksr6in"
Kubernetes Node Down
        │
        ▼
Suppress:
PodUnavailable on same node
ContainerUnavailable on same node
```

This prevents cascading alert storms.

---

# 22. Dependency Inhibition

Potential examples include:

```text id="ux3ru8"
PostgreSQL Down
      │
      ▼
Suppress some dependent application
database-connectivity alerts
```

However application-level availability alerts may remain important because they represent user impact.

Inhibition rules must therefore be designed carefully.

---

# 23. Silence

Silences temporarily suppress matching notifications.

Typical use cases:

* Planned maintenance
* Known controlled test
* Temporary accepted issue

Silences must have:

* Owner
* Reason
* Expiration

Permanent silence should not replace fixing a bad alert rule.

---

# 24. Maintenance Windows

Planned maintenance should integrate with alerting.

Possible process:

```text id="b807ll"
Change Approved
     │
     ▼
Maintenance Window
     │
     ▼
Scoped Silence
     │
     ▼
Maintenance
     │
     ▼
Silence Expires
```

Silences should be as narrow as possible.

---

# 25. Notification Routing

Routing should eventually consider:

* Service
* Severity
* Environment
* Team
* Business criticality

Conceptual model:

```text id="fjsg1m"
Alert
  │
  ├── Critical → Immediate operations channel
  ├── Warning  → Standard operations channel
  └── Info     → Dashboard / non-disruptive channel
```

Notification integrations depend on the available communication tooling.

---

# 26. Ownership

Every operational alert should have an accountable owner.

Examples:

| Alert Domain | Owner            |
| ------------ | ---------------- |
| Kubernetes   | Platform         |
| PostgreSQL   | Data / Platform  |
| Airflow      | Data Engineering |
| MLflow       | MLOps            |
| AI inference | AI / Platform    |
| Backup       | Platform         |
| Security     | Security Owner   |

One individual may hold multiple logical roles in the current project.

---

# 27. Runbook Integration

Critical and important alerts should link directly to runbooks.

Example:

```text id="135jb3"
Alert:
PostgreSQLUnavailable

Runbook:
RB-DATA-POSTGRES-001
```

A runbook should explain:

* Symptoms
* Diagnosis
* Recovery
* Validation
* Escalation

---

# 28. Dashboard Integration

Alerts should link to the most relevant dashboard.

Example:

```text id="4b0czj"
Alert
  ↓
Business API dashboard
  ↓
Prometheus metrics
  ↓
Tempo trace
  ↓
Loki logs
```

This reduces investigation time.

---

# 29. Infrastructure Alerts

Recommended infrastructure alerts include:

* Node unavailable
* CPU saturation
* Memory pressure
* Disk pressure
* Filesystem nearly full
* Network errors
* Storage I/O errors

Resource alerts should focus on sustained conditions or reliability risk.

---

# 30. Kubernetes Alerts

Recommended Kubernetes alerts include:

* Node NotReady
* Deployment replicas unavailable
* StatefulSet unavailable
* Pod CrashLoopBackOff
* Excessive Pod restarts
* Pending Pods
* PVC problems
* API server unavailable
* Control-plane component failure

Existing kube-prometheus-stack rules should be reviewed rather than blindly duplicated.

---

# 31. Application Alerts

Recommended application alerts use service-level metrics:

* Availability degradation
* High error rate
* High latency
* Request timeout rate
* Dependency failure
* Queue saturation

Application alerts should use RED metrics where possible.

---

# 32. PostgreSQL Alerts

Recommended database alerts include:

* Database unavailable
* Connection saturation
* Disk capacity risk
* Excessive deadlocks
* Excessive long-running queries
* Backup failure

Not every query slowdown requires immediate notification.

---

# 33. Airflow Alerts

Critical data workflow alerts include:

* Critical DAG failure
* Critical task failure
* Scheduler unavailable
* Data freshness breach
* Excessive retry rate
* Pipeline SLA violation

Alerts should distinguish critical production pipelines from experiments.

---

# 34. Data Freshness Alerts

Example:

```text id="jhlb1k"
Dataset expected every 6 hours

Current age = 9 hours

→ DataFreshnessSLOBreached
```

This is more business-relevant than simply alerting on an isolated failed task.

---

# 35. Data Quality Alerts

Potential alerts include:

* Critical DQ rule failure
* Significant row-count anomaly
* Referential integrity failure
* Schema validation failure

Severity should reflect downstream business impact.

---

# 36. AI Service Alerts

Recommended AI service alerts include:

* AI endpoint unavailable
* Inference error rate high
* Inference latency high
* Model loading failure
* Queue depth excessive
* Token throughput degradation

Technical availability and AI quality should remain distinct.

---

# 37. GPU Alerts

Potential GPU alerts include:

* GPU unavailable
* VRAM saturation
* Sustained high utilization
* Temperature risk
* GPU process failure

Because GPU resources are limited, resource saturation may materially affect service latency.

---

# 38. RAG Alerts

Future RAG alerts may include:

* Vector store unavailable
* Embedding service unavailable
* Retrieval error rate high
* Retrieval latency excessive
* Index synchronization failed

Quality metrics may eventually generate warnings when retrieval quality degrades.

---

# 39. Security Alerts

Security-related alerts may include:

* Repeated authentication failures
* Unexpected privileged activity
* RBAC modifications
* Suspicious API behavior
* Secret access failures

Operational Prometheus/Loki alerts do not replace a full SIEM.

---

# 40. Backup Alerts

Backup alerts are mandatory for critical assets.

Examples:

```text id="ptb5d3"
BackupJobFailed
BackupMissing
BackupStorageNearCapacity
RestoreTestFailed
BackupTooOld
```

A backup system that silently stops working creates significant hidden risk.

---

# 41. Restore Validation Alerts

Recovery readiness should also be monitored.

Example:

```text id="3w6gvo"
Last restore test > 30 days
```

This may generate a warning or governance event.

Restore confidence is as important as backup execution.

---

# 42. Observability Platform Alerts

The observability stack must monitor itself.

Examples:

* Prometheus scrape failures
* Prometheus disk risk
* Alertmanager unavailable
* Loki ingestion errors
* Tempo unavailable
* OpenTelemetry Collector dropping telemetry
* Grafana unavailable

Loss of visibility should not remain invisible.

---

# 43. SLO Alerts

Critical services should progressively adopt SLO-based alerting.

Instead of only:

```text id="icdjbn"
Error Rate > 5%
```

SLO alerting asks:

```text id="j9dtwr"
Is this failure rate consuming the error budget
fast enough to threaten the SLO?
```

This better aligns alerts with reliability objectives.

---

# 44. Burn-Rate Alerts

Burn rate describes the speed at which an error budget is consumed.

Example:

```text id="bkky8f"
Burn rate = 1
→ consuming budget at exactly sustainable rate

Burn rate = 10
→ consuming budget 10× too fast
```

High burn rate indicates urgent reliability risk.

---

# 45. Multi-Window Burn Rate

Future SLO alerts should combine short and long windows.

Example concept:

```text id="ysn79m"
High burn over 5 minutes
AND
High burn over 1 hour
```

This reduces false positives from temporary spikes.

---

# 46. Alert Fatigue

Alert fatigue occurs when operators receive too many low-value alerts.

Effects include:

* Alerts ignored
* Slower response
* Important alerts missed
* Lower operational trust

Alert volume should therefore be treated as an operational quality metric.

---

# 47. Alert Quality Metrics

Future alerting metrics may include:

* Alerts per day
* Alerts per service
* Alerts by severity
* Repeated alerts
* Flapping alerts
* Alerts resulting in incidents
* Alerts manually silenced
* False positive rate

These metrics help improve alert quality.

---

# 48. Alert Review

Alert rules should be reviewed:

* After major incidents
* After architecture changes
* When service ownership changes
* When new SLOs are introduced
* When alerts become noisy
* When alerts never fire for long periods

An unused alert may still be valuable, but it should be intentionally retained.

---

# 49. Alert Testing

Alert rules should be tested before production.

Validation includes:

* PromQL syntax
* Threshold behavior
* `for` duration
* Labels
* Annotations
* Runbook URL
* Routing
* Inhibition
* Resolution behavior

---

# 50. Controlled Alert Testing

A safe validation workflow:

```text id="acp5vd"
Create test rule
      │
      ▼
Trigger controlled condition
      │
      ▼
Prometheus fires
      │
      ▼
Alertmanager routes
      │
      ▼
Notification received
      │
      ▼
Alert resolves
```

Both firing and recovery behavior must be verified.

---

# 51. Rule Validation in CI/CD

Future CI/CD should validate:

* YAML syntax
* PrometheusRule schemas
* PromQL
* Required labels
* Required annotations
* Runbook presence

This prevents invalid alerting configuration from reaching production.

---

# 52. Alert Configuration as Code

Alerting configuration should remain in Git.

Examples:

```text id="hyi2bg"
PrometheusRule
AlertmanagerConfig
Routing configuration
Inhibition rules
Alert templates
```

Workflow:

```text id="ezdf2b"
Git
 ↓
Merge Request
 ↓
Validation
 ↓
Argo CD
 ↓
Monitoring Stack
```

---

# 53. Example Repository Structure

Possible organization:

```text id="obgoei"
monitoring/
└── alerts/
    ├── infrastructure/
    ├── kubernetes/
    ├── applications/
    ├── data/
    ├── ai/
    ├── security/
    ├── backup/
    └── slo/
```

The final structure should align with the existing GitOps repository.

---

# 54. Change Management

Significant alert changes should follow the Change Management process.

Examples:

* Removing a critical alert
* Changing critical thresholds
* Changing routing
* Modifying inhibition
* Changing SLO burn-rate rules

Poor alert configuration can create operational blind spots.

---

# 55. Incident Integration

A critical alert should transition naturally into Incident Management.

```text id="kfk49f"
Alert
  ↓
Acknowledge
  ↓
Incident
  ↓
Investigation
  ↓
Mitigation
  ↓
Recovery
  ↓
Post-Incident Review
```

Not every warning requires a formal incident.

---

# 56. Problem Management Integration

Repeated alerts may indicate a deeper problem.

Example:

```text id="5u6rqf"
DiskPressure alert
every week
   │
   ▼
Problem Management
   │
   ▼
Retention / capacity root cause
```

Suppressing the alert is not the solution.

---

# 57. Capacity Integration

Capacity warnings should provide enough lead time for action.

Bad:

```text id="j54194"
Disk 100% full
```

Better:

```text id="d1jcy4"
Disk > 80% and projected growth indicates
capacity exhaustion within operational window
```

Predictive alerts can be introduced as maturity increases.

---

# 58. Alert Escalation

Escalation should depend on:

* Severity
* Duration
* Service criticality
* Business impact
* Ownership response

The current project may not require formal 24/7 escalation, but the architecture should support future escalation workflows.

---

# 59. Recovery Notifications

Operators should know when a firing condition resolves.

Resolution notifications are useful for:

* Critical service failures
* Major availability incidents
* Backup failures

However excessive resolution notifications can also add noise.

Notification behavior should be tuned by severity.

---

# 60. Current Implementation

Current alerting capabilities include:

* Prometheus
* PrometheusRule
* Alertmanager
* kube-prometheus-stack rules
* ETL alerts
* Row-count validation
* Platform monitoring
* Grafana dashboards

The platform already provides a strong technical foundation for structured alerting.

---

# 61. Current Maturity

```text id="kzzc21"
Prometheus Rules          → Strong
Alertmanager              → Implemented
Kubernetes Alerts         → Strong
Infrastructure Alerts     → Strong
Application Alerts        → Developing
Data Alerts               → Implemented / Developing
AI Alerts                 → Developing
Backup Alerts             → Developing
Runbook Integration       → To Formalize
SLO Burn-Rate Alerts      → To Implement
Alert Governance          → To Formalize
Alert Quality Metrics     → To Implement
```

---

# 62. Physical Resource Constraints

The alerting architecture operates on fixed resources.

Alert rule complexity must therefore remain controlled.

Avoid:

* Excessive expensive PromQL
* Thousands of unnecessary rules
* Extremely short evaluation intervals
* High-cardinality queries

Alerting must not materially increase Prometheus resource pressure.

---

# 63. Future Evolution

Planned improvements include:

* Standard alert templates
* Required alert ownership
* Runbook links
* Formal severity policy
* Service-aware grouping
* Improved inhibition
* SLO burn-rate alerts
* Data freshness alerts
* AI reliability alerts
* GPU alerts
* Restore-test alerts
* Alert quality dashboards
* CI/CD rule validation
* Regular alert reviews
* Automated incident enrichment

---

# 64. Architecture Decisions

Key decisions include:

* Prometheus evaluates metrics-based alert conditions
* Alertmanager manages routing, grouping, inhibition, and notification
* Critical alerts must represent meaningful service or business risk
* Service symptoms take priority over noisy low-level causes
* All important alerts require ownership
* Critical alerts require runbooks
* `for` durations are used to reduce transient noise
* Inhibition reduces cascading alerts
* Silences are temporary operational controls, not permanent fixes
* SLO-based burn-rate alerting is the target model for critical services
* Backup and restore readiness require explicit alerts
* Alert rules are managed through GitOps
* Alert quality must be reviewed continuously

---

# 65. Related Documents

* Observability Architecture
* Metrics Architecture
* Logging Architecture
* Distributed Tracing
* OpenTelemetry Architecture
* Dashboard Strategy
* SLI/SLO Monitoring
* Observability Governance
* Observability Operations
* Incident Management
* Problem Management
* Capacity Management
* Availability Management
* Backup and Restore
* AI Observability
* Security Monitoring
* SRE Practices
