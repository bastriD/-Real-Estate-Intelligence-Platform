# Backup and Restore Architecture

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the Backup and Restore Architecture of the Enterprise AI Platform.

It establishes the strategy, responsibilities, technologies, retention policies, validation procedures, and recovery mechanisms required to protect platform data and configuration against accidental deletion, corruption, infrastructure failure, security incidents, and operational errors.

The objective is not simply to create backups.

The objective is to ensure that critical platform assets are **recoverable within defined business requirements**.

---

# 2. Scope

This architecture applies to:

* Kubernetes resources
* PostgreSQL databases
* Application data
* Airflow
* MLflow
* MLflow artifacts
* OpenMetadata
* Git repositories
* GitOps configuration
* Kubernetes configuration
* Secrets
* Certificates
* Observability configuration
* AI models
* AI configuration
* Infrastructure configuration
* Platform documentation

---

# 3. Objectives

The Backup and Restore strategy aims to:

* Protect critical data
* Protect platform configuration
* Enable reliable restoration
* Minimize data loss
* Reduce recovery time
* Protect against accidental deletion
* Support disaster recovery
* Ensure backup integrity
* Provide auditable recovery procedures
* Validate backups through restore testing

---

# 4. Backup Principles

The platform follows these principles:

* Restore Capability Over Backup Quantity
* Automate Backups
* Test Restores Regularly
* Encrypt Sensitive Backups
* Separate Backups from Primary Systems
* Define Retention Explicitly
* Monitor Backup Execution
* Version Configuration in Git
* Protect Critical State
* Document Recovery Dependencies

A backup is considered operationally useful only when its restoration process has been validated.

---

# 5. Backup Architecture

```text
Platform Workloads
       │
       ├── Databases
       ├── Kubernetes State
       ├── Application Data
       ├── AI / ML Artifacts
       ├── Configuration
       └── Git Repositories
              │
              ▼
       Backup Processes
              │
              ▼
       Backup Storage
              │
              ▼
       Integrity Validation
              │
              ▼
       Retention Management
              │
              ▼
       Restore Testing
```

---

# 6. Backup vs High Availability

High Availability and backup solve different problems.

High Availability protects primarily against service interruption.

Backup protects against:

* Data deletion
* Logical corruption
* Configuration errors
* Ransomware
* Operator mistakes
* Failed upgrades
* Application corruption

Example:

```text
Replicated corrupted database
            =
Multiple copies of corrupted data
```

Replication therefore does not replace backup.

---

# 7. Backup vs Disaster Recovery

Backup provides recoverable copies of data and configuration.

Disaster Recovery defines how the entire service or platform is reconstructed after a major failure.

Relationship:

```text
Backup
   │
   ▼
Recoverable Data
   │
   ▼
Disaster Recovery Procedure
   │
   ▼
Reconstructed Platform
```

Backup is therefore one of the foundations of Disaster Recovery.

---

# 8. Backup Classification

Assets should be classified according to recoverability requirements.

## Tier 1 — Critical State

Examples:

* PostgreSQL databases
* Git repositories
* GitOps configuration
* Critical Kubernetes state
* Secrets
* MLflow metadata
* OpenMetadata metadata

Requires the strongest backup controls.

---

## Tier 2 — Important State

Examples:

* MLflow artifacts
* AI models
* Airflow metadata
* Application persistent data
* Platform documentation

Requires scheduled backup and restore validation.

---

## Tier 3 — Reconstructable State

Examples:

* Container images available from trusted registries
* Kubernetes Deployments stored in Git
* Helm charts
* CI/CD configuration
* Infrastructure configuration stored in repositories

These assets may be recreated from source-controlled definitions.

---

## Tier 4 — Disposable State

Examples:

* Temporary files
* Caches
* Ephemeral containers
* Regenerable logs
* Build workspaces

Backup is generally unnecessary.

---

# 9. Recovery Point Objective

Recovery Point Objective (RPO) defines the maximum acceptable amount of data loss measured in time.

Example targets:

