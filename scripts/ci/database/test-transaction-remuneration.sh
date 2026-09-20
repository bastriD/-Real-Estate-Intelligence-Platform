#!/bin/sh
# database:test-transaction-remuneration / script. Sourced by GitLab; run from the project checkout.

kubectl -n real-estate get deploy real-estate-postgresql
MIGRATION_010_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '010'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_010_APPLIED" != "yes" ]; then
  echo "ERROR: migration 010 must be applied before running transaction/remuneration tests."
  exit 1
fi
echo "Running transaction and remuneration foundation tests..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/tests/013_transaction_remuneration.sql
echo "============================================================"
echo "TRANSACTION / REMUNERATION TESTS SUCCESSFUL"
echo "============================================================"
