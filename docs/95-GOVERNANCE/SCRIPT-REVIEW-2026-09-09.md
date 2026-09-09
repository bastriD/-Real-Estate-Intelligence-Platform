# Script review — 9 September 2026

## Scope and result

Reviewed Python, SQL, and CI wiring across API services, matching, ingestion, warehouse, observability, and governance. This is a targeted logic/structure review, not a claim that every branch or external integration is validated.

The review began at `d43ea13`. Commit `3368624` (request endpoint authorization) arrived during the review and was preserved. Final tests include that commit and the working-tree fixes below. No cluster, production database, GitOps state, or external metadata service was changed.

Four defects were reproduced and fixed. Further findings are recorded below; the review does not mark them resolved.

## Fixed defects

| Priority | Defect and consequence | Correction |
|---|---|---|
| P1 | Migration 005 allows `demande.id_mandat = NULL`, but ORM/input/output schemas required an integer. Generated requests could fail API serialization, and API creation still required an already-signed mandate. | Made the ORM and schemas nullable; skip mandate lookup only when absent. Explicit unknown mandate IDs remain rejected. |
| P1 | Matching filtered on `statut IS NOT NULL`, admitting sold, expired, and unavailable properties. | Operational candidate retrieval now requires `ACTIF`, matching the database status vocabulary. |
| P2 | API database URLs concatenated credentials directly. Special characters could change URL parsing and prevent connection creation. | Construct and encode the SQLAlchemy URL through `URL.create`. |
| P2 | RAW numeric parsing accepted infinity or raised exceptions on NaN/infinity, potentially aborting a batch instead of recording a quality error. | Decimal and integer parsing reject non-finite values before comparisons/conversion. |

Changed implementation files:

- `src/api/db/models/demande.py`
- `src/api/schemas/demande.py`
- `src/api/services/demande.py`
- `src/ai/matching/repository.py`
- `src/api/core/config.py`
- `database/seeds/transform_raw_to_staging.py`

Added regression tests under `tests/backend/test_review_regressions.py`, `tests/ai/test_candidate_availability.py`, and `tests/data/test_numeric_parsing.py`. Updated the backend CI job and change triggers to include these tests.

The availability regression executes the actual candidate SELECT against an in-memory SQLite table with four property statuses. It demonstrates predicate behavior; it does not establish PostgreSQL compatibility or deployed availability. Pre-mandate tests verify schema behavior and the service's mandate-validation branch, not a live database transaction.

## Open findings

### P1 — Authorization remains incomplete

At `3368624`, client and request endpoints have role dependencies. Mandates, presentations, visits, and recommendations still lack equivalent authentication dependencies, and there is no global application guard. Request role checks also do not constrain access to the requesting hunter's own resources. Request authors are accepted from payload IDs and checked for existence rather than bound to the authenticated identity.

Evidence: `src/api/api/v1/router.py`, endpoint modules, `src/api/core/dependencies.py`, and `src/api/services/demande.py`.

Next action: finish the role/resource matrix, enforce ownership and trusted authorship, and test through HTTP with missing credentials, unauthorized roles, and another hunter's IDs. Preserve the newly added role checks.

### P1 — Ingestion can overwrite a historical request version

`database/seeds/load_staging_recherches_to_oltp.py:228` selects a version by `source_recherche_ref`; line 246 then updates its criteria and ingestion batch in place. It does not require that version to remain active. If a generated request was subsequently revised through the API, a later ingestion can rewrite its original inactive version, altering the criteria behind existing presentations and evaluation evidence.

Next action: distinguish an unchanged retry from changed source data. Preserve existing version content; create a new version for a real change or explicitly freeze synthetic fixtures once they are used as evidence. Coordinate this with the unique source-reference constraint from migration 005.

### P2 — Combined list filters silently discard criteria

`src/api/services/bien.py:21` returns on city before considering status/type. `src/api/services/presentation.py:48` returns on request-version ID before considering property ID. A request supplying both parameters does not narrow the result as its shape suggests.

This behavior was reproduced for properties. Existing tests explicitly encode filter precedence, so this is also a contract/test-design issue. Decide whether the API should combine predicates (recommended) or reject mutually exclusive parameters, then update both services and tests.

### P2 — Explicit null updates can raise unhandled exceptions

`PresentationUpdate(statut=None)` is accepted by Pydantic, but `src/api/services/presentation.py:121` accesses `.value` on `None`. This was reproduced as `AttributeError`. The same pattern appears in client/visit updates; mandate updates also accept null values for fields later used in comparisons or enum conversion. A null client email is converted to the literal string `"None"`.

Next action: distinguish omitted fields from explicit null. Reject null for non-nullable columns with input validation; preserve clearing of legitimately nullable fields. Add HTTP regressions for 422 responses rather than server errors.

### P2 — Split validation accepts fractional labels

`src/ai/matching/dataset_split.py:63` casts labels to integers before checking membership in `{0, 1}`. A dataset containing 0.4 and 1.4 per group successfully passed `create_group_aware_split` in a reproduction. The returned partitions still contained the invalid fractional labels.

Next action: validate original numeric values before conversion and check other training/evaluation entry points for the same truncation pattern.

### P2 — Pipeline connection strings still concatenate unescaped credentials

The API URL defect is fixed, but ingestion scripts have a separate libpq connection-string pattern: e.g. `database/seeds/transform_raw_to_staging.py:74` and `load_staging_recherches_to_oltp.py:61`. Passwords containing spaces, quotes, or backslashes can break those strings.

Next action: use psycopg keyword arguments or `make_conninfo` consistently across loaders; test round-trip credential parsing with synthetic special-character inputs.

### P2 — Six-month mandate semantics remain unenforced

The schema explicitly defers the rule and `MandatService._validate_dates` only checks ordering. Arbitrary durations can be accepted, with no explicit renewal history. This predates the new remuneration calculation but directly affects eligibility.

Next action: settle calendar-month and renewal semantics, then enforce them across writes. Do not rewrite already-applied migrations.

### P2 — Data-quality counts are declared rather than observed

`observability/metrics/dq_runner.py` hard-codes per-layer check counts. A successful SQL process reports all configured checks passed; a failed process reports exactly one failure and zero passes regardless of which checks executed. These are not measured per-check results and may mislead dashboards if interpreted that way.

Next action: either expose clearly named batch-level status only or collect actual check outcomes and derive counts from them.

## Verification

- Existing core suite before fixes: **194 passed** (two MLflow-dependent test modules initially excluded while installing dependencies).
- New regression cases before fixes: **10 failed, 4 passed**, reproducing the four defect categories above.
- Full backend, AI, and data suite after fixes: **217 passed**, **83.09% coverage of `src/api`**, exceeding the existing 80% gate.
- Updated CI selection executed locally: **145 passed**, **83.09% backend coverage**.
- Parsed **103 Python files** with `ast.parse` and **14 CI YAML files** with PyYAML; `git diff --check` passed.
- Seven dependency/API deprecation warnings remain; no test failures.

Tests used Python 3.12.14 in an isolated, ignored `.venv-review` environment. Test database variables pointed to loopback port 1 and dummy credentials; no live database was used. Dependencies were installed from the repository's allowed ranges, so these results are not a guarantee for an older deployed dependency set. SQL migrations, the complete Airflow DAG, OpenMetadata calls, and warehouse loads were inspected selectively but not executed.

Saved JUnit/coverage artifacts: `docs/evidence/03-BC03/C6-Tests-Executes/script-review-2026-09-09/`.

## Practical limits of the changes

The pre-mandate fix requires migration 005 to be applied, as intended by the existing ingestion design. It does not implement later mandate attachment or customer ownership. Excluding unavailable properties changes candidate sets, so deployed matching metrics should be regenerated after rollout rather than compared as though the selection policy were unchanged. No commit or deployment was performed.
