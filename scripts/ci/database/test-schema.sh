#!/bin/sh
# database:test-schema / script. Sourced by GitLab; run from the project checkout.

kubectl -n real-estate get deploy real-estate-postgresql
kubectl -n real-estate exec deploy/real-estate-postgresql \
  -i -- \
  psql \
    -U real_estate_user \
    -d real_estate \
    -v ON_ERROR_STOP=1 \
    < database/tests/001_schema_structure.sql
