# Observability Operations

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the operational procedures used to run, maintain, troubleshoot, and continuously improve the observability platform of the Enterprise AI Platform.

It converts the observability architecture into concrete operational practices covering:

* Prometheus
* Grafana
* Loki
* Promtail
* Tempo
* OpenTelemetry Collector
* Alertmanager
* Metrics exporters
* Dashboards
* Alerting
* Telemetry pipelines

The objective is to ensure that the observability platform itself remains reliable and capable of detecting problems across the wider platform.

---

# 2. Scope

This document applies to:

* Prometheus
* Grafana
* Loki
* Promtail
* Tempo
* OpenTelemetry Collector
* Alertmanager
* kube-state-metrics
* node-exporter
* Pushgateway
* Application instrumentation
* Kubernetes telemetry
* Data telemetry
* AI telemetry
* Dashboards
* Alerts
* SLI/SLO monitoring

---

# 3. Objectives

Observability Operations aims to:

* Keep telemetry pipelines operational
* Detect observability failures
* Restore missing telemetry
* Control resource consumption
* Maintain dashboards
* Maintain alerts
* Validate telemetry after deployments
* Manage retention
* Troubleshoot collection problems
* Support incident investigation
* Preserve operational visibility during failures
* Reduce observability technical debt

---

# 4. Operational Principles

The platform follows these principles:

* Monitor the Monitoring Platform
* Validate Telemetry, Not Only Processes
* Restore Visibility Quickly
* Protect Business Workloads First
* Automate Repetitive Operations
* Troubleshoot Layer by Layer
* Prefer Configuration as Code
* Avoid Uncontrolled Telemetry Growth
* Record Operational Changes
* Review Observability Health Regularly

---

# 5. Operational Architecture

```text
Telemetry Producers
        │
        ▼
Collectors / Exporters
        │
        ▼
Observability Backends
        │
        ▼
Grafana / Alertmanager
        │
        ▼
Operations
        │
        ▼
Validation / Recovery / Improvement
```

Observability operations must verify every layer rather than assuming successful telemetry delivery.

---

# 6. Operational Responsibility

Logical responsibilities include:

## Platform Operations

Responsible for:

* Prometheus
* Grafana
* Loki
* Tempo
* OpenTelemetry Collector
* Alertmanager

## Application Teams

Responsible for:

* Application metrics
* Structured logs
* Trace instrumentation
* Application dashboards
* Service alerts

## Data Engineering

Responsible for:

* Airflow telemetry
* Pipeline metrics
* Data freshness
* Data quality alerts

## AI / MLOps

Responsible for:

* MLflow telemetry
* AI inference metrics
* GPU monitoring
* AI traces

One person may currently perform several logical roles.

---

# 7. Daily Operational Checks

Routine health checks should confirm:

```text
Prometheus healthy
Grafana healthy
Loki healthy
Tempo healthy
OpenTelemetry Collector healthy
Alertmanager healthy
Critical scrape targets UP
No critical telemetry storage pressure
No unexplained alert storms
```

These checks should increasingly be automated.

---

# 8. Prometheus Health

Validate Prometheus:

```bash
kubectl -n monitoring get pods
```

Identify Prometheus Pods and confirm:

```text
STATUS = Running
READY = expected containers
```

Check Prometheus service:

```bash
kubectl -n monitoring get svc
```

---

# 9. Prometheus Target Health

The most important Prometheus operational question is:

> Are expected targets being scraped successfully?

PromQL:

```promql
up
```

A healthy target normally reports:

```text
1
```

An unavailable scrape target reports:

```text
0
```

---

# 10. Critical Target Validation

Critical targets may include:

* Kubernetes API
* kube-state-metrics
* node-exporter
* Application APIs
* Airflow
* PostgreSQL exporter
* AI services

Missing critical targets should be investigated promptly.

---

# 11. Missing Metrics Troubleshooting

When expected metrics disappear:

```text
1. Confirm application is running
2. Confirm /metrics endpoint exists
3. Test endpoint manually
4. Verify Kubernetes Service
5. Verify ServiceMonitor / PodMonitor
6. Verify label selectors
7. Check Prometheus Targets
8. Check network connectivity
9. Inspect scrape errors
10. Verify metric name
```

Troubleshooting should proceed from producer toward backend.

---

# 12. Metrics Endpoint Validation

Example:

```bash
curl http://<service>:<port>/metrics
```

Expected result:

```text
Prometheus-compatible metrics
```

If the endpoint fails, Prometheus is not the primary problem.

---

# 13. ServiceMonitor Validation

Check resources:

```bash
kubectl get servicemonitor -A
```

Inspect:

```bash
kubectl -n <namespace> describe servicemonitor <name>
```

Verify:

* Labels
* Selector
* Namespace selector
* Port name
* Path
* Interval

A common failure is mismatch between Service labels and ServiceMonitor selectors.

---

# 14. PodMonitor Validation

Check:

```bash
kubectl get podmonitor -A
```

Ensure Pod labels and monitored ports match the PodMonitor configuration.

---

# 15. Prometheus Resource Monitoring

Prometheus itself should be monitored for:

* CPU
* Memory
* Disk
* Series count
* Ingestion rate
* Query duration
* Rule evaluation duration

Observability operations should detect telemetry-induced resource exhaustion before Prometheus becomes unstable.

---

# 16. Prometheus Storage Pressure

When Prometheus storage approaches capacity:

1. Confirm disk usage.
2. Check retention configuration.
3. Check series growth.
4. Identify high-cardinality metrics.
5. Check recent instrumentation changes.
6. Reduce unnecessary telemetry if required.
7. Increase storage only where justified.

Do not immediately increase retention or storage without understanding growth.

---

# 17. Series Growth Investigation

Potential causes include:

* New labels
* Dynamic IDs
* User identifiers
* Request IDs
* Full URLs
* New exporters
* Unbounded AI dimensions

Cardinality problems should be corrected at the telemetry source or collection layer.

---

# 18. Prometheus Rule Health

Validate rules:

```bash
kubectl get prometheusrule -A
```

Operational checks should identify:

* Invalid rules
* Expensive rules
* Missing rules
* Unexpected alert state

Rule evaluation failures represent observability degradation.

---

# 19. Grafana Health

Check:

```bash
kubectl -n monitoring get pods
```

Verify Grafana availability and data-source connectivity.

If Grafana fails but Prometheus, Loki, and Tempo remain healthy, telemetry still exists.

This distinction matters during recovery.

---

# 20. Grafana Data Source Troubleshooting

When a dashboard shows no data:

1. Check dashboard query.
2. Check selected time range.
3. Check variables.
4. Test data source directly.
5. Verify Prometheus/Loki/Tempo availability.
6. Check metric or log existence.
7. Check dashboard version.

Do not assume the telemetry backend failed because a panel is empty.

---

# 21. Broken Dashboard Troubleshooting

Common causes include:

* Metric renamed
* Label renamed
* Dashboard variable broken
* Recording rule removed
* Namespace changed
* Service renamed
* Incorrect time range

Dashboard changes should be correlated with Git history.

---

# 22. Loki Health

Validate Loki Pods:

```bash
kubectl get pods -A | grep loki
```

Check:

* Pod health
* Storage
* Ingestion
* Query functionality

Loki failure should generate monitoring alerts.

---

# 23. Promtail Health

Validate Promtail:

```bash
kubectl get pods -A | grep promtail
```

Because Promtail typically runs across nodes, missing Pods may mean logs from an entire node are not being collected.

---

# 24. Missing Logs Troubleshooting

When logs disappear:

```text
1. Confirm application writes stdout/stderr
2. Check container logs with kubectl logs
3. Confirm Promtail runs on node
4. Check Promtail configuration
5. Check Promtail errors
6. Verify Loki connectivity
7. Verify labels
8. Query Loki directly
```

---

# 25. Container Log Validation

Example:

```bash
kubectl -n <namespace> logs <pod>
```

If logs appear here but not in Loki, investigate collection.

If logs do not appear here, investigate the application.

---

# 26. Promtail Troubleshooting

Inspect Promtail logs:

```bash
kubectl -n <namespace> logs <promtail-pod>
```

Look for:

* Loki connection failures
* Parsing errors
* Permission errors
* File discovery problems
* Dropped entries

---

# 27. Loki Storage Pressure

If Loki approaches capacity:

1. Measure storage growth.
2. Identify high-volume services.
3. Check DEBUG logging.
4. Review retention.
5. Check label explosion.
6. Review recent application changes.
7. Reduce low-value logging.

Increasing storage without addressing excessive log volume can hide the underlying problem.

---

# 28. Excessive Logging

Potential signs include:

* Sudden Loki growth
* Increased Promtail bandwidth
* Large application log volumes
* Repeated identical messages

