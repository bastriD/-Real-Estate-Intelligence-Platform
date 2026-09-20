#!/bin/sh
# backend:tests / imports-and-openapi. Sourced by GitLab; run from the project checkout.

python - <<'PY'
from src.api.schemas.vente import (
    VenteCreate,
    VenteOrigine,
    VenteRead,
)

from src.api.schemas.paiement import (
    PaiementRead,
)

from src.api.schemas.paiement_transition import (
    PaiementTransitionRequest,
)

from src.api.services.vente import (
    VenteAlreadyExistsError,
    VenteNotFoundError,
    VenteService,
    VenteValidationError,
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

from src.api.services.remuneration import (
    RemunerationAlreadyCalculatedError,
    RemunerationConfigurationError,
    RemunerationDataError,
    RemunerationNotFoundError,
    RemunerationService,
)

from src.api.services.paiement import (
    PaiementNotFoundError,
    PaiementService,
    PaiementTransitionError,
    PaiementValidationError,
)

from src.api.db.models.paiement import Paiement
from src.api.db.models.bareme_commission import BaremeCommission
from src.api.db.models.parametres_honoraires import ParametresHonoraires
from src.api.db.models.parametres_remuneration import ParametresRemuneration
from src.api.db.models.palier_performance import PalierPerformance

from src.api.repositories.paiement import PaiementRepository
from src.api.repositories.bareme_commission import BaremeCommissionRepository
from src.api.repositories.parametres_honoraires import (
    ParametresHonorairesRepository,
)
from src.api.repositories.parametres_remuneration import (
    ParametresRemunerationRepository,
)
from src.api.repositories.palier_performance import (
    PalierPerformanceRepository,
)

print("Vente service/schema imports successful.")
print("Remuneration calculator imports successful.")
print("Remuneration persistence/service/schema imports successful.")
print("Payment lifecycle service/schema imports successful.")
PY
python - <<'PY'
from src.api.main import app

openapi_paths = app.openapi().get(
    "paths",
    {},
)

required_methods = {
    "/api/v1/ventes": {
        "get",
        "post",
    },
    "/api/v1/remunerations/ventes/{vente_id}/calcul": {
        "post",
    },
    "/api/v1/remunerations/ventes/{vente_id}": {
        "get",
    },
    "/api/v1/remunerations/{paiement_id}": {
        "get",
    },
    "/api/v1/paiements/{paiement_id}/statut": {
        "patch",
    },
}

for path, methods in required_methods.items():
    assert path in openapi_paths, (
        f"Missing required API route: {path}"
    )

    available_methods = {
        method.lower()
        for method in openapi_paths[path]
        if method.lower()
        in {
            "get",
            "post",
            "put",
            "patch",
            "delete",
        }
    }

    missing_methods = (
        methods - available_methods
    )

    assert not missing_methods, (
        f"Missing methods for {path}: "
        + ", ".join(
            sorted(missing_methods)
        )
    )

print(
    "Required Vente, remuneration and payment "
    "OpenAPI routes registered."
)
PY
