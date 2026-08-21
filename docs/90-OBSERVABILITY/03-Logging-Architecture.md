# Logging Architecture

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the Logging Architecture of the Enterprise AI Platform.

It establishes how logs are generated, collected, enriched, transported, stored, queried, correlated, retained, secured, and governed across infrastructure, Kubernetes, applications, data services, and AI workloads.

The objective is to provide centralized and reliable log visibility for troubleshooting, incident response, security analysis, operational monitoring, and auditability.

---

# 2. Scope

This architecture applies to:

* Kubernetes
* Containers
* Infrastructure services
* Applications
* APIs
* PostgreSQL
* Airflow
* dbt workloads
* MLflow
* OpenMetadata
* Ollama
* AI services
* GitOps services
* CI/CD services
* Security-relevant events
* Platform services

---

# 3. Objectives

The logging platform aims to:

* Centralize logs
* Improve troubleshooting
* Support Root Cause Analysis
* Support incident response
* Correlate logs with metrics and traces
* Detect operational anomalies
* Support security investigations
* Preserve useful operational history
* Reduce unnecessary logging volume
* Protect sensitive information
* Standardize log structure

---

# 4. Logging Principles

The platform follows these principles:

* Centralize Logs
* Prefer Structured Logging
* Log Events, Not Everything
* Protect Sensitive Data
* Correlate Logs with Traces
* Use Bounded Labels
* Manage Retention Explicitly
* Avoid High-Cardinality Labels
* Keep Logs Searchable
* Manage Logging Configuration as Code
* Preserve Diagnostic Value
* Control Storage Consumption

---

# 5. High-Level Logging Architecture

```text
Applications
Kubernetes
Platform Services
Data Services
AI Services
      │
      ▼
stdout / stderr
      │
      ▼
Node Log Files
      │
      ▼
Promtail
      │
      ▼
Loki
      │
      ▼
Grafana
      │
      ▼
Operations / SRE / Security
```

This is the primary current logging flow.

---

# 6. Current Logging Stack

The current architecture uses:

| Capability            | Technology                |
| --------------------- | ------------------------- |
| Log Production        | Applications / Containers |
| Kubernetes Collection | Promtail                  |
| Centralized Storage   | Loki                      |
| Query Language        | LogQL                     |
| Visualization         | Grafana                   |
| Correlation           | Grafana + Tempo           |
| Deployment            | Kubernetes / GitOps       |

This provides a lightweight and Kubernetes-native centralized logging architecture.

---

# 7. Container Logging Model

Containers should write logs primarily to:

```text
stdout
stderr
```

Applications should avoid managing their own local rotating log files inside containers unless a specific requirement exists.

Kubernetes runtime logs can then be collected centrally.

---

# 8. Kubernetes Log Flow

Conceptual Kubernetes log flow:

```text
Pod
 │
 ▼
Container stdout/stderr
 │
 ▼
Container Runtime Log
 │
 ▼
Node Filesystem
 │
 ▼
Promtail
 │
 ▼
Loki
```

This model keeps application logging independent of the log backend.

---

# 9. Promtail

Promtail currently collects Kubernetes logs.

Responsibilities include:

* Discover log files
* Identify Kubernetes metadata
* Parse log records
* Attach selected labels
* Forward records to Loki

Promtail configuration should remain managed through GitOps.

---

# 10. Promtail Discovery

Promtail should automatically discover Kubernetes workloads where practical.

Useful Kubernetes metadata may include:

* Namespace
* Pod
* Container
* Application
* Node

Metadata should be carefully selected to avoid excessive label cardinality.

---

# 11. Loki

Loki provides centralized log storage and querying.

Loki differs from traditional full-text indexing systems by primarily indexing labels rather than every word contained in the log message.

This architecture can significantly reduce resource requirements when label design is controlled.

---

# 12. Loki Data Model

Each log stream is defined by a set of labels.

Example:

```text
{
  namespace="airflow",
  app="scheduler",
  container="scheduler"
}
```

The stream then contains individual log entries.

Label design is therefore a critical architectural concern.

---

# 13. Labels

Useful labels may include:

```text
namespace
application
service
environment
container
level
cluster
```

Labels should have relatively low and predictable cardinality.

---

# 14. Labels to Avoid

The following should generally not be Loki labels:

```text
request_id
trace_id
user_id
session_id
email
IP_address
order_id
prompt
timestamp
random_UUID
```

These values can generate extremely high-cardinality streams.

They should instead remain inside the structured log payload.

---

# 15. Structured Logging

Applications should prefer structured logging where practical.

Recommended example:

```json
{
  "timestamp": "2026-08-21T08:30:00Z",
  "level": "ERROR",
  "service": "business-api",
  "environment": "production",
  "trace_id": "81af431",
  "request_id": "req-101",
  "event": "database_query_failed",
  "message": "Database query failed"
}
```

Structured logs improve:

* Searching
* Filtering
* Correlation
* Automated processing
* Security analysis

---

# 16. Common Log Fields

Recommended application fields include:

```text
timestamp
level
service
environment
message
event
trace_id
request_id
version
```

Optional fields may include:

```text
duration_ms
status_code
component
operation
error_type
```

Sensitive values should not be included unnecessarily.

---

# 17. Timestamp

Logs should include timestamps using a consistent format.

Recommended:

```text
ISO 8601
UTC
```

Example:

```text
2026-08-21T08:30:00Z
```

Consistent timestamps are essential for cross-system correlation.

---

# 18. Log Levels

Recommended levels include:

## DEBUG

Detailed diagnostic information.

Use primarily during development or temporary troubleshooting.

## INFO

Normal application lifecycle and significant operational events.

## WARNING

Unexpected situation that does not currently prevent operation.

## ERROR

Operation failed or service functionality is affected.

## CRITICAL

Severe failure affecting service availability or integrity.

---

# 19. Production Logging Levels

Production should normally use:

```text
INFO
WARNING
ERROR
CRITICAL
```

`DEBUG` should be enabled temporarily and intentionally.

Excessive debug logging can create:

* Storage pressure
* CPU overhead
* Sensitive-data exposure
* Operational noise

---

# 20. Event-Oriented Logging

Applications should prefer meaningful events.

Better:

```text
event="user_authentication_failed"
```

Rather than:

```text
message="something happened"
```

Event-oriented logging makes dashboards, alerts, and searches more reliable.

---

# 21. Request Logging

API request logs may capture:

* Method
* Route
* Status code
* Duration
* Request ID
* Trace ID

Example:

```json
{
  "event": "http_request",
  "method": "GET",
  "route": "/properties",
  "status_code": 200,
  "duration_ms": 52,
  "trace_id": "abc123"
}
```

Do not unnecessarily log request payloads.

---

# 22. Error Logging

Errors should include enough context for investigation.

Useful fields:

* Error class
* Component
* Operation
* Trace ID
* Request ID
* Service version

Stack traces may be appropriate for unexpected server-side errors but should not be exposed to external clients.

---

# 23. Correlation IDs

A request should carry identifiers across dependent services.

Recommended identifiers include:

```text
trace_id
request_id
```

Example:

```text
Browser
  │
  ▼
API
trace_id=abc
  │
  ▼
Database call
trace_id=abc
  │
  ▼
AI request
trace_id=abc
```

This enables end-to-end investigation.

---

# 24. Logs and Distributed Tracing

Logs and traces should complement each other.

Example workflow:

```text
Grafana Metric
      │
      ▼
Tempo Trace
      │
      ▼
trace_id
      │
      ▼
Loki Logs
```

The shared trace identifier enables fast navigation between signals.

---

# 25. LogQL

LogQL is Loki's query language.

Basic example:

```logql
{namespace="airflow"}
```

Filtering:

```logql
{namespace="airflow"} |= "ERROR"
```

Structured JSON parsing:

```logql
{app="business-api"}
| json
| level="ERROR"
```

Operational queries should eventually be standardized for important services.

---

# 26. Log-Derived Metrics

Loki queries may derive rates from log events.

Example:

```logql
sum(
  rate(
    {app="business-api"} |= "authentication_failed" [5m]
  )
)
```

However, high-value numeric operational signals should usually be implemented directly as Prometheus metrics.

