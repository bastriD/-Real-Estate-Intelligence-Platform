#!/bin/sh
# Read-only release prerequisite; migrations remain explicit database jobs.

INVOICE_SCHEMA_READY="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 -tAc \
      "SELECT CASE WHEN
         (SELECT COUNT(*) FROM migration_control.schema_version WHERE version = '015') = 1
         AND to_regclass('real_estate.facture_client') IS NOT NULL
       THEN 'yes' ELSE 'no' END;"
)"
if [ "$INVOICE_SCHEMA_READY" != "yes" ]; then
  echo "ERROR: migration 015 is required before backend GitOps publication."
  echo "Run database:migrate-015 and database:test-facture-client, then retry publication."
  exit 1
fi
