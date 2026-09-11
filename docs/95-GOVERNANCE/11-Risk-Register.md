# Enterprise AI Platform — Risk Register

**Version:** 1.0
**Status:** Active
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform / Chasse Immobilière
**Last Updated:** 2026-09-10
**System of Record:** Git

---

# 1. Purpose

This document is the authoritative Risk Register for the Real Estate Intelligence Platform and its supporting Enterprise AI Platform.

It applies the risk-management framework defined in:

```text
docs/95-GOVERNANCE/04-Risk-Management.md
```

The Risk Management document defines **how risks are managed**.

This register records **which risks currently exist**, their severity, their controls, their residual exposure, their treatment, and their evidence.

The register supports:

* BC01 — SI audit, cartography and risk analysis;
* BC02 — project risk management, PCA and PRA;
* architecture governance;
* security governance;
* data governance;
* operational governance;
* AI governance;
* certification evidence.

---

# 2. Evidence Principle

Risk assessment follows:

```text
Evidence
   ↓
Risk Identification
   ↓
Inherent Assessment
   ↓
Existing Controls
   ↓
Residual Assessment
   ↓
Treatment
   ↓
Monitoring / Review
```

A documented or planned control is not considered equivalent to a runtime-verified control.

The project uses the following evidence hierarchy:

```text
Runtime evidence
    >
Repository / source code
    >
CI evidence
    >
GitOps desired state
    >
Documentation
    >
Historical assumption
```

Future or target-state capabilities must not be used to artificially reduce current residual risk.

---

# 3. Scoring Model

## 3.1 Likelihood

| Score | Level          | Meaning               |
| ----: | -------------- | --------------------- |
|     1 | Rare           | Unlikely              |
|     2 | Unlikely       | Could occur           |
|     3 | Possible       | Realistic             |
|     4 | Likely         | Expected periodically |
|     5 | Almost Certain | Expected frequently   |

## 3.2 Impact

| Score | Level      | Meaning                                              |
| ----: | ---------- | ---------------------------------------------------- |
|     1 | Negligible | Minimal effect                                       |
|     2 | Minor      | Limited disruption                                   |
|     3 | Moderate   | Meaningful service/project impact                    |
|     4 | Major      | Significant business/technical impact                |
|     5 | Critical   | Severe business, security, compliance or data impact |

## 3.3 Risk Score

```text
Risk Score = Likelihood × Impact
```

| Score | Classification |
| ----: | -------------- |
|   1–4 | Low            |
|   5–9 | Moderate       |
| 10–16 | High           |
| 17–25 | Critical       |

Both inherent and residual risk are recorded.

---

# 4. Risk Status

Allowed statuses:

```text
Identified
Under Assessment
Open
Treatment In Progress
Accepted
Monitoring
Closed
```

`Closed` does not mean that the historical record is deleted.

---

# 5. Risk Summary

| ID             | Risk                                                | Domain         | Inherent |   Residual | Status                |
| -------------- | --------------------------------------------------- | -------------- | -------: | ---------: | --------------------- |
| RISK-INFRA-001 | Physical host failure                               | Infrastructure |  15 High | 8 Moderate | Monitoring            |
| RISK-INFRA-002 | Storage exhaustion or local storage failure         | Infrastructure |  16 High | 9 Moderate | Monitoring            |
| RISK-K8S-001   | Kubernetes worker/node unavailable                  | Kubernetes     |  12 High | 6 Moderate | Monitoring            |
| RISK-NET-001   | Routing or DNS inconsistency                        | Infrastructure |  12 High | 6 Moderate | Monitoring            |
| RISK-DATA-001  | PostgreSQL data loss or corruption                  | Data           |  15 High | 8 Moderate | Monitoring            |
| RISK-OPS-001   | Backup failure or stale backup remains undetected   | Operations     |  15 High |    12 High | Treatment In Progress |
| RISK-OPS-002   | Recovery exceeds acceptable duration                | Operations     |  12 High | 8 Moderate | Monitoring            |
| RISK-OPS-003   | Loss of observability                               | Operations     |  12 High | 6 Moderate | Monitoring            |
| RISK-DATA-002  | Data-quality controls provide false confidence      | Data           |  12 High | 8 Moderate | Treatment In Progress |
| RISK-DATA-003  | Historical ingestion/version lineage ambiguity      | Data           |  12 High | 9 Moderate | Open                  |
| RISK-SEC-001   | Credential or secret exposure                       | Security       |  15 High |    10 High | Treatment In Progress |
| RISK-SEC-002   | Fine-grained authorization incomplete               | Security       |  16 High |    12 High | Treatment In Progress |
| RISK-SEC-003   | Incomplete security/business audit coverage         | Security       |  12 High | 8 Moderate | Treatment In Progress |
| RISK-BUS-001   | Mandate lifecycle rules not fully enforced          | Business       |  12 High | 9 Moderate | Open                  |
| RISK-BUS-002   | Hunter remuneration requirements incomplete         | Business       |  16 High |    12 High | Open                  |
| RISK-ARCH-001  | Documentation / architecture drift                  | Architecture   |  12 High | 8 Moderate | Treatment In Progress |
| RISK-AI-001    | Local GPU capacity or AI host unavailable           | AI             |  12 High | 6 Moderate | Monitoring            |
| RISK-AI-002    | ML capability mistaken for production capability    | AI             |  12 High | 6 Moderate | Monitoring            |
| RISK-PROJ-001  | Excessive scope and technology expansion            | Project        |  16 High | 6 Moderate | Monitoring            |
| RISK-PROJ-002  | Certification evidence insufficient or inconsistent | Project        |  16 High | 8 Moderate | Treatment In Progress |

---

# 6. Detailed Risk Register

## RISK-INFRA-001 — Physical Host Failure

**Domain:** Infrastructure
**Owner:** Platform
**Status:** Monitoring
**Treatment:** Reduce

### Risk statement

Because the platform operates on a finite on-premise Proxmox infrastructure, failure of a physical host may remove several virtual machines or Kubernetes nodes simultaneously and may affect platform availability.

### Inherent risk

```text
Likelihood: 3
Impact:     5
Score:      15 — High
```

### Existing controls

* multiple Kubernetes control-plane nodes;
* multiple Kubernetes workers;
* Kubernetes workload rescheduling;
* Git-based infrastructure/application reconstruction information;
* GitOps desired state;
* PostgreSQL backup and restore procedure;
* external MinIO backup target;
* monitoring and node-health visibility;
* documented recovery procedures.

### Residual risk

The physical infrastructure remains finite and does not provide unlimited hardware redundancy. Stateful workloads using local storage can remain tied to a failed host.

```text
Likelihood: 2
Impact:     4
Score:      8 — Moderate
```

### Evidence

* Kubernetes cluster architecture;
* infrastructure architecture;
* PCA/PRA documentation;
* PostgreSQL backup/restore evidence;
* Argo CD desired-state reconstruction capability.

### Review

**Review Date:** 2026-10-10

---

## RISK-INFRA-002 — Storage Exhaustion or Local Storage Failure

**Domain:** Infrastructure
**Owner:** Platform / Operations
**Status:** Monitoring
**Treatment:** Reduce

### Risk statement

Because several platform workloads rely on finite local storage and the `local-path` StorageClass, storage exhaustion or node-local storage failure may cause service degradation or loss of persistent workload availability.

### Inherent risk

```text
Likelihood: 4
Impact:     4
Score:      16 — High
```

### Existing controls

* infrastructure monitoring;
* Prometheus metrics;
* Grafana visibility;
* persistent-volume monitoring capabilities;
* backup of critical PostgreSQL data;
* external MinIO backup destination;
* operational documentation.

### Residual risk

`local-path` does not itself provide distributed storage redundancy.

```text
Likelihood: 3
Impact:     3
Score:      9 — Moderate
```

### Treatment

Continue capacity monitoring and preserve external backups.

Distributed storage may be evaluated later if justified by availability requirements.

### Review

**Review Date:** 2026-10-10

---

## RISK-K8S-001 — Kubernetes Worker or Node Unavailable

**Domain:** Kubernetes
**Owner:** Platform
**Status:** Monitoring
**Treatment:** Reduce

### Risk statement

Failure or loss of connectivity of a Kubernetes worker can interrupt workloads scheduled on that node.

### Inherent risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Existing controls

* multiple worker nodes;
* multiple control-plane nodes;
* Kubernetes scheduling/rescheduling;
* readiness/liveness mechanisms where implemented;
* Prometheus node/workload monitoring;
* GitOps reconciliation.

### Residual risk

Stateless workloads have stronger recovery characteristics than workloads attached to node-local persistent storage.

```text
Likelihood: 2
Impact:     3
Score:      6 — Moderate
```

### Review

**Review Date:** 2026-10-10

---

## RISK-NET-001 — Routing or DNS Inconsistency

**Domain:** Infrastructure / Network
**Owner:** Platform
**Status:** Monitoring
**Treatment:** Reduce

### Risk statement

Because the homelab uses multiple network ranges, static routes and local DNS/host resolution, inconsistent routing or host configuration can isolate Kubernetes nodes or infrastructure services.

### Inherent risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Evidence of exposure

A real infrastructure incident demonstrated inconsistent `/etc/hosts` management and missing routes to `10.20.2.0/24` on some systems.

### Existing controls

* documented host mappings;
* documented static routing requirements;
* node-health monitoring;
* Kubernetes connectivity checks;
* infrastructure troubleshooting procedures.

### Residual risk

Configuration remains partly dependent on host/network configuration outside Kubernetes reconciliation.

```text
Likelihood: 2
Impact:     3
Score:      6 — Moderate
```

### Review

**Review Date:** 2026-10-10

---

## RISK-DATA-001 — PostgreSQL Data Loss or Corruption

**Domain:** Data
**Owner:** Data / Platform
**Status:** Monitoring
**Treatment:** Reduce

### Risk statement

Because PostgreSQL is a critical system of record and does not currently operate as a database-level HA cluster, database corruption, accidental deletion, storage failure or destructive migration could result in loss of operational data.

### Inherent risk

```text
Likelihood: 3
Impact:     5
Score:      15 — High
```

### Existing controls

* migration control;
* database validation;
* scheduled PostgreSQL logical backup;
* external MinIO backup storage;
* isolated restore procedure;
* integrity validation after restore;
* permanent Kubernetes CronJob deployed through GitOps;
* backup/recovery documentation.

### Runtime evidence

A PostgreSQL backup and isolated restore exercise has been executed successfully and the permanent backup CronJob has been deployed through CI/GitOps/Argo CD.

### Residual risk

PostgreSQL database-level HA is not currently implemented.

```text
Likelihood: 2
Impact:     4
Score:      8 — Moderate
```

### Review

**Review Date:** 2026-10-10

---

## RISK-OPS-001 — Backup Failure or Stale Backup Remains Undetected

**Domain:** Operations
**Owner:** Platform / Operations
**Status:** Treatment In Progress
**Treatment:** Reduce

### Risk statement

Although scheduled PostgreSQL backup exists, failure or prolonged staleness of backups may remain undetected if backup-specific freshness and failure alerting is incomplete.

### Inherent risk

```text
Likelihood: 3
Impact:     5
Score:      15 — High
```

### Existing controls

* scheduled daily PostgreSQL backup;
* external MinIO destination;
* manual backup execution evidence;
* successful restore evidence;
* Kubernetes job visibility;
* general observability platform.

### Remaining gaps

* dedicated backup failure alerting;
* backup-age/staleness alerting;
* formal retention/ILM policy;
* automated periodic restore validation.

### Residual risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Planned treatment

* expose backup success timestamp;
* alert on failed backup;
* alert on stale backup;
* define retention lifecycle;
* periodically repeat restore exercises.

### Review

**Review Date:** 2026-10-10

---

## RISK-OPS-002 — Recovery Exceeds Acceptable Duration

**Domain:** Operations
**Owner:** Platform / Data
**Status:** Monitoring
**Treatment:** Reduce

### Risk statement

A successful database restore proves recoverability but does not automatically prove that the complete business service can be recovered within a formally validated RTO.

### Inherent risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Existing controls

* PRA documentation;
* recovery sequence;
* PostgreSQL isolated restore procedure;
* successful restore validation;
* GitOps reconstruction capability;
* application deployment automation.

### Remaining gap

Full application/platform recovery duration has not been established as a measured production SLA.

### Residual risk

```text
Likelihood: 2
Impact:     4
Score:      8 — Moderate
```

### Review

**Review Date:** 2026-10-10

---

## RISK-OPS-003 — Loss of Observability

**Domain:** Operations
**Owner:** Platform
**Status:** Monitoring
**Treatment:** Reduce

### Risk statement

Failure of monitoring, logging or tracing services can delay incident detection and increase recovery time.

### Inherent risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Existing controls

* Prometheus;
* Alertmanager;
* Grafana;
* Loki;
* Tempo;
* OpenTelemetry Collector;
* application metrics;
* recommendation business metrics;
* Kubernetes health visibility.

### Residual risk

The observability platform itself remains a platform dependency.

```text
Likelihood: 2
Impact:     3
Score:      6 — Moderate
```

### Review

**Review Date:** 2026-10-10

---

## RISK-DATA-002 — Data-Quality Controls Provide False Confidence

**Domain:** Data
**Owner:** Data
**Status:** Treatment In Progress
**Treatment:** Reduce

### Risk statement

Because some DQ reporting logic relies on declared or hard-coded expected check counts, a successful summary may overstate actual data-quality coverage if the underlying checks evolve without corresponding metadata updates.

### Inherent risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Existing controls

* dbt tests;
* staging validation;
* referential-integrity checks;
* OpenMetadata quality capabilities;
* DQ runner;
* automated tests;
* pipeline validation.

### Remaining gap

Expected DQ coverage should progressively be derived from executed checks rather than manually maintained totals.

### Residual risk

```text
Likelihood: 2
Impact:     4
Score:      8 — Moderate
```

### Review

**Review Date:** 2026-10-10

---

## RISK-DATA-003 — Historical Ingestion / Version Lineage Ambiguity

**Domain:** Data
**Owner:** Data
**Status:** Open
**Treatment:** Reduce

### Risk statement

If repeated ingestion overwrites or ambiguously associates historical search/version information, analytical lineage and reproducibility may become inaccurate.

### Inherent risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Existing controls

* `source_recherche_ref`;
* ingestion batch metadata;
* `demande_version`;
* raw and staging layers;
* migration control;
* OpenMetadata lineage;
* training-dataset metadata.

### Residual risk

The code review identified historical-version overwrite ambiguity that still requires explicit resolution or documented acceptance.

```text
Likelihood: 3
Impact:     3
Score:      9 — Moderate
```

### Review

**Review Date:** 2026-10-10

---

## RISK-SEC-001 — Credential or Secret Exposure

**Domain:** Security
**Owner:** Security / Platform
**Status:** Treatment In Progress
**Treatment:** Reduce

### Risk statement

Credentials may be exposed through CI variables, connection strings, logs, repository configuration or improperly managed Kubernetes Secrets.

### Inherent risk

```text
Likelihood: 3
Impact:     5
Score:      15 — High
```

### Existing controls

* Kubernetes Secrets;
* GitLab CI variables;
* application configuration through environment variables;
* least-privilege principles;
* GitOps separation;
* application authentication;
* RBAC.

### Known limitations

* Vault workload integration is not currently proven;
* some pipeline connection-string handling requires continued review;
* TLS verification bypass has existed in CI-related workflows and should not become a production security assumption.

### Residual risk

```text
Likelihood: 2
Impact:     5
Score:      10 — High
```

### Review

**Review Date:** 2026-10-10

---

## RISK-SEC-002 — Fine-Grained Authorization Incomplete

**Domain:** Security
**Owner:** Application / Security
**Status:** Treatment In Progress
**Treatment:** Reduce

### Risk statement

Role-level RBAC is implemented, but incomplete object/resource ownership enforcement may allow an authenticated role to access resources beyond the intended business ownership boundary.

### Inherent risk

```text
Likelihood: 4
Impact:     4
Score:      16 — High
```

### Existing controls

Authentication source:

```text
real_estate.utilisateur
```

Roles:

```text
ADMIN
CLIENT
CHASSEUR
SERVICE
```

Authentication and authorization capabilities include:

* Argon2id password hashing;
* JWT authentication;
* protected API routes;
* role-level RBAC;
* endpoint-specific role restrictions.

### Remaining gap

Fine-grained ownership authorization is not complete across all resources.

Examples include enforcing relationships such as:

```text
CLIENT → only own resources

CHASSEUR → only assigned business resources
```

where required by the business model.

### Residual risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Review

**Review Date:** 2026-10-10

---

## RISK-SEC-003 — Incomplete Audit Coverage

**Domain:** Security / Compliance
**Owner:** Application / Security
**Status:** Treatment In Progress
**Treatment:** Reduce

### Risk statement

Incomplete audit coverage can prevent reconstruction of sensitive business or security actions.

### Inherent risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Existing controls

Application audit is implemented for:

* Presentation operations;
* Presentation creation through recommendation;
* Visite operations;
* Mandat operations.

Audit records are persisted in:

```text
real_estate.audit_log
```

and are written in the application transaction.

### Remaining gaps

Audit coverage remains incomplete for:

* Demande changes;
* Client changes;
* authentication/security events.

### Residual risk

```text
Likelihood: 2
Impact:     4
Score:      8 — Moderate
```

### Review

**Review Date:** 2026-10-10

---

## RISK-BUS-001 — Mandate Lifecycle Rules Not Fully Enforced

**Domain:** Business / Application
**Owner:** Business / Application
**Status:** Open
**Treatment:** Reduce

### Risk statement

If mandate validity, expiration and renewal rules are not fully enforced by the application, business operations may continue against a mandate that no longer satisfies the required business conditions.

### Inherent risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Existing controls

* mandate data model;
* mandate API;
* mandate audit trail;
* database constraints;
* explicit pre-mandate demand lifecycle.

### Remaining gap

The required six-month validity/renewal semantics are not fully enforced.

### Residual risk

```text
Likelihood: 3
Impact:     3
Score:      9 — Moderate
```

### Review

**Review Date:** 2026-10-10

---

## RISK-BUS-002 — Hunter Remuneration Requirements Incomplete

**Domain:** Business / Application
**Owner:** Business / Application
**Status:** Open
**Treatment:** Reduce

### Risk statement

The updated business requirements introduce hunter remuneration rules that are not yet completely represented by the current application and data model.

This may lead to incorrect or non-reproducible remuneration calculations.

### Inherent risk

```text
Likelihood: 4
Impact:     4
Score:      16 — High
```

### Existing foundations

* `chasseur`;
* `mandat`;
* `paiement`;
* `bareme_commission`;
* transactional data;
* audit capability.

### Remaining gaps

The current review identified missing or incomplete capabilities around:

* remuneration calculation service;
* company fee parameter;
* commission-grid validity/overlap rules;
* transaction origin;
* beneficiary identification;
* refusal/denial reason;
* single-beneficiary constraint;
* mandate validity dependency;
* performance-score inputs;
* immutable historical calculation details;
* payment/invoice workflow;
* remuneration-specific access control;
* acceptance tests.

### Residual risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Treatment

Address only to the extent required by the validated Fil Rouge requirements and certification scope.

### Review

**Review Date:** 2026-10-10

---

## RISK-ARCH-001 — Documentation and Architecture Drift

**Domain:** Architecture / Governance
**Owner:** Architecture / Governance
**Status:** Treatment In Progress
**Treatment:** Reduce

### Risk statement

Because the architecture documentation includes both current and target-state technologies, readers or assessors may incorrectly interpret future capabilities as currently implemented.

### Inherent risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Examples

Target/future elements appearing in architecture material include:

* RAG;
* AI Gateway;
* frontend capabilities;
* Keycloak;
* Qdrant/vector search;
* Vault integration;
* Kafka;
* future lakehouse capabilities.

These must not be confused with the runtime-verified Real Estate platform.

