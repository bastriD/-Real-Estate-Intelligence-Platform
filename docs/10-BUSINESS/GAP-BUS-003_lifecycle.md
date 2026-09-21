# GAP-BUS-003 — Facture Client / Client Invoice Lifecycle

**Project:** Enterprise AI Platform — Real Estate Intelligence Platform
**Business domain:** Transaction / Finance / Accounting
**Gap:** GAP-BUS-003
**Status:** IMPLEMENTED — RUNTIME VERIFIED
**Database migration:** 015
**Runtime environment:** Kubernetes / `real-estate` namespace
**Validation date:** 2026-09-20

---

# 1. Purpose

This document records the implementation and runtime validation of the **Client Invoice lifecycle** for the Real Estate Intelligence Platform.

The objective of GAP-BUS-003 is to implement the StarterPack business requirement according to which, following completion of a property purchase and receipt of the company's honoraires, the buyer receives an invoice.

The implementation provides:

* explicit Client Invoice persistence;
* immutable financial snapshots;
* linkage to the completed sale;
* linkage to the purchasing client;
* linkage to the applicable honoraires configuration;
* server-side calculation of company fees;
* validation that honoraires have actually been received;
* controlled invoice numbering;
* duplicate prevention;
* RBAC;
* ownership-scoped reads;
* auditability;
* REST API access.

This gap is distinct from the future **Hunter Invoice / Facture Chasseur** workflow.

---

# 2. StarterPack Business Requirement

The official StarterPack establishes the following business sequence for the purchasing client:

1. the property transaction progresses to the authentic deed;
2. the authentic deed is signed;
3. company honoraires become payable;
4. the buyer pays the honoraires separately from the property purchase price;
5. the notary secures/collects these honoraires for the company;
6. after this financial event, the client receives an invoice.

The StarterPack defines company honoraires using the formula:

```text
H = F + (t × P)
```

Where:

```text
H = company honoraires
F = fixed fee
t = percentage rate
P = property purchase amount
```

The parameters applicable on the authentic-deed date must be used.

The StarterPack also distinguishes this Client Invoice from the later hunter remuneration workflow.

The hunter invoice therefore remains a separate business capability:

```text
Client honoraires received
        ↓
Client Invoice
        ↓
Hunter remuneration becomes payable
        ↓
Hunter prepares/sends invoice
        ↓
Invoice verification
        ↓
Hunter payment programmed
        ↓
Hunter payment completed
```

GAP-BUS-003 covers the **Client Invoice**, not the Hunter Invoice.

---

# 3. Position in the Global Business Flow

The current business lineage is:

```text
CLIENT
  ↓
DEMANDE
  ↓
DEMANDE_AFFECTATION
  ↓
DEMANDE_VERSION
  ↓
MANDAT
  ↓
BIEN
  ↓
MATCHING
  ↓
PRESENTATION
  ↓
VISITE
  ↓
OFFRE
  ↓
VENTE
  ↓
ACTE AUTHENTIQUE
  ↓
HONORAIRES ENTREPRISE
  ↓
FACTURE CLIENT          ← GAP-BUS-003
  ↓
REMUNERATION CHASSEUR
  ↓
FACTURE CHASSEUR        ← GAP-BUS-004
  ↓
PAIEMENT CHASSEUR
```

The Client Invoice therefore belongs to the **completed transaction / accounting** portion of the platform.

---

# 4. Separation Between Paiement and Facture Client

A deliberate architectural distinction exists between:

```text
real_estate.paiement
```

and:

```text
real_estate.facture_client
```

They represent different business concepts.

## 4.1 Paiement

`paiement` represents the financial lifecycle surrounding the transaction and hunter remuneration.

The deployed table contains 32 columns and includes information such as:

* `id_paiement`
* `id_vente`
* `id_mandat`
* `date_acte_authentique`
* `montant_achat`
* `montant_honoraires`
* `date_reception_honoraires`
* `statut`
* `montant_chasseur`
* `date_paiement_chasseur`
* remuneration eligibility;
* remuneration configuration;
* hunter performance snapshot;
* calculated rates and scores.

Payment statuses include the operational financial lifecycle such as:

```text
ATTENDU
RECU
VERIFIE
PROGRAMME
PAYE
ANNULE
```

## 4.2 Facture Client

`facture_client` represents an **immutable accounting/commercial snapshot** issued for a completed sale.

It does not duplicate the operational payment lifecycle.

This avoids maintaining two competing sources of truth for payment status.

Consequently, fields such as:

```text
date_reception_honoraires
date_paiement_chasseur
statut paiement
```

remain in `paiement`.

This separation is intentional.

---

# 5. Migration 015

Migration:

```text
015
```

Description recorded in PostgreSQL:

```text
Add client invoice foundation for completed sales
```

Applied:

```text
2026-09-20 21:51:57.36161+00
```

Migration 015 is now **applied and immutable**.

It must never be modified retrospectively.

Any future justified schema evolution must use a new migration number.

---

# 6. Migration Lineage

Runtime inspection of:

```text
migration_control.schema_version
```

confirmed the following recent lineage:

```text
010  Add transaction and auditable remuneration calculation foundation
011  Seed initial approved remuneration business configuration
012  Backfill hunter entry dates from earliest known legacy business activity...
013  Add explicit demande client ownership and mandate-client consistency
014  Add versioned commercial offer workflow
015  Add client invoice foundation for completed sales
```

The migration-control table contains:

```text
version
description
applied_at
```

No migration checksum or SQL body is stored in this table.

Therefore Git remains the authoritative source for migration SQL, while PostgreSQL records application history.

---

# 7. Deployed Facture Client Schema

Runtime inspection confirmed:

```text
real_estate.facture_client
```

with 11 columns.

| Column                    | Type        | Nullable |
| ------------------------- | ----------- | -------- |
| id_facture_client         | bigint      | NO       |
| id_vente                  | bigint      | NO       |
| id_client                 | bigint      | NO       |
| id_parametres_honoraires  | bigint      | NO       |
| numero_facture            | varchar     | NO       |
| date_emission             | date        | NO       |
| montant_achat             | numeric     | NO       |
| montant_fixe_applique     | numeric     | NO       |
| taux_pourcentage_applique | numeric     | NO       |
| montant_honoraires_ht     | numeric     | NO       |
| date_creation             | timestamptz | NO       |

`date_creation` defaults to:

```text
CURRENT_TIMESTAMP
```

---

# 8. Database Constraints

Runtime inspection confirmed 11 constraints.

## Primary key

```text
pk_facture_client
```

Protects:

```text
id_facture_client
```

## Unique invoice number

```text
uq_facture_client_numero
```

Guarantees uniqueness of:

```text
numero_facture
```

## One invoice per sale

```text
uq_facture_client_vente
```

Guarantees:

```text
VENTE 1 ─── 0..1 FACTURE_CLIENT
```

A Vente cannot receive multiple Client Invoices.

## Foreign keys

```text
fk_facture_client_vente
fk_facture_client_client
fk_facture_client_parametres_honoraires
```

All use:

```text
ON DELETE RESTRICT
```

This protects historical accounting lineage.

## Financial checks

The database also enforces:

```text
montant_achat > 0
montant_fixe_applique >= 0
0 <= taux_pourcentage_applique <= 1
montant_honoraires_ht >= 0
length(trim(numero_facture)) > 0
```

---

# 9. Indexes

Six indexes are deployed:

```text
pk_facture_client
uq_facture_client_numero
uq_facture_client_vente
idx_facture_client_client
idx_facture_client_date_emission
idx_facture_client_parametres_honoraires
```

Naming follows the project's database convention:

```text
pk_   Primary Key
uq_   Unique constraint/index
idx_  ordinary performance index
fk_   Foreign Key
ck_   Check constraint
```

PostgreSQL implements PRIMARY KEY and UNIQUE constraints using unique indexes.

Therefore `pk_facture_client`, `uq_facture_client_numero`, and `uq_facture_client_vente` appearing in the index list is expected behavior and does not represent redundant indexes.

---

# 10. Financial Configuration

Runtime configuration used for the controlled transaction:

```text
id_parametres_honoraires = 3
date_debut_validite      = 2026-01-01
date_fin_validite        = NULL
montant_fixe             = 3000.00
taux_pourcentage         = 0.025000
actif                    = true
```

The effective formula therefore becomes:

```text
H = 3000 + (0.025 × P)
```

For the controlled transaction:

```text
P = €300,000
```

Therefore:

```text
H = 3000 + (0.025 × 300000)

H = 3000 + 7500

H = €10,500
```

The API produced exactly:

```text
montant_honoraires_ht = 10500.00
```

---

# 11. Backend Vertical Slice

Runtime inspection of backend image:

```text
gitlab.local:4567/root/chasse_immobiliere/backend:df64f062
```

confirmed the following deployed implementation:

```text
/app/src/api/db/models/facture_client.py
/app/src/api/repositories/facture_client.py
/app/src/api/schemas/facture_client.py
/app/src/api/services/facture_client.py
/app/src/api/api/v1/endpoints/factures_clients.py
```

The implementation therefore follows the established backend layering:

```text
HTTP
 ↓
FastAPI Endpoint
 ↓
Authentication / RBAC
 ↓
Pydantic Schema
 ↓
FactureClientService
 ↓
FactureClientRepository
 ↓
SQLAlchemy
 ↓
PostgreSQL
```

---

# 12. Router Registration

The Facture Client router is registered in:

```text
src/api/api/v1/router.py
```

through:

```text
factures_clients_router
```

and included in the main API router.

The router prefix is:

```text
/factures-clients
```

The main API prefix is:

```text
/api/v1
```

Final endpoints are therefore:

```text
GET  /api/v1/factures-clients
GET  /api/v1/factures-clients/{invoice_id}
POST /api/v1/factures-clients
```

---

# 13. API Creation Contract

Runtime inspection of `FactureClientCreate` confirmed that the creation payload contains exactly one field:

```text
id_vente
```

Example:

```json
{
  "id_vente": 3
}
```

The caller cannot submit:

```text
id_client
montant_achat
montant_fixe_applique
taux_pourcentage_applique
montant_honoraires_ht
id_parametres_honoraires
numero_facture
```

These values are derived server-side.

This prevents callers from fabricating invoice financial information.

---

# 14. Server-Side Business Logic

`FactureClientService.create_facture()` performs the following workflow.

## 14.1 Sale resolution

The service retrieves the Vente and its Mandat.

If the sale cannot be resolved:

```text
404 Resource not found
```

is returned.

## 14.2 Duplicate protection

The service verifies whether an invoice already exists for the Vente.

If one exists:

```text
409 A client invoice already exists for this sale
```

is returned.

The database independently enforces the same rule through:

```text
uq_facture_client_vente
```

This provides defense in depth.

## 14.3 Authentic deed validation

The service ensures:

```text
date_acte_authentique <= current date
```

An invoice cannot be issued before the authentic deed has occurred.

## 14.4 Honoraires receipt validation

The associated Paiement must exist.

Its status must be one of:

```text
RECU
VERIFIE
PROGRAMME
PAYE
```

and:

```text
date_reception_honoraires IS NOT NULL
```

The date must satisfy:

```text
date_acte_authentique
    <= date_reception_honoraires
    <= invoice issuance date
```

Therefore the Client Invoice cannot be issued before the company has received the honoraires.

This directly implements the StarterPack business sequence.

---

# 15. Effective Parameter Selection

The service retrieves the honoraires configuration effective on:

```text
vente.date_acte_authentique
```

It does not simply use today's active configuration.

This preserves historical financial correctness.

The service then uses the existing shared calculation:

```text
calculate_company_fees()
```

rather than implementing a second fee-calculation algorithm.

---

# 16. Financial Snapshot Consistency

Before issuing the invoice, the service cross-checks the Paiement snapshot against the Vente and effective configuration.

It validates:

```text
payment.id_mandat
    == vente.id_mandat

payment.date_acte_authentique
    == vente.date_acte_authentique

payment.montant_achat
    == vente.montant_achat

payment.id_parametres_honoraires
    == effective parameters

payment.montant_honoraires
    == newly calculated fees
```

If the received-fee snapshot differs from the sale or applicable configuration, invoice creation is rejected.

This prevents an invoice from being issued against inconsistent financial history.

---

# 17. Client Ownership Derivation

The invoice client is not supplied by the caller.

The authoritative lineage is:

```text
FactureClient
      ↓
Vente
      ↓
Mandat
      ↓
Client
```

The service derives:

```text
id_client = mandat.id_client
```

For the controlled runtime scenario:

```text
Vente 3
  ↓
Mandat 17
  ↓
Client 18
```

The generated invoice therefore correctly contains:

```text
id_client = 18
```

---

# 18. Invoice Number

The deployed service generates the invoice number deterministically from the Vente:

```text
FC-{id_vente:010d}
```

For Vente 3:

```text
FC-0000000003
```

The implementation explicitly avoids:

```text
MAX(numero) + 1
```

style numbering races.

The database additionally guarantees uniqueness through:

```text
uq_facture_client_numero
```

---

# 19. Immutable Financial Snapshot

When the invoice is created, the following values are frozen:

```text
id_vente
id_client
id_parametres_honoraires
numero_facture
date_emission
montant_achat
montant_fixe_applique
taux_pourcentage_applique
montant_honoraires_ht
date_creation
```

This means future changes to fee parameters do not rewrite the historical invoice.

The invoice records the financial conditions actually applicable to the transaction.

---

# 20. RBAC

The deployed endpoint defines the following authorization model.

## ADMIN

ADMIN can:

```text
LIST invoices
GET invoice
CREATE invoice
```

Invoice creation is explicitly:

```python
require_roles("ADMIN")
```

## CLIENT

CLIENT can:

```text
LIST own invoices
GET own invoice
```

The client scope is derived from:

```text
require_client_identity(current_user)
```

## CHASSEUR

CHASSEUR can:

```text
LIST accessible invoices
GET accessible invoice
```

The hunter scope is derived from:

```text
require_chasseur_identity(current_user)
```

## SERVICE

SERVICE is not included in the Facture Client endpoint roles.

---

# 21. Enumeration Protection

For single invoice access, the service intentionally returns the same response for:

```text
invoice does not exist
```

and:

```text
invoice exists but does not belong to the authenticated scope
```

Response:

```text
404 Resource not found
```

This prevents unauthorized users from determining whether another invoice exists.

---

# 22. Controlled Runtime Scenario

The runtime transaction used for validation was:

```text
Vente                  3
Mandat                 17
Client                 18
Paiement               9
Authentic deed         2026-09-14
Honoraires received    2026-09-14
Payment status         PAYE
Purchase amount        €300,000.00
Honoraires parameters  3
Company honoraires     €10,500.00
```

Before the controlled test:

```text
facture_client rows for Vente 3 = 0
```

This provided a clean runtime scenario.

---

# 23. Runtime Test — Invoice Creation

Request:

```text
POST /api/v1/factures-clients
```

Payload:

```json
{
  "id_vente": 3
}
```

Authentication:

```text
ADMIN
```

Runtime result:

```text
HTTP 201
```

Response:

```json
{
  "id_facture_client": 3,
  "id_vente": 3,
  "id_client": 18,
  "id_parametres_honoraires": 3,
  "numero_facture": "FC-0000000003",
  "date_emission": "2026-09-20",
  "montant_achat": "300000.00",
  "montant_fixe_applique": "3000.00",
  "taux_pourcentage_applique": "0.0250",
  "montant_honoraires_ht": "10500.00",
  "date_creation": "2026-09-20T22:14:38.761940Z"
}
```

Result:

```text
PASS
```

---

# 24. Runtime Test — PostgreSQL Persistence

Direct PostgreSQL verification confirmed:

```text
id_facture_client          3
numero_facture             FC-0000000003
id_vente                   3
id_client                  18
id_parametres_honoraires   3
date_emission              2026-09-20
montant_achat              300000.00
montant_fixe_applique      3000.00
taux_pourcentage_applique  0.0250
montant_honoraires_ht      10500.00
```

Result:

```text
PASS
```

---

# 25. Runtime Test — Audit Trail

Creation generated:

```text
audit_log.id_audit = 34
```

with:

```text
table_name = facture_client
operation  = INSERT
record_id  = 3
utilisateur = admin.auth.test@example.com
```

Audit context records:

```text
action                     ISSUE_FACTURE_CLIENT
source                     api
id_vente                   3
id_mandat                  17
id_paiement                9
id_utilisateur             1
date_acte_authentique      2026-09-14
date_reception_honoraires  2026-09-14
```

The complete invoice snapshot is also stored in:

```text
nouvelle_valeur
```

Result:

```text
PASS
```

This establishes end-to-end traceability:

```text
Authenticated ADMIN
      ↓
API
      ↓
Vente 3
      ↓
Mandat 17
      ↓
Client 18
      ↓
Paiement 9
      ↓
Facture Client 3
      ↓
Audit Event 34
```

---

# 26. Runtime Test — Duplicate Protection

The exact same creation request was executed a second time.

Result:

```text
HTTP 409
```

Response:

```json
{
  "detail": "A client invoice already exists for this sale"
}
```

No second invoice was created.

This proves the application-level uniqueness rule.

The database additionally guarantees the same invariant with:

```text
uq_facture_client_vente
```

Result:

```text
PASS
```

---

# 27. Runtime Test — GET by ID

Request:

```text
GET /api/v1/factures-clients/3
```

Result:

```text
HTTP 200
```

The API returned the same immutable financial snapshot:

