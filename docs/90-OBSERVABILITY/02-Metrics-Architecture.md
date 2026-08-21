# Metrics Architecture

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the Metrics Architecture of the Enterprise AI Platform.

It establishes how quantitative telemetry is:

* Produced
* Exposed
* Discovered
* Collected
* Stored
* Aggregated
* Queried
* Visualized
* Alerted upon
* Governed

Prometheus is the primary metrics platform.

The architecture covers infrastructure, Kubernetes, applications, data workloads, AI services, and platform components.

---

# 2. Scope

The metrics architecture applies to:

* Physical and virtual infrastructure
* Kubernetes control plane
* Kubernetes worker nodes
* Containers
* Applications
* APIs
* PostgreSQL
* Airflow
* Data pipelines
* MLflow
* OpenMetadata
* Ollama
* AI inference services
* GPU workloads
* GitOps services
* CI/CD services
* Backup operations
* Platform services

---

# 3. Objectives

The metrics platform aims to:

* Provide reliable quantitative telemetry
* Detect service degradation
* Measure infrastructure utilization
* Measure application behavior
* Monitor Kubernetes health
* Monitor data workloads
* Monitor AI workloads
* Support capacity planning
* Support SLI/SLO measurement
* Support alerting
* Enable historical trend analysis
* Reduce Mean Time to Detect
* Support Root Cause Analysis

---

# 4. Architecture Principles

The metrics architecture follows these principles:

* Prometheus as the Primary Metrics Platform
* Pull-Based Collection by Default
* Service-Level Metrics Over Infrastructure-Only Metrics
* Standardized Metric Naming
* Controlled Label Cardinality
* Metrics Configuration as Code
* Actionable Metrics
* Resource-Aware Retention
* Aggregation Where Valuable
* Open Standards Where Practical
* Metrics Are Not Logs

---

# 5. High-Level Metrics Architecture

```text
Infrastructure
Kubernetes
Applications
Data Platform
AI Platform
     │
     ▼
Metrics Producers
     │
     ├── Native /metrics
     ├── Exporters
     ├── OpenTelemetry
     └── Pushgateway
     │
     ▼
Prometheus Discovery
     │
     ├── ServiceMonitor
     ├── PodMonitor
     └── Static / Additional Targets
     │
     ▼
Prometheus
     │
     ├── Raw Time Series
     ├── Recording Rules
     └── Alerting Rules
     │
     ├───────────────┐
     ▼               ▼
Grafana         Alertmanager
     │               │
     ▼               ▼
Dashboards       Operations
```

---

# 6. Prometheus

Prometheus is the authoritative operational time-series metrics engine.

Responsibilities include:

* Target discovery
* Metrics scraping
* Time-series storage
* PromQL queries
* Recording rules
* Alert rule evaluation
* Integration with Grafana
* Integration with Alertmanager

Prometheus should remain focused on numeric time-series telemetry.

Logs belong in Loki.

Traces belong in Tempo.

---

# 7. Prometheus Collection Model

Prometheus primarily uses a pull model.

```text
Prometheus
    │
    │ HTTP GET /metrics
    ▼
Target
    │
    ▼
Metrics Response
```

Example target:

```text
http://application:8080/metrics
```

Advantages include:

* Centralized discovery
* Centralized scrape control
* Target health visibility
* Simple failure detection
* Reduced application responsibility

---

# 8. Scrape Targets

Typical targets include:

```text
Kubernetes API
kube-state-metrics
node-exporter
Application APIs
Airflow
PostgreSQL Exporter
Ingress Controller
Argo CD
OpenTelemetry Collector
Custom Data Jobs
AI Services
GPU Exporters
```

Not every component requires a dedicated exporter if it already exposes Prometheus-compatible metrics.

---

# 9. Kubernetes Service Discovery

Prometheus should use Kubernetes-native service discovery where possible.

The Prometheus Operator provides abstractions such as:

```text
ServiceMonitor
PodMonitor
PrometheusRule
```

This allows monitoring configuration to follow Kubernetes workloads automatically.

---

# 10. ServiceMonitor

A `ServiceMonitor` defines how Prometheus discovers and scrapes Kubernetes Services.

Conceptual example:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: business-api
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: business-api
  namespaceSelector:
    matchNames:
      - production
  endpoints:
    - port: metrics
      path: /metrics
      interval: 30s
