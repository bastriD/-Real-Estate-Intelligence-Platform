#!/usr/bin/env bash

set -euo pipefail

echo "============================================================"
echo " Real Estate Governance-as-Code"
echo "============================================================"

if [[ -z "${OM_URL:-}" ]]; then
  echo "ERROR: OM_URL is not defined"
  exit 1
fi

if [[ -z "${OM_JWT_TOKEN:-}" ]]; then
  echo "ERROR: OM_JWT_TOKEN is not defined"
  exit 1
fi

echo "OpenMetadata endpoint: ${OM_URL}"
echo "Starting governance apply..."

python3 /app/scripts/main.py

echo "============================================================"
echo " Governance apply completed successfully"
echo "============================================================"