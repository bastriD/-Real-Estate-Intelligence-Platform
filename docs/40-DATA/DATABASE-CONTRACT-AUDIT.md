# Database and ingestion contract audit

Reviewed: 2026-09-22. Status: findings and proposed corrections, **not implemented**.

Follow-up: sector ingestion/projection and dbt property-file version normalization
have since been implemented in the working tree. See
[the sector contract and rollout](SECTOR-INGESTION-CONTRACT.md). Other findings
below remain open; the audit's original validation describes the pre-fix state.

This audit compares repository definitions and consumers. It does not establish
which migrations are applied to the deployed database. No database connection,
migration, ingestion, deployment, commit or push was performed.

## Implemented data path

```text
generator -> MinIO -> raw -> staging -> real_estate (OLTP)
                                         |
                                         v
                                     warehouse -> dbt staging views -> marts
```

- `database/migrations/001_initial_schema.sql` plus subsequent migrations define
  the operational schema. Migration 017 adds version-sector links and property
  sector mapping; it does not extend the warehouse.
- `database/migrations/003_warehouse_schema.sql` and
  `009_mandat_lifecycle_warehouse.sql` define the warehouse used by its loader.
- `database/oltp/003_raw_ingestion_schema.sql` and `004_staging_schema.sql` define
  ingestion schemas through separate manual CI jobs. Their numeric prefixes
  are not positions in the migration sequence.
- `database/seeds/` contains executable generators and ingestion/load programs,
  not just static reference-data seeds.
- `database/olap/load_warehouse.py` loads analytical dimensions and facts.
- `pipelines/dbt/models/staging/` contains views over warehouse tables. This is
  different from the PostgreSQL `staging` ingestion schema.
- `pipelines/airflow/real_estate_ingestion_dag.py` orchestrates these operations.
  The data image explicitly copies individual entrypoints and SQL checks in
  `deploy/docker/Dockerfile.data-pipeline`.

## Confirmed discrepancies

P1 means data corruption/misattribution or a valid operational input preventing
the load. P2 means conditional failure, incomplete analytics or misleading
contracts. Priorities do not assert that a triggering row exists in production.

| Priority | Contract and evidence | Effect and required correction |
| --- | --- | --- |
| P1 | `load_warehouse.py:292-360`: `fact_annonce` joins staging using only the property reference, and takes prices, surfaces and dates from current OLTP values. It never reads `INGESTION_BATCH`. | A reference reused across sources or batches can attach the wrong batch or values. A delayed warehouse load can assign today's price to an older observation. Load generated observations from valid rows of the selected batch, with explicit source identity and stable collection timestamps. Keep the non-generated source path explicit. |
| P1 | `load_staging_to_oltp.py:281-301`: every conflict sets `statut = 'ACTIF'` and `date_collecte = CURRENT_TIMESTAMP`. | Replaying a generated property that was sold or withdrawn reactivates it for matching and changes collection time. Preserve business lifecycle state and use an explicit, stable observation timestamp. Specify how out-of-order batches should behave. |
| P1 | `load_warehouse.py:545-548`: presentation client comes from the mandate although migration 013 establishes `demande.id_client`. | A customer-owned request without a mandate becomes the UNKNOWN customer in the warehouse. Join the client through `d.id_client`; keep hunter attribution a separately defined rule. |
| P1 | `load_warehouse.py:621-622`: payment hunter comes from the mandate, ignoring migration 010's frozen `paiement.id_chasseur_beneficiaire`. | Revenue/remuneration can be attributed to the wrong hunter, or to a hunter when no internal beneficiary exists. Use the payment beneficiary, reserving any mandate fallback for explicitly identified legacy records. |
| P1 | Migration 001 permits `surface_min >= 0`; API criteria also permit zero. Migration 003 requires `surface_min > 0`. | A valid operational request with zero minimum surface aborts the warehouse transaction. Align the warehouse constraint in a new forward migration, not by rewriting 003. |
| P2 | `database/olap/001_warehouse_schema.sql` conflicts with migration 003: `full_date` versus `date_complete`, `warehouse_loaded_at` versus `dw_loaded_at`, and different dimension layouts. | Applying this alternate DDL creates a schema incompatible with the active loader. Retire its executable DDL and point to the canonical migration chain. It is not the DDL used by the current warehouse migration CI job. |
| P2 | Migration 003's localisation uniqueness is `(pays, code_postal, ville)` with nullable postcode; the loader relies on `ON CONFLICT` for idempotence. | Repeated NULL-postcode locations can accumulate because ordinary PostgreSQL uniqueness does not equate NULLs. Deduplicate with fact-FK remapping, then add null-safe uniqueness in a forward migration. The city mart's unconditional postcode `not_null` test also contradicts the nullable upstream contract. |
| P2 | `load_dim_source` and `load_dim_bien` only insert missing current members. They never update changed attributes or create/close history. | Status, DPE and descriptive attributes become stale. Select and implement an explicit current-state or historical-dimension policy. Current marts filtering `is_current = true` would discard historical fact rows if proper history were introduced without updating those joins. |
| P2 | `load_bridge_mandat_secteur` only inserts links. | Removing an operational link leaves stale analytical geography. Reconcile removed links as well as additions within the load transaction. |
| P2 | Migration 017's `demande_version_secteur` and `bien.id_secteur` are absent from warehouse loading; `dim_demande_version` also omits generated-search lineage and explicit customer ownership. | Analytics cannot reconstruct the complete criteria used by matching. Add a version-sector bridge, property-sector mapping and the necessary owner/origin/lineage fields; do not substitute mandate sectors for version criteria. |
| P2 | Market marts use `count(distinct fa.reference_externe)` while OLTP property identity is `(id_source, reference_externe)`. | Different sources sharing a reference are undercounted in cross-source aggregates. Count the complete business identity, taking the chosen dimension-history policy into account. |
| P2 | `transform_raw_to_staging.py` accepts zero price and surface; SQL check 005 rejects both. Staging `type_bien` allows 80 characters whereas operational `type_bien` allows 50. | The validator can accept values that downstream checks or writes reject. Align validation and quarantine policy with the target columns and explicitly choose whether zero-price advertisements are admissible. |
| P2 | `load_staging_recherches_to_oltp.py:221-288` finds a version by source reference alone, then overwrites criteria and batch in place. | A reused source reference can rewrite the evidence associated with existing presentations/training data. Identical retries should be no-ops; changed input needs rejection or a new version with preserved lineage. |
| P2 | DAG generation clears local fixtures, generates random references, and uploads under a run-derived batch. The raw loader skips a previously loaded file/batch on existence alone. | Clearing and rerunning generation for an already imported run can replace its MinIO input while PostgreSQL retains the old dataset. Persist/check a content manifest and reuse completed batch artifacts; existence alone is not content idempotence. |
| P2 | The DAG exports a batch for warehouse loading, but its warehouse DQ task passes no batch and SQL 007 contains no batch reconciliation. | A successful gold check does not prove this run's observations reached the warehouse. Add batch-scoped identity, value and count reconciliation, in addition to global invariants. |

