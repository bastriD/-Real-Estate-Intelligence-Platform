# PCA / PRA — PostgreSQL Backup, Restore and GitOps Automation

## Enterprise Real Estate Intelligence Platform

**Project:** Chasse Immobilière — Fil Rouge Data & IA
**Scope:** BC02 — Infrastructure, resilience, continuity and disaster recovery
**Platform:** Kubernetes / PostgreSQL / MinIO / GitLab CI / Argo CD
**Namespace:** `real-estate`
**Date:** September 2026

---

# 1. Purpose

This document describes the implementation and runtime validation of the PostgreSQL disaster-recovery strategy for the Real Estate platform.

The objective is to ensure that the business database can be:

1. backed up outside its Kubernetes persistent volume;
2. stored in dedicated external object storage;
3. protected using a least-privilege backup identity;
4. validated before being considered usable;
5. restored into a clean PostgreSQL instance;
6. checked against the production business-data baseline;
7. automated through a permanent Kubernetes CronJob;
8. managed through the existing GitOps deployment architecture.

The work forms part of the platform's **PCA/PRA — Plan de Continuité d'Activité / Plan de Reprise d'Activité** strategy.

---

# 2. Initial Situation

## 2.1 PostgreSQL architecture

The Real Estate PostgreSQL database was inspected directly from the Kubernetes cluster.

Observed architecture:

* Kubernetes namespace: `real-estate`
* PostgreSQL image: `postgres:16`
* Workload: Kubernetes Deployment
* PostgreSQL replicas: `1`
* Service: `real-estate-postgresql`
* Port: `5432`
* PersistentVolumeClaim: `real-estate-postgresql-pvc`
* Capacity: `5Gi`
* Access mode: `RWO`
* StorageClass: `local-path`

The StorageClass uses:

```text
Provisioner: rancher.io/local-path
ReclaimPolicy: Delete
VolumeBindingMode: WaitForFirstConsumer
```

No PostgreSQL replication or database-level HA mechanism was evidenced.

No automated PostgreSQL backup CronJob was present before this implementation.

---

# 3. Initial Risk Analysis

The existing PostgreSQL deployment provides persistence across normal Pod restarts because the database uses a PVC.

However, this alone is not a PRA.

Deleting or recreating the PostgreSQL Pod is not a meaningful disaster-recovery test because the same persistent volume remains available.

The important failure scenarios are instead:

* PVC loss;
* node/storage loss;
* database corruption;
* accidental destructive operation;
* failure requiring reconstruction of PostgreSQL from an independent copy.

The original architecture therefore had the following major risk:

```text
PostgreSQL
    |
    v
local-path PVC
    |
    v
Single storage dependency
```

A second independent copy of the database was required.

---

# 4. Existing Object Storage Discovery

The Kubernetes namespaces were inspected for MinIO workloads.

No MinIO server was found running inside Kubernetes.

Further investigation of the existing MLflow configuration showed that the platform already uses an **external MinIO instance**.

The endpoint is:

```text
http://minio.lab.local:9000
```

Cluster DNS resolved:

```text
minio.lab.local
        |
        v
192.168.1.117
```

The MinIO health endpoint responded successfully with HTTP 200.

This established that MinIO could be used as storage external to the PostgreSQL Kubernetes PVC.

---

# 5. Existing MinIO Storage

The MinIO server already contained the following buckets:

```text
airflow/
loki/
mlflow/
real-estate/
tempo/
velero/
```

The existing `real-estate` bucket was inspected.

It already contained project data such as:

```text
raw/generated/...
```

Observed configuration:

* access: private;
* anonymous access: disabled;
* versioning: disabled;
* ILM: disabled;
* approximately 15 MiB;
* approximately 15,030 objects.

Because this bucket already has a data-platform responsibility, PostgreSQL PRA backups were deliberately **not mixed with the normal Real Estate data lake objects**.

---

# 6. Dedicated PRA Backup Bucket

A dedicated MinIO bucket was created:

```text
real-estate-backups
```

The bucket was configured as:

```text
Private access      : enabled
Anonymous access    : disabled
Versioning          : enabled
ILM                  : not yet configured
```

The intended PostgreSQL hierarchy is:

```text
real-estate-backups/
└── postgresql/
    ├── real_estate-<timestamp>.dump
    └── real_estate-<timestamp>.dump.sha256
```

Separating operational backups from raw project data provides:

* clearer ownership;
* independent access control;
* easier retention management;
* easier PRA evidence;
* reduced risk of accidental cross-access;
* future lifecycle-policy isolation.

---

# 7. Bucket Versioning

Versioning was explicitly enabled on:

```text
real-estate-backups
```

This was runtime verified.

Versioning provides additional protection against accidental replacement or deletion of backup objects.

During the access-control test, deletion of a test object created a MinIO delete marker with a Version ID, confirming versioning behavior at runtime.

---

# 8. Least-Privilege MinIO Policy

A dedicated policy was created:

```text
real-estate-backup-policy
```

The policy grants bucket-level permissions only against:

```text
arn:aws:s3:::real-estate-backups
```

with:

```text
s3:GetBucketLocation
s3:ListBucket
```

Object-level permissions apply only to:

```text
arn:aws:s3:::real-estate-backups/*
```

with:

```text
s3:GetObject
s3:PutObject
s3:DeleteObject
```

The policy does not grant general access to the other MinIO buckets.

The policy was inspected after creation and its effective configuration was confirmed.

---

# 9. Dedicated Backup Identity

A dedicated MinIO identity was created:

```text
real-estate-backup
```

It was attached only to:

```text
real-estate-backup-policy
```

Runtime verification showed:

```text
Status     : enabled
Policy     : real-estate-backup-policy
Membership : none
```

This means the backup process does not need to reuse an administrative MinIO account.

---

# 10. Credential Rotation

During the initial setup, the first generated backup credential became visible during interactive testing.

It was therefore treated as exposed.

The credential was immediately rotated by:

1. generating a new random secret;
2. recreating the dedicated backup identity;
3. reattaching the least-privilege policy;
4. creating a Kubernetes Secret with the rotated credential.

The rotated secret value was not included in project documentation or committed to Git.

---

# 11. Kubernetes Backup Secret

The backup credentials are exposed to Kubernetes workloads through:

```text
real-estate-backup-s3
```

Namespace:

```text
real-estate
```

Type:

```text
Opaque
```

The Secret contains:

```text
AWS_ACCESS_KEY_ID
AWS_ENDPOINT_URL
AWS_SECRET_ACCESS_KEY
S3_BUCKET
```

The values are not stored in the Git repository.

The PostgreSQL backup workload also uses the existing:

```text
real-estate-postgresql-secret
```

with:

```text
POSTGRES_DB
POSTGRES_HOST
POSTGRES_PASSWORD
POSTGRES_PORT
POSTGRES_USER
```

---

# 12. Least-Privilege Runtime Test

A temporary MinIO client Pod was created to validate the dedicated backup identity.

The Pod consumed:

```text
real-estate-backup-s3
```

through Kubernetes Secret injection.

The following operations were tested.

## Allowed bucket listing

Access to:

```text
real-estate-backups
```

succeeded.

## Write test

A test object was successfully uploaded:

```text
real-estate-backups/pra-validation/pra-test.txt
```

## Read test

The object was downloaded/read successfully.

Expected content was recovered:

```text
PRA access validation
```

## Cross-bucket security test

The same identity attempted to access:

```text
real-estate
```

The operation returned:

```text
Access Denied
```

This proves that the dedicated identity cannot use its backup credentials to access the normal Real Estate data bucket.

## Cleanup

The test object was deleted.

Because bucket versioning was enabled, MinIO returned a delete marker and Version ID.

The temporary test Pod completed successfully and was subsequently deleted.

### Result

