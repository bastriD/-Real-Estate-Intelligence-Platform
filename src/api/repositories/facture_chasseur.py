from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.facture_chasseur import FactureChasseur
from src.api.db.models.paiement import Paiement


class FactureChasseurRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _scope(chasseur_id: int | None):
        statement = select(FactureChasseur).join(Paiement, Paiement.id_paiement == FactureChasseur.id_paiement)
        if chasseur_id is not None:
            statement = statement.where(Paiement.id_chasseur_beneficiaire == chasseur_id)
        return statement

    def list_accessible(self, chasseur_id: int | None = None) -> list[FactureChasseur]:
        return list(self.session.scalars(self._scope(chasseur_id).order_by(
            FactureChasseur.id_paiement, FactureChasseur.numero_version)).all())

    def get_by_id(self, invoice_id: int, chasseur_id: int | None = None) -> FactureChasseur | None:
        return self.session.scalar(self._scope(chasseur_id).where(FactureChasseur.id_facture_chasseur == invoice_id))

    def get_latest(self, payment_id: int) -> FactureChasseur | None:
        return self.session.scalar(select(FactureChasseur).where(
            FactureChasseur.id_paiement == payment_id).order_by(FactureChasseur.numero_version.desc()).limit(1))

    def get_by_id_for_update(self, invoice_id: int) -> FactureChasseur | None:
        return self.session.scalar(select(FactureChasseur).where(
            FactureChasseur.id_facture_chasseur == invoice_id).with_for_update()
            .execution_options(populate_existing=True))

    def create(self, invoice: FactureChasseur) -> FactureChasseur:
        self.session.add(invoice)
        self.session.flush()
        self.session.refresh(invoice)
        return invoice
