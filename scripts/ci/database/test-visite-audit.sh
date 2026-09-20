#!/bin/sh
# database:test-visite-audit / script. Sourced by GitLab; run from the project checkout.

kubectl -n real-estate get deploy real-estate-postgresql
kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/tests/008_visite_audit.sql