## Additional drift and coverage gaps

- The two operational SQL examples (`database/oltp/001_operational_queries.sql`
  and `002_explain_analyze.sql`) do not implement the current matching contract.
  They allow unknown price/surface under bounded criteria, apply hard room/DPE
  restrictions and omit version sectors. The actual candidate repository uses
  explicit sector alternatives and different hard-filter rules. Update examples
  and their query tests together; do not change matching to imitate old examples.
- `pipelines/dbt/models/staging/sources.yml` omits the already implemented
  `warehouse.fact_mandat_periode` and describes demands as mandate-dependent.
  Its operational catalogue predates several migrations. Missing models for
  offers, sales and invoices are analytical coverage gaps, not proof that the
  operational implementations are broken.
- `pipelines/dbt/models/marts/schema.yml` declares `version: 3`, unlike the
  other property files. dbt documents only `version: 2` when that optional tag
  is supplied. Normalize this and run the pinned dbt 1.9 parser; no dbt runtime
  was available in the review environment to reproduce its exact behaviour.
  Reference: https://docs.getdbt.com/reference/project-configs/version
- Migration 003 seeds dates only for 2020-2035, and SQL 007 requires exactly
  5,844 rows. Staging permits publication dates from 2000. An older accepted
  date can therefore fail a warehouse date FK. Test coverage of referenced
  dates, not a permanently fixed dimension row count.
- Raw/staging checks require five generated searches and 1,000 advertisements;
  these agree with today's DAG generator arguments. This is fixture-specific
  validation, not a general business invariant. Do not apply those counts to
  real customer requests or other ingestion sources.
- The DAG has no read-only schema prerequisite check before ingestion. Manual
  migrations and a newer pipeline image can therefore be out of sync. Add a
  readiness gate for the actual required tables/columns/migrations; it should
  not run migrations automatically.
- `scripts/ci/warehouse/validate.sh` greps for table names in migration 003. It
  cannot establish compatibility among DDL, loader SQL, dbt and data values.
  SQL 007 checks useful counts/constraints but does not check the ownership,
  beneficiary, sector or observation-value contracts above.

## Correction order and acceptance cases

1. Preserve migrations 001-017. Consolidate the schema entrypoint and prepare a
   forward migration (018 if still available) for warehouse constraints and
   search-sector projection. Include safe reconciliation of existing rows.
2. Fix loader grain, batch lineage, ownership and beneficiary attribution;
   protect ingestion replay and operational lifecycle state. Decide dimension
   history semantics before changing fact/dimension joins.
3. Align transformation rules, SQL DQ and dbt sources/tests/marts. Extend Docker
   copies and CI changes filters whenever entrypoints or modules are added.
4. Add the DAG readiness gate and batch-specific warehouse reconciliation while
   preserving existing task IDs, deployment controls and the pinned image flow.
5. Validate on the user's trusted runtime after reviewing and applying the
   forward migration. Do not silently rebuild historical facts from current
   OLTP prices: reconcile against retained raw/staging observations first.

Required regression scenarios: two sources sharing one reference; two batches
with different prices; delayed and repeated loads; sold-property replay; changed
input under an existing batch; no-mandate customer presentation; beneficiary
different from mandate hunter; no internal beneficiary; minimum surface zero;
NULL postcode; dates outside the seeded calendar; changed DPE/status; removed
sector links; multiple acceptable search sectors and unmapped property sectors.

## Validation performed

- `.venv-review/Scripts/python.exe -m pytest tests/data tests/ci -q`:
  **1,545 passed**. These existing tests passing does not validate the missing
  cross-layer contracts or execute PostgreSQL SQL checks.
- Direct, in-memory call to `transform_annonce` with otherwise admissible
  metadata and `prix='0', surface='0'` returned `quality_valid=True` and no
  errors. SQL 005 explicitly rejects those values.
- No live schema introspection, SQL DQ execution, dbt execution or Airflow run.
  No application, migration or pipeline implementation was changed by this audit.
