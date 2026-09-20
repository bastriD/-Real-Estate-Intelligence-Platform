#!/bin/sh
# database:test-remuneration-configuration / script. Sourced by GitLab; run from the project checkout.

kubectl -n real-estate get deploy real-estate-postgresql
MIGRATION_011_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '011'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_011_APPLIED" != "yes" ]; then
  echo "ERROR: migration 011 must be applied before running remuneration configuration tests."
  exit 1
fi
echo "Running remuneration configuration tests..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/tests/014_remuneration_configuration.sql
echo "============================================================"
echo "REMUNERATION CONFIGURATION TESTS SUCCESSFUL"
echo "============================================================"
