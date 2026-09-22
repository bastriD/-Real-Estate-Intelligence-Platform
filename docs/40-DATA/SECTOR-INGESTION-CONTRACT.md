# Sector ingestion: implementation and rollout

The ingestion DAG accepts optional property and generated-search sectors
through the existing chain. Standard generation is the default; sector-bearing
fixtures are an additional integration-test mode. Migration 017's API and strict matching behaviour
remain unchanged. Migration 018 adds ingestion/warehouse columns; migrations
001-017 must not be edited or replayed.

## Data flow

```text
sector_test only: active real_estate.secteur catalogue (read only)
  -> fixtures/annonces/secteurs.json (portable geographic codes, no database IDs)
  -> generer_annonces.py --secteurs-catalogue ...
  -> recherches.csv + annonces.csv + json/annonce_XXXX.json
  -> MinIO -> downloaded files -> raw -> staging
  -> resolve supplied codes against active canonical sectors
       -> bien.id_secteur
       -> demande_version_secteur
  -> warehouse.dim_bien.secteur_key
     + warehouse.bridge_demande_version_secteur
  -> dbt staging models and reconciliation tests
```

`database/seeds/sector_contract.py` implements identity, resolution and read-only
catalogue export. Codes contain `geo-v1-` followed by SHA-256 of a compact JSON
array of country, city, neighbourhood and postcode, with NFC Unicode
normalization, trimmed whitespace and case folding. IDs are independent of
database sequences. Renaming geographic attributes changes the code: old input
needs explicit reconciliation, not a guessed replacement. Duplicate normalized
canonical identities abort resolution.

The existing `generate_source_data` task checks migration 018 and required
columns in both modes using `sector_contract.py --check-schema`. This read-only
check does not load or export sectors. The task uses the existing PostgreSQL
and S3 secret references. In `sector_test` only, it then exports active French
sectors with neighbourhoods/postcodes and uploads the catalogue with generated
artifacts. There is no second hard-coded catalogue and ingestion creates no sectors.

## Generation modes

In Airflow's trigger form, select the `generation_mode` parameter:

| Mode | Behaviour |
| --- | --- |
| `standard` (default) | Original heterogeneous generator behaviour, including optional coordinates and missing sectors; no catalogue export or catalogue-dependent generation. |
| `sector_test` | Explicit sector-bearing search/property fixtures generated from the active catalogue. |

Equivalent trigger configuration is `{"generation_mode": "standard"}` or
`{"generation_mode": "sector_test"}`. Unsupported modes fail before generation.
Both retain five searches and 1,000 announcements to satisfy existing batch DQ.
The parameter is passed as a pod environment variable, not interpolated as shell
code. Schema readiness is checked before resetting the pod's generated files.

Model training, dataset validation/splitting, comparison, MLflow, API matching,
warehouse projection and the MLOps release jobs remain part of the project.
These modes select fixture generation only; they do not remove those extensions
or modify frozen training splits. Switching modes produces a different dataset,
so follow the existing dataset validation/split workflow for training.

New synthetic searches choose one sector. Their generated positive announcements
carry the same code. This is a generation rule: production loaders independently
resolve each property's supplied code, never copying a customer's preference
onto it. API searches retain support for multiple acceptable sectors.
Sector-aware fixtures omit random city-centre coordinates because the catalogue
does not supply neighbourhood boundaries. Addresses remain synthetic test data.

## Compatibility and rejection rules

- Legacy CSVs without a code remain readable and unmapped. City/postcode alone
  cannot establish precise neighbourhood membership.
- Standalone generation without `--secteurs-catalogue` retains historical
  behaviour and prints that it supplies no sectors. The DAG supplies a catalogue
  only in `sector_test`. An explicitly empty catalogue fails.
- Raw preserves the code as text; staging carries its cleaned value. OLTP loaders
  reject unknown/inactive codes and conflicting city/postcode before their own
  writes commit. Invalid explicit evidence does not become a city-only match.
  This is fail-fast loading, not a new quarantine subsystem.
- Property assignment follows the location UPSERT in the same transaction.
  Migration 017 invalidates an old mapping first; resolved source evidence may
  then assign the new one. Missing evidence preserves reviewed mappings only
  when location is unchanged. Changed location still invalidates them.
- Identical search-sector retries are idempotent. A changed sector on an already
  linked generated version is rejected; generate a new search reference. Legacy
  retries do not erase existing version-sector links.
- Warehouse property sectors represent current geography, with zero for unknown.
  Search alternatives retain version identity. The next load removes obsolete
  links and resets invalidated property mappings. General warehouse SCD history
  is not implemented by this change.
- Existing properties are not automatically backfilled. Use migration 017's
  reviewed sector-assignment API when evidence exists. Generate a new batch for
  fully sector-bearing synthetic fixtures; do not infer neighbourhoods from
  historical random coordinates.

## Rollout on the trusted runner

1. Commit/push through the normal user-controlled process.
2. Ensure raw/staging schemas, warehouse 003 and migration 017 exist; run manual
   `database:migrate-018`. The SQL is transactional; the CI job safely skips an
   already registered 018. Airflow never applies migrations automatically.
3. Build/publish the data image and DAG through existing jobs. Task IDs, manual
   schedule and image digest pinning are preserved. Missing prerequisites stop
   the generation task before generation/upload.
4. Run a standard batch and an explicit `sector_test` batch. OLTP DQ includes `database/tests/021_ingestion_sectors.sql`
   for that batch, checking search/property sector agreement and reporting the
   number of checked rows. Zero sector-bearing rows are expected for standard
   generation, but are not proof that the sector-test path was exercised.
5. `database:test-ingestion-sectors` runs the same read-only assertions across
   all sector-bearing staged rows. dbt tests reconcile operational and analytical
   property/search links, including missing and obsolete links.
6. Verify matching with two neighbourhoods sharing a postcode: the chosen sector
   is eligible, a different or unmapped sector is excluded. Other hard constraints
   (status, city, type, price and optional surface) still apply.

Other findings in `DATABASE-CONTRACT-AUDIT.md` remain separate work, including
observation-batch grain and general property-status replay. This rollout does
not repair historical warehouse values or frozen training datasets.

## Validation scope

Offline tests exercise actual CSV/JSON generation, raw loader parameter mapping,
transformations, staging bindings, resolution, assignment ordering, retries,
rejections, catalogue export, prerequisites and CI/Docker wiring. Existing API
and matching regressions remain part of the verification suites.

The standard generator is retained as the baseline for the starter pack's
intentionally heterogeneous data. Sector mode is our documented extension,
not an assignment requirement. See the [official generator instructions](https://github.com/DiginamicFormation/Fil-Rouge-EISI-Data-IA-26-D04-StarterPack/blob/main/outils/Readme.md).

No deployed database, migration, Airflow run or dbt/PostgreSQL execution was
performed locally. The runtime SQL/dbt checks are supplied for the trusted runner;
local mocks do not establish PostgreSQL execution success.
