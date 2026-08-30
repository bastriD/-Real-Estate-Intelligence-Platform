from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.visite import Visite


class VisiteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Visite]:
        statement = select(Visite).order_by(
            Visite.id_visite
        )
        return list(self.session.scalars(statement).all())

    def get_by_id(
        self,
        visite_id: int,
    ) -> Visite | None:
        statement = select(Visite).where(
            Visite.id_visite == visite_id
        )
        return self.session.scalar(statement)

    def list_by_presentation(
        self,
        presentation_id: int,
    ) -> list[Visite]:
        statement = (
            select(Visite)
            .where(
                Visite.id_presentation == presentation_id
            )
            .order_by(
                Visite.date_visite,
                Visite.id_visite,
            )
        )
        return list(self.session.scalars(statement).all())

    def create(
        self,
        visite: Visite,
    ) -> Visite:
        self.session.add(visite)
        self.session.flush()
        self.session.refresh(visite)
        return visite

    def delete(
        self,
        visite: Visite,
    ) -> None:
        self.session.delete(visite)
        self.session.flush()