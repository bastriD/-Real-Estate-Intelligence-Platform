# Availability Management Architecture

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the Availability Management Architecture of the Enterprise AI Platform.

It establishes the processes, metrics, responsibilities, and technical controls required to ensure that business applications and platform services achieve appropriate levels of availability.

The objective is to design, measure, monitor, and continuously improve service availability while balancing business requirements, infrastructure constraints, operational complexity, and cost.

---

# 2. Scope

This architecture applies to:

* Business Applications
* Kubernetes Platform
* Infrastructure Services
* Network Services
* Data Platform
* AI and LLM Services
* DevOps Services
* Observability Services
* Storage Services
* External Dependencies

---

# 3. Objectives

The Availability Management framework aims to:

* Meet defined service availability targets
* Minimize unplanned downtime
* Detect failures rapidly
* Reduce recovery time
* Eliminate critical single points of failure where practical
* Measure availability objectively
* Improve platform resilience
* Align availability targets with business requirements

---

# 4. Availability Principles

The platform follows these principles:

* Availability Based on Business Criticality
* Redundancy Where It Provides Value
* Failure Detection by Default
* Automated Recovery Where Practical
* Graceful Degradation
* Measurable Service Objectives
* Continuous Improvement
* No False High-Availability Claims

Availability requirements must reflect the capabilities and limitations of the physical infrastructure.

---

# 5. Availability Architecture

```text
Business Services
        │
        ▼
Application Services
        │
        ▼
Kubernetes Services
        │
        ▼
Platform Services
        │
        ▼
Compute / Storage / Network
        │
        ▼
Observability
        │
        ▼
Detection / Recovery / Improvement
```

Availability must be considered across the complete service dependency chain.

A highly available application cannot provide high availability when a critical underlying dependency remains unavailable.

---

# 6. Availability vs High Availability

Availability Management and High Availability are related but distinct.

**High Availability Architecture** defines technical mechanisms such as:

* Redundancy
* Replication
* Multiple instances
* Failover
* Load balancing
* Distributed workloads

**Availability Management** defines:

* Availability targets
* Measurement
* Monitoring
* Reporting
* Operational response
* Availability reviews
* Continuous improvement

A service can therefore use HA mechanisms while still failing to achieve its availability objective.

---

# 7. Service Criticality

Services should be classified according to business impact.

## Tier 1 — Critical

Examples:

* Core Kubernetes control plane
* Network services required by the platform
* Critical business APIs
* Authentication services

Requires the strongest practical availability controls.

---

## Tier 2 — Important

Examples:

* PostgreSQL
* Airflow
* MLflow
* Argo CD
* Production AI services

Temporary interruption is acceptable but should be minimized.

---

## Tier 3 — Supporting

Examples:

* Development environments
* Experimental AI workloads
* Non-critical dashboards
* Test services

Longer recovery periods may be acceptable.

---

# 8. Service Level Indicators

Availability is measured using Service Level Indicators (SLIs).

Examples include:

* Successful request ratio
* Service uptime
* API success rate
* Kubernetes workload availability
* Database connectivity
* Job execution success
* AI inference success
* Endpoint health

Example:

```text
Availability =
Successful Service Time
----------------------- × 100
Total Service Time
```

Monitoring should measure the service from the consumer perspective wherever possible.

---

# 9. Service Level Objectives

Service Level Objectives (SLOs) define the expected reliability of a service.

Example targets:

```text
Critical Service       Target SLO
----------------------------------
Core Platform           99.9%
Business API            99.9%
Database Service        99.9%
AI Inference            99.5%
Development Services    99.0%
```

These values are examples and must be validated against actual business requirements and infrastructure capabilities before becoming contractual targets.

---

# 10. Error Budgets

An error budget represents the acceptable amount of service unavailability within an SLO.

For example:

```text
SLO: 99.9%

Maximum unavailable time:

~43 minutes per 30-day period
```

Error budgets can help balance reliability and delivery velocity.

If the error budget is exhausted, priority may shift toward:

* Reliability improvements
* Problem resolution
* Technical debt reduction
* Capacity improvements
* Deployment stabilization

---

# 11. Failure Detection

Availability depends on rapid failure detection.

Current detection mechanisms include:

* Kubernetes readiness probes
* Kubernetes liveness probes
* Kubernetes events
* Prometheus metrics
* Grafana dashboards
* Loki logs
* Tempo traces
* OpenTelemetry telemetry

Failures should be detected before users report them whenever technically possible.

---

# 12. Kubernetes Availability

Kubernetes contributes several availability mechanisms:

* ReplicaSets
* Deployments
* StatefulSets
* Pod rescheduling
* Readiness probes
* Liveness probes
* Services
* Rolling updates
* Pod disruption controls
* Multiple control-plane nodes

Workloads should define appropriate resource requests and health checks to support reliable scheduling and recovery.

---

# 13. Application Availability

Applications should support:

* Multiple replicas where resources permit
* Stateless design where practical
* Health endpoints
* Graceful shutdown
* Retry policies
* Request timeouts
* Connection management
* Dependency failure handling

Applications should avoid assuming that dependencies are permanently available.

---

# 14. Data Platform Availability

Availability requirements apply to:

* PostgreSQL
* Airflow
* dbt workloads
* OpenMetadata
* Data pipelines

Controls may include:

* Database backups
* Pipeline retries
* Job idempotency
* Failure alerts
* Data validation
* Recovery procedures

Data availability must consider both infrastructure availability and data correctness.

---

# 15. AI Service Availability

AI services introduce additional availability considerations.

Components include:

* Ollama
* Qwen models
* MLflow
* AI APIs
* Embedding services
* Future RAG services

Metrics include:

* Inference success rate
* Model loading failures
* GPU availability
* Inference latency
* Request queue depth
* Model endpoint availability

AI service availability must not be confused with AI response quality.

A model endpoint can be technically available while producing unacceptable responses.

---

# 16. GPU Availability

The project operates with limited physical GPU resources.

Current physical AI resources include two NVIDIA GTX 1080 GPUs with 8 GB VRAM each.

These resources are fixed constraints for the current platform architecture.

Therefore, availability must prioritize:

* Efficient GPU scheduling
* Controlled concurrency
* Workload prioritization
* Resource monitoring
* Graceful degradation
* CPU fallback where technically appropriate
* Queue management

The architecture must not assume unlimited GPU capacity or near-term hardware expansion.

---

# 17. Network Availability

Network availability is critical because most platform services depend on internal communication.

Controls include:

* Network monitoring
* DNS monitoring
* Ingress health checks
* Connectivity validation
* Network policy validation
* Latency monitoring
* Packet-loss monitoring

Critical network dependencies should be documented.

---

# 18. Storage Availability

Storage failures may affect:

* Kubernetes workloads
* PostgreSQL
* MLflow artifacts
* Logs
* Backups
* AI models
* Data pipelines

Storage availability controls include:

* Capacity monitoring
* Disk health monitoring
* Backup validation
* Recovery procedures
* Persistent volume monitoring

Storage availability must be considered separately from data durability.

---

# 19. Graceful Degradation

Not every dependency failure should cause complete platform failure.

Examples include:

```text
LLM unavailable
    ↓
Application remains available
    ↓
AI functionality temporarily disabled
```

or:

```text
Analytics pipeline unavailable
    ↓
Existing dashboard data remains accessible
    ↓
Data refresh marked as delayed
```

Graceful degradation limits the business impact of partial platform failures.

---

# 20. Dependency Management

Service availability depends on upstream and downstream dependencies.

Example:

```text
Business Application
        │
        ├── API
        │
        ├── PostgreSQL
        │
        ├── AI Service
        │     └── GPU
        │
        ├── Kubernetes
        │
        ├── DNS
        │
        └── Network
```

Critical dependencies should be documented and monitored.

Dependency mapping will later support:

* Impact analysis
* Incident response
* Change management
* Disaster recovery
* Capacity planning

---

# 21. Recovery

Recovery mechanisms include:

* Kubernetes pod restart
* Pod rescheduling
* Deployment rollback
* Git revert
* Argo CD reconciliation
* Helm rollback
* Database restore
* Service restart
* Model rollback

Recovery mechanisms should be documented through operational runbooks.

---

# 22. Availability Monitoring

Current technologies include:

* Prometheus
* Grafana
* Loki
* Tempo
* OpenTelemetry
* Kubernetes metrics

Recommended dashboards include:

* Service availability
* Kubernetes health
* API availability
* Database availability
* AI inference availability
* GPU health
* Dependency health
* SLO compliance

---

# 23. Availability Alerts

Alerts should be based on actionable conditions.

Examples include:

* Service unavailable
* Replica count below minimum
* Database unreachable
* Kubernetes node unavailable
* Persistent volume failure
* AI endpoint unavailable
* GPU unavailable
* Excessive error rate
* SLO degradation

Alerting should avoid unnecessary noise and alert fatigue.

---

# 24. Availability Reviews

Availability should be reviewed periodically.

Reviews should analyze:

* Actual availability
* SLO compliance
* Major incidents
* Recurring failures
* MTTR
* Dependency failures
* Capacity constraints
* Error budget consumption

Results should generate concrete improvement actions.

---

# 25. Availability Metrics

Recommended metrics include:

```text
Availability
MTBF
MTTR
Failure Rate
Recovery Time
SLO Compliance
Error Budget Consumption
Incident Frequency
Dependency Availability
```

Where:

**MTBF** — Mean Time Between Failures

**MTTR** — Mean Time to Recovery

These metrics support objective reliability analysis.

---

# 26. Planned Maintenance

Planned maintenance should follow Change Management procedures.

Maintenance activities may include:

* Kubernetes upgrades
* Operating system maintenance
* Database maintenance
* Storage maintenance
* Certificate operations
* Platform upgrades

Where possible, maintenance should minimize service interruption.

---

# 27. Current Implementation

Current availability capabilities include:

* Three-node Kubernetes control plane
* Multiple Kubernetes worker nodes
* Kubernetes workload rescheduling
* NGINX Ingress
* cert-manager
* Argo CD reconciliation
* GitOps recovery
* Prometheus
* Grafana
* Loki
* Tempo
* OpenTelemetry
* Platform health monitoring

These capabilities provide a strong logical availability foundation.

However, physical infrastructure constraints remain part of the availability model and must be documented rather than hidden.

---

# 28. Availability Constraints

The current environment is primarily a resource-constrained private platform.

Important constraints include:

* Fixed physical infrastructure
* Limited GPU capacity
* Local hardware dependencies
* Shared physical resources
* Limited hardware redundancy in some layers

Therefore:

> Logical Kubernetes redundancy does not automatically guarantee complete physical high availability.

This distinction must remain explicit throughout the architecture documentation.

---

# 29. Future Evolution

Improvements that do not necessarily require major physical infrastructure expansion include:

* Formal SLI/SLO definitions
* Error budget dashboards
* Synthetic health checks
* Better dependency monitoring
* Improved readiness and liveness probes
* Pod Disruption Budgets
* Automated recovery validation
* Availability reporting
* Failure simulation
* SLO-based alerting

These improvements increase operational maturity while respecting current infrastructure constraints.

---

# 30. Architecture Decisions

Key architectural decisions include:

* Availability targets based on business criticality
* Explicit distinction between logical and physical availability
* Kubernetes-native recovery mechanisms
* Observability-driven failure detection
* SLO-based availability management
* Graceful degradation where practical
* Recovery automation where safe
* No assumption of unlimited physical resources

---

# 31. Related Documents

* High Availability Architecture
* Service Management
* Incident Management
* Problem Management
* Change Management
* Capacity Management
* Observability Architecture
* Backup and Restore
* Business Continuity
* Disaster Recovery
* SRE Practices
