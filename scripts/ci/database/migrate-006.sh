#!/bin/sh
# database:migrate-006 / script. Sourced by GitLab; run from the project checkout.

kubectl version --client
kubectl -n real-estate get deploy real-estate-postgresql
echo "Checking migration 006 prerequisites..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('real_estate.client') AS client,
        to_regclass('real_estate.chasseur') AS chasseur,
        to_regclass('migration_control.schema_version') AS schema_version;
    "
MIGRATION_006_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM migration_control.schema_version
           WHERE version = '006'
         )
         THEN 'yes'
         ELSE 'no'
       END;" 2>/dev/null || true
)"

if [ "$MIGRATION_006_APPLIED" = "yes" ]; then
  echo "Migration 006 already applied - skipping safely."
  exit 0
fi
echo "Applying migration 006..."

kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/migrations/006_auth_identity.sql
echo "Verifying authentication identity table..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        to_regclass('real_estate.utilisateur') AS utilisateur;
    "
echo "Verifying utilisateur columns..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        column_name,
        data_type,
        is_nullable
      FROM information_schema.columns
      WHERE table_schema = 'real_estate'
        AND table_name = 'utilisateur'
      ORDER BY ordinal_position;
    "
echo "Checking bootstrap account count..."

USER_COUNT="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT COUNT(*)
       FROM real_estate.utilisateur;"
)"

echo "Authentication identities: ${USER_COUNT}"

if [ "${USER_COUNT}" != "0" ]; then
  echo "ERROR: migration 006 unexpectedly created authentication accounts."
  exit 1
fi
echo "Verifying migration registry..."

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        version,
        description,
        applied_at
      FROM migration_control.schema_version
      WHERE version = '006';
    "
echo "============================================================"
echo "MIGRATION 006 SUCCESSFULLY APPLIED"
echo "============================================================"

kubectl -n real-estate exec deploy/real-estate-postgresql -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    -c "
      SELECT
        role,
        COUNT(*) AS identities
      FROM real_estate.utilisateur
      GROUP BY role
      ORDER BY role;
    "
