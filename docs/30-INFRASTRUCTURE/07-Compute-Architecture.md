# Compute Architecture

**Version:** 1.0  
**Status:** Draft  
**Owner:** Bastri Murad  
**Project:** Enterprise AI Platform  
**Business Application:** Real Estate Intelligence Platform  
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document defines the compute architecture of the Enterprise AI Platform.

It describes how CPU, memory, GPU and Kubernetes compute resources are allocated, scheduled, monitored and optimized across the platform.

The objective is to maximize resource efficiency while maintaining platform reliability within the constraints of the available infrastructure.

---

# 2. Scope

This document covers:

- Physical compute resources
- Virtual compute allocation
- Kubernetes compute scheduling
- CPU management
- Memory management
- GPU management
- Workload prioritization
- Autoscaling strategy
- Capacity optimization

---

# 3. Compute Objectives

The compute platform is designed to provide:

- Efficient resource utilization
- Predictable workload performance
- Fair resource allocation
- Controlled resource consumption
- Platform stability
- AI workload support
- Future scalability

---

# 4. Compute Layers

```
Business Applications
        │
Platform Services
        │
Kubernetes Scheduler
        │
Virtual Machines
        │
Physical CPU / RAM / GPU
```

Each layer consumes compute resources from the layer below.

---

# 5. Physical Compute Resources

Current compute infrastructure consists of:

- Physical CPUs
- Physical RAM
- Two NVIDIA GTX 1080 GPUs (8 GB VRAM each)

These resources represent the fixed compute capacity available to the platform.

No major hardware expansion is planned.

---

# 6. Virtual Compute

Proxmox allocates virtual resources to each VM.

Resources include:

- Virtual CPUs (vCPU)
- Memory
- Virtual disks
- Network interfaces

Allocation is based on workload responsibilities rather than equal distribution.

---

# 7. Kubernetes Compute Model

Kubernetes schedules workloads according to:

- Available CPU
- Available Memory
- Resource Requests
- Resource Limits
- Node Availability
- Scheduling Policies

Pods should never assume unlimited compute capacity.

---

# 8. CPU Management

CPU resources are shared across workloads.

Each production workload should define:

- CPU Request
- CPU Limit

Objectives:

- Prevent CPU starvation
- Avoid noisy neighbors
- Maintain platform responsiveness
- Guarantee minimum compute resources

---

# 9. Memory Management

Memory is managed through Kubernetes resource limits.

Every workload should define:

- Memory Request
- Memory Limit

Memory exhaustion may result in:

- OOMKilled Pods
- Scheduling failures
- Reduced platform stability

Memory allocation should therefore be conservative and continuously monitored.

---

# 10. GPU Architecture

The platform contains two NVIDIA GTX 1080 GPUs.

Current GPU usage focuses on:

- Ollama inference
- AI experimentation
- Embedding generation
- Model evaluation

GPU memory is independent for each device.

Applications must explicitly target the required GPU.

---

# 11. GPU Scheduling

GPU workloads require dedicated scheduling.

Future scheduling may use:

- Node Affinity
- Taints
- Tolerations
- NVIDIA Device Plugin

GPU-intensive workloads should avoid competing for the same device.

One GPU may be reserved for stable inference while the second is used for experimentation.

---

# 12. Workload Categories

The platform distinguishes several workload classes.

## Critical

Examples:

- Kubernetes Control Plane
- PostgreSQL
- Argo CD
- Core Platform Services

Priority:

Highest

---

## Platform

Examples:

- Airflow
- MLflow
- OpenMetadata
- Monitoring

Priority:

High

---

## AI

Examples:

- Ollama
- Embedding Services
- Future Qdrant

Priority:

Medium to High

---

## Business Applications

Examples:

- FastAPI
- React
- APIs
- Recommendation Engine

Priority:

Medium

---

## Experimental

Examples:

- AI testing
- Temporary workloads
- Research environments

Priority:

Lowest

---

# 13. Resource Requests and Limits

Every production deployment should define:

```yaml
resources:
  requests:
    cpu:
    memory:

  limits:
    cpu:
    memory:
```

Benefits include:

- Predictable scheduling
- Stable platform
- Fair resource sharing
- Better capacity planning

---

# 14. Namespace Resource Governance

Production namespaces should implement:

- ResourceQuota
- LimitRange

Objectives:

- Prevent uncontrolled resource consumption
- Isolate workloads
- Protect critical services

---

# 15. Horizontal Scaling

The platform supports horizontal scaling where appropriate.

Examples:

- FastAPI
- React
- Airflow workers
- Stateless APIs

Scaling remains limited by the fixed physical infrastructure.

---

# 16. Vertical Scaling

Stateful services may require vertical scaling.

Examples:

- PostgreSQL
- MLflow
- OpenMetadata

Vertical scaling should be validated before implementation.

---

# 17. Scheduling Strategy

Scheduling priorities are based on:

1. Platform stability
2. Data integrity
3. AI workloads
4. Business services
5. Experimental workloads

Critical services must always receive compute resources before optional workloads.

---

# 18. Monitoring

Compute resources are monitored through:

- Prometheus
- Grafana
- Kubernetes Metrics
- Node Exporter

Metrics include:

- CPU utilization
- Memory utilization
- Node pressure
- GPU utilization
- GPU temperature
- Pod restarts
- OOM events
- Scheduling failures

---

# 19. Performance Optimization

Optimization techniques include:

- Resource tuning
- Pod distribution
- Right-sizing workloads
- Model quantization
- Batch optimization
- Log retention
- Efficient scheduling
- Controlled concurrency

Optimization should precede requests for additional hardware.

---

# 20. Constraints

Current limitations include:

- Fixed CPU capacity
- Fixed RAM
- Two GPUs
- 8 GB VRAM per GPU
- Residential electrical environment
- Single Proxmox host

These constraints define the compute boundary of the platform.

---

# 21. Current State

Current compute capabilities include:

- Kubernetes workload scheduling
- Multi-node cluster
- CPU and memory resource management
- AI inference using Ollama
- GPU acceleration
- GitOps-managed deployments

The platform operates within a fixed-capacity infrastructure.

---

# 22. Target State

The target architecture focuses on improving efficiency rather than increasing hardware.

Future improvements include:

- GPU-aware scheduling
- Better workload distribution
- Improved resource dashboards
- Namespace quotas
- Performance benchmarking
- AI workload optimization

---

# 23. Architecture Decisions

Key compute decisions include:

- Kubernetes as the compute orchestrator
- Resource Requests and Limits for all production workloads
- Namespace resource governance
- Dedicated GPU workloads
- Compute optimization before hardware expansion
- Continuous monitoring of compute resources

---

# 24. Related Documents

- Infrastructure Architecture
- Physical Architecture
- Virtual Infrastructure
- Kubernetes Architecture
- Storage Architecture
- Capacity Planning
- AI Architecture
- Observability Architecture