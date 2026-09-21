# GAP-BUS-004 — Facture Chasseur

Repository implementation: 2026-09-21. Structured submission, manual conformity
review and payment gating are implemented and locally unit/contract tested.
Migration 016 and SQL test 019 have **not been executed by Codex**. This gap is
not marked runtime verified or closed.

## Requirement and existing foundation

Business reference: StarterPack baseline
`902207e3c72fe5c806f639020e00558d0f592a26`,
[hunter remuneration journey](https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack/blob/902207e3c72fe5c806f639020e00558d0f592a26/user-stories/07_chasseur_remuneration_et_performance.feature)
and [project reference](https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack/blob/902207e3c72fe5c806f639020e00558d0f592a26/Readme.md).
The journey establishes receipt of company fees, informing the hunter of the
amount, invoice preparation/submission, verification, programmed payment,
paid status and performance refresh. It does not specify exact conformity
criteria, rejection/correction mechanics or a required upload format.
The future assistant journey describes autonomous verification; the review
implemented here is explicitly manual.

| Concern | Existing implementation / remaining gap |
| --- | --- |
| Remuneration calculation | `RemunerationService` and calculator already persist entitlement, beneficiary, amount, configuration and performance snapshot in `paiement`. Reused without recalculation. |
| Amount visibility | Existing `/remunerations` reads expose persisted payment amounts. No notification delivery subsystem is introduced. |
| Payment lifecycle | Existing `ATTENDU → RECU → VERIFIE → PROGRAMME → PAYE`, with cancellation before payment. Reused. |
| Invoice evidence | Previously absent: `VERIFIE` alone did not establish a submission, owner, amount, reviewer or result. Added in migration 016. |
| Generic documents | Existing `document` requires property context and has no reusable upload API. No artificial property association is introduced. |
| Client invoices / transaction identity | Migration 015 and completed client invoicing are untouched. No `vente.id_offre` is added. |

## Project decisions

These are implementation decisions, not additional attributed StarterPack rules:

- An incoming invoice is a **structured business record** containing a
  hunter-supplied reference, date and amount. It is not a PDF, uploaded document,
  tax-compliance certification or automated document-analysis result.
- The authoritative owner and expected amount are
  `paiement.id_chasseur_beneficiaire` and `paiement.montant_chasseur`.
  Ownership never comes from request fields or a current mandate reassignment.
- Submission requires a received-fee payment (`RECU`, `VERIFIE` or `PROGRAMME`),
  a linked sale, positive remuneration, affirmative entitlement and coherent
  deed/receipt dates. Invoice date must fall between fee receipt and today (UTC).
- A positive submitted amount may differ from the expected amount so a
  nonconforming submission can be recorded and rejected. Conformity requires
  exact Decimal equality with the persisted remuneration, matching beneficiary
  and valid dates. No rounding tolerance or new remuneration engine is added.
- Only ADMIN reviews. A rejection requires a reason; a conforming decision
  forbids a rejection reason. The server supplies reviewer identity and time.
- Only one submitted or conforming invoice may exist per payment. Rejected
  submissions are retained; correction creates the next version. There is no
  edit/delete endpoint for previous versions. References can be reused in a
  correction; this increment does not enforce global or per-hunter invoice
  number uniqueness across different payments.
- Accepting an invoice advances `RECU → VERIFIE → PROGRAMME` using the existing
  payment service, in one transaction with invoice and audit changes. `PROGRAMME`
  records workflow readiness; no bank transfer or payment date is invented.
- Existing ADMIN payment execution remains `PATCH /paiements/{id}/statut` to
  `PAYE`, with its required payment date. All advances to `VERIFIE`, `PROGRAMME`
  or `PAYE` require a matching conforming invoice. Repeating the current status
  remains an idempotent no-op; it does not create missing evidence.

`SOUMISE → CONFORME` is terminal for that invoice version.
`SOUMISE → REJETEE` permits a **new** `SOUMISE` version. This is an invoice review
lifecycle, not a replacement payment state machine.

Existing unpaid `VERIFIE`/`PROGRAMME` payments can receive a genuine submission
and review without a status downgrade. Already `PAYE` or `ANNULE` payments
cannot accept submissions or reviews. No historical invoices are fabricated,
and the previously verified payment 9 is not changed. A pending invoice on a
subsequently cancelled payment remains visible as historical evidence.

Notification delivery, PDF/upload storage, autonomous conformity analysis,
bank execution and immediate performance recomputation are not implemented
by this increment. Existing analytics/warehouse processing remains responsible
for its existing refresh cadence; no new refresh guarantee is claimed.

## API and security

All paths below have prefix `/api/v1`.

| Method / path | Authorization | Result |
| --- | --- | --- |
| `GET /factures-chasseurs` | ADMIN: all; CHASSEUR: own payment lineage | Submission history |
| `GET /factures-chasseurs/{invoice_id}` | Same scope | One version; absent/foreign both 404 |
| `POST /factures-chasseurs` | CHASSEUR with authenticated hunter identity | 201; submit own invoice |
| `POST /factures-chasseurs/{invoice_id}/decision` | ADMIN only | Conformity or rejection |

CLIENT and SERVICE have no access. Missing authentication gives 401; missing
hunter identity gives 403. Submission/decision schemas reject forged owner,
reviewer, timestamps and version fields. Business conflicts give 409; invalid
dates/amount conformity give 422. Existing role definitions are unchanged.

Submission body (replace the payment identifier with an eligible owned payment):

```json
{"id_paiement": 123, "numero_facture": "CH-2026-001", "date_facture": "2026-09-21", "montant": "3939.60"}
```

Decision bodies:

```json
{"statut": "CONFORME"}
```

```json
{"statut": "REJETEE", "motif_rejet": "Le montant ne correspond pas à la rémunération."}
```

## Persistence, concurrency and audit

Migration `016_facture_chasseur.sql` creates `real_estate.facture_chasseur` with
payment/hunter/verifier FKs, payment/version uniqueness, a partial unique index
for active invoices, positive amount/version checks and consistent
status/reviewer/date/reason checks. It adds no columns to existing tables and
does not modify migrations 001–015.

The API enforces cross-table ownership, amount, eligibility and lifecycle
rules. SQL constraints enforce row shape, references and uniqueness. Direct
privileged SQL writes are not equivalent to passing the API workflow.

Submission and review lock the payment first. Review then locks and refreshes
the invoice to avoid stale SQLAlchemy identity-map state after another review.
Uniqueness constraints provide a second defence against duplicate submissions.
The existing payment service accepts an internal `commit=False` option so the
invoice service owns the complete commit/rollback boundary. It is not exposed
as an HTTP option. Database concurrency is not proven by local mock tests.

Audit uses the existing `audit_log` service: `submit_facture_chasseur` INSERT
and `decide_facture_chasseur` UPDATE carry authenticated actor identity,
payment/version, expected amount and JSON snapshots. Existing payment
transition audit events are persisted in the same transaction. Rejection
reason and verifier/time remain on the invoice. Failure prevents partial
invoice/payment/audit commits.

## File organization

| Responsibility | Files |
| --- | --- |
| SQL schema / runtime assertions | `database/migrations/016_facture_chasseur.sql`, `database/tests/019_facture_chasseur.sql` |
| ORM / payloads | `src/api/db/models/facture_chasseur.py`, `src/api/schemas/facture_chasseur.py` |
| Queries / workflow | `src/api/repositories/facture_chasseur.py`, `src/api/services/facture_chasseur.py` |
| Payment integration | `src/api/repositories/paiement.py`, `src/api/services/paiement.py` |
| HTTP | `src/api/api/v1/endpoints/factures_chasseurs.py`, `src/api/api/v1/router.py` |
| CI configuration | `.gitlab-ci.yml`, `.gitlab/ci/database.yml`, `.gitlab/ci/database-hunter-invoice.yml` |
| CI database scripts | `scripts/ci/database/migrate-016.sh`, `test-facture-chasseur.sh`, `validate.sh` |
| Backend release / OpenAPI | `scripts/ci/backend/publish-gitops/check-invoice-schema.sh`, `scripts/ci/backend/validate/openapi-and-summary.sh` |
| Backend tests | `tests/backend/test_facture_chasseur_service.py`, `test_facture_chasseur_api.py`, `test_facture_chasseur_repository.py`, existing `test_paiement_service.py` |
| CI tests | `tests/ci/test_facture_chasseur_ci.py`, existing `tests/ci/test_pipeline.py` |
| Documentation | This document, `Readme.md`, repository/CI map, requirements/evidence matrix |

The small additional database component keeps existing YAML under 200 lines
and inherits `.database-operation`; existing job names, runner, manual controls
and resource lock remain stable. Script entrypoints remain sourced.

## Verification and owner handoff

Executed locally with the existing Python 3.12 review environment and test-only
settings, without infrastructure provisioning or runtime database access:

```sh
python -m pytest tests/backend tests/data tests/ai/test_candidate_availability.py --cov=src/api --cov-fail-under=80 -q
python -m pytest tests/ci tests/ai -q
git diff --check
```

Results: 583 passed / 3 existing opt-in database tests skipped; API coverage
86.22%. CI/AI: 1,554 passed. Local tests cover RBAC, scoped reads, invalid
submissions, rejected history, amount conformity, payment gating, transaction
failure paths, fresh locked reads, SQL query compilation and CI structure.
These are not PostgreSQL integration or runtime claims.

Owner execution order through the existing pipeline:

1. Commit/push and inspect validation jobs.
2. Run manual `database:migrate-016` after migration 015. The wrapper safely
   skips an already registered 016; the SQL migration itself rejects replay.
3. Run manual `database:test-facture-chasseur`. SQL test 019 verifies actual
   PostgreSQL constraints and version coexistence using fresh transactional
   fixtures. It requires an existing hunter mandate and ADMIN identity and
   rolls back business mutations; identity sequences may advance.
4. Continue backend image/GitOps publication. The read-only release guard
   requires migrations 015/016 and both invoice tables. It does not prove SQL
   test success or execute migrations. Inspect both test jobs before release.
5. After Argo CD sync, use a new eligible payment to verify own-hunter
   submission, cross-owner denial, duplicate conflict, rejection/correction,
   conforming acceptance and atomic `PROGRAMME` progression. Verify direct
   payment advancement without an invoice fails, then record `PAYE` through
   the existing endpoint with a valid date. Inspect invoice, payment and audit
   persistence, including after a rejected amount and repeated decision.

NOT DEPLOYED BY CODEX.
Deployment must proceed through GitLab CI → Registry → lab-gitops → Argo CD → Kubernetes.

Runtime verification: NOT CLAIMED.
Runtime verification must be performed after GitLab/GitOps deployment.