Logs should not replace proper metrics instrumentation.

---

# 27. Infrastructure Logs

Infrastructure logging may include:

* Operating-system events
* Kubernetes node errors
* Runtime errors
* Networking events
* Storage failures

Infrastructure logs complement node and Kubernetes metrics.

---

# 28. Kubernetes Logs

Important Kubernetes logging sources include:

* Application Pods
* Ingress Controller
* cert-manager
* Argo CD
* Airflow
* MLflow
* OpenMetadata
* Monitoring services

Kubernetes control-plane logging requirements should be defined according to available access and operational value.

---

# 29. NGINX Ingress Logs

Ingress logs provide visibility into external HTTP traffic.

Useful fields include:

* Host
* Route
* HTTP method
* Status
* Response time
* Upstream service
* Request ID

Ingress logs should not contain sensitive authorization headers.

---

# 30. Argo CD Logging

Argo CD logs support investigation of:

* Repository connectivity
* Synchronization failures
* Manifest errors
* Authentication issues
* Reconciliation failures

Argo CD logs are particularly useful when deployment state differs from Git.

---

# 31. Airflow Logging

Airflow logs are critical for Data Engineering operations.

Log sources include:

* Scheduler
* Webserver
* Tasks
* Workers
* DAG execution

Important events include:

* DAG failure
* Task failure
* Retry
* Dependency failure
* Data extraction failure
* Database errors

Task logs should be correlated with workflow metrics where possible.

---

# 32. dbt Logging

dbt logs may contain:

* Model execution
* Test failures
* Compilation problems
* Database errors
* Transformation duration

dbt test failures should integrate with Data Quality operations.

---

# 33. PostgreSQL Logging

PostgreSQL logs may provide:

* Authentication failures
* Connection errors
* Database startup/shutdown
* Deadlocks
* Slow queries where configured
* Errors
* Checkpoint information

Logging must be tuned carefully to avoid excessive volume.

---

# 34. OpenMetadata Logging

OpenMetadata logging supports diagnosis of:

* Metadata ingestion failures
* Search problems
* API errors
* Database connectivity
* Workflow failures

These logs complement OpenMetadata metadata and ingestion status.

---

# 35. MLflow Logging

MLflow logs should capture:

* API errors
* Registry failures
* Database failures
* Artifact storage failures
* Authentication issues
* Service startup

Experiment contents belong primarily in MLflow rather than platform logs.

---

# 36. AI Service Logs

AI inference logs may include:

* Model name
* Model version
* Request status
* Inference duration
* Token counts
* Failure reason
* Trace ID

Avoid logging:

* Full prompts by default
* Full generated responses
* Sensitive enterprise context
* Authentication tokens

AI logging must balance diagnostic value with privacy and security.

---

# 37. RAG Logging

Future RAG services may log:

* Retrieval request
* Retriever status
* Number of chunks retrieved
* Retrieval latency
* Reranker latency
* Source identifiers
* Failure events

Raw source content should not be unnecessarily duplicated into logs.

---

# 38. Agent Logging

Agentic workflows may require logs for:

* Agent started
* Plan created
* Tool selected
* Tool execution result
* Human approval requested
* Workflow failed
* Workflow completed

Detailed reasoning or hidden chain-of-thought should not be treated as an operational logging requirement.

Operationally relevant actions and decisions should instead be recorded explicitly.

---

# 39. Security Logs

Security-relevant events may include:

* Failed authentication
* Authorization failure
* Secret access failure
* RBAC modification
* Unexpected administrative action
* Deployment modification
* API abuse

Security logs should be retained according to security policy and operational requirements.

---

# 40. Sensitive Data

Logs must not intentionally expose:

* Passwords
* API keys
* Authentication tokens
* Session cookies
* Private keys
* Database passwords
* Secret environment variables

Additional care is required for:

* Personal information
* Legal documents
* Business-sensitive data
* AI prompts and outputs

---

# 41. Redaction

Applications should redact sensitive values before log emission.

Example:

Incorrect:

```text
Authorization: Bearer eyJ...
```

Correct:

```text
Authorization: [REDACTED]
```

Redaction should happen as close to the log source as possible.

