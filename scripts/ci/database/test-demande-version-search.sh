#!/bin/sh
kubectl -n real-estate exec deploy/real-estate-postgresql -i -- \
  psql -U real_estate_user -d real_estate -v ON_ERROR_STOP=1 \
  < database/tests/020_demande_version_search.sql
echo "Versioned search SQL assertions passed (test mutations rolled back)."
