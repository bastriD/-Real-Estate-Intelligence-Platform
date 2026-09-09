from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.mandat import (
    MandatCreate,
    MandatRead,
    MandatUpdate,
)
from src.api.services.mandat import (
    ChasseurNotFoundForMandatError,
    ClientNotFoundForMandatError,
    MandatAlreadyExistsError,
    MandatNotFoundError,
    MandatService,
    MandatValidationError,
)


router = APIRouter(
    prefix="/mandats",
    tags=["Mandats"],
)


@router.get(
    "",
    response_model=list[MandatRead],
)
def list_mandats(
    client_id: int | None = Query(default=None, gt=0),
    chasseur_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR")
    ),
) -> list[MandatRead]:
    service = MandatService(db)

    try:
        if client_id is not None:
            return service.list_by_client(client_id)

        if chasseur_id is not None:
            return service.list_by_chasseur(chasseur_id)

        return service.list_mandats()

    except (
        ClientNotFoundForMandatError,
        ChasseurNotFoundForMandatError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{mandat_id}",
    response_model=MandatRead,
)
def get_mandat(
    mandat_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR")
    ),
) -> MandatRead:
    service = MandatService(db)

    try:
        return service.get_mandat(mandat_id)

    except MandatNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=MandatRead,
    status_code=status.HTTP_201_CREATED,
)
def create_mandat(
    payload: MandatCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR")
    ),
) -> MandatRead:
    service = MandatService(db)

    try:
        return service.create_mandat(
            payload,
            utilisateur=current_user.email,
        )

    except MandatAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except (
        ClientNotFoundForMandatError,
        ChasseurNotFoundForMandatError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except MandatValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{mandat_id}",
    response_model=MandatRead,
)
def update_mandat(
    mandat_id: int,
    payload: MandatUpdate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR")
    ),
) -> MandatRead:
    service = MandatService(db)

    try:
        return service.update_mandat(
            mandat_id,
            payload,
            utilisateur=current_user.email,
        )

    except (
        MandatNotFoundError,
        ClientNotFoundForMandatError,
        ChasseurNotFoundForMandatError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except MandatAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except MandatValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{mandat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_mandat(
    mandat_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR")
    ),
) -> None:
    service = MandatService(db)

    try:
        service.delete_mandat(
            mandat_id,
            utilisateur=current_user.email,
        )

    except MandatNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except MandatValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc