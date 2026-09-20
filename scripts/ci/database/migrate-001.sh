#!/bin/sh
# database:migrate-001 / script. Sourced by GitLab; run from the project checkout.

kubectl version --client
kubectl get namespace real-estate
kubectl -n real-estate get deploy real-estate-postgresql
ALREADY_APPLIED="$(
  kubectl -n real-estate exec deploy/real-estate-postgresql -- \
    psql \
      -U real_estate_user \
      -d real_estate \
      -tAc \
      "SELECT CASE
         WHEN to_regclass('real_estate.client') IS NOT NULL
         THEN 'yes'
         ELSE 'no'
       END;"
)"

if [ "$ALREADY_APPLIED" = "yes" ]; then
  echo "Migration 001 already applied - skipping safely."
  exit 0
fi
kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/migrations/001_initial_schema.sql
