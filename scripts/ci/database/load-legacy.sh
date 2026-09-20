#!/bin/sh
# database:load-legacy / script. Sourced by GitLab; run from the project checkout.

kubectl -n real-estate get deploy real-estate-postgresql
LEGACY_EXISTS="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN EXISTS (
           SELECT 1
           FROM information_schema.schemata
           WHERE schema_name = 'Fil_Rouge_Depart'
         )
         THEN 'yes'
         ELSE 'no'
       END;"
)"

if [ "$LEGACY_EXISTS" = "yes" ]; then
  echo "Legacy schema Fil_Rouge_Depart already exists - skipping import."
  exit 0
fi
kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/legacy/PgSQL.sql