### Existing controls

* architecture documentation;
* ADRs;
* Git history;
* evidence hierarchy;
* certification evidence consolidation;
* explicit current/future review.

### Residual risk

```text
Likelihood: 2
Impact:     4
Score:      8 — Moderate
```

### Treatment

Create a certification-specific current-state SI cartography and explicitly mark target/future architecture separately.

### Review

**Review Date:** 2026-10-10

---

## RISK-AI-001 — Local GPU Capacity or AI Host Unavailable

**Domain:** AI / Infrastructure
**Owner:** AI / Platform
**Status:** Monitoring
**Treatment:** Reduce / Accept

### Risk statement

The local AI environment depends on a dedicated GTX 1080 GPU host with finite VRAM. Hardware failure or capacity exhaustion can make local inference unavailable.

### Inherent risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Existing controls

* local-first inference;
* quantized model;
* Ollama;
* GPU capacity awareness;
* AI treated as an enhancement rather than a mandatory dependency for core business operations;
* deterministic matching remains independent from the local LLM.

### Residual risk

Because core Real Estate functionality can operate without Ollama inference, the business impact is reduced.

```text
Likelihood: 3
Impact:     2
Score:      6 — Moderate
```

### Review

**Review Date:** 2026-10-10

---

## RISK-AI-002 — Experimental ML Capability Mistaken for Production Capability

**Domain:** AI / MLOps
**Owner:** AI / Governance
**Status:** Monitoring
**Treatment:** Reduce

### Risk statement

Because MLflow experiments, training/evaluation code and a dedicated GPU environment exist, project documentation or presentation may incorrectly imply that a trained ML model currently drives production recommendations.

### Inherent risk

```text
Likelihood: 3
Impact:     4
Score:      12 — High
```

### Current verified state

Production recommendation logic currently relies on deterministic business eligibility and deterministic weighted ranking.

The project also contains:

* training dataset generation;
* ML evaluation code;
* Logistic Regression experimental baseline;
* MLflow experiment tracking;
* GTX 1080 AI node;
* Ollama/Qwen local inference environment.

However:

* no GPU-trained Real Estate ranking model is currently in production;
* no production ML model promotion is established;
* no OpenMetadata ML model registration is currently established;
* RAG is not a production Real Estate capability.

### Residual risk

Explicit current/target-state labeling substantially reduces the risk.

```text
Likelihood: 2
Impact:     3
Score:      6 — Moderate
```

### Review

**Review Date:** 2026-10-10

---

## RISK-PROJ-001 — Excessive Scope and Technology Expansion

**Domain:** Project / Architecture
**Owner:** Project / Architecture
**Status:** Monitoring
**Treatment:** Reduce

### Risk statement

Because the platform can support many technologies and architectural extensions, adding non-essential components before certification requirements are proven may increase complexity and delay completion.

### Inherent risk

```text
Likelihood: 4
Impact:     4
Score:      16 — High
```

### Potential scope-expansion examples

* Kubeflow;
* Spark;
* Iceberg;
* Trino;
* JupyterHub;
* Kafka;
* Qdrant;
* RAG;
* MCP;
* additional frontend scope;
* Databricks-style lakehouse capabilities.

### Existing controls

* certification-first prioritization;
* evidence matrix;
* MoSCoW prioritization;
* deferred architecture roadmap;
* explicit separation between current and future state.

### Residual risk

```text
Likelihood: 2
Impact:     3
Score:      6 — Moderate
```

### Review

**Review Date:** 2026-10-10

---

## RISK-PROJ-002 — Certification Evidence Insufficient or Inconsistent

**Domain:** Project / Governance
**Owner:** Project / Governance
**Status:** Treatment In Progress
**Treatment:** Reduce

### Risk statement

A technically implemented capability may fail to demonstrate a certification competency if repository, automated test, CI, runtime, documentation and presentation evidence are incomplete or inconsistent.

### Inherent risk

```text
Likelihood: 4
Impact:     4
Score:      16 — High
```

### Existing controls

Certification review uses the matrix:

