from fastapi import HTTPException, status

from src.api.schemas.auth import AuthenticatedUser
from src.api.services.demande_affectation import (
    DemandeAffectationService,
)


def require_chasseur_identity(
    current_user: AuthenticatedUser,
) -> int:
    if (
        current_user.role != "CHASSEUR"
        or current_user.id_chasseur is None
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hunter identity is not available",
        )

    return current_user.id_chasseur


def enforce_chasseur_ownership(
    current_user: AuthenticatedUser,
    resource_chasseur_id: int,
) -> None:
    if current_user.role == "ADMIN":
        return

    chasseur_id = require_chasseur_identity(current_user)

    if resource_chasseur_id != chasseur_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )


def enforce_demande_access(
    current_user: AuthenticatedUser,
    demande_id: int,
    affectation_service: DemandeAffectationService,
) -> None:
    if current_user.role in {"ADMIN", "SERVICE"}:
        return

    chasseur_id = require_chasseur_identity(current_user)

    if not affectation_service.hunter_can_access_demande(
        demande_id=demande_id,
        chasseur_id=chasseur_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )


def enforce_demande_ownership(
    current_user: AuthenticatedUser,
    demande_id: int,
    affectation_service: DemandeAffectationService,
) -> None:
    if current_user.role in {"ADMIN", "SERVICE"}:
        return

    chasseur_id = require_chasseur_identity(current_user)

    if not affectation_service.hunter_owns_demande(
        demande_id=demande_id,
        chasseur_id=chasseur_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )