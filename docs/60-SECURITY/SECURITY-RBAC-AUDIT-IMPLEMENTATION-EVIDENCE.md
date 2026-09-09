# Security, Authentication, RBAC & Audit Trail

**Project:** PROJECT_FIL_ROUGE — Enterprise Real Estate Intelligence Platform
**Training:** Diginamic Data & IA
**Component:** FastAPI Backend / PostgreSQL / Kubernetes / GitOps
**Date:** 2026-09-09
**Status:** Implemented, Tested, Deployed and Partially Runtime-Evidenced
**Security checkpoint:** Authentication + RBAC + Business Audit Trail

---

# 1. Purpose

The Real Estate Intelligence Platform initially provided a functional data platform and business API but did not yet provide complete application-level identity and authorization controls.

The security workstream therefore focused on introducing a pragmatic security architecture suitable for the current project scope:

* application identities;
* secure password storage;
* authentication;
* JWT access tokens;
* role-based access control;
* protection of business endpoints;
* authenticated actor propagation;
* business-operation auditing;
* PostgreSQL audit persistence;
* Kubernetes secret usage;
* non-root backend execution;
* data minimization and RGPD considerations;
* automated security regression testing;
* runtime evidence.

The objective was not to introduce a full enterprise IAM platform such as Keycloak.

The objective was to establish a clear and demonstrable security chain:

```text
Identity
   ↓
Authentication
   ↓
JWT
   ↓
FastAPI Security Dependency
   ↓
RBAC
   ↓
Business Service
   ↓
Business Transaction
   ↓
Audit Trail
```

---

# 2. Security Architecture

The implemented architecture is:

```text
                    USER / FUTURE UI
                           │
                           │ email + password
                           ▼
                 POST /api/v1/auth/login
                           │
                           ▼
                  AuthenticationService
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       utilisateur table         Password verification
                                      Argon2
              │
              ▼
          JWT issued
              │
              ▼
      Authorization: Bearer
              │
              ▼
         FastAPI Backend
              │
              ▼
        get_current_user()
              │
              ▼
        require_roles(...)
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
   Authorized     HTTP 403
       │
       ▼
 Business Endpoint
       │
       ▼
 Business Service
       │
       ├──── Business mutation
       │
       └──── AuditLogService
                    │
                    ▼
           real_estate.audit_log
```

The same backend security layer will remain valid when a web UI is introduced later.

The UI will not implement independent authorization or audit rules.

---

# 3. Application Identity Model

## 3.1 Migration 006

A dedicated application identity table was introduced through migration:

```text
006
```

Table:

```text
real_estate.utilisateur
```

The identity model is deliberately separate from the legacy:

```text
Fil_Rouge_Depart.utilisateurs
```

The legacy table is therefore not used as the new application's authentication identity source.

---

## 3.2 Identity Structure

The application identity contains:

```text
id_utilisateur
email
password_hash
role
actif
id_client
id_chasseur
derniere_connexion
date_creation
date_modification
```

Supported roles:

```text
ADMIN
CLIENT
CHASSEUR
SERVICE
```

---

## 3.3 Business Identity Constraints

The database enforces relationships between application roles and business identities.

### CLIENT

A CLIENT identity must reference exactly one:

```text
real_estate.client
```

and must not reference a hunter.

### CHASSEUR

A CHASSEUR identity must reference exactly one:

```text
real_estate.chasseur
```

and must not reference a client.

### ADMIN / SERVICE

ADMIN and SERVICE identities do not require client or hunter business identities.

---

## 3.4 Database Controls

The identity table includes:

* primary key;
* role constraint;
* business-identity consistency constraint;
* non-empty password hash constraint;
* basic email validation;
* case-insensitive unique email;
* partial unique client identity;
* partial unique hunter identity;
* foreign keys with RESTRICT behavior.

Migration 006 does **not** automatically create default accounts.

This avoids embedding operational credentials in database migrations.

---

# 4. Password Security

Plain-text passwords are not stored.

Backend dependency:

```text
pwdlib[argon2]
```

Password handling uses:

```python
PasswordHash.recommended()
```

The backend provides:

```text
hash_password()
verify_password()
```

