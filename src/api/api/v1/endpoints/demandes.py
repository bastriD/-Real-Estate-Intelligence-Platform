from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.demande import (
    DemandeCreate,
    DemandeHistory,
    DemandeRead,
    DemandeRevision,
    DemandeStatusUpdate,
    DemandeVersionRead,
    DemandeWithCurrentVersion,
)
from src.api.services.demande import (
    ChasseurNotFoundForDemandeError,
    ClientNotFoundForDemandeError,
    DemandeAlreadyExistsError,
    DemandeNotFoundError,
    DemandeService,
    DemandeValidationError,
    MandatNotFoundForDemandeError,
)

router = APIRouter(
    prefix="/demandes",
    tags=["Demandes"],
)


@router.get(
    "",
    response_model=list[DemandeRead],
)
def list_demandes(
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "SERVICE")
    ),
) -> list[DemandeRead]:
    service = DemandeService(db)
    return service.list_demandes()


@router.get(
    "/{demande_id}",
    response_model=DemandeWithCurrentVersion,
)
def get_demande(
    demande_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "SERVICE")
    ),
) -> DemandeWithCurrentVersion:
    service = DemandeService(db)

    try:
        demande = service.get_demande(demande_id)
        current_version = service.get_current_version(demande_id)

        return DemandeWithCurrentVersion(
            id_demande=demande.id_demande,
            reference_demande=demande.reference_demande,
            date_creation=demande.date_creation,
            statut=demande.statut,
            id_mandat=demande.id_mandat,
            current_version=current_version,
        )

    except DemandeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DemandeValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/{demande_id}/history",
    response_model=DemandeHistory,
)
def get_demande_history(
    demande_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "SERVICE")
    ),
) -> DemandeHistory:
    service = DemandeService(db)

    try:
        demande, versions = service.get_history(demande_id)

        return DemandeHistory(
            id_demande=demande.id_demande,
            reference_demande=demande.reference_demande,
            date_creation=demande.date_creation,
            statut=demande.statut,
            id_mandat=demande.id_mandat,
            versions=versions,
        )

    except DemandeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=DemandeWithCurrentVersion,
    status_code=status.HTTP_201_CREATED,
)
def create_demande(
    payload: DemandeCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "SERVICE")
    ),
) -> DemandeWithCurrentVersion:
    service = DemandeService(db)

    try:
        demande, version = service.create_demande(payload)

        return DemandeWithCurrentVersion(
            id_demande=demande.id_demande,
            reference_demande=demande.reference_demande,
            date_creation=demande.date_creation,
            statut=demande.statut,
            id_mandat=demande.id_mandat,
            current_version=version,
        )

    except DemandeAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except (
        MandatNotFoundForDemandeError,
        ClientNotFoundForDemandeError,
        ChasseurNotFoundForDemandeError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DemandeValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.post(
    "/{demande_id}/revisions",
    response_model=DemandeVersionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_revision(
    demande_id: int,
    payload: DemandeRevision,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "SERVICE")
    ),
) -> DemandeVersionRead:
    service = DemandeService(db)

    try:
        return service.create_revision(demande_id, payload)

    except DemandeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except (
        ClientNotFoundForDemandeError,
        ChasseurNotFoundForDemandeError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DemandeValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{demande_id}/status",
    response_model=DemandeRead,
)
def update_demande_status(
    demande_id: int,
    payload: DemandeStatusUpdate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "SERVICE")
    ),
) -> DemandeRead:
    service = DemandeService(db)

    try:
        return service.update_status(demande_id, payload)

    except DemandeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DemandeValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc