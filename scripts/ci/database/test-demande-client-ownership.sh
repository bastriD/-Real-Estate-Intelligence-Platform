#!/bin/sh
# database:test-demande-client-ownership / script. Sourced by GitLab; run from the project checkout.

kubectl -n real-estate get deploy real-estate-postgresql
MIGRATION_013_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '013'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_013_APPLIED" != "yes" ]; then
  echo "ERROR: migration 013 must be applied before running DEMANDE client ownership tests."
  exit 1
fi
echo "Running DEMANDE client ownership tests..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/tests/016_demande_client_ownership.sql
echo "============================================================"
echo "DEMANDE CLIENT OWNERSHIP TESTS SUCCESSFUL"
echo "============================================================"
