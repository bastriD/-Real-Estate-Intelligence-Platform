from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.facture_client import FactureClient
from src.api.db.models.mandat import Mandat
from src.api.db.models.paiement import Paiement
from src.api.db.models.vente import Vente


class FactureClientRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _accessible_statement(*, client_id: int | None, chasseur_id: int | None):
        statement = (
            select(FactureClient)
            .join(Vente, Vente.id_vente == FactureClient.id_vente)
            .join(Mandat, Mandat.id_mandat == Vente.id_mandat)
        )
        if client_id is not None:
            statement = statement.where(Mandat.id_client == client_id)
        if chasseur_id is not None:
            # Same completed-sale beneficiary rule as Vente/Paiement reads.
            statement = statement.where(Vente.id_chasseur_beneficiaire == chasseur_id)
        return statement

    def list_accessible(
        self, *, client_id: int | None = None, chasseur_id: int | None = None,
    ) -> list[FactureClient]:
        statement = self._accessible_statement(
            client_id=client_id, chasseur_id=chasseur_id,
        ).order_by(FactureClient.id_facture_client)
        return list(self.session.scalars(statement).all())

    def get_by_id(
        self, invoice_id: int, *, client_id: int | None = None,
        chasseur_id: int | None = None,
    ) -> FactureClient | None:
        statement = self._accessible_statement(
            client_id=client_id, chasseur_id=chasseur_id,
        ).where(FactureClient.id_facture_client == invoice_id)
        return self.session.scalar(statement)

    def get_by_vente(self, vente_id: int) -> FactureClient | None:
        return self.session.scalar(select(FactureClient).where(FactureClient.id_vente == vente_id))

    def get_by_numero(self, numero: str) -> FactureClient | None:
        return self.session.scalar(select(FactureClient).where(FactureClient.numero_facture == numero))

    def get_sale_context(self, vente_id: int):
        # Freeze the lineage and sale inputs until invoice + audit commit.
        return self.session.execute(
            select(Vente, Mandat)
            .join(Mandat, Mandat.id_mandat == Vente.id_mandat)
            .where(Vente.id_vente == vente_id)
            .with_for_update(of=(Vente, Mandat))
        ).one_or_none()

    def create(self, invoice: FactureClient) -> FactureClient:
        self.session.add(invoice)
        self.session.flush()
        self.session.refresh(invoice)
        return invoice

    def get_payment_for_update(self, vente_id: int) -> Paiement | None:
        return self.session.scalar(
            select(Paiement).where(Paiement.id_vente == vente_id).with_for_update()
        )