The resulting stored value is an Argon2 password hash.

Example architecture:

```text
Password entered
      │
      ▼
Argon2 verification
      │
      ├── invalid → authentication rejected
      │
      └── valid
             │
             ▼
          JWT issued
```

Runtime test accounts confirmed that authentication operates using stored password hashes rather than stored plaintext passwords.

---

# 5. JWT Authentication

JWT support is implemented in:

```text
src/api/core/security.py
```

Configuration is supplied through:

```text
src/api/core/config.py
```

Current JWT characteristics include:

```text
Algorithm: HS256
Expiration: 30 minutes
Secret: environment / Kubernetes Secret
```

The JWT secret is required by application configuration.

It is not intended to be hard-coded in application source code.

---

# 6. Authentication Endpoint

Authentication endpoint:

```text
POST /api/v1/auth/login
```

Implementation:

```text
src/api/api/v1/endpoints/auth.py
```

Authentication flow:

```text
email/password
      │
      ▼
lookup utilisateur
      │
      ▼
password verification
      │
      ▼
account status
      │
      ▼
JWT
```

Invalid credentials result in:

```text
HTTP 401
```

Inactive-account handling exists separately.

The login endpoint is intentionally public because authentication must be possible before possession of a JWT.

---

# 7. Authentication Dependencies

Central FastAPI security dependencies are implemented in:

```text
src/api/core/dependencies.py
```

## get_current_user()

Responsibilities:

1. retrieve Bearer token;
2. reject missing token;
3. decode JWT;
4. retrieve corresponding application identity;
5. verify account state;
6. construct `AuthenticatedUser`.

Missing or invalid authentication results in an authentication failure.

---

## require_roles()

Authorization is centralized through:

```python
require_roles(...)
```

Example:

```python
require_roles(
    "ADMIN",
    "CHASSEUR",
    "SERVICE",
)
```

The dependency checks the authenticated user's role before the business endpoint executes.

Unauthorized role access results in:

```text
HTTP 403
```

This separates:

```text
Authentication → Who are you?
Authorization  → Are you allowed to perform this action?
```

---

# 8. Runtime Test Identities

Temporary identities were created for runtime verification.

## ADMIN

```text
id_utilisateur: 1
email: admin.auth.test@example.com
role: ADMIN
active: true
```

## CLIENT

```text
id_utilisateur: 2
email: client.auth.test@example.com
role: CLIENT
active: true
id_client: 1
```

## CHASSEUR

```text
id_utilisateur: 3
email: chasseur.auth.test@example.com
role: CHASSEUR
active: true
id_chasseur: 1
```

The CHASSEUR identity is associated with the corresponding business hunter record.

These accounts are test identities and are not intended as permanent production credentials.

They should eventually be removed or rotated.

No SERVICE runtime test identity has yet been evidenced.

---

# 9. RBAC Policy

The current authorization model is role-based.

It is not yet fine-grained ownership-based authorization.

---

## 9.1 Clients

Endpoints:

```text
CREATE
GET
LIST
UPDATE
DELETE
```

Allowed:

```text
ADMIN
```

Runtime evidence:

```text
No token → 401
ADMIN    → 200 / authorized
CLIENT   → 403
```

Status:

```text
RUNTIME VERIFIED
```

---

# 10. Demandes

Operations include:

```text
CREATE
GET
LIST
REVISION
HISTORY
STATUS UPDATE
```

Allowed:

```text
ADMIN
CHASSEUR
SERVICE
```

CLIENT is currently excluded.

Runtime evidence:

```text
No token  → 401
ADMIN     → authorized
CHASSEUR  → authorized
CLIENT    → 403
```

SERVICE is currently code-level verified but not separately runtime-evidenced with a SERVICE test account.

---

# 11. Presentations

Operations:

```text
CREATE
GET
LIST
UPDATE
DELETE
```

Allowed:

```text
ADMIN
CHASSEUR
SERVICE
```

CLIENT is excluded.

Runtime evidence includes:

```text
No token  → 401
ADMIN     → authorized
CHASSEUR  → authorized
CLIENT    → 403
```

Presentation authorization is runtime verified.

---

# 12. Visites

Operations:

```text
CREATE
GET
LIST
UPDATE
DELETE
```

Allowed:

```text
ADMIN
CHASSEUR
```

Not currently allowed:

```text
CLIENT
SERVICE
```

Runtime evidence:

```text
No token  → 401
ADMIN     → authorized
CHASSEUR  → authorized
CLIENT    → 403
```

---

# 13. Mandats

Operations:

```text
CREATE
GET
LIST
UPDATE
DELETE
```

Allowed:

```text
ADMIN
CHASSEUR
```

CLIENT and SERVICE are currently excluded.

Runtime evidence:

```text
No token  → 401
ADMIN     → authorized
CHASSEUR  → authorized
CLIENT    → 403
```

---

# 14. Recommendations

Endpoint:

```text
POST /api/v1/demande-versions/{id}/recommendations
```

Allowed:

```text
ADMIN
CHASSEUR
SERVICE
```

CLIENT is excluded.

Runtime evidence:

```text
No token  → 401
ADMIN     → authorized
CHASSEUR  → authorized
CLIENT    → 403
```

SERVICE is protected at code level but does not yet have separate runtime account evidence.

---

# 15. Biens

The current property endpoints are read-only:

```text
GET /biens
GET /biens/{id}
```

Allowed:

```text
ADMIN
CHASSEUR
CLIENT
SERVICE
```

Runtime evidence includes:

```text
No token  → 401
ADMIN     → authorized
CHASSEUR  → authorized
CLIENT    → authorized
```

SERVICE remains code-level verified.

---

# 16. Public Technical Endpoints

Not every endpoint should require business authentication.

The following remain intentionally public:

```text
/auth/login
/health
/ready
```

Their lack of RBAC protection is therefore deliberate.

Prometheus `/metrics` is treated separately as an infrastructure/observability endpoint rather than as a business API.

---

# 17. Deployed RBAC Inventory

Runtime introspection of the deployed routers established the following state:

| Domain          | Operation     |             RBAC |
| --------------- | ------------- | ---------------: |
| Auth            | login         | Public by design |
| Clients         | create        |                ✅ |
| Clients         | get           |                ✅ |
| Clients         | list          |                ✅ |
| Clients         | update        |                ✅ |
| Clients         | delete        |                ✅ |
| Demandes        | create        |                ✅ |
| Demandes        | revision      |                ✅ |
| Demandes        | get           |                ✅ |
| Demandes        | history       |                ✅ |
| Demandes        | list          |                ✅ |
| Demandes        | update status |                ✅ |
| Biens           | get           |                ✅ |
| Biens           | list          |                ✅ |
| Presentations   | create        |                ✅ |
| Presentations   | get           |                ✅ |
| Presentations   | list          |                ✅ |
| Presentations   | update        |                ✅ |
| Presentations   | delete        |                ✅ |
| Recommendations | generate      |                ✅ |
| Visites         | create        |                ✅ |
| Visites         | get           |                ✅ |
| Visites         | list          |                ✅ |
| Visites         | update        |                ✅ |
| Visites         | delete        |                ✅ |
| Mandats         | create        |                ✅ |
| Mandats         | get           |                ✅ |
| Mandats         | list          |                ✅ |
| Mandats         | update        |                ✅ |
| Mandats         | delete        |                ✅ |
| Health          | health        | Public by design |
| Health          | readiness     | Public by design |

Therefore all currently identified business routers are protected at role level.

---

# 18. Current RBAC Limitation

The current RBAC implementation is deliberately role-level.

For example:

```text
CLIENT
```

does not yet have ownership-based access such as:

```text
CLIENT may access only its own demandes
CLIENT may access only its own presentations
CLIENT may access only its own visites
```

Likewise, CHASSEUR authorization generally represents:

```text
role = CHASSEUR
```

rather than:

```text
this exact CHASSEUR is assigned to this exact client/demande
```

Therefore the correct current security claim is:

> All current business endpoints are protected by role-level RBAC.

The project must **not** claim complete fine-grained resource authorization yet.

---

# 19. PostgreSQL Audit Architecture

Audit persistence uses:

```text
real_estate.audit_log
```

The table existed from the earlier database migration work but initially had no backend integration.