```

This configuration should be stored in Git.

---

# 11. PodMonitor

A `PodMonitor` can scrape Pods directly when a Service abstraction is unnecessary.

Example use cases:

* Specialized agents
* Per-Pod telemetry
* Internal workloads without Services

ServiceMonitor should generally be preferred where a stable service abstraction already exists.

---

# 12. Scrape Intervals

Scrape intervals should reflect operational requirements.

Example:

```text
Critical service metrics      15–30 seconds
Standard platform metrics     30–60 seconds
Slow-changing metrics         1–5 minutes
```

Shorter intervals increase:

* Storage consumption
* CPU usage
* Network traffic
* Query volume

Scrape frequency must therefore reflect actual operational value.

---

# 13. Node Metrics

`node-exporter` provides operating-system and host metrics.

Important indicators include:

* CPU utilization
* Load average
* Memory
* Swap
* Filesystem capacity
* Disk I/O
* Network traffic
* Network errors
* System uptime

Example metric:

```text
node_memory_MemAvailable_bytes
```

---

# 14. Kubernetes State Metrics

`kube-state-metrics` exposes Kubernetes object state.

Examples include:

* Deployment replicas
* Pod phases
* Node conditions
* StatefulSet status
* Job status
* PVC status
* Resource requests
* Resource limits

Example:

```text
kube_deployment_status_replicas_available
```

This complements resource metrics from nodes and containers.

---

# 15. Container Metrics

Container resource metrics may include:

* CPU usage
* Memory usage
* Network traffic
* Filesystem usage

These metrics help identify:

* Resource saturation
* Memory pressure
* CPU throttling
* Noisy workloads
* Capacity problems

---

# 16. Kubernetes Control Plane Metrics

Important control-plane indicators include:

* API server availability
* API request latency
* API errors
* Scheduler health
* Controller Manager health
* etcd health
* etcd latency

Control-plane monitoring is especially important because the platform operates a multi-control-plane Kubernetes architecture.

---

# 17. Application Metrics

Applications should expose metrics that describe user-facing behavior.

Recommended HTTP metrics include:

```text
http_requests_total
http_request_duration_seconds
http_requests_in_progress
```

Useful labels may include:

```text
method
route
status_code
service
```

Avoid using raw URLs containing dynamic IDs.

---

# 18. RED Method

Application monitoring should use the RED method where appropriate.

## Rate

How many requests are processed?

## Errors

How many requests fail?

## Duration

How long do requests take?

Example:

```text
Rate
+
Errors
+
Duration
=
Service Behavior
```

RED is particularly useful for APIs and microservices.

---

# 19. USE Method

Infrastructure resources may use the USE method.

## Utilization

How busy is the resource?

## Saturation

Is demand exceeding capacity?

## Errors

Is the resource experiencing failures?

USE is particularly useful for:

* CPU
* Memory
* Storage
* Network
* GPU

---

# 20. PostgreSQL Metrics

Database metrics should include:

* Database availability
* Active connections
* Connection utilization
* Query duration
* Transactions
* Locks
* Deadlocks
* Cache behavior
* Database size
* Replication state where applicable

A PostgreSQL exporter may expose these metrics to Prometheus.

Database monitoring must complement database logs and query analysis.

---

# 21. Airflow Metrics

Airflow metrics should cover:

* DAG execution count
* DAG failures
* Task failures
* Task retries
* Task duration
* Scheduler health
* Queue state
* Executor behavior

Critical DAGs should additionally expose business-level indicators.

---

# 22. Custom Pipeline Metrics

The platform already uses monitoring around ETL execution and row counts.

Custom metrics may include:

```text
etl_last_success_timestamp
etl_duration_seconds
etl_rows_processed_total
etl_failures_total
data_quality_checks_failed_total
```

These metrics allow operational monitoring of the data lifecycle.

---

# 23. Data Freshness Metrics

Data availability is not enough.

Data must also be sufficiently current.

Example:

```text
data_last_refresh_timestamp_seconds
```

Freshness can then be calculated:

```text
current_time
-
last_successful_refresh
=
data_age
```

This can become an SLI for critical analytical datasets.

---

# 24. Data Quality Metrics

Data quality metrics may include:

* Null violations
* Duplicate violations
* Schema failures
* Row-count anomalies
* Referential-integrity failures
* Validation success rate

Example:

```text
data_quality_checks_total
data_quality_checks_failed_total
```

These metrics bridge Data Engineering and SRE.

---

# 25. MLflow Metrics

MLflow itself should be monitored operationally.

Examples include:

* Service availability
* Request latency
* Request failures
* Backend database connectivity
* Artifact storage connectivity

Experiment metrics stored inside MLflow should not automatically be duplicated into Prometheus.

Prometheus monitors the service.

MLflow stores ML lifecycle information.

---

# 26. AI Inference Metrics

AI services should expose operational metrics including:

```text
ai_inference_requests_total
ai_inference_failures_total
ai_inference_duration_seconds
ai_requests_in_progress
```

Additional metrics may include:

* Prompt tokens
* Completion tokens
* Tokens per second
* Queue depth
* Model load duration
* Model version

---

# 27. AI Metric Labels

Useful bounded labels may include:

```text
model
endpoint
status
environment
```

Avoid labels such as:

```text
prompt
user_id
request_id
full_response
```

These create cardinality, privacy, and security problems.

Request-specific context belongs in traces and logs.

---

# 28. GPU Metrics

GPU monitoring should cover:

* GPU utilization
* GPU memory utilization
* Temperature
* Power where available
* Process utilization
* Errors

The current physical AI environment contains two NVIDIA GTX 1080 GPUs with 8 GB VRAM each.

Because GPU capacity is constrained, GPU saturation is a significant capacity and reliability signal.

---

# 29. GPU Exporter

A compatible NVIDIA metrics exporter may expose GPU telemetry to Prometheus where supported by the hardware and driver stack.

Conceptual flow:

```text
NVIDIA GPU
    │
    ▼
