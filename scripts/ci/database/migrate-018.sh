#!/bin/sh
# Manual forward migration; existing operation template serializes execution.
SECTOR_MIGRATION_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 -tAc \
      "SELECT COUNT(*) FROM migration_control.schema_version WHERE version = '018';"
)"
if [ "$SECTOR_MIGRATION_COUNT" = "1" ]; then
  echo "Migration 018 already applied - skipping safely."
  exit 0
fi
if [ "$SECTOR_MIGRATION_COUNT" != "0" ]; then
  echo "ERROR: unexpected migration 018 registry state."
  exit 1
fi
kubectl -n real-estate exec deploy/real-estate-postgresql -i -- \
  psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 \
  < database/migrations/018_ingestion_sector_contract.sql