---

# 42. Privacy

Logging must follow data minimization principles.

The question should be:

> Do we actually need this value to operate the service?

rather than:

> Can we technically log this value?

Operational need should determine collection.

---

# 43. Multiline Logs

Stack traces and some application outputs may span multiple lines.

Promtail pipelines should correctly group multiline events where necessary.

Without proper handling:

```text
one stack trace
```

may incorrectly become:

```text
20 unrelated log messages
```

Multiline configuration should therefore be tested for relevant workloads.

---

# 44. Parsing

Promtail may parse formats such as:

* JSON
* logfmt
* Regex
* Container runtime format

Structured application JSON is preferable because it reduces complex parsing requirements.

---

# 45. Pipeline Stages

Promtail processing may conceptually include:

```text
Read
 ↓
Parse
 ↓
Extract
 ↓
Label Selected Fields
 ↓
Redact / Transform
 ↓
Send to Loki
```

Not every parsed field should become a label.

---

# 46. Cardinality

Loki cardinality is heavily influenced by labels.

Dangerous:

```text
{user_id="128374"}
```

Better:

```text
{service="business-api", environment="prod"}
```

High-cardinality data should remain inside the log body.

---

# 47. Stream Explosion

Poor labels can create enormous numbers of streams.

Example:

```text
service
×
pod
×
container
×
request_id
×
user_id
```

This can lead to:

* Increased memory consumption
* Storage overhead
* Slow queries
* Operational instability

Label governance is therefore mandatory.

---

# 48. Retention

Log retention must reflect operational value and available storage.

Possible starting targets:

```text
Operational application logs   14–30 days
Debug logs                     Short-term only
Security logs                  Policy dependent
Historical diagnostic logs     As justified
```

The actual values should be based on measured storage growth.

---

# 49. Loki Storage Capacity

Loki storage consumption depends on:

* Log volume
* Retention
* Compression
* Number of streams
* Query patterns

Storage must be monitored continuously.

Alerts should be configured before disk pressure becomes critical.

---

# 50. Log Volume Budget

Applications should have reasonable logging expectations.

A service producing excessive logs should be investigated.

Possible causes include:

* Debug mode accidentally enabled
* Repeated errors
* Logging loops
* Excessive request payload logging
* Misconfigured retries

Logging volume itself can become an operational metric.

---

# 51. Query Performance

Loki queries should use selective labels before text filters.

Better:

```logql
{namespace="airflow", app="scheduler"} |= "ERROR"
```

Worse:

```logql
{} |= "ERROR"
```

Broad queries may consume significantly more resources.

---

# 52. Grafana Integration

Grafana provides the primary log query interface.

Dashboards should provide links from:

```text
Service
 ↓
Metrics
 ↓
Logs
```

and, where trace context exists:

```text
Logs
 ↓
Trace
```

This reduces investigation time.

---

# 53. Log Panels

Dashboards may include:

* Recent application errors
* Kubernetes errors
* Failed authentication
* Airflow failures
* Deployment errors

However dashboards should not simply display huge raw log streams.

Panels should answer specific operational questions.

---

# 54. Logging and Incident Management

Logs provide evidence during incident investigation.

Typical process:

```text
Alert
 ↓
Affected Service Identified
 ↓
Metrics Reviewed
 ↓
Logs Queried
 ↓
Trace Correlated
 ↓
Root Cause Identified
```

Important investigation queries should be captured in runbooks.

---

# 55. Logging and Problem Management

Historical logs help identify:

* Repeating exceptions
* Recurring dependency failures
* Periodic authentication failures
* Repeated scheduler errors
* Application error patterns

These support Root Cause Analysis.

---

# 56. Logging and Security Monitoring

Centralized logs provide a foundation for security investigations.

Future security analytics may identify:

* Brute-force attempts
* Repeated authorization failures
* Unexpected administrative operations
* Suspicious API use
* Unexpected deployment behavior

Loki currently provides operational log analytics rather than a full enterprise SIEM.

This distinction should remain explicit.

---

# 57. Logging and SRE

Logs help support SRE practices but should not become the primary SLI source.

SLIs should primarily use measurable metrics where possible.