| Test                           | Result             |
| ------------------------------ | ------------------ |
| Backup bucket access           | PASS               |
| Object upload                  | PASS               |
| Object read                    | PASS               |
| Access to `real-estate` bucket | DENIED as expected |
| Object cleanup                 | PASS               |
| Versioning behavior            | PASS               |

---

# 13. Vault Investigation

The cluster was inspected to determine whether backup credentials could immediately be managed through Vault.

A Vault Agent Injector was found:

```text
vault-agent-injector
```

However, the `real-estate` namespace had:

* no Vault annotations;
* no dedicated Vault-enabled ServiceAccount;
* no demonstrated Vault server integration for this workload.

No SealedSecret, ExternalSecret, SecretStore or ClusterSecretStore mechanism was evidenced for this namespace.

Therefore Vault was **not introduced as a dependency of the PRA implementation**.

Current decision:

```text
Kubernetes Secret now
        |
        v
Vault / external secret integration later
```

This prevents an unrelated secret-management migration from blocking disaster-recovery implementation.

---

# 14. Production Database Size

Before testing backup and restore, the production database size was measured.

Observed database:

```text
real_estate
```

Approximate size:

```text
47 MB
```

Exact observed value:

```text
49,462,295 bytes
```

This established the scale of the recovery test.

---

# 15. PostgreSQL Backup Test

A temporary Kubernetes Job was created to perform the first controlled PostgreSQL backup.

The backup used:

```text
postgres:16
```

and:

```text
pg_dump
```

with:

```text
--format=custom
--compress=6
```

The generated file was approximately:

```text
4.3 MiB
```

---

# 16. Backup Structural Validation

A backup is not considered valid merely because a file exists.

Immediately after `pg_dump`, the dump was inspected using:

```text
pg_restore --list
```

The resulting restore catalogue contained:

```text
394 entries
```

The backup file was also checked to ensure that it was non-empty.

Therefore the backup process validated the dump before uploading it to external storage.

---

# 17. Upload to MinIO

The validated PostgreSQL dump was uploaded to:

```text
real-estate-backups/postgresql/
```

The runtime test created:

```text
postgresql/real_estate-20260909T210700Z.dump
```

Observed remote properties included:

```text
Size      : approximately 4.3 MiB
VersionID : d87a1721-910a-469b-8e49-1a2d260ffa00
```

The object was successfully inspected using MinIO tooling after upload.

This backup object was deliberately retained as PRA evidence.

---

# 18. Production Business Baseline

Before restoring the database, a business-data baseline was captured from production.

Observed counts:

| Table             |   Rows |
| ----------------- | -----: |
| `audit_log`       |     10 |
| `bien`            | 14,000 |
| `client`          |     18 |
| `demande`         |     87 |
| `demande_version` |     88 |
| `mandat`          |     17 |
| `presentation`    |     12 |
| `visite`          |      1 |

These counts became the reference for the restore integrity test.

---

# 19. Isolated Restore Environment

The production database and production PVC were **not destroyed or modified** for the PRA test.

Instead, an isolated PostgreSQL 16 environment was created using temporary Kubernetes resources:

```text
Deployment:
real-estate-postgresql-restore-test

Service:
real-estate-postgresql-restore-test
```

The restore database used temporary storage based on:

```text
emptyDir
```

This allowed a genuine restore operation without creating unnecessary risk for the production database.

---

# 20. Restore from MinIO

The restore process downloaded the exact previously generated object:

```text
real-estate-backups/postgresql/
real_estate-20260909T210700Z.dump
```

The temporary PostgreSQL instance was checked with:

```text
pg_isready
```

before the restore.

PostgreSQL reported that it was accepting connections.

The dump was then restored using:

```text
pg_restore
```

---

# 21. Measured Restore Duration

The observed PostgreSQL restore operation completed in:

```text
6 seconds
```

The restored database size was approximately:

```text
45 MB
```

compared with approximately:

```text
47 MB
```

for production.

This size difference is not considered an integrity failure because logical dump/restore can reconstruct database storage more compactly and remove physical dead space.

The important validation is the logical content of the restored database.

---

# 22. Restore Integrity Verification

