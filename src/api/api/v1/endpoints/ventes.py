from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from src.api.core.authorization import (
    enforce_chasseur_ownership,
)
from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.schemas.vente import (
    VenteCreate,
    VenteRead,
)
from src.api.services.vente import (
    BienNotFoundForVenteError,
    PresentationNotFoundForVenteError,
    VenteAlreadyExistsError,
    VenteNotFoundError,
    VenteService,
    VenteValidationError,
)


router = APIRouter(
    prefix="/ventes",
    tags=["Ventes"],
)


@router.get(
    "",
    response_model=list[VenteRead],
)
def list_ventes(
    mandat_id: int | None = Query(
        default=None,
        gt=0,
    ),
    chasseur_id: int | None = Query(
        default=None,
        gt=0,
    ),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "ADMIN",
            "CHASSEUR",
        )
    ),
) -> list[VenteRead]:
    service = VenteService(db)

    if current_user.role == "CHASSEUR":
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

        own_chasseur_id = (
            current_user.id_chasseur
        )

        if chasseur_id is not None:
            enforce_chasseur_ownership(
                current_user,
                chasseur_id,
            )

        if mandat_id is not None:
            ventes = (
                service.list_by_mandat(
                    mandat_id
                )
            )

            return [
                vente
                for vente in ventes
                if (
                    vente
                    .id_chasseur_beneficiaire
                    == own_chasseur_id
                )
            ]

        return service.list_by_chasseur(
            own_chasseur_id
        )

    if mandat_id is not None:
        return service.list_by_mandat(
            mandat_id
        )

    if chasseur_id is not None:
        return service.list_by_chasseur(
            chasseur_id
        )

    return service.list_ventes()


@router.get(
    "/{vente_id}",
    response_model=VenteRead,
)
def get_vente(
    vente_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "ADMIN",
            "CHASSEUR",
        )
    ),
) -> VenteRead:
    service = VenteService(db)

    try:
        vente = service.get_vente(
            vente_id
        )

        if (
            vente
            .id_chasseur_beneficiaire
            is not None
        ):
            enforce_chasseur_ownership(
                current_user,
                vente
                .id_chasseur_beneficiaire,
            )
        elif current_user.role == "CHASSEUR":
            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail="Resource not found",
            )

        return vente

    except VenteNotFoundError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=VenteRead,
    status_code=status.HTTP_201_CREATED,
)
def create_vente(
    payload: VenteCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            "ADMIN",
            "CHASSEUR",
        )
    ),
) -> VenteRead:
    service = VenteService(db)

    try:
        if current_user.role == "CHASSEUR":
            mandat = (
                service
                ._get_mandat(
                    payload.id_mandat
                )
            )

            enforce_chasseur_ownership(
                current_user,
                mandat.id_chasseur,
            )

        return service.create_vente(
            payload,
            utilisateur=(
                current_user.email
            ),
        )

    except VenteAlreadyExistsError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(exc),
        ) from exc

    except (
        VenteValidationError,
        PresentationNotFoundForVenteError,
        BienNotFoundForVenteError,
    ) as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(exc),
        ) from exc