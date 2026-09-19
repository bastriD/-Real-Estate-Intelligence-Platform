# Requirements & Evidence Matrix

**Version:** 1.0
**Status:** Active — Living Governance Document
**Owner:** Bastri Murad
**Project:** Enterprise AI Platform
**Business Application:** Real Estate Intelligence Platform
**Certification:** RNCP40573
**Last Updated:** 2026-09-15

---

# 1. Purpose

This document is the central requirements-to-evidence traceability matrix for the Real Estate Intelligence Platform.

It connects:

```text
Requirement
    |
    v
Business / Technical Design
    |
    v
Implementation
    |
    v
Tests
    |
    v
Deployment / Runtime
    |
    v
Evidence
    |
    v
Remaining Gap
```

Its objectives are to:

* demonstrate coverage of the Diginamic StarterPack;
* connect requirements to concrete project artifacts;
* distinguish documentation from implementation;
* distinguish implementation from runtime verification;
* identify remaining functional and evidence gaps;
* provide a central navigation document for project review and jury preparation;
* preserve BC04 and BC06 as extended project competencies without incorrectly presenting them as mandatory StarterPack blocks.

This matrix is a living governance artifact.

It must be updated when implementation, testing, deployment or evidence status materially changes.

---

# 2. Scope Model

The project deliberately has two complementary scopes.

## 2.1 Official StarterPack certification baseline

The reviewed Diginamic StarterPack defines the Fil Rouge primarily around:

```text
BC01
BC02
BC03
BC05
```

BC05 is the principal Data / AI block of the project.

These four blocks constitute the primary StarterPack traceability baseline used by this matrix.

## 2.2 Extended project scope

The Real Estate Intelligence Platform additionally covers:

```text
BC04 — Cybersecurity
BC06 — DevOps
```

BC04 and BC06 are therefore retained as first-class project workstreams and portfolio evidence.

They must not, however, be presented as mandatory blocks of the reviewed StarterPack assignment.

The complete project scope is consequently:

```text
BC01 ─ SI Strategy
BC02 ─ Project Management
BC03 ─ Application Engineering
BC04 ─ Cybersecurity          [Extended project scope]
BC05 ─ Data & AI
BC06 ─ DevOps                [Extended project scope]
```

---

# 3. Status Vocabulary

The matrix uses controlled evidence states.

| Status                | Meaning                                                           |
| --------------------- | ----------------------------------------------------------------- |
| DESIGNED              | Architecture or requirement has been formally designed            |
| IMPLEMENTED           | Source code, schema or configuration exists                       |
| TESTED                | Automated or controlled tests have been executed                  |
| CI VALIDATED          | Relevant CI execution has been explicitly observed successful     |
| DEPLOYED              | Component has been deployed through the target delivery mechanism |
| RUNTIME VERIFIED      | Behaviour has been directly observed in the running platform      |
| PARTIAL               | Requirement is only partially satisfied                           |
| MISSING               | Required capability or artifact does not currently exist          |
| REQUIRES VERIFICATION | Implementation may exist but evidence is insufficient             |
| NOT APPLICABLE        | Requirement does not apply to the selected scope                  |

A directory, source file or design document alone does not constitute runtime evidence.

Historical evidence remains historical and must not automatically be interpreted as current runtime health.

---

# 4. Evidence Principles

Evidence must answer:

```text
WHAT?
WHERE?
WHEN?
WHICH VERSION?
EXPECTED RESULT?
OBSERVED RESULT?
PASS / FAIL?
```

Evidence hierarchy:

```text
Runtime evidence
      >
Executed tests
      >
CI evidence
      >
Deployed configuration
      >
Source implementation
      >
Design documentation
      >
Assumption
```

No evidence may be fabricated to complete this matrix.

---

# 5. BC01 — SI Strategy

**Scope:** Official StarterPack

Primary evidence root:

```text
docs/evidence/01-BC01/
```

## BC01 Traceability

| Requirement                         | Project response                                                     | Evidence                                                          | Status                         | Remaining action                                               |
| ----------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------ | -------------------------------------------------------------- |
| Audit the existing SI               | Existing/current-state architecture and SI analysis documented       | `01-BC01/C1-Audit-SI/README.md` + current-state diagrams          | IMPLEMENTED                    | Consolidate authoritative diagram/version and legacy anomalies |
| Produce SI cartography              | Multiple PlantUML/rendered architecture views exist                  | `C1-Audit-SI/`                                                    | IMPLEMENTED                    | Remove/identify obsolete duplicates                            |
| Define target SI strategy           | Enterprise AI/Data platform strategy documented                      | `C2-Strategie-SI/README.md`                                       | IMPLEMENTED                    | Final jury-oriented synthesis                                  |
| Compare OLTP and OLAP architecture  | Separation documented and implemented                                | `C3-Architecture-OLTP-OLAP/.../README.md`, Data architecture docs | IMPLEMENTED / RUNTIME VERIFIED | Synchronize evidence index with current warehouse              |
| Analyze components and interactions | Kubernetes, API, Data, MLOps and observability components documented | `C4-Composants-Interactions-Performance/README.md`                | IMPLEMENTED                    | Add latest financial/business flow where absent                |
| Analyze performance/scalability     | Architecture addresses scaling and performance                       | C4 + infrastructure/data docs                                     | PARTIAL                        | Add measured workload evidence where required                  |
| Architecture decision matrix        | Alternatives must be compared with explicit criteria                 | `C5-Decision-Architecture/`                                       | MISSING                        | Produce weighted decision matrix                               |
| Eco-responsible architecture        | Principles documented                                                | `C6-Eco-Conception/` and supporting architecture                  | PARTIAL                        | Add concise quantified trade-off evidence                      |
| Technology watch                    | Supporting technology-watch material exists                          | `supporting/Veille-Technologique/README.md`                       | IMPLEMENTED                    | Consolidate findings into decisions                            |
| Architecture target                 | Target architecture documented                                       | `supporting/Architecture-Cible/README.md`                         | IMPLEMENTED                    | Keep synchronized with runtime                                 |

### BC01 Current Assessment

BC01 has substantial architecture and strategy evidence.

The main remaining requirements are evidence consolidation, the explicit architecture decision matrix, measured performance where required, and stronger quantified eco-design justification.

---

# 6. BC02 — Project Management

**Scope:** Official StarterPack

Primary evidence root:

```text
docs/evidence/02-BC02/
```

## BC02 Traceability

| Requirement             | Project response                                          | Evidence                                                         | Status                               | Remaining action                                                                        |
| ----------------------- | --------------------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------ | --------------------------------------------------------------------------------------- |
| Opportunity study       | Project opportunity documented                            | `C1-Etude-Opportunite/README.md`                                 | IMPLEMENTED                          | Final consistency review                                                                |
| Prioritized backlog     | Backlog structure exists                                  | `C2-Backlog-Priorise/README.md`                                  | IMPLEMENTED                          | Synchronize with remaining StarterPack gaps                                             |
| Technical specification | Technical requirements documented across project          | `C3-Cahier-Charges-RGPD-PSH/README.md` + technical specification | IMPLEMENTED                          | Ensure final standalone CDCT is linked                                                  |
| RGPD requirements       | Privacy requirements represented                          | C3 + BC05/C7                                                     | PARTIAL                              | Complete final treatment register/evidence                                              |
| Accessibility / PSH     | Accessibility principles represented                      | C3 + BC03 mockup work                                            | PARTIAL                              | Produce final annotated accessibility evidence                                          |
| Business processes      | Business processes documented                             | `C4-Processus-Metier/README.md`                                  | PARTIAL                              | Synchronize with current transaction/payment lifecycle and remaining Offer/Invoice gaps |
| Note de cadrage         | Framing material exists                                   | `C5-Note-Cadrage/README.md` + Note de cadrage                    | IMPLEMENTED                          | Ensure final standalone artifact is linked                                              |
| Planning and milestones | Planning structure exists                                 | `C6-Planning-Jalons/README.md`                                   | PARTIAL                              | Add baseline vs actual milestones where defensible                                      |
| Risk management         | Risk register exists                                      | `C7-Risques-PCA-PRA/README.md`, governance risk register         | IMPLEMENTED                          | Keep current                                                                            |
| PCA/PRA                 | PostgreSQL backup/restore strategy implemented and tested | PCA/PRA documentation                                            | TESTED / DEPLOYED / RUNTIME VERIFIED | Final application-level recovery measurement and RPO/RTO evidence                       |
| Stakeholders            | Stakeholder analysis exists                               | `C8-Parties-Prenantes-RACI/README.md`                            | IMPLEMENTED                          | Final review                                                                            |
| RACI                    | RACI evidence exists                                      | C8                                                               | IMPLEMENTED                          | Link real decision records where available                                              |
| Acceptance criteria     | Requirements increasingly mapped to executable behaviour  | tests + this matrix                                              | PARTIAL                              | Complete remaining business-gap acceptance criteria                                     |

### BC02 Current Assessment

BC02 has a strong documentation foundation.

The largest remaining work is not creation of a new project-management framework but consolidation of final acceptance criteria, current business processes, accessibility/RGPD evidence and measured recovery objectives.

---

# 7. BC03 — Application Engineering

**Scope:** Official StarterPack

Primary evidence root:

```text
docs/evidence/03-BC03/
```

## BC03 Traceability

| Requirement                 | Project response                                           | Evidence                                                                    | Status                                                 | Remaining action                                                       |
| --------------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------- |
| Application architecture    | FastAPI layered backend documented                         | `C1-Architecture-Applicative-Maquettes/README.md`, application architecture | IMPLEMENTED                                            |                                                                        |
| Application mockups         | Integration/mockup requirement represented                 | C1                                                                          | PARTIAL                                                | Finalize required mockup evidence; no new production frontend required |
| Business processes          | Application workflows documented                           | `C2-Processus-Metier/README.md`                                             | PARTIAL                                                | Add Offer/Invoice flows once implemented                               |
| Technical environment       | Kubernetes/FastAPI/PostgreSQL/Data platform documented     | `C3-Environnement-Eco-Conception/README.md`                                 | IMPLEMENTED / DEPLOYED                                 |                                                                        |
| Eco-design                  | Principles represented                                     | C3                                                                          | PARTIAL                                                | Add measurable evidence where useful                                   |
| Architecture patterns       | Repository/service/router and platform patterns documented | `C4-Patterns-Architecture/README.md`                                        | IMPLEMENTED                                            |                                                                        |
| Authentication              | JWT authentication implemented                             | application/security code and docs                                          | IMPLEMENTED / TESTED / RUNTIME VERIFIED                |                                                                        |
| Password security           | Argon2id implemented                                       | security implementation                                                     | IMPLEMENTED / TESTED                                   |                                                                        |
| RBAC                        | ADMIN/CHASSEUR/CLIENT/SERVICE roles                        | `C5-Securite-Applicative/README.md` + security evidence                     | IMPLEMENTED / TESTED / RUNTIME VERIFIED                |                                                                        |
| Resource ownership          | Hunter ownership verified across key business resources    | security/runtime evidence                                                   | TESTED / RUNTIME VERIFIED                              | Extend consistently to future Offer/Invoice resources                  |
| Audit                       | Business audit logging implemented                         | audit documentation/runtime evidence                                        | IMPLEMENTED / RUNTIME VERIFIED                         |                                                                        |
| Demand workflow             | Demande and versioning implemented                         | API/database/tests                                                          | IMPLEMENTED / TESTED                                   |                                                                        |
| Pre-mandate demand          | Demand can exist before mandate                            | migration 005                                                               | IMPLEMENTED / TESTED                                   | Explicit client/prospect ownership remains to close                    |
| Hunter assignment           | `demande_affectation` implemented                          | migration 007                                                               | IMPLEMENTED / TESTED / CI VALIDATED                    |                                                                        |
| Mandate lifecycle           | Six-month renewable mandate periods                        | migration 008                                                               | IMPLEMENTED / TESTED / CI VALIDATED / RUNTIME VERIFIED |                                                                        |
| Matching                    | Deterministic recommendation service                       | matching service/tests                                                      | IMPLEMENTED / TESTED / RUNTIME VERIFIED                |                                                                        |
| Presentation                | Matching materialization/idempotence                       | API/database/tests                                                          | IMPLEMENTED / TESTED / RUNTIME VERIFIED                |                                                                        |
| Visit                       | Visit lifecycle implemented                                | API/tests/evidence                                                          | IMPLEMENTED / TESTED / RUNTIME VERIFIED                |                                                                        |
| Sale                        | Vente API/domain implemented                               | service/API/tests                                                           | IMPLEMENTED / TESTED / RUNTIME VERIFIED                |                                                                        |
| Remuneration                | Deterministic remuneration service                         | remuneration implementation/tests                                           | IMPLEMENTED / TESTED / RUNTIME VERIFIED                |                                                                        |
| Payment lifecycle           | ATTENDU→RECU→VERIFIE→PROGRAMME→PAYE                        | payment API/runtime evidence                                                | IMPLEMENTED / TESTED / RUNTIME VERIFIED                |                                                                        |
| Offer workflow              | Offer submission/revision/acceptance/rejection             | none currently                                                              | MISSING                                                | Implement business workflow                                            |
| Client invoice              | Company/client invoicing evidence                          | none currently                                                              | MISSING                                                | Model and implement                                                    |
| Hunter invoice verification | Invoice/document verification before payment               | payment state alone insufficient                                            | MISSING                                                | Model document/invoice verification                                    |
| Client contextual feedback  | Partial comments/visits exist                              | application                                                                 | PARTIAL                                                | Verify required client-scoped actions                                  |
| Notifications               | Reliable workflow notifications                            | insufficient evidence                                                       | MISSING / REQUIRES VERIFICATION                        | Define and implement required notifications                            |
| Executed tests              | Multiple application test campaigns exist                  | `C6-Tests-Executes/`                                                        | TESTED                                                 | Add current consolidated evidence                                      |
| Automated quality           | GitLab CI definitions exist                                | `C7-Qualite-Automatisee-CI/README.md`                                       | IMPLEMENTED                                            | Capture current relevant successful CI runs                            |

### BC03 Current Assessment

The core backend business application is substantially implemented.

The principal remaining business gaps are now concentrated around:

```text
Offer
Invoice
Hunter invoice verification
Pre-mandate client ownership
Client-scoped contextual actions
Notifications
```

These are targeted additions, not reasons to redesign the existing backend.

---

# 8. BC04 — Cybersecurity

**Scope:** Extended project / portfolio competency

Current dedicated evidence root:

```text
docs/evidence/04-BC04/
```

**Current state:** directory not yet created.

Existing security evidence is distributed across:

```text
docs/60-SECURITY/
docs/evidence/03-BC03/C5-Securite-Applicative/
docs/evidence/05-BC05/C8-Souverainete-Securite-IA/
```

## BC04 Traceability

| Requirement               | Project response                                            | Evidence                     | Status                                  | Remaining action                                                   |
| ------------------------- | ----------------------------------------------------------- | ---------------------------- | --------------------------------------- | ------------------------------------------------------------------ |
| Security architecture     | Security architecture documented                            | `docs/60-SECURITY/`          | IMPLEMENTED                             |                                                                    |
| Authentication security   | JWT + Argon2id                                              | backend/security tests       | IMPLEMENTED / TESTED                    |                                                                    |
| Authorization             | RBAC and ownership controls                                 | security/runtime evidence    | IMPLEMENTED / TESTED / RUNTIME VERIFIED |                                                                    |
| Auditability              | PostgreSQL business audit                                   | runtime audit evidence       | IMPLEMENTED / RUNTIME VERIFIED          |                                                                    |
| Container least privilege | Backend image UID/GID 10001                                 | image/runtime evidence       | IMPLEMENTED / RUNTIME VERIFIED          |                                                                    |
| Secret management         | Kubernetes Secret references                                | deployment manifests/runtime | IMPLEMENTED                             |                                                                    |
| Security risk assessment  | Risk material exists                                        | governance/security docs     | PARTIAL                                 | Produce BC04-specific risk/control mapping                         |
| Penetration testing       | No dedicated executed campaign established                  | —                            | MISSING                                 | Execute scoped lab assessment                                      |
| Remediation/retest        | Depends on pentest findings                                 | —                            | MISSING                                 | Capture remediation and retest                                     |
| Incident investigation    | No dedicated forensic exercise established                  | —                            | MISSING                                 | Execute controlled incident exercise                               |
| Security indicators       | Some operational/security signals exist                     | observability/security       | PARTIAL                                 | Produce BC04 security indicator evidence                           |
| SAST                      | CI evidence not currently established                       | CI                           | REQUIRES VERIFICATION                   | Inspect/configure and retain result                                |
| Dependency scanning       | Not established as executed evidence                        | CI                           | REQUIRES VERIFICATION                   | Configure/execute if selected                                      |
| Container scanning        | Not established as executed evidence                        | CI                           | REQUIRES VERIFICATION                   | Configure/execute if selected                                      |
| Secret scanning           | Not established as executed evidence                        | CI                           | REQUIRES VERIFICATION                   | Configure/execute if selected                                      |
| TLS trust                 | Historical SSL bypass concerns require current verification | GitOps/CI                    | REQUIRES VERIFICATION                   | Verify trusted CA path and remove bypasses if still present        |
| AI security               | Extensive design documentation exists                       | BC05/C8                      | PARTIAL                                 | Keep implemented controls distinct from future RAG/prompt controls |

### BC04 Current Assessment

The platform already contains meaningful preventive security controls.

BC04's main deficiency is **dedicated executed cybersecurity evidence**, particularly penetration testing, remediation/retest and incident investigation.

This is an evidence/workstream gap rather than absence of all security engineering.

---

# 9. BC05 — Data & AI

**Scope:** Official StarterPack — core project block

Primary evidence root:

```text
docs/evidence/05-BC05/
```

## BC05 Traceability

| Requirement                   | Project response                                          | Evidence                                            | Status                                                               | Remaining action                                  |
| ----------------------------- | --------------------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------- |
| MCD                           | Current business model documented                         | `C1-MCD-Migration-SQL/MCD-MERISE-PROJET.md`         | IMPLEMENTED                                                          |                                                   |
| MLD                           | Relational logical model documented                       | `MLD-PROJET.md`                                     | IMPLEMENTED                                                          |                                                   |
| MPD                           | PostgreSQL physical model documented                      | `MPD-POSTGRESQL.md`                                 | IMPLEMENTED                                                          |                                                   |
| SQL migrations                | Versioned migrations implemented                          | database migrations                                 | IMPLEMENTED / RUNTIME VERIFIED                                       |                                                   |
| Migration preservation        | Applied migrations preserved; extensions use new versions | migration_control                                   | IMPLEMENTED / RUNTIME VERIFIED                                       |                                                   |
| OLTP                          | PostgreSQL operational model                              | Data architecture/runtime                           | IMPLEMENTED / DEPLOYED / RUNTIME VERIFIED                            |                                                   |
| OLTP optimization             | Index/constraint strategy exists                          | `C2-OLTP-Optimisation/README.md`                    | IMPLEMENTED                                                          | Add measured EXPLAIN evidence where still missing |
| OLAP                          | Dimensional warehouse implemented                         | `C3-OLAP-Alimentation/README.md`, Data Warehouse V3 | IMPLEMENTED / RUNTIME VERIFIED                                       |                                                   |
| Warehouse grains              | Mandate, mandate period, payment etc. distinguished       | warehouse docs/schema                               | IMPLEMENTED                                                          |                                                   |
| Warehouse payment propagation | Payment 9 propagated into `fact_paiement`                 | runtime evidence                                    | RUNTIME VERIFIED                                                     |                                                   |
| Airflow orchestration         | End-to-end ingestion DAG                                  | pipeline                                            | IMPLEMENTED / DEPLOYED / RUNTIME VERIFIED                            |                                                   |
| Data Quality RAW              | Validation stage                                          | Data Quality V3                                     | IMPLEMENTED / RUNTIME VERIFIED                                       |                                                   |
| Data Quality STAGING          | Validation stage                                          | Data Quality V3                                     | IMPLEMENTED / RUNTIME VERIFIED                                       |                                                   |
| Data Quality OLTP             | Validation stage                                          | Data Quality V3                                     | IMPLEMENTED / RUNTIME VERIFIED                                       |                                                   |
| Data Quality WAREHOUSE        | Validation and financial reconciliation                   | Data Quality V3                                     | IMPLEMENTED / RUNTIME VERIFIED                                       |                                                   |
| dbt                           | Analytical transformations/tests                          | warehouse/dbt                                       | IMPLEMENTED / RUNTIME VERIFIED                                       |                                                   |
| 3V analysis                   | Volume/velocity/variety work                              | `C4-Volume-Velocite-Variete/README.md`              | IMPLEMENTED                                                          | Synchronize measurements if needed                |
| Matching design               | Explicit features and deterministic baseline              | `C5-Modele-Matching-IA/README.md`                   | IMPLEMENTED / TESTED                                                 |                                                   |
| Matching evaluation           | Controlled evaluation executed                            | matching/MLflow evidence                            | RUNTIME VERIFIED                                                     |                                                   |
| Matching production model     | Final trained ML model                                    | —                                                   | NOT APPLICABLE to current StarterPack requirement / future extension |                                                   |
| AI program architecture       | AI workflow documented                                    | `C6-Programme-IA/README.md`                         | IMPLEMENTED                                                          |                                                   |
| MLflow                        | Experiment tracking                                       | AI/MLOps evidence                                   | IMPLEMENTED / DEPLOYED / RUNTIME VERIFIED for evaluation             |                                                   |
| RGPD                          | Privacy principles documented                             | `C7-RGPD/README.md`                                 | PARTIAL                                                              | Complete treatment-specific register/evidence     |
| AI sovereignty                | Local-first design                                        | `C8-Souverainete-Securite-IA/README.md`             | DESIGNED / PARTIAL RUNTIME EVIDENCE                                  | Avoid claiming unexecuted RAG/prompt controls     |
| OpenMetadata                  | Governance/catalog deployed                               | governance/runtime evidence                         | IMPLEMENTED / DEPLOYED                                               |                                                   |
| Data lineage                  | Current platform lineage documented                       | `docs/40-DATA/06-Data-Lineage.md`                   | IMPLEMENTED                                                          |                                                   |
| Data Quality documentation    | Current framework synchronized                            | `docs/40-DATA/05-Data-Quality.md`                   | IMPLEMENTED                                                          |                                                   |
| Data model documentation      | Current model synchronized                                | `docs/40-DATA/02-Data-Model.md`                     | IMPLEMENTED                                                          |                                                   |
| Data Warehouse documentation  | Current warehouse synchronized                            | `docs/40-DATA/03-Data-Warehouse.md`                 | IMPLEMENTED                                                          |                                                   |

### BC05 Current Assessment

BC05 is the most mature project block.

The remaining work is primarily:

* measured OLTP optimization evidence,
* RGPD register completion,
* evidence consolidation,
* controlled final Data/AI presentation,
* continued separation of deterministic matching from optional future ML extensions.

---

# 10. BC06 — DevOps

**Scope:** Extended project / portfolio competency

Current dedicated evidence root:

```text
docs/evidence/06-BC06/
```

**Current state:** directory not yet created.

Existing DevOps evidence is distributed across:

```text
docs/30-INFRASTRUCTURE/
docs/70-DEVOPS/
docs/80-OPERATIONS/
docs/90-OBSERVABILITY/
docs/PCA PRA/
GitLab CI
lab-gitops
Argo CD
Kubernetes runtime
```

## BC06 Traceability

| Requirement              | Project response                            | Evidence                   | Status                         | Remaining action                                 |
| ------------------------ | ------------------------------------------- | -------------------------- | ------------------------------ | ------------------------------------------------ |
| DevOps strategy          | GitOps/Kubernetes platform architecture     | DevOps/infrastructure docs | IMPLEMENTED                    |                                                  |
| Source control           | Git repositories/versioning                 | Git                        | IMPLEMENTED                    |                                                  |
| CI pipeline              | Modular GitLab CI                           | `.gitlab/ci/`              | IMPLEMENTED                    | Consolidate latest successful execution evidence |
| Automated tests          | CI test stages exist                        | CI/test evidence           | IMPLEMENTED / TESTED           |                                                  |
| Container build          | Backend/data pipeline images                | GitLab Registry            | IMPLEMENTED                    |                                                  |
| Kubernetes orchestration | kubeadm HA cluster                          | runtime evidence           | DEPLOYED / RUNTIME VERIFIED    |                                                  |
| GitOps                   | Argo CD reconciliation                      | Argo CD runtime            | DEPLOYED / RUNTIME VERIFIED    |                                                  |
| Deployment health        | Core Real Estate apps Synced/Healthy        | Argo CD/Kubernetes         | RUNTIME VERIFIED               |                                                  |
| Health probes            | `/health`, `/ready`                         | deployment/runtime         | IMPLEMENTED / RUNTIME VERIFIED |                                                  |
| Resource requests/limits | Backend resource policy                     | deployment                 | IMPLEMENTED                    |                                                  |
| Non-root image           | UID/GID 10001                               | container runtime          | RUNTIME VERIFIED               |                                                  |
| Observability            | Prometheus/Grafana/Loki/Tempo/OTEL          | observability stack        | DEPLOYED                       |                                                  |
| Business metrics         | Real-estate metrics                         | Prometheus/Grafana         | RUNTIME VERIFIED               |                                                  |
| Financial metrics        | Payment/fees/remuneration/rate              | Grafana runtime            | RUNTIME VERIFIED               |                                                  |
| Data Quality metrics     | Layer status via Pushgateway/Prometheus     | observability              | RUNTIME VERIFIED               |                                                  |
| Backup automation        | PostgreSQL CronJob                          | PRA                        | DEPLOYED / RUNTIME VERIFIED    |                                                  |
| Restore                  | Isolated PostgreSQL 16 restore              | PRA evidence               | TESTED / RUNTIME VERIFIED      |                                                  |
| Rollback demonstration   | Target capability exists through GitOps     | —                          | REQUIRES VERIFICATION          | Execute/document controlled rollback             |
| Failure alerting         | Monitoring stack exists                     | —                          | PARTIAL                        | Execute alert scenario and retain evidence       |
| Release traceability     | Git→CI→Registry→GitOps→Runtime architecture | cross-cutting evidence     | PARTIAL                        | Consolidate one complete delivered-version trace |
| Performance/resources    | Kubernetes metrics available                | monitoring                 | PARTIAL                        | Capture measured results                         |
| REX DevOps               | Dedicated final return-of-experience        | —                          | MISSING                        | Produce BC06 REX                                 |
| Dedicated BC06 portfolio | No evidence directory currently             | —                          | MISSING                        | Create and organize evidence                     |

### BC06 Current Assessment

DevOps implementation is substantial and already operating.

The principal BC06 gap is **evidence packaging and controlled operational demonstrations**, not creation of a new deployment platform.

---

# 11. Cross-Cutting Requirements

Primary evidence root:

```text
docs/evidence/99-CROSS-CUTTING/
```

## Traceability

| Requirement           | Current state                                             | Status                         | Remaining action                          |
| --------------------- | --------------------------------------------------------- | ------------------------------ | ----------------------------------------- |
| Documentation as code | Extensive Markdown/PlantUML documentation                 | IMPLEMENTED                    | Maintain synchronization                  |
| Git traceability      | Source/version history                                    | IMPLEMENTED                    | Link important final commits              |
| CI traceability       | Pipelines exist                                           | IMPLEMENTED                    | Capture final successful pipeline IDs     |
| GitOps traceability   | Argo CD deployment model                                  | DEPLOYED / RUNTIME VERIFIED    | Consolidate release chain                 |
| Runtime evidence      | Kubernetes/API/PostgreSQL/Airflow/Grafana evidence exists | RUNTIME VERIFIED               | Organize by requirement                   |
| RGPD                  | Design exists                                             | PARTIAL                        | Final register/evidence                   |
| Accessibility         | Recommendations exist                                     | PARTIAL                        | Final annotated mockups                   |
| Eco-design            | Architecture principles exist                             | PARTIAL                        | Quantified decision evidence              |
| Data sovereignty      | Local-first platform                                      | IMPLEMENTED / PARTIAL EVIDENCE | Verify exact external flows               |
| Security              | Multiple preventive controls                              | IMPLEMENTED / PARTIAL EVIDENCE | BC04 exercises                            |
| PCA/PRA               | PostgreSQL recovery proven                                | TESTED / RUNTIME VERIFIED      | Application-level objectives              |
| Observability         | Platform + business monitoring                            | DEPLOYED / RUNTIME VERIFIED    | Alert/recovery drills                     |
| Evidence integrity    | Evidence policy documented                                | IMPLEMENTED                    | Continue preserving dates/version context |

---

# 12. Current Business Requirement Coverage

The current implemented business lifecycle is:

```text
Client
  |
  v
Demande
  |
  v
Affectation Chasseur
  |
  v
Demande Version
  |
  v
Mandat
  |
  v
Mandat Period
  |
  v
Matching
  |
  v
Presentation
  |
  v
Visite
  |
  v
Vente
  |
  v
Honoraires
  |
  v
Remuneration
  |
  v
Paiement
```

The reviewed StarterPack business journey additionally requires areas that remain incomplete:

```text
Offer workflow
Client invoice
Hunter invoice / verification
Reliable notifications
Client contextual actions
```

These are tracked as confirmed business gaps.

---

# 13. Confirmed Functional Gap Register

## GAP-BUS-001 — Pre-Mandate Client Ownership

**Status:** MISSING / PARTIAL

A demand can exist before a mandate, but the request requires an explicit client/prospect ownership model independent of mandate attachment.

Required outcome:

```text
Client
  |
  v
Demande
```

must remain explicit before:

```text
Demande
  |
  v
Mandat
```

Historical unknown ownership must not be fabricated.

---

## GAP-BUS-002 — Offer Workflow

**Status:** MISSING

Required lifecycle includes:

```text
Offer
  |
  +--> submitted
  +--> revised
  +--> accepted
  +--> rejected
  +--> withdrawn
```

Offer history must be traceable.

A resulting sale should be linkable to the accepted offer where applicable while preserving legitimate external-sale paths.

---

## GAP-BUS-003 — Client Invoice

**Status:** MISSING

The post-sale business flow requires company/client invoicing.

The current payment/remuneration implementation does not prove that a client invoice exists.

---

## GAP-BUS-004 — Hunter Invoice Verification

**Status:** MISSING

The hunter remuneration workflow requires evidence of the hunter invoice/document and its verification.

`PAIEMENT.statut = VERIFIE` alone does not establish:

```text
invoice exists
invoice belongs to hunter
invoice amount is valid
verification occurred
verifier identity
verification result
verification date
```

These must be represented explicitly.

---

## GAP-BUS-005 — Document Context

**Status:** PARTIAL

A generic document model exists.

Its relationship with:

* mandates,
* offers,
* invoices,
* visits,
* transaction evidence

