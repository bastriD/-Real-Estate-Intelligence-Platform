#!/bin/sh
# warehouse:migrate-003 / script. Sourced by GitLab; run from the project checkout.

kubectl version --client
kubectl get namespace real-estate
kubectl -n real-estate get deploy real-estate-postgresql
MIGRATION_003_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '003'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_003_APPLIED" = "yes" ]; then
  echo "Migration 003 already applied - skipping safely."
  exit 0
fi
kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/migrations/003_warehouse_schema.sql
kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
    INSERT INTO migration_control.schema_version (
        version,
        description
    )
    VALUES (
        '003',
        'Create analytical warehouse for market, business, matching and financial analytics'
    )
    ON CONFLICT (version) DO NOTHING;
    "
kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
    SELECT
        table_schema,
        table_name
    FROM information_schema.tables
    WHERE table_schema = 'warehouse'
    ORDER BY table_name;
    "
