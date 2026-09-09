from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.presentation import (
    PresentationCreate,
    PresentationRead,
    PresentationUpdate,
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
        return service.get_presentation(presentation_id)

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
        return service.create_presentation(payload)

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
        return service.update_presentation(
            presentation_id,
            payload,
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
) -> Response:
    try:
        service.delete_presentation(presentation_id)

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

    return Response(status_code=status.HTTP_204_NO_CONTENT)