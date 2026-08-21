# OpenTelemetry Architecture

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the OpenTelemetry Architecture of the Enterprise AI Platform.

It establishes how OpenTelemetry is used as the common observability standard for generating, propagating, processing, and exporting telemetry across applications, Kubernetes workloads, data services, and AI services.

The objective is to reduce vendor-specific instrumentation, standardize telemetry, and provide a consistent integration layer between workloads and observability backends.

---

# 2. Scope

This architecture applies to:

* Application instrumentation
* FastAPI services
* Internal APIs
* Data services
* AI services
* RAG services
* Future agentic workflows
* Kubernetes workloads
* OpenTelemetry SDKs
* OpenTelemetry Collector
* Metrics
* Logs
* Traces
* Context propagation

---

# 3. Objectives

OpenTelemetry aims to:

* Standardize observability instrumentation
* Reduce backend coupling
* Provide consistent telemetry metadata
* Enable distributed tracing
* Support metrics collection
* Support structured telemetry pipelines
* Improve signal correlation
* Simplify future backend changes
* Centralize telemetry processing
* Support vendor-neutral observability

---

# 4. OpenTelemetry Principles

The platform follows these principles:

* Open Standards First
* Instrument Once, Export Independently
* Centralize Telemetry Processing
* Preserve Trace Context
* Use Semantic Conventions
* Minimize Application-Specific Backend Logic
* Control Telemetry Volume
* Protect Sensitive Information
* Manage Collector Configuration as Code
* Observability Must Not Break Business Services

---

# 5. High-Level Architecture

```text
Application
    │
    ├── OpenTelemetry SDK
    │
    └── Auto-Instrumentation
             │
             ▼
          OTLP
             │
             ▼
OpenTelemetry Collector
             │
     ┌───────┼────────┐
     │       │        │
     ▼       ▼        ▼
 Metrics    Logs     Traces
     │       │        │
     ▼       ▼        ▼
Prometheus  Loki     Tempo
     │       │        │
     └───────┼────────┘
             ▼
           Grafana
```

The Collector acts as the common telemetry processing layer.

---

# 6. OpenTelemetry Components

The architecture consists of:

* OpenTelemetry API
* OpenTelemetry SDK
* Auto-Instrumentation
* OTLP
* Context Propagation
* OpenTelemetry Collector
* Semantic Conventions
* Resource Attributes

Each component has a different responsibility.

---

# 7. OpenTelemetry API

The OpenTelemetry API provides the application-facing interface for instrumentation.

Applications may use it to create:

* Traces
* Spans
* Metrics
* Context

Application code should depend on the OpenTelemetry API rather than backend-specific telemetry libraries where practical.

---

# 8. OpenTelemetry SDK

The SDK implements telemetry generation.

Responsibilities include:

* Trace creation
* Span processing
* Metrics aggregation
* Context handling
* Sampling
* Export

The SDK should be configured centrally where possible.

---

# 9. Auto-Instrumentation

Auto-instrumentation provides baseline telemetry without requiring manual code changes for every operation.

Typical integrations may capture:

* HTTP requests
* FastAPI operations
* HTTP clients
* PostgreSQL calls
* Framework middleware

Auto-instrumentation should be the default starting point where mature integrations exist.

---

# 10. Manual Instrumentation

Manual instrumentation is used for business- or AI-specific operations that automatic instrumentation cannot understand.

Examples:

```text
property.analysis
rag.retrieve
rag.rerank
ai.inference
model.validation
business.recommendation
```

Manual instrumentation should remain intentional and limited to meaningful operations.

---

# 11. OTLP

OpenTelemetry Protocol (OTLP) is the preferred telemetry transport.

Supported transports commonly include:

```text
OTLP/gRPC
OTLP/HTTP
```

Conceptually:

```text
Application
    │
    ▼
OTLP
    │
    ▼
Collector
```

Using OTLP avoids direct application dependency on Tempo, Prometheus, or other specific backends.

---

# 12. OTLP Endpoints

Workloads should send telemetry to a stable Collector endpoint.

Example conceptual endpoints:

```text
otel-collector.monitoring.svc:4317
otel-collector.monitoring.svc:4318
```

The exact service naming depends on the deployed configuration.

---

# 13. Context Propagation

OpenTelemetry propagates context between distributed services.

Preferred tracing standard:

```text
W3C Trace Context
```

Key header:

```text
traceparent
```

Context propagation enables independent services to contribute spans to the same distributed trace.

---

# 14. Resource Attributes

Resource attributes describe the entity producing telemetry.

Recommended attributes include:

```text
service.name
service.version
deployment.environment
service.namespace
```

Kubernetes enrichment may additionally provide:

```text
k8s.namespace.name
k8s.pod.name
k8s.deployment.name
k8s.node.name
```

Stable resource metadata significantly improves querying and correlation.

---

# 15. Mandatory Service Identity

Every instrumented service should define:

```text
service.name
```

Example:

```text
service.name=business-api
```

Without stable service identity, telemetry becomes difficult to aggregate and interpret.

---

# 16. Service Version

Where practical, telemetry should expose:

```text
service.version
```

Examples:

```text
service.version=1.4.2
service.version=git-a93f21d
```

This helps correlate incidents with deployments.

---

# 17. Deployment Environment

Telemetry should identify environment.

Example:

```text
deployment.environment=production
```

This avoids mixing:

* Development
* Testing
* Staging
* Production

inside the same operational queries.

---

# 18. Semantic Conventions

OpenTelemetry Semantic Conventions standardize attribute names across technologies.

Examples include:

```text
http.request.method
http.response.status_code
db.system
server.address
service.name
```

Standard conventions should be preferred over custom equivalents whenever available.

---

# 19. Custom Attributes

Custom attributes should only be introduced when they provide meaningful domain context.

Example:

```text
ai.operation=generate
ai.model=qwen3:8b
business.domain=real-estate
```

Custom naming should remain standardized across the platform.

---

# 20. Sensitive Attributes

OpenTelemetry telemetry must not intentionally expose:

* Passwords
* API keys
* Tokens
* Session cookies
* Private keys
* Full prompts
* Full generated responses
* Sensitive documents
* Database credentials

Telemetry enrichment must respect privacy and security controls.

---

# 21. OpenTelemetry Collector

The Collector is the central telemetry processing component.

Responsibilities include:

* Receiving telemetry
* Processing telemetry
* Enriching telemetry
* Filtering telemetry
* Batching telemetry
* Sampling traces
* Exporting telemetry

The Collector decouples telemetry producers from storage backends.

---

# 22. Collector Pipeline Model

Collector pipelines follow:

```text
Receiver
   │
   ▼
Processor
   │
   ▼
Exporter
```

Multiple pipelines may exist simultaneously.

Example:

```text
traces:
  receivers
      ↓
  processors
      ↓
  exporters
```

---

# 23. Receivers

Receivers accept telemetry.

Examples may include:

```text
otlp
prometheus
hostmetrics
```

The preferred application-facing receiver is OTLP.

---

# 24. OTLP Receiver

Example conceptual configuration:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:
```

This enables both standard OTLP transports.

---

# 25. Prometheus Receiver

The Collector may scrape Prometheus-compatible targets where appropriate.

However, the existing Prometheus platform should remain the primary Kubernetes metrics collection engine unless a specific architectural benefit justifies moving scrape responsibility.

The Collector should complement rather than unnecessarily duplicate Prometheus.

---

# 26. Processors

Processors modify telemetry before export.

Common processors include:

* Batch
* Memory limiter
* Resource
* Attributes
* Filter
* Sampling

Processors provide an important governance and performance layer.

---

# 27. Batch Processor

The batch processor groups telemetry before export.

Benefits include:

* Lower network overhead
* Better exporter efficiency
* Improved throughput

Conceptual configuration:

```yaml
processors:
  batch: {}
```

Batching should normally be enabled.

---

# 28. Memory Limiter

The memory limiter protects the Collector from uncontrolled telemetry pressure.

Example concept:

```yaml
processors:
  memory_limiter:
    check_interval: 1s
    limit_percentage: 75
```

Exact limits must reflect assigned Kubernetes resources.

---

# 29. Resource Processor

The resource processor may add or modify resource metadata.

Example use cases:

* Environment
* Cluster
* Platform
* Business domain

Enrichment should remain stable and bounded.

---

# 30. Attributes Processor

The attributes processor can:

* Add attributes
* Delete attributes
* Update attributes
* Hash attributes

This can help enforce telemetry governance before data leaves the Collector.

---

# 31. Filtering

Telemetry may be filtered to reduce:

* Noise
* Cost
* Sensitive content
* Unnecessary spans
* Low-value metrics

Filtering must be tested carefully to avoid removing important diagnostic data.

---

# 32. Exporters

Exporters send telemetry to downstream systems.

Current architecture targets include:

```text
Tempo
Prometheus-compatible metrics flow
Loki-compatible logging flow
```

The precise exporter type depends on the deployed OpenTelemetry and backend integrations.

---

# 33. Traces Pipeline

Conceptually:

```text
Applications
    │
    ▼
OTLP Receiver
    │
    ▼
Memory Limiter
    │
    ▼
Resource Enrichment
    │
    ▼
Batch
    │
    ▼
Tempo
```

This is the primary distributed tracing use case.

---

# 34. Metrics Pipeline

Metrics may originate from:

* OpenTelemetry SDK
* Prometheus endpoints
* Infrastructure exporters

The current architecture retains Prometheus as the authoritative operational metrics system.

OpenTelemetry metrics should therefore integrate cleanly into Prometheus rather than create an unrelated metrics silo.

---

# 35. Logs Pipeline

OpenTelemetry can support log pipelines, but the current centralized logging architecture already uses:

```text
Promtail
→ Loki
```

Migration of all logs to OpenTelemetry should not be performed only for architectural uniformity.

A migration should require a demonstrated operational benefit.

---

# 36. Architecture Position

The platform therefore uses OpenTelemetry primarily as:

```text
Instrumentation Standard
+
Trace Context Standard
+
Collector Layer
```

while specialized backends retain their responsibilities.

This reduces unnecessary complexity.

---

# 37. Collector Deployment Model

Potential Kubernetes deployment patterns include:

## Central Gateway

```text
Applications
    │
    ▼
Central Collector
```

Advantages:

* Simple management
* Central configuration

## Agent

Collector runs near workloads or nodes.

Advantages:

* Local collection
* Reduced application/backend coupling

## Combined

Agents forward to central gateway collectors.

This provides higher scalability but increases complexity.

---

# 38. Current Deployment Strategy

For the current platform scale, a simple Collector deployment is preferred unless operational measurements demonstrate the need for a more complex topology.

This aligns with the fixed-resource architecture.

Complexity must be justified by real requirements.

---

# 39. Collector Availability

The Collector is an observability service.

Its failure should not cause application failure.

Applications should:

* Export asynchronously
* Use bounded queues
* Avoid blocking business requests
* Drop telemetry when necessary rather than fail business processing

Observability must remain non-critical to core request completion.

---

# 40. Retry Behavior

Exporters may retry temporary backend failures.

Retries must be bounded.

Unbounded retries may cause:

* Memory growth
* Queue growth
* Collector saturation
* Cascading telemetry failures

Telemetry resilience must not become resource exhaustion.

---

# 41. Queuing

Collector exporters may use queues where appropriate.

Queues can absorb temporary backend outages.

However:

```text
Long outage
+
Unlimited queue
=
Memory / disk problem
```

Queue size must therefore remain controlled.

---

# 42. Sampling

Trace sampling may be performed:

* In the application SDK
* In the Collector
* Using tail sampling

The Collector is particularly useful for centralized tail-sampling policies.

---

# 43. Tail Sampling

Tail sampling can prioritize traces based on outcomes.

Examples:

* Errors
* High latency
* Specific critical services

Conceptual policy:

```text
Keep error traces
Keep slow traces
Sample routine successful traces
```

This provides diagnostic value while controlling storage.

---

# 44. Sampling Governance

Sampling policies should consider:

* Traffic volume
* Service criticality
* Error rate
* Storage
* AI workload complexity

Critical workflows may justify higher trace retention than non-critical traffic.

---

# 45. Metrics Cardinality

OpenTelemetry metrics must follow the same cardinality governance as Prometheus metrics.

Avoid dimensions such as:

```text
user_id
request_id
session_id
prompt
full_url
```

High-cardinality attributes may become expensive time-series dimensions downstream.

---

# 46. Trace Attribute Cardinality

Tracing can tolerate more unique values than Prometheus metrics, but attributes should still be operationally meaningful.

Excessive attribute volume increases:

* Storage
* Transfer
* Search complexity

Instrumentation should remain deliberate.

---

# 47. Kubernetes Metadata Enrichment

The Collector may enrich telemetry with Kubernetes metadata.

Potential attributes:

```text
k8s.namespace.name
k8s.pod.name
k8s.deployment.name
k8s.node.name
```

This improves correlation between application and platform telemetry.

---

# 48. Kubernetes RBAC

Metadata enrichment components may require Kubernetes API permissions.

RBAC must follow Least Privilege.

The Collector should receive only the permissions required for metadata discovery.

---

# 49. OpenTelemetry and FastAPI

FastAPI services are strong candidates for OpenTelemetry instrumentation.

Recommended telemetry includes:

* Incoming HTTP spans
* Outgoing HTTP spans
* PostgreSQL spans
* Custom business spans
* Request latency
* Status
* Trace context

Manual spans can supplement framework instrumentation.

---

# 50. OpenTelemetry and PostgreSQL

Supported database instrumentation can provide visibility into:

* Query latency
* Database dependency calls
* Errors

Sensitive SQL parameters should not be captured unnecessarily.

Database metrics remain in Prometheus.

Database traces explain request-level latency.

---

# 51. OpenTelemetry and AI Services

AI workloads should use OpenTelemetry to capture operational stages.

Examples:

```text
ai.request
ai.prompt_build
ai.inference
ai.response_validation
```

Attributes may include:

```text
ai.model.name
ai.operation
```

Sensitive prompt and output content should not be captured by default.

---

# 52. OpenTelemetry and RAG

RAG instrumentation may include:

```text
rag.request
embedding.generate
vector.search
rerank
context.build
llm.generate
```

This allows performance analysis across the retrieval and generation pipeline.

---

# 53. OpenTelemetry and Agents

Future agent workflows may trace:

* Agent request
* Planning
* Tool invocation
* External dependency
* Approval stage
* Completion

Instrumentation should focus on explicit actions and observable workflow stages.

---

# 54. Hidden Reasoning

Observability must not depend on collecting private model chain-of-thought.

Instead, systems should record:

* Tool chosen
* Action executed
* Policy result
* Validation result
* Outcome
* Latency
* Error

These events provide sufficient operational traceability without requiring hidden reasoning content.

---

# 55. OpenTelemetry and Logs

Applications may include trace identifiers inside structured logs.

Example:

```json
{
  "service": "business-api",
  "trace_id": "abc123",
  "level": "ERROR",
  "message": "database timeout"
}
```

This enables Loki-to-Tempo correlation.

---

# 56. OpenTelemetry and Prometheus

OpenTelemetry metrics should align with Prometheus conventions.

Requirements include:

* Stable metric names
* Bounded labels
* Standard units
* Meaningful dimensions

The objective is one coherent metrics architecture rather than parallel incompatible standards.

---

# 57. OpenTelemetry and Tempo

Tempo remains the authoritative distributed trace backend.

OpenTelemetry should send traces through the Collector rather than binding application code directly to Tempo-specific interfaces.

This preserves backend independence.

---

# 58. OpenTelemetry and Grafana

Grafana consumes telemetry through specialized backends.

```text
Prometheus → Metrics
Loki       → Logs
Tempo      → Traces
```

OpenTelemetry standardizes telemetry generation and transport beneath these systems.

---

# 59. Telemetry Correlation

Desired observability correlation:

```text
Service Error
    │
    ▼
Prometheus Metric
    │
    ▼
Tempo Trace
    │
    ▼
Loki Log
```

Shared resource attributes and trace context make this possible.

---

# 60. Security

OpenTelemetry infrastructure must follow platform security requirements.

Controls include:

* Kubernetes RBAC
* Namespace isolation
* TLS where required
* Restricted OTLP exposure
* Network Policies
* Secret management

The Collector should not expose unrestricted public telemetry endpoints.

---

# 61. OTLP Exposure

OTLP endpoints should generally remain internal.

External applications should not be allowed to send arbitrary telemetry into the platform without authentication and governance.

Untrusted telemetry may cause:

* Storage abuse
* Cardinality problems
* Misleading metrics
* Sensitive-data injection

---

# 62. Data Minimization

Instrumentation should collect only the information needed for:

* Reliability
* Diagnostics
* Performance
* Governance

Avoid using observability as an uncontrolled data capture mechanism.

---

# 63. Telemetry Redaction

Sensitive attributes should be removed before export.

Possible enforcement points include:

```text
Application
    │
    ▼
Collector attributes/filter processor
    │
    ▼
Backend
```

Defense in depth is preferable.

---

# 64. Collector Monitoring

The Collector itself must expose health metrics.

Important indicators include:

* Received telemetry
* Exported telemetry
* Dropped telemetry
* Export failures
* Queue size
* Memory usage
* CPU usage

Collector saturation should be detectable.

---

# 65. Collector Health

Health monitoring should answer:

```text
Is Collector running?

Is telemetry being received?

Is telemetry being exported?

Are records being dropped?
```

A healthy process does not automatically mean healthy telemetry delivery.

---

# 66. Resource Limits

Collector Pods should define:

* CPU requests
* CPU limits where appropriate
* Memory requests
* Memory limits

The memory limiter processor should align with those Kubernetes limits.

---

# 67. GitOps Management

Collector configuration should be stored in Git.

Examples include:

* Receivers
* Processors
* Exporters
* Pipelines
* Sampling rules
* Resource enrichment

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
Collector
```

---

# 68. Configuration Validation

Collector configuration changes should be validated before production.

Validation should include:

* YAML syntax
* Collector config loading
* Pipeline connectivity
* Export connectivity
* Expected resource attributes
* No unintended sensitive data
* No significant telemetry loss

---

# 69. Change Management

Major changes may affect all observability signals.

Examples:

* New sampling policy
* New exporter
* New filtering rule
* Resource attribute changes

Such changes should follow Change Management because they can reduce platform visibility.

---

# 70. Failure Modes

Potential failures include:

* Collector unavailable
* Tempo unavailable
* Network failure
* Export timeout
* Memory pressure
* Invalid configuration
* Telemetry overload

Recovery procedures should distinguish between application failure and observability pipeline failure.

---

# 71. Backpressure Strategy

The telemetry pipeline should fail safely.

Priority:

```text
Business Request
    >
Telemetry Delivery
```

If required, telemetry may be sampled, dropped, or temporarily buffered rather than blocking critical applications.

---

# 72. Current Implementation

Current capabilities include:

* OpenTelemetry Collector
* Tempo
* Prometheus
* Grafana
* Loki
* Kubernetes
* Distributed tracing
* OpenTelemetry-based telemetry workflows

This provides a strong foundation for standardizing application instrumentation.

---

# 73. Current Maturity

```text
OpenTelemetry Collector        → Implemented
Tempo Integration              → Implemented
Trace Collection               → Implemented
Application Instrumentation    → Developing
Resource Standardization       → Developing
Semantic Convention Adoption   → Developing
AI Instrumentation             → Developing
RAG Instrumentation            → Future / Developing
Tail Sampling                  → Future
Telemetry Redaction            → To Formalize
Collector Governance           → To Formalize
```

---

# 74. Resource Constraints

OpenTelemetry processing must respect the fixed physical infrastructure.

Therefore:

* Collector resources must be limited
* Telemetry volume must be controlled
* Sampling should be used where justified
* Unnecessary transformations should be avoided
* Multiple Collector tiers should not be introduced without demonstrated need

Operational simplicity is an architectural requirement.

---

# 75. Future Evolution

Planned improvements include:

* Standard OpenTelemetry SDK configuration
* Shared instrumentation libraries
* Standard resource attributes
* Wider FastAPI instrumentation
* Database instrumentation
* AI semantic conventions where mature
* RAG instrumentation standards
* Tail sampling
* Kubernetes metadata enrichment
* Telemetry redaction
* Collector health dashboards
* CI validation
* Network Policies for OTLP
* Standard observability templates for new services

---

# 76. Architecture Decisions

Key decisions include:

* OpenTelemetry is the preferred telemetry instrumentation standard
* OTLP is the preferred application telemetry transport
* The Collector decouples applications from observability backends
* Tempo remains the trace backend
* Prometheus remains the primary operational metrics backend
* Loki remains the centralized log backend
* Existing specialized collectors are retained when they provide better operational simplicity
* Semantic conventions are preferred over custom attributes
* `service.name` is mandatory for instrumented applications
* Sensitive data must not be captured by default
* Telemetry must never become a hard dependency for business processing
* Collector complexity must remain proportional to actual platform scale
* Collector configuration is managed through GitOps

---

# 77. Related Documents

* Observability Architecture
* Metrics Architecture
* Logging Architecture
* Distributed Tracing
* Dashboard Strategy
* Alerting Strategy
* SLI/SLO Monitoring
* Observability Governance
* Observability Operations
* AI Observability
* Platform Engineering
* SRE Practices
