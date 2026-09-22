#!/bin/sh
# Manual forward migration; the shared database operation lock is retained.
NOTARIAL_MIGRATION_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 -tAc \
      "SELECT COUNT(*) FROM migration_control.schema_version WHERE version = '019';"
)"
if [ "$NOTARIAL_MIGRATION_COUNT" = "1" ]; then
  echo "Migration 019 already applied - skipping safely."
  exit 0
fi
if [ "$NOTARIAL_MIGRATION_COUNT" != "0" ]; then
  echo "ERROR: unexpected migration 019 registry state."
  exit 1
fi
kubectl -n real-estate exec deploy/real-estate-postgresql -i -- \
  psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 \
  < database/migrations/019_notarial_workflow.sql
