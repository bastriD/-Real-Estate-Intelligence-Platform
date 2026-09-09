# Visite audit — local implementation evidence

Base commit: `333f5f5`, plus the uncommitted Visite audit changes.

Status: **IMPLEMENTED / LOCALLY TESTED**. Deployment and PostgreSQL runtime verification are pending.

The create, update and delete endpoints pass the authenticated user's email into VisiteService. Each mutation writes an INSERT, UPDATE or DELETE audit row through the existing AuditLogService and the same SQLAlchemy session, before the business commit. Update/delete capture the prior state. Snapshots serialize dates to ISO strings and copy photo lists. Audit exceptions roll back the session; existing role restrictions and response behavior remain in place.

Local Python 3.12.14 results:

- Focused Visite suite: **28 passed**.
- Full configured CI test selection: **167 passed** (157 backend, 9 data, 1 candidate-availability test).
- Backend coverage: **85.24%**, above the 80% gate.
- Seven existing deprecation warnings; no failures. `git diff --check` passed.

Command (with dummy database settings pointing to loopback port 1 and a test JWT secret):

```text
python -m pytest tests/backend tests/data tests/ai/test_candidate_availability.py --cov=src/api --cov-fail-under=80
```

Artifacts alongside this note contain focused and full JUnit reports plus coverage XML. The service tests use a mocked SQLAlchemy session and actual audit objects; HTTP tests override the current-user and business-service dependencies. They verify snapshots, actor propagation, commit ordering, rollback calls and role rejection. They do not prove persistence/rollback in PostgreSQL or live JWT behavior.

Next: normal GitLab CI → GitOps → Argo CD delivery, then controlled Visite CRUD and PostgreSQL audit verification. No schema migration is needed. Existing Presentation and Recommendation audits were not changed.
