# GAP-BUS-002 — Offre Workflow

**Project:** Enterprise Real Estate Intelligence Platform  
**Application:** Real Estate Intelligence Platform  
**Gap:** GAP-BUS-002  
**Domain:** Commercial Offer / Offre  
**Status:** CLOSED — RUNTIME VERIFIED WITH RBAC QUALIFICATION  
**Migration:** 014 — `014_offre_workflow.sql`  
**Database Test:** 017 — `017_offre_workflow.sql`  
**Last Updated:** 2026-09-20

---

# 1. Purpose

This document records the complete analysis, design, implementation, testing, CI validation, deployment and runtime evidence for:

```text
GAP-BUS-002 — Offre workflow
```

The objective was to introduce the missing commercial-offer lifecycle between property presentation activity and the final property sale.

Before this implementation, the platform supported the surrounding business domains but did not persist the commercial negotiation itself.

The business chain contained a gap:

```text
CLIENT
  |
  v
DEMANDE
  |
  v
AFFECTATION CHASSEUR
  |
  v
DEMANDE_VERSION
  |
  v
MANDAT
  |
  v
MATCHING
  |
  v
PRESENTATION
  |
  +------> VISITE
  |
  X
  |
OFFRE
  |
  X
  |
ACCEPTATION / REFUS / REVISION
  |
  v
VENTE
```

After GAP-BUS-002, the platform can represent the commercial-offer lifecycle explicitly:

```text
CLIENT
  |
  v
DEMANDE
  |
  v
AFFECTATION CHASSEUR
  |
  v
DEMANDE_VERSION
  |
  v
MANDAT
  |
  v
MATCHING
  |
  v
PRESENTATION
  |
  +------> VISITE
  |
  v
OFFRE
  |
  +------> REFUSEE
  |
  +------> RETIREE
  |
  +------> EXPIREE
  |
  +------> REVISEE
  |           |
  |           v
  |      NEW OFFER VERSION
  |
  +------> ACCEPTEE
               |
               v
             VENTE
               |
               v
       ACTE AUTHENTIQUE
               |
               v
     HONORAIRES / REMUNERATION
               |
               v
            PAIEMENT
```

---

# 2. Original Business Gap

At the beginning of GAP-BUS-002, no implemented `Offre` business domain existed.

The platform already represented:

```text
Presentation
Visite
Vente
```

but the commercial negotiation between these stages was missing.

Consequently, the information system could not persistently answer questions such as:

```text
Which presentation produced an offer?
What amount was proposed?
When was the offer submitted?
Was the offer accepted or refused?
Was the offer withdrawn?
Did the offer expire?
Was the amount revised?
What was the previous amount?
How many commercial versions existed?
Which version was finally accepted?
Who recorded the commercial decision?
Was the negotiation history preserved?
```

The initial state was therefore classified as:

```text
GAP-BUS-002
Offre workflow
STATUS: MISSING
```

This was a genuine missing business capability rather than a partially implemented feature.

---

# 3. Requirement Analysis

The Offre domain was analyzed before implementation.

The implementation deliberately avoided introducing an underspecified table such as:

```text
offre(
    id,
    montant,
    statut
)
```

because such a model would not provide sufficient lineage, historical integrity or lifecycle control.

The investigation considered the existing:

```text
Presentation model
Visite model
Vente model
Demande ownership model
DemandeAffectation model
RBAC implementation
Audit architecture
PostgreSQL conventions
FastAPI service architecture
GitLab CI architecture
GitOps deployment model
```

The design had to preserve the ability to establish the upstream business context of an offer through existing relationships rather than duplicating identities unnecessarily.

---

# 4. Domain Design Decisions

The final design uses `Presentation` as the direct business parent of an offer.

```text
Presentation 1 --------< N Offre
Presentation 1 --------< N Visite
```

An Offre is therefore associated with the property and search context already represented by its Presentation.

The lineage is:

```text
OFFRE
  |
  v
PRESENTATION
  |
  +------> BIEN
  |
  v
DEMANDE_VERSION
  |
  v
DEMANDE
  |
  +------> CLIENT
  |
  +------> DEMANDE_AFFECTATION
                |
                v
             CHASSEUR
```

This avoids duplicating client, property, demande or hunter identifiers inside `offre`.

---

# 5. Offre and Visite Relationship

No direct foreign key was introduced between `Offre` and `Visite`.

The implemented model is:

```text
             PRESENTATION
              /        \
             /          \
            v            v
         VISITE        OFFRE
```

rather than:

```text
VISITE -> OFFRE
```

A commercial offer belongs to the presented property/search context.

A visit may occur as part of that commercial process, but the database does not require every offer to reference one specific visit.

This prevents an unnecessary structural dependency that was not justified by the implemented business requirement.

---

# 6. Offre and Vente Relationship

Migration 014 does not add:

```text
vente.id_offre
```

The existing Vente model remains unchanged.

Offer and sale lineage can currently be reconstructed through the common Presentation business context.

The implemented change therefore closes the missing Offre lifecycle without rewriting the already validated Vente model.

A future requirement may introduce stronger explicit transaction identity if justified by the transaction-consistency backlog, but that is outside GAP-BUS-002.

---

# 7. Versioning Strategy

Each row in `real_estate.offre` represents one immutable commercial proposal version with respect to its amount and proposal identity.

Revision does not overwrite the original proposal amount.

Instead:

