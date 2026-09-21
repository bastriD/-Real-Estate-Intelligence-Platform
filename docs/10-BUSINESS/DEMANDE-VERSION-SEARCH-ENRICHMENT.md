# Migration 017 — Versioned search criteria and geography

Repository integration reviewed on 2026-09-21. Migration execution and deployed
runtime verification remain pending with the owner.

## Review conclusion

The proposed relationship `DemandeVersion N:N Secteur` is appropriate: search
geography belongs to the exact criteria version, independently of mandate
coverage. Multiple sectors are alternatives, not simultaneous requirements.
The 17 descriptions correspond to the legacy fixture imported by migration 002;
legacy mandate 13 was excluded there. Version 1 is enriched, not later business
revisions. Original descriptions are preserved and exposed on version reads.

The integration strengthens the submitted migration:

- Exact reference/description checks precede enrichment. A count of 17 alone
  would not detect a changed description or an unexpected replacement row.
- Already structured legacy V1 rows cause a rollback instead of being silently
  overwritten. Investigate such a failure before adapting the reviewed backfill.
- Every expected precise sector mapping is checked (13 associations), including
  the two alternatives for Écusson / Beaux-Arts. Missing/ambiguous sectors fail
  the migration. Broad city names do not create invented neighbourhood matches.
- T2/T3/T4/T5 → Appartement is retained as an explicit **project vocabulary
  convention**, not proof that the original text specifies dwelling type.
- Property geography was absent. Migration 017 now also adds nullable
  `bien.id_secteur`, its FK/index and an ingestion-safe invalidation trigger.
  No property assignments are fabricated from postcode, address text or legacy
  mandate coverage. Existing rows remain unmapped until reviewed.

This remains a one-time, reviewed legacy backfill, not a general natural-language
parser. It is deliberately strict about the legacy baseline and migration 016.
Applied migrations 001–016 are unchanged. The migration is transactional.

## Backend contract

`secteur_ids` is an optional list on existing demande create/revision payloads
and version responses. It defaults to `[]`, accepts up to 100 distinct positive
IDs, and requires existing active canonical sectors. When `ville` is supplied,
every chosen sector must belong to that city. Without a city, explicit sectors
can represent alternatives across cities.

Existing revisions are complete criteria replacements, not partial patches.
Therefore omitting `secteur_ids` on a revision means `[]`; callers retaining
geography must resubmit it. Previous versions retain their own associations.
No new permissions to alter another client's demande are introduced; existing
ownership, authorship and role checks remain in the existing endpoints.

Version reads include `description_recherche_legacy` as optional read-only
source evidence. A newly created revision does not copy or rewrite the old
version's legacy description.

`GET /api/v1/secteurs` lists active canonical sectors for authenticated users.
`PUT /api/v1/biens/{bien_id}/secteur` is ADMIN-only:

```json
{"id_secteur": 3}
```

The sector must exist, be active and belong to the property's known city.
`{"id_secteur": null}` clears an assignment. The field is required, preventing
an accidentally empty request from clearing it. Property reads expose the
current `id_secteur`. Assignment locks the property and commits the existing
audit-log event atomically; actor identity comes from authentication.

When ingestion changes address, city, postcode or coordinates, the database
clears an existing assignment and audits `invalidate_bien_secteur` in the same
transaction. Price-only updates and unchanged locations retain it. The trigger
covers existing ingestion SQL without requiring a second ingestion path or an
updated data-loader image. SQL privileges must permit its audit INSERT, as with
the current application database role; verify in the owner's SQL/runtime checks.

## Matching behaviour

| Criterion | Behaviour |
| --- | --- |
| Listing availability | Only `ACTIF`, unchanged |
| City | Existing case-insensitive equality when specified; required unless explicit sectors are supplied |
| Property type / maximum budget | Required and filtered as before |
| Minimum surface | Filtered when specified; absence no longer blocks matching or invents a value |
| Sectors | `bien.id_secteur = ANY(selected IDs)`; alternatives; unknown property sectors excluded |
| Rooms / bedrooms / DPE | Existing ranking signals retained, not newly turned into hard exclusion rules |
| Flexible preference text | Preserved as JSON; “terrasse ou jardin” is not split into two mandatory booleans; no new NLP scoring claimed |

