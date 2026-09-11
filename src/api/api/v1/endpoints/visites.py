from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
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
from src.api.schemas.visite import (
    VisiteCreate,
    VisiteRead,
    VisiteUpdate,
)
from src.api.services.demande_affectation import (
    DemandeAffectationService,
)
from src.api.services.visite import (
    PresentationNotFoundForVisiteError,
    VisiteDeleteConflictError,
    VisiteNotFoundError,
    VisiteService,
    VisiteValidationError,
)

router = APIRouter(
    prefix="/visites",
    tags=["Visites"],
)


def get_service(
    db: Session = Depends(get_db),
) -> VisiteService:
    return VisiteService(db)


@router.get(
    "",
    response_model=list[VisiteRead],
)
def list_visites(
    presentation_id: int | None = Query(
        default=None,
        gt=0,
    ),
    service: VisiteService = Depends(get_service),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR")
    ),
) -> list[VisiteRead]:
    if current_user.role == "CHASSEUR":
        chasseur_id = require_chasseur_identity(
            current_user
        )

        return service.list_visites_for_chasseur(
            chasseur_id=chasseur_id,
            presentation_id=presentation_id,
        )

    return service.list_visites(
        presentation_id=presentation_id
    )


@router.get(
    "/{visite_id}",
    response_model=VisiteRead,
)
def get_visite(
    visite_id: int,
    service: VisiteService = Depends(get_service),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR")
    ),
) -> VisiteRead:
    try:
        if current_user.role == "CHASSEUR":
            demande_id = (
                service.get_demande_id_for_visite(
                    visite_id
                )
            )

            enforce_demande_access(
                current_user=current_user,
                demande_id=demande_id,
                affectation_service=DemandeAffectationService(
                    service.session
                ),
            )

        return service.get_visite(visite_id)

    except VisiteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visite not found",
        ) from exc


@router.post(
    "",
    response_model=VisiteRead,
    status_code=status.HTTP_201_CREATED,
)
def create_visite(
    payload: VisiteCreate,
    service: VisiteService = Depends(get_service),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR")
    ),
) -> VisiteRead:
    try:
        if current_user.role == "CHASSEUR":
            demande_id = (
                service.get_demande_id_for_presentation(
                    payload.id_presentation
                )
            )

            enforce_demande_access(
                current_user=current_user,
                demande_id=demande_id,
                affectation_service=DemandeAffectationService(
                    service.session
                ),
            )

        return service.create_visite(
            payload,
            utilisateur=current_user.email,
        )

    except PresentationNotFoundForVisiteError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found",
        ) from exc

    except VisiteValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid visite data",
        ) from exc


@router.patch(
    "/{visite_id}",
    response_model=VisiteRead,
)
def update_visite(
    visite_id: int,
    payload: VisiteUpdate,
    service: VisiteService = Depends(get_service),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR")
    ),
) -> VisiteRead:
    try:
        if current_user.role == "CHASSEUR":
            demande_id = (
                service.get_demande_id_for_visite(
                    visite_id
                )
            )

            enforce_demande_access(
                current_user=current_user,
                demande_id=demande_id,
                affectation_service=DemandeAffectationService(
                    service.session
                ),
            )

        return service.update_visite(
            visite_id,
            payload,
            utilisateur=current_user.email,
        )

    except VisiteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visite not found",
        ) from exc

    except VisiteValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid visite data",
        ) from exc


@router.delete(
    "/{visite_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_visite(
    visite_id: int,
    service: VisiteService = Depends(get_service),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR")
    ),
) -> Response:
    try:
        if current_user.role == "CHASSEUR":
            demande_id = (
                service.get_demande_id_for_visite(
                    visite_id
                )
            )

            enforce_demande_access(
                current_user=current_user,
                demande_id=demande_id,
                affectation_service=DemandeAffectationService(
                    service.session
                ),
            )

        service.delete_visite(
            visite_id,
            utilisateur=current_user.email,
        )

    except VisiteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visite not found",
        ) from exc

    except VisiteDeleteConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Visite cannot be deleted because "
                "it is referenced by another resource"
            ),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )