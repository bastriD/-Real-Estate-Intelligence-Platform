from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.paiement import Paiement
from src.api.db.models.facture_chasseur import FactureChasseur


class PaiementRepository:
    def __init__(self, db: Session):
        self.db = db

    def has_conforming_invoice(self, payment_id: int) -> bool:
        # Use current persisted financial lineage, not just an invoice status.
        statement = select(FactureChasseur.id_facture_chasseur).join(
            Paiement, Paiement.id_paiement == FactureChasseur.id_paiement,
        ).where(
            Paiement.id_paiement == payment_id,
            Paiement.droit_remuneration.is_(True),
            Paiement.date_reception_honoraires.is_not(None),
            FactureChasseur.statut == "CONFORME",
            FactureChasseur.id_chasseur == Paiement.id_chasseur_beneficiaire,
            FactureChasseur.montant == Paiement.montant_chasseur,
        ).limit(1)
        return self.db.scalar(statement) is not None

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
