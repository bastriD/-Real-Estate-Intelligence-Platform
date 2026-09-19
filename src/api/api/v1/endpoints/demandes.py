from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.core.authorization import enforce_demande_access
from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.demande import (
    DemandeCreate,
    DemandeHistory,
    DemandeMandatLink,
    DemandeRead,
    DemandeRevision,
    DemandeStatusUpdate,
    DemandeVersionRead,
    DemandeWithCurrentVersion,
)
from src.api.schemas.demande_affectation import (
    DemandeAffectationCreate,
    DemandeAffectationDecision,
    DemandeAffectationRead,
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
from src.api.services.demande_affectation import (
    ChasseurNotFoundForAffectationError,
    DemandeAffectationAuthorizationError,
    DemandeAffectationConflictError,
    DemandeAffectationNotFoundError,
    DemandeAffectationService,
    DemandeAffectationValidationError,
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
        require_roles("ADMIN", "CHASSEUR","CLIENT", "SERVICE")
    ),
) -> list[DemandeRead]:
    service = DemandeService(db)

    if current_user.role == "CHASSEUR":
        if current_user.id_chasseur is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Hunter identity is not available",
            )

        return service.list_demandes_for_chasseur(
            current_user.id_chasseur
        )
    if current_user.role == "CLIENT":
        if current_user.id_client is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client identity is not available",
            )

        return service.list_demandes_for_client(
            current_user.id_client
        )
    return service.list_demandes()


@router.get(
    "/{demande_id}",
    response_model=DemandeWithCurrentVersion,
)
def get_demande(
    demande_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR","CLIENT", "SERVICE")
    ),
) -> DemandeWithCurrentVersion:
    service = DemandeService(db)
    affectation_service = DemandeAffectationService(db)

    try:
        enforce_demande_access(
            current_user=current_user,
            demande_id=demande_id,
            affectation_service=affectation_service,
            demande_service=service,
        )

        demande = service.get_demande(demande_id)
        current_version = service.get_current_version(demande_id)

        return DemandeWithCurrentVersion(
            id_demande=demande.id_demande,
            reference_demande=demande.reference_demande,
            date_creation=demande.date_creation,
            statut=demande.statut,
            id_client=demande.id_client,
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
        require_roles("ADMIN", "CHASSEUR","CLIENT", "SERVICE")
    ),
) -> DemandeHistory:
    service = DemandeService(db)
    affectation_service = DemandeAffectationService(db)

    try:
        enforce_demande_access(
            current_user=current_user,
            demande_id=demande_id,
            affectation_service=affectation_service,
            demande_service=service,
        )

        demande, versions = service.get_history(demande_id)

        return DemandeHistory(
            id_demande=demande.id_demande,
            reference_demande=demande.reference_demande,
            date_creation=demande.date_creation,
            statut=demande.statut,
            id_client=demande.id_client,
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
        require_roles("ADMIN", "CHASSEUR","CLIENT", "SERVICE")
    ),
) -> DemandeWithCurrentVersion:
    service = DemandeService(db)

    if current_user.role == "CLIENT":
        if current_user.id_client is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client identity is not available",
            )

        if payload.id_client != current_user.id_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )

        if (
            payload.auteur_client_id
            != current_user.id_client
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
    try:
        demande, version = service.create_demande(payload)

        return DemandeWithCurrentVersion(
            id_demande=demande.id_demande,
            reference_demande=demande.reference_demande,
            date_creation=demande.date_creation,
            statut=demande.statut,
            id_client=demande.id_client,
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
        require_roles("ADMIN", "CHASSEUR","CLIENT", "SERVICE")
    ),
) -> DemandeVersionRead:
    service = DemandeService(db)
    affectation_service = DemandeAffectationService(db)
    
    if current_user.role == "CLIENT":
        if current_user.id_client is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client identity is not available",
            )

        if (
            payload.auteur_client_id
            != current_user.id_client
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
    try:
        enforce_demande_access(
            current_user=current_user,
            demande_id=demande_id,
            affectation_service=affectation_service,
            demande_service=service,
        )

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
    affectation_service = DemandeAffectationService(db)

    try:
        enforce_demande_access(
            current_user=current_user,
            demande_id=demande_id,
            affectation_service=affectation_service,
            demande_service=service,
        )

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
@router.patch(
    "/{demande_id}/mandat",
    response_model=DemandeRead,
)
def link_demande_mandat(
    demande_id: int,
    payload: DemandeMandatLink,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR", "SERVICE")
    ),
) -> DemandeRead:
    service = DemandeService(db)
    affectation_service = DemandeAffectationService(db)

    try:
        enforce_demande_access(
            current_user=current_user,
            demande_id=demande_id,
            affectation_service=affectation_service,
            demande_service=service,
        )

        return service.link_mandat(
            demande_id=demande_id,
            mandat_id=payload.id_mandat,
        )

    except (
        DemandeNotFoundError,
        MandatNotFoundForDemandeError,
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
    "/{demande_id}/affectations",
    response_model=DemandeAffectationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_demande_affectation(
    demande_id: int,
    payload: DemandeAffectationCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN")
    ),
) -> DemandeAffectationRead:
    service = DemandeAffectationService(db)

    try:
        return service.create_assignment(
            demande_id=demande_id,
            chasseur_id=payload.id_chasseur,
            current_user=current_user,
        )

    except (
        DemandeAffectationNotFoundError,
        ChasseurNotFoundForAffectationError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DemandeAffectationAuthorizationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except DemandeAffectationConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except DemandeAffectationValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "/{demande_id}/affectations",
    response_model=list[DemandeAffectationRead],
)
def list_demande_affectations(
    demande_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("ADMIN", "CHASSEUR")
    ),
) -> list[DemandeAffectationRead]:
    service = DemandeAffectationService(db)

    try:
        affectations = service.list_by_demande(demande_id)

        if current_user.role == "ADMIN":
            return affectations

        if (
            current_user.role != "CHASSEUR"
            or current_user.id_chasseur is None
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Hunter identity is not available",
            )

        visible_affectations = [
            affectation
            for affectation in affectations
            if affectation.id_chasseur
            == current_user.id_chasseur
        ]

        if not visible_affectations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment history not found",
            )

        return visible_affectations

    except DemandeAffectationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{demande_id}/affectations/decision",
    response_model=DemandeAffectationRead,
)
def decide_demande_affectation(
    demande_id: int,
    payload: DemandeAffectationDecision,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles("CHASSEUR")
    ),
) -> DemandeAffectationRead:
    service = DemandeAffectationService(db)

    try:
        return service.decide_assignment(
            demande_id=demande_id,
            payload=payload,
            current_user=current_user,
        )

    except DemandeAffectationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DemandeAffectationAuthorizationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except DemandeAffectationConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except DemandeAffectationValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc