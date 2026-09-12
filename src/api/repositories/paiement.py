from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.paiement import Paiement


class PaiementRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        id_paiement: int,
    ) -> Paiement | None:
        stmt = select(Paiement).where(
            Paiement.id_paiement
            == id_paiement
        )

        return self.db.scalar(stmt)

    def get_by_id_for_update(
        self,
        id_paiement: int,
    ) -> Paiement | None:
        stmt = (
            select(Paiement)
            .where(
                Paiement.id_paiement
                == id_paiement
            )
            .with_for_update()
        )

        return self.db.scalar(stmt)

    def get_by_vente(
        self,
        id_vente: int,
    ) -> Paiement | None:
        stmt = select(Paiement).where(
            Paiement.id_vente
            == id_vente
        )

        return self.db.scalar(stmt)

    def list_by_mandat(
        self,
        id_mandat: int,
    ) -> list[Paiement]:
        stmt = (
            select(Paiement)
            .where(
                Paiement.id_mandat
                == id_mandat
            )
            .order_by(
                Paiement.id_paiement.desc()
            )
        )

        return list(
            self.db.scalars(
                stmt
            ).all()
        )

    def list_by_chasseur(
        self,
        id_chasseur: int,
    ) -> list[Paiement]:
        stmt = (
            select(Paiement)
            .where(
                Paiement.id_chasseur_beneficiaire
                == id_chasseur
            )
            .order_by(
                Paiement.id_paiement.desc()
            )
        )

        return list(
            self.db.scalars(
                stmt
            ).all()
        )

    def create(
        self,
        paiement: Paiement,
    ) -> Paiement:
        self.db.add(
            paiement
        )
        self.db.flush()
        self.db.refresh(
            paiement
        )

        return paiement

    def refresh(
        self,
        paiement: Paiement,
    ) -> Paiement:
        self.db.refresh(
            paiement
        )

        return paiement