#!/bin/sh
# Explicit manual migration using the existing serialized database workflow.
PREVIOUS_MIGRATION_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 -tAc \
      "SELECT COUNT(*) FROM migration_control.schema_version WHERE version = '016';"
)"
if [ "$PREVIOUS_MIGRATION_COUNT" != "1" ]; then
  echo "ERROR: migration 016 must be applied before migration 017."
  exit 1
fi
SEARCH_MIGRATION_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 -tAc \
      "SELECT COUNT(*) FROM migration_control.schema_version WHERE version = '017';"
)"
if [ "$SEARCH_MIGRATION_COUNT" = "1" ]; then
  echo "Migration 017 already applied - skipping safely."
  exit 0
fi
if [ "$SEARCH_MIGRATION_COUNT" != "0" ]; then
  echo "ERROR: unexpected migration 017 registry state."
  exit 1
fi
kubectl -n real-estate exec deploy/real-estate-postgresql -i -- \
  psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 \
  < database/migrations/017_demande_version_search_enrichment.sql
echo "Run database:test-demande-version-search before releasing backend or matching workloads."
