# ADR-0011 — Adopt Loki, Tempo, and OpenTelemetry for Centralized Logs and Distributed Tracing

**Status:** Accepted
**Date:** 2026-08-21
**Decision Owner:** Bastri Murad
**Domain:** Observability / Platform / SRE
**Project:** Enterprise AI Platform
**Related ADRs:** ADR-0001, ADR-0002, ADR-0010
**Related Technologies:** Loki, Promtail, Tempo, OpenTelemetry, Grafana, Prometheus
**Supersedes:** None
**Superseded By:** None

---

# 1. Context

The Enterprise AI Platform requires more than metrics alone.

Prometheus provides time-series metrics and alert evaluation, but operators also need to understand:

* What happened inside a service
* Which error occurred
* Which request failed
* Which dependency introduced latency
* How a request crossed multiple services
* What sequence of operations led to failure

The platform therefore requires dedicated capabilities for:

* Centralized logging
* Distributed tracing
* Cross-signal correlation
* Standard telemetry instrumentation

The architecture should remain open-source, local, Kubernetes-aligned, and resource-aware.

---

# 2. Problem

A metrics-only observability model can answer:

```text
Is the service unhealthy?
```

but often cannot answer:

```text
Why is the service unhealthy?
```

The platform therefore requires complementary observability signals:

```text
Metrics
+
Logs
+
Traces
```

These signals must integrate with the existing Prometheus/Grafana stack rather than creating separate disconnected monitoring silos.

---

# 3. Decision

The platform will use:

* **Loki** as the centralized log backend
* **Promtail** as the current Kubernetes log collector
* **Tempo** as the distributed tracing backend
* **OpenTelemetry** as the preferred vendor-neutral instrumentation and telemetry collection standard
* **Grafana** as the unified exploration interface

The architecture becomes:

```text
Applications / Kubernetes
        │
        ├── Metrics ───────────────► Prometheus
        │
        ├── Logs ─► Promtail ─────► Loki
        │
        └── Traces ─► OTel ───────► Tempo
                                      │
                                      ▼
                                   Grafana
```

Specialized backends remain responsible for their respective telemetry types.

---

# 4. Architecture Principle

The platform deliberately chooses:

> Standardized instrumentation with specialized telemetry backends.

Rather than:

> Forcing metrics, logs, and traces into a single generic storage system.

This provides clearer responsibilities and allows each backend to use a data model optimized for its signal type.

---

# 5. Current Implementation

The platform already operates:

* Loki
* Promtail
* Tempo
* OpenTelemetry Collector
* Grafana
* Prometheus

Current state:

```text
IMPLEMENTED
```

The observability architecture therefore already contains the core technical components defined by this ADR.

---

# 6. Alternatives Considered

## Option 1 — Loki + Tempo + OpenTelemetry

Advantages:

* Open source
* Strong Grafana integration
* Kubernetes friendly
* Local deployment
* Relatively resource-efficient
* Vendor-neutral instrumentation
* Strong logs-to-traces correlation
* Integrates with existing Prometheus stack

Disadvantages:

* Several components must be operated
* Retention must be governed
* Telemetry configuration can become complex
* OpenTelemetry maturity varies by language/integration

Selected.

---

## Option 2 — Elasticsearch / OpenSearch for Logs

Advantages:

* Powerful search
* Mature ecosystem
* Rich full-text indexing

Disadvantages:

* Higher resource consumption
* Existing platform already uses Loki effectively
* Search indexing is unnecessary for many Kubernetes log use cases
* Additional storage/operations burden

Not selected as the primary logging backend.

OpenSearch remains used where required by other platform services such as OpenMetadata.

---

## Option 3 — Jaeger for Distributed Tracing

Advantages:

* Mature
* Widely used
* Strong tracing capabilities

Disadvantages:

* Tempo integrates more naturally with the existing Grafana stack
* Additional backend would provide little current benefit
* Avoid unnecessary observability duplication

Not selected.

---

## Option 4 — SaaS Unified Observability Platform

Examples:

* Datadog
* New Relic
* Splunk

Advantages:

* Managed service
* Unified interface
* Advanced analytics

Disadvantages:

* External telemetry transfer
* Recurring cost
* Vendor lock-in
* Data-sovereignty considerations
* Existing local stack already satisfies current requirements

Not selected as the default architecture.

---

# 7. Decision Criteria

The decision considered:

| Criterion              | Importance |
| ---------------------- | ---------: |
| Local deployment       |   Critical |
| Kubernetes integration |   Critical |
| Grafana integration    |       High |
| Logging capability     |   Critical |
| Distributed tracing    |   Critical |
| Open standards         |       High |
| Resource efficiency    |       High |
| GitOps compatibility   |       High |
| Data sovereignty       |       High |
| Vendor independence    |       High |

The selected stack provides the strongest fit.

---

# 8. Loki Role

Loki provides centralized log storage and query.

Responsibilities include:

* Log ingestion
* Label-indexed log streams
* LogQL
* Grafana integration
* Centralized Kubernetes log exploration

Loki is intentionally optimized around labels rather than full indexing of all log content.

---

# 9. Promtail Role

Promtail currently collects Kubernetes logs.

Conceptual flow:

```text
Container stdout/stderr
        │
        ▼
Node log files
        │
        ▼
Promtail
        │
        ▼
Loki
```

Promtail handles:

* Discovery
* Parsing
* Metadata enrichment
* Label assignment
* Loki forwarding

---

# 10. Log Collection Standard

Applications should primarily write to:

```text
stdout
stderr
```

rather than maintaining arbitrary internal container log files.

This enables centralized collection through the Kubernetes logging model.

---

# 11. Structured Logging

Applications should progressively use structured logs.

Example:

```json
{
  "timestamp": "2026-08-21T09:30:00Z",
  "level": "ERROR",
  "service": "business-api",
  "trace_id": "abc123",
  "event": "database_timeout",
  "message": "Database request timed out"
}
```

This improves correlation and automated analysis.

---

# 12. Loki Label Governance

Loki labels must remain bounded.

Recommended:

```text
service
namespace
environment
container
```

Avoid:

```text
request_id
trace_id
user_id
session_id
uuid
```

High-cardinality identifiers belong in the log payload.

---

# 13. Log Retention

Log retention must remain explicit.

A reasonable starting operational window may be:

```text
14–30 days
```

depending on:

* Available storage
* Log volume
* Security requirements
* Investigation needs

Retention should be tuned from actual usage.

---

# 14. Tempo Role

Tempo provides distributed trace storage and retrieval.

A trace represents the execution path of one distributed operation.

Example:

```text
HTTP Request
   │
   ├── FastAPI
   │    ├── PostgreSQL
   │    └── AI Service
   │         ├── Retrieval
   │         └── Ollama
   │
   ▼
Response
```

Tempo allows these operations to be viewed as one logical request.

---

# 15. Span Model

Each meaningful operation becomes a span.

Examples:

```text
http.request
postgres.query
rag.retrieve
embedding.generate
ollama.generate
```

Spans should represent operationally meaningful boundaries.

---

# 16. Trace Context

The platform should use standard trace propagation.

Preferred standard:

```text
W3C Trace Context
```

Typical propagation header:

```text
traceparent
```

This allows independently implemented services to participate in the same trace.

---

# 17. OpenTelemetry Role

OpenTelemetry provides the standard instrumentation and collection model.

It is used for:

* Tracing APIs
* SDKs
* Auto-instrumentation
* Resource metadata
* Context propagation
* OTLP telemetry transport
* Collector processing

OpenTelemetry reduces direct coupling between applications and Tempo.

---

# 18. OpenTelemetry Architecture

```text
Application
    │
    ▼
OpenTelemetry SDK
    │
    ▼
OTLP
    │
    ▼
OpenTelemetry Collector
    │
    ▼
Tempo
```

Applications should not require Tempo-specific instrumentation.

---

# 19. OpenTelemetry Collector

The Collector provides a centralized telemetry-processing layer.

Responsibilities include:

* Receive telemetry
* Batch telemetry
* Enrich metadata
* Filter telemetry
* Apply sampling
* Export telemetry

This creates a controlled point for observability governance.

---

# 20. Collector Pipelines

Conceptually:

```text
Receiver
   │
   ▼
Processor
   │
   ▼
Exporter
```

For traces:

```text
OTLP
 ↓
Memory Limiter
 ↓
Resource Enrichment
 ↓
Batch
 ↓
Tempo
```

---

# 21. Semantic Conventions

OpenTelemetry semantic conventions should be used where available.

Examples:

```text
service.name
service.version
http.request.method
http.response.status_code
db.system
```

Standard attributes reduce inconsistent telemetry naming.

---

# 22. Service Identity

Every instrumented service should define a stable:

```text
service.name
```

Example:

```text
service.name=business-api
```

Service identity should remain consistent across:

* Prometheus
* Loki
* Tempo
* Grafana

---

# 23. Cross-Signal Correlation

The target model is:

```text
Prometheus
   │
   ▼
Metric Indicates Failure
   │
   ▼
Tempo Trace
   │
   ▼
Slow / Failed Span
   │
   ▼
Loki Logs
```

This is the central reason for integrating the observability signals.

---

# 24. Logs-to-Traces Correlation

Application logs should include trace identifiers where practical.

Example:

```json
{
  "trace_id": "abc123",
  "service": "business-api",
  "message": "AI request timeout"
}
```

Grafana can then link the log event with the corresponding Tempo trace.

---

# 25. Metrics-to-Traces Correlation

Prometheus histograms may use exemplars where supported.

Conceptually:

```text
High Latency Point
      │
      ▼
Trace ID
      │
      ▼
Tempo Trace
```

This allows rapid investigation from aggregate metrics into specific requests.

---

# 26. Grafana Role

Grafana provides one user-facing observability environment while specialized backends remain independent.

```text
Grafana
 │
 ├── Prometheus
 ├── Loki
 └── Tempo
```

This gives operators a unified experience without requiring a monolithic storage platform.

---

# 27. Why Not One Backend for Everything

Metrics, logs, and traces have fundamentally different access and storage patterns.

Metrics require:

* Efficient time-series aggregation

Logs require:

* Event and text exploration

Traces require:

* Distributed execution relationships

Specialized backends therefore provide better operational alignment.

---

# 28. AI Tracing

AI workloads particularly benefit from tracing.

Example:

```text
ai.request
   │
   ├── validation
   ├── prompt.build
   ├── retrieval
   ├── ollama.generate
   └── response.validation
```

This distinguishes AI inference delay from retrieval, network, or application delay.

---

# 29. RAG Tracing

Future RAG tracing should expose:

```text
rag.request
   │
   ├── embedding.generate
   ├── vector.search
   ├── rerank
   ├── context.build
   └── llm.generate
```

This provides end-to-end AI observability without logging full sensitive document contents.

---

# 30. Sensitive Telemetry

Logs and traces must not intentionally capture:

* Passwords
* API keys
* Tokens
* Private keys
* Full sensitive documents
* Raw personal information
* Full AI prompts by default
* Full AI responses by default

Telemetry minimization is mandatory.

---

# 31. AI Prompt Logging

Full prompt logging is not enabled as a general observability requirement.

Operational metadata should instead capture:

* Model
* Request status
* Duration
* Trace ID
* Prompt version where relevant
* Token count where supported

This balances diagnosis with privacy.

---

# 32. Hidden Reasoning

AI observability does not require storage of hidden model chain-of-thought.

Instead record explicit operational facts such as:

* Model used
* Tool selected
* Tool executed
* Validation result
* Approval result
* Final status

This is sufficient for governance and diagnosis.

---

# 33. Sampling

Distributed traces may be sampled to control telemetry volume.

Possible strategies include:

* Head sampling
* Probability sampling
* Tail sampling

The current platform should use conservative trace volumes because physical storage and compute are fixed.

---

# 34. Tail Sampling

Future Collector policies may retain:

* Error traces
* Slow traces
* Selected critical workflows

while sampling routine successful traces.

This improves diagnostic value without retaining everything.

---

# 35. Trace Retention

A reasonable initial trace-retention target may be:

```text
7–14 days
```

This should be adjusted based on:

* Trace volume
* Storage
* Investigation requirements

---

# 36. Resource Governance

Observability consumes:

* CPU
* Memory
* Storage
* Network

Therefore:

* Log volume must be controlled
* Trace sampling must be controlled
* Retention must be controlled
* Collector resources must be bounded

Observability must not starve critical workloads.

---

# 37. Failure Isolation

Application processing should not fail because telemetry backends are unavailable.

Preferred behavior:

```text
Business Request
      │
      ├── Process Normally
      │
      └── Export Telemetry Asynchronously
```

Telemetry delivery has lower priority than business request completion.

---

# 38. Collector Failure

If the OpenTelemetry Collector fails:

* Application processing should normally continue
* Traces may be lost
* Export retries should remain bounded
* Memory queues must not grow indefinitely

Observability should degrade safely.

---

# 39. Loki Failure

If Loki is unavailable:

* Applications should continue
* Logs may remain temporarily at container/node layer
* Central log search becomes unavailable

Application runtime should not synchronously depend on Loki.

---

# 40. Tempo Failure

If Tempo is unavailable:

* Applications continue
* Trace visibility is degraded
* Metrics and logs remain available

This preserves partial observability.

---

# 41. Disaster Recovery

Most configuration is recoverable from Git.

Important assets include:

* Loki configuration
* Promtail configuration
* Tempo configuration
* OpenTelemetry Collector configuration
* Grafana data-source definitions

Historical observability data has lower recovery priority than current visibility.

---

# 42. Recovery Priorities

