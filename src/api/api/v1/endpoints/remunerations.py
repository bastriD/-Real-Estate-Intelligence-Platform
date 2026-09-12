from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from src.api.core.authorization import (
    enforce_chasseur_ownership,
)
from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.repositories.mandat import MandatRepository
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.paiement import PaiementRead
from src.api.services.remuneration import (
    RemunerationAlreadyCalculatedError,
    RemunerationConfigurationError,
    RemunerationDataError,
    RemunerationNotFoundError,
    RemunerationService,
)


router = APIRouter(
    prefix="/remunerations",
    tags=["Remunerations"],
)


def _enforce_mandat_access(
    *,
    db: Session,
    current_user: AuthenticatedUser,
    mandat_id: int,
) -> None:
    if current_user.role != "CHASSEUR":
        return

    if current_user.id_chasseur is None:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Hunter identity is "
                "not available"
            ),
        )

    mandat = (
        MandatRepository(db)
        .get_by_id(
            mandat_id
        )
    )

    if mandat is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Resource not found",
        )

    enforce_chasseur_ownership(
        current_user,
        mandat.id_chasseur,
    )


@router.post(
    "/ventes/{vente_id}/calcul",
    response_model=PaiementRead,
    status_code=status.HTTP_201_CREATED,
)
def calculate_remuneration(
    vente_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "ADMIN",
            "CHASSEUR",
        )
    ),
) -> PaiementRead:
    service = RemunerationService(
        db
    )

    try:
        vente = service._get_vente(
            vente_id
        )

        _enforce_mandat_access(
            db=db,
            current_user=current_user,
            mandat_id=vente.id_mandat,
        )

        return service.calculate_for_vente(
            vente_id,
            utilisateur=(
                current_user.email
            ),
        )

    except RemunerationNotFoundError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc

    except RemunerationAlreadyCalculatedError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(exc),
        ) from exc

    except RemunerationConfigurationError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc

    except RemunerationDataError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc


@router.get(
    "/ventes/{vente_id}",
    response_model=PaiementRead,
)
def get_remuneration_by_vente(
    vente_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "ADMIN",
            "CHASSEUR",
        )
    ),
) -> PaiementRead:
    service = RemunerationService(
        db
    )

    try:
        paiement = service.get_by_vente(
            vente_id
        )

        _enforce_mandat_access(
            db=db,
            current_user=current_user,
            mandat_id=paiement.id_mandat,
        )

        return paiement

    except RemunerationNotFoundError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc


@router.get(
    "/{paiement_id}",
    response_model=PaiementRead,
)
def get_remuneration(
    paiement_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "ADMIN",
            "CHASSEUR",
        )
    ),
) -> PaiementRead:
    service = RemunerationService(
        db
    )

    try:
        paiement = service.get_paiement(
            paiement_id
        )

        _enforce_mandat_access(
            db=db,
            current_user=current_user,
            mandat_id=paiement.id_mandat,
        )

        return paiement

    except RemunerationNotFoundError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc