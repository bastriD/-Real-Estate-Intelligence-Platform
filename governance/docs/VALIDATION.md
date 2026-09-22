# Governance configuration validation

Run from the repository root:

```sh
python governance/scripts/validate_config.py --repository .
python -m pytest tests/ci/test_governance_contracts.py -q
```

The existing `governance:validate` job runs this preflight. Changes to database
definitions and dbt also select validation, because they can invalidate metadata.
The existing `scripts/main.py` entrypoint validates configuration before reading
credentials or making OpenMetadata calls. No deployment command has changed.

Every enabled operation must supply its required collections and typed record
fields. Validation rejects duplicate JSON keys/record identifiers, escaping file
paths, unknown tags, glossary terms, owners, domains and quality-domain references.
CI also checks table references against repository SQL definitions and dbt
sources/models. This is a repository inventory, not proof of live deployment.
OpenMetadata asset resolution remains a runtime responsibility.

`tagging/real_estate_tags.json` defines classifications; metric definitions live
only in `metrics/real_estate_metrics.json`. Privacy tags describe restrictions;
they do not themselves implement database permissions or pseudonymisation.

KPI expressions describe measures over their declared source. Overview metrics
read precomputed columns. Grouped metrics sum `nb_annonces`, not summary rows.
Source grouping uses `source_nom`. City grouping combines identical city labels
across postal codes and countries. Active mandates sums `nb_mandats` for `ACTIF`
in the warehouse snapshot; it does not calculate status from expiry dates.
Market counts represent listing observations, not distinct properties.

The offline metric check supports the project's simple dbt mart projections and
measure expressions, not arbitrary SQL parsing. Regression tests execute measures
against SQLite fixtures; PostgreSQL queries and OpenMetadata publication still
require verification on the trusted runner. Certification policy and quality
result publication have not changed in this update.