GPU Metrics Exporter
    │
    ▼
Prometheus
    │
    ▼
Grafana
```

Hardware and exporter compatibility must be validated before treating GPU telemetry as implemented.

---

# 30. Ollama Metrics

Where native Prometheus metrics are unavailable or insufficient, Ollama monitoring may use:

* Application instrumentation
* Reverse-proxy metrics
* OpenTelemetry instrumentation
* Synthetic requests
* Custom exporters

Important measurements include:

* Availability
* Inference latency
* Failure rate
* Request volume
* Model
* Queueing
* Token throughput

---

# 31. Pushgateway

Prometheus primarily expects scrapeable long-running targets.

Short-lived batch jobs present a different problem.

Pushgateway can be used selectively for service-level batch metrics.

Example:

```text
Batch Job
    │
    ▼
Pushgateway
    │
    ▼
Prometheus
```

Suitable examples include:

* ETL job completion
* Batch validation results
* Scheduled data processing

---

# 32. Pushgateway Limitations

Pushgateway should not become the default metrics transport.

Problems include:

* Stale metrics
* Lifecycle management
* Manual cleanup
* Loss of Prometheus pull semantics

It should therefore be limited to appropriate short-lived workloads.

---

# 33. Metric Types

Prometheus supports several important metric types.

## Counter

Monotonically increasing value.

Example:

```text
http_requests_total
```

## Gauge

Value that may increase or decrease.

Example:

```text
queue_depth
```

## Histogram

Distribution of observations.

Example:

```text
http_request_duration_seconds
```

## Summary

Client-side statistical observations.

Histograms are generally preferred where server-side aggregation across instances is required.

---

# 34. Metric Naming

Metrics should follow predictable naming conventions.

Recommended format:

```text
<namespace>_<subsystem>_<metric>_<unit>
```

Example:

```text
retail_etl_duration_seconds
```

Units should be included where relevant.

Preferred base units include:

```text
seconds
bytes
ratio
total
```

---

# 35. Counter Naming

Counters should generally use:

```text
_total
```

Example:

```text
api_requests_total
```

Avoid:

```text
api_number_of_requests
```

Standard conventions improve PromQL readability.

---

# 36. Label Strategy

Labels provide dimensions for metrics.

Example:

```text
http_requests_total{
    method="GET",
    route="/customers",
    status="200"
}
```

Labels should be:

* Bounded
* Predictable
* Operationally useful

---

# 37. Cardinality

Every unique combination of metric name and labels creates a time series.

Example:

```text
metric
×
method
×
route
×
status
×
instance
```

Poor label design can create thousands or millions of unnecessary series.

---

# 38. High-Cardinality Labels

Avoid:

```text
user_id
email
request_id
session_id
timestamp
UUID
full_url
prompt
```

These values may be nearly unique for every request.

They belong in logs or traces.

---

# 39. Cardinality Governance

Cardinality should be reviewed when introducing:

* New metrics
* New labels
* High-volume applications
* AI telemetry
* Dynamic endpoints

Prometheus resource consumption should be monitored as part of platform capacity management.

---

# 40. Recording Rules

Recording rules precompute frequently used PromQL expressions.

Example:

```yaml
groups:
  - name: api-recording
    rules:
      - record: service:http_requests:rate5m
        expr: rate(http_requests_total[5m])
```

Benefits include:

* Faster dashboards
* Standardized calculations
* Reduced repeated query complexity
* Reusable SLI calculations

---

# 41. Recording Rule Use Cases

Recording rules are especially valuable for:

* Request rates
* Error ratios
* Latency percentiles
* SLI calculations
* Resource utilization
* Data freshness
* Aggregated business metrics

Rules should be version controlled.

---

# 42. Alerting Rules

Prometheus evaluates alerting conditions.

Example:

```yaml
groups:
  - name: api-alerts
    rules:
      - alert: HighAPIErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) > 0.05
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "API error rate is above 5%"
```

Alert rules should focus on actionable service conditions.

---

# 43. PromQL

PromQL is the primary metrics query language.

Examples:

Request rate:

```promql
rate(http_requests_total[5m])
```

CPU usage:

```promql
rate(node_cpu_seconds_total{mode!="idle"}[5m])
```

Error ratio:

```promql
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

PromQL expressions used operationally should be standardized and documented.

---

# 44. Histogram Quantiles

Latency is better represented by distributions than simple averages.

Example:

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)
```

This estimates the 95th percentile latency.

Useful percentiles commonly include:

```text
P50
P90
P95
P99
```

---

# 45. Metrics and SLOs

Prometheus provides the measurement foundation for SLOs.

Example availability SLI:

```text
successful_requests
-------------------
total_requests
```

PromQL:

```promql
sum(rate(http_requests_total{status!~"5.."}[30d]))
/
sum(rate(http_requests_total[30d]))
```

SLO calculations should eventually use standardized recording rules.

---

# 46. Error Budget Metrics

Example:

```text
SLO target
     │
     ▼
Measured SLI
     │
     ▼
Error Budget Consumption
```

Grafana can visualize:

* Remaining error budget
* Burn rate
* Current SLI
* SLO target

This connects Prometheus directly with SRE practices.

---

# 47. Multi-Window Burn Rate

Future mature SLO alerting should prefer error-budget burn rates rather than only static availability thresholds.

Conceptually:

```text
Fast burn
→ immediate reliability risk

Slow burn
→ sustained reliability degradation
```

This reduces noisy alerts while detecting genuine SLO risk.

---

# 48. Grafana Integration

Grafana queries Prometheus using PromQL.

Recommended dashboard hierarchy:

```text
Platform Overview
        │
        ▼
Domain
        │
        ▼
Service
        │
        ▼
Component
```

Dashboards should reuse recording rules where practical.

---

# 49. Metric Correlation

Metrics should support correlation with other observability signals.

Example:

```text
High Error Rate
      │
      ▼
Prometheus
      │
      ▼
Grafana
      │
      ├── Loki Logs
      └── Tempo Traces
```

Metrics identify that something is wrong.

Logs and traces help explain why.

---

# 50. Deployment Correlation

Operational metrics should be correlated with changes.

Relevant sources include:

* GitLab pipelines
* Git commits
* Argo CD sync events
* Kubernetes rollouts
* MLflow model promotions

Example:

```text
Deployment
    │
    ▼
Latency Increase
    │
    ▼
Error Increase
```

This makes change-related regressions easier to identify.

---

# 51. Retention

Prometheus retention must balance operational history with available storage.

Example starting target:

```text
15–30 days
```

The actual value should be determined from:

* Time-series count
* Scrape frequency
* Available storage
* Growth rate
* Query requirements

Retention should be measured rather than selected arbitrarily.

---

# 52. Long-Term Metrics

The current architecture does not require a large distributed long-term metrics platform.

Future requirements may justify technologies such as:

* Thanos
* Mimir

They should not be introduced without a demonstrated requirement.

The current environment benefits more from operational simplicity and controlled resource usage.

---

# 53. Prometheus Storage Monitoring

Prometheus itself must be monitored.

Important indicators include:

* TSDB size
* Series count
* Sample ingestion rate
* Query latency
* Scrape failures
* Rule evaluation duration
* Disk utilization
* Memory consumption

Prometheus must not become a hidden platform resource bottleneck.

---

# 54. Prometheus Availability

For the current environment, observability architecture should remain proportionate to business requirements and available resources.

A fully distributed Prometheus architecture would introduce:

* Additional CPU
* Additional memory
* Additional storage
* Additional operational complexity

The platform should therefore prioritize reliable recovery and configuration-as-code before unnecessary observability clustering.

---

# 55. Metrics Security

Metrics endpoints may expose operational information.

Controls should include:

* Internal network exposure where possible
* Kubernetes NetworkPolicies
* RBAC
* TLS where appropriate
* Authentication where required
* Sensitive-label avoidance

Metrics must never contain credentials.

---

# 56. Metrics Privacy

Metrics should avoid unnecessary personal information.

Do not use labels containing:

* Names
* Email addresses
* User identifiers unless strictly controlled
* Raw prompts
* Business-sensitive free text

Aggregated operational information should be preferred.

---

# 57. Metrics as Code

Metrics configuration should be stored in Git.

Examples include:

```text
ServiceMonitor
PodMonitor
PrometheusRule
Grafana dashboard definitions
Exporter configuration
OpenTelemetry configuration
```

Workflow:

```text
Git
 ↓