The same business counts were queried against the restored database.

Results:

| Table             | Production | Restored | Result |
| ----------------- | ---------: | -------: | ------ |
| `audit_log`       |         10 |       10 | PASS   |
| `bien`            |     14,000 |   14,000 | PASS   |
| `client`          |         18 |       18 | PASS   |
| `demande`         |         87 |       87 | PASS   |
| `demande_version` |         88 |       88 | PASS   |
| `mandat`          |         17 |       17 | PASS   |
| `presentation`    |         12 |       12 | PASS   |
| `visite`          |          1 |        1 | PASS   |

All selected business tables matched the production baseline exactly.

This provides runtime evidence that the backup could be restored into a clean PostgreSQL 16 instance while preserving the tested business data.

---

# 23. Temporary Environment Cleanup

After successful restore validation, the temporary recovery environment was removed.

Deleted resources included:

```text
real-estate-postgresql-restore-test Deployment
real-estate-postgresql-restore-test Service
restore test Job
backup test Job
MinIO access-test Pod
```

The production PostgreSQL workload and PVC were not modified.

The MinIO backup object was retained as recovery evidence.

---

# 24. Proven Recovery Chain

The following chain has now been runtime tested:

```text
Production PostgreSQL
        |
        | pg_dump
        v
Custom PostgreSQL dump
        |
        | pg_restore --list
        v
Structural validation
        |
        | least-privilege MinIO identity
        v
real-estate-backups
        |
        | versioned object
        v
External backup
        |
        | download
        v
Isolated PostgreSQL 16
        |
        | pg_restore
        v
Restored database
        |
        | SQL business checks
        v
Integrity validation
```

This is a materially stronger PRA test than simply restarting or deleting a PostgreSQL Pod.

---

# 25. Backup Automation

After the manual recovery chain was proven, the backup process was converted into a permanent Kubernetes CronJob.

Source manifest:

```text
deploy/kubernetes/pra/
└── postgresql-backup-cronjob.yaml
```

CronJob:

```text
real-estate-postgresql-backup
```

Namespace:

```text
real-estate
```

Configured schedule:

```text
0 2 * * *
```

Concurrency:

```text
Forbid
```

The workload contains two execution phases.

## PostgreSQL dump phase

Image:

```text
postgres:16
```

Responsibilities:

* obtain PostgreSQL credentials from Kubernetes Secret;
* verify PostgreSQL connectivity;
* create a custom-format compressed dump;
* reject an empty dump;
* validate the restore catalogue using `pg_restore --list`;
* calculate SHA-256 checksum;
* record backup metadata.

## MinIO upload phase

Image:

```text
minio/mc
```

Responsibilities:

* obtain dedicated backup credentials from Kubernetes Secret;
* connect to the external MinIO endpoint;
* upload the PostgreSQL dump;
* upload its SHA-256 checksum;
* verify the uploaded objects using `mc stat`;
* expose useful backup information in the Job logs.

---

# 26. Checksum

The automated backup workflow generates:

```text
real_estate-<timestamp>.dump.sha256
```

using:

```text
sha256sum
```

The checksum is stored alongside the backup object in MinIO.

This provides an additional integrity artifact for future recovery procedures.

---

# 27. GitOps Architecture

Unlike the AI/MLOps evaluation workloads, the PostgreSQL backup is a permanent operational workload.

Therefore it must not depend on a GitLab pipeline being active when a scheduled backup is due.

The selected architecture is:

```text
chasse_immobiliere
        |
        | source manifests
        v
deploy/kubernetes/pra
        |
        | GitLab CI
        v
pra:publish-gitops
        |
        v
lab-gitops
        |
        +--> workloads/real-estate/pra
        |
        +--> apps/real-estate-pra
        |
        v
Argo CD root application
        |
        v
real-estate-pra
        |
        v
Kubernetes
        |
        v
real-estate-postgresql-backup CronJob
```

This follows the same permanent deployment principle already used by the Real Estate backend.

---

# 28. PRA Source Files

The source repository now contains:

```text
deploy/kubernetes/pra/
├── application.yaml
├── kustomization.yaml
└── postgresql-backup-cronjob.yaml
```

The Kustomization manages the permanent backup workload.

The Argo CD Application is named:

```text
real-estate-pra
```

and targets:

```text
workloads/real-estate/pra
```

inside:

```text
https://gitlab.local/root/lab-gitops.git
```

branch:

```text
main
```

---

# 29. GitLab CI Integration

A dedicated CI definition was added:

```text
.gitlab/ci/pra.yml
```

The root:

```text
.gitlab-ci.yml
```

was updated to include:

```yaml
- local: .gitlab/ci/pra.yml
```

No new GitLab stage was required because the existing pipeline already contains:

```text
validate
database
build
deploy
```

The PRA publication uses:

```text
deploy
```

---

# 30. `pra:publish-gitops`

The dedicated job is:

```text
pra:publish-gitops
```

It runs on the existing shell runner.

This is important because the developer workstation does not contain Kubernetes administration tooling.

The architecture therefore remains:

```text
Windows workstation
    |
    | edit / commit / push
    v
GitLab
    |
    | shell runner with kubectl
    v
Kubernetes + GitOps validation
```

`kubectl` is not required on the Windows development workstation.

---

# 31. CI Validation Responsibilities

The PRA CI job is designed to validate:

* PRA source directory;
* CronJob manifest;
* Kustomization;
* Argo CD Application;
* Kubernetes namespace;
* PostgreSQL Secret existence;
* MinIO backup Secret existence;
* required Secret keys without printing their values;
* expected PostgreSQL image;
* expected MinIO client image;
* `pg_dump` presence;
* `pg_restore` validation;
* SHA-256 generation;
* MinIO upload commands;
* MinIO remote verification;
* CronJob schedule;
* concurrency policy;
* Kustomize rendering;
* Kubernetes client-side manifest validation.

Secret values are not intentionally printed by these checks.

---

# 32. GitOps Publication

The CI job is designed to publish:

```text
deploy/kubernetes/pra/postgresql-backup-cronjob.yaml
```

to:

```text
lab-gitops/workloads/real-estate/pra/
```

and:

```text
deploy/kubernetes/pra/application.yaml
```

to:

```text
lab-gitops/apps/real-estate-pra/
```

The GitOps repository is cloned using the existing:

```text
lab-gitops-git-credentials
```

mechanism already used by the platform.

Only the PRA paths are staged for the PRA publication commit.

---

# 33. Argo CD Responsibility

After GitLab CI publishes the desired state, Argo CD becomes responsible for maintaining the permanent CronJob.

The intended runtime chain is:

```text
Git commit
    ↓
GitLab CI
    ↓
lab-gitops/main
    ↓
Argo CD root-app
    ↓
real-estate-pra
    ↓
CronJob
```

This provides:

* declarative desired state;
* automatic reconciliation;
* self-healing;
* traceability;
* separation between application source and runtime desired state.

---

# 34. Important Deployment Status

At the time this documentation section was prepared, the PRA source files and CI/GitOps publication mechanism had been created and staged in the application repository.

The permanent CronJob must **not yet be described as runtime verified** until the corresponding GitLab pipeline and Argo CD reconciliation evidence have been collected.

Required final evidence is:

```text
pra:publish-gitops successful
        ↓
GitOps commit created
        ↓
real-estate-pra Synced / Healthy
        ↓
real-estate-postgresql-backup exists
        ↓
manual CronJob-triggered Job succeeds
        ↓
new MinIO backup object exists
```

This distinction is important for certification evidence.

---

# 35. RPO

The intended automated backup frequency is:

```text
daily
```

Once the CronJob is deployed and successfully operating, the planned RPO is therefore:

```text
RPO target <= 24 hours
```

This is currently a **target derived from the backup schedule**.

It becomes an operationally evidenced RPO only after successful scheduled backup execution is demonstrated.

---

# 36. RTO

The measured database restore operation was:

```text
6 seconds
```