```text
Requirement / Competency
Implemented Capability
Repository Artifact
Automated Test
CI Evidence
Runtime Evidence
Documentation
Screenshot Needed
Status
Gap
```

Official priority is:

```text
BC01
BC02
BC03
BC05
```

### Current treatment

The project is now following:

```text
PROVE
  ↓
MAP
  ↓
IDENTIFY REAL GAPS
  ↓
CLOSE ONLY REAL GAPS
  ↓
CONSOLIDATE EVIDENCE
  ↓
SOUTENANCE
```

### Residual risk

```text
Likelihood: 2
Impact:     4
Score:      8 — Moderate
```

### Review

**Review Date:** 2026-10-10

---

# 7. Risk-to-Control Matrix

| Risk           | Main Current Controls                         | Remaining Gap                            |
| -------------- | --------------------------------------------- | ---------------------------------------- |
| RISK-INFRA-001 | K8s multi-node, backup, GitOps, monitoring    | Physical/local-storage dependency        |
| RISK-INFRA-002 | Monitoring, backup                            | Distributed storage not implemented      |
| RISK-K8S-001   | Multiple workers/control planes, rescheduling | Stateful local-storage exposure          |
| RISK-NET-001   | Documented routes/hosts, monitoring           | Host/network config remains external     |
| RISK-DATA-001  | Backup, MinIO, restore test, migrations       | PostgreSQL HA absent                     |
| RISK-OPS-001   | Scheduled backup, MinIO, restore proof        | Failure/staleness alerting + ILM         |
| RISK-OPS-002   | PRA, restore test, GitOps                     | Full measured service RTO                |
| RISK-OPS-003   | Prometheus/Grafana/Loki/Tempo/OTel            | Monitoring platform dependency           |
| RISK-DATA-002  | dbt/DQ/OpenMetadata                           | Declarative/hard-coded coverage counts   |
| RISK-DATA-003  | version refs, raw/staging, lineage            | Historical overwrite semantics           |
| RISK-SEC-001   | Secrets, CI variables, RBAC                   | Vault/integration and credential hygiene |
| RISK-SEC-002   | JWT + role RBAC                               | Object ownership                         |
| RISK-SEC-003   | `audit_log`                                   | Demande/Client/auth-event coverage       |
| RISK-BUS-001   | mandate model/API/audit                       | validity/renewal enforcement             |
| RISK-BUS-002   | commission/payment foundations                | remuneration workflow                    |
| RISK-ARCH-001  | docs/ADRs/evidence review                     | current-state certification map          |
| RISK-AI-001    | graceful degradation                          | single GPU host                          |
| RISK-AI-002    | MLflow/evaluation + explicit boundaries       | production model not yet established     |
| RISK-PROJ-001  | certification-first roadmap                   | continued scope discipline               |
| RISK-PROJ-002  | evidence matrix                               | complete BC01/02/03/05 consolidation     |

---

# 8. Risk Review Priorities

Current highest residual risks are:

```text
RISK-OPS-001   Backup monitoring / retention
RISK-SEC-001   Credential exposure
RISK-SEC-002   Fine-grained authorization
RISK-BUS-002   Hunter remuneration requirements
```

These risks have a residual score of `10` or greater.

They should receive priority review.

This does **not** automatically mean they must all be implemented before certification.

Treatment priority must consider:

* certification requirements;
* business criticality;
* available evidence;
* security/compliance impact;
* implementation cost;
* project scope.

---

# 9. Accepted Architectural Constraints

The following are currently treated as explicit architectural constraints rather than hidden assumptions:

### Finite physical infrastructure

The platform operates on homelab/on-premise hardware.

### Local-path storage

The Kubernetes environment currently uses `local-path` storage.

### PostgreSQL without database-level HA

Recoverability is currently addressed primarily through backup/restore rather than PostgreSQL replication/failover.

### Single local GPU environment

The GTX 1080 AI node provides experimental/local AI capability but is not required for core deterministic Real Estate business operation.

### Vault not yet integrated into workloads

Kubernetes Secrets and CI variables remain the current implemented secret mechanisms.

### Production RAG not implemented

RAG remains a future architecture capability.

### MCP not implemented as a production business capability

Any future MCP integration requires explicit security and authorization governance.

### Lakehouse not currently implemented

MinIO exists, but MinIO alone is not classified as a lakehouse.

---

# 10. Closed / Reduced Risk Evidence

Risk records should not disappear when controls are successfully implemented.

An important example is database recoverability.

Earlier project documentation identified:

```text
Restore non testé
```

as a significant risk.

The project subsequently implemented and verified:

```text
PostgreSQL
   ↓
Logical Backup
   ↓
External MinIO
   ↓
Isolated PostgreSQL Restore
   ↓
Integrity Validation
```

The permanent backup CronJob was also deployed through:

```text
GitLab CI
   ↓
GitOps publication
   ↓
Argo CD
   ↓
Kubernetes
```

Therefore the risk is no longer accurately represented as simply:

```text
"Restore not tested"
```

The remaining risks are now more precise:

```text
Backup failure/staleness detection
Retention lifecycle
Full recovery-duration measurement
PostgreSQL HA
```

This demonstrates continuous risk reassessment.

---

# 11. Review Cadence

### Continuous

Monitor technical indicators where available.

Examples:

* storage utilization;
* Kubernetes node health;
* API health;
* recommendation failures;
* backup status;
* DQ failures.

### Monthly

Review High and Critical residual risks.

### Quarterly

Review the complete Risk Register.

### Event-driven

Review affected risks after:

* architecture changes;
* major deployment;
* infrastructure incident;
* security incident;
* data-quality incident;
* failed backup;
* failed restore;
* new business requirement;
* certification requirement change.

---

# 12. Certification Mapping

## BC01

This register provides evidence for:

```text
SI cartography
        +
Risk analysis
        ↓
SI Audit Dossier
```

Together with the current-state SI cartography, it forms the principal evidence for **BC01 — C1**.

## BC02

This register also feeds:

```text
Project Risks
     ↓
Mitigation
     ↓
PCA / PRA
     ↓
Recovery Evidence
```

and therefore supports **BC02 — C7**.

---

# 13. Evidence References

Primary supporting documentation includes:

```text
docs/95-GOVERNANCE/04-Risk-Management.md
docs/95-GOVERNANCE/11-Risk-Register.md

docs/30-INFRASTRUCTURE/
docs/40-DATA/
docs/50-AI/
docs/60-SECURITY/
docs/70-DEVOPS/
docs/80-OPERATIONS/
docs/90-OBSERVABILITY/

docs/evidence/01-BC01/
docs/evidence/02-BC02/

PCA-PRA-MIGRATION.md
```

Runtime, CI and GitOps evidence should be referenced from the corresponding certification evidence dossiers rather than fabricated inside this register.

---

# 14. Current Maturity

```text
Risk Awareness                STRONG
Risk Methodology              DOCUMENTED
Risk Taxonomy                 DOCUMENTED
Formal Risk Register          IMPLEMENTED
Stable Risk IDs               IMPLEMENTED
Inherent Risk Scoring         IMPLEMENTED
Control Mapping               IMPLEMENTED
Residual Risk Scoring         IMPLEMENTED
Risk Ownership                IMPLEMENTED
Risk Review Dates             IMPLEMENTED
Runtime Evidence Linking      DEVELOPING
Risk as Code                  TARGET
Automated Risk CI Validation  TARGET
Continuous KRI Correlation    TARGET
```

---

# 15. Conclusion

The Real Estate Intelligence Platform now maintains an explicit risk-management chain:

```text
Architecture / Runtime / Requirements
              ↓
        Risk Identification
              ↓
        Inherent Assessment
              ↓
        Existing Controls
              ↓
        Evidence Validation
              ↓
        Residual Assessment
              ↓
        Treatment / Acceptance
              ↓
        Monitoring and Review
```

The objective is not to claim that the platform has no risk.

The objective is to demonstrate that:

```text
Risks are known
        +
Risks are scored
        +
Risks have owners
        +
Controls are explicit
        +
Residual exposure is visible
        +
Evidence is preferred over assumption
        +
Treatment is prioritized
```

This Risk Register is the authoritative project record for that purpose.
