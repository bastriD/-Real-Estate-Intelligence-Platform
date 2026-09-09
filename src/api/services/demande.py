from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.chasseur import Chasseur
from src.api.db.models.client import Client
from src.api.db.models.demande import Demande, DemandeVersion
from src.api.db.models.mandat import Mandat
from src.api.repositories.demande import DemandeRepository
from src.api.schemas.demande import (
    DemandeCreate,
    DemandeRevision,
    DemandeStatusUpdate,
)


class DemandeAlreadyExistsError(Exception):
    pass


class DemandeNotFoundError(Exception):
    pass


class MandatNotFoundForDemandeError(Exception):
    pass


class ClientNotFoundForDemandeError(Exception):
    pass


class ChasseurNotFoundForDemandeError(Exception):
    pass


class DemandeValidationError(Exception):
    pass


class DemandeService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = DemandeRepository(session)

    def list_demandes(self) -> list[Demande]:
        return self.repository.list_all()

    def get_demande(self, demande_id: int) -> Demande:
        demande = self.repository.get_by_id(demande_id)

        if demande is None:
            raise DemandeNotFoundError(
                f"Demande {demande_id} not found"
            )

        return demande

    def get_current_version(
        self,
        demande_id: int,
    ) -> DemandeVersion:
        self.get_demande(demande_id)

        version = self.repository.get_current_version(demande_id)

        if version is None:
            raise DemandeValidationError(
                f"Demande {demande_id} has no active version"
            )

        return version

    def get_history(
        self,
        demande_id: int,
    ) -> tuple[Demande, list[DemandeVersion]]:
        demande = self.get_demande(demande_id)
        versions = self.repository.list_versions(demande_id)

        return demande, versions

    def create_demande(
        self,
        payload: DemandeCreate,
    ) -> tuple[Demande, DemandeVersion]:
        if (
            payload.reference_demande is not None
            and self.repository.get_by_reference(
                payload.reference_demande
            )
            is not None
        ):
            raise DemandeAlreadyExistsError(
                "Demande with reference "
                f"{payload.reference_demande} already exists"
            )

        if payload.id_mandat is not None:
            self._ensure_mandat_exists(payload.id_mandat)
        self._validate_author(
            payload.auteur_client_id,
            payload.auteur_chasseur_id,
        )

        demande = Demande(
            reference_demande=payload.reference_demande,
            statut=payload.statut.value,
            id_mandat=payload.id_mandat,
        )

        try:
            demande = self.repository.create_demande(demande)

            version = DemandeVersion(
                numero_version=1,
                motif_modification=payload.motif_modification,
                ville=payload.ville,
                code_postal=payload.code_postal,
                type_bien=payload.type_bien,
                budget_min=payload.budget_min,
                budget_max=payload.budget_max,
                surface_min=payload.surface_min,
                nb_pieces_min=payload.nb_pieces_min,
                nb_chambres_min=payload.nb_chambres_min,
                dpe_max=(
                    payload.dpe_max.value
                    if payload.dpe_max is not None
                    else None
                ),
                criteres_souhaites=payload.criteres_souhaites,
                active=True,
                id_demande=demande.id_demande,
                auteur_client_id=payload.auteur_client_id,
                auteur_chasseur_id=payload.auteur_chasseur_id,
                auteur_systeme=payload.auteur_systeme,
            )

            version = self.repository.create_version(version)

            self.session.commit()

            return demande, version

        except IntegrityError as exc:
            self.session.rollback()

            raise DemandeValidationError(
                "Demande creation violates a database constraint"
            ) from exc

    def create_revision(
        self,
        demande_id: int,
        payload: DemandeRevision,
    ) -> DemandeVersion:
        self.get_demande(demande_id)

        self._validate_author(
            payload.auteur_client_id,
            payload.auteur_chasseur_id,
        )

        try:
            current = self.repository.get_current_version(
                demande_id,
                for_update=True,
            )

            if current is None:
                raise DemandeValidationError(
                    f"Demande {demande_id} has no active version"
                )

            new_version_number = current.numero_version + 1

            current.active = False
            self.session.flush()

            new_version = DemandeVersion(
                numero_version=new_version_number,
                motif_modification=payload.motif_modification,
                ville=payload.ville,
                code_postal=payload.code_postal,
                type_bien=payload.type_bien,
                budget_min=payload.budget_min,
                budget_max=payload.budget_max,
                surface_min=payload.surface_min,
                nb_pieces_min=payload.nb_pieces_min,
                nb_chambres_min=payload.nb_chambres_min,
                dpe_max=(
                    payload.dpe_max.value
                    if payload.dpe_max is not None
                    else None
                ),
                criteres_souhaites=payload.criteres_souhaites,
                active=True,
                id_demande=demande_id,
                auteur_client_id=payload.auteur_client_id,
                auteur_chasseur_id=payload.auteur_chasseur_id,
                auteur_systeme=payload.auteur_systeme,
            )

            new_version = self.repository.create_version(
                new_version
            )

            self.session.commit()

            return new_version

        except DemandeValidationError:
            self.session.rollback()
            raise

        except IntegrityError as exc:
            self.session.rollback()

            raise DemandeValidationError(
                "Demande revision violates a database constraint"
            ) from exc

    def update_status(
        self,
        demande_id: int,
        payload: DemandeStatusUpdate,
    ) -> Demande:
        demande = self.get_demande(demande_id)

        demande.statut = payload.statut.value

        try:
            self.session.commit()
            self.session.refresh(demande)

            return demande

        except IntegrityError as exc:
            self.session.rollback()

            raise DemandeValidationError(
                "Demande status update violates a database constraint"
            ) from exc

    def _ensure_mandat_exists(
        self,
        mandat_id: int,
    ) -> None:
        statement = select(Mandat.id_mandat).where(
            Mandat.id_mandat == mandat_id
        )

        if self.session.scalar(statement) is None:
            raise MandatNotFoundForDemandeError(
                f"Mandat {mandat_id} not found"
            )

    def _validate_author(
        self,
        client_id: int | None,
        chasseur_id: int | None,
    ) -> None:
        if client_id is not None:
            statement = select(Client.id_client).where(
                Client.id_client == client_id
            )

            if self.session.scalar(statement) is None:
                raise ClientNotFoundForDemandeError(
                    f"Client {client_id} not found"
                )

        if chasseur_id is not None:
            statement = select(Chasseur.id_chasseur).where(
                Chasseur.id_chasseur == chasseur_id
            )

            if self.session.scalar(statement) is None:
                raise ChasseurNotFoundForDemandeError(
                    f"Chasseur {chasseur_id} not found"
                )
