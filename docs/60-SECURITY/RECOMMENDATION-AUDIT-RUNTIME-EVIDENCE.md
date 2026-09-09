# Recommendation Audit Trail — Implementation & Runtime Evidence

**Project:** PROJECT_FIL_ROUGE — Enterprise Real Estate Intelligence Platform
**Component:** FastAPI Backend / Recommendation Engine / Security & Audit
**Date:** 2026-09-09
**Status:** Runtime Verified
**Scope:** Auditability of presentations generated automatically by the recommendation workflow

---

## 1. Objective

The Real Estate Intelligence Platform persists property recommendations as records in:

```text
real_estate.presentation
```

The platform already supported audit logging for direct Presentation CRUD operations performed through the Presentation API.

A remaining gap was identified in the recommendation workflow.

The recommendation engine persisted new `Presentation` records directly through `PresentationRepository`, bypassing `PresentationService`.

Consequently:

```text
Direct Presentation API
    → PresentationService
    → AuditLogService
    → audit_log
```

was audited, while:

```text
Recommendation API
    → RecommendationService
    → PresentationRepository
    → presentation
```

was not.

The objective was therefore to extend the existing audit mechanism to recommendation-generated presentations without changing the deterministic matching algorithm, recommendation idempotency, Prometheus instrumentation, or transactional persistence model.

---

## 2. Initial Runtime Finding

Inspection of the deployed `RecommendationService` established that recommendation persistence used:

```text
PresentationRepository
```

directly.

The workflow:

1. loads the matching input;
2. calculates deterministic matching features;
3. ranks eligible properties;
4. checks whether a Presentation already exists;
5. creates missing Presentation records;
6. flushes the SQLAlchemy session;
7. assigns generated presentation IDs;
8. commits the complete Top-N recommendation operation.

The existing implementation intentionally used one final transaction for the complete recommendation operation.

This behavior needed to be preserved.

---

## 3. Design Decision

The recommendation workflow was **not** refactored to call `PresentationService.create_presentation()`.

Doing so could have changed the existing transaction boundary because the direct Presentation service owns its own business transaction behavior.

Instead, `AuditLogService` was integrated directly into `RecommendationService`.

The resulting architecture is:

```text
Authenticated User
        │
        ▼
FastAPI Recommendation Endpoint
        │
        │ current_user.email
        ▼
RecommendationService
        │
        ├── Deterministic eligibility/ranking
        │
        ├── PresentationRepository
        │       │
        │       └── CREATE Presentation
        │
        ├── Session FLUSH
        │       │
        │       └── generated id_presentation available
        │
        ├── AuditLogService
        │       │
        │       └── CREATE audit_log entry
        │
        └── Single COMMIT
```

The Presentation and corresponding audit entry therefore participate in the same database transaction.

If persistence fails:

```text
ROLLBACK
 ├── Presentation
 └── Audit entry
```

This prevents partial recommendation persistence and orphan audit records.

---

## 4. Modified Components

### Recommendation Service

File:

```text
src/api/services/recommendation.py
```

The service now initializes:

```python
self.audit = AuditLogService(db)
```

The authenticated actor can be propagated through:

```python
utilisateur: str | None = None
```

After newly created presentations have been flushed and their database-generated IDs are available, an audit entry is generated for each new Presentation.

Audit operation:

```text
INSERT
```

Audit table:

```text
presentation
```

Audit context:

```json
{
  "source": "recommendation",
  "action": "generate_recommendations"
}
```

The audit snapshot records the persisted Presentation information, including:

```text
id_presentation
id_demande_version
id_bien
score_matching
statut
date_presentation
```

### Recommendation API Endpoint

File:

```text
src/api/api/v1/endpoints/recommendations.py
```

The endpoint was already protected by:

```python
require_roles("ADMIN", "CHASSEUR", "SERVICE")
```

The authenticated identity is now propagated to the recommendation service:

```python
utilisateur=current_user.email
```

The audit trail therefore identifies the authenticated application user who initiated recommendation generation.

---

## 5. Idempotency Behavior

Existing Presentation records are not audited again as new INSERT operations.

The workflow first executes the existing lookup:

```text
get_by_demande_and_bien(...)
```

If the Presentation already exists:

```text
existing_presentations += 1
```

and the existing Presentation is reused.

No new Presentation is inserted and therefore no new `INSERT` audit event is generated.

Only genuinely new recommendation-generated Presentation records produce new audit entries.

This preserves the existing recommendation idempotency behavior.

---

## 6. Automated Test Evidence

### Recommendation Service Tests

The recommendation service test suite was updated to verify:

* audit creation for newly generated presentations;
* authenticated user propagation;
* correct Presentation snapshot;
* correct audit context;
* no duplicate audit INSERT for reused Presentation records;
* preservation of database flush and commit behavior;
* compatibility with recommendation Prometheus metrics.

Result:

```text
11 passed
```

### Recommendation API Tests

API tests were updated to provide an authenticated user when directly invoking the FastAPI endpoint and to verify propagation of:

```text
admin.auth.test@example.com
```

to `RecommendationService`.

Result:

```text
4 passed
```

### Full Backend Regression

The complete backend test suite was executed after the changes.

Result:

```text
135 passed
```

No backend regression was detected.

---

## 7. Kubernetes Deployment Evidence

The deployed backend was inspected in namespace:

```text
real-estate
```

Observed state:

```text
Deployment: real-estate-backend
Ready:      1/1
Available:  1
```

Deployed image:

```text
gitlab.local:4567/root/chasse_immobiliere/backend:333f5f51
```

Running pod:

```text
real-estate-backend-c57c8bcc4-hl6d2
```

Node:

```text
k8s-wk-05
```

Pod restarts:

```text
0
```

Argo CD state:

```text
Application: real-estate-backend
Sync:        Synced
Health:      Healthy
Revision:    f4ef4359058d52d4358582b2fafac89efb1a886c
```

Runtime Python introspection inside the deployed backend confirmed:

```text
AuditLogService: True
self.audit: True
generate_recommendations audit context: True
utilisateur parameter: True
```

The deployed Recommendation API endpoint was also inspected.

Result:

```text
current_user.email passed: True
```

The deployed code therefore contained both the audit implementation and authenticated actor propagation.

---

## 8. End-to-End Runtime Verification

A clean demand version was selected:

```text
id_demande_version = 56
```

Before the test:

```text
presentations_before = 0
recommendation_audits_before = 0
```

The recommendation endpoint was invoked using the authenticated ADMIN test identity:

```text
admin.auth.test@example.com
```

Request:

```text
POST /api/v1/demande-versions/56/recommendations?limit=1
```

The API returned:

```json
{
  "id_demande_version": 56,
  "requested_limit": 1,
  "eligible_candidates": 200,
  "selected_candidates": 1,
  "created_presentations": 1,
  "existing_presentations": 0,
  "recommendations": [
    {
      "id_bien": 11225,
      "reference_externe": "AN-4G1AYBSY",
      "matching_score": "100.0",
      "rank": 1,
      "presentation_id": 31,
      "persisted": true
    }
  ]
}
```

This proved that the recommendation workflow created exactly one new Presentation.

---

## 9. Database Verification

The persisted Presentation was queried directly from PostgreSQL.

Result:

```text
id_presentation      31
id_demande_version   56
id_bien              11225
score_matching       100.00
statut                IDENTIFIE
```

The corresponding `real_estate.audit_log` record was then retrieved.

Result:

```text
id_audit       7
table_name     presentation
operation      INSERT
record_id      31
utilisateur    admin.auth.test@example.com
```

Previous value:

```text
null
```

New value:

```json
{
  "statut": "IDENTIFIE",
  "id_bien": 11225,
  "score_matching": "100.00",
  "id_presentation": 31,
  "date_presentation": null,
  "id_demande_version": 56
}
```

Context:

```json
{
  "action": "generate_recommendations",
  "source": "recommendation"
}
```

