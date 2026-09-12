from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from src.api.core.dependencies import (
    require_roles,
)
from src.api.db.session import get_db
from src.api.schemas.auth import (
    AuthenticatedUser,
)
from src.api.schemas.paiement import (
    PaiementRead,
)
from src.api.schemas.paiement_transition import (
    PaiementTransitionRequest,
)
from src.api.services.paiement import (
    PaiementNotFoundError,
    PaiementService,
    PaiementTransitionError,
    PaiementValidationError,
)


router = APIRouter(
    prefix="/paiements",
    tags=["Paiements"],
)


@router.patch(
    "/{paiement_id}/statut",
    response_model=PaiementRead,
)
def transition_paiement(
    paiement_id: int,
    payload: PaiementTransitionRequest,
    db: Session = Depends(
        get_db
    ),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "ADMIN",
        )
    ),
) -> PaiementRead:
    service = PaiementService(
        db
    )

    try:
        return service.transition(
            paiement_id,
            statut_cible=payload.statut,
            utilisateur=(
                current_user.email
            ),
            date_reception_honoraires=(
                payload
                .date_reception_honoraires
            ),
            date_paiement_chasseur=(
                payload
                .date_paiement_chasseur
            ),
            motif_annulation=(
                payload.motif_annulation
            ),
        )

    except PaiementNotFoundError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc

    except PaiementTransitionError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(exc),
        ) from exc

    except PaiementValidationError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc