from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.bien import Bien


class BienRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Bien]:
        statement = select(Bien).order_by(Bien.id_bien)
        return list(self.session.scalars(statement).all())

    def get_by_id(
        self,
        bien_id: int,
    ) -> Bien | None:
        statement = select(Bien).where(
            Bien.id_bien == bien_id
        )
        return self.session.scalar(statement)

    def list_by_ville(
        self,
        ville: str,
    ) -> list[Bien]:
        statement = (
            select(Bien)
            .where(Bien.ville == ville)
            .order_by(Bien.id_bien)
        )
        return list(self.session.scalars(statement).all())

    def list_by_statut(
        self,
        statut: str,
    ) -> list[Bien]:
        statement = (
            select(Bien)
            .where(Bien.statut == statut)
            .order_by(Bien.id_bien)
        )
        return list(self.session.scalars(statement).all())

    def list_by_type(
        self,
        type_bien: str,
    ) -> list[Bien]:
        statement = (
            select(Bien)
            .where(Bien.type_bien == type_bien)
            .order_by(Bien.id_bien)
        )
        return list(self.session.scalars(statement).all())