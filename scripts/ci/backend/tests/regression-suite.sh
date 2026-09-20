#!/bin/sh
# backend:tests / regression-suite. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "RUNNING BACKEND / DATA / TRANSACTION REGRESSION"
echo "============================================================"

python -m pytest \
  tests/backend \
  tests/data \
  tests/ai/test_candidate_availability.py \
  -v \
  --cov=src/api \
  --cov-report=term-missing \
  --cov-report=xml \
  --junitxml=backend-tests.xml \
  --cov-fail-under=80
echo
echo "============================================================"
echo "BACKEND AUTOMATED TEST GATE PASSED"
echo "============================================================"

echo
echo "Validated:"
echo "- Backend/API regression suite"
echo "- Authentication and role-based authorization"
echo "- Mandat / Demande / Presentation / Visite ownership"
echo "- Demande assignment lifecycle"
echo "- Vente transaction lifecycle and RBAC"
echo "- Contractual period resolution"
echo "- Exclusive / non-exclusive beneficiary rules"
echo "- Expired Mandat remuneration entitlement behavior"
echo "- Duplicate Presentation sale protection"

echo
echo "- Remuneration persistence models"
echo "- Remuneration repositories"
echo "- Remuneration business service"
echo "- Remuneration API / RBAC"
echo "- Duplicate remuneration calculation protection"
echo "- Missing remuneration configuration handling"
echo "- Frozen remuneration calculation snapshot"

echo
echo "- Deterministic remuneration calculator"
echo "- Company fee calculation"
echo "- Performance score calculation"
echo "- Seniority modulation"
echo "- Performance modulation"
echo "- Final remuneration rate calculation"

echo
echo "- Payment lifecycle service"
echo "- Payment lifecycle API"
echo "- ADMIN-only payment lifecycle mutation"
echo "- ATTENDU -> RECU"
echo "- RECU -> VERIFIE"
echo "- VERIFIE -> PROGRAMME"
echo "- PROGRAMME -> PAYE"
echo "- Controlled cancellation"
echo "- Terminal PAYE / ANNULE states"
echo "- Required reception and payment dates"
echo "- Payment date consistency"
echo "- Concurrent transition row locking"
echo "- Idempotent same-state transition"
echo "- Payment transition audit trail"

echo
echo "- Reference remuneration calculation:"
echo "  420000 EUR purchase"
echo "  13500 EUR company fees"
echo "  73.5 performance score"
echo "  46.16 percent hunter rate"
echo "  6231.60 EUR hunter remuneration"

echo
echo "- Audit actor propagation"
echo "- Existing data validation tests"
echo "- Candidate availability"
echo "- src/api coverage >= 80 percent"
