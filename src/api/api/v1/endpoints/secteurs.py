from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.bien import BienRead
from src.api.schemas.secteur import BienSecteurUpdate, SecteurRead
from src.api.services.bien import BienNotFoundError
from src.api.services.secteur import SecteurService, SecteurValidationError


router = APIRouter(tags=["Secteurs"])


@router.get("/secteurs", response_model=list[SecteurRead])
def list_secteurs(db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_roles("ADMIN", "CHASSEUR", "CLIENT", "SERVICE"))):
    return SecteurService(db).list_active()


@router.put("/biens/{bien_id}/secteur", response_model=BienRead)
def assign_bien_secteur(payload: BienSecteurUpdate, bien_id: int = Path(gt=0),
    db: Session = Depends(get_db), user: AuthenticatedUser = Depends(require_roles("ADMIN"))):
    try:
        return SecteurService(db).assign_bien(bien_id, payload.id_secteur,
            actor=user.email, actor_id=user.id_utilisateur)
    except BienNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Bien not found") from exc
    except SecteurValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
