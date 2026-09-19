from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.core.authorization import (
    enforce_demande_access,
    require_chasseur_identity,
)
from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.presentation import (
    PresentationCreate,
    PresentationRead,
    PresentationUpdate,
)
from src.api.services.demande import DemandeService
from src.api.services.demande_affectation import (
    DemandeAffectationService,
)

from src.api.services.presentation import (
    BienNotFoundForPresentationError,
    DemandeVersionNotFoundForPresentationError,
    PresentationAlreadyExistsError,
    PresentationDeleteConflictError,
    PresentationNotFoundError,
    PresentationService,
    PresentationValidationError,
)

router = APIRouter(
    prefix="/presentations",
    tags=["Presentations"],
)


def get_service(
    db: Session = Depends(get_db),
) -> PresentationService:
    return PresentationService(db)


@router.get(
    "",
    response_model=list[PresentationRead],
)
def list_presentations(
    demande_version_id: int | None = Query(
        default=None,
        gt=0,
    ),
    bien_id: int | None = Query(
        default=None,
        gt=0,
    ),
    service: PresentationService = Depends(get_service),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "SERVICE")
    ),
) -> list[PresentationRead]:
    if current_user.role == "CHASSEUR":
        chasseur_id = require_chasseur_identity(
            current_user
        )

        return service.list_presentations_for_chasseur(
            chasseur_id=chasseur_id,
            demande_version_id=demande_version_id,
            bien_id=bien_id,
        )

    return service.list_presentations(
        demande_version_id=demande_version_id,
        bien_id=bien_id,
    )


@router.get(
    "/{presentation_id}",
    response_model=PresentationRead,
)
def get_presentation(
    presentation_id: int,
    service: PresentationService = Depends(get_service),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "SERVICE")
    ),
) -> PresentationRead:
    try:
        if current_user.role == "CHASSEUR":
            demande_id = (
                service.get_demande_id_for_presentation(
                    presentation_id
                )
            )

            enforce_demande_access(
                current_user=current_user,
                demande_id=demande_id,
                affectation_service=DemandeAffectationService(
                    service.session
                ),
                demande_service=DemandeService(
                    service.session
                )
            )

        return service.get_presentation(
            presentation_id
        )

    except PresentationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found",
        ) from exc


@router.post(
    "",
    response_model=PresentationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_presentation(
    payload: PresentationCreate,
    service: PresentationService = Depends(get_service),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "SERVICE")
    ),
) -> PresentationRead:
    try:
        if current_user.role == "CHASSEUR":
            demande_id = (
                service.get_demande_id_for_version(
                    payload.id_demande_version
                )
            )

            enforce_demande_access(
                current_user=current_user,
                demande_id=demande_id,
                affectation_service=DemandeAffectationService(
                    service.session
                ),
                demande_service=DemandeService(
                    service.session
                )
            )

        return service.create_presentation(
            payload,
            utilisateur=current_user.email,
        )

    except DemandeVersionNotFoundForPresentationError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande version not found",
        ) from exc

    except BienNotFoundForPresentationError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bien not found",
        ) from exc

    except PresentationAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This property is already associated with "
                "this demande version"
            ),
        ) from exc

    except PresentationValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid presentation data",
        ) from exc


@router.patch(
    "/{presentation_id}",
    response_model=PresentationRead,
)
def update_presentation(
    presentation_id: int,
    payload: PresentationUpdate,
    service: PresentationService = Depends(get_service),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "SERVICE")
    ),
) -> PresentationRead:
    try:
        if current_user.role == "CHASSEUR":
            demande_id = (
                service.get_demande_id_for_presentation(
                    presentation_id
                )
            )

            enforce_demande_access(
                current_user=current_user,
                demande_id=demande_id,
                affectation_service=DemandeAffectationService(
                    service.session
                ),
                demande_service=DemandeService(
                    service.session
                )
            )

        return service.update_presentation(
            presentation_id,
            payload,
            utilisateur=current_user.email,
        )

    except PresentationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found",
        ) from exc

    except PresentationValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid presentation data",
        ) from exc


@router.delete(
    "/{presentation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_presentation(
    presentation_id: int,
    service: PresentationService = Depends(get_service),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "SERVICE")
    ),
) -> None:
    try:
        if current_user.role == "CHASSEUR":
            demande_id = (
                service.get_demande_id_for_presentation(
                    presentation_id
                )
            )

            enforce_demande_access(
                current_user=current_user,
                demande_id=demande_id,
                affectation_service=DemandeAffectationService(
                    service.session
                ),
                demande_service=DemandeService(
                    service.session
                )
            )

        service.delete_presentation(
            presentation_id,
            utilisateur=current_user.email,
        )

    except PresentationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found",
        ) from exc

    except PresentationDeleteConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Presentation cannot be deleted because "
                "it is referenced by another resource"
            ),
        ) from exc