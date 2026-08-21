# Capacity Planning

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document defines the capacity planning strategy of the Enterprise AI Platform.

It establishes how compute, storage, networking and GPU resources are monitored, evaluated and managed throughout the platform lifecycle.

Rather than planning hardware expansion, the objective is to maximize the efficiency and reliability of the existing infrastructure.

---

# 2. Scope

This document covers:

- CPU capacity
- Memory capacity
- GPU capacity
- Storage capacity
- Network capacity
- Kubernetes scheduling
- Workload growth
- Capacity monitoring
- Forecasting
- Operational reviews

---

# 3. Objectives

Capacity planning aims to:

- Prevent resource exhaustion
- Detect growth trends
- Maintain platform stability
- Support workload prioritization
- Optimize resource utilization
- Delay unnecessary hardware expansion
- Support informed architectural decisions

---

# 4. Capacity Planning Principles

The platform follows these principles:

- Measure before optimizing.
- Optimize before expanding.
- Monitor continuously.
- Define thresholds.
- Forecast trends.
- Review capacity regularly.
- Treat compute resources as shared assets.

---

# 5. Capacity Domains

The platform monitors five primary resource domains.

```
CPU

↓

Memory

↓

GPU

↓

Storage

↓

Network
```

Each domain has dedicated monitoring and operational thresholds.

---

# 6. CPU Capacity

CPU planning focuses on:

- Node utilization
- Workload distribution
- Scheduling pressure
- Peak utilization
- Average utilization

Monitoring includes:

- Total CPU usage
- Per-node usage
- Per-namespace usage
- Per-pod usage
- CPU throttling

Recommended operational targets:

| Metric | Target |
|---------|--------|
| Average CPU utilization | <70% |
| Sustained utilization | <80% |
| Critical threshold | >90% |

---

# 7. Memory Capacity

Memory planning evaluates:

- Available memory
- Memory requests
- Memory limits
- OOM events
- Node pressure

Recommended thresholds:

| Metric | Target |
|---------|--------|
| Average memory usage | <75% |
| Warning threshold | 85% |
| Critical threshold | 95% |

OOMKilled Pods require investigation.

---

# 8. GPU Capacity

The platform currently provides:

- 2 × NVIDIA GTX 1080
- 8 GB VRAM each

GPU monitoring includes:

- Utilization
- VRAM usage
- Temperature
- Active workloads
- Queue length
- Inference latency

GPU workloads should be scheduled intentionally to avoid resource contention.

---

# 9. Storage Capacity

Storage monitoring includes:

- Persistent Volumes
- Databases
- Object storage
- Logs
- Metrics
- Traces
- ML artifacts
- Backups

Recommended thresholds:

| Metric | Target |
|---------|--------|
| Normal utilization | <70% |
| Warning | 80% |
| Critical | 90% |

Retention policies should be reviewed before expanding storage.

---

# 10. Network Capacity

Network monitoring includes:

- Bandwidth utilization
- Packet loss
- Latency
- Ingress throughput
- Error rates

The current residential network is sufficient for expected workloads.

---

# 11. Kubernetes Capacity

Cluster health indicators include:

- Allocatable CPU
- Allocatable Memory
- Node pressure
- Scheduling failures
- Pending Pods
- Evictions
- Unschedulable workloads

Kubernetes should maintain sufficient headroom for recovery operations.

---

# 12. Namespace Capacity

Each production namespace should be governed through:

- ResourceQuota
- LimitRange
- Requests
- Limits

Resource usage should be reviewed periodically.

---

# 13. Workload Prioritization

When resources become constrained, workloads are prioritized as follows:

| Priority | Workload |
|----------|----------|
| Critical | Kubernetes Control Plane |
| Critical | PostgreSQL |
| High | Argo CD |
| High | Monitoring |
| High | Airflow |
| High | MLflow |
| Medium | Business APIs |
| Medium | Frontend |
| Low | AI experiments |
| Lowest | Temporary testing |

This prioritization guides scheduling and operational decisions.

---

# 14. Growth Forecasting

Capacity planning is based on observed trends rather than assumptions.

Growth indicators include:

- Database growth
- Log volume
- Metrics retention
- Artifact storage
- Number of Pods
- Number of Services
- Active users
- AI inference requests

Forecasts should support operational planning.

---

# 15. Monitoring Tools

Capacity is monitored using:

| Tool | Purpose |
|------|---------|
| Prometheus | Metrics collection |
| Grafana | Dashboards |
| Node Exporter | Node metrics |
| kube-state-metrics | Kubernetes metrics |
| NVIDIA GPU Exporter (future) | GPU metrics |

---

# 16. Alerting

Capacity alerts should include:

- High CPU
- High memory
- Disk usage
- PVC growth
- GPU utilization
- GPU temperature
- Node pressure
- OOMKilled Pods
- Scheduling failures

Alerts should be actionable and reviewed regularly.

---

# 17. Capacity Review Process

Capacity should be reviewed on a regular basis.

Review activities include:

- Infrastructure health assessment
- Trend analysis
- Resource optimization
- Storage cleanup
- Namespace review
- GPU workload analysis
- Backup verification

Findings should be recorded in the operational documentation.

---

# 18. Optimization Strategy

Before considering additional hardware, the following actions should be evaluated:

- Right-size resource requests
- Adjust resource limits
- Remove unused workloads
- Clean old container images
- Reduce retention periods
- Archive inactive data
- Optimize AI models
- Improve scheduling
- Consolidate workloads

Expansion should be considered only after optimization opportunities have been exhausted.

---

# 19. Current Capacity Model

The platform operates within a fixed-capacity environment.

Capacity planning therefore focuses on:

- Operational efficiency
- Resource governance
- Controlled workload growth
- Predictable performance

The objective is not unlimited scalability but sustainable operation.

---

# 20. Risks

| Risk | Mitigation |
|------|------------|
| CPU saturation | Workload optimization |
| Memory exhaustion | Resource tuning |
| GPU contention | Explicit scheduling |
| Storage exhaustion | Retention policies |
| Network congestion | Monitoring and workload planning |
| Resource fragmentation | Regular capacity reviews |

---

# 21. Architecture Decisions

Key decisions include:

- Fixed-capacity infrastructure
- Continuous monitoring
- Resource optimization before expansion
- Kubernetes resource governance
- Namespace quotas
- GPU-aware scheduling
- Forecasting based on measured usage

---

# 22. Related Documents

- Infrastructure Architecture
- Compute Architecture
- Storage Architecture
- Kubernetes Architecture
- High Availability
- Disaster Recovery Plan
- Observability Architecture
- Operations Manual