Likely causes include:

* Debug logging
* Retry loops
* Exception loops
* Misconfigured health checks
* Excessive request logging

---

# 29. Tempo Health

Validate Tempo:

```bash
kubectl get pods -A | grep tempo
```

Check:

* Availability
* Trace ingestion
* Storage
* Query response

Tempo health should be visible in the monitoring platform.

---

# 30. Missing Trace Troubleshooting

When traces are absent:

```text
1. Confirm application instrumentation
2. Confirm trace created
3. Confirm OTLP endpoint
4. Check Collector health
5. Check Collector pipeline
6. Check export errors
7. Check Tempo ingestion
8. Search correct time range
9. Verify sampling
```

Sampling must always be considered before declaring telemetry loss.

---

# 31. Trace Context Problems

If a request appears as multiple independent traces:

Investigate:

* `traceparent` propagation
* HTTP client instrumentation
* Framework middleware
* Proxy behavior
* Unsupported client libraries

Broken propagation reduces end-to-end visibility.

---

# 32. OpenTelemetry Collector Health

Check Collector Pods:

```bash
kubectl get pods -A | grep otel
```

Then inspect logs:

```bash
kubectl -n <namespace> logs <collector-pod>
```

---

# 33. Collector Operational Metrics

Monitor:

* Received telemetry
* Exported telemetry
* Dropped telemetry
* Export errors
* Queue depth
* CPU
* Memory

Collector Pod `Running` status alone does not guarantee telemetry delivery.

---

# 34. Collector Export Failures

Possible causes:

* Tempo unavailable
* Network failure
* TLS error
* Incorrect endpoint
* Authentication problem
* Backend overload

Collector errors should be correlated with backend health.

---

# 35. Collector Memory Pressure

If memory grows unexpectedly:

1. Check telemetry volume.
2. Check exporter failure.
3. Check queues.
4. Check batch configuration.
5. Check sampling.
6. Check new instrumentation.
7. Validate memory limiter.

Unbounded queues should be avoided.

---

# 36. Alertmanager Health

Validate:

```bash
kubectl -n monitoring get pods
```

Confirm Alertmanager is running and receiving alerts.

---

# 37. Alert Delivery Troubleshooting

When an expected notification does not arrive:

```text
1. Check Prometheus rule
2. Verify alert expression
3. Confirm alert is firing
4. Check Alertmanager
5. Check routing
6. Check inhibition
7. Check silences
8. Check notification integration
```

Each layer must be validated independently.

---

# 38. Unexpected Alert Storm

During an alert storm:

1. Identify common root alert.
2. Check infrastructure dependency.
3. Verify grouping.
4. Verify inhibition.
5. Silence only where required.
6. Resolve root issue.
7. Review alert rules afterward.

Do not permanently silence noisy alerts during the incident.

---

# 39. Alert Silence Operations

Silences should include:

* Owner
* Reason
* Scope
* Expiration

Example reasons:

* Planned maintenance
* Controlled recovery test
* Known temporary issue

Expired conditions should automatically become visible again.

---

# 40. Observability After Deployment

Every important deployment should validate telemetry.

Checklist:

```text
Application Running
Metrics Present
Logs Present
Trace Present
Dashboard Working
Alerts Healthy
No Telemetry Explosion
```

Observability verification should become part of deployment validation.

---

# 41. Application Observability Smoke Test

Example:

1. Send test request.
2. Confirm response.
3. Check request metric.
4. Check application log.
5. Find trace.
6. Verify dashboard.
7. Verify service version.

This confirms all three telemetry signals.

---

# 42. Data Pipeline Validation

After Airflow or ETL changes:

Validate:

* DAG metrics
* Task logs
* Pipeline duration
* Row counts
* Data freshness
* DQ results
* Relevant alerts

A successful code deployment does not prove observable pipeline operation.

---

# 43. AI Observability Validation

After AI service deployment:

Verify:

* AI endpoint health
* Inference metric
* Inference log
* Trace
* Model identifier
* GPU telemetry where available
* Latency
* Failure metric

This ensures AI services remain operationally visible.

---

# 44. Dashboard Maintenance

Operational dashboard maintenance includes:

* Fix broken queries
* Remove obsolete panels
* Update variables
* Validate data sources
* Review thresholds
* Review default time ranges
* Retire unused dashboards

Critical dashboards require ownership.

---