Typical observability recovery order:

```text
Prometheus / Alertmanager
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
OpenTelemetry Pipelines
```

The exact dependency order may vary.

---

# 43. Governance as Code

Observability configuration is part of Governance as Code.

Governed artifacts include:

* Logging configuration
* Collector configuration
* Trace sampling
* Retention
* Service naming
* Resource attributes
* Grafana data-source definitions

These should be version controlled.

---

# 44. Observability Policy as Code

Future controls may validate:

```text
Critical service:
- has metrics
- has centralized logs
- has service.name
- has tracing where required
- has dashboard
- has alerts
```

This can create measurable observability coverage.

---

# 45. Compliance Evidence

The observability stack can produce evidence for:

* Security events
* SLO compliance
* Backup status
* Policy violations
* AI availability
* Data freshness

This connects observability with continuous governance.

---

# 46. Risk Evidence

Key Risk Indicators may derive from:

* Loki event patterns
* Prometheus metrics
* Tempo latency
* Collector drop rates

This supports Risk as Code.

---

# 47. Technology Governance Status

Recommended classifications:

```text
Technology: Loki
Category: Observability / Logging
Lifecycle: ADOPT

Technology: Tempo
Category: Observability / Tracing
Lifecycle: ADOPT

Technology: OpenTelemetry
Category: Observability / Standard
Lifecycle: ADOPT

Technology: Promtail
Category: Observability / Log Collection
Lifecycle: ADOPT / Review with ecosystem lifecycle
```

Promtail lifecycle should be reviewed if the upstream observability ecosystem changes materially.

---

# 48. Technical Debt Consideration

The architecture itself is not technical debt.

Possible future debt includes:

* Missing trace propagation
* Unstructured application logs
* Excessive Loki labels
* Missing trace sampling governance
* Manual Collector configuration
* Missing AI tracing

These should be improved without replacing the observability architecture unnecessarily.

---

# 49. Risks

## Risk — Excessive Log Volume

Mitigation:

* Logging standards
* Retention
* DEBUG restrictions

## Risk — High Cardinality

Mitigation:

* Loki label governance
* OTel attribute governance

## Risk — Trace Storage Growth

Mitigation:

* Sampling
* Retention

## Risk — Sensitive Telemetry Exposure

Mitigation:

* Redaction
* Data minimization
* Access controls

## Risk — Collector Saturation

Mitigation:

* Memory limiter
* Batching
* Resource monitoring

---

# 50. Positive Consequences

The platform gains:

* Centralized logging
* Distributed tracing
* Open telemetry standards
* Cross-signal correlation
* Better Root Cause Analysis
* Better AI/RAG observability
* Stronger governance evidence
* Reduced observability vendor lock-in

---

# 51. Negative Consequences

The platform accepts:

* Multiple observability services
* Storage requirements
* Sampling governance
* Logging governance
* Instrumentation effort
* Additional operational knowledge

These costs are justified by the diagnostic capability gained.

---

# 52. Success Criteria

The decision remains successful while:

* Logs remain centrally searchable
* Distributed traces provide diagnostic value
* Applications remain decoupled from backends through OpenTelemetry
* Metrics/logs/traces can be correlated
* Resource usage remains controlled
* Sensitive telemetry remains governed

---

# 53. Review Triggers

Review this ADR if:

* Loki or Tempo no longer satisfies scale requirements
* OpenTelemetry standards materially change
* Promtail lifecycle requires migration
* Observability resource consumption becomes disproportionate
* A replacement provides measurable operational improvement
* Multi-cluster requirements change substantially

---

# 54. Governance as Code Metadata

Future machine-readable representation:

```yaml
id: ADR-0011
title: Adopt Loki Tempo and OpenTelemetry for Centralized Logs and Distributed Tracing
status: accepted

domain:
  - observability
  - platform
  - sre

technologies:
  - loki
  - promtail
  - tempo
  - opentelemetry
  - grafana

owner: platform-observability
implementation_status: implemented

related_adrs:
  - ADR-0001
  - ADR-0002
  - ADR-0010

alternatives:
  - elasticsearch
  - jaeger
  - saas-observability

principles:
  - specialized-backends
  - vendor-neutral-instrumentation
  - local-observability
  - telemetry-minimization

supersedes: null
superseded_by: null
```

---

# 55. Related Documents

* ADR-0001-Kubernetes
* ADR-0002-ArgoCD-GitOps
* ADR-0010-Prometheus-Grafana
* Logging Architecture
* Distributed Tracing
* OpenTelemetry Architecture
* Observability Governance
* Observability Operations
* AI Observability
* Risk Management
* Compliance Governance
