#!/bin/sh
# database:migrate-016. Sourced inside the existing database resource lock.

kubectl -n real-estate get deploy real-estate-postgresql
PREVIOUS_MIGRATION_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 -tAc \
      "SELECT COUNT(*) FROM migration_control.schema_version WHERE version = '015';"
)"
if [ "$PREVIOUS_MIGRATION_COUNT" != "1" ]; then
  echo "ERROR: migration 015 must be applied before migration 016."
  exit 1
fi
HUNTER_INVOICE_MIGRATION_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 -tAc \
      "SELECT COUNT(*) FROM migration_control.schema_version WHERE version = '016';"
)"
if [ "$HUNTER_INVOICE_MIGRATION_COUNT" = "1" ]; then
  echo "Migration 016 already applied - skipping safely."
  exit 0
fi
if [ "$HUNTER_INVOICE_MIGRATION_COUNT" != "0" ]; then
  echo "ERROR: unexpected migration 016 registry state."
  exit 1
fi
kubectl -n real-estate exec deploy/real-estate-postgresql -i -- \
  psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 \
  < database/migrations/016_facture_chasseur.sql
echo "Migration 016 applied. Run database:test-facture-chasseur before releasing the backend."
