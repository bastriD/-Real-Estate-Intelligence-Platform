# Site Reliability Engineering (SRE) Practices

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the Site Reliability Engineering (SRE) practices of the Enterprise AI Platform.

It establishes the principles, metrics, operational practices, and engineering mechanisms used to maintain reliable services while supporting continuous delivery and platform evolution.

The objective is to balance reliability, delivery velocity, operational effort, and infrastructure constraints through measurable engineering practices.

---

# 2. Scope

This document applies to:

* Kubernetes
* Platform Services
* Business Applications
* Data Platform
* AI Platform
* CI/CD
* GitOps
* Observability
* Incident Response
* Capacity Management
* Availability Management
* Disaster Recovery
* Operational Automation

---

# 3. Objectives

SRE practices aim to:

* Improve service reliability
* Reduce operational toil
* Establish measurable reliability targets
* Improve incident response
* Reduce recovery time
* Enable safe change velocity
* Increase automation
* Improve operational knowledge
* Manage reliability through data
* Support continuous improvement

---

# 4. SRE Principles

The platform follows these principles:

* Reliability Is Measurable
* Automate Repetitive Operations
* Accept Controlled Failure
* Define Reliability Objectives
* Use Error Budgets
* Prefer Engineering Over Manual Operations
* Learn from Incidents
* Reduce Toil
* Design for Failure
* Observe Before Optimizing

SRE is treated as an engineering discipline rather than an operations support function.

---

# 5. SRE Operating Model

```text
Business Expectations
        │
        ▼
Service Level Objectives
        │
        ▼
Service Level Indicators
        │
        ▼
Monitoring & Alerting
        │
        ▼
Operations
        │
        ├── Incident Response
        ├── Automation
        ├── Capacity Management
        └── Reliability Engineering
        │
        ▼
Continuous Improvement
```

---

# 6. Service Level Indicators

Service Level Indicators (SLIs) are measurable signals that represent service reliability.

Typical SLIs include:

* Availability
* Request success rate
* Error rate
* Latency
* Throughput
* Data freshness
* Job success
* Model inference success
* RAG retrieval success
* Backup success

Each critical service should define meaningful SLIs.

---

# 7. Service Level Objectives

Service Level Objectives (SLOs) define acceptable reliability targets.

Example targets:

| Service                  |                 Example SLO |
| ------------------------ | --------------------------: |
| Core Business API        |          99.9% availability |
| Kubernetes Control Plane |          99.9% availability |
| PostgreSQL               |          99.9% availability |
| AI Inference API         |          99.5% availability |
| Airflow Critical DAGs    |    99% successful execution |
| Data Freshness           | Within defined pipeline SLA |

These targets remain architecture objectives until measured and validated.

---

# 8. Service Level Agreements

Service Level Agreements (SLAs) are formal commitments to service consumers.

The current project does not assume contractual external SLAs.

Instead, the architecture primarily uses internal:

* SLIs
* SLOs
* Recovery objectives
* Operational targets

Future production environments may introduce formal SLAs where required.

---

# 9. Error Budgets

Error budgets define how much unreliability is acceptable while remaining within an SLO.

Example:

```text
SLO = 99.9%

Allowed failure = 0.1%
```

For a 30-day period:

```text
Approximate error budget
≈ 43 minutes
```

Error budgets help balance reliability and delivery velocity.

---

# 10. Error Budget Policy

When a service remains within its error budget:

* Feature delivery may continue normally.
* Controlled experimentation is acceptable.
* Platform evolution proceeds.

When a service consumes excessive error budget:

* Reliability work receives priority.
* Risky releases may be delayed.
* Root causes are investigated.
* Technical debt affecting reliability is prioritized.
* Capacity and architecture are reviewed.

This avoids arbitrary trade-offs between stability and delivery speed.

---

# 11. Reliability Engineering

Reliability is designed into services through:

* Multiple replicas
* Health probes
* Resource requests
* Resource limits
* Graceful shutdown
* Retry strategies
* Timeouts
* Idempotency
* Backup
* Recovery procedures
* GitOps reconciliation

Reliability should not depend exclusively on manual intervention.

---

# 12. Designing for Failure

The platform assumes components may fail.

Examples:

* Pod failure
* Worker failure
* Storage saturation
* Network interruption
* AI model failure
* GPU failure
* Database corruption

Applications and platform services should recover or degrade gracefully where practical.

---

# 13. Toil

SRE defines toil as repetitive operational work that is:

* Manual
* Repetitive
* Automatable
* Reactive
* Low long-term value
* Scales linearly with platform growth

Examples include:

* Manual deployments
* Repeated Pod restarts
* Manual certificate renewal
* Manual backup verification
* Repetitive incident diagnosis
* Manual environment configuration

---

# 14. Toil Reduction

The platform reduces toil through:

* Argo CD
* GitOps
* Kubernetes reconciliation
* cert-manager
* CI/CD
* Automated backups
* Monitoring
* Alerting
* Infrastructure as Code
* Runbooks

The target is not to remove all operations work, but to replace repetitive work with engineering.

---

# 15. Automation Priority

Automation should prioritize tasks that are:

```text
Frequent
+
Error Prone
+
Repeatable
+
Operationally Important
```

Examples include:

* Application deployment
* Backup execution
* Backup validation
* Certificate renewal
* Health verification
* Namespace provisioning
* Model deployment
* Data quality checks

Automation should include validation and safe failure behavior.

---

# 16. Observability

SRE depends heavily on observability.

Current platform capabilities include:

* Prometheus
* Grafana
* Loki
* Tempo
* OpenTelemetry

These provide:

* Metrics
* Logs
* Traces
* Dashboards
* Alerts

Observability should answer both:

> Is the service failing?

and:

> Why is the service failing?

---

# 17. Monitoring Strategy

Monitoring should focus on service behavior rather than only infrastructure health.

Recommended signals include the Four Golden Signals:

## Latency

How long requests take.

## Traffic

How much demand the service receives.

## Errors

How frequently requests fail.

## Saturation

How close resources are to capacity.

These signals apply across platform services.

---

# 18. Kubernetes SRE Metrics

Recommended Kubernetes reliability metrics include:

* Node readiness
* Pod restart rate
* CrashLoopBackOff
* Pending Pods
* CPU saturation
* Memory pressure
* Disk pressure
* Deployment availability
* Replica mismatch
* API server health

These indicators support proactive reliability management.

---

# 19. Data Platform SRE

Data platform reliability includes:

* Pipeline success rate
* Pipeline duration
* Data freshness
* Data quality
* Database availability
* Query latency
* ETL retry rate
* Metadata ingestion success

A technically running pipeline that produces invalid data should not be considered reliable.

---

# 20. AI Platform SRE

AI-specific reliability includes:

* Inference availability
* Inference latency
* GPU utilization
* Model loading success
* Token throughput
* Error rate
* RAG retrieval success
* Embedding service health
* Model response validation

AI SRE must combine technical availability with model/service quality.

---

# 21. Reliability and AI Quality

An AI system may be operational while still producing poor results.

Therefore AI reliability includes:

```text
Technical Reliability
+
Model Quality
+
Retrieval Quality
+
Response Quality
```

Examples of AI-specific SLO candidates:

* Inference success rate
* Maximum latency
* Minimum citation coverage
* Retrieval relevance threshold
* Model error rate

These should evolve as measurement capabilities mature.

---

# 22. Incident Management

SRE integrates directly with Incident Management.

Lifecycle:

```text
Detect
  ↓
Respond
  ↓
Mitigate
  ↓
Recover
  ↓
Learn
  ↓
Improve
```

The objective is not only rapid restoration but reduction of future recurrence.

---

# 23. On-Call Principles

A mature SRE operating model may introduce on-call responsibilities.

Principles include:

* Clear ownership
* Actionable alerts
* Defined escalation
* Runbooks
* Reasonable alert volume
* Post-incident review

The current project does not require a formal 24/7 on-call rotation.

The architecture defines the operating principles for future adoption.

---

# 24. Alert Quality

Alerts should be:

* Actionable
* Relevant
* Prioritized
* Service-oriented
* Linked to runbooks where possible

Poor alert:

```text
CPU = 82%
```

Better alert:

```text
Business API latency SLO is at risk because
worker CPU has remained saturated for 15 minutes.
```

SRE alerts should focus on user impact.

---

# 25. Alert Fatigue

Excessive alerting reduces operational effectiveness.

To prevent alert fatigue:

* Remove non-actionable alerts
* Deduplicate alerts
* Correlate related events
* Use severity levels
* Tune thresholds
* Review noisy alerts after incidents

Alert quality matters more than alert quantity.

---

# 26. Runbooks

Runbooks provide repeatable operational procedures.

Examples include:

* Pod recovery
* Kubernetes node recovery
* PostgreSQL restore
* Argo CD recovery
* Certificate troubleshooting
* Airflow failure recovery
* MLflow recovery
* Ollama restart
* Disk pressure remediation

Runbooks should contain exact validation steps.

---

# 27. Runbook Structure

Recommended structure:

```text
Purpose
Symptoms
Prerequisites
Diagnosis
Recovery Procedure
Validation
Rollback
Escalation
Related Alerts
```

Runbooks should be stored as version-controlled documentation.

---

# 28. Postmortems

Significant incidents should generate postmortems.

Postmortems should document:

* Timeline
* Impact
* Root cause
* Detection
* Response
* Recovery
* Contributing factors
* Corrective actions
* Preventive actions

The objective is learning rather than blame.

---

# 29. Blameless Culture

Human error should generally be analyzed as a system condition.

Instead of:

> Why did the engineer make the mistake?

Ask:

> Why did the system allow one mistake to cause this impact?

This encourages engineering improvements such as:

* Validation
* Automation
* Policy enforcement
* Safer defaults
* Review processes

---

# 30. Problem Management Integration

Recurring incidents should transition into Problem Management.

Example:

```text
Repeated Disk Pressure Incident
        │
        ▼
Problem Record
        │
        ▼
Root Cause Analysis
        │
        ▼
Retention / Capacity Fix
```

This prevents repeated operational firefighting.

---

# 31. Change Reliability

Every production change carries reliability risk.

SRE should monitor:

* Deployment failure rate
* Rollback frequency
* Error budget consumption after release
* Performance regression
* Incident correlation with changes

Git history and Argo CD provide valuable change correlation data.

---

# 32. DORA Metrics

DevOps and SRE maturity may be monitored using DORA-style indicators:

* Deployment Frequency
* Lead Time for Changes
* Change Failure Rate
* Mean Time to Restore

These metrics describe delivery performance and stability together.

---

# 33. Capacity and Reliability

Resource exhaustion is a reliability problem.

SRE works with Capacity Management to monitor:

* CPU headroom
* Memory headroom
* Storage growth
* Kubernetes scheduling capacity
* GPU availability
* Network performance

Critical workloads should maintain enough capacity for recovery and rescheduling.

---

# 34. Resource Constraints

The physical platform is intentionally fixed.

AI capacity includes:

* 2 × NVIDIA GTX 1080
* 8 GB VRAM per GPU

The SRE strategy therefore emphasizes:

* Workload optimization
* Resource limits
* Scheduling
* Quantized models
* Controlled concurrency
* Service prioritization
* Graceful degradation

Reliability must be achieved through engineering rather than assumed hardware expansion.

---

# 35. Graceful Degradation

Where practical, optional capabilities should fail independently.

Example:

```text
AI Inference Failure
        │
        ▼
AI Recommendation Disabled
        │
        ▼
Core Business Application Continues
```

This prevents auxiliary services from becoming unnecessary critical dependencies.

---

# 36. Capacity Headroom

Operating every resource permanently near 100% utilization reduces reliability.

The platform should preserve practical headroom for:

* Traffic spikes
* Pod rescheduling
* Recovery
* Maintenance
* Temporary workloads

Exact headroom depends on resource type and business criticality.

---

# 37. SRE and GitOps

GitOps provides several SRE benefits:

* Desired state
* Drift detection
* Automated reconciliation
* Change history
* Rollback
* Reproducibility

Operational model:

```text
Git
 ↓
Argo CD
 ↓
Kubernetes
 ↓
Observability
 ↓
Reliability Feedback
 ↓
Git Improvement
```

This creates a closed reliability feedback loop.

---

# 38. SRE and Platform Engineering

Platform Engineering provides reusable capabilities.

SRE ensures those capabilities meet reliability requirements.

Together:

```text
Platform Engineering
        │
        ▼
Reusable Platform Capabilities

SRE
        │
        ▼
Reliable Platform Capabilities
```

Both disciplines reinforce each other.

---

# 39. SRE and Security

Reliability and security overlap.

Examples include:

* Credential failures
* Certificate expiration
* DDoS
* Malicious workloads
* Supply-chain compromise
* Security-driven service isolation

Security incidents therefore influence service reliability and error budgets.

---

# 40. Reliability Testing

Reliability should be tested, not assumed.

Testing may include:

* Pod deletion
* Worker node drain
* Failed deployment rollback
* Database restore
* Network interruption
* Storage recovery
* GPU service failure
* Dependency failure

Testing should begin with controlled low-risk scenarios.

---

# 41. Chaos Engineering

Future maturity may include controlled failure injection.

Examples:

* Kill a Pod
* Remove a worker
* Introduce network latency
* Stop an AI service
* Simulate database unavailability

Chaos experiments must:

* Have defined scope
* Have rollback conditions
* Avoid uncontrolled risk
* Produce measurable learning

Chaos Engineering is optional and should be introduced only after recovery procedures are mature.

---

# 42. SRE Metrics

Recommended reliability indicators include:

```text
Availability
Latency
Error Rate
Throughput
MTTR
MTBF
Change Failure Rate
Deployment Frequency
Error Budget Consumption
Incident Frequency
Backup Success
Restore Success
Data Freshness
AI Inference Success
```

Metrics should support decisions rather than exist purely for reporting.

---

# 43. Reliability Dashboard

A future reliability dashboard may consolidate:

* SLO status
* Error budget
* Critical incidents
* Deployment health
* Capacity
* Backup health
* Kubernetes health
* Database health
* AI service health

This provides a service-level view of platform reliability.

---

# 44. SRE Review

A periodic reliability review should evaluate:

* SLO compliance
* Error budget
* Incident trends
* Major problems
* Capacity
* Backup health
* DR test results
* Alert quality
* Toil
* Technical debt

Each review should produce prioritized reliability actions.

---

# 45. Reliability Backlog

Reliability improvements should be managed as engineering work.

Examples:

* Improve health probes
* Add missing resource limits
* Automate backup validation
* Reduce noisy alerts
* Improve database recovery
* Add network monitoring
* Improve AI fallback
* Automate node recovery

Reliability work should compete transparently with feature development.

---

# 46. Current Implementation

Current platform capabilities supporting SRE include:

* Kubernetes HA control plane
* Multiple worker nodes
* GitLab
* CI/CD
* Argo CD
* GitOps
* Prometheus
* Grafana
* Loki
* Tempo
* OpenTelemetry
* Airflow
* MLflow
* PostgreSQL
* OpenMetadata
* Ollama
* Velero
* cert-manager
* NGINX Ingress
* Documented incident and recovery processes

This provides a strong foundation for adopting formal SRE practices.

---

# 47. Current Maturity

Current maturity can be characterized as:

```text
Observability             → Strong
GitOps                    → Strong
Automation                → Strong / Developing
Incident Management       → Documented
Problem Management        → Documented
Backup / DR               → Documented / Developing
Formal SLOs               → To Implement
Error Budgets             → To Implement
Toil Measurement          → To Implement
Reliability Reviews       → To Formalize
Chaos Engineering         → Future
```

This avoids claiming SRE controls that are not yet operational.

---

# 48. Future Evolution

Planned improvements include:

* Formal service SLIs
* Formal SLOs
* Error budget dashboards
* SLO-based alerting
* Reliability scorecards
* Automated restore tests
* Toil measurement
* Reliability backlog
* Synthetic monitoring
* AI reliability metrics
* Controlled chaos engineering
* Automated remediation
* Predictive reliability analysis

These enhancements can be implemented progressively without changing the platform's core architecture.

---

# 49. Architecture Decisions

Key SRE decisions include:

* Reliability is measured through service indicators
* SLOs are preferred over vague uptime expectations
* Error budgets balance reliability and delivery velocity
* GitOps provides the desired-state reliability mechanism
* Observability is required for all critical services
* Toil should be automated where safe and valuable
* Postmortems are blameless
* Recurring incidents become Problem Management work
* Capacity is treated as a reliability concern
* AI quality and AI availability are measured separately
* Physical resource constraints are accepted and engineered around
* Reliability testing should progressively validate assumptions

---

# 50. Related Documents

* Service Management
* Incident Management
* Problem Management
* Change Management
* Capacity Management
* Availability Management
* Backup and Restore
* Business Continuity
* Disaster Recovery
* GitOps Architecture
* Platform Engineering
* Observability Architecture
* AI Observability
