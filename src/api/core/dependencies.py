from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.api.core.security import decode_access_token
from src.api.db.session import get_db
from src.api.repositories.utilisateur import UtilisateurRepository
from src.api.schemas.auth import AuthenticatedUser


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    utilisateur_id = payload.get("uid")

    if not isinstance(utilisateur_id, int):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repository = UtilisateurRepository(db)
    utilisateur = repository.get_by_id(utilisateur_id)

    if utilisateur is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not utilisateur.actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication account is inactive",
        )

    return AuthenticatedUser(
        id_utilisateur=utilisateur.id_utilisateur,
        email=utilisateur.email,
        role=utilisateur.role,
        id_client=utilisateur.id_client,
        id_chasseur=utilisateur.id_chasseur,
    )


def require_roles(
    *allowed_roles: str,
) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    def dependency(
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return dependency