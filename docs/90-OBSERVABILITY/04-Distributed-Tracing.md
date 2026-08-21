# Distributed Tracing Architecture

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the Distributed Tracing Architecture of the Enterprise AI Platform.

It establishes how individual requests and workflows are traced across application services, Kubernetes workloads, databases, AI services, data pipelines, and external dependencies.

The objective is to provide end-to-end visibility into request execution and enable rapid identification of latency, failures, bottlenecks, and dependency problems.

---

# 2. Scope

This architecture applies to:

* Business APIs
* Internal microservices
* Kubernetes workloads
* FastAPI applications
* PostgreSQL interactions
* AI inference services
* Ollama
* RAG pipelines
* Embedding services
* Future vector databases
* OpenTelemetry-instrumented services
* External APIs
* Platform services where tracing is supported

---

# 3. Objectives

The tracing platform aims to:

* Follow requests end to end
* Identify latency sources
* Identify failing dependencies
* Support Root Cause Analysis
* Correlate services
* Correlate logs and metrics
* Visualize distributed workflows
* Monitor AI request chains
* Support performance engineering
* Reduce Mean Time to Recovery

---

# 4. Tracing Principles

The platform follows these principles:

* Trace Complete Request Paths
* Use OpenTelemetry Standards
* Propagate Context Automatically
* Instrument Critical Boundaries
* Correlate Traces with Logs
* Avoid Sensitive Trace Attributes
* Control Sampling
* Minimize Runtime Overhead
* Prefer Meaningful Spans
* Manage Tracing Configuration as Code

---

# 5. High-Level Tracing Architecture

```text
User Request
     │
     ▼
Ingress
     │
     ▼
Business API
     │
     ├── PostgreSQL
     │
     ├── Internal Service
     │
     └── AI Service
             │
             ├── Retriever
             ├── Vector Store
             └── LLM
     │
     ▼
OpenTelemetry
     │
     ▼
OpenTelemetry Collector
     │
     ▼
Tempo
     │
     ▼
Grafana
```

Each component contributes spans to the same logical trace.

---

# 6. Trace

A trace represents the complete execution of one distributed operation.

Example:

```text
Trace ID: 7a9f...

User Request
 ├── Ingress
 ├── FastAPI
 │    ├── PostgreSQL Query
 │    └── AI Request
 │         ├── Retrieval
 │         └── Ollama Inference
 └── Response
```

The Trace ID links all related operations.

---

# 7. Span

A span represents one operation within a trace.

A span may describe:

* HTTP request
* Function execution
* Database query
* External API call
* RAG retrieval
* Model inference
* Queue processing
* Validation operation

Each span should have:

* Name
* Start time
* Duration
* Parent span
* Status
* Attributes
* Events where appropriate

---

# 8. Parent-Child Relationships

Spans form a hierarchical structure.

Example:

```text
HTTP Request
    │
    ├── Authentication
    │
    ├── Database Query
    │
    └── AI Inference
          │
          ├── Retrieval
          └── LLM Call
```

This hierarchy shows where time is spent.

---

# 9. Trace Context

Tracing depends on context propagation.

Key identifiers include:

```text
trace_id
span_id
parent_span_id
```

The Trace ID remains consistent across the request.

Each operation receives a unique Span ID.

---

# 10. W3C Trace Context

OpenTelemetry uses standardized context propagation.

Recommended standard:

```text
W3C Trace Context
```

Typical HTTP header:

```text
traceparent
```

This improves interoperability between tracing libraries and services.

---

# 11. Context Propagation

Context must propagate between services.

Example:

```text
Frontend
   │
   │ traceparent
   ▼
FastAPI
   │
   │ traceparent
   ▼
AI Service
   │
   │ traceparent
   ▼
Retriever
```

Without propagation, distributed spans become separate traces and lose their diagnostic value.

---

# 12. OpenTelemetry Instrumentation

OpenTelemetry is the preferred tracing standard.

Instrumentation can be:

## Automatic

Framework integrations generate spans automatically.

Examples:

* HTTP requests
* FastAPI
* Database drivers
* HTTP clients

## Manual

Custom spans are created for domain-specific operations.

Examples:

* RAG retrieval
* Model inference
* Data validation
* Business workflow steps

Both approaches should be used selectively.

---

# 13. Automatic Instrumentation

Automatic instrumentation provides broad baseline visibility with limited application changes.

Typical automatically captured operations include:

* Incoming HTTP requests
* Outgoing HTTP requests
* Database calls
* Framework middleware

Automatic instrumentation should be the starting point for supported applications.

---

# 14. Manual Instrumentation

Manual instrumentation should capture important operations not visible automatically.

Example:

```python
with tracer.start_as_current_span("rag.retrieve_documents"):
    ...
```

Useful custom spans may include:

```text
rag.retrieve
rag.rerank
ai.prompt_build
ai.inference
data.validation
business.property_analysis
```

Span names should describe stable operations rather than dynamic values.

---

# 15. Span Naming

Good:

```text
HTTP GET /properties
postgres.query
rag.retrieve
ollama.generate
```

Bad:

```text
request-7283628
query-user-12345
prompt-"full user prompt"
```

Dynamic information belongs in attributes, when appropriate, not span names.

---

# 16. Span Attributes

Attributes provide searchable metadata.

Useful attributes may include:

```text
service.name
deployment.environment
http.request.method
http.route
http.response.status_code
db.system
ai.model.name
ai.operation
```

Attributes should remain bounded and operationally meaningful.

---

# 17. Sensitive Attributes

Traces should not contain:

* Passwords
* Tokens
* API keys
* Full prompts by default
* Full model responses
* Sensitive legal content
* Database credentials
* Personal information unless explicitly required and controlled

Tracing should follow the same minimization principles as logging.

---

# 18. Service Naming

Every traced application should define a stable service name.

Example:

```text
service.name=business-api
service.name=ai-gateway
service.name=rag-service
```

Stable naming is essential for service topology and Grafana exploration.

---

# 19. Environment Attributes

Useful resource attributes include:

```text
deployment.environment=development
deployment.environment=staging
deployment.environment=production
```

This prevents confusion when multiple environments produce telemetry.

---

# 20. Kubernetes Attributes

Relevant Kubernetes context may include:

* Namespace
* Pod
* Deployment
* Node
* Container

OpenTelemetry resource detection can enrich traces with this information.

Pod-specific values should be used carefully when querying large volumes.

---

# 21. HTTP Tracing

HTTP spans should capture:

* Method
* Route
* Status
* Duration
* Server/service
* Client dependency

Route templates should be used instead of raw paths where possible.

Better:

```text
/properties/{id}
```

instead of:

```text
/properties/839273
```

This improves consistency and reduces cardinality.

---

# 22. Database Tracing

Database tracing helps identify:

* Slow queries
* Connection delays
* Transaction latency
* Database dependency failures

Example trace:

```text
FastAPI Request
      │
      ▼
postgres.query
Duration: 750 ms
```

Tracing should not expose sensitive SQL parameters unnecessarily.

---

# 23. PostgreSQL Trace Correlation

A slow request may be investigated as:

```text
API latency high
      │
      ▼
Tempo trace
      │
      ▼
postgres span = 1.8 s
      │
      ▼
PostgreSQL metrics
      │
      ▼
High connection saturation
```

This demonstrates cross-signal observability.

---

# 24. AI Inference Tracing

AI operations benefit strongly from tracing because they may involve multiple sequential steps.

Example:

```text
AI Request
   │
   ├── Input Validation
   ├── Prompt Assembly
   ├── Model Queue
   ├── Ollama Inference
   └── Output Validation
```

Each operation should be visible independently where instrumentation justifies it.

---

# 25. Ollama Tracing

Ollama may not provide full native distributed tracing for every interaction.

Tracing can therefore be implemented around the client request.

Example:

```text
FastAPI
   │
   ▼
Span: ollama.generate
   │
   ▼
HTTP request to Ollama
```

Useful measurements include:

* Request duration
* Model
* Status
* Timeout
* Error state

---

# 26. RAG Tracing

RAG flows require detailed tracing because failures may occur in several layers.

Example:

```text
rag.request
   │
   ├── embedding.generate
   │
   ├── vector.search
   │
   ├── rerank
   │
   ├── context.build
   │
   └── llm.generate
```

This allows engineers to distinguish:

* Retrieval latency
* Embedding latency
* Vector-store latency
* LLM latency

---

# 27. Retrieval Attributes

Useful RAG attributes may include:

```text
retrieval.result_count
retrieval.strategy
embedding.model
reranker.enabled
```

Avoid attaching the full retrieved document contents as trace attributes.

---

# 28. Agentic Workflow Tracing

Future AI agents may create complex execution chains.

Example:

```text
agent.workflow
    │
    ├── agent.plan
    ├── tool.database_query
    ├── tool.metadata_search
    ├── human.approval
    └── agent.finalize
```

Tracing should focus on operationally meaningful actions.

Hidden model reasoning is not required for observability.

---

# 29. Data Pipeline Tracing

Distributed tracing can complement Airflow where data workflows call multiple services.

Potential trace spans include:

* API extraction
* Database write
* Transformation service
* External request

Airflow remains the authoritative orchestration view for DAG structure and task state.

Tracing complements rather than replaces Airflow execution metadata.

---

# 30. Tempo

Tempo is the current distributed tracing backend.

Responsibilities include:

* Trace ingestion
* Trace storage
* Trace retrieval
* Grafana integration

Tempo is designed to work closely with Grafana, Loki, and Prometheus.

---

# 31. Tempo Architecture

Conceptually:

```text
Applications
      │
      ▼
OpenTelemetry Collector
      │
      ▼
Tempo
      │
      ▼
Grafana
```

The actual deployment architecture should remain proportionate to the current platform size and resources.

---

# 32. Grafana Trace Exploration

Grafana provides the primary tracing interface.

Operators should be able to inspect:

* Trace duration
* Service path
* Span latency
* Errors
* Dependencies

A trace should provide a rapid visual answer to:

> Where did the request spend its time?

---

# 33. Metrics-to-Traces Correlation

Example workflow:

```text
Grafana:
P95 latency increased
        │
        ▼
Select exemplar / trace
        │
        ▼
Tempo
        │
        ▼
Identify slow AI inference
```

Exemplars can connect Prometheus observations with individual traces where supported.

---

# 34. Logs-to-Traces Correlation

Structured logs should include trace identifiers.

Example log:

```json
{
  "level": "ERROR",
  "service": "business-api",
  "trace_id": "7a9f4312",
  "message": "AI service timeout"
}
```

Grafana can then link this event to the corresponding Tempo trace.

---

# 35. Trace-to-Logs Correlation

An engineer investigating a trace should be able to move directly to logs from the same:

* Service
* Trace ID
* Time window

This greatly improves troubleshooting efficiency.

---

# 36. Service Graphs

Tracing data may be used to derive service dependency graphs.

Example:

```text
Ingress
   ↓
Business API
   ├── PostgreSQL
   └── AI Gateway
         ↓
       Ollama
```

Service graphs help visualize application dependencies and identify bottlenecks.

---

# 37. Sampling

Tracing every request can produce excessive telemetry.

Sampling controls how many traces are retained.

Strategies include:

* Always-on
* Probability sampling
* Head sampling
* Tail sampling

The appropriate strategy depends on traffic and resource constraints.

---

# 38. Head Sampling

Head sampling decides whether to retain a trace at the beginning of the request.

Advantages:

* Simple
* Low overhead

Limitation:

The outcome of the request is not yet known.

A later error may therefore belong to a discarded trace.

---

# 39. Tail Sampling

Tail sampling decides after more of the trace is known.

It can prioritize:

* Errors
* Slow requests
* Specific services
* Rare events

Tail sampling provides stronger diagnostic value but requires additional processing and buffering.

---

# 40. Sampling Strategy

For the current resource-constrained environment, tracing should start conservatively.

Potential strategy:

```text
Development
→ Higher sampling

Production normal traffic
→ Partial sampling

Errors
→ Retain

Slow requests
→ Prefer retention
```

Sampling should be tuned using observed telemetry volume.

---

# 41. Sampling and Errors

Error traces provide high diagnostic value.

Where practical:

```text
Error Trace
    ↓
Higher retention priority
```

Similarly, high-latency traces may deserve increased retention priority.

---

# 42. Trace Retention

Trace retention should normally be shorter than critical metrics retention.

Possible initial target:

```text
7–14 days
```

Actual retention must consider:

* Trace volume
* Sampling
* Storage
* Investigation needs
* Resource constraints

---

# 43. Trace Volume

Trace volume depends on:

```text
Request Rate
×
Spans Per Request
×
Sampling Rate
```

Complex RAG or agentic workflows may generate many spans from a single user request.

This should be monitored carefully.

---

# 44. Span Explosion

Over-instrumentation creates unnecessary span volume.

Avoid tracing every trivial internal function.

Useful spans should represent:

* Network calls
* Database interactions
* Meaningful business operations
* Expensive processing
* Important AI stages

Instrumentation quality matters more than span quantity.

---

# 45. Instrumentation Overhead

Tracing adds:

* CPU usage
* Memory usage
* Network traffic
* Storage consumption

Instrumentation must therefore remain proportionate.

Tracing must not materially degrade the business service it monitors.

---

# 46. OpenTelemetry Collector

The OpenTelemetry Collector is the preferred processing layer.

Responsibilities include:

* Receive traces
* Enrich resources
* Batch spans
* Apply sampling
* Export to Tempo

This separates applications from backend-specific details.

---

# 47. Collector Failure

Applications should not depend synchronously on the Collector.

If telemetry export fails:

```text
Application
    │
    ├── Continue Business Request
    │
    └── Drop / buffer telemetry according to policy
```

Observability must not become a hard business dependency.

---

# 48. Baggage

OpenTelemetry baggage propagates contextual key/value information across service boundaries.

It should be used carefully.

Potential bounded examples:

```text
tenant.type
business.domain
```

Sensitive or high-cardinality information should not be propagated through baggage.

---

# 49. Security

Tracing information can expose system architecture and application behavior.

Access should therefore be protected through:

* Authentication
* RBAC
* Internal service exposure
* TLS where appropriate
* Restricted Grafana access

Tracing data should be considered operationally sensitive.

---

# 50. Privacy

Do not unnecessarily capture:

* User prompts
* Personal data
* Documents
* Model outputs
* Authentication values
* Full SQL parameters

Operational attributes should be sufficient to troubleshoot without duplicating sensitive business data.

---

# 51. Tracing and Incident Management

Typical incident workflow:

```text
Alert
 ↓
Prometheus Metric
 ↓
Affected Request
 ↓
Tempo Trace
 ↓
Slow / Failing Span
 ↓
Loki Logs
 ↓
Root Cause
```

Tracing bridges monitoring and detailed diagnosis.

---

# 52. Tracing and Problem Management

Historical traces can identify:

* Repeated slow dependencies
* Recurring database latency
* Frequent API retries
* Repeated AI timeouts
* Long-running RAG stages

These patterns support root-cause and architectural analysis.

---

# 53. Tracing and Capacity Management

Tracing helps identify where demand consumes time and resources.

Examples:

* AI queue latency
* Database contention
* External API delays
* Slow vector retrieval

It complements infrastructure metrics during capacity investigations.

---

# 54. Tracing and SRE

Tracing helps SRE teams understand why SLIs degrade.

Example:

```text
Latency SLI breach
       │
       ▼
Tempo
       │
       ▼
80% of request duration
inside AI inference
```

This enables targeted reliability improvements.

---

# 55. Tracing and GitOps

Tracing configuration should be managed through Git where possible.

Examples:

* Collector pipelines
* Sampling configuration
* Instrumentation settings
* Tempo values
* Grafana data-source configuration

This provides traceability and rollback.

---

# 56. CI/CD Instrumentation Validation

Applications should eventually validate tracing as part of deployment testing.

Validation may include:

* Trace produced
* Trace ID present
* Service name correct
* Parent-child relationships correct
* Critical spans present
* Sensitive values absent
* Tempo receives trace

Observability functionality should be treated as a service requirement.

---

# 57. Trace Smoke Test

Example validation workflow:

```text
Send request
    │
    ▼
Receive successful response
    │
    ▼
Find Trace ID
    │
    ▼
Open Tempo
    │
    ▼
Verify expected spans
```

A known test endpoint may simplify validation.

---

# 58. Current Implementation

Current capabilities include:

* Tempo
* OpenTelemetry Collector
* OpenTelemetry instrumentation
* Grafana
* Prometheus
* Loki

This provides the core technical platform for distributed tracing and cross-signal correlation.

---

# 59. Current Maturity

```text
Tempo                         → Implemented
OpenTelemetry Collector       → Implemented
Distributed Tracing Backend   → Implemented
Application Tracing           → Developing
Metrics-to-Trace Correlation  → Developing
Log-to-Trace Correlation      → Developing
AI Tracing                    → Developing
RAG Tracing                   → Future / Developing
Agent Tracing                 → Future
Sampling Governance           → To Formalize
Trace Retention Governance    → To Formalize
```

---

# 60. Physical Resource Constraints

Tracing must operate within the existing physical platform.

Therefore:

* Sampling must be controlled
* Retention must remain appropriate
* Span volume must be measured
* Over-instrumentation must be avoided
* Telemetry workloads must not compete excessively with business and AI workloads

Tracing quality takes priority over collecting every possible span.

---

# 61. Future Evolution

Planned improvements include:

* Broader FastAPI instrumentation
* Standard service naming
* Automatic database tracing
* End-to-end AI request tracing
* RAG span standards
* AI Gateway tracing
* Agent workflow tracing
* Trace-to-log correlation
* Metrics exemplars
* Tail sampling
* Slow-trace retention rules
* Standard instrumentation libraries
* Tracing validation in CI/CD
* Service graph dashboards

---

# 62. Architecture Decisions

Key decisions include:

* Tempo remains the distributed tracing backend
* OpenTelemetry is the preferred instrumentation standard
* OpenTelemetry Collector decouples applications from the tracing backend
* W3C Trace Context is preferred for propagation
* Stable service names are mandatory
* Request-specific values should not become uncontrolled trace attributes
* Sensitive content should not be captured by default
* Automatic instrumentation provides the baseline
* Manual spans are reserved for meaningful domain operations
* AI and RAG operations require dedicated logical spans
* Sampling is preferred over unlimited trace retention
* Observability failures must not become application failures
* Tracing configuration should be managed through GitOps

---

# 63. Related Documents

* Observability Architecture
* Metrics Architecture
* Logging Architecture
* OpenTelemetry Architecture
* Dashboard Strategy
* Alerting Strategy
* SLI/SLO Monitoring
* Observability Governance
* Observability Operations
* AI Observability
* Incident Management
* Problem Management
* SRE Practices
