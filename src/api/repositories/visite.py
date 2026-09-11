from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.demande import DemandeVersion
from src.api.db.models.demande_affectation import DemandeAffectation
from src.api.db.models.presentation import Presentation
from src.api.db.models.visite import Visite


class VisiteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Visite]:
        statement = select(Visite).order_by(
            Visite.id_visite
        )
        return list(self.session.scalars(statement).all())

    def list_accessible_by_chasseur(
        self,
        chasseur_id: int,
        presentation_id: int | None = None,
    ) -> list[Visite]:
        statement = (
            select(Visite)
            .join(
                Presentation,
                Presentation.id_presentation
                == Visite.id_presentation,
            )
            .join(
                DemandeVersion,
                DemandeVersion.id_demande_version
                == Presentation.id_demande_version,
            )
            .join(
                DemandeAffectation,
                DemandeAffectation.id_demande
                == DemandeVersion.id_demande,
            )
            .where(
                DemandeAffectation.id_chasseur
                == chasseur_id,
                DemandeAffectation.statut.in_(
                    (
                        "ASSIGNEE",
                        "ACCEPTEE",
                    )
                ),
            )
        )

        if presentation_id is not None:
            statement = statement.where(
                Visite.id_presentation
                == presentation_id
            )

        statement = statement.order_by(
            Visite.date_visite,
            Visite.id_visite,
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

    def get_demande_id(
        self,
        visite_id: int,
    ) -> int | None:
        statement = (
            select(DemandeVersion.id_demande)
            .join(
                Presentation,
                Presentation.id_demande_version
                == DemandeVersion.id_demande_version,
            )
            .join(
                Visite,
                Visite.id_presentation
                == Presentation.id_presentation,
            )
            .where(
                Visite.id_visite == visite_id
            )
        )

        return self.session.scalar(statement)

    def get_demande_id_for_presentation(
        self,
        presentation_id: int,
    ) -> int | None:
        statement = (
            select(DemandeVersion.id_demande)
            .join(
                Presentation,
                Presentation.id_demande_version
                == DemandeVersion.id_demande_version,
            )
            .where(
                Presentation.id_presentation
                == presentation_id
            )
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