from fastapi import HTTPException, status

from src.api.schemas.auth import AuthenticatedUser


def require_chasseur_identity(
    current_user: AuthenticatedUser,
) -> int:
    """
    Return the authenticated hunter identifier.

    ADMIN users do not use this helper because they have unrestricted
    access at the resource-policy level.
    """
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
    """
    ADMIN has unrestricted resource access.

    A CHASSEUR may access only resources assigned to the same
    id_chasseur.

    A 404 is deliberately returned for cross-owner access so the API
    does not disclose the existence of another hunter's resource.
    """
    if current_user.role == "ADMIN":
        return

    chasseur_id = require_chasseur_identity(current_user)

    if resource_chasseur_id != chasseur_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )