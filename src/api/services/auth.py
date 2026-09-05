from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.api.core.security import (
    create_access_token,
    verify_password,
)
from src.api.db.models.utilisateur import Utilisateur
from src.api.repositories.utilisateur import UtilisateurRepository
from src.api.schemas.auth import TokenResponse


class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = UtilisateurRepository(session)

    def authenticate(
        self,
        email: str,
        password: str,
    ) -> Utilisateur:
        utilisateur = self.repository.get_by_email(email)

        if utilisateur is None:
            raise InvalidCredentialsError(
                "Invalid email or password"
            )

        if not utilisateur.actif:
            raise InactiveUserError(
                "Authentication account is inactive"
            )

        if not verify_password(
            password,
            utilisateur.password_hash,
        ):
            raise InvalidCredentialsError(
                "Invalid email or password"
            )

        utilisateur.derniere_connexion = datetime.now(timezone.utc)

        self.session.commit()
        self.session.refresh(utilisateur)

        return utilisateur

    def login(
        self,
        email: str,
        password: str,
    ) -> TokenResponse:
        utilisateur = self.authenticate(
            email=email,
            password=password,
        )

        access_token = create_access_token(
            subject=utilisateur.email,
            role=utilisateur.role,
            utilisateur_id=utilisateur.id_utilisateur,
        )

        return TokenResponse(
            access_token=access_token,
        )