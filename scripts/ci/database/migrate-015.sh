#!/bin/sh
# database:migrate-015. Sourced by GitLab in the existing database resource lock.

kubectl -n real-estate get deploy real-estate-postgresql

PREVIOUS_MIGRATION_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 -tAc \
      "SELECT COUNT(*) FROM migration_control.schema_version WHERE version = '014';"
)"
if [ "$PREVIOUS_MIGRATION_COUNT" != "1" ]; then
  echo "ERROR: migration 014 must be applied before migration 015."
  exit 1
fi

INVOICE_MIGRATION_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 -tAc \
      "SELECT COUNT(*) FROM migration_control.schema_version WHERE version = '015';"
)"
if [ "$INVOICE_MIGRATION_COUNT" = "1" ]; then
  echo "Migration 015 already applied - skipping safely."
  exit 0
fi
if [ "$INVOICE_MIGRATION_COUNT" != "0" ]; then
  echo "ERROR: unexpected migration 015 registry state."
  exit 1
fi

kubectl -n real-estate exec deploy/real-estate-postgresql -i -- \
  psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 \
  < database/migrations/015_facture_client.sql

echo "Migration 015 applied. Run database:test-facture-client before releasing the backend."