```text
FC-0000000003
Vente 3
Client 18
€300,000 purchase
€3,000 fixed fee
2.5%
€10,500 HT
```

Result:

```text
PASS
```

---

# 28. Runtime Test — LIST

Request:

```text
GET /api/v1/factures-clients
```

using ADMIN authentication.

Result:

```text
HTTP 200
```

The returned collection contained:

```text
FC-0000000003
```

with the expected persisted financial snapshot.

Result:

```text
PASS
```

---

# 29. Runtime Test — Nonexistent Resource

Request:

```text
GET /api/v1/factures-clients/999999
```

Result:

```text
HTTP 404
```

Response:

```json
{
  "detail": "Resource not found"
}
```

Result:

```text
PASS
```

This confirms the enumeration-safe resource behavior.

---

# 30. CLIENT / CHASSEUR Runtime Limitation

Runtime inspection searched for identities associated with:

```text
Client 18
```

and the hunter benefiting from:

```text
Vente 3
```

No matching `utilisateur` accounts existed.

Result:

```text
0 rows
```

Therefore genuine CLIENT and CHASSEUR runtime access tests were deliberately not manufactured by creating artificial production-like identities.

The deployed endpoint and service implement the ownership scopes, but direct Kubernetes E2E evidence for those roles remains separate from the ADMIN runtime evidence.

This limitation must remain explicit in jury documentation.

It does not invalidate the successfully verified ADMIN business lifecycle.

---

# 31. Runtime Deployment Evidence

During validation:

```text
Namespace:
real-estate
```

Backend:

```text
Deployment:
real-estate-backend

Ready:
1/1

Image:
gitlab.local:4567/root/chasse_immobiliere/backend:df64f062
```

PostgreSQL:

```text
PostgreSQL 16
Ready: 1/1
```

Migration 015 was present in:

```text
migration_control.schema_version
```

and the resulting schema was directly inspected from PostgreSQL.

---

# 32. Business Invariants Proven

The following invariants are now demonstrated.

### INV-FC-001

A Client Invoice references an existing Vente.

**Status:** enforced.

### INV-FC-002

A Client Invoice references an existing Client.

**Status:** enforced.

### INV-FC-003

The Client is derived from the persisted Vente → Mandat lineage.

**Status:** implemented and runtime verified.

### INV-FC-004

One Vente can have at most one Client Invoice.

**Status:** database enforced and runtime verified.

### INV-FC-005

An invoice number is unique.

**Status:** database enforced.

### INV-FC-006

An invoice cannot be issued before the authentic deed.

**Status:** service enforced.

### INV-FC-007

An invoice cannot be issued before company honoraires are received.

**Status:** service enforced.

### INV-FC-008

The applicable honoraires configuration is selected according to the authentic-deed date.

**Status:** implemented.

### INV-FC-009

The financial calculation uses the shared company-fee calculator.

**Status:** implemented and runtime result verified.

### INV-FC-010

The invoice freezes the transaction financial snapshot.

**Status:** database persisted and runtime verified.

### INV-FC-011

Invoice issuance is auditable.

**Status:** runtime verified.

### INV-FC-012

Only ADMIN can issue Client Invoices through the API.

**Status:** endpoint enforced.

### INV-FC-013

CLIENT and CHASSEUR reads use authenticated persisted identity scopes.

**Status:** implemented; direct role-specific runtime E2E not performed for the controlled transaction because matching identities do not exist.

### INV-FC-014

Foreign and nonexistent invoice access use the same not-found semantics.

**Status:** implemented; nonexistent-resource runtime path verified.

---

# 33. StarterPack vs Enterprise Implementation

It is important to distinguish requirements from project design.

## StarterPack requirement

The StarterPack establishes:

```text
Authentic deed
    ↓
Company honoraires paid/received
    ↓
Client receives invoice
```

and the honoraires calculation based on:

```text
fixed amount + percentage of purchase price
```

## Enterprise implementation

The project strengthens this requirement with:

* explicit relational invoice persistence;
* immutable financial snapshots;
* historical fee-parameter lineage;
* one-invoice-per-sale invariant;
* deterministic invoice numbering;
* ADMIN-only issuance;
* CLIENT/CHASSEUR read scopes;
* enumeration protection;
* financial consistency validation;
* audit logging;
* database constraints;
* API contracts;
* Kubernetes runtime validation.

These are enterprise implementation decisions supporting the StarterPack business requirement.

They must not be presented as if every technical detail were explicitly dictated by the StarterPack.

---

# 34. VAT / TTC / Billing Address Boundary

The deployed Client Invoice currently stores:

```text
montant_honoraires_ht
```

It does not currently store dedicated:

```text
taux_tva
montant_tva
montant_ttc
billing address snapshot
invoice PDF
```

The currently verified StarterPack evidence does not establish these as explicit requirements for GAP-BUS-003.

They must therefore not be invented merely to make the model appear more sophisticated.

If later required by a formal accounting/legal requirement or a project enhancement decision, they must be introduced through a justified future schema evolution.

Migration 015 must not be rewritten.

---

# 35. Migration 015 Decision

Migration 015 is:

```text
APPLIED
VALID
IMMUTABLE
```

The fact that it is named:

```text
Add client invoice foundation for completed sales
```

does not mean the current capability consists only of a database table.

The application layer now supplies the complete validated business behavior around that foundation.

No migration 016 is justified merely to add redundant payment lifecycle information to `facture_client`.

A future migration must correspond to a genuine new schema requirement.

---

# 36. Evidence Matrix

| Capability                        | Evidence                       | Status             |
| --------------------------------- | ------------------------------ | ------------------ |
| Migration 015 applied             | PostgreSQL `schema_version`    | PASS               |
| `facture_client` table            | PostgreSQL schema inspection   | PASS               |
| PK/FK/check constraints           | PostgreSQL catalog             | PASS               |
| One invoice per Vente             | `uq_facture_client_vente`      | PASS               |
| Unique invoice number             | `uq_facture_client_numero`     | PASS               |
| Backend model                     | deployed container             | PASS               |
| Repository                        | deployed container             | PASS               |
| Pydantic schemas                  | deployed container             | PASS               |
| Service                           | deployed container             | PASS               |
| FastAPI endpoint                  | deployed container             | PASS               |
| Router registration               | deployed container             | PASS               |
| ADMIN create                      | HTTP 201 runtime               | PASS               |
| Server-derived Client             | Client 18 runtime              | PASS               |
| Server-derived configuration      | Params 3 runtime               | PASS               |
| Company-fee calculation           | €10,500 runtime                | PASS               |
| PostgreSQL persistence            | direct SQL                     | PASS               |
| Audit logging                     | audit event 34                 | PASS               |
| Duplicate protection              | HTTP 409 runtime               | PASS               |
| GET invoice                       | HTTP 200 runtime               | PASS               |
| LIST invoices                     | HTTP 200 runtime               | PASS               |
| Missing resource                  | HTTP 404 runtime               | PASS               |
| CLIENT ownership implementation   | source/runtime code inspection | IMPLEMENTED        |
| CHASSEUR ownership implementation | source/runtime code inspection | IMPLEMENTED        |
| CLIENT direct E2E                 | no matching runtime identity   | NOT RUNTIME TESTED |
| CHASSEUR direct E2E               | no matching runtime identity   | NOT RUNTIME TESTED |

---

# 37. Final Status

GAP-BUS-003 is classified as:

```text
IMPLEMENTED
DATABASE APPLIED
DEPLOYED
CORE BUSINESS LIFECYCLE RUNTIME VERIFIED
AUDIT VERIFIED
FINANCIAL CONSISTENCY VERIFIED
```

Highest evidence level:

```text
RUNTIME VERIFIED
```

for the core Client Invoice lifecycle and ADMIN path.

Role-specific CLIENT/CHASSEUR direct E2E remains explicitly unverified in the current Kubernetes dataset because appropriate authenticated identities are absent.

---

# 38. Conclusion

The platform now implements the StarterPack Client Invoice requirement as a traceable enterprise business capability.

For the controlled transaction:

```text
Vente 3
   ↓
Mandat 17
   ↓
Client 18
   ↓
Authentic deed 2026-09-14
   ↓
Paiement 9
   ↓
€10,500 honoraires received
   ↓
Facture Client 3
   ↓
FC-0000000003
   ↓
€10,500 HT
   ↓
Audit Event 34
```

The invoice cannot be issued from arbitrary client or financial values.

Its authoritative data is reconstructed from persisted business lineage, validated against the received-payment snapshot, calculated using the configuration effective on the authentic-deed date, frozen into an immutable accounting snapshot, and audited against the authenticated administrator.

**GAP-BUS-003 — Facture Client is therefore complete for its currently established StarterPack scope.**

The next distinct business capability in the agreed implementation sequence is:

```text
GAP-BUS-004 — Facture Chasseur
```

which must remain separate from the Client Invoice lifecycle documented here.