This value must **not** be presented as the complete platform RTO.

The complete recovery process also includes:

* provisioning a replacement PostgreSQL environment;
* retrieving the backup;
* restoring it;
* validating integrity;
* reconnecting application services;
* validating API behavior;
* potentially performing DNS/service/cutover operations.

Therefore:

```text
Measured pg_restore component: 6 seconds
Full operational RTO: not yet measured
```

A realistic final RTO target should be defined separately and validated through a complete recovery exercise.

---

# 37. PCA Considerations

The current work primarily improves the **PRA** capability.

The platform already provides some continuity mechanisms at other layers through Kubernetes and GitOps, but PostgreSQL remains a single-replica workload.

Current PostgreSQL architecture does not provide demonstrated database HA.

Therefore:

```text
PCA:
partial

PRA:
backup + isolated restore strongly demonstrated
```

Potential future PCA improvements include:

* PostgreSQL replication;
* PostgreSQL operator;
* multi-node database architecture;
* replicated storage;
* automatic failover;
* secondary recovery site.

These are not required to invalidate the current backup/restore PRA implementation, but they represent stronger continuity options.

---

# 38. Security Model

The backup architecture follows several security principles.

## Separation of duties

Normal project data:

```text
real-estate
```

Backups:

```text
real-estate-backups
```

## Least privilege

Backup identity:

```text
real-estate-backup
```

Policy:

```text
real-estate-backup-policy
```

Access to unrelated bucket:

```text
DENIED
```

## Secret separation

PostgreSQL credentials:

```text
real-estate-postgresql-secret
```

Backup storage credentials:

```text
real-estate-backup-s3
```

## No plaintext credentials in Git

The backup manifests reference Kubernetes Secret names only.

Actual backup credential values are not included in the repository.

---

# 39. Current Limitations

The following items remain outside the completed runtime evidence.

## Automated backup deployment

The permanent CronJob still requires final CI/Argo CD runtime verification if the pipeline has not yet completed.

## Retention policy

The dedicated backup bucket currently has:

```text
ILM: disabled
```

A retention strategy still needs to be implemented.

Proposed policy:

```text
30 daily backups
```

The exact policy must be implemented and evidenced before being claimed.

## Backup monitoring

Backup failure/staleness monitoring is not yet implemented.

Future observability should detect:

* failed CronJob;
* no successful backup within expected period;
* backup duration anomalies;
* backup size anomalies.

## Full application recovery

The isolated PostgreSQL restore was validated at database level.

The backend API has not yet been demonstrated against the restored PostgreSQL instance as part of this PRA exercise.

## Full RTO

Only the PostgreSQL restore component has been measured.

## PostgreSQL HA

No database replication or automatic PostgreSQL failover has been demonstrated.

## Secret manager integration

Vault Agent Injector exists in the cluster, but the Real Estate backup workload is not currently integrated with Vault.

---

# 40. Next Technical Steps

The next PCA/PRA steps are:

1. deploy `pra:publish-gitops`;
2. verify the GitLab CI job;
3. verify the resulting `lab-gitops` commit;
4. verify `real-estate-pra` in Argo CD;
5. verify `real-estate-postgresql-backup` in Kubernetes;
6. manually trigger one Job from the deployed CronJob;
7. verify Job completion and logs;
8. verify the new MinIO dump and checksum objects;
9. implement MinIO retention / ILM;
10. implement backup monitoring and alerting;
11. optionally perform backend API validation against an isolated restored database;
12. define and measure the final operational RTO.

---

# 41. Evidence Status Matrix

| Capability                     | Designed | Implemented         | Tested                   | Runtime Verified | Evidenced |
| ------------------------------ | -------- | ------------------- | ------------------------ | ---------------- | --------- |
| Dedicated backup bucket        | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| Bucket versioning              | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| Least-privilege MinIO policy   | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| Dedicated backup identity      | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| Credential rotation            | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| Kubernetes backup Secret       | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| Cross-bucket access denial     | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| PostgreSQL custom dump         | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| `pg_restore --list` validation | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| MinIO backup upload            | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| Versioned backup object        | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| Isolated PostgreSQL restore    | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| Business row-count validation  | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| Restore duration measurement   | Yes      | Yes                 | Yes                      | Yes              | Yes       |
| SHA-256 in automated workflow  | Yes      | Source implemented  | Pending permanent job    | Pending          | Pending   |
| Permanent backup CronJob       | Yes      | Source implemented  | Pending CI               | Pending          | Pending   |
| GitOps PRA publication         | Yes      | CI implemented      | Pending pipeline         | Pending          | Pending   |
| Argo CD PRA Application        | Yes      | Source implemented  | Pending deployment       | Pending          | Pending   |
| Daily automated backup         | Yes      | Source implemented  | Pending deployment       | Pending          | Pending   |
| RPO ≤ 24h                      | Yes      | Schedule configured | Pending automation proof | No               | No        |
| Retention / ILM                | Proposed | No                  | No                       | No               | No        |
| Backup monitoring              | Proposed | No                  | No                       | No               | No        |
| API recovery validation        | Planned  | No                  | No                       | No               | No        |
| Full operational RTO           | Planned  | No                  | No                       | No               | No        |
| PostgreSQL HA                  | No       | No                  | No                       | No               | No        |

---

# 42. Certification-Relevant Conclusion

Before this work, PostgreSQL depended on a single `local-path` persistent volume and no automated external database backup was evidenced.

The platform now has a **runtime-proven PostgreSQL recovery chain**.

The following has been demonstrated:

```text
PostgreSQL production data
        ↓
pg_dump custom backup
        ↓
structural validation
        ↓
least-privilege external MinIO storage
        ↓
versioned backup object
        ↓
download from external storage
        ↓
clean PostgreSQL 16 instance
        ↓
pg_restore
        ↓
business integrity verification
```

The tested restore reproduced the selected production business-table counts exactly, including 14,000 properties, 87 demands, 88 demand versions and the other captured business entities.

The PostgreSQL restore operation itself completed in approximately **6 seconds** for the tested database.

The recovery mechanism is now being operationalized as a permanent daily Kubernetes CronJob managed through the platform's existing:

```text
GitLab CI
    ↓
lab-gitops
    ↓
Argo CD
    ↓
Kubernetes
```

deployment model.

This provides strong evidence for the PRA portion of BC02 while keeping the remaining gaps explicit: automated retention, backup monitoring, final CronJob runtime evidence, full API recovery validation and complete operational RTO measurement.

---

# 43. Final Status

## Runtime proven

* external MinIO reachable;
* dedicated backup bucket;
* private bucket;
* versioning enabled;
* least-privilege policy;
* dedicated backup identity;
* credential rotation;
* Kubernetes Secret integration;
* allowed backup-bucket access;
* denied unrelated-bucket access;
* PostgreSQL backup;
* structural dump validation;
* external upload;
* versioned backup object;
* isolated PostgreSQL restore;
* exact selected business row-count recovery;
* measured 6-second database restore component;
* safe cleanup of temporary recovery resources.

## Implemented in source / awaiting final deployment evidence

* permanent Kubernetes backup CronJob;
* SHA-256 generation;
* daily schedule;
* concurrency protection;
* Kustomize workload;
* Argo CD Application;
* dedicated `pra:publish-gitops`;
* root GitLab CI inclusion.

## Remaining

* final GitLab/Argo CD/CronJob runtime evidence;
* successful Job manually triggered from permanent CronJob;
* retention / ILM;
* backup failure/staleness monitoring;
* complete application recovery validation;
* final RTO measurement;
* final BC02 PCA/PRA evidence package.

---

**PRA core backup and recovery capability: IMPLEMENTED AND RUNTIME PROVEN**

**PRA operational automation: IMPLEMENTED IN SOURCE — FINAL DEPLOYMENT EVIDENCE PENDING**

**PCA/PRA / BC02 overall: ADVANCED, NOT YET DECLARED COMPLETE**
