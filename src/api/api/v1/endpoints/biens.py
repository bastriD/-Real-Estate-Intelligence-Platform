from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.bien import BienRead, BienStatut
from src.api.services.bien import BienNotFoundError, BienService

router = APIRouter(
    prefix="/biens",
    tags=["Biens"],
)


def get_service(
    db: Session = Depends(get_db),
) -> BienService:
    return BienService(db)


@router.get(
    "",
    response_model=list[BienRead],
)
def list_biens(
    ville: str | None = Query(default=None),
    statut: BienStatut | None = Query(default=None),
    type_bien: str | None = Query(default=None),
    service: BienService = Depends(get_service),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "CLIENT", "SERVICE")
    ),
) -> list[BienRead]:
    return service.list_biens(
        ville=ville,
        statut=statut.value if statut is not None else None,
        type_bien=type_bien,
    )


@router.get(
    "/{bien_id}",
    response_model=BienRead,
)
def get_bien(
    bien_id: int,
    service: BienService = Depends(get_service),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "CLIENT", "SERVICE")
    ),
) -> BienRead:
    try:
        return service.get_bien(bien_id)

    except BienNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bien not found",
        ) from exc