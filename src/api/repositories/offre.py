from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.demande import DemandeVersion
from src.api.db.models.demande_affectation import DemandeAffectation
from src.api.db.models.offre import Offre
from src.api.db.models.presentation import Presentation


class OffreRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Offre]:
        statement = select(Offre).order_by(
            Offre.id_presentation,
            Offre.numero_version,
        )

        return list(
            self.session.scalars(statement).all()
        )

    def list_accessible_by_chasseur(
        self,
        chasseur_id: int,
        presentation_id: int | None = None,
    ) -> list[Offre]:
        statement = (
            select(Offre)
            .join(
                Presentation,
                Presentation.id_presentation
                == Offre.id_presentation,
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
                Offre.id_presentation
                == presentation_id
            )

        statement = statement.order_by(
            Offre.id_presentation,
            Offre.numero_version,
        )

        return list(
            self.session.scalars(statement).all()
        )

    def get_by_id(
        self,
        offre_id: int,
    ) -> Offre | None:
        statement = select(Offre).where(
            Offre.id_offre == offre_id
        )

        return self.session.scalar(statement)
    def get_by_id_for_update(
        self,
        offre_id: int,
    ) -> Offre | None:
        statement = (
            select(Offre)
            .where(
                Offre.id_offre == offre_id
            )
            .with_for_update()
        )

        return self.session.scalar(statement)
    
    def get_demande_id(
        self,
        offre_id: int,
    ) -> int | None:
        statement = (
            select(DemandeVersion.id_demande)
            .join(
                Presentation,
                Presentation.id_demande_version
                == DemandeVersion.id_demande_version,
            )
            .join(
                Offre,
                Offre.id_presentation
                == Presentation.id_presentation,
            )
            .where(
                Offre.id_offre == offre_id
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
    ) -> list[Offre]:
        statement = (
            select(Offre)
            .where(
                Offre.id_presentation
                == presentation_id
            )
            .order_by(Offre.numero_version)
        )

        return list(
            self.session.scalars(statement).all()
        )

    def get_latest_for_presentation(
        self,
        presentation_id: int,
        *,
        for_update: bool = False,
    ) -> Offre | None:
        statement = (
            select(Offre)
            .where(
                Offre.id_presentation
                == presentation_id
            )
            .order_by(
                Offre.numero_version.desc()
            )
            .limit(1)
        )

        if for_update:
            statement = statement.with_for_update()

        return self.session.scalar(statement)

    def create(
        self,
        offre: Offre,
    ) -> Offre:
        self.session.add(offre)
        self.session.flush()
        self.session.refresh(offre)

        return offre
    def save(
        self,
        offre: Offre,
    ) -> Offre:
        self.session.add(offre)
        self.session.flush()
        self.session.refresh(offre)

        return offre