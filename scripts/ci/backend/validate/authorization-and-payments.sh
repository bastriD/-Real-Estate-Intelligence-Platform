#!/bin/sh
# backend:validate / authorization-and-payments. Sourced by GitLab; run from the project checkout.

python - <<'PY'
from src.api.core.authorization import (
    enforce_chasseur_ownership,
    enforce_demande_access,
    enforce_demande_ownership,
    require_chasseur_identity,
)

from src.api.services.demande_affectation import (
    DemandeAffectationService,
)

from src.api.services.mandat import (
    MandatService,
)

from src.api.services.vente import (
    VenteService,
)

from src.api.services.remuneration import (
    RemunerationAlreadyCalculatedError,
    RemunerationConfigurationError,
    RemunerationDataError,
    RemunerationNotFoundError,
    RemunerationService,
)

from src.api.services.remuneration_calculator import (
    PerformanceScores,
    PerformanceWeights,
    RemunerationCalculationInput,
    RemunerationCalculationResult,
    calculate_company_fees,
    calculate_final_rate,
    calculate_performance_modulation,
    calculate_performance_score,
    calculate_remuneration,
    calculate_seniority_bonus,
)

from src.api.services.paiement import (
    PaiementNotFoundError,
    PaiementService,
    PaiementTransitionError,
    PaiementValidationError,
)

from src.api.schemas.paiement import (
    PaiementRead,
)

from src.api.schemas.paiement_transition import (
    PaiementTransitionRequest,
)

print(
    "Authorization / ownership "
    "module imports successful."
)

print(
    "Demande assignment service "
    "import successful."
)

print(
    "Vente transaction service "
    "import successful."
)

print(
    "Remuneration calculator/service/schema "
    "imports successful."
)

print(
    "Payment lifecycle service/schema "
    "imports successful."
)
PY
python - <<'PY'
from src.api.db.models.paiement import (
    Paiement,
)

from src.api.db.models.bareme_commission import (
    BaremeCommission,
)

from src.api.db.models.parametres_honoraires import (
    ParametresHonoraires,
)

from src.api.db.models.parametres_remuneration import (
    ParametresRemuneration,
)

from src.api.db.models.palier_performance import (
    PalierPerformance,
)

from src.api.repositories.paiement import (
    PaiementRepository,
)

from src.api.repositories.bareme_commission import (
    BaremeCommissionRepository,
)

from src.api.repositories.parametres_honoraires import (
    ParametresHonorairesRepository,
)

from src.api.repositories.parametres_remuneration import (
    ParametresRemunerationRepository,
)

from src.api.repositories.palier_performance import (
    PalierPerformanceRepository,
)

print(
    "Remuneration / payment persistence models "
    "imported successfully."
)

print(
    "Remuneration / payment repositories "
    "imported successfully."
)
PY
