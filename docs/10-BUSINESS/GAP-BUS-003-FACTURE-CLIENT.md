# GAP-BUS-003 — Facture client

**Status: implemented and locally verified; GitLab/GitOps/lab verification pending.**
Date: 2026-09-20. The user will commit, push and perform live checks.
This gap is **not closed** until the deployment and runtime checklist below is complete.

## Business requirement and source

**STARTERPACK REQUIREMENT:** the buyer pays company fees separately from the
purchase price; the notary collects/secures those fees. The client receives an
invoice after the authentic deed and fee payment. Fees use `H = F + t × P`,
with parameters effective on the authentic-deed date. Hunter invoicing is a
later, distinct workflow.

Reference supplied for this implementation:
`DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack`, baseline
`902207e3c72fe5c806f639020e00558d0f592a26`. The supplied business requirements
are the source for this increment; no new StarterPack interpretation or tax
requirement has been inferred.

## Project design decisions

- Migration [015](../../database/migrations/015_facture_client.sql) is retained
  as supplied: one immutable invoice per sale, no VAT fields, credit notes,
  payment-status lifecycle or invented historical invoices.
- `numero_facture = FC-{id_vente padded to at least 10 digits}`. It is stable,
  readable, server-generated and unique. It is a project identifier, not a
  claim about legally prescribed chronological accounting numbering.
- `date_emission` is the server's current UTC date. A future authentic deed or
  future fee-reception date cannot justify issuance.
- The field name `montant_honoraires_ht` follows migration 015. No tax engine,
  VAT configuration or claim of a legally complete invoice document is added.
- Only ADMIN issues invoices, consistent with financial lifecycle mutation.
  CLIENT and CHASSEUR receive scoped read access; SERVICE has no invoice access.
- Fee receipt is evidenced by the existing `paiement` row for the sale, in
  `RECU`, `VERIFIE`, `PROGRAMME` or `PAYE`, with a receipt date between the deed
  and issuance. The receipt, purchase, mandate, configuration and fee amount
  must agree with the sale and deed-effective calculation.

### Necessary payment compatibility change

Previously, a payment without hunter remuneration entitlement could only be
cancelled, preventing receipt recording for otherwise invoiceable sales.
`PaiementService` now permits `ATTENDU -> RECU` for those sales. It continues
to reject their `VERIFIE`, `PROGRAMME` and `PAYE` transitions. Receipt dates,
ADMIN authorization, row locking and audit behavior remain in the existing
payment service. This does not pay a hunter or implement GAP-BUS-004.

## Architecture and physical model

```text
POST /api/v1/factures-clients {id_vente}
  -> existing authentication / ADMIN role
  -> FactureClientCreate (extra fields forbidden)
  -> FactureClientService
  -> FactureClientRepository: lock Vente + Mandat, then Paiement
  -> ParametresHonorairesRepository.get_effective(deed_date)
  -> existing calculate_company_fees() using Decimal and HALF_UP cents
  -> insert FactureClient + AuditLog in one transaction
```

Files follow the existing five backend layers, all named `facture_client.py`
under `src/api/db/models`, `repositories`, `schemas` and `services`, with the
HTTP module `src/api/api/v1/endpoints/factures_clients.py`. The production
router imports/registers the endpoint and model through existing imports.

`real_estate.facture_client` contains:

| Fields | Role |
| --- | --- |
| `id_facture_client` | BIGINT identity primary key |
| `id_vente`, `id_client`, `id_parametres_honoraires` | RESTRICT foreign keys |
| `numero_facture`, `date_emission` | Unique business reference and issuance date |
| `montant_achat`, `montant_honoraires_ht` | NUMERIC(14,2) snapshots |
| `montant_fixe_applique` | NUMERIC(12,2) snapshot |
| `taux_pourcentage_applique` | NUMERIC(7,4) snapshot |
| `date_creation` | TIMESTAMPTZ default CURRENT_TIMESTAMP |

The DB enforces unique sale/number, nonempty numbers and individual financial
bounds. The application enforces derived ownership, receipt eligibility and
calculation consistency. Migration 015's ownership query is a one-time
validation, **not** a trigger enforcing lineage on future direct SQL writes.
Immutability is enforced by the API surface; direct privileged SQL writes
remain outside that protection. No applied migration 001–014 was edited.

## API and access control

| Route | ADMIN | CLIENT | CHASSEUR | SERVICE |
| --- | --- | --- | --- | --- |
| `POST /api/v1/factures-clients` | Issue | 403 | 403 | 403 |
| `GET /api/v1/factures-clients` | All | Own only | Beneficiary only | 403 |
| `GET /api/v1/factures-clients/{invoice_id}` | Read | Own only | Beneficiary only | 403 |

POST accepts only `{"id_vente": 123}`. It does not accept client identity,
invoice number, dates, fees or purchase amounts. Successful issuance returns
201; missing sale/invoice returns 404; duplicate sale/number returns 409;
invalid eligibility/input returns 422; missing authentication returns 401.
There is no PUT, PATCH, DELETE or invoice cancellation endpoint.

Client access uses `facture_client -> vente -> mandat.id_client`, never a
query/body identity or the denormalized invoice owner alone. Hunter access
uses `vente.id_chasseur_beneficiaire`, matching completed-sale read rules.
Missing business identity returns 403. Foreign and nonexistent invoices use
the identical 404 response `Resource not found`; lists filter in SQL.

## Audit and concurrent issuance

The existing `real_estate.audit_log` receives one INSERT event with action
`ISSUE_FACTURE_CLIENT`, actor email and authenticated user ID, invoice snapshot,
sale/mandate/payment IDs, deed date and receipt date. Decimal values are JSON
strings. No JWT or credential is recorded.

Sale/mandate and payment row locks protect issuance inputs. The database
UNIQUE constraints remain the final duplicate safeguard. Named unique
violations become 409, other integrity failures become 422, and failures
before commit roll back both invoice and audit. Fees are stored on the
invoice, so later parameter edits cannot change historical amounts.

## Local verification

- Backend/data/candidate regression: 513 tests passed, API coverage above 80%.
- Full AI and offline CI suites: 1,502 tests passed.
- Invoice service/API tests cover derived identity, date-effective parameter
  lookup, HALF_UP rounding, snapshot stability, overflow, missing prerequisites,
  role/ownership enforcement, forged fields, duplicates and rollback/audit.
- PostgreSQL 16: actual migration 015 and SQL test 018 executed successfully
  after unchanged OLTP prerequisite migrations and the supplied legacy fixture.
  Test 018 verified columns, constraints, indexes, rejected mutations and
  configuration-independent snapshots; invoice/sale counts were zero after
  its final ROLLBACK. Identity sequences may advance during rolled-back tests.
- Opt-in PostgreSQL API tests exercise real repositories, services and audit
  writes, own/foreign reads, receipt without hunter entitlement, duplicate
  rejection and a real UNIQUE violation after a simulated stale pre-check.
  Authentication is overridden with test identities in these integration tests;
  this does not prove live JWT provisioning or production authorization state.
- The model's columns/types/nullability match the migrated PostgreSQL table.
- Full-tree `git diff --check` reports pre-existing whitespace in the user's
  requirements matrix and historical MLD edits. New implementation files are
  checked separately; those unrelated edits are preserved.

Run normal checks using the repository map. To include the PostgreSQL tests,
set `FACTURE_TEST_DATABASE_URL` to an **isolated local** PostgreSQL database
named `gap003_*`, migrated through 015 and containing a mandate/configuration
fixture, then run `tests/backend/test_facture_client_repository.py`. Use the
project's `postgresql+psycopg` driver. The tests roll back their outer transaction
even when services commit. Without that variable, three local-DB tests skip.

## CI and deployment handoff

- Existing `.database-operation` template, runner, resource lock and manual
  controls are reused by `database:migrate-015` and `database:test-facture-client`.
- The migration script requires version 014, skips a registered 015 and sources
  the exact migration file. Test 018 runs via the existing kubectl/psql pattern.
- Backend regression automatically discovers the new tests. OpenAPI validation
  requires both invoice paths. Offline CI executes the release guard with
  stubbed kubectl success/missing-schema/command-failure cases.
- `backend:publish-gitops` checks migration 015 registration and table presence
  **before** credentials or GitOps writes. If absent, it fails with instructions
  to run the two manual DB jobs and retry. It never applies migrations itself.
- Component YAML remains below 200 lines and shell files below 250 lines.

User-owned live verification order:

1. Commit/push the scoped changes, including the previously untracked migration
   015 and updated test 018. Review existing unrelated documentation edits separately.
2. Verify pipeline, backend, data and AI validation jobs are green.
3. Run `database:migrate-015`, then `database:test-facture-client`; inspect their
   successful logs and migration registry/table evidence.
4. Verify the backend image build; retry GitOps publication if its schema guard
   failed before step 3. Publication remains source -> CI -> registry -> lab-gitops.
5. Verify the resulting GitOps revision/image digest, Argo CD Synced/Healthy and
   backend pod Running/Ready. Do not substitute permanent `kubectl apply`.
6. Use a controlled sale and existing payment calculation/receipt workflow.
   Issue as ADMIN, verify the returned owner and deed-effective Decimal amount,
   then repeat to obtain 409. Verify CLIENT own read and foreign 404, hunter
   beneficiary read/foreign 404 where applicable, and corresponding audit entry.
7. Record sanitized pipeline/job IDs, image/GitOps revisions, Argo/pod evidence,
   business IDs, HTTP results and audit IDs here. Never include tokens or secrets.

**Pending:** live GitLab CI, registry build, GitOps publication, Argo/pod health,
lab migration 015, live API/JWT scenario and live audit evidence. These have not
been performed by this implementation session. No commit or push was made.

## Boundaries

GAP-BUS-004 hunter invoicing and GAP-BUS-006 accepted-offer transaction identity
remain separate. There is no migration 016 or `vente.id_offre` change. Financial
configuration edits that disagree with an already received payment cause invoice
issuance to fail closed; reconciling that inconsistency remains an administrative
task. Credit notes, refunds, billing-address completion, invoice document rendering,
tax compliance and a general ledger are outside this increment.
