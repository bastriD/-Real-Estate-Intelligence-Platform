#!/bin/sh
# Read-only prerequisite shared by backend publication and matching workloads.
SEARCH_SCHEMA_READY="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 -tAc \
      "SELECT CASE WHEN
         (SELECT COUNT(*) FROM migration_control.schema_version WHERE version = '017') = 1
         AND to_regclass('real_estate.demande_version_secteur') IS NOT NULL
         AND EXISTS (SELECT 1 FROM information_schema.columns
                     WHERE table_schema = 'real_estate' AND table_name = 'bien' AND column_name = 'id_secteur')
       THEN 'yes' ELSE 'no' END;"
)"
if [ "$SEARCH_SCHEMA_READY" != "yes" ]; then
  echo "ERROR: migration 017 is required. Run database:migrate-017 and database:test-demande-version-search."
  exit 1
fi