# 45. Alert Maintenance

Regular alert maintenance should include:

* Remove false positives
* Add missing alerts
* Update runbooks
* Review thresholds
* Review severity
* Review routing
* Review inhibition

Alert quality should continuously improve.

---

# 46. Recording Rule Maintenance

Recording rules should be reviewed for:

* Usage
* Query performance
* Accuracy
* Naming
* Dependency on deprecated metrics

Unused complex rules may consume resources without operational value.

---

# 47. Retention Operations

Retention should be monitored rather than configured once and forgotten.

Review:

* Prometheus growth
* Loki growth
* Tempo growth
* Available storage
* Operational investigation requirements

Retention should be adjusted only with evidence.

---

# 48. Capacity Review

Observability capacity review should evaluate:

```text
CPU
Memory
Storage
Metric Series
Log Ingestion
Trace Ingestion
Query Load
```

Growth trends should be tracked.

---

# 49. Resource Prioritization

If observability causes resource contention:

Priority is:

```text
Core Business Workloads
        >
Critical Data Services
        >
Critical AI Services
        >
Core Observability
        >
Diagnostic Telemetry Detail
```

Reduce telemetry detail before degrading essential business services.

---

# 50. Observability Backup

Critical observability configuration should primarily be recovered from Git.

Examples:

* Prometheus rules
* Grafana dashboards
* Loki configuration
* Tempo configuration
* OpenTelemetry configuration
* Alertmanager configuration

Historical telemetry receives lower recovery priority.

---

# 51. Observability Disaster Recovery

Recommended recovery order:

```text
Prometheus
    │
    ▼
Alertmanager
    │
    ▼
Grafana
    │
    ▼
Loki
    │
    ▼
Tempo
    │
    ▼
OpenTelemetry Collection
```

The exact sequence may vary based on deployment dependencies.

The core objective is to regain visibility early during platform recovery.

---

# 52. Prometheus Recovery

Recovery should use GitOps definitions where practical.

Validate after restoration:

```promql
up
```

Then verify:

* Targets
* Rules
* Alerts
* Storage
* Grafana connectivity

---

# 53. Grafana Recovery

Restore:

* Grafana deployment
* Data-source provisioning
* Dashboard definitions
* Authentication configuration

Dashboards managed as code should automatically return through GitOps.

---

# 54. Loki Recovery

Priority is restoring current log ingestion.

Historical logs may be restored where required by policy.

Validate:

* Promtail connectivity
* New log ingestion
* Query functionality

---

# 55. Tempo Recovery

Restore trace ingestion and Grafana connectivity.

Historical traces generally receive lower recovery priority than current operational trace capability.

---

# 56. Collector Recovery

After Collector restoration:

Verify:

* OTLP endpoints
* Receivers
* Processors
* Exporters
* Backend connectivity
* No dropped telemetry

---

# 57. Configuration Change Procedure

Observability changes should follow:

```text
Modify Git
   │
   ▼
Review
   │
   ▼
Validate
   │
   ▼
Merge
   │
   ▼
Argo CD
   │
   ▼
Observe Change
```

Manual production configuration should be minimized.

---

# 58. Emergency Changes

During an incident, temporary changes may be required.

Examples:

* Enable debug logging
* Increase trace sampling
* Add temporary alert
* Silence known secondary alerts

Temporary changes should be:

* Documented
* Time-limited
* Reverted after investigation
* Converted to Git-managed configuration if retained

---

# 59. Debug Logging Procedure

When temporary DEBUG logging is required:

1. Define affected service.
2. Define duration.
3. Estimate log-volume impact.
4. Enable logging.
5. Perform investigation.
6. Disable DEBUG.
7. Verify Loki storage impact.

Do not leave temporary debug configuration permanently enabled.

---

# 60. Increased Trace Sampling

Temporary high trace sampling may be useful during complex incidents.

Before enabling:

* Check Tempo capacity
* Check Collector capacity
* Limit affected service
* Define duration

Restore normal sampling after investigation.

---

# 61. Runbooks

Core observability runbooks should include:

```text
Prometheus Down
Prometheus Target Missing
Prometheus Storage Pressure
Loki Down
Missing Logs
Loki Storage Pressure
Tempo Down
Missing Traces
Collector Failure
Grafana Down
Alertmanager Failure
Alert Storm
```

Runbooks should contain diagnosis and validation steps.

---

# 62. Incident Integration

