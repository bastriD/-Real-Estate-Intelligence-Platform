from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.api.db.models.demande import Demande, DemandeVersion
from src.api.db.models.demande_affectation import DemandeAffectation


class DemandeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Demande]:
        statement = select(Demande).order_by(
            Demande.id_demande
        )

        return list(
            self.session.scalars(statement).all()
        )

    def list_accessible_by_chasseur(
        self,
        chasseur_id: int,
    ) -> list[Demande]:
        statement = (
            select(Demande)
            .join(
                DemandeAffectation,
                DemandeAffectation.id_demande
                == Demande.id_demande,
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
            .order_by(Demande.id_demande)
        )

        return list(
            self.session.scalars(statement).all()
        )
    def list_owned_by_client(
        self,
        client_id: int,
    ) -> list[Demande]:
        statement = (
            select(Demande)
            .where(
                Demande.id_client == client_id
            )
            .order_by(Demande.id_demande)
        )

        return list(
            self.session.scalars(statement).all()
        )
    def get_by_id(
        self,
        demande_id: int,
    ) -> Demande | None:
        statement = select(Demande).where(
            Demande.id_demande == demande_id
        )

        return self.session.scalar(statement)

    def get_by_reference(
        self,
        reference_demande: str,
    ) -> Demande | None:
        statement = select(Demande).where(
            Demande.reference_demande
            == reference_demande
        )

        return self.session.scalar(statement)

    def create_demande(
        self,
        demande: Demande,
    ) -> Demande:
        self.session.add(demande)
        self.session.flush()
        self.session.refresh(demande)

        return demande

    def get_current_version(
        self,
        demande_id: int,
        *,
        for_update: bool = False,
    ) -> DemandeVersion | None:
        statement = select(DemandeVersion).options(selectinload(DemandeVersion.secteur_links)).where(
            DemandeVersion.id_demande
            == demande_id,
            DemandeVersion.active.is_(True),
        )

        if for_update:
            statement = statement.with_for_update()

        return self.session.scalar(statement)

    def list_versions(
        self,
        demande_id: int,
    ) -> list[DemandeVersion]:
        statement = (
            select(DemandeVersion).options(selectinload(DemandeVersion.secteur_links))
            .where(
                DemandeVersion.id_demande
                == demande_id
            )
            .order_by(
                DemandeVersion.numero_version
            )
        )

        return list(
            self.session.scalars(statement).all()
        )

    def create_version(
        self,
        version: DemandeVersion,
    ) -> DemandeVersion:
        self.session.add(version)
        self.session.flush()
        self.session.refresh(version)

        return version
