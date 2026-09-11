# StarterPack comparison and completion plan — BC01 to BC06

Review date: 2026-09-11. Scope: all six competency blocks, explicitly confirmed by the project owner.

Local commit: `221533547427fab77519f3cda583c1bde77a1e13`, plus the current working-tree documentation changes. Public StarterPack HEAD verified through the GitHub API: `902207e3c72fe5c806f639020e00558d0f592a26`.

## Assessment

The project has substantial backend, data, matching, delivery, and observability implementation. It is not yet a complete business delivery or a defensible evidence package for all six blocks. The largest implementation gap is the commercial/remuneration workflow. The largest additional competency gap is BC04 security assessment and incident investigation. BC02 and the cross-cutting deliverables need consolidation into actual reviewable documents.

This is a source/documentation assessment. No production environment, external GitOps repository, cluster, or live database was audited. The earlier local test run in this conversation passed 239 tests with seven warnings; those tests were not rerun for this report. Historical runtime reports are credited as dated evidence, not current health checks. No completion percentage or certification award is inferred from file counts.

## Baseline and scope

The [pinned assignment](https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack/blob/902207e3c72fe5c806f639020e00558d0f592a26/Readme.md) uses four project phases and covers BC01/02/03/05. Our six-block scope additionally includes BC04 and BC06, assessed against [RNCP40573](https://www.francecompetences.fr/recherche/rncp/40573/).

Two scope corrections matter: the existing website and business client are outside the StarterPack implementation scope, although mockups and accessibility recommendations remain deliverables; training a matching model is not required by that assignment. The implemented ML tooling is useful additional work. A new React application, RAG, Kafka, Spark, Vault, or Keycloak should not displace missing business behavior or mandatory evidence.

The [evaluation grid](https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack/blob/902207e3c72fe5c806f639020e00558d0f592a26/documents%20utiles/GRILLE-EVALUATION.md) favors concise, defensible deliverables. Our long architecture documents are supporting material; they do not automatically replace a completed register, mockup, decision matrix, or execution report.

## Position by block

| Block | Current position | Evidence in this repository | Remaining work |
|---|---|---|---|
| BC01 — SI strategy | Substantial documentation; baseline closure incomplete | Current-state diagrams, SI strategy, OLTP/OLAP comparison, component analysis, ADRs, risk register, supporting technology-watch material | Separate the inherited business SI audit from the new platform audit. Attach fixture anomalies and their disposition. Finish the weighted architecture decision matrix, consolidate watch findings into decisions, and prepare the stakeholder presentation. |
| BC02 — Project management | Documented foundation; final deliverables incomplete | Opportunity study, backlog, framing/planning/RACI sections, risk register, dated database recovery report | Produce or attach the standalone technical specification and framing note; establish dates, owners, effort/budget assumptions, dependencies, acceptance criteria, RACI, and real decision/meeting records. Complete business processes, privacy/accessibility evidence, and full recovery objectives. |
| BC03 — Application | Core backend implemented and locally tested; commercial scope incomplete | FastAPI services, SQLAlchemy repositories, versioned demands, matching/presentations, visits, JWT/RBAC/audit, Python tests and CI | Complete commercial endpoints and their rules; enforce owner/resource boundaries; produce mockups and final process diagrams; execute database-backed acceptance and attach code-specific pattern explanations. |
| BC04 — Cybersecurity | Preventive controls exist; dedicated assessment evidence missing | Authentication, role gates, audit persistence, non-root backend image, Secret references, security architecture, security tests | Create a dedicated block mapping. Complete scoped risk/control analysis, lab pentest and remediation/retest evidence, an incident/forensic exercise, and security indicators with reports. Address concrete authorization and certificate-trust gaps. |
| BC05 — Data and AI | Strongest implementation area; remaining model and evidence gaps | Migrations 001–006, conceptual/logical/physical models, loaders, dbt, DQ, governance, deterministic matching, training/comparison modules | Reconcile models with migrations and remuneration extensions, demonstrate migration and constraint behavior, produce measured EXPLAIN before/after results, benchmark growth assumptions, consolidate warehouse/ML runs and privacy controls, and prepare a Data/AI REX. |
| BC06 — DevOps | Substantial implementation; operational demonstration incomplete | Modular GitLab CI, images, Kubernetes/Kustomize, GitOps publication, Prometheus/Grafana assets, backup CronJob and historical restore report | Create a dedicated block mapping and REX. Demonstrate clean build-to-deploy, quality/security gates, rollback, failure alerting, recovery, and resource/performance measurements against the delivered version. Link external infrastructure evidence. |

The official BC04 scope includes risk/security strategy, penetration testing, forensic investigation, and security indicators. BC06 includes a business-aligned automation strategy, CI/CD/GitOps, container orchestration, and observability; its deliverables include a completed DevOps project and REX. These are competency outcomes, not a mandate to install particular products. See the [official block descriptions](https://www.francecompetences.fr/recherche/rncp/40573/).

## Concrete implementation gaps

### 1. Remuneration and payment workflow — highest business priority

The existing [September 9 remuneration gap review](STARTERPACK-GAP-REVIEW-2026-09-09.md) examines the same StarterPack commit verified today. Its central finding remains current: SQL tables exist for commission grids and payments, but no corresponding calculation/payment service, router, or test suite is present in the inspected source tree.

Complete this as one coherent increment:

- Record fee/rate ownership, eligibility, time-window, rounding, grid-selection, and renewal decisions. Preserve ambiguities in imported legacy rates until resolved.
- Extend the data model for transaction attribution, versioned parameters, and frozen calculation inputs/results. Preserve applied migration history.
- Implement deterministic Decimal-based calculations, boundary tests, and historical reproducibility.
- Implement authorized and idempotent calculation/payment operations, invoice validation/status transitions, and performance updates.
- Propagate resulting data changes to warehouse, dbt, and governance.

The [remuneration specification](https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack/blob/902207e3c72fe5c806f639020e00558d0f592a26/documents%20utiles/REGLES-CALCUL-REMUNERATION.md) and associated scenarios should be the acceptance input. Proposed teaching example parameters must remain distinguished from project decisions. The earlier review also identifies an expired-mandate worked-example ambiguity; it should not silently become a passing business case.

### 2. Mandates and the full business journey

`src/api/schemas/mandat.py` checks that the end date is not before the start date. It does not enforce six calendar months from signature or a traceable renewal process. The initial SQL migration explicitly defers the six-month rule.

Create acceptance scenarios covering initial validity, renewal history, expiry, and their consequences for remuneration. Complete or explicitly disposition the remaining journey: hunter assignment/acceptance, client feedback/comments, offer/deed handling, invoices/payments, and notifications. A database table does not establish an exposed, usable business workflow. Mockups can demonstrate integration with the existing client applications without replacing them.

### 3. Resource ownership is not established by role gates

Role checks have progressed since the September 9 alignment report: current business endpoint modules use `require_roles`. The older claim that most routes lack authentication is superseded.

However, `list_mandats()` allows a CHASSEUR to omit filters and reach the unrestricted listing; `get_mandat()` retrieves the supplied ID without comparing it to the authenticated hunter. The inspected service and repository do not add that ownership boundary. Define the intended access policy and enforce it consistently for mandates, demands, presentations, visits, and future financial data. Test two different hunters/clients, not only anonymous versus allowed roles.

### 4. Delivery security and operational gates

GitOps publication workflows still contain `GIT_SSL_NO_VERIFY=true`. Replace those bypasses with lab CA trust and demonstrate successful publication with verification enabled.

No executable pentest/forensic evidence or configured common SAST/dependency/image scanning job was identified in the inspected CI/test/deployment paths. Select useful checks, define failure criteria, and retain results and remediation evidence. Inspect the actual job dependency graph to prove that failing acceptance/security checks block the relevant delivery path; configuration presence alone is insufficient.

### 5. Recovery is advanced but not finished

The [PCA/PRA report](../PCA%20PRA/PCA-PRA-POSTGRESQL.md) records external backup, isolated restore, and matching selected business table counts. It reports approximately six seconds for the tested PostgreSQL restore component. Credit that evidence; do not describe recovery as wholly absent or label six seconds as the complete application RTO.

The report itself leaves permanent CronJob execution, retention/ILM, failure/staleness monitoring, application recovery, and final RTO open. The daily CronJob manifest exists. Finish its runtime proof and measure restoration through API readiness and a business transaction.

## Required evidence and document gaps

The [StarterPack traceability matrix](https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack/blob/902207e3c72fe5c806f639020e00558d0f592a26/documents%20utiles/TRACABILITE-COMPETENCES.md) connects competencies to deliverables, including privacy, accessibility, eco-design, and AI data security. Use it for the original four blocks and extend it with the official requirements for BC04/06.

| Deliverable | Observed gap | Completion evidence |
|---|---|---|
| Inherited-SI audit | Current BC01 audit focuses heavily on the new platform; a clearly consolidated fixture-anomaly register was not established | Original-model diagram, concrete problematic records/rules, severity, migration disposition, and legacy commission interpretation |
| Architecture decision matrix | BC01 comparison explicitly marks weighted C5 decision as still to produce | Alternatives, weights, rationale, result, and sensitivity to changed growth assumptions |
| Technical specification and framing note | BC02 indexes say standalone files are absent or need attachment | Self-contained scope, rules, API integration, acceptance, dates, resources, and budget assumptions |
| Planning and responsibilities | General planning/RACI documentation exists; final dated project evidence remains to consolidate | Baseline versus actual milestones, named owners, decision records and stakeholder reviews; no fabricated meetings |
| Privacy register | BC05 C7 explicitly says the standalone register is absent locally | Completed treatment-specific table with purposes, legal bases, recipients, retention, and security; link implemented controls |
| Accessibility | Recommendations are described; final mockups remain open | Concise note and annotated mockups covering keyboard use, contrast, targets, labels, alternatives, and error behavior |
| Eco-design | Principles exist; quantified backup-frequency tradeoff not established | Compare minute/hour/12-hour/day backup options, retention/storage implications and chosen policy; distinguish estimates from measurements |
| Performance | SQL and methodology exist; OLTP index evidence is marked pending | Repeatable dataset and workload, EXPLAIN ANALYZE/BUFFERS before/after, timings, query plans, and interpretation |
| End-to-end acceptance | Local tests and partial dated runtime reports exist | PostgreSQL-backed complete business scenario, denial cases, persistence checks, version/environment and captured results |
| BC04 portfolio | No dedicated `04-BC04` evidence directory found | Risk/control mapping, scoped lab assessment, remediation/retest, incident timeline, preserved evidence, findings and security dashboard/report |
| BC06 portfolio | No dedicated `06-BC06` evidence directory found | Strategy, pipeline/release trace, rollback, monitoring/alert drill, resource results, recovery evidence, and REX |

These are missing or incomplete in the reviewed checkout; externally held evidence may close them once attached and verified. A separate directory is an organizational recommendation, not a certification rule.

## Recommended delivery order

| Order | Deliverable | Exit condition |
|---|---|---|
| 1 | Six-block acceptance matrix and business decisions | Every required outcome has an owner, artifact path, status, and acceptance check; remuneration ambiguities and frontend scope are explicit |
| 2 | Complete the commercial backend and authorization | Mandate validity/renewal, financial calculation/payment lifecycle, and owner boundaries pass unit and database-backed acceptance |
| 3 | Close baseline documents and models | Final mockups, specification, framing/planning/RACI, RGPD register, eco note, decision matrix, and synchronized MCD/MLD/SQL |
| 4 | Validate data and growth | Migration/constraint results, warehouse/DQ evidence, measured query/ingestion/matching results, and reproducible Data/AI report |
| 5 | Complete BC04 security evidence | Agreed lab assessment and incident-investigation exercises completed, findings remediated or explicitly tracked, retest and indicators retained |
| 6 | Complete BC06 operations and final presentation | Release/rollback/alert/recovery demonstrations and REX linked to delivered versions; concise jury navigation and individual oral rehearsal |

Documentation and operational preparation can progress alongside implementation. More ML models, model serving, RAG, enterprise IAM products, or a new frontend are follow-on choices unless added explicitly to the accepted scope.

## Navigation and evidence hygiene

The current evidence tree covers BC01/02/03/05 and cross-cutting items. BC01 C3 is accidentally nested twice; BC01 C1 has both `README.md` and `README-v1.md`. Choose authoritative entry points and repair references when consolidating the portfolio. Keep historical reports dated; do not overwrite them as if their observations were current.

Useful local sources inspected include `src/api/api/v1/router.py`, `src/api/api/v1/endpoints/mandats.py`, `src/api/services/mandat.py`, `src/api/schemas/mandat.py`, migrations 001–006, `.gitlab/ci/`, `deploy/`, and the competency evidence indexes. The [application architecture](../20-APPLICATION/01-Application-Architecture.md) and [root README](../../Readme.md) now provide the implementation entry points. Their mention of a planned React interface describes an optional project extension, not a missing StarterPack implementation obligation.