Observability incidents follow normal Incident Management.

Example:

```text
Prometheus unavailable
        │
        ▼
Monitoring blind spot
        │
        ▼
Operational incident
```

Severity depends on duration and loss of critical visibility.

---

# 63. Problem Management Integration

Repeated observability failures should generate Problem Management activity.

Examples:

* Recurrent Prometheus OOM
* Loki storage exhaustion
* Collector overload
* Repeated missing application telemetry
* Frequent dashboard failures

Recurring symptoms should not be repeatedly patched without root-cause analysis.

---

# 64. Weekly Operational Review

Recommended review topics:

* Critical scrape failures
* Alert volume
* Broken dashboards
* Storage usage
* Log growth
* Trace growth
* Collector errors
* Unowned observability issues

The cadence may be adapted to actual platform usage.

---

# 65. Monthly Observability Review

Recommended topics include:

* Capacity trends
* Retention
* High-cardinality metrics
* High-volume logs
* Alert quality
* Dashboard quality
* Missing service coverage
* Observability technical debt

---

# 66. Quarterly Architecture Review

Review:

* Tooling suitability
* Telemetry standards
* OpenTelemetry adoption
* SLI/SLO maturity
* AI observability
* Storage requirements
* Governance compliance

Architectural complexity should only increase when justified.

---

# 67. Operational Metrics

The observability platform should measure its own effectiveness.

Potential indicators include:

```text
Scrape Success Rate
Telemetry Drop Rate
Alert Delivery Success
Dashboard Availability
Collector Export Success
Prometheus Storage Growth
Loki Ingestion Rate
Tempo Ingestion Rate
```

---

# 68. Observability Coverage

Operations should maintain visibility into which services have:

* Metrics
* Logs
* Traces
* Dashboards
* Alerts
* SLOs
* Runbooks

Coverage gaps become explicit technical debt.

---

# 69. Current Implementation

Current operational capabilities include:

* Prometheus
* Grafana
* Loki
* Promtail
* Tempo
* OpenTelemetry Collector
* Alertmanager
* kube-prometheus-stack
* node-exporter
* kube-state-metrics
* Pushgateway
* ETL monitoring
* Row-count monitoring
* Application monitoring
* AI/API monitoring
* GitOps

This provides a strong operational foundation.

---

# 70. Current Maturity

```text
Prometheus Operations       → Strong
Grafana Operations          → Strong
Loki Operations             → Strong
Tempo Operations            → Implemented / Developing
Collector Operations        → Developing
Alert Operations            → Strong / Developing
Telemetry Smoke Tests       → To Formalize
Observability Runbooks      → To Formalize
Capacity Reviews            → Developing
Coverage Reviews            → To Implement
SLO Operations              → To Implement
```

---

# 71. Physical Resource Constraints

Observability operations must remain aligned with the fixed physical infrastructure.

Therefore:

* Telemetry volume must be actively managed
* Retention must be controlled
* Cardinality must be monitored
* Debug logging must remain temporary
* Trace sampling must remain proportionate
* Observability scaling must not assume immediate hardware expansion

Operational discipline is preferred over unnecessary infrastructure growth.

---

# 72. Future Evolution

Planned improvements include:

* Formal observability runbooks
* Automated telemetry smoke tests
* Prometheus cardinality dashboard
* Loki volume dashboard
* Collector drop-rate monitoring
* Automated dashboard validation
* Alert quality dashboards
* Observability coverage matrix
* SLO operational reviews
* Automated configuration validation
* Recovery exercises for observability components
* Deployment telemetry checks in CI/CD

---

# 73. Architecture Decisions

Key operational decisions include:

* The observability stack monitors itself
* Missing telemetry is treated as an operational failure
* Troubleshooting follows producer-to-backend flow
* Configuration is recovered primarily from Git
* Historical telemetry has lower DR priority than current visibility
* Debug telemetry is temporary and controlled
* Telemetry validation is part of deployment validation
* Observability resource consumption must remain bounded
* Recurring observability issues enter Problem Management
* Operational reviews continuously improve telemetry quality

---

# 74. Related Documents

* Observability Architecture
* Metrics Architecture
* Logging Architecture
* Distributed Tracing
* OpenTelemetry Architecture
* Dashboard Strategy
* Alerting Strategy
* SLI/SLO Monitoring
* Observability Governance
* Incident Management
* Problem Management
* Capacity Management
* Disaster Recovery
* SRE Practices