The security workstream connected application business operations to this table.

---

# 20. Audit Table

Important fields:

```text
id_audit
date_evenement
schema_name
table_name
operation
record_id
utilisateur
ancienne_valeur
nouvelle_valeur
contexte
```

Audit values use JSONB for business snapshots.

---

# 21. Audit Database Constraints

Allowed operations:

```text
INSERT
UPDATE
DELETE
```

Database constraint:

```text
operation IN (
    'INSERT',
    'UPDATE',
    'DELETE'
)
```

The audit context must be a JSON object.

Indexes support:

* chronological lookup;
* table lookup;
* business-record lookup.

There are currently no database triggers implementing application audit automatically.

Audit creation is application-driven.

---

# 22. Audit Backend Components

Audit support was implemented through:

```text
src/api/db/models/audit_log.py
src/api/repositories/audit_log.py
src/api/services/audit_log.py
```

Responsibilities are separated as:

```text
AuditLog SQLAlchemy model
          │
          ▼
AuditLogRepository
          │
          ▼
AuditLogService
          │
          ▼
Business Service
```

---

# 23. Audit Transaction Strategy

A fundamental design rule was adopted:

> The business mutation and corresponding audit record must participate in the same database transaction.

Repositories therefore perform persistence/flush behavior without independently committing the audit.

The business service owns the transaction.

Conceptually:

```text
BEGIN
  │
  ├── mutate business record
  │
  ├── create audit record
  │
  └── COMMIT
```

On failure:

```text
ROLLBACK
```

This prevents:

```text
business record without audit
```

or:

```text
audit record without business mutation
```

for the audited transaction.

---

# 24. Direct Presentation CRUD Auditing

Presentation was selected as the first complete business domain for application-level audit integration.

The following operations were integrated:

```text
CREATE → INSERT audit
UPDATE → UPDATE audit
DELETE → DELETE audit
```

The authenticated user's email is propagated from the endpoint to the business service.

---

# 25. Presentation INSERT Audit

A temporary Presentation was created through the authenticated API.

Runtime test:

```text
id_demande_version = 1
id_bien = 13
```

Created:

```text
id_presentation = 30
score_matching = 88.50
statut = PRESENTE
```

Audit result:

```text
operation   = INSERT
record_id   = 30
utilisateur = admin.auth.test@example.com
```

Old value:

```text
null
```

New value contained the created Presentation snapshot.

Context:

```json
{
  "action": "create_presentation",
  "source": "api"
}
```

---

# 26. Presentation UPDATE Audit

The same Presentation was modified.

Before:

```text
score_matching = 88.50
statut = PRESENTE
```

After:

```text
score_matching = 95.50
statut = VISITE
```

Audit operation:

```text
UPDATE
```

The audit record contained:

```text
ancienne_valeur → previous snapshot
nouvelle_valeur → updated snapshot
utilisateur     → admin.auth.test@example.com
```

Context:

```json
{
  "action": "update_presentation",
  "source": "api"
}
```

---

# 27. Presentation DELETE Audit

The temporary Presentation was then deleted through the authenticated API.

HTTP result:

```text
204 No Content
```

Audit operation:

```text
DELETE
```

The audit contained:

```text
ancienne_valeur → final Presentation state
nouvelle_valeur → null
utilisateur     → admin.auth.test@example.com
```

Context:

```json
{
  "action": "delete_presentation",
  "source": "api"
}
```

---

# 28. Direct CRUD Audit Chronology

The database therefore demonstrated the complete sequence:

```text
Presentation 30

INSERT
  ↓
UPDATE
  ↓
DELETE
```

with the same authenticated actor:

```text
admin.auth.test@example.com
```

This proves complete direct Presentation mutation traceability.

Status:

```text
DESIGNED          ✅
IMPLEMENTED       ✅
TESTED            ✅
DEPLOYED          ✅
RUNTIME VERIFIED  ✅
EVIDENCED         ✅
```

---

# 29. Recommendation Audit Gap

After direct Presentation CRUD auditing was completed, a second persistence path was discovered.

The recommendation engine created Presentation records directly through:

```text
PresentationRepository
```

rather than:

```text
PresentationService
```

Initial architecture:

```text
RecommendationService
       │
       ▼
PresentationRepository
       │
       ▼
presentation
```

This meant recommendation-generated Presentation records could bypass the newly implemented audit path.

This was identified as a real security/audit gap rather than being hidden by documentation.

---

# 30. Recommendation Audit Design

The existing recommendation transaction was intentionally preserved.

The service performs Top-N persistence as one transaction.

Therefore it was not blindly changed to call the normal Presentation service.

Instead:

```text
RecommendationService
       │
       ├── PresentationRepository
       │
       ├── flush()
       │
       ├── AuditLogService
       │
       └── commit()
```

was implemented.

The generated Presentation IDs become available after flush, allowing correct audit `record_id` values.

---

# 31. Authenticated Actor Propagation

The recommendation endpoint already had:

```python
current_user: AuthenticatedUser = Depends(
    require_roles(
        "ADMIN",
        "CHASSEUR",
        "SERVICE",
    )
)
```

The endpoint now propagates:

```python
utilisateur=current_user.email
```

to the Recommendation service.

Therefore the recommendation audit identifies the real authenticated application actor.

---

# 32. Recommendation Audit Context

New recommendation-generated Presentations use:

```text
operation = INSERT
```

Context:

```json
{
  "source": "recommendation",
  "action": "generate_recommendations"
}
```

This allows audit consumers to distinguish:

```text
manual/direct API Presentation creation
```

from:

```text
Presentation created by recommendation generation
```

without changing the allowed audit operation vocabulary.

---

# 33. Recommendation Idempotency

The existing recommendation workflow checks:

```text
id_demande_version + id_bien
```

before creating a Presentation.

If the Presentation already exists:

```text
existing presentation reused
```

and no new INSERT audit event is created.

Only genuinely created Presentation records generate audit INSERT events.

Automated tests explicitly verified this behavior.

---

# 34. Recommendation Automated Tests

Recommendation service tests were extended for audit behavior.

Verified:

* new Presentation → audit generated;
* correct authenticated actor;
* correct Presentation snapshot;
* correct context;
* multiple new Presentations → corresponding audits;
* existing Presentation → no duplicate INSERT audit;
* mixed existing/new recommendation behavior;
* transaction flush preserved;
* single final commit preserved;
* recommendation metrics preserved.

Result:

```text
11 passed
```

---

# 35. Recommendation API Tests

Direct endpoint tests were updated to provide an authenticated user and verify propagation of:

```text
admin.auth.test@example.com
```

Result:

```text
4 passed
```

---

# 36. Full Backend Regression

After the complete audit change:

```text
python -m pytest tests/backend -v
```

Result:

```text
135 passed
```

Therefore no backend regression was detected after integrating recommendation auditing.

---

# 37. Deployed Kubernetes State

Runtime deployment inspected:

```text
Namespace: real-estate
Deployment: real-estate-backend
Ready: 1/1
Available: 1
```

Observed image:

```text
gitlab.local:4567/root/chasse_immobiliere/backend:333f5f51
```

Observed pod:

```text
real-estate-backend-c57c8bcc4-hl6d2
```

Node:

```text
k8s-wk-05
```

Restarts:

```text
0
```

---

# 38. GitOps Evidence

Argo CD application:

```text
real-estate-backend
```

Observed state:

```text
Sync:   Synced
Health: Healthy
```

Observed GitOps revision:

```text
f4ef4359058d52d4358582b2fafac89efb1a886c
```

This confirms the inspected backend was managed through the expected GitOps deployment path.

---

# 39. Deployed Recommendation Code Verification

Runtime Python introspection inside the actual backend pod confirmed:

```text
AuditLogService: True
self.audit: True
generate_recommendations audit context: True
utilisateur parameter: True
```

Endpoint introspection confirmed:

```text
current_user.email passed: True
```

This provides deployment-level evidence rather than relying solely on the local source repository.

---

# 40. Recommendation End-to-End Runtime Test

A clean demand version was selected:

```text
id_demande_version = 56
```

Initial state:

```text
presentations_before = 0
recommendation_audits_before = 0
```

The real protected endpoint was called using:

```text
admin.auth.test@example.com
```

Request:

```text
POST /api/v1/demande-versions/56/recommendations?limit=1
```

Response established:

```text
eligible_candidates     = 200
selected_candidates     = 1
created_presentations   = 1
existing_presentations  = 0
```

Generated recommendation:

```text
id_bien             = 11225
reference_externe   = AN-4G1AYBSY
matching_score      = 100.0
rank                = 1
presentation_id     = 31
persisted           = true
```

---

# 41. Recommendation Database Evidence

PostgreSQL contained:

```text
id_presentation      = 31
id_demande_version   = 56
id_bien              = 11225
score_matching       = 100.00
statut                = IDENTIFIE
```

Corresponding audit record:

```text
id_audit       = 7
table_name     = presentation
operation      = INSERT
record_id      = 31
utilisateur    = admin.auth.test@example.com
```

Old value:

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

This proves the complete runtime chain:

```text
Authenticated ADMIN
       ↓
RBAC
       ↓
Recommendation endpoint
       ↓
Deterministic recommendation
       ↓
Presentation INSERT
       ↓
Audit INSERT
       ↓
Authenticated actor recorded
```

---

# 42. Presentation Audit Coverage

Presentation audit now covers both persistence paths.

## Direct API path

```text
CREATE → INSERT audit ✅
UPDATE → UPDATE audit ✅
DELETE → DELETE audit ✅
```

## Recommendation path

```text
Recommendation-created Presentation
        ↓
INSERT audit ✅
```

Therefore the previously identified Presentation audit bypass has been closed.

---

# 43. Secrets Management

Runtime inspection established use of Kubernetes Secrets for application credentials.

Backend configuration uses:

```text
real-estate-postgresql-secret
real-estate-backend-auth
```

MLOps jobs also use Kubernetes secret references.

OpenMetadata uses its corresponding secret configuration.

No plain PostgreSQL password was observed in the inspected deployment manifests.

The project should nevertheless not claim that the following have already been demonstrated:

```text
automatic secret rotation
external secret manager
Vault integration
database encryption at rest
complete secret lifecycle management
```

These remain separate security maturity topics.

---

# 44. Environment File Protection

The local:

```text
.env
```

file was removed from Git tracking and is ignored through:

```text
.gitignore
```

This prevents future normal commits of the local environment file.

This does **not**, by itself, prove that no secret has ever existed in Git history.

No such claim should be made without repository-history evidence.

---

# 45. Container Runtime Security

The backend Docker image creates a dedicated application user:

```text
uid = 10001
gid = 10001
```

and runs:

```dockerfile
USER appuser
```

Runtime verification previously confirmed:

```text
uid=10001(appuser)
gid=10001(appuser)
```

Therefore the backend application process does not run as root.

Status:

```text
IMPLEMENTED       ✅
DEPLOYED          ✅
RUNTIME VERIFIED  ✅
```

Explicit Kubernetes `securityContext` hardening is a separate deferred improvement and must not be claimed as implemented merely because the container runs non-root.

---

# 46. RGPD / Data Minimization

Security work also includes existing privacy-oriented warehouse design.

The warehouse client dimension deliberately excludes direct fields such as:

```text
nom
prenom
email
telephone
```

from analytical exposure.

A controlled source identifier remains available for lineage where required.

Therefore the project contains an implemented example of:

```text
data minimization
```

rather than simply documenting RGPD theoretically.

OpenMetadata governance/tagging complements this architecture.

---

# 47. Authentication Event Auditing

Authentication events are **not yet** stored in the current business audit table.

The existing constraint allows:

```text
INSERT
UPDATE
DELETE
```

Events such as:

```text
LOGIN_SUCCESS
LOGIN_FAILURE
TOKEN_REJECTED
```

do not naturally belong to this vocabulary.

They must therefore not be disguised as CRUD operations.

A future implementation should use either:

```text
migration 007 extending the audit event model
```

or:

```text
dedicated security_event table
```

depending on the final design.

---

# 48. Remaining Business Audit Coverage

Presentation is currently the strongest fully evidenced audited domain.

Other mutable domains still need equivalent analysis and implementation where required:

```text
clients
mandats
demandes
demande revisions/status
visites
```

These should be implemented incrementally rather than claiming global audit coverage prematurely.

---

# 49. Current Security Evidence Matrix

| Security capability                  | Designed | Implemented | Tested | Deployed |                                      Runtime verified |
| ------------------------------------ | -------: | ----------: | -----: | -------: | ----------------------------------------------------: |
| Dedicated application identity       |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Password hashing                     |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| JWT authentication                   |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Login endpoint                       |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Current-user dependency              |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Role-based authorization             |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| ADMIN runtime role                   |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| CLIENT runtime role                  |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| CHASSEUR runtime role                |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| SERVICE role                         |        ✅ |           ✅ |      ✅ |        ✅ | ⚠️ code-level, no dedicated runtime identity evidence |
| Business endpoint RBAC               |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Fine-grained ownership authorization |       ⚠️ |           ❌ |      ❌ |        ❌ |                                                     ❌ |
| Audit database model                 |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Audit repository/service             |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Direct Presentation INSERT audit     |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Direct Presentation UPDATE audit     |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Direct Presentation DELETE audit     |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Recommendation Presentation audit    |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Authenticated audit actor            |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Old/new business snapshots           |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Audit action/source context          |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Authentication-event audit           |       ⚠️ |           ❌ |      ❌ |        ❌ |                                                     ❌ |
| Clients business audit               |       ⚠️ |           ❌ |      ❌ |        ❌ |                                                     ❌ |
| Demandes business audit              |       ⚠️ |           ❌ |      ❌ |        ❌ |                                                     ❌ |
| Mandats business audit               |       ⚠️ |           ❌ |      ❌ |        ❌ |                                                     ❌ |
| Visites business audit               |       ⚠️ |           ❌ |      ❌ |        ❌ |                                                     ❌ |
| Kubernetes Secret consumption        |        ✅ |           ✅ |      — |        ✅ |                                                     ✅ |
| Non-root backend process             |        ✅ |           ✅ |      — |        ✅ |                                                     ✅ |
| Explicit K8s securityContext         |       ⚠️ |    Deferred |      — |        ❌ |                                                     ❌ |
| Warehouse PII minimization           |        ✅ |           ✅ |      ✅ |        ✅ |                                                     ✅ |
| Secret rotation                      |       ⚠️ |           ❌ |      ❌ |        ❌ |                                                     ❌ |
| External secret manager              |       ⚠️ |           ❌ |      ❌ |        ❌ |                                                     ❌ |

---

# 50. Security Test Results

Latest backend regression after RBAC and audit changes:

```text
135 passed
```

Focused recommendation service tests:

```text
11 passed
```

Focused recommendation API tests:

```text
4 passed
```

Earlier dedicated Presentation service/API tests also verified the direct audited CRUD behavior.

The runtime API tests additionally established expected authorization behavior such as:

```text
401 → unauthenticated
403 → authenticated but unauthorized role
2xx → authorized role
```

---

# 51. Security and Audit Evidence Chain

The project can now demonstrate a concrete evidence chain:

```text
Database migration
       ↓
Application identity
       ↓
Argon2 password hash
       ↓
Login
       ↓
JWT
       ↓
AuthenticatedUser
       ↓
RBAC
       ↓
Protected endpoint
       ↓
Business service
       ↓
Business mutation
       ↓
AuditLogService
       ↓
PostgreSQL audit_log
       ↓
Authenticated actor
       ↓
Old/new values
       ↓
Action context
       ↓
Kubernetes runtime verification
```

This is substantially stronger evidence than security documentation alone because the chain has been tested against the deployed application.

---

# 52. Future UI Integration

The planned UI does not require a new security architecture.

It will use the existing backend flow:

```text
Login page
   │
   ▼
POST /auth/login
   │
   ▼
JWT
   │
   ▼
UI sends Bearer token
   │
   ▼
FastAPI authentication
   │
   ▼
RBAC
   │
   ▼
Business action
   │
   ▼
Audit trail
```

For example, when a hunter creates or modifies an audited Presentation through the future UI:

```text
CHASSEUR clicks action
       ↓
UI sends authenticated API request
       ↓
Backend identifies CHASSEUR
       ↓
RBAC authorizes request
       ↓
Business mutation
       ↓
audit_log.utilisateur = authenticated user's email
```