Logs are better suited for:

* Diagnostics
* Investigation
* Event context
* Error analysis

---

# 58. GitOps

Logging configuration should be managed in Git.

Examples include:

* Promtail configuration
* Loki values
* Retention configuration
* Parsing pipelines
* Grafana log dashboards

Workflow:

```text
Git
 ↓
Review
 ↓
Argo CD
 ↓
Loki / Promtail
```

---

# 59. Configuration Changes

Logging configuration changes should be validated carefully.

Potential impact includes:

* Missing logs
* Increased storage
* Parsing failure
* Stream explosion
* Sensitive-data exposure

Significant logging changes should follow Change Management processes.

---

# 60. Logging Health Monitoring

The logging platform itself must be monitored.

Important indicators include:

* Promtail health
* Promtail errors
* Loki availability
* Ingestion failures
* Loki storage usage
* Query latency
* Dropped logs
* Stream count

Loss of log visibility should generate an operational warning.

---

# 61. Logging Failure Strategy

Application availability should not depend directly on Loki.

Architecture:

```text
Application
     │
     ├── Business Processing
     │
     └── stdout/stderr
              │
              ▼
          Logging Stack
```

If Loki becomes unavailable, critical application processing should continue where possible.

---

# 62. Backpressure

Telemetry infrastructure should avoid causing application failure through logging backpressure.

Applications should not synchronously wait for the centralized logging backend during normal request processing.

This keeps logging from becoming a critical runtime dependency.

---

# 63. Backup

Most operational logs do not require traditional backup if their retention is explicitly defined.

Higher-value log categories may require different treatment according to:

* Security policy
* Compliance
* Audit requirements

Logging configuration itself should be backed up through Git.

---

# 64. Current Implementation

Current logging capabilities include:

* Loki
* Promtail
* Kubernetes container logs
* Grafana log exploration
* Application logs
* Airflow logs
* Platform logs
* Centralized observability integration

This provides a strong centralized logging foundation.

---

# 65. Current Maturity

```text
Centralized Logging        → Strong
Kubernetes Log Collection  → Strong
Loki                       → Strong
Promtail                   → Strong
Grafana Integration        → Strong
Structured Application Logs→ Developing
Trace Correlation          → Developing
AI Logging Standards       → To Formalize
Retention Governance       → To Formalize
Security Log Analytics     → Developing
Cardinality Governance     → To Formalize
```

---

# 66. Resource Constraints

Logging operates on the existing fixed infrastructure.

Therefore:

* Log volume must be controlled
* Retention must be measured
* Debug logging must remain temporary
* High-cardinality labels must be avoided
* Low-value logs should not be retained indefinitely

Operational data must not compete unnecessarily with business, data, and AI workloads.

---

# 67. Future Evolution

Planned improvements include:

* Standard structured-log schema
* Broader trace ID propagation
* Log-to-trace correlation
* Application log libraries/templates
* Data-platform logging standards
* AI logging standards
* Security detection queries
* Log-volume dashboards
* Retention automation
* Sensitive-data redaction validation
* Logging checks in CI/CD
* Improved multiline parsing
* Centralized logging runbooks

---

# 68. Architecture Decisions

Key decisions include:

* Loki remains the centralized log backend
* Promtail remains the current Kubernetes log collector
* Applications primarily log to stdout/stderr
* Structured JSON logging is preferred for applications
* Kubernetes metadata is used selectively
* High-cardinality values must not become labels
* Sensitive information must not be logged
* Trace and request IDs remain log fields rather than Loki labels
* Logs support diagnostics, while Prometheus remains the primary SLI source
* Logging configuration is managed through GitOps
* Retention must reflect available storage
* Logging failures should not directly break business services
* Loki is an operational log platform, not currently a full enterprise SIEM

---

# 69. Related Documents

* Observability Architecture
* Metrics Architecture
* Distributed Tracing
* OpenTelemetry Architecture
* Dashboard Strategy
* Alerting Strategy
* SLI/SLO Monitoring
* Observability Governance
* Observability Operations
* Security Monitoring
* AI Observability
* Incident Management
* Problem Management
* SRE Practices
