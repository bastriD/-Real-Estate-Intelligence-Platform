#!/bin/sh
# backend:validate / openapi-and-summary. Sourced by GitLab; run from the project checkout.

python - <<'PY'
from src.api.main import app

print("Application:", app.title)
print("Version:", app.version)

schema = app.openapi()

paths = sorted(
    schema.get(
        "paths",
        {},
    ).keys()
)

print("OpenAPI routes:")

for path in paths:
    print(f" - {path}")

required_routes = {
    "/health",
    "/ready",
    "/api/v1/health",
    "/api/v1/ready",
    "/api/v1/auth/login",
    "/api/v1/ventes",
    "/api/v1/factures-clients",
    "/api/v1/factures-clients/{invoice_id}",
    "/api/v1/factures-chasseurs",
    "/api/v1/factures-chasseurs/{invoice_id}",
    "/api/v1/factures-chasseurs/{invoice_id}/decision",
    "/api/v1/remunerations/ventes/{vente_id}/calcul",
    "/api/v1/remunerations/ventes/{vente_id}",
    "/api/v1/remunerations/{paiement_id}",
    "/api/v1/paiements/{paiement_id}/statut",
}

missing_routes = (
    required_routes.difference(paths)
)

if missing_routes:
    raise RuntimeError(
        "Missing required API routes: "
        f"{sorted(missing_routes)}"
    )

print(
    "Backend OpenAPI validation "
    "successful."
)
PY
echo
echo "============================================================"
echo "BACKEND VALIDATION COMPLETED"
echo "============================================================"

echo
echo "Validated here:"
echo "- Backend dependency compatibility"
echo "- Backend Python syntax"
echo "- Authentication dependency compatibility"
echo "- Password hashing primitives"
echo "- JWT encode/decode primitives"
echo "- Authorization / ownership imports"
echo "- Demande assignment imports"
echo "- Mandat lifecycle imports"
echo "- Mandat period / renewal imports"

echo "- Vente transaction imports"

echo "- Remuneration persistence model imports"
echo "- Remuneration repository imports"
echo "- Remuneration calculator imports"
echo "- Remuneration business service imports"
echo "- Remuneration schema imports"
echo "- Remuneration API endpoint syntax"

echo "- Payment lifecycle service imports"
echo "- Payment transition schema imports"
echo "- Payment API endpoint syntax"

echo "- Ownership endpoint syntax"
echo "- AI matching runtime import compatibility"
echo "- Backend deployment structure"
echo "- FastAPI/OpenAPI contract"

echo
echo "Required remuneration routes:"
echo "- POST /api/v1/remunerations/ventes/{vente_id}/calcul"
echo "- GET  /api/v1/remunerations/ventes/{vente_id}"
echo "- GET  /api/v1/remunerations/{paiement_id}"

echo
echo "Required payment lifecycle route:"
echo "- PATCH /api/v1/paiements/{paiement_id}/statut"

echo
echo "Behavioral validation is performed by backend:tests:"
echo "- Backend/API automated tests"
echo "- Authentication"
echo "- RBAC"
echo "- Mandat ownership"
echo "- Mandat lifecycle"
echo "- Mandat renewal periods"
echo "- Demande assignment lifecycle"
echo "- Demande ownership"
echo "- Presentation ownership"
echo "- Visite ownership"
echo "- Vente ownership / transaction lifecycle"
echo "- Remuneration deterministic calculation"
echo "- Remuneration persistence/service behavior"
echo "- Remuneration API / ownership / RBAC"
echo "- Duplicate remuneration protection"
echo "- Remuneration configuration error handling"
echo "- Payment lifecycle transitions"
echo "- Payment transition authorization"
echo "- Payment transition audit"
echo "- Audit compatibility"
echo "- Data tests"
echo "- Candidate availability"
echo "- API coverage >= 80 percent"

echo
echo "Additional validation responsibilities:"
echo "- ai:validate"
echo "- ai-mlops:evaluate"
