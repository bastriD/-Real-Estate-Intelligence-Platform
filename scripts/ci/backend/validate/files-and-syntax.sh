#!/bin/sh
# backend:validate / files-and-syntax. Sourced by GitLab; run from the project checkout.

test -f requirements-backend.txt
test -f requirements-ai.txt
test -f requirements-backend-test.txt
test -f requirements-ai-training.txt
test -f src/api/main.py
test -f src/api/core/config.py
test -f src/api/core/security.py
test -f src/api/core/dependencies.py
test -f src/api/core/authorization.py
test -f src/api/db/session.py
test -f src/api/db/models/utilisateur.py
test -f src/api/db/models/audit_log.py
test -f src/api/repositories/utilisateur.py
test -f src/api/repositories/audit_log.py
test -f src/api/services/auth.py
test -f src/api/services/audit_log.py
test -f src/api/schemas/auth.py
test -f src/api/db/models/demande.py
test -f src/api/db/models/demande_affectation.py
test -f src/api/db/models/mandat.py
test -f src/api/db/models/mandat_periode.py
test -f src/api/db/models/presentation.py
test -f src/api/db/models/visite.py
test -f src/api/db/models/vente.py
test -f src/api/db/models/paiement.py
test -f src/api/db/models/bareme_commission.py
test -f src/api/db/models/parametres_honoraires.py
test -f src/api/db/models/parametres_remuneration.py
test -f src/api/db/models/palier_performance.py
test -f src/api/repositories/demande.py
test -f src/api/repositories/demande_affectation.py
test -f src/api/repositories/mandat.py
test -f src/api/repositories/presentation.py
test -f src/api/repositories/visite.py
test -f src/api/repositories/vente.py
test -f src/api/repositories/paiement.py
test -f src/api/repositories/bareme_commission.py
test -f src/api/repositories/parametres_honoraires.py
test -f src/api/repositories/parametres_remuneration.py
test -f src/api/repositories/palier_performance.py
test -f src/api/services/demande.py
test -f src/api/services/demande_affectation.py
test -f src/api/services/mandat.py
test -f src/api/services/presentation.py
test -f src/api/services/visite.py
test -f src/api/services/vente.py
test -f src/api/services/remuneration_calculator.py
test -f src/api/services/remuneration.py
test -f src/api/services/paiement.py
test -f src/api/schemas/demande_affectation.py
test -f src/api/schemas/mandat.py
test -f src/api/schemas/vente.py
test -f src/api/schemas/paiement.py
test -f src/api/schemas/paiement_transition.py
test -f src/api/api/v1/router.py
test -f src/api/api/v1/endpoints/health.py
test -f src/api/api/v1/endpoints/auth.py
test -f src/api/api/v1/endpoints/mandats.py
test -f src/api/api/v1/endpoints/demandes.py
test -f src/api/api/v1/endpoints/presentations.py
test -f src/api/api/v1/endpoints/visites.py
test -f src/api/api/v1/endpoints/ventes.py
test -f src/api/api/v1/endpoints/remunerations.py
test -f src/api/api/v1/endpoints/paiements.py
test -f src/ai/matching/features.py
test -f src/ai/matching/repository.py
test -f src/ai/matching/evaluate.py
test -f deploy/docker/Dockerfile.backend
test -f deploy/kubernetes/backend/deployment.yaml
test -f deploy/kubernetes/backend/service.yaml
test -f deploy/kubernetes/backend/servicemonitor.yaml
test -f deploy/kubernetes/backend/kustomization.yaml
test -f deploy/kubernetes/backend/application.yaml
python -m py_compile \
  src/api/main.py \
  src/api/core/config.py \
  src/api/core/security.py \
  src/api/core/dependencies.py \
  src/api/core/authorization.py \
  src/api/db/session.py \
  src/api/db/models/utilisateur.py \
  src/api/db/models/audit_log.py \
  src/api/db/models/demande.py \
  src/api/db/models/demande_affectation.py \
  src/api/db/models/mandat.py \
  src/api/db/models/mandat_periode.py \
  src/api/db/models/presentation.py \
  src/api/db/models/visite.py \
  src/api/db/models/vente.py \
  src/api/db/models/paiement.py \
  src/api/db/models/bareme_commission.py \
  src/api/db/models/parametres_honoraires.py \
  src/api/db/models/parametres_remuneration.py \
  src/api/db/models/palier_performance.py \
  src/api/repositories/utilisateur.py \
  src/api/repositories/audit_log.py \
  src/api/repositories/demande.py \
  src/api/repositories/demande_affectation.py \
  src/api/repositories/mandat.py \
  src/api/repositories/presentation.py \
  src/api/repositories/visite.py \
  src/api/repositories/vente.py \
  src/api/repositories/paiement.py \
  src/api/repositories/bareme_commission.py \
  src/api/repositories/parametres_honoraires.py \
  src/api/repositories/parametres_remuneration.py \
  src/api/repositories/palier_performance.py \
  src/api/services/auth.py \
  src/api/services/audit_log.py \
  src/api/services/demande.py \
  src/api/services/demande_affectation.py \
  src/api/services/mandat.py \
  src/api/services/presentation.py \
  src/api/services/visite.py \
  src/api/services/vente.py \
  src/api/services/remuneration_calculator.py \
  src/api/services/remuneration.py \
  src/api/services/paiement.py \
  src/api/schemas/auth.py \
  src/api/schemas/demande_affectation.py \
  src/api/schemas/mandat.py \
  src/api/schemas/vente.py \
  src/api/schemas/paiement.py \
  src/api/schemas/paiement_transition.py \
  src/api/api/v1/router.py \
  src/api/api/v1/endpoints/health.py \
  src/api/api/v1/endpoints/auth.py \
  src/api/api/v1/endpoints/mandats.py \
  src/api/api/v1/endpoints/demandes.py \
  src/api/api/v1/endpoints/presentations.py \
  src/api/api/v1/endpoints/visites.py \
  src/api/api/v1/endpoints/ventes.py \
  src/api/api/v1/endpoints/remunerations.py \
  src/api/api/v1/endpoints/paiements.py \
  src/ai/matching/features.py \
  src/ai/matching/repository.py \
  src/ai/matching/evaluate.py
