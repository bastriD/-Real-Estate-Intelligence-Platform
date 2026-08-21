# Disaster Recovery Operations

**Version:** 1.0
**Status:** Draft
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Last Updated:** 2026-08-21

---

# 1. Purpose

This document defines the operational Disaster Recovery (DR) procedures of the Enterprise AI Platform.

It describes how the platform is assessed, reconstructed, restored, validated, and returned to normal operation following a major technical disaster.

The objective is to transform the Disaster Recovery architecture into a repeatable operational recovery process.

This document focuses on execution.

---

# 2. Scope

This procedure applies to disasters affecting:

* Physical infrastructure
* Proxmox virtualization
* Kubernetes cluster
* Networking
* Persistent storage
* GitLab
* Argo CD
* PostgreSQL
* Airflow
* MLflow
* MinIO
* OpenMetadata
* Observability
* AI services
* Business applications

---

# 3. Disaster Recovery Objectives

Disaster Recovery aims to:

* Restore essential infrastructure
* Restore critical data
* Reconstruct the Kubernetes platform
* Re-establish GitOps
* Recover business applications
* Recover data and AI services
* Validate integrity
* Minimize business downtime
* Preserve auditability
* Prevent recovery from introducing additional damage

---

# 4. Recovery Principles

The platform follows these principles:

* Safety Before Speed
* Contain Before Restore
* Recover Dependencies First
* Restore Critical Services First
* Git as the Configuration Source of Truth
* Validate Every Recovery Stage
* Do Not Trust an Unknown Recovery Point
* Do Not Restore Compromised State Blindly
* Document Every Recovery Action
* Business Validation Ends the Recovery

---

# 5. Disaster Definition

A disaster is an event that cannot reasonably be resolved using normal incident procedures.

Examples include:

* Complete Kubernetes cluster loss
* Proxmox host failure
* Major storage corruption
* Critical database loss
* Severe ransomware event
* Complete GitLab failure
* Major network infrastructure failure
* Multiple simultaneous infrastructure failures
* Platform state corruption
* Destructive administrative error

---

# 6. Disaster Severity

## DR1 — Component Disaster

Examples:

* PostgreSQL corruption
* MLflow loss
* GitLab failure

Most platform services remain operational.

---

## DR2 — Platform Disaster

Examples:

* Kubernetes unavailable
* Major storage failure
* GitOps platform lost

Requires reconstruction of significant platform components.

---

## DR3 — Infrastructure Disaster

Examples:

* Proxmox host failure
* Major physical disk failure
* Complete virtualization loss

Requires rebuilding infrastructure before platform recovery.

---

## DR4 — Security Disaster

Examples:

* Ransomware
* Privileged credential compromise
* Supply-chain compromise
* Malicious platform modification

Recovery requires containment and identification of a trusted recovery point before restoration.

---

# 7. DR Activation Criteria

Disaster Recovery should be activated when:

* Critical service recovery exceeds normal incident procedures
* The Kubernetes control plane cannot be recovered normally
* Critical storage is unavailable
* Primary infrastructure has been lost
* Multiple Tier-1 services fail simultaneously
* Recovery requires reconstruction rather than restart
* Cybersecurity containment requires platform isolation
* Incident management formally escalates to disaster status

---

# 8. Recovery Leadership

During a disaster, responsibilities should be explicit.

## Disaster Recovery Coordinator

Responsible for:

* DR activation
* Recovery coordination
* Priority management
* Status communication
* Recovery closure

## Platform Engineer

Responsible for:

* Proxmox
* Virtual machines
* Kubernetes
* GitOps
* Networking
* Storage integration

## Data Engineer

Responsible for:

* PostgreSQL
* Airflow
* Data integrity
* OpenMetadata
* Data pipeline validation

## AI / MLOps Engineer

Responsible for:

* MLflow
* Model artifacts
* Ollama
* AI services
* GPU validation

## Security Owner

Responsible for:

* Security containment
* Trusted recovery point validation
* Credential rotation
* Security validation

## Business Owner

Responsible for:

* Recovery priorities
* Business workaround decisions
* Business functionality validation

In the current project these roles may be performed by the same person while remaining logically distinct.

---

# 9. Recovery Command Structure

The recovery process should follow a controlled sequence.

```text
Incident Manager / DR Coordinator
              │
              ├── Infrastructure Recovery
              │
              ├── Kubernetes Recovery
              │
              ├── Data Recovery
              │
              ├── AI Recovery
              │
              └── Business Validation
```

Parallel recovery should occur only where dependencies permit.

---

# 10. Disaster Recovery Lifecycle

```text
Disaster Detected
       │
       ▼
Assess
       │
       ▼
Contain
       │
       ▼
Select Trusted Recovery Point
       │
       ▼
Recover Infrastructure
       │
       ▼
Recover Platform
       │
       ▼
Recover Data
       │
       ▼
Recover Applications
       │
       ▼
Validate
       │
       ▼
Return to Service
       │
       ▼
Post-Disaster Review
```

---

# 11. Initial Assessment

Before restoration begins, determine:

* What failed?
* What remains operational?
* Is data corruption present?
* Is the incident security-related?
* Is the primary storage trustworthy?
* Are backups available?
* Are Git repositories available?
* Is network infrastructure operational?
* Is physical hardware usable?
* Which recovery tier applies?

No restoration should begin before the failure scope is understood.

---

# 12. Containment

Containment protects remaining healthy systems.

Actions may include:

* Isolate compromised hosts
* Disable network access
* Revoke credentials
* Suspend Argo CD synchronization
* Disable CI/CD pipelines
* Stop database writes
* Preserve logs
* Preserve forensic evidence
* Disconnect corrupted storage
* Freeze affected Git branches

Containment is especially important for cybersecurity incidents.

---

# 13. Trusted Recovery Point

A trusted recovery point is the latest state known to be healthy.

Potential sources include:

* Validated database backup
* Known-good Git commit
* Signed container image
* Previous Helm release
* Verified MLflow model version
* Known-good VM backup
* Validated Velero backup

For security incidents, "latest" is not automatically "best."

The recovery point must predate the compromise.

---

# 14. Recovery Priority

Recommended platform recovery order:

```text
1. Physical Infrastructure
2. Network
3. Virtualization
4. Kubernetes Control Plane
5. Kubernetes Workers
6. Storage
7. Secrets / Certificates
8. GitLab / Git
9. Argo CD / GitOps
10. PostgreSQL
11. Core Platform Services
12. Data Platform
13. AI Platform
14. Business Applications
15. Observability
16. Non-Critical Services
```

Dependencies may require limited adjustments.

---

# 15. Minimum Viable Recovery

The entire platform does not need to be restored before business service resumes.

The Minimum Viable Platform should prioritize:

```text
Network
+
Kubernetes
+
Storage
+
Secrets
+
PostgreSQL
+
Ingress
+
Core Business API
```

Then restore optional services progressively.

---

# 16. Physical Infrastructure Recovery

If hardware remains available:

* Verify hardware health
* Verify disks
* Verify memory
* Verify network
* Verify GPU availability
* Verify cooling and power stability

If hardware failed:

* Replace failed component where possible
* Restore Proxmox environment
* Reattach surviving storage
* Restore VM backups

Physical limitations of the platform must be respected.

No recovery plan assumes immediate access to additional servers or GPUs.

---

# 17. Proxmox Recovery

Recovery activities may include:

1. Install or restore Proxmox VE.
2. Restore network bridge configuration.
3. Restore storage configuration.
4. Validate host networking.
5. Restore VM backups.
6. Validate VM startup.
7. Confirm Kubernetes node connectivity.

Recommended validation:

```bash
ip addr
ip route
ping <gateway>
```

VM recovery should prioritize Kubernetes control planes and critical workers.

---

# 18. Kubernetes Control Plane Recovery

If sufficient control-plane nodes remain healthy, restore quorum before rebuilding unnecessary nodes.

Validation:

```bash
kubectl get nodes
kubectl get pods -A
kubectl get --raw='/readyz?verbose'
```

Expected outcome:

* Kubernetes API available
* etcd quorum available
* CoreDNS operational
* Scheduler operational
* Controller Manager operational

If the entire cluster is lost, perform full cluster reconstruction.

---

# 19. Full Kubernetes Reconstruction

General sequence:

```text
Operating Systems
      │
      ▼
Container Runtime
      │
      ▼
kubeadm Control Plane
      │
      ▼
Additional Control Planes
      │
      ▼
CNI
      │
      ▼
Worker Nodes
      │
      ▼
Ingress
      │
      ▼
cert-manager
      │
      ▼
Argo CD
```

The exact installation steps must be documented in the Kubernetes runbook.

---

# 20. Kubernetes Network Recovery

Restore:

* Node routing
* Flannel CNI
* CoreDNS
* Required static routes
* Ingress networking

Validation:

```bash
kubectl get pods -n kube-system
kubectl get svc -A
kubectl get ingress -A
```

Test Pod-to-Pod and Pod-to-Service connectivity before restoring higher-level applications.

---

# 21. Storage Recovery

Before attaching recovered stateful workloads:

* Validate underlying disks
* Validate storage paths
* Validate StorageClasses
* Validate PersistentVolumes
* Validate PersistentVolumeClaims

Commands:

```bash
kubectl get storageclass
kubectl get pv
kubectl get pvc -A
```

Do not attach corrupted persistent data blindly.

---

# 22. Secrets and Certificate Recovery

Restore:

* Required Kubernetes Secrets
* Service credentials
* TLS issuer configuration
* cert-manager
* Critical private keys where required

Validate:

```bash
kubectl get secrets -A
kubectl get clusterissuer
kubectl get certificates -A
```

After a security incident, affected credentials should be rotated rather than simply restored.

---

# 23. GitLab Recovery

If GitLab is lost:

1. Restore GitLab service.
2. Restore repositories.
3. Restore GitLab metadata.
4. Restore registry configuration.
5. Validate Git access.
6. Validate CI/CD.
7. Validate GitLab Runner.

Git repositories are critical because they contain much of the platform's recoverable desired state.

---

# 24. GitOps Bootstrap

Argo CD should be restored early.

Recovery sequence:

```text
Install Argo CD
      │
      ▼
Restore Repository Credentials
      │
      ▼
Restore Root Application
      │
      ▼
Sync GitOps Repository
      │
      ▼
Reconcile Platform Services
```

Validate:

```bash
kubectl -n argocd get pods
kubectl -n argocd get applications
```

Do not enable unrestricted automatic synchronization until the recovered repositories and cluster state are confirmed trustworthy.

---

# 25. PostgreSQL Recovery

PostgreSQL receives highest data recovery priority.

Procedure:

1. Provision PostgreSQL.
2. Validate storage.
3. Create database.
4. Restore latest trusted backup.
5. Validate schemas.
6. Validate row counts.
7. Validate critical constraints.
8. Validate application connectivity.

Example:

```bash
pg_restore \
  --clean \
  --if-exists \
  --dbname=<database> \
  <backup-file>
```

Credentials must come from approved secret storage.

---

# 26. PostgreSQL Validation

Validation should include:

```sql
SELECT current_database();

SELECT COUNT(*) FROM <critical_table>;
```

Additional validation:

* Schema versions
* Referential integrity
* Critical business records
* Application login
* Write test where appropriate

Do not declare the database recovered based only on process startup.

---

# 27. Airflow Recovery

Restore:

* Helm / GitOps definition
* DAG repositories
* Metadata database
* Connections
* Variables
* Required secrets

Validate:

```bash
kubectl -n airflow get pods
```

Then verify:

* Scheduler healthy
* Webserver accessible
* DAGs loaded
* Critical DAG can execute
* Database connectivity works

---

# 28. MLflow Recovery

Restore:

```text
MLflow Backend Database
+
MinIO / Artifact Storage
```

Validation:

* MLflow UI reachable
* Experiments visible
* Model Registry available
* Production model versions present
* Model artifacts downloadable

A model registry without artifacts is incomplete.

---

# 29. MinIO Recovery

Restore:

* Buckets
* Objects
* Access configuration
* Required credentials

Validate:

* Artifact listing
* Artifact retrieval
* MLflow access
* Object integrity

Unique AI and ML artifacts receive higher priority than externally reproducible base models.

---

# 30. OpenMetadata Recovery

Restore:

* OpenMetadata service
* Database
* Search/index dependencies
* Ingestion configurations

Validate:

* UI availability
* Data services
* Metadata catalog
* Ownership
* Lineage
* Quality configuration

Rebuild derived indexes where practical instead of treating them as irreplaceable primary data.

---

# 31. AI Infrastructure Recovery

Validate AI resources:

```bash
nvidia-smi
```

Confirm:

* Both available GTX 1080 GPUs recognized where applicable
* CUDA operational
* Driver operational
* Required model runtime available

The two 8 GB GPUs must be treated as separate constrained resources.

---

# 32. Ollama Recovery

Recovery includes:

* Restore Ollama service
* Restore configuration
* Download or restore required models
* Validate remote inference access

Example validation:

```bash
curl http://<ollama-host>:11434/api/tags
```

Models available from trusted upstream sources may be re-downloaded instead of restored from backup.

Custom or fine-tuned models require artifact recovery.

---

# 33. AI Service Validation

Validate:

* AI API availability
* Model loading
* Inference
* Latency
* Authentication
* Observability

Use a known deterministic smoke-test prompt where possible.

Example expected validation:

```text
Model receives request
→ returns response
→ response is logged
→ trace is generated
→ metrics are emitted
```

---

# 34. Business Application Recovery

Restore through GitOps where possible.

Validation should include:

* Frontend availability
* API availability
* Authentication
* Database connectivity
* CRUD operations
* Critical business workflow
* Optional AI functionality

Business functionality receives priority over supporting platform UI services.

---

# 35. Observability Recovery

Restore:

* Prometheus
* Grafana
* Loki
* Tempo
* OpenTelemetry Collector
* Alertmanager

Configuration should primarily come from Git.

Historical telemetry may receive lower recovery priority than current monitoring capability.

The critical objective is to regain visibility into the recovered platform.

---

# 36. Recovery Validation Gates

Each recovery stage should have a validation gate.

Example:

```text
Infrastructure Healthy?
        │
       YES
        ▼
Kubernetes Healthy?
        │
       YES
        ▼
Storage Healthy?
        │
       YES
        ▼
Database Healthy?
        │
       YES
        ▼
Application Healthy?
        │
       YES
        ▼
Business Validation
```

Failure at any gate should stop dependent recovery activities until the issue is understood.

---

# 37. Technical Validation Checklist

Before service restoration:

* Kubernetes nodes Ready
* CoreDNS operational
* Ingress operational
* TLS operational
* Storage mounted
* PostgreSQL validated
* GitOps synchronized
* Critical Pods healthy
* Application endpoints healthy
* Backups operational again
* Monitoring operational

---

# 38. Business Validation

Technical recovery alone is insufficient.

Business validation should confirm:

* Users can authenticate
* Critical data is present
* Business transactions work
* Required workflows operate
* Reports show expected data
* AI features work or are intentionally degraded
* No unreconciled critical data remains

Only then can the business service be declared recovered.

---

# 39. Failback

If recovery occurred on temporary infrastructure, failback must be controlled.

Procedure:

```text
Stabilize Recovery Environment
       │
       ▼
Prepare Primary Environment
       │
       ▼
Synchronize Data
       │
       ▼
Validate Primary
       │
       ▼
Controlled Cutover
       │
       ▼
Validate Business Service
       │
       ▼
Retire Temporary Environment
```

Failback is a change and must follow Change Management procedures.

---

# 40. Recovery Evidence

Every DR event or test should preserve:

* Incident timeline
* Commands executed
* Backup versions used
* Git commits used
* Restore duration
* Validation results
* RPO achieved
* RTO achieved
* Problems encountered
* Corrective actions

This evidence supports governance and continuous improvement.

---

# 41. DR Testing

Disaster Recovery must be tested progressively.

## Level 1 — Backup Restore Test

Restore an individual asset.

## Level 2 — Service Recovery

Restore one platform service completely.

## Level 3 — Kubernetes Application Recovery

Reconstruct a namespace or application.

## Level 4 — Platform Recovery

Recover major platform layers.

## Level 5 — Full Disaster Simulation

Assume complete platform loss and reconstruct from backups, Git, and documentation.

---

# 42. Recommended DR Test Scenarios

Examples:

### Test A

Delete a non-production namespace and restore with Velero.

### Test B

Restore PostgreSQL into an isolated database instance.

### Test C

Reinstall Argo CD and recover applications from the root GitOps repository.

### Test D

Simulate one worker-node failure.

### Test E

Rebuild a disposable Kubernetes worker from scratch.

### Test F

Recover MLflow metadata and validate model artifacts.

These exercises prove recoverability incrementally without placing the complete environment at unnecessary risk.

---

# 43. Security Disaster Procedure

For suspected compromise:

1. Isolate affected systems.
2. Disable compromised accounts.
3. Suspend automated deployment if required.
4. Preserve forensic evidence.
5. Identify initial compromise time.
6. Select recovery point predating compromise.
7. Rotate credentials.
8. Restore clean systems.
9. Validate security configuration.
10. Reconnect services gradually.
11. Increase monitoring.
12. Conduct security review.

Security recovery prioritizes trustworthiness over speed.

---

# 44. DR Metrics

Recommended metrics include:

* RTO achieved
* RPO achieved
* Restore success rate
* Backup validation success
* Recovery test completion rate
* Mean recovery duration
* Number of manual recovery steps
* Number of failed recovery dependencies
* Recovery documentation coverage

---

# 45. Automation Opportunities

Future automation may include:

* Automated PostgreSQL restore tests
* Automated Velero recovery testing
* GitOps bootstrap automation
* Kubernetes bootstrap automation
* Automated health validation
* DR orchestration pipelines
* Credential rotation workflows
* Automated evidence generation

Automation should reduce repetitive tasks without eliminating required safety gates.

---

# 46. Current Recovery Strengths

The architecture already provides several strong recovery mechanisms:

* Declarative Kubernetes configuration
* GitLab repositories
* Argo CD
* GitOps reconciliation
* PostgreSQL backup capability
* Velero
* MLflow
* MinIO
* Airflow
* OpenMetadata
* Centralized documentation
* Observability platform

These considerably reduce the amount of infrastructure that must be reconstructed manually.

---

# 47. Current Recovery Constraints

Current limitations include:

* Fixed physical infrastructure
* Shared physical failure domains
* Single-site operation
* Limited spare hardware
* Two GTX 1080 GPUs with 8 GB VRAM each
* No assumption of immediate hardware expansion

Recovery strategy must therefore focus on:

* Reconstructability
* Data protection
* Workload prioritization
* Minimum viable platform
* Efficient use of existing resources

---

# 48. Future Evolution

Planned improvements include:

* Formal automated DR tests
* Off-site backup copies
* Immutable backup storage
* Automated cluster bootstrap
* Infrastructure-as-Code for Proxmox VMs
* Formal RPO/RTO dashboards
* Recovery automation
* Dependency-aware recovery orchestration
* Automated credential rotation
* DR evidence generation

These improvements increase recovery confidence without requiring architectural redesign.

---

# 49. Architecture Decisions

Key operational DR decisions include:

* Containment precedes restoration
* Restore from trusted recovery points only
* Dependency order controls recovery order
* GitOps is the primary platform reconstruction mechanism
* Databases require application-aware restore
* MLflow requires both metadata and artifact recovery
* Re-download reproducible base models instead of unnecessarily backing them up
* Minimum Viable Platform is restored before the full platform
* Observability must be restored early enough to validate recovery
* Business validation closes the DR process
* Failback is governed as a production change
* DR procedures must be tested, not assumed

---

# 50. Related Documents

* Infrastructure Disaster Recovery Architecture
* Backup and Restore
* Business Continuity
* High Availability
* Availability Management
* Incident Management
* Problem Management
* Change Management
* Kubernetes Architecture
* Data Architecture
* AI Platform Architecture
* Security Architecture
* SRE Practices
