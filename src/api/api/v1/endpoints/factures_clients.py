from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from src.api.core.authorization import require_chasseur_identity, require_client_identity
from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.facture_client import FactureClientCreate, FactureClientRead
from src.api.services.facture_client import (
    FactureClientAlreadyExistsError, FactureClientNotFoundError,
    FactureClientService, FactureClientValidationError,
)


router = APIRouter(prefix="/factures-clients", tags=["Factures clients"])


def _scope(user: AuthenticatedUser) -> dict[str, int | None]:
    return {
        "client_id": require_client_identity(user) if user.role == "CLIENT" else None,
        "chasseur_id": require_chasseur_identity(user) if user.role == "CHASSEUR" else None,
    }


@router.get("", response_model=list[FactureClientRead])
def list_factures_clients(
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN", "CLIENT", "CHASSEUR")),
) -> list[FactureClientRead]:
    return FactureClientService(db).list_factures(**_scope(current_user))


@router.get("/{invoice_id}", response_model=FactureClientRead)
def get_facture_client(
    invoice_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN", "CLIENT", "CHASSEUR")),
) -> FactureClientRead:
    try:
        return FactureClientService(db).get_facture(invoice_id, **_scope(current_user))
    except FactureClientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=FactureClientRead, status_code=status.HTTP_201_CREATED)
def create_facture_client(
    payload: FactureClientCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN")),
) -> FactureClientRead:
    try:
        return FactureClientService(db).create_facture(
            payload, utilisateur=current_user.email, id_utilisateur=current_user.id_utilisateur,
        )
    except FactureClientNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FactureClientAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except FactureClientValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
