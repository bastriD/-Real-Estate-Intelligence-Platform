# ADR-0010 — Adopt Prometheus and Grafana as the Primary Metrics and Visualization Platform

**Status:** Accepted
**Date:** 2026-08-21
**Decision Owner:** Bastri Murad
**Domain:** Observability / Platform / SRE
**Project:** Enterprise AI Platform
**Related ADRs:** ADR-0001, ADR-0002, ADR-0009
**Related Technologies:** Prometheus, Grafana, kube-prometheus-stack, Alertmanager, node-exporter, kube-state-metrics
**Supersedes:** None
**Superseded By:** None

---

# 1. Context

The Enterprise AI Platform runs a large number of infrastructure, Kubernetes, data, AI, governance, and application workloads.

These workloads require a common observability capability able to answer questions such as:

* Is the platform healthy?
* Which Kubernetes nodes are under pressure?
* Are applications available?
* Are data pipelines succeeding?
* Is PostgreSQL saturated?
* Are GPUs overloaded?
* Are AI inference services failing?
* Are SLOs being met?
* Are backups succeeding?
* Are governance controls healthy?

Without a standard metrics and visualization layer, operational information would become fragmented across individual tools and manual commands.

---

# 2. Problem

The platform needs a monitoring architecture capable of:

```text id="pg01"
Metrics Collection
      │
      ▼
Time-Series Storage
      │
      ▼
Query
      │
      ▼
Alert Evaluation
      │
      ▼
Dashboards
      │
      ▼
Operations / SRE
```

The architecture must support:

* Kubernetes
* Infrastructure
* Applications
* Data pipelines
* Databases
* AI workloads
* SLOs
* Governance metrics

The platform should remain open, self-hosted, and compatible with the existing Kubernetes architecture.

---

# 3. Decision

The platform will use **Prometheus** as the authoritative operational metrics and time-series monitoring platform.

**Grafana** will be used as the primary visualization and observability exploration interface.

The standard architecture is:

```text id="pg02"
Infrastructure / Applications
          │
          ▼
       Exporters
          │
          ▼
      Prometheus
          │
          ├── Recording Rules
          ├── Alert Rules
          └── Time Series
               │
               ▼
             Grafana
```

Alertmanager remains responsible for alert routing and notification management.

---

# 4. Architecture Role

Prometheus provides:

* Metrics scraping
* Time-series storage
* PromQL
* Recording rules
* Alert rule evaluation
* Service monitoring

Grafana provides:

* Dashboards
* Visualization
* Data-source correlation
* Operational exploration
* SLO views
* Metrics/logs/traces navigation

The two technologies serve complementary responsibilities.

---

# 5. Current Implementation

The platform already operates a Prometheus/Grafana stack using Kubernetes-native monitoring.

Current capabilities include:

* kube-prometheus-stack
* Prometheus
* Grafana
* Alertmanager
* kube-state-metrics
* node-exporter
* Pushgateway
* Kubernetes monitoring
* ETL monitoring
* Application monitoring
* Data platform monitoring

Current state:

```text id="pg03"
IMPLEMENTED
```

---

# 6. Alternatives Considered

## Option 1 — Prometheus + Grafana

Advantages:

* Open source
* Kubernetes-native ecosystem
* Strong PromQL
* Mature
* Large community
* Excellent exporter ecosystem
* Strong GitOps support
* Self-hosted
* Good SRE/SLO alignment
* Integrates naturally with Loki and Tempo

Disadvantages:

* Requires resource management
* High cardinality can become expensive
* Long-term retention requires planning
* Grafana requires dashboard governance

Selected.

---

## Option 2 — Zabbix

Advantages:

* Mature infrastructure monitoring
* Strong traditional host monitoring
* Centralized alerting

Disadvantages:

* Less Kubernetes-native
* Less aligned with current cloud-native architecture
* Would overlap with Prometheus

Not selected.

---

## Option 3 — Nagios

Advantages:

* Mature
* Simple monitoring model
* Large history

Disadvantages:

* Less suitable for dynamic Kubernetes workloads
* Less flexible time-series model
* Weaker fit with modern observability

Not selected.

---

## Option 4 — Datadog / SaaS Monitoring

Advantages:

* Rich managed platform
* Integrated metrics/logs/traces
* Strong out-of-box experience

Disadvantages:

* External SaaS dependency
* Recurring cost
* Data sovereignty considerations
* Vendor lock-in
* Existing open-source stack already satisfies requirements

Not selected as the default architecture.

---

# 7. Decision Criteria

The decision considered:

| Criterion              | Importance |
| ---------------------- | ---------: |
| Kubernetes integration |   Critical |
| Open source            |       High |
| Local deployment       |   Critical |
| Metrics capability     |   Critical |
| Alerting               |   Critical |
| SLO support            |       High |
| GitOps compatibility   |       High |
| Resource efficiency    |       High |
| Ecosystem              |       High |
| Vendor independence    |       High |

Prometheus and Grafana provide the best overall fit.

---

# 8. Metrics Architecture

The standard flow is:

```text id="pg04"
Application / Exporter
       │
       ▼
/metrics
       │
       ▼
Prometheus Scrape
       │
       ▼
Time Series
       │
       ▼
PromQL
```

Applications should expose Prometheus-compatible metrics where practical.

---

# 9. Kubernetes Monitoring

The Kubernetes monitoring stack includes:

* kube-state-metrics
* node-exporter
* Kubernetes component metrics
* Pod/application metrics

This allows visibility into:

```text id="pg05"
Nodes
Pods
Deployments
StatefulSets
Namespaces
CPU
Memory
Storage
Network
```

---

# 10. Infrastructure Metrics

Infrastructure monitoring should cover:

* CPU
* Memory
* Disk
* Filesystem
* Network
* Load
* Host availability

These provide the base for capacity and availability management.

---

# 11. Application Metrics

Applications should use the RED method where appropriate:

```text id="pg06"
Rate
Errors
Duration
```

Examples include:

* Request rate
* HTTP error rate
* P95 latency

This supports both troubleshooting and SLO measurement.

---

# 12. Data Platform Metrics

Data workloads may expose:

* Pipeline success
* Pipeline duration
* Rows processed
* Data freshness
* Data quality result

These make data reliability visible as an operational concern.

---

# 13. Airflow Metrics

Airflow monitoring should include:

* DAG success
* DAG failure
* Task failure
* Retry rate
* Scheduler health
* DAG duration

Critical workflows should be distinguishable from experimental DAGs.

---

# 14. AI Metrics

AI metrics should progressively include:

```text id="pg07"
Inference request rate
Inference failure rate
Inference duration
Queue depth
GPU utilization
VRAM utilization
Tokens per second
```

These metrics must remain bounded and avoid high-cardinality dimensions.

---

# 15. GPU Monitoring

Because the AI platform has limited GPU resources, GPU observability is important.

Relevant signals include:

* GPU utilization
* Memory utilization
* Temperature
* Active processes
* Saturation

These metrics support capacity decisions rather than hardware assumptions.

---

# 16. Metric Naming

Metrics should use stable names.

Recommended style:

```text id="pg08"
<namespace>_<subsystem>_<metric>_<unit>
```

Examples:

```text id="pg09"
ai_inference_requests_total
retail_etl_duration_seconds
```

---

# 17. Metric Types

The architecture uses standard Prometheus metric semantics.

## Counter

For cumulative events.

Example:

```text id="pg10"
http_requests_total
```

## Gauge

For current state.

Example:

```text id="pg11"
gpu_memory_used_bytes
```

## Histogram

For latency and other distributions.

Example:

```text id="pg12"
http_request_duration_seconds
```

---

# 18. Label Governance

Prometheus labels must remain bounded.

Good examples:

```text id="pg13"
service
environment
namespace
status
route
model
```

Avoid labels such as:

```text id="pg14"
user_id
request_id
session_id
email
prompt
uuid
```

High-cardinality labels can destabilize Prometheus.

---

# 19. Cardinality as an Architecture Concern

Potential series count roughly grows through combinations of labels.

Example:

```text id="pg15"
service
×
route
×
status
×
user_id
```

Adding unbounded identifiers can cause explosive series growth.

Cardinality governance is mandatory.

---

# 20. ServiceMonitor and PodMonitor

Kubernetes workloads should use declarative monitoring resources where appropriate.

Examples:

```text id="pg16"
ServiceMonitor
PodMonitor
```

These resources should be managed through GitOps.

---

# 21. Recording Rules

Frequently reused or expensive expressions should become recording rules.

Benefits:

* Faster dashboards
* Standardized SLI calculations
* Reduced query duplication

Example:

```text id="pg17"
Raw Metrics
     │
     ▼
Recording Rule
     │
     ▼
Reusable Time Series
```

---

# 22. Alerting

Prometheus evaluates alert conditions through `PrometheusRule`.

Example flow:

```text id="pg18"
Metric
  │
  ▼
PrometheusRule
  │
  ▼
Alert
  │
  ▼
Alertmanager
```

Alertmanager handles routing, grouping, inhibition, and notifications.

---

# 23. SLO Integration

Prometheus is the primary measurement engine for operational SLI/SLO calculations.