```text
Offer v1
  |
  | revision
  v
v1 -> REVISEE

and

v2 -> SOUMISE
```

This preserves commercial history.

Example:

```text
Version 1
250000.00 EUR
SOUMISE
    |
    | revision
    v
REVISEE

Version 2
245000.00 EUR
SOUMISE
    |
    | decision
    v
ACCEPTEE
```

The historical amount of version 1 remains available after version 2 is created.

---

# 8. Offre Lifecycle

Supported statuses are:

```text
SOUMISE
ACCEPTEE
REFUSEE
RETIREE
EXPIREE
REVISEE
```

The principal lifecycle is:

```text
                    +--> ACCEPTEE
                    |
                    +--> REFUSEE
                    |
SOUMISE ------------+--> RETIREE
                    |
                    +--> EXPIREE
                    |
                    +--> REVISEE
                            |
                            v
                     new SOUMISE version
```

`REVISEE` is a historical terminal state for the superseded version.

The new proposal receives the next `numero_version`.

---

# 9. Human Decisions and Expiration

The explicit decision API supports commercial decisions represented by the application contract.

`EXPIREE` is not treated as a human `OffreDecision`.

No scheduler, background expiration engine or additional orchestration technology was invented as part of this gap.

Automatic expiration may be implemented later if a concrete requirement requires it.

---

# 10. PostgreSQL Table

Migration 014 introduces:

```text
real_estate.offre
```

The deployed structure contains:

```text
id_offre        BIGINT GENERATED ALWAYS AS IDENTITY
id_presentation BIGINT NOT NULL
numero_version  INTEGER NOT NULL
montant         NUMERIC(14,2) NOT NULL
date_offre      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
date_expiration TIMESTAMPTZ NULL
date_decision   TIMESTAMPTZ NULL
statut          VARCHAR(20) NOT NULL DEFAULT 'SOUMISE'
commentaire     TEXT NULL
date_creation   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
```

---

# 11. Relational Integrity

The Offre table is protected by a foreign key:

```text
offre.id_presentation
    ->
presentation.id_presentation
```

with:

```text
ON DELETE RESTRICT
```

This prevents deletion of a Presentation that is already referenced by commercial history.

---

# 12. Version Uniqueness

The following uniqueness rule is enforced:

```text
UNIQUE (
    id_presentation,
    numero_version
)
```

A Presentation cannot contain two Offre rows with the same version number.

This provides deterministic commercial version history.

---

# 13. Accepted-Offer Uniqueness

A partial unique index exists:

```text
uq_offre_presentation_acceptee
```

with the semantic rule:

```text
At most one ACCEPTEE offer per Presentation
```

This prevents two versions for the same Presentation from simultaneously representing the accepted commercial outcome.

The existence of this partial unique index was verified directly against the deployed PostgreSQL schema.

---

# 14. Database Check Constraints

The deployed table contains checks for:

```text
numero_version > 0
montant > 0
valid status values
expiration consistency
decision-date consistency
```

The expiration invariant is:

```text
date_expiration IS NULL
OR
date_expiration > date_offre
```

The decision invariant distinguishes pending/expiration states from explicit decision states.

Conceptually:

```text
SOUMISE
EXPIREE
    ->
date_decision IS NULL
```

and:

```text
ACCEPTEE
REFUSEE
RETIREE
REVISEE
    ->
date_decision IS NOT NULL
```

This prevents inconsistent lifecycle states from being persisted.

---

# 15. Database Indexes

Runtime inspection confirmed indexes supporting:

```text
primary key
presentation lookup
status lookup
offer-date lookup
version uniqueness
accepted-offer uniqueness
```

Observed deployed indexes include:

```text
pk_offre
idx_offre_date_offre
idx_offre_presentation
idx_offre_statut
uq_offre_presentation_acceptee
uq_offre_presentation_version
```

---

# 16. Migration 014

The database change is implemented by:

```text
database/migrations/014_offre_workflow.sql
```

Migration 014 creates the versioned Offre workflow and its relational integrity rules.

It follows the project rule that already applied migrations are immutable.

At the runtime validation checkpoint, migration control reported:

```text
014 | Add versioned commercial offer workflow
```

with application timestamp:

```text
2026-09-20 16:43:20.88955+00
```

The relation lookup confirmed:

```text
to_regclass('real_estate.offre')
=
real_estate.offre
```

Migration 014 is therefore:

```text
IMPLEMENTED
CI VALIDATED
DEPLOYED
RUNTIME VERIFIED
```

---

# 17. Dedicated Database Test

The dedicated database validation file is:

```text
database/tests/017_offre_workflow.sql
```

CI wiring was implemented for the Offre database workflow.

A later attempt to execute this repository file directly from `k8s-cp-01` did not run because the source repository file was not present on the control-plane filesystem.

The shell failed before `kubectl` or `psql` consumed the SQL file.

Therefore this document does not claim that test 017 was independently executed from the Kubernetes control plane.

Runtime database evidence instead comes from:

```text
migration_control
live table inspection
live constraints
live indexes
live API persistence
live audit records
```

This distinction is intentional and preserves evidence accuracy.

---

# 18. Database CI Integration

The database CI workflow was extended with:

```text
scripts/ci/database/migrate-014.sh
scripts/ci/database/test-offre-workflow.sh
```

and corresponding jobs in:

```text
.gitlab/ci/database.yml
```

for:

```text
database:migrate-014
database:test-offre-workflow
```

The CI structure continued to respect the repository's sourced-script architecture.

The structural CI expectation count was updated accordingly.

---

# 19. Application Implementation

The Offre domain was implemented through the existing application layering.

Implemented files include:

```text
src/api/db/models/offre.py
src/api/repositories/offre.py
src/api/schemas/offre.py
src/api/services/offre.py
src/api/api/v1/endpoints/offres.py
```

and registration in:

```text
src/api/api/v1/router.py
```

The implementation follows:

```text
HTTP
  |
  v
FastAPI endpoint
  |
  v
Pydantic schema
  |
  v
OffreService
  |
  v
OffreRepository
  |
  v
SQLAlchemy
  |
  v
PostgreSQL
```

---

# 20. ORM Model

The SQLAlchemy Offre model maps the new PostgreSQL relation into the application domain.

It represents:

```text
identity
presentation relationship
commercial version
amount
offer timestamp
optional expiration
decision timestamp
status
comment
creation timestamp
```

Database constraints remain the authoritative persistence guard while the application layer provides earlier business validation.

---

# 21. Repository Layer

The Offre repository encapsulates persistence operations required by the service.

The repository supports the service without moving authorization decisions into raw persistence code.

This preserves separation of concerns:

```text
Repository
    ->
data access

Service
    ->
business lifecycle
authorization context
audit orchestration
```

---

# 22. API Schemas

The Pydantic schemas define contracts for:

```text
offer creation
offer representation
offer decision
offer revision
```

Validation is performed before invalid payloads reach persistence logic.

The API contract exposes the business lifecycle rather than requiring clients to manipulate database rows directly.

---

# 23. Service Layer

`OffreService` coordinates:

```text
Presentation resolution
authorization
version allocation
offer creation
decision transitions
revision behavior
audit events
persistence
```

The service layer is the primary application-level location for the Offre business rules.

---

# 24. FastAPI Endpoints

The deployed OpenAPI specification exposes five Offre operations:

```text
GET, POST  /api/v1/offres
GET        /api/v1/offres/{offre_id}
POST       /api/v1/offres/{offre_id}/decision
POST       /api/v1/offres/{offre_id}/revisions
```

This provides:

```text
list
create
retrieve
decide
revise
```

without exposing arbitrary status mutation.

All five operations were observed in the OpenAPI contract of the deployed backend.

---

# 25. Authorization Model

The implemented Offre API is restricted to:

```text
ADMIN
CHASSEUR
```

It is not exposed to:

```text
CLIENT
SERVICE
```

for the implemented workflow.

No unsupported `MANAGER`, seller or property-owner role was invented.

The platform roles remain:

```text
ADMIN
CHASSEUR
CLIENT
SERVICE
```

---

# 26. Chasseur Ownership Lineage

A CHASSEUR does not gain access merely because an `id_offre` is known.

Authorization follows business lineage:

```text
OFFRE
  |
  v
PRESENTATION
  |
  v
DEMANDE_VERSION
  |
  v
DEMANDE
  |
  v
DEMANDE_AFFECTATION
  |
  v
CHASSEUR
```

The existing demande-access enforcement is reused rather than introducing a second, inconsistent ownership mechanism.

This reduces IDOR/cross-owner access risk.

---

# 27. ADMIN Authorization

ADMIN may operate on the Offre workflow according to the existing administrative authorization model.

Runtime lifecycle validation was executed with an authenticated ADMIN test identity.

No authentication token, JWT secret or credential is included in this documentation.

---

# 28. CHASSEUR Runtime Qualification

Automated tests validate:

```text
CHASSEUR own-resource access
CHASSEUR cross-owner concealment
```

However, direct runtime verification of those two CHASSEUR scenarios was not completed.

The deployed dataset contained one active authenticated test CHASSEUR mapped to:

```text
id_chasseur = 1
```

but its owned active demandes did not have an existing suitable Presentation.

A read-only search across the owned demandes and available Biens returned:

```text
0 rows
```

for the basic compatibility criteria used to locate a legitimate runtime candidate.

The project deliberately did not fabricate an unrealistic property/presentation relationship solely to manufacture runtime evidence.

The existing CHASSEUR credential was also not recovered from shell history, and the account was not reset merely for evidence generation.

Therefore the correct evidence state is:

```text
CHASSEUR own-resource RBAC
    TESTED — automated

CHASSEUR cross-owner concealment
    TESTED — automated

Direct CHASSEUR runtime E2E
    NOT VERIFIED
```

This qualification does not invalidate the deployed Offre workflow, but it must remain explicit.

---

# 29. Cross-Owner Concealment

Automated ownership API tests cover cross-owner behavior.

The expected security behavior is resource concealment rather than revealing another hunter's business resource.

The corresponding behavior is covered by the Offre ownership API test suite.

Direct production-like runtime execution with a CHASSEUR token remains outside the collected runtime evidence for the reason documented above.

---

# 30. Audit Architecture

No new audit table was created.

The implementation reuses:

```text
real_estate.audit_log
```

No unnecessary parallel audit architecture was introduced.

OffreService records explicit business audit events for the Offre lifecycle.

This follows the platform principle that audit claims must correspond to implemented behavior rather than assuming every table is automatically audited.

---

# 31. Audited Offre Actions

The implemented audit context distinguishes actions including:

```text
create_offre
revise_offre
decide_offre
```

Audit records preserve relevant context such as:

```text
source
presentation
version
previous/new offer relationship
from status
to status
authenticated actor
```

The runtime audit trail was inspected after controlled API operations.

---

# 32. Automated Tests

Dedicated backend tests were implemented:

```text
tests/backend/test_offre_service.py
tests/backend/test_offre_ownership_api.py
tests/backend/test_offre_api.py
tests/backend/test_offre_audit.py
```

Results:

```text
Offre service tests          23 passed
Offre ownership API tests    12 passed
Offre HTTP API tests         12 passed
Offre audit tests            10 passed
--------------------------------------
Targeted Offre total         57 passed
```

---

# 33. CI Structural Tests

Repository CI structural validation passed:

```text
1365 passed
```

This includes validation of the CI architecture after adding the two Offre database operations.

---

# 34. Full Regression

The full backend/data regression command completed successfully with:

```text
445 passed
```

The coverage command used the repository gate:

```text
--cov-fail-under=80
```

and the gate passed.

The Offre implementation therefore did not regress the validated backend/data behavior covered by that suite.

---

# 35. Git Validation

The implementation was committed with:

```text
feat: implement versioned offer workflow
```

and pushed to GitLab.

The user-observed GitLab pipeline completed green.

The implementation then proceeded through the normal project delivery path rather than using direct permanent Kubernetes mutation.

---

# 36. Delivery Path

The deployment followed the platform's expected GitOps chain:

```text
Source repository
      |
      v
GitLab CI
      |
      v
Container Registry
      |
      v
lab-gitops
      |
      v
Argo CD
      |
      v
Kubernetes
```

This preserves the project's deployment architecture and auditability.

---

# 37. Deployed Backend Image

Runtime inspection confirmed the Offre implementation in backend image:

```text
gitlab.local:4567/root/chasse_immobiliere/backend:3c993cce
```

The deployed application exposed the new Offre routes through its live OpenAPI specification.

---

# 38. Argo CD State

At the deployment/runtime validation checkpoint, the Real Estate applications were observed as synchronized and healthy, including the relevant backend and PostgreSQL applications.

The deployment remained managed through the expected GitOps control plane.

No direct `kubectl apply` deployment was used as the permanent delivery mechanism.

---

# 39. Kubernetes Health

Final runtime health inspection showed:

```text
deployment.apps/real-estate-backend
READY       1/1
UP-TO-DATE  1
AVAILABLE   1

deployment.apps/real-estate-postgresql
READY       1/1
UP-TO-DATE  1
AVAILABLE   1
```

The backend pod was:

```text
1/1 Running
0 restarts
```

and PostgreSQL was:

```text
1/1 Running
0 restarts
```

Recent matching and backup Jobs shown during the inspection were in:

```text
Completed
```

state.

No failing Real Estate workload appeared in the final runtime output.

---

# 40. Runtime Validation Strategy

Runtime validation used a controlled ADMIN scenario against an existing Presentation.

The selected Presentation was:

```text
id_presentation       32
id_bien               16025
id_demande_version    137
presentation_statut   IDENTIFIE
id_demande            17
id_client             18
id_chasseur           2
affectation_statut    ACCEPTEE
existing offers       0
```

This Presentation provided a clean starting point for the Offre lifecycle.

The created Offre records are controlled E2E validation data and must not be represented as genuine historical customer negotiations.

---

# 41. Runtime Scenario A — Create Offre

The deployed FastAPI application was used.

Request:

```http
POST /api/v1/offres
```

Relevant payload:

```json
{
  "id_presentation": 32,
  "montant": 250000.00,
  "commentaire": "Runtime verification GAP-BUS-002"
}
```

Result:

```text
HTTP 201
```

Created offer:

```text
id_offre        13
id_presentation 32
numero_version  1
montant         250000.00
statut          SOUMISE
date_decision   NULL
```

This proves that the deployed API can create and persist a versioned commercial offer.

---

# 42. Runtime Persistence — Version 1

PostgreSQL confirmed persistence of Offre 13.

The initial commercial state was:

```text
Offre 13
Presentation 32
Version 1
250000.00 EUR
SOUMISE
```

This established the initial offer state before revision.

---

# 43. Runtime Audit — Creation

The corresponding audit event was persisted in:

```text
real_estate.audit_log
```

Observed audit record:

```text
record_id   13
operation   INSERT
actor       admin.auth.test@example.com
```

Relevant context included:

```json
{
  "action": "create_offre",
  "source": "api",
  "numero_version": 1,
  "id_presentation": 32
}
```

This proves that Offre creation is attributable to the authenticated runtime actor.

---

# 44. Runtime Scenario B — Revision

Offre 13 was revised through the deployed API.

Request:

```http
POST /api/v1/offres/13/revisions
```

Payload:

```json
{
  "montant": 245000.00,
  "commentaire": "Runtime revision GAP-BUS-002"
}
```

Result:

```text
HTTP 201
```

New offer:

```text
id_offre        14
id_presentation 32
numero_version  2
montant         245000.00
statut          SOUMISE
```

The original row was not overwritten.

---

# 45. Runtime Historical Preservation

PostgreSQL showed both commercial versions:

```text
Offre 13
--------
Presentation 32
Version      1
Amount       250000.00
Status       REVISEE
Decision     populated

Offre 14
--------
Presentation 32
Version      2
Amount       245000.00
Status       SOUMISE
Decision     NULL
```

This is direct runtime evidence that revision preserves the previous amount and creates a new version.

The history is therefore:

```text
250000 EUR
SOUMISE
   |
   | revise
   v
250000 EUR
REVISEE
   |
   +----------------------+
                          |
                          v
                    245000 EUR
                    SOUMISE
```

---

# 46. Runtime Audit — Revision

Two audit events represented the revision operation.

The original Offre received an UPDATE event:

```text
Offre 13
SOUMISE -> REVISEE
```

with context including:

```text
action              revise_offre
new_offre_id        14
new_numero_version  2
```

The new Offre received an INSERT event:

```text
Offre 14
Version 2
SOUMISE
```

with context including:

```text
action              revise_offre
previous_offre_id   13
```

Both were attributed to the authenticated ADMIN actor.

This provides explicit audit lineage between commercial versions.

---

# 47. Runtime Scenario C — Acceptance

The second offer version was accepted through the deployed API.

Request:

```http
POST /api/v1/offres/14/decision
```

Payload:

```json
{
  "statut": "ACCEPTEE",
  "commentaire": "Runtime acceptance GAP-BUS-002"
}
```

Result:

```text
HTTP 200
```

Final response state:

```text
id_offre        14
numero_version  2
montant         245000.00
statut          ACCEPTEE
date_decision   2026-09-20T16:56:13.274416Z
```

This proves the deployed API can execute a commercial decision transition.

---

# 48. Final PostgreSQL Runtime State

Final database inspection showed:

```text
id_offre | version | montant   | statut
---------+---------+-----------+----------
13       | 1       | 250000.00 | REVISEE
14       | 2       | 245000.00 | ACCEPTEE
```

Decision timestamps were populated consistently for both historical decision states.

The final commercial sequence is therefore:

```text
Presentation 32
      |
      v
Offre 13
Version 1
250000 EUR
SOUMISE
      |
      | revise
      v
REVISEE
      |
      v
Offre 14
Version 2
245000 EUR
SOUMISE
      |
      | accept
      v
ACCEPTEE
```

---

# 49. Runtime Audit — Acceptance

The acceptance produced an UPDATE audit event for Offre 14.

Observed transition:

```text
SOUMISE
   ->
ACCEPTEE
```

Relevant context included:

```json
{
  "action": "decide_offre",
  "source": "api",
  "to_status": "ACCEPTEE",
  "from_status": "SOUMISE",
  "numero_version": 2,
  "id_presentation": 32
}
```

The event was attributed to the authenticated ADMIN runtime identity.

---

# 50. Runtime Audit Sequence

The complete controlled Offre audit sequence included:

```text
Audit 30
INSERT Offre 13
create_offre

Audit 31
UPDATE Offre 13
SOUMISE -> REVISEE

Audit 32
INSERT Offre 14
revision successor

Audit 33
UPDATE Offre 14
SOUMISE -> ACCEPTEE
```

This demonstrates audit continuity across creation, revision and decision.

---

# 51. Accepted-Offer Constraint Runtime Evidence

The deployed PostgreSQL schema was inspected directly.

The partial unique index:

```text
uq_offre_presentation_acceptee
```

was present with the accepted-offer predicate.

A second accepted offer was deliberately not manufactured in the runtime database merely to force a constraint violation.

The constraint behavior is covered by the dedicated database/test implementation, while runtime evidence confirms that the protection is deployed physically.

This avoids unnecessary mutation of controlled business data.

---

# 52. Controlled Runtime Data

The following records were deliberately used or created during GAP-BUS-002 runtime validation:

```text
Presentation 32
```

and:

```text
Offre 13
Version 1
250000.00
REVISEE
```

and:

```text
Offre 14
Version 2
245000.00
ACCEPTEE
```

These must be described as:

> controlled E2E validation records

and not as genuine customer commercial transactions.

Their retention or cleanup should follow the project's evidence/data-fixture policy.

---

# 53. Complete Validation Chain

GAP-BUS-002 was validated through the following engineering chain:

```text
Business requirement
        |
        v
Existing-domain investigation
        |
        v
Domain modeling
        |
        v
Migration 014
        |
        v
PostgreSQL constraints / indexes
        |
        v
ORM
        |
        v
Repository
        |
        v
Pydantic schemas
        |
        v
OffreService
        |
        v
RBAC / ownership lineage
        |
        v
Audit integration
        |
        v
FastAPI endpoints
        |
        v
Targeted tests
        |
        v
Full regression
        |
        v
CI structural validation
        |
        v
GitLab pipeline
        |
        v
Container image
        |
        v
lab-gitops
        |
        v
Argo CD
        |
        v
Kubernetes
        |
        v
Migration runtime inspection
        |
        v
Live OpenAPI
        |
        v
ADMIN API E2E
        |
        v
PostgreSQL persistence
        |
        v
Audit verification
        |
        v
Final Kubernetes health
```

---

# 54. Implementation Status

| Component | Status |
| --- | --- |
| Business requirement analyzed | VERIFIED |
| Existing domain inspected before design | VERIFIED |
| Offre domain model | IMPLEMENTED |
| Migration 014 | DEPLOYED |
| `real_estate.offre` | RUNTIME VERIFIED |
| Presentation FK | RUNTIME VERIFIED |
| Version uniqueness | RUNTIME VERIFIED |
| Accepted-offer partial unique index | RUNTIME VERIFIED |
| Check constraints | RUNTIME VERIFIED |
| ORM | IMPLEMENTED / DEPLOYED |
| Repository | IMPLEMENTED / DEPLOYED |
| API schemas | IMPLEMENTED / DEPLOYED |
| OffreService | IMPLEMENTED / DEPLOYED |
| Router registration | RUNTIME VERIFIED |
| Five API operations | RUNTIME VERIFIED |
| Audit integration | RUNTIME VERIFIED |
| ADMIN create | RUNTIME VERIFIED |
| ADMIN revision | RUNTIME VERIFIED |
| ADMIN acceptance | RUNTIME VERIFIED |
| Historical version preservation | RUNTIME VERIFIED |
| PostgreSQL persistence | RUNTIME VERIFIED |
| CHASSEUR own-resource authorization | TESTED — AUTOMATED |
| CHASSEUR cross-owner concealment | TESTED — AUTOMATED |
| Direct CHASSEUR runtime E2E | NOT VERIFIED |
| Offre service tests | 23 PASSED |
| Offre ownership API tests | 12 PASSED |
| Offre HTTP API tests | 12 PASSED |
| Offre audit tests | 10 PASSED |
| Targeted Offre suite | 57 PASSED |
| CI structural tests | 1365 PASSED |
| Full backend/data regression | 445 PASSED |
| Coverage gate >= 80% | PASSED |
| GitLab pipeline | PASSED |
| GitOps deployment | VERIFIED |
| Backend image | DEPLOYED |
| PostgreSQL migration 014 | APPLIED |
| Final Kubernetes health | VERIFIED |
| Direct control-plane execution of DB test 017 | NOT EXECUTED |

---

# 55. Acceptance Criteria

The following GAP-BUS-002 acceptance criteria are satisfied:

* [x] An offer is linked to a valid Presentation.
* [x] Multiple commercial versions may exist for one Presentation.
* [x] Each version has a unique version number per Presentation.
* [x] Offer amounts must be positive.
* [x] Offer lifecycle statuses are constrained.
* [x] Expiration timestamps are structurally validated.
* [x] Decision timestamps are consistent with lifecycle state.
* [x] At most one accepted offer may exist per Presentation.
* [x] Revision preserves the previous offer row.
* [x] Revision creates a new SOUMISE version.
* [x] Accepted/refused/revised history can be preserved.
* [x] ADMIN may operate the implemented Offre workflow.
* [x] CHASSEUR ownership behavior is covered by automated tests.
* [x] Cross-owner CHASSEUR access is covered by automated tests.
* [x] CLIENT is not granted the implemented administrative/hunter Offre operations.
* [x] SERVICE is not granted the implemented administrative/hunter Offre operations.
* [x] Creation is audited.
* [x] Revision is audited.
* [x] Decision is audited.
* [x] Runtime audit actor attribution is verified.
* [x] FastAPI exposes the five expected operations.
* [x] Targeted Offre tests pass.
* [x] Full backend/data regression passes.
* [x] CI structural validation passes.
* [x] GitLab pipeline passes.
* [x] Migration 014 is applied in the deployed PostgreSQL database.
* [x] Offre constraints and indexes are present in runtime.
* [x] Implementation is deployed through GitOps.
* [x] Runtime creation is verified.
* [x] Runtime revision is verified.
* [x] Runtime acceptance is verified.
* [x] Runtime historical preservation is verified.
* [x] Final Kubernetes workloads are healthy.
* [ ] Direct CHASSEUR E2E runtime evidence collected.

The final unchecked item is an evidence qualification, not an unimplemented authorization feature.

The corresponding behavior is covered by automated tests, but direct runtime proof was not manufactured using artificial business data.

---

# 56. Security Impact

GAP-BUS-002 extends the existing ownership model instead of introducing authorization based solely on `id_offre`.

For CHASSEUR access:

```text
Offre
  ->
Presentation
  ->
DemandeVersion
  ->
Demande
  ->
DemandeAffectation
  ->
Chasseur
```

This improves:

```text
resource scoping
least privilege
cross-owner protection
IDOR resistance
authorization consistency
audit interpretation
```

The implementation reuses the established demande authorization semantics rather than creating a second ownership source.

---

# 57. Data Integrity Impact

The Offre implementation adds relational and historical integrity at multiple levels.

```text
Foreign key
    ->
valid Presentation

Unique presentation/version
    ->
deterministic history

Positive amount
    ->
valid commercial value

Status check
    ->
known lifecycle

Decision invariant
    ->
consistent status/timestamp state

Partial accepted uniqueness
    ->
single accepted outcome per Presentation

Revision-as-new-row
    ->
historical amount preservation
```

This is materially stronger than mutable single-row offer storage.

---

# 58. Auditability Impact

Before GAP-BUS-002, the platform could not audit a commercial negotiation because no Offre domain existed.

After implementation, the platform can attribute:

```text
offer creation
offer revision
commercial decision
```

to an authenticated actor while retaining old and new business states.

The revision audit also links:

```text
previous_offre_id
    ->
new_offre_id
```

which improves commercial lineage.

---

# 59. No Unnecessary Technology Introduced

GAP-BUS-002 was implemented using the existing platform:

```text
FastAPI
Pydantic
SQLAlchemy
PostgreSQL
JWT/RBAC
audit_log
pytest
GitLab CI
GitOps
Argo CD
Kubernetes
```

No new technology was added merely to implement the workflow.

In particular, the gap did not require:

```text
Kafka
Spark
Databricks
Snowflake
Kubeflow
vector database
RAG
service mesh
additional database engine
```

This keeps the implementation proportional to the requirement.

---

# 60. Known Boundary — Vente Identity

Migration 014 deliberately does not add:

```text
vente.id_offre
```

Therefore GAP-BUS-002 establishes the Offre lifecycle but does not claim to resolve every transaction-identity question between an accepted offer and the eventual sale.

The broader transaction identity / relationship consistency topic remains a separate backlog item.

This boundary prevents GAP-BUS-002 from silently expanding into unrelated Vente redesign.

---

# 61. Known Boundary — Seller Decision Actor

The current domain does not contain a dedicated:

```text
VENDEUR
PROPRIETAIRE
```

actor model.

The implementation therefore does not invent a seller identity or unsupported application role.

Acceptance/refusal is recorded as the commercial decision in the platform by an authorized ADMIN/CHASSEUR actor.

This distinguishes:

```text
business decision being recorded
```

from:

```text
identity of the external person who originally made that decision
```

The latter is not represented by the current domain model.

---

# 62. Known Boundary — Automatic Expiration

`EXPIREE` exists as a valid lifecycle status.

GAP-BUS-002 does not introduce a scheduler that automatically transitions overdue SOUMISE offers to EXPIREE.

Such automation would require its own operational requirement and test strategy.

The status model is ready for that evolution without requiring it for closure of the current gap.

---

# 63. Known Boundary — Concurrency

The partial unique accepted-offer index provides database protection against multiple accepted offers for one Presentation.

Broader concurrency concerns remain part of the separate concurrency backlog.

GAP-BUS-002 does not claim to resolve all cross-domain concurrent business operations.

---

# 64. Known Boundary — Direct CHASSEUR Runtime Evidence

The application code and automated tests cover CHASSEUR ownership.

The final runtime dataset did not provide a legitimate compatible property/presentation chain for the available authenticated CHASSEUR.

The compatibility search returned no candidate rows.

Rather than:

```text
fabricating a poor property match
changing business ownership
resetting an account solely for evidence
```

the runtime validation stopped at the evidence boundary.

This is consistent with the project's evidence principle:

```text
do not manufacture stronger evidence than the runtime genuinely supports
```

---

# 65. Relationship With GAP-BUS-001

GAP-BUS-002 builds on the ownership semantics closed by GAP-BUS-001.

GAP-BUS-001 established that:

```text
Client ownership
Hunter assignment
Version authorship
Mandate contractual relationship
```

are separate concepts.

GAP-BUS-002 reuses that model.

An Offre does not introduce a new owner field.

Instead:

```text
Offre
  ->
Presentation
  ->
DemandeVersion
  ->
Demande
```

provides the client/search lineage, while:

```text
Demande
  ->
DemandeAffectation
  ->
Chasseur
```

provides hunter authorization lineage.

GAP-BUS-001 therefore remains closed and is not reopened by the Offre implementation.

---

# 66. Resulting Business Model

The relevant business model is now:

```text
CLIENT
  |
  | owns
  v
DEMANDE
  |
  +--------------------------+
  |                          |
  | versions                 | assignment
  v                          v
DEMANDE_VERSION      DEMANDE_AFFECTATION
  |                          |
  |                          v
  |                       CHASSEUR
  |
  v
PRESENTATION
  |
  +-------------------+
  |                   |
  v                   v
VISITE               OFFRE
                      |
                      +--> v1
                      |
                      +--> v2
                      |
                      +--> ...
                      |
                      v
              commercial decision
                      |
                      v
                    VENTE
```

The platform can now preserve the commercial negotiation instead of jumping directly from visit/presentation activity to a completed sale.

---

# 67. Resulting End-to-End Lifecycle

The current business lifecycle is:

```text
CLIENT
  ->
DEMANDE
  ->
AFFECTATION CHASSEUR
  ->
DEMANDE_VERSION
  ->
MANDAT
  ->
BIEN INGESTION
  ->
MATCHING
  ->
PRESENTATION
  ->
VISITE
  ->
OFFRE
  ->
ACCEPTATION / REFUS / REVISION
  ->
VENTE
  ->
ACTE AUTHENTIQUE
  ->
HONORAIRES
  ->
FACTURE CLIENT [GAP]
  ->
REMUNERATION CHASSEUR
  ->
FACTURE CHASSEUR [GAP]
  ->
PAIEMENT
  ->
WAREHOUSE / ANALYTICS
```

GAP-BUS-002 is no longer a missing stage in this chain.

---

# 68. Architectural Principles Demonstrated

The implementation demonstrates several project architecture principles.

## Separation of Concerns

```text
Endpoint
Schema
Service
Repository
ORM
Database
```

retain distinct responsibilities.

## Security by Design

Authorization follows existing business lineage instead of trusting arbitrary IDs.

## Defense in Depth

Application validation is complemented by PostgreSQL constraints and indexes.

## Data Integrity

Foreign keys, checks, uniqueness and historical versioning protect commercial state.

## API-First Design

Business transitions are represented by explicit HTTP operations.

## Auditability by Design

Creation, revision and decision events are recorded with authenticated actor context.

## Testability

Service, HTTP, ownership, audit, CI and regression tests cover the implementation.

## Automation First

Validation and deployment use GitLab CI and GitOps.

## Documentation as Code

