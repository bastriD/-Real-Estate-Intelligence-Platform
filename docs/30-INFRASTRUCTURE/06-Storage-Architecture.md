# Storage Architecture

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-07-30

---

# 1. Purpose

This document defines the storage architecture of the Enterprise AI Platform.

It describes how persistent data is stored, managed, protected and maintained across Kubernetes workloads.

The architecture ensures reliable persistence for platform services, business applications and AI workloads while respecting the hardware constraints of the platform.

---

# 2. Scope

This document covers:

- Persistent Volumes
- Storage Classes
- Stateful workloads
- Object storage
- Database storage
- Backup storage
- Storage lifecycle
- Capacity management
- Disaster recovery integration

---

# 3. Storage Objectives

The storage platform is designed to provide:

- Data persistence
- Reliability
- Recoverability
- Predictable performance
- Resource efficiency
- Simple administration
- Platform portability

---

# 4. Storage Principles

The storage architecture follows these principles:

- Persistent data must never rely on container filesystems.
- Stateful workloads must use Persistent Volumes.
- Backups are mandatory for critical data.
- Storage growth must be monitored continuously.
- Data retention must be controlled.
- Storage is allocated according to business value.

---

# 5. Storage Layers

```
Business Applications
        │
Persistent Volumes
        │
Storage Classes
        │
Virtual Disks
        │
Physical Storage
```

Each layer abstracts the one below it.

---

# 6. Storage Consumers

Current persistent workloads include:

| Service | Data Stored |
|----------|-------------|
| PostgreSQL | Relational data |
| MinIO | Objects and ML artifacts |
| MLflow | Metadata and model registry |
| Airflow | Metadata database |
| OpenMetadata | Metadata repository |
| Grafana | Dashboards |
| Loki | Log indexes |
| Tempo | Trace data |
| GitLab | Repositories and registry |
| Velero | Backup metadata |

Each workload owns its storage and should not directly access another workload's data.

---

# 7. Persistent Volumes

Persistent Volumes provide durable storage independent of Pod lifecycle.

Responsibilities include:

- Data persistence
- Stateful application support
- Volume abstraction
- Recovery support

Pods may be recreated without data loss.

---

# 8. Persistent Volume Claims

Applications request storage through Persistent Volume Claims (PVCs).

Each PVC defines:

- Requested capacity
- Access mode
- Storage class

PVCs decouple workloads from physical storage implementation.

---

# 9. Storage Classes

Storage Classes define how storage is provisioned.

Responsibilities include:

- Dynamic provisioning
- Performance profile
- Volume lifecycle

Future Storage Classes may support different performance tiers if the infrastructure evolves.

---

# 10. Database Storage

PostgreSQL stores:

- Platform metadata
- Business data
- Configuration
- Application data

Requirements:

- Persistent storage
- Backup integration
- Controlled growth
- Periodic maintenance

Database files must never be stored inside ephemeral containers.

---

# 11. Object Storage

MinIO provides S3-compatible object storage.

Current usage includes:

- MLflow artifacts
- Datasets
- Backup archives
- Documents
- Future media assets

Object storage complements relational storage rather than replacing it.

---

# 12. AI Storage

AI workloads persist:

- Trained models
- Model versions
- Embeddings (future)
- Evaluation reports
- Prompt templates (future)
- Experiment artifacts

These assets are managed through MLflow and object storage.

---

# 13. Monitoring Data

Observability components generate persistent data:

- Metrics
- Logs
- Traces

Retention policies prevent uncontrolled storage growth.

---

# 14. Storage Lifecycle

Every dataset follows the same lifecycle.

```
Create

↓

Use

↓

Maintain

↓

Archive

↓

Delete
```

Storage should not accumulate obsolete information indefinitely.

---

# 15. Backup Integration

Critical persistent data is protected through:

- Velero
- Database dumps
- Git repositories
- Object storage backups

Backups are validated through restoration testing.

Snapshots are complementary and do not replace backups.

---

# 16. Capacity Management

Storage usage is continuously monitored.

Key indicators include:

- Disk utilization
- PVC growth
- Database size
- Object storage usage
- Log growth
- Backup size
- Artifact growth

Alerts should be configured before storage exhaustion occurs.

---

# 17. Data Retention

Retention policies should define:

- Metrics retention
- Log retention
- Trace retention
- ML artifacts
- Temporary datasets
- Backups

Retention periods must balance operational needs with available capacity.

---

# 18. Storage Security

Persistent data is protected through:

- Kubernetes RBAC
- Namespace isolation
- TLS for network communication
- Backup protection
- Access control

Future enhancements may include encryption at rest and immutable backups.

---

# 19. Failure Scenarios

| Failure | Recovery Strategy |
|----------|-------------------|
| PVC corruption | Restore from backup |
| Database corruption | Restore database dump |
| Object loss | Restore object storage backup |
| Disk saturation | Capacity cleanup and expansion planning |
| Accidental deletion | Restore from backup |
| Storage node failure | Recover using documented procedures |

---

# 20. Constraints

Current platform limitations include:

- Fixed physical storage capacity
- Single physical host
- Local storage only
- Shared storage resources

Storage architecture prioritizes efficient use of existing resources over hardware expansion.

---

# 21. Architecture Decisions

Key storage decisions include:

- Kubernetes Persistent Volumes for stateful workloads
- Persistent Volume Claims for application storage
- PostgreSQL for relational persistence
- MinIO for object storage
- MLflow artifact storage in MinIO
- Backup-first strategy
- Controlled retention policies
- Continuous capacity monitoring

---

# 22. Current State

Current storage architecture includes:

- Kubernetes Persistent Volumes
- Persistent Volume Claims
- PostgreSQL persistent data
- MinIO object storage
- MLflow artifacts
- Airflow metadata
- OpenMetadata repository
- Grafana persistence
- Loki storage
- Tempo storage
- Velero backup metadata

The storage platform successfully supports all current workloads.

---

# 23. Target State

The target storage architecture focuses on operational maturity rather than new hardware.

Future improvements include:

- Better storage monitoring
- Automated retention policies
- Capacity forecasting
- Storage usage dashboards
- Backup validation automation
- Storage governance

---

# 24. Related Documents

- Infrastructure Architecture
- Physical Architecture
- Virtual Infrastructure
- Kubernetes Architecture
- Data Architecture
- Disaster Recovery Plan
- Capacity Planning
- Backup Strategy
- Observability Architecture