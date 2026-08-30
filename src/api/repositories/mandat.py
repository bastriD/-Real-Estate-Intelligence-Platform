from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.mandat import Mandat


class MandatRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Mandat]:
        statement = (
            select(Mandat)
            .order_by(Mandat.id_mandat)
        )

        return list(
            self.session.scalars(statement).all()
        )

    def get_by_id(self, mandat_id: int) -> Mandat | None:
        statement = (
            select(Mandat)
            .where(Mandat.id_mandat == mandat_id)
        )

        return self.session.scalar(statement)

    def get_by_reference(
        self,
        reference_mandat: str,
    ) -> Mandat | None:
        statement = (
            select(Mandat)
            .where(Mandat.reference_mandat == reference_mandat)
        )

        return self.session.scalar(statement)

    def list_by_client(
        self,
        client_id: int,
    ) -> list[Mandat]:
        statement = (
            select(Mandat)
            .where(Mandat.id_client == client_id)
            .order_by(Mandat.id_mandat)
        )

        return list(
            self.session.scalars(statement).all()
        )

    def list_by_chasseur(
        self,
        chasseur_id: int,
    ) -> list[Mandat]:
        statement = (
            select(Mandat)
            .where(Mandat.id_chasseur == chasseur_id)
            .order_by(Mandat.id_mandat)
        )

        return list(
            self.session.scalars(statement).all()
        )

    def create(self, mandat: Mandat) -> Mandat:
        self.session.add(mandat)
        self.session.flush()
        self.session.refresh(mandat)

        return mandat

    def delete(self, mandat: Mandat) -> None:
        self.session.delete(mandat)
        self.session.flush()