The business gap, implementation and evidence are maintained with the repository.

---

# 69. RNCP / Portfolio Value

GAP-BUS-002 provides evidence for competencies involving:

```text
business requirement analysis
business-process modeling
relational data modeling
database migration
data integrity
API design
backend architecture
security/RBAC
auditability
automated testing
CI/CD
GitOps
Kubernetes deployment
runtime validation
requirement-to-production traceability
```

Certification mapping must remain aligned with the official StarterPack/RNCP traceability.

BC04/BC06-related material may be retained as extended professional portfolio evidence without claiming those blocks are mandatory StarterPack scope when they are not.

---

# 70. Evidence Summary for Jury

A concise defensible explanation is:

> The original platform contained Presentation, Visite and Vente domains but no persistent commercial-offer workflow. GAP-BUS-002 introduced a versioned `real_estate.offre` domain linked to Presentation. Revisions preserve historical rows rather than overwriting amounts, and PostgreSQL enforces valid amounts, statuses, version uniqueness, decision consistency and at most one accepted offer per Presentation. The FastAPI backend exposes list, create, retrieve, decision and revision operations with ADMIN/CHASSEUR authorization based on existing demande assignment lineage. Creation, revision and decision are written to the existing audit trail. The implementation passed 57 targeted Offre tests, 1365 CI structural tests and a 445-test backend/data regression with the 80% coverage gate. It was delivered through GitLab CI, the container registry, GitOps and Argo CD. Migration 014 and the Offre schema were verified in the running PostgreSQL database. A controlled runtime scenario created a EUR 250,000 offer, revised it to a new EUR 245,000 version, accepted the second version and verified both historical persistence and audit events. Direct CHASSEUR runtime E2E evidence was not manufactured because the deployed dataset did not contain a legitimate compatible candidate; that ownership behavior remains covered by automated tests.

---

# 71. Final Runtime Evidence

Controlled Presentation:

```text
Presentation 32
id_bien             16025
id_demande_version  137
id_demande          17
id_client           18
id_chasseur         2
```

Initial offer:

```text
Offre 13
Version 1
250000.00 EUR
SOUMISE
```

After revision:

```text
Offre 13
Version 1
250000.00 EUR
REVISEE
```

New version:

```text
Offre 14
Version 2
245000.00 EUR
SOUMISE
```

After decision:

```text
Offre 14
Version 2
245000.00 EUR
ACCEPTEE
date_decision = 2026-09-20T16:56:13.274416Z
```

Audit sequence:

```text
INSERT  Offre 13  create_offre
UPDATE  Offre 13  SOUMISE -> REVISEE
INSERT  Offre 14  revise_offre successor
UPDATE  Offre 14  SOUMISE -> ACCEPTEE
```

Final Kubernetes state:

```text
real-estate-backend
1/1 Running
0 restarts

real-estate-postgresql
1/1 Running
0 restarts
```

---

# 72. GAP Closure Decision

## GAP-BUS-002

**Status: CLOSED**

Highest overall evidence state:

```text
RUNTIME VERIFIED
```

with the explicit qualification:

```text
ADMIN lifecycle:
RUNTIME VERIFIED

PostgreSQL schema/integrity:
RUNTIME VERIFIED

Audit:
RUNTIME VERIFIED

CHASSEUR own-resource RBAC:
AUTOMATED TEST VERIFIED

CHASSEUR cross-owner concealment:
AUTOMATED TEST VERIFIED

Direct CHASSEUR runtime E2E:
NOT VERIFIED
```

The qualification is preserved because evidence states must reflect what was actually executed.

It does not convert the implemented Offre domain back into an open business gap.

---

# 73. Final Conclusion

**GAP-BUS-002 is CLOSED.**

The Real Estate Intelligence Platform now supports a persistent, versioned and auditable commercial-offer lifecycle.

The platform has moved from:

```text
Presentation
   ->
Visite
   ->
[missing commercial negotiation]
   ->
Vente
```

to:

```text
Presentation
   |
   +--> Visite
   |
   v
Offre v1
   |
   | revision
   v
Offre v2
   |
   | accept / refuse / withdraw
   v
Commercial outcome
   |
   v
Vente
```

The implementation is protected by:

```text
Presentation lineage
+ versioned history
+ PostgreSQL constraints
+ accepted-offer uniqueness
+ RBAC
+ assignment-based hunter ownership
+ audit trail
+ automated tests
+ regression tests
+ CI
+ GitOps
+ Kubernetes deployment
+ runtime API verification
+ runtime PostgreSQL verification
```

The next business work must not reopen the now-validated Offre workflow unless a new requirement specifically changes its contract.

---

# 74. Remaining Business Priorities

With GAP-BUS-001 and GAP-BUS-002 closed, the remaining confirmed/review-required business topics include:

```text
Client invoice lifecycle
Hunter invoice verification/lifecycle
Transaction identity / relationship consistency
Buyer contextual API
Notifications
Performance recalculation
Historical financial integrity
Concurrency controls
```

These must be handled individually using the same evidence-driven method:

```text
requirement
  ->
source inspection
  ->
runtime inspection
  ->
precise gap
  ->
smallest coherent design
  ->
implementation
  ->
targeted tests
  ->
regression
  ->
CI
  ->
GitOps
  ->
runtime verification
  ->
evidence
  ->
documentation
```

GAP-BUS-002 must now be treated as an implemented platform capability rather than a missing future feature.
