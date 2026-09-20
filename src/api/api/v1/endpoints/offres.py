from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from src.api.core.authorization import (
    enforce_demande_access,
    require_chasseur_identity,
)
from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.offre import (
    OffreCreate,
    OffreDecision,
    OffreRead,
    OffreRevision,
)
from src.api.services.demande import DemandeService
from src.api.services.demande_affectation import (
    DemandeAffectationService,
)
from src.api.services.offre import (
    OffreNotFoundError,
    OffreService,
    OffreTransitionError,
    OffreValidationError,
    PresentationNotFoundForOffreError,
)


router = APIRouter(
    prefix="/offres",
    tags=["Offres"],
)


def get_service(
    db: Session = Depends(get_db),
) -> OffreService:
    return OffreService(db)


@router.get(
    "",
    response_model=list[OffreRead],
)
def list_offres(
    presentation_id: int | None = Query(
        default=None,
        gt=0,
    ),
    service: OffreService = Depends(
        get_service
    ),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "ADMIN",
            "CHASSEUR",
        )
    ),
) -> list[OffreRead]:
    if current_user.role == "CHASSEUR":
        chasseur_id = require_chasseur_identity(
            current_user
        )

        return service.list_offres_for_chasseur(
            chasseur_id=chasseur_id,
            presentation_id=presentation_id,
        )

    return service.list_offres(
        presentation_id=presentation_id
    )


@router.get(
    "/{offre_id}",
    response_model=OffreRead,
)
def get_offre(
    offre_id: int,
    service: OffreService = Depends(
        get_service
    ),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "ADMIN",
            "CHASSEUR",
        )
    ),
) -> OffreRead:
    try:
        if current_user.role == "CHASSEUR":
            demande_id = (
                service.get_demande_id_for_offre(
                    offre_id
                )
            )

            enforce_demande_access(
                current_user=current_user,
                demande_id=demande_id,
                affectation_service=(
                    DemandeAffectationService(
                        service.session
                    )
                ),
                demande_service=DemandeService(
                    service.session
                ),
            )

        return service.get_offre(
            offre_id
        )

    except OffreNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offre not found",
        ) from exc


@router.post(
    "",
    response_model=OffreRead,
    status_code=status.HTTP_201_CREATED,
)
def create_offre(
    payload: OffreCreate,
    service: OffreService = Depends(
        get_service
    ),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "ADMIN",
            "CHASSEUR",
        )
    ),
) -> OffreRead:
    try:
        if current_user.role == "CHASSEUR":
            demande_id = (
                service
                .get_demande_id_for_presentation(
                    payload.id_presentation
                )
            )

            enforce_demande_access(
                current_user=current_user,
                demande_id=demande_id,
                affectation_service=(
                    DemandeAffectationService(
                        service.session
                    )
                ),
                demande_service=DemandeService(
                    service.session
                ),
            )

        return service.create_offre(
            payload,
            utilisateur=current_user.email,
        )

    except PresentationNotFoundForOffreError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found",
        ) from exc

    except OffreValidationError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc


@router.post(
    "/{offre_id}/decision",
    response_model=OffreRead,
)
def decide_offre(
    offre_id: int,
    payload: OffreDecision,
    service: OffreService = Depends(
        get_service
    ),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "ADMIN",
            "CHASSEUR",
        )
    ),
) -> OffreRead:
    try:
        if current_user.role == "CHASSEUR":
            demande_id = (
                service.get_demande_id_for_offre(
                    offre_id
                )
            )

            enforce_demande_access(
                current_user=current_user,
                demande_id=demande_id,
                affectation_service=(
                    DemandeAffectationService(
                        service.session
                    )
                ),
                demande_service=DemandeService(
                    service.session
                ),
            )

        return service.decide_offre(
            offre_id,
            payload,
            utilisateur=current_user.email,
        )

    except OffreNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offre not found",
        ) from exc

    except OffreTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except OffreValidationError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc


@router.post(
    "/{offre_id}/revisions",
    response_model=OffreRead,
    status_code=status.HTTP_201_CREATED,
)
def revise_offre(
    offre_id: int,
    payload: OffreRevision,
    service: OffreService = Depends(
        get_service
    ),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "ADMIN",
            "CHASSEUR",
        )
    ),
) -> OffreRead:
    try:
        if current_user.role == "CHASSEUR":
            demande_id = (
                service.get_demande_id_for_offre(
                    offre_id
                )
            )

            enforce_demande_access(
                current_user=current_user,
                demande_id=demande_id,
                affectation_service=(
                    DemandeAffectationService(
                        service.session
                    )
                ),
                demande_service=DemandeService(
                    service.session
                ),
            )

        return service.revise_offre(
            offre_id,
            payload,
            utilisateur=current_user.email,
        )

    except OffreNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Offre not found",
        ) from exc

    except OffreTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except OffreValidationError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc