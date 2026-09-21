from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from src.api.core.authorization import require_chasseur_identity
from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.facture_chasseur import FactureChasseurCreate, FactureChasseurDecision, FactureChasseurRead
from src.api.services.facture_chasseur import (
    FactureChasseurConflictError, FactureChasseurNotFoundError,
    FactureChasseurService, FactureChasseurValidationError,
)


router = APIRouter(prefix="/factures-chasseurs", tags=["Factures chasseurs"])


def _scope(user: AuthenticatedUser) -> int | None:
    return require_chasseur_identity(user) if user.role == "CHASSEUR" else None


def _error(exc):
    if isinstance(exc, FactureChasseurNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, FactureChasseurConflictError):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=422, detail=str(exc))


@router.get("", response_model=list[FactureChasseurRead])
def list_factures_chasseurs(
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN", "CHASSEUR")),
):
    return FactureChasseurService(db).list_factures(_scope(current_user))


@router.get("/{invoice_id}", response_model=FactureChasseurRead)
def get_facture_chasseur(
    invoice_id: int = Path(gt=0), db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN", "CHASSEUR")),
):
    try:
        return FactureChasseurService(db).get_facture(invoice_id, _scope(current_user))
    except FactureChasseurNotFoundError as exc:
        raise _error(exc) from exc


@router.post("", response_model=FactureChasseurRead, status_code=status.HTTP_201_CREATED)
def submit_facture_chasseur(
    payload: FactureChasseurCreate, db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles("CHASSEUR")),
):
    try:
        return FactureChasseurService(db).submit(
            payload, chasseur_id=require_chasseur_identity(current_user),
            utilisateur=current_user.email, id_utilisateur=current_user.id_utilisateur,
        )
    except (FactureChasseurNotFoundError, FactureChasseurConflictError, FactureChasseurValidationError) as exc:
        raise _error(exc) from exc


@router.post("/{invoice_id}/decision", response_model=FactureChasseurRead)
def decide_facture_chasseur(
    payload: FactureChasseurDecision, invoice_id: int = Path(gt=0), db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN")),
):
    try:
        return FactureChasseurService(db).decide(
            invoice_id, payload, utilisateur=current_user.email, id_utilisateur=current_user.id_utilisateur,
        )
    except (FactureChasseurNotFoundError, FactureChasseurConflictError, FactureChasseurValidationError) as exc:
        raise _error(exc) from exc
