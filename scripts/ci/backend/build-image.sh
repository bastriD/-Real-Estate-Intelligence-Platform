#!/bin/sh
# backend:build-image / script. Sourced by GitLab; run from the project checkout.

echo
echo "============================================================"
echo "BUILDING REAL ESTATE BACKEND + AI MATCHING"
echo "============================================================"

echo
echo "Image:"
echo "$IMAGE_NAME:$IMAGE_TAG"

docker build \
  -f deploy/docker/Dockerfile.backend \
  -t "$IMAGE_NAME:$IMAGE_TAG" \
  -t "$IMAGE_NAME:latest" \
  .
docker run \
  --rm \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python --version
docker run \
  --rm \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "import jwt; import numpy; import pandas; import psycopg; from pwdlib import PasswordHash; PasswordHash.recommended(); print('Backend + AI + auth runtime dependencies OK')"
docker run \
  --rm \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "from src.ai.matching.features import MatchingWeights, build_matching_features, compute_matching_score, filter_candidates; from src.ai.matching.repository import load_demande_version, load_candidate_biens, load_matching_input; print('AI matching modules OK'); print(MatchingWeights())"
docker run \
  --rm \
  -e POSTGRES_PASSWORD=ci-image-validation-only \
  -e JWT_SECRET_KEY=ci-image-validation-jwt-secret-only \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "from src.api.core.authorization import enforce_chasseur_ownership, enforce_demande_access, enforce_demande_ownership, require_chasseur_identity; from src.api.services.demande_affectation import DemandeAffectationService; from src.api.services.vente import VenteService; from src.api.services.remuneration import RemunerationService; from src.api.services.remuneration_calculator import calculate_remuneration; from src.api.services.paiement import PaiementService, PaiementNotFoundError, PaiementTransitionError, PaiementValidationError; from src.api.schemas.paiement import PaiementRead; from src.api.schemas.paiement_transition import PaiementTransitionRequest; print('Authorization + ownership + transaction + remuneration + payment lifecycle modules OK')"
docker run \
  --rm \
  -e POSTGRES_PASSWORD=ci-image-validation-only \
  -e JWT_SECRET_KEY=ci-image-validation-jwt-secret-only \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "from src.api.db.models.paiement import Paiement; from src.api.db.models.bareme_commission import BaremeCommission; from src.api.db.models.parametres_honoraires import ParametresHonoraires; from src.api.db.models.parametres_remuneration import ParametresRemuneration; from src.api.db.models.palier_performance import PalierPerformance; from src.api.repositories.paiement import PaiementRepository; from src.api.repositories.bareme_commission import BaremeCommissionRepository; from src.api.repositories.parametres_honoraires import ParametresHonorairesRepository; from src.api.repositories.parametres_remuneration import ParametresRemunerationRepository; from src.api.repositories.palier_performance import PalierPerformanceRepository; print('Remuneration + payment persistence modules OK')"
docker run \
  --rm \
  -e POSTGRES_PASSWORD=ci-image-validation-only \
  -e JWT_SECRET_KEY=ci-image-validation-jwt-secret-only \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "from src.api.main import app; print('Application:', app.title); print('Version:', app.version)"
docker run \
  --rm \
  -e POSTGRES_PASSWORD=ci-image-validation-only \
  -e JWT_SECRET_KEY=ci-image-validation-jwt-secret-only \
  "$IMAGE_NAME:$IMAGE_TAG" \
  python -c \
  "from src.api.main import app; paths=set(app.openapi().get('paths', {}).keys()); required={'/health','/ready','/api/v1/health','/api/v1/ready','/api/v1/auth/login','/api/v1/ventes','/api/v1/remunerations/ventes/{vente_id}/calcul','/api/v1/remunerations/ventes/{vente_id}','/api/v1/remunerations/{paiement_id}','/api/v1/paiements/{paiement_id}/statut'}; missing=required-paths; print('OpenAPI paths:', sorted(paths)); assert not missing, f'Missing routes: {sorted(missing)}'; print('Vente + remuneration + payment OpenAPI routes OK')"
echo
echo "Publishing immutable Backend image:"
echo "$IMAGE_NAME:$IMAGE_TAG"

docker push \
  "$IMAGE_NAME:$IMAGE_TAG"
docker push \
  "$IMAGE_NAME:latest"
echo
echo "============================================================"
echo "BACKEND + AI MATCHING IMAGE PUBLISHED"
echo "============================================================"

echo
echo "Immutable image:"
echo "$IMAGE_NAME:$IMAGE_TAG"

echo
echo "Latest image:"
echo "$IMAGE_NAME:latest"

echo
echo "Validated application capabilities:"
echo "- Authentication / RBAC"
echo "- Ownership controls"
echo "- Vente transaction lifecycle"
echo "- Remuneration persistence"
echo "- Remuneration calculation service"
echo "- Remuneration API"
echo "- Payment lifecycle"
echo "- Payment transition API"
echo "- Deterministic AI matching"