must be evaluated and extended only where required.

---

## GAP-BUS-006 — Transaction Identity

**Status:** REQUIRES DESIGN / IMPLEMENTATION

The platform must prevent the same real commercial transaction from being recorded or remunerated more than once while still allowing genuinely distinct transactions.

Individual foreign keys and simple uniqueness constraints may not be sufficient.

---

## GAP-BUS-007 — Visit Scope for Remuneration

**Status:** REQUIRES BUSINESS VERIFICATION

The exact visit population used by remuneration must be reconciled with the StarterPack interpretation.

The current implementation must not be changed until the intended business scope is documented.

---

## GAP-BUS-008 — Historical Financial Integrity

**Status:** PARTIAL

Calculation snapshots exist.

Stronger protection of finalized financial inputs/results should be assessed so historical calculations remain reproducible while legitimate correction workflows remain possible.

---

## GAP-BUS-009 — Relationship Consistency

**Status:** PARTIAL

A sale references several related business objects.

The platform must guarantee consistency between:

```text
sale
mandate
mandate period
presentation
property
beneficiary hunter
```

Individual foreign keys do not automatically prove cross-relationship consistency.

---

## GAP-BUS-010 — Concurrency Controls

**Status:** REQUIRES VERIFICATION

Database triggers and uniqueness controls exist.

Concurrency safety of overlap checks and financial uniqueness must be explicitly assessed rather than inferred from trigger presence.

---

## GAP-BUS-011 — Buyer API / Contextual Actions

**Status:** PARTIAL / MISSING

Client-scoped operations should support the required business interactions while preventing cross-client access.

Required exact operations must be derived from the accepted business workflow.

---

## GAP-BUS-012 — Notifications

**Status:** MISSING / REQUIRES VERIFICATION

Required business notifications and expiry handling need reliable implementation and idempotent behaviour.

External delivery may remain configurable or disabled in controlled test environments.

---

## GAP-BUS-013 — Performance Recalculation

**Status:** PARTIAL

The timing and triggers for hunter performance recalculation, including payment and mandate-expiry events, require explicit business semantics.

No new performance criterion should be invented to resolve ambiguity.

---

# 14. Controlled E2E Evidence

A controlled E2E validation scenario has already demonstrated the implemented core chain:

```text
Mandat 17
   |
Mandat Period 2
   |
Demand Version 137
   |
Property 16025
   |
Presentation 32
   |
Visit 6
   |
Sale 3
   |
Payment 9
```

Observed outcome:

```text
Purchase amount       300,000.00 EUR
Company fees           10,500.00 EUR
Hunter remuneration     3,939.60 EUR
Final rate                 37.52%
Payment status               PAYE
```

The scenario demonstrated:

* matching,
* presentation,
* visit,
* sale,
* remuneration,
* payment lifecycle,
* audit,
* warehouse propagation,
* business metrics.

It is a **controlled E2E validation scenario**, not a genuine historical commercial transaction.

---

# 15. Database Evolution Evidence

Applied migration sequence currently verified through:

```text
001
002
003
004
005
006
007
008
009
010
011
012
```

Major recent evolution:

```text
005 -> pre-mandate demand
006 -> authentication identity
007 -> hunter assignment
008 -> six-month mandate lifecycle
009 -> mandate-period warehouse fact
010 -> transaction/remuneration foundation
011 -> approved remuneration configuration
012 -> hunter seniority provenance/backfill
```

Applied migrations must not be rewritten.

Any new schema work must use the next unused migration after checking the actual repository/database sequence.

---

# 16. Data Platform Evidence

Current validated pipeline:

```text
generate_source_data
        |
load_raw
        |
validate_raw
        |
transform_staging
        |
validate_staging
        |
load_oltp
        |
validate_oltp
        |
load_warehouse
        |
validate_warehouse
        |
dbt_run
        |
dbt_test
        |
collect_metrics
```

A successful complete runtime execution has been observed.

The DAG is currently manually triggered (`schedule=None`).

It must not be described as a periodic scheduled ingestion pipeline.

---

# 17. Observability Evidence

Current stack includes:

```text
Prometheus
Grafana
Loki
Promtail
Tempo
OpenTelemetry Collector
Pushgateway
```

Business/financial metrics include:

```text
real_estate_paiements_payes_total
real_estate_honoraires_total_euros
real_estate_remunerations_chasseur_total_euros
real_estate_taux_remuneration_moyen
```

Runtime Grafana evidence has shown:

```text
Paid Payments                   1
Company Fees Collected         10.50K EUR
Hunter Remuneration Paid        3.94K EUR
Average Remuneration Rate      37.52%
```

Metric agreement with warehouse values must not be used by itself to claim that the collector reads a particular warehouse table.

Physical metric-source lineage requires inspection of the collector implementation.

---

# 18. AI / ML Evidence Boundary

The project currently has a deterministic matching baseline.

MLflow is used for experimentation/evaluation.

The project must distinguish:

```text
Deterministic production-capable baseline
```

from:

```text
Experimental ML training/evaluation
```

A final trained production matching model is not currently required to satisfy the reviewed StarterPack.

RAG, vector databases, Kafka and additional LLM architecture are not mandatory project gaps.

They must only be introduced if a concrete accepted requirement justifies them.

---

# 19. Evidence Directory Gaps

Current evidence roots:

```text
01-BC01
02-BC02
03-BC03
05-BC05
99-CROSS-CUTTING
```

Missing dedicated roots:

```text
04-BC04
06-BC06
```

These directories should eventually be created because BC04 and BC06 remain part of the extended project scope.

Their absence does not mean no security or DevOps work exists.

It means the evidence is currently distributed and requires dedicated portfolio packaging.

---

# 20. Documentation Drift Register

Known documentation/evidence drift includes:

* historical test counts in evidence indexes;
* historical gap reviews that predate migrations 007–012;
* old statements describing remuneration/payment as missing;
* old statements describing six-month mandate lifecycle as missing;
* AI/security documents mixing implemented controls with target/future controls;
* duplicate BC01 C1 documentation;
* duplicated BC01 C3 directory nesting;
* evidence indexes requiring synchronization with current runtime state.

Historical reports should not be rewritten to appear current.

Instead:

```text
Historical assessment
        |
        v
Current matrix
        |
        v
Current evidence
```

should demonstrate project evolution.

---

# 21. Current Priority Backlog

The current priority is no longer broad platform construction.

The next implementation work should close confirmed business gaps in coherent slices.

Recommended order:

```text
1. Pre-mandate client ownership
2. Offer workflow
3. Invoice model / verification
4. Transaction identity and relationship consistency
5. Buyer contextual API
6. Notifications
7. Performance recalculation semantics
8. Historical financial integrity
9. Concurrency verification/hardening
```

Documentation/evidence work can proceed in parallel for:

```text
BC01 decision matrix
BC02 final deliverable consolidation
BC03 current test evidence
BC04 portfolio
BC05 performance/RGPD evidence
BC06 portfolio and operational demonstrations
```

---

# 22. Definition of Requirement Closure

A requirement is not considered fully closed simply because code exists.

For a business requirement, the target closure chain is:

```text
Requirement accepted
      |
      v
Architecture/model updated
      |
      v
Migration if necessary
      |
      v
Implementation
      |
      v
Automated tests
      |
      v
Database-backed acceptance
      |
      v
CI validation
      |
      v
GitOps deployment
      |
      v
Runtime verification
      |
      v
Evidence archived
      |
      v
Documentation synchronized
```

Not every requirement requires every stage, but skipped stages must be justified.

---

# 23. Matrix Maintenance Rules

This document must be updated when:

* a new business requirement is accepted;
* a confirmed gap is implemented;
* a migration is applied;
* a significant test campaign completes;
* CI validation changes status;
* a deployment is runtime verified;
* a major evidence artifact is added;
* a requirement is intentionally removed or declared out of scope.

Do not convert:

```text
DESIGNED
```

directly into:

```text
RUNTIME VERIFIED
```

without evidence.

Do not convert historical runtime evidence into current health evidence without a new observation.

---

# 24. Jury Navigation

For review and presentation, the recommended navigation is:

```text
REQUIREMENTS-EVIDENCE-MATRIX.md
            |
            +--> BC01 evidence
            |
            +--> BC02 evidence
            |
            +--> BC03 evidence
            |
            +--> BC05 evidence
            |
            +--> BC04 extended evidence
            |
            +--> BC06 extended evidence
            |
            +--> Cross-cutting evidence
```

The matrix is the entry point.

Detailed architecture documents remain supporting evidence rather than replacing concise competency deliverables.

---

# 25. Current Overall Assessment

The project has moved beyond an architecture prototype.

It currently demonstrates substantial implementation across:

* software architecture,
* PostgreSQL OLTP,
* dimensional analytics,
* Data Quality,
* matching,
* MLOps experimentation,
* security,
* RBAC,
* audit,
* remuneration,
* financial lifecycle,
* Kubernetes,
* GitOps,
* observability,
* governance,
* PCA/PRA.

The remaining work is concentrated in two categories.

## Business completion

```text
Offer
Invoice
Invoice verification
Pre-mandate ownership
Buyer interactions
Notifications
Transaction integrity
Financial historical integrity
```

## Evidence completion

```text
BC01 decision evidence
BC02 final consolidation
BC03 current execution evidence
BC04 dedicated portfolio
BC05 measured optimization/RGPD evidence
BC06 dedicated portfolio and operational demonstrations
```

The correct strategy is therefore:

```text
PRESERVE VALIDATED PLATFORM
        +
CLOSE CONFIRMED BUSINESS GAPS
        +
EXECUTE MISSING EVIDENCE
        +
SYNCHRONIZE DOCUMENTATION
        +
PREPARE JURY NAVIGATION
```

rather than rebuilding already validated components.

---

# 26. Conclusion

This matrix establishes the authoritative connection between the project requirements, implementation and evidence.

It preserves the official StarterPack distinction:

```text
BC01 + BC02 + BC03 + BC05
```

while retaining:

```text
BC04 + BC06
```

as deliberate extended project competencies.

The platform already provides substantial technical and runtime evidence. The remaining work can now be managed as explicit, traceable gaps instead of broad or speculative platform development.

Every future implementation increment should update this matrix so that the final project can demonstrate not only what was designed, but what was actually:

```text
IMPLEMENTED
TESTED
VALIDATED
DEPLOYED
OBSERVED
AND EVIDENCED
```