Merge Request
 ↓
Validation
 ↓
Argo CD
 ↓
Kubernetes
 ↓
Prometheus
```

---

# 58. GitOps Repository Structure

A possible structure is:

```text
monitoring/

├── prometheus/
│   ├── servicemonitors/
│   ├── podmonitors/
│   ├── rules/
│   └── values.yaml
│
├── grafana/
│   └── dashboards/
│
├── loki/
├── tempo/
└── opentelemetry/
```

The final repository layout should remain aligned with the existing GitOps repository organization.

---

# 59. Metrics Testing

Metrics should be validated during application deployment.

Validation should confirm:

* `/metrics` endpoint reachable
* Target discovered
* Target `UP`
* Expected metrics present
* Labels correct
* No dangerous cardinality
* Dashboard queries functional
* Alerts evaluate correctly

---

# 60. Example Validation

Prometheus target health can be verified from Prometheus or using queries such as:

```promql
up
```

Specific service:

```promql
up{job="business-api"}
```

Expected:

```text
1 = Target reachable
0 = Target unavailable
```

---

# 61. Metrics Operational Runbook

When a metric disappears:

```text
1. Check application health
2. Check /metrics endpoint
3. Check Service
4. Check ServiceMonitor / PodMonitor
5. Check Prometheus target discovery
6. Check scrape error
7. Check network connectivity
8. Check relabeling
9. Check Prometheus health
```

This procedure should become part of Observability Operations.

---

# 62. Current Implementation

Current metrics capabilities include:

* Prometheus
* kube-prometheus-stack
* Grafana
* kube-state-metrics
* node-exporter
* Kubernetes metrics
* Pushgateway
* ETL metrics
* Row-count validation
* Airflow monitoring
* Application monitoring
* AI/API monitoring
* Prometheus alert rules

This provides a strong existing metrics foundation.

---

# 63. Current Maturity

```text
Prometheus                  → Strong
Infrastructure Metrics      → Strong
Kubernetes Metrics          → Strong
Application Metrics         → Implemented / Developing
Data Pipeline Metrics       → Implemented / Developing
Pushgateway                 → Implemented
AI Metrics                  → Developing
GPU Metrics                 → To Validate / Implement
Recording Rules             → Developing
Formal SLI Metrics          → To Implement
Error Budget Metrics        → To Implement
Cardinality Governance      → To Formalize
```

---

# 64. Resource Constraints

The platform operates on fixed physical infrastructure.

Metrics collection must therefore avoid unnecessary resource consumption.

Priority order:

```text
Business-critical metrics
        ↓
Platform reliability metrics
        ↓
Data / AI operational metrics
        ↓
Diagnostic metrics
        ↓
Low-value telemetry
```

Low-value metrics should not consume resources merely because they are technically available.

---

# 65. Future Evolution

Planned improvements include:

* Formal application metric standards
* GPU metrics
* Extended AI metrics
* SLI recording rules
* Error budget calculations
* Burn-rate alerts
* Data freshness SLIs
* Metrics validation in CI/CD
* Cardinality dashboards
* Prometheus capacity monitoring
* Deployment annotations
* Standardized service dashboards

Long-term distributed metrics storage should only be introduced when justified by measured requirements.

---

# 66. Architecture Decisions

Key decisions include:

* Prometheus remains the authoritative operational metrics engine
* Kubernetes-native discovery is preferred
* ServiceMonitor is preferred for stable Kubernetes services
* Pull-based metrics collection is the default
* Pushgateway is restricted to appropriate batch workloads
* RED is preferred for service monitoring
* USE is preferred for infrastructure resources
* Histograms are preferred for aggregatable latency measurements
* High-cardinality labels are prohibited
* Request-specific data belongs in logs and traces
* Prometheus retention is constrained by operational value and available resources
* Metrics configuration is managed through GitOps
* Long-term distributed metrics platforms are deferred until justified
* SLI/SLO measurements will build on standardized Prometheus metrics

---

# 67. Related Documents

* Observability Architecture
* Logging Architecture
* Distributed Tracing
* OpenTelemetry Architecture
* Dashboard Strategy
* Alerting Strategy
* SLI/SLO Monitoring
* Observability Governance
* Observability Operations
* AI Observability
* Capacity Management
* SRE Practices
