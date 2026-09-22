from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.notaire import (
    DossierNotarialCreate, DossierNotarialRead, MouvementNotarialCreate,
    MouvementNotarialRead, NotaireCreate, NotaireRead, SignatureNotariale,
)
from src.api.services.notaire import NotaireService, NotarialConflictError, NotarialNotFoundError, NotarialValidationError
from src.api.services.vente import VenteAlreadyExistsError, VenteValidationError
from src.api.services.paiement import PaiementTransitionError, PaiementValidationError

router = APIRouter(prefix="/notaires", tags=["Notaires"], dependencies=[Depends(require_roles("ADMIN"))])


def call(action):
    try:
        return action()
    except NotarialNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except (NotarialConflictError, VenteAlreadyExistsError, PaiementTransitionError) as exc:
        raise HTTPException(409, str(exc)) from exc
    except (NotarialValidationError, VenteValidationError, PaiementValidationError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("", response_model=list[NotaireRead])
def list_notaires(db: Session = Depends(get_db)):
    return NotaireService(db).repository.notaires()


@router.post("", response_model=NotaireRead, status_code=201)
def create_notaire(payload: NotaireCreate, db: Session = Depends(get_db), user: AuthenticatedUser = Depends(require_roles("ADMIN"))):
    return call(lambda: NotaireService(db).create_notaire(payload, utilisateur=user.email))


@router.post("/dossiers", response_model=DossierNotarialRead, status_code=201)
def create_dossier(payload: DossierNotarialCreate, db: Session = Depends(get_db), user: AuthenticatedUser = Depends(require_roles("ADMIN"))):
    return call(lambda: NotaireService(db).create_dossier(payload, utilisateur=user.email))


@router.get("/dossiers/{identifier}", response_model=DossierNotarialRead)
def get_dossier(identifier: int = Path(gt=0), db: Session = Depends(get_db)):
    return call(lambda: NotaireService(db).get_dossier(identifier))


@router.post("/dossiers/{identifier}/signature", response_model=DossierNotarialRead)
def sign(payload: SignatureNotariale, identifier: int = Path(gt=0), db: Session = Depends(get_db), user: AuthenticatedUser = Depends(require_roles("ADMIN"))):
    return call(lambda: NotaireService(db).sign(identifier, payload, utilisateur=user.email))


@router.get("/dossiers/{identifier}/mouvements", response_model=list[MouvementNotarialRead])
def list_movements(identifier: int = Path(gt=0), db: Session = Depends(get_db)):
    service = NotaireService(db)
    call(lambda: service.get_dossier(identifier))
    return service.repository.movements(identifier)


@router.post("/dossiers/{identifier}/mouvements", response_model=MouvementNotarialRead, status_code=201)
def record_movement(payload: MouvementNotarialCreate, identifier: int = Path(gt=0), db: Session = Depends(get_db), user: AuthenticatedUser = Depends(require_roles("ADMIN"))):
    return call(lambda: NotaireService(db).record_movement(identifier, payload, utilisateur=user.email))