Examples include:

* Availability
* Latency
* Error rate
* Data freshness
* AI inference success

The architecture therefore treats Prometheus as part of the SRE foundation.

---

# 24. Error Budgets

Future SLO implementation should calculate:

```text id="pg19"
SLI
  │
  ▼
SLO
  │
  ▼
Error Budget
  │
  ▼
Burn Rate
```

Prometheus provides the numerical basis.

Grafana provides visualization.

Alertmanager provides operational response.

---

# 25. Grafana Role

Grafana is the unified observability visualization layer.

It connects to:

```text id="pg20"
Prometheus → Metrics
Loki       → Logs
Tempo      → Traces
```

This allows investigation across multiple signal types without introducing separate operational interfaces for each backend.

---

# 26. Dashboard Hierarchy

Dashboards should follow:

```text id="pg21"
Platform Overview
      │
      ▼
Domain Dashboard
      │
      ▼
Service Dashboard
      │
      ▼
Diagnostic Dashboard
```

This reduces dashboard sprawl.

---

# 27. Dashboard as Code

Critical Grafana dashboards should be version controlled.

Possible mechanisms include:

* Grafana JSON
* ConfigMaps
* provisioning definitions
* Helm values

Target workflow:

```text id="pg22"
Git
 ↓
Review
 ↓
Argo CD
 ↓
Grafana
```

---

# 28. Grafana Is Not the Source of Truth

Grafana visualizes telemetry.

It does not replace:

* Prometheus time-series state
* Loki logs
* Tempo traces
* SLO definitions
* Governance definitions

Important dashboards should not exist only as manually edited UI state.

---

# 29. Observability Correlation

The target operational model is:

```text id="pg23"
Metric Alert
    │
    ▼
Grafana Dashboard
    │
    ▼
Tempo Trace
    │
    ▼
Loki Logs
```

This improves Mean Time to Recovery.

---

# 30. Deployment Annotations

Grafana should eventually show deployment events.

Example:

```text id="pg24"
13:00 Deployment
13:04 Error Rate ↑
```

This improves change correlation and incident analysis.

---

# 31. Security Consequences

Monitoring data can expose:

* Infrastructure structure
* Service names
* Internal endpoints
* Resource usage
* Incident information

Grafana and Prometheus should not be publicly exposed without explicit security controls.

---

# 32. Access Control

Controls should include:

* Authentication
* RBAC
* Restricted network access
* TLS
* Least privilege

Administrative Grafana capabilities should be limited.

---

# 33. Public Dashboards

Public/anonymous dashboards are not the default.

Operational dashboards may reveal sensitive architecture information.

Any public dashboard requires explicit justification.

---

# 34. Data Sovereignty

Prometheus and Grafana are operated locally.

This supports:

* Data sovereignty
* Reduced external dependency
* Predictable operational control
* No mandatory SaaS telemetry export

This aligns with the broader local-first platform architecture.

---

# 35. Retention

Metrics retention must remain explicit.

Retention depends on:

* Storage
* Operational investigation needs
* SLO windows
* Capacity analysis

The current environment should avoid indefinite retention without measured benefit.

---

# 36. Storage Pressure

Prometheus storage pressure can impact monitoring reliability.

Operational controls include:

* Disk alerts
* Series-count review
* Retention control
* Cardinality analysis

The monitoring system must not become an unbounded storage consumer.

---

# 37. Resource Constraints

The platform has fixed compute and storage resources.

Therefore:

* Scrape intervals must be justified
* Cardinality must be controlled
* Expensive queries should be optimized
* Dashboard refresh rates should be reasonable

Observability must not starve business or AI workloads.

---

# 38. Monitoring the Monitoring Platform

Prometheus and Grafana must themselves be monitored.

Important indicators include:

* Prometheus availability
* Scrape failures
* Rule-evaluation failures
* Disk usage
* Grafana availability
* Alertmanager availability

Loss of observability is itself an operational risk.

---

# 39. Disaster Recovery

Most Prometheus/Grafana configuration should be recoverable through GitOps.

Important assets include:

```text id="pg25"
Prometheus configuration
PrometheusRule
ServiceMonitor
Grafana dashboards
Grafana provisioning
Alertmanager configuration
```

Historical metrics generally have lower recovery priority than current monitoring capability.

---

# 40. Recovery Order

Typical observability recovery priority:

```text id="pg26"
Prometheus
   │
   ▼
Alertmanager
   │
   ▼
Grafana
   │
   ▼
Additional Observability Components
```

The objective is to restore platform visibility quickly.

---

# 41. Governance as Code

Prometheus/Grafana support Governance as Code in multiple ways.

