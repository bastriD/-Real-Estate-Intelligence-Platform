from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.vente import Vente


class VenteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Vente]:
        statement = (
            select(Vente)
            .order_by(Vente.id_vente)
        )

        return list(
            self.session.scalars(statement).all()
        )

    def get_by_id(
        self,
        vente_id: int,
    ) -> Vente | None:
        statement = (
            select(Vente)
            .where(
                Vente.id_vente == vente_id
            )
        )

        return self.session.scalar(statement)

    def get_by_presentation(
        self,
        presentation_id: int,
    ) -> Vente | None:
        statement = (
            select(Vente)
            .where(
                Vente.id_presentation
                == presentation_id
            )
        )

        return self.session.scalar(statement)

    def list_by_mandat(
        self,
        mandat_id: int,
    ) -> list[Vente]:
        statement = (
            select(Vente)
            .where(
                Vente.id_mandat == mandat_id
            )
            .order_by(
                Vente.date_acte_authentique,
                Vente.id_vente,
            )
        )

        return list(
            self.session.scalars(statement).all()
        )

    def list_by_chasseur(
        self,
        chasseur_id: int,
    ) -> list[Vente]:
        statement = (
            select(Vente)
            .where(
                Vente.id_chasseur_beneficiaire
                == chasseur_id
            )
            .order_by(
                Vente.date_acte_authentique,
                Vente.id_vente,
            )
        )

        return list(
            self.session.scalars(statement).all()
        )

    def create(
        self,
        vente: Vente,
    ) -> Vente:
        self.session.add(
            vente
        )
        self.session.flush()
        self.session.refresh(
            vente
        )

        return vente