| Service                       |      Example RPO |
| ----------------------------- | ---------------: |
| Critical PostgreSQL databases | 24 hours or less |
| Git repositories              |         24 hours |
| MLflow metadata               |         24 hours |
| ML artifacts                  |         24 hours |
| OpenMetadata                  |         24 hours |
| Platform configuration        | Git commit level |
| Observability historical data |      Best effort |

These values remain architecture targets until validated against actual business requirements.

---

# 10. Recovery Time Objective

Recovery Time Objective (RTO) defines the maximum targeted time required to restore a service.

Example targets:

| Service                       | Example RTO |
| ----------------------------- | ----------: |
| GitOps configuration          |      1 hour |
| Critical database             |     4 hours |
| Kubernetes applications       |     4 hours |
| MLflow                        |     8 hours |
| Airflow                       |     8 hours |
| OpenMetadata                  |     8 hours |
| Historical observability data | Best effort |

RTO targets must reflect available hardware and operational resources.

---

# 11. PostgreSQL Backup

PostgreSQL contains critical platform and business data.

Backup strategies may include:

* `pg_dump`
* `pg_dumpall`
* Physical backups
* Volume snapshots
* WAL archiving where required

Logical backup example:

```bash
pg_dump \
  --format=custom \
  --file=database.dump \
  database_name
```

Restore example:

```bash
pg_restore \
  --clean \
  --if-exists \
  --dbname=database_name \
  database.dump
```

Production procedures must obtain credentials from approved secret management mechanisms rather than hard-coded scripts.

---

# 12. Kubernetes Backup

Kubernetes contains both declarative and persistent state.

Declarative configuration should primarily exist in Git.

Examples:

* Deployments
* Services
* Ingress
* ConfigMaps
* Helm values
* Argo CD Applications
* NetworkPolicies
* RBAC configuration

Persistent state requires dedicated backup mechanisms.

Current or planned Kubernetes backup tooling may include:

* Velero
* CSI snapshots
* Application-aware database backups

---

# 13. Velero Strategy

Velero can protect Kubernetes resources and supported persistent volumes.

Typical scope includes:

```text
Namespaces
Deployments
Services
ConfigMaps
Secrets
Ingress
RBAC
PersistentVolumeClaims
PersistentVolumes
```

Backup operations should be scheduled and monitored.

Restore procedures should support:

* Namespace recovery
* Application recovery
* Cluster migration
* Disaster recovery

Velero must complement application-level database backup rather than replace it.

---

# 14. Git and GitOps Backup

Git provides one of the strongest recovery mechanisms within the architecture.

Repositories may contain:

* Kubernetes manifests
* Helm configuration
* Argo CD applications
* Infrastructure as Code
* CI/CD pipelines
* Application source code
* Airflow DAGs
* Governance policies
* Documentation

Git repositories therefore represent critical recovery assets.

They should not rely exclusively on a single GitLab instance.

Repository backups or mirrors should be maintained separately.

---

# 15. GitLab Backup

GitLab contains:

* Repositories
* Issues
* Merge requests
* CI/CD configuration
* User configuration
* Metadata

GitLab backup should protect both:

```text
Git Repository Data
+
GitLab Application Metadata
```

A repository clone alone does not represent a complete GitLab backup.

---

# 16. Airflow Backup

Airflow recovery requires protection of:

* DAG repositories
* Metadata database
* Configuration
* Connections
* Variables
* Required secrets

DAGs should remain version-controlled in Git.

The metadata database requires database-level backup.

Sensitive Airflow configuration must be handled through approved secret management.

---

# 17. MLflow Backup

MLflow contains two primary categories of state.

## Metadata

Includes:

* Experiments
* Runs
* Parameters
* Metrics
* Model registry information

This state is typically stored in the MLflow backend database.

## Artifacts

Includes:

* Model files
* Training outputs
* Evaluation artifacts

The architecture therefore requires:

```text
MLflow Backup
      │
      ├── Backend Database
      │
      └── Artifact Storage
```

Both must be recoverable to reconstruct the ML lifecycle.

---

# 18. AI Model Backup

AI assets may include:

* ML models
* Fine-tuned models
* Embedding models
* Model configuration
* Evaluation results
* Prompt templates

Models downloaded from external trusted registries may be reconstructable.

Internally trained or fine-tuned models should be treated as critical assets.

Model backups should preserve:

* Model version
* Checksum
* Training metadata
* Dataset reference
* Source code version
* Evaluation results

---

# 19. Ollama Model Recovery

Large base models can consume significant storage.

Backing up every downloaded model may therefore be inefficient.

Models that can be reliably retrieved from trusted sources may instead be documented using:

```text
Model Name
Model Version
Source
Checksum
Configuration
Deployment Parameters
```

Unique or customized models require actual artifact backup.

---

# 20. OpenMetadata Backup

OpenMetadata contains important governance information including:

* Metadata
* Lineage
* Ownership
* Data quality configuration
* Service definitions
* Governance relationships

Recovery must protect the underlying metadata database and any required search/index configuration.

Where indexes can be rebuilt from authoritative metadata, database state receives higher backup priority.

---

# 21. Observability Backup

Observability components include:

* Prometheus
* Grafana
* Loki
* Tempo

Not all historical telemetry requires long-term backup.

Priority should be given to configuration:

* Grafana dashboards
* Alert rules
* Prometheus configuration
* Loki configuration
* Tempo configuration
* OpenTelemetry configuration

Where possible, these should exist as code in Git.

Historical telemetry retention depends on operational and compliance requirements.

---

# 22. Secrets Backup

Secrets require special handling.

Examples include:

* Database passwords
* API tokens
* TLS private keys
* Application secrets
* Service credentials

Backups containing secrets must be:

* Encrypted
* Access controlled
* Audited
* Stored separately from general backups where appropriate

Plain-text secret backups are prohibited.

---

# 23. Certificate Recovery

cert-manager can regenerate many certificates when:

* Cluster configuration is available
* Issuer configuration is available
* DNS/network access is restored

Critical private certificate authorities or manually managed certificates require dedicated protected backup.

---

# 24. Backup Storage

Backups should not exist exclusively on the same storage system as production data.

Recommended architecture:

```text
Production Storage
        │
        ▼
Local Backup
        │
        ▼
Independent Backup Storage
        │
        ▼
Optional Off-Site Copy
```

This follows the principle of failure-domain separation.

---

# 25. 3-2-1 Backup Principle

Where feasible, critical assets should follow the 3-2-1 principle:

```text
3 copies of important data

2 different storage types or systems

1 copy outside the primary failure domain
```

For the current resource-constrained environment, implementation may be incremental.

The architectural principle remains the target.

---

# 26. Retention Strategy

Example retention policy:

```text
Daily backups      → 7 days

Weekly backups     → 4 weeks

Monthly backups    → 6–12 months
```

Retention should depend on:

* Business requirements
* Storage capacity
* Regulatory requirements
* Data sensitivity
* Recovery requirements

Not every dataset requires identical retention.

---

# 27. Backup Encryption

Sensitive backups should be encrypted:

* At rest
* During transfer

Encryption keys must be protected independently.

Losing the encryption key makes encrypted backups unrecoverable.

---

# 28. Backup Integrity

Backup integrity should be validated through:

* Checksums
* Backup job status
* File validation
* Database validation
* Artifact validation
* Storage monitoring

Successful job execution alone does not prove recoverability.

---

# 29. Restore Testing

Restore testing is mandatory for critical services.

Recommended process:

```text
Select Backup
      │
      ▼
Create Isolated Recovery Environment
      │
      ▼
Restore Data
      │
      ▼
Start Service
      │
      ▼
Validate Application
      │
      ▼
Validate Data
      │
      ▼
Record Result
```

Restore tests should record:

* Backup used
* Restore duration
* Errors encountered
* Data validation results
* Actual RPO
* Actual RTO
* Corrective actions

---

# 30. Restore Priority

During major recovery, services should be restored according to dependency order.

Example:

```text
1. Physical Infrastructure

2. Network

3. Kubernetes

4. Storage

5. Secrets / Certificates

6. GitLab / GitOps

7. Databases

8. Core Platform Services

9. Data Platform

10. AI Platform

11. Business Applications

12. Observability
```

The exact sequence depends on service dependencies.

---

# 31. Restore Validation

A restore is not complete when data has merely been copied.

Validation should verify:

* Service starts successfully
* Database integrity
* Application connectivity
* Authentication
* Data availability
* Model availability
* Pipeline execution
* API functionality
* Business functionality

Recovery should ultimately be validated from the business service perspective.

---

# 32. Backup Monitoring

Backup monitoring should include:

* Backup success
* Backup failure
* Backup duration
* Backup size
* Storage utilization
* Last successful backup
* Restore test status
* Retention compliance

Prometheus and Grafana may be used to expose backup health metrics.

---

# 33. Alerting

Alerts should be generated for:

* Failed backup
* Missing scheduled backup
* Backup storage exhaustion
* Corrupted backup
* Backup duration anomaly
* Restore validation failure
* Retention policy failure

Critical backup failures should create operational incidents.

---

# 34. Security

Backup systems represent high-value security targets.

Controls include:

* Least privilege
* Encryption
* Separate credentials
* Immutable storage where possible
* Audit logging
* Restricted deletion rights
* Network isolation where practical

Compromise of production credentials should not automatically grant the ability to destroy every backup.

---

# 35. Ransomware Considerations

Backup architecture should consider ransomware and malicious deletion.

Controls may include:

* Offline copies
* Immutable backups
* Separate administrative credentials
* Restricted deletion permissions
* Independent storage
* Multiple backup generations

Backup isolation is therefore a security requirement as well as an operational requirement.

---

# 36. Backup Ownership

Every critical backup should have an owner.

Example:

| Asset         | Responsibility    |
| ------------- | ----------------- |
| PostgreSQL    | Data / Platform   |
| Kubernetes    | Platform          |
| GitLab        | DevOps / Platform |
| MLflow        | MLOps / Platform  |
| Airflow       | Data Engineering  |
| OpenMetadata  | Data Governance   |
| AI Models     | AI / MLOps        |
| Observability | Platform / SRE    |

In the current project, responsibilities may be performed by the same person while remaining logically separated in the architecture.

---

# 37. Current Implementation

The current platform already contains important recoverability mechanisms:

* Git-based configuration
* GitLab repositories
* Argo CD GitOps
* Kubernetes declarative manifests
* PostgreSQL
* MLflow
* MinIO-backed artifacts
* Airflow
* OpenMetadata
* Prometheus
* Grafana
* Loki
* Tempo
* Velero namespace/platform capability

These provide a strong basis for a formal backup architecture.

---

# 38. Current Infrastructure Constraints

The physical infrastructure is intentionally fixed and resource constrained.

The platform therefore prioritizes:

* Critical data first
* Configuration-as-Code
* Efficient retention
* Deduplication where available
* Reconstructable assets over unnecessary copies
* Restore validation over excessive backup frequency

Large AI model files should not consume backup capacity when they can be reliably reconstructed from trusted sources.

Unique enterprise data must receive higher priority.

---

# 39. Future Evolution

Future improvements include:

* Formal backup schedules
* Automated PostgreSQL backups
* Automated Velero schedules
* GitLab backup automation
* MinIO replication or independent artifact backup
* Immutable backup storage
* Off-site backup
* Automated restore testing
* Backup dashboards
* RPO/RTO compliance reporting
* Backup encryption key lifecycle management

These improvements should be introduced according to risk and available resources.

---

# 40. Architecture Decisions

Key architectural decisions include:

* Git is the primary recovery source for declarative configuration
* Databases require application-aware backup
* Velero protects Kubernetes state but does not replace database backup
* Critical backups must cross failure domains
* Sensitive backups require encryption
* Reconstructable assets receive lower backup priority
* Unique AI artifacts require protection
* Restore testing is mandatory for critical data
* Backup success does not equal recovery success
* RPO and RTO must eventually be measured, not merely documented

---

# 41. Related Documents

* Infrastructure Architecture
* Kubernetes Architecture
* Data Architecture
* AI Platform Architecture
* Security Architecture
* Service Management
* Incident Management
* Availability Management
* Business Continuity
* Disaster Recovery
* SRE Practices
