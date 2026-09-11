from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.demande import DemandeVersion
from src.api.db.models.demande_affectation import DemandeAffectation
from src.api.db.models.presentation import Presentation


class PresentationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Presentation]:
        statement = select(Presentation).order_by(
            Presentation.id_presentation
        )
        return list(self.session.scalars(statement).all())

    def list_accessible_by_chasseur(
        self,
        chasseur_id: int,
        demande_version_id: int | None = None,
        bien_id: int | None = None,
    ) -> list[Presentation]:
        statement = (
            select(Presentation)
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

        if demande_version_id is not None:
            statement = statement.where(
                Presentation.id_demande_version
                == demande_version_id
            )

        if bien_id is not None:
            statement = statement.where(
                Presentation.id_bien == bien_id
            )

        statement = statement.order_by(
            Presentation.id_presentation
        )

        return list(self.session.scalars(statement).all())

    def get_by_id(
        self,
        presentation_id: int,
    ) -> Presentation | None:
        statement = select(Presentation).where(
            Presentation.id_presentation == presentation_id
        )
        return self.session.scalar(statement)

    def get_demande_id(
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

    def get_demande_id_for_version(
        self,
        demande_version_id: int,
    ) -> int | None:
        statement = select(
            DemandeVersion.id_demande
        ).where(
            DemandeVersion.id_demande_version
            == demande_version_id
        )

        return self.session.scalar(statement)

    def get_by_demande_and_bien(
        self,
        demande_version_id: int,
        bien_id: int,
    ) -> Presentation | None:
        statement = select(Presentation).where(
            Presentation.id_demande_version
            == demande_version_id,
            Presentation.id_bien == bien_id,
        )
        return self.session.scalar(statement)

    def list_by_demande_version(
        self,
        demande_version_id: int,
    ) -> list[Presentation]:
        statement = (
            select(Presentation)
            .where(
                Presentation.id_demande_version
                == demande_version_id
            )
            .order_by(Presentation.id_presentation)
        )
        return list(self.session.scalars(statement).all())

    def list_by_bien(
        self,
        bien_id: int,
    ) -> list[Presentation]:
        statement = (
            select(Presentation)
            .where(Presentation.id_bien == bien_id)
            .order_by(Presentation.id_presentation)
        )
        return list(self.session.scalars(statement).all())

    def create(
        self,
        presentation: Presentation,
    ) -> Presentation:
        self.session.add(presentation)
        self.session.flush()
        self.session.refresh(presentation)
        return presentation

    def delete(
        self,
        presentation: Presentation,
    ) -> None:
        self.session.delete(presentation)
        self.session.flush()