from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.api.db.models.utilisateur import Utilisateur


class UtilisateurRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(
        self,
        utilisateur_id: int,
    ) -> Utilisateur | None:
        statement = (
            select(Utilisateur)
            .where(
                Utilisateur.id_utilisateur == utilisateur_id
            )
        )

        return self.session.scalar(statement)

    def get_by_email(
        self,
        email: str,
    ) -> Utilisateur | None:
        statement = (
            select(Utilisateur)
            .where(
                func.lower(Utilisateur.email)
                == email.strip().lower()
            )
        )

        return self.session.scalar(statement)

    def create(
        self,
        utilisateur: Utilisateur,
    ) -> Utilisateur:
        self.session.add(utilisateur)
        self.session.flush()
        self.session.refresh(utilisateur)

        return utilisateur