The UI therefore does not need to create audit records itself.

---

# 53. Potential Audit Administration UI

A future ADMIN screen could expose audit history.

Possible fields:

```text
Date/time
Actor
Domain/table
Record ID
Operation
Previous value
New value
Source
Action
```

Access should be restricted.

A normal CLIENT should not receive unrestricted access to global audit history.

CHASSEUR visibility, if implemented, should eventually be scoped to business records they are authorized to access.

---

# 54. What We Can Claim

Based on current evidence, the project can legitimately state:

> The backend implements dedicated application identities, Argon2 password hashing, JWT authentication and role-based access control for all current business routers.

It can also state:

> Authentication and authorization have been runtime verified using ADMIN, CLIENT and CHASSEUR identities, including unauthenticated and unauthorized access scenarios.

For audit:

> The backend implements transactional application-level audit logging using PostgreSQL `real_estate.audit_log`.

And more specifically:

> Direct Presentation INSERT, UPDATE and DELETE operations are runtime audited with authenticated actor identity, previous/new state and operation context.

And:

> Presentation records generated through the recommendation engine are also audited transactionally, closing the previously identified repository-level audit bypass.

For runtime:

> The secured backend and audit implementation have been inspected and exercised on the Kubernetes deployment managed through GitOps and Argo CD.

---

# 55. What We Must Not Claim Yet

The project must not currently claim:

```text
❌ complete fine-grained authorization
❌ CLIENT ownership filtering across all resources
❌ CHASSEUR assignment-level authorization everywhere
❌ complete business audit across every table
❌ login/security-event auditing
❌ SERVICE runtime role evidence
❌ MFA
❌ SSO/federation
❌ Keycloak integration
❌ automatic secret rotation
❌ Vault/external secret manager
❌ proven encryption at rest
❌ explicit Kubernetes securityContext hardening
❌ complete enterprise IAM
```

Keeping these distinctions explicit makes the security evidence more credible.

---

# 56. Overall Status

## Authentication

```text
DESIGNED          ✅
IMPLEMENTED       ✅
TESTED            ✅
DEPLOYED          ✅
RUNTIME VERIFIED  ✅
```

## Role-Based Access Control

```text
DESIGNED          ✅
IMPLEMENTED       ✅
TESTED            ✅
DEPLOYED          ✅
RUNTIME VERIFIED  ✅

Scope: role-level authorization
```

## Direct Presentation Audit

```text
DESIGNED          ✅
IMPLEMENTED       ✅
TESTED            ✅
DEPLOYED          ✅
RUNTIME VERIFIED  ✅
EVIDENCED         ✅
```

## Recommendation Presentation Audit

```text
DESIGNED          ✅
IMPLEMENTED       ✅
TESTED            ✅
DEPLOYED          ✅
RUNTIME VERIFIED  ✅
EVIDENCED         ✅
```

## Global Business Audit

```text
PARTIAL 🟠
```

because other mutable business domains remain to be integrated.

## Fine-Grained Authorization

```text
NOT YET IMPLEMENTED 🟠
```

---

# 57. Conclusion

The security workstream transformed the backend from an essentially functional business API into an authenticated and role-protected application platform.

The implemented chain now provides:

```text
Secure identity
      +
Password hashing
      +
JWT authentication
      +
Role-based authorization
      +
Protected business APIs
      +
Authenticated actor propagation
      +
Transactional business auditing
      +
Old/new state traceability
      +
Kubernetes runtime evidence
      +
Automated regression tests
```

The strongest end-to-end evidence currently exists around the Presentation lifecycle.

Direct Presentation operations have been proven for:

```text
INSERT
UPDATE
DELETE
```

and the recommendation engine has separately been proven to generate audited Presentation INSERT events while preserving its Top-N transaction and idempotency behavior.

The backend regression suite remains green:

```text
135 / 135 tests passed
```

The current security checkpoint should therefore be considered **materially implemented and runtime verified**, while explicitly retaining the remaining work around fine-grained ownership authorization, broader business-domain auditing, authentication-event auditing, and additional security hardening.
