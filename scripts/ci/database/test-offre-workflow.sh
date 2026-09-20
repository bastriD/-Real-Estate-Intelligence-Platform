#!/bin/sh
# database:test-offre-workflow / script. Sourced by GitLab; run from the project checkout.

kubectl -n real-estate get deploy real-estate-postgresql

MIGRATION_014_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '014'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_014_APPLIED" != "yes" ]; then
  echo "ERROR: migration 014 must be applied before running OFFRE workflow tests."
  exit 1
fi

echo "Running OFFRE workflow tests..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/tests/017_offre_workflow.sql

echo "============================================================"
echo "OFFRE WORKFLOW TESTS SUCCESSFUL"
echo "============================================================"