Governed artifacts include:

* ServiceMonitors
* PodMonitors
* PrometheusRules
* Recording rules
* SLO definitions
* Grafana dashboards
* Alertmanager configuration

These should be version controlled.

---

# 42. SLO as Code

Future machine-readable SLO definitions may generate:

* Prometheus recording rules
* Prometheus alert rules
* Grafana dashboards

This reduces manual inconsistency.

---

# 43. Governance Evidence

Prometheus metrics can provide evidence for governance controls.

Examples:

```text id="pg27"
Backup Success
Restore Test Age
Policy Violation Count
SLO Status
Disk Capacity
Data Freshness
```

Operational telemetry therefore becomes part of continuous governance.

---

# 44. Risk as Code Integration

Key Risk Indicators can derive from Prometheus.

Examples:

```text id="pg28"
RISK-INFRA-STORAGE
→ filesystem usage

RISK-AI-CAPACITY
→ GPU saturation

RISK-OPS-BACKUP
→ backup success
```

This connects monitoring with Risk Governance.

---

# 45. Compliance Evidence

Prometheus may provide machine-readable evidence for controls such as:

* Backup freshness
* Certificate expiry
* Service availability
* Restore-test recency

This supports Continuous Compliance.

---

# 46. When Prometheus Should NOT Be Used

Prometheus is not intended to store:

* Application log bodies
* Distributed traces
* Large business datasets
* High-cardinality event streams

Those belong in specialized systems.

---

# 47. When Grafana Should NOT Be Used

Grafana should not become:

* A business database
* The authoritative SLO definition store
* The Risk Register
* The Data Catalog

It remains a visualization and operational exploration platform.

---

# 48. Technical Debt Consideration

Prometheus and Grafana are not currently technical debt.

Potential debt includes:

* High-cardinality metrics
* Unowned dashboards
* Missing recording rules
* Manual dashboards
* Missing SLOs
* Excessive retention

These should be governed rather than solved by replacing the stack.

---

# 49. Technology Governance Status

Recommended classifications:

```text id="pg29"
Technology: Prometheus
Category: Observability / Metrics
Lifecycle: ADOPT

Technology: Grafana
Category: Observability / Visualization
Lifecycle: ADOPT
```

---

# 50. Risks

## Risk — High Cardinality

Mitigation:

* Metric standards
* Label governance
* Series monitoring

## Risk — Storage Exhaustion

Mitigation:

* Retention management
* Disk alerts

## Risk — Monitoring Blind Spot

Mitigation:

* Self-monitoring
* Alerting
* Recovery procedures

## Risk — Dashboard Drift

Mitigation:

* Dashboard as Code
* GitOps

---

# 51. Positive Consequences

The platform gains:

* Standard metrics
* Central monitoring
* Strong Kubernetes integration
* Flexible querying
* SLO foundation
* Alerting
* Unified dashboards
* Open-source local observability
* Governance evidence

---

# 52. Negative Consequences

The platform accepts:

* Prometheus storage management
* Cardinality governance
* Dashboard maintenance
* Monitoring-stack resource usage

These costs are justified by the operational value.

---

# 53. Success Criteria

The decision remains successful while:

* Critical services expose useful metrics
* Prometheus remains reliable
* Grafana dashboards answer operational questions
* Alerting remains actionable
* SLOs can be measured
* Observability resource use remains controlled

---

# 54. Review Triggers

Review this ADR if:

* Prometheus can no longer satisfy metrics scale
* Long-term retention requirements materially change
* Multi-cluster scale grows significantly
* A replacement provides substantial operational value
* Observability requirements change fundamentally

---

# 55. Governance as Code Metadata

Future representation:

```yaml id="pg30"
id: ADR-0010
title: Adopt Prometheus and Grafana as Primary Metrics and Visualization Platform
status: accepted

domain:
  - observability
  - platform
  - sre

technologies:
  - prometheus
  - grafana
  - alertmanager

owner: platform-observability
implementation_status: implemented

related_adrs:
  - ADR-0001
  - ADR-0002
  - ADR-0009

alternatives:
  - zabbix
  - nagios
  - datadog

governance_capabilities:
  - slo-measurement
  - risk-indicators
  - compliance-evidence

supersedes: null
superseded_by: null
```

---

# 56. Related Documents

* ADR-0001-Kubernetes
* ADR-0002-ArgoCD-GitOps
* ADR-0009-Ollama-Local-AI
* Observability Architecture
* Metrics Architecture
* Dashboard Strategy
* Alerting Strategy
* SLI/SLO Monitoring
* Observability Governance
* Observability Operations
* Risk Management
* Compliance Governance