The shared operational matching repository loads geography from the requested
version. API recommendations, evaluation, training dataset construction and
comparison use that repository. Searches without sectors retain city-based
retrieval. Generated staging searches have no invented sector assignments or
label changes. Feature names, scoring weights, model feature vectors and split
contracts remain unchanged. Deterministic MLflow parameters now include the
sector list so evaluation criteria are visible.

**Expect no neighbourhood-specific results until relevant properties have
reviewed assignments.** Postcodes are not neighbourhood identifiers. This
behaviour avoids presenting unverifiable location matches as compliant.

## File map

| Layer | Main files |
| --- | --- |
| Database | `database/migrations/017_demande_version_search_enrichment.sql`, `database/tests/020_demande_version_search.sql` |
| SQLAlchemy | `src/api/db/models/secteur.py`, `demande_version_secteur.py`; extended `demande.py`, `bien.py` |
| Pydantic | `src/api/schemas/secteur.py`; extended `demande.py`, `bien.py` |
| Persistence | `src/api/repositories/secteur.py`; eager version-sector reads in `demande.py`, property locking in `bien.py` |
| Services | `src/api/services/demande.py`, `secteur.py` |
| API | Existing demande endpoints consume updated schemas; `src/api/api/v1/endpoints/secteurs.py`, router registration |
| Matching | `src/ai/matching/repository.py`, `mlflow_tracking.py` |
| CI | `.gitlab/ci/database-search.yml`; `scripts/ci/database/migrate-017.sh`, `test-demande-version-search.sh`, `check-search-schema.sh` |
| Tests | `tests/backend/test_demande_secteurs.py`, `test_secteur_api_service.py`, `tests/ai/test_matching_secteurs.py`, `tests/ci/test_search_enrichment_ci.py` |

The new CI component inherits `.database-operation` and keeps its manual,
blocking, serialized database controls. Backend publication and all five
matching workloads check migration 017 before starting. These checks are
read-only and do not apply migrations. Existing change filters already cover
shared CI scripts; database validation also selects the new component.

## Verification and rollout

Executed offline using the existing review environment:

```sh
python -m pytest tests/backend tests/data tests/ai/test_candidate_availability.py --cov=src/api --cov-fail-under=80 -q
python -m pytest tests/ci tests/ai -q
git diff --check
```

Observed: 618 backend/data tests passed, 3 existing opt-in PostgreSQL tests
skipped, API coverage 86.87%; 1,623 CI/AI tests passed. Tests cover payloads,
version isolation, rollback paths, API roles, matching query construction,
optional-surface scoring, baseline source checks and stubbed release guards.
These do not establish live PostgreSQL migration or runtime success.

Owner rollout:

1. Commit/push and inspect CI validation.
2. Run `database:migrate-017` after 016, then
   `database:test-demande-version-search`. Test 020 uses transaction-scoped
   fixtures and rolls back business mutations; sequences may advance.
3. Continue/retry backend publication and matching jobs through the existing
   GitLab → Registry → lab-gitops → Argo CD → Kubernetes path.
4. Verify catalogue visibility; create/revise a scoped demande with sector IDs;
   check both versions retain their distinct criteria; verify foreign-owner
   access remains denied and invalid sectors fail.
5. Assign known properties through the ADMIN endpoint. Verify either selected
   neighbourhood matches, unrelated/unmapped properties do not, city-only
   searches still work, missing surface is allowed, and audit rows persist.
6. Inspect ingestion location-change invalidation and subsequent reassignment
   in a controlled owner-approved runtime scenario.

No database container, deployment, runtime DB connection, commit or push was
performed by Codex for this integration. Migration 017 is **not claimed applied**.
