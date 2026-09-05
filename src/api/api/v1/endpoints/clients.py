from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.client import ClientCreate, ClientRead, ClientUpdate
from src.api.services.client import (
    ClientAlreadyExistsError,
    ClientNotFoundError,
    ClientService,
)

router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
)


@router.get(
    "",
    response_model=list[ClientRead],
)
def list_clients(
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN")),
) -> list[ClientRead]:
    service = ClientService(db)
    return service.list_clients()


@router.get(
    "/{client_id}",
    response_model=ClientRead,
)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
) -> ClientRead:
    service = ClientService(db)

    try:
        return service.get_client(client_id)

    except ClientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=ClientRead,
    status_code=status.HTTP_201_CREATED,
)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
) -> ClientRead:
    service = ClientService(db)

    try:
        return service.create_client(payload)

    except ClientAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{client_id}",
    response_model=ClientRead,
)
def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
) -> ClientRead:
    service = ClientService(db)

    try:
        return service.update_client(client_id, payload)

    except ClientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ClientAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
) -> None:
    service = ClientService(db)

    try:
        service.delete_client(client_id)

    except ClientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc