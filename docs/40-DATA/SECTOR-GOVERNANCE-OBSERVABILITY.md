# Sector governance and observability

The [sector ingestion contract](SECTOR-INGESTION-CONTRACT.md) also applies to
OpenMetadata and Grafana. Standard generation permits missing sectors.
`sector_test` supplies explicit catalogue geography; it does not guarantee a
100% matching score. Generation mode is not persisted in the current tables.

Governance definitions describe `secteur_code`, optional property sectors and
versioned search-sector alternatives, their lineage, ownership and privacy.
Search-version identifiers remain confidential indirect identifiers. The market
data product includes the sector dimension, not customer search-sector bridges.
Quality metadata references the two SQL assertions in `021_ingestion_sectors.sql`
and dbt's `sector_projection_reconciles.sql`; it does not execute those tests or
claim a historical pass count. The DQ runner now counts 16 OLTP assertions.

The existing Business KPIs & Platform dashboard adds current property counts
with and without sectors and their coverage percentage. Unknown property member
0 is excluded; an empty inventory has no percentage. Missing sectors are neutral.
The existing Data Quality dashboard adds live property/search projection
discrepancy counts and explicit sector-code counts for the latest staging batches.
These are snapshots: discrepancies can reflect a pending warehouse refresh.
Batch code presence does not identify generation mode. Existing dashboard UIDs,
titles, panels and model-training behavior are preserved.

## Rollout and verification

1. Apply migration 018 using the existing migration workflow, then load/refresh
   warehouse projections and run dbt, including its reconciliation test.
2. Refresh OpenMetadata database/dbt ingestion so the new tables and columns
   exist before applying the governance definitions through the existing job.
3. Publish the existing Grafana dashboards using the existing GitOps workflow.
   New SQL panels require migration 018 and the configured PostgreSQL datasource.
4. Verify both standard and sector_test ingestion on the trusted runner, inspect
   SQL/dbt results and Grafana query permissions, and confirm the catalogue assets.

Offline verification: `python -m pytest tests/ci tests/data tests/ai -q`.
These tests validate configuration contracts, not live database queries or
OpenMetadata/Grafana deployment. The user performs commit, push and runtime checks.
