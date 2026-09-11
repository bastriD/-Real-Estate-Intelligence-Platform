from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.demande_affectation import DemandeAffectation


class DemandeAffectationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(
        self,
        affectation_id: int,
    ) -> DemandeAffectation | None:
        statement = select(DemandeAffectation).where(
            DemandeAffectation.id_affectation == affectation_id
        )
        return self.session.scalar(statement)

    def list_by_demande(
        self,
        demande_id: int,
    ) -> list[DemandeAffectation]:
        statement = (
            select(DemandeAffectation)
            .where(
                DemandeAffectation.id_demande == demande_id
            )
            .order_by(
                DemandeAffectation.date_affectation,
                DemandeAffectation.id_affectation,
            )
        )

        return list(self.session.scalars(statement).all())

    def list_by_chasseur(
        self,
        chasseur_id: int,
        *,
        statut: str | None = None,
    ) -> list[DemandeAffectation]:
        statement = select(DemandeAffectation).where(
            DemandeAffectation.id_chasseur == chasseur_id
        )

        if statut is not None:
            statement = statement.where(
                DemandeAffectation.statut == statut
            )

        statement = statement.order_by(
            DemandeAffectation.date_affectation,
            DemandeAffectation.id_affectation,
        )

        return list(self.session.scalars(statement).all())

    def get_current_by_demande(
        self,
        demande_id: int,
        *,
        for_update: bool = False,
    ) -> DemandeAffectation | None:
        statement = select(DemandeAffectation).where(
            DemandeAffectation.id_demande == demande_id,
            DemandeAffectation.statut.in_(
                ("ASSIGNEE", "ACCEPTEE")
            ),
        )

        if for_update:
            statement = statement.with_for_update()

        return self.session.scalar(statement)

    def get_accepted_by_demande(
        self,
        demande_id: int,
    ) -> DemandeAffectation | None:
        statement = select(DemandeAffectation).where(
            DemandeAffectation.id_demande == demande_id,
            DemandeAffectation.statut == "ACCEPTEE",
        )

        return self.session.scalar(statement)

    def get_pending_for_chasseur(
        self,
        demande_id: int,
        chasseur_id: int,
        *,
        for_update: bool = False,
    ) -> DemandeAffectation | None:
        statement = select(DemandeAffectation).where(
            DemandeAffectation.id_demande == demande_id,
            DemandeAffectation.id_chasseur == chasseur_id,
            DemandeAffectation.statut == "ASSIGNEE",
        )

        if for_update:
            statement = statement.with_for_update()

        return self.session.scalar(statement)

    def create(
        self,
        affectation: DemandeAffectation,
    ) -> DemandeAffectation:
        self.session.add(affectation)
        self.session.flush()
        self.session.refresh(affectation)
        return affectation

    def save(
        self,
        affectation: DemandeAffectation,
    ) -> DemandeAffectation:
        self.session.add(affectation)
        self.session.flush()
        self.session.refresh(affectation)
        return affectation