The audit row therefore corresponds directly to the Presentation persisted by the recommendation request.

---

## 10. Traceability

The runtime evidence provides the following traceability chain:

```text
Authenticated ADMIN
admin.auth.test@example.com
        │
        ▼
POST recommendation endpoint
id_demande_version = 56
limit = 1
        │
        ▼
200 eligible candidates
        │
        ▼
1 candidate selected
id_bien = 11225
        │
        ▼
Presentation created
id_presentation = 31
score = 100.00
status = IDENTIFIE
        │
        ▼
Audit entry created
id_audit = 7
operation = INSERT
record_id = 31
        │
        ▼
Actor
admin.auth.test@example.com
        │
        ▼
Context
source = recommendation
action = generate_recommendations
```

This establishes application-user-to-business-record traceability for recommendation-generated presentations.

---

## 11. Current Verification Status

| Capability                              | Status             |
| --------------------------------------- | ------------------ |
| Audit design                            | ✅ DESIGNED         |
| Recommendation audit implementation     | ✅ IMPLEMENTED      |
| Service tests                           | ✅ TESTED           |
| API tests                               | ✅ TESTED           |
| Full backend regression                 | ✅ 135/135 PASS     |
| Kubernetes deployment                   | ✅ DEPLOYED         |
| Argo CD health                          | ✅ SYNCED / HEALTHY |
| Authenticated actor propagation         | ✅ RUNTIME VERIFIED |
| Recommendation Presentation persistence | ✅ RUNTIME VERIFIED |
| Recommendation audit INSERT             | ✅ RUNTIME VERIFIED |
| Audit snapshot                          | ✅ RUNTIME VERIFIED |
| Audit context                           | ✅ RUNTIME VERIFIED |
| End-to-end traceability                 | ✅ EVIDENCED        |

**Final status:**

```text
DESIGNED
    ↓
IMPLEMENTED
    ↓
TESTED
    ↓
DEPLOYED
    ↓
RUNTIME VERIFIED
    ↓
EVIDENCED
```

---

## 12. Combined Presentation Audit Coverage

At this checkpoint, two Presentation mutation paths have runtime audit evidence.

### Direct Presentation CRUD

Runtime verified:

```text
INSERT
UPDATE
DELETE
```

with:

* authenticated actor;
* previous value where applicable;
* new value where applicable;
* API action context;
* record identifier.

### Recommendation-Generated Presentations

Runtime verified:

```text
INSERT
```

with:

* authenticated actor;
* generated Presentation identifier;
* persisted Presentation snapshot;
* recommendation-specific context.

Therefore the previously identified gap where recommendation persistence bypassed Presentation audit logging is now closed.

---

## 13. Remaining Audit Scope

This evidence does **not** mean that application audit logging is complete globally.

Other mutable business domains still need to be evaluated and, where required, integrated with the same audit mechanism, including:

```text
clients
demandes / demande revisions
mandats
visites
```

Authentication-event auditing is also a separate concern.

The current `audit_log.operation` database constraint accepts:

```text
INSERT
UPDATE
DELETE
```

Therefore events such as:

```text
LOGIN_SUCCESS
LOGIN_FAILURE
```

must not be artificially represented as CRUD operations.

If authentication-event auditing is required, it should be introduced through an explicit schema evolution or dedicated security-event model.

---

## 14. Conclusion

The recommendation workflow now participates in the platform's application-level audit architecture.

The implementation preserves the existing deterministic recommendation behavior and transactional Top-N persistence while adding authenticated traceability for newly generated Presentation records.

The complete path has been verified through:

```text
Source implementation
        +
Automated service tests
        +
API tests
        +
135-test backend regression
        +
Kubernetes deployment inspection
        +
Argo CD verification
        +
Authenticated API execution
        +
PostgreSQL business-record verification
        +
PostgreSQL audit-record verification
```

The recommendation-generated Presentation audit gap is therefore considered **closed and evidenced as of 2026-09-09**.
