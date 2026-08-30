from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.chasseur import Chasseur
from src.api.db.models.client import Client
from src.api.db.models.mandat import Mandat
from src.api.repositories.mandat import MandatRepository
from src.api.schemas.mandat import MandatCreate, MandatUpdate


class MandatAlreadyExistsError(Exception):
    pass


class MandatNotFoundError(Exception):
    pass


class MandatValidationError(Exception):
    pass


class ClientNotFoundForMandatError(Exception):
    pass


class ChasseurNotFoundForMandatError(Exception):
    pass


class MandatService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = MandatRepository(session)

    def list_mandats(self) -> list[Mandat]:
        return self.repository.list_all()

    def get_mandat(self, mandat_id: int) -> Mandat:
        mandat = self.repository.get_by_id(mandat_id)

        if mandat is None:
            raise MandatNotFoundError(
                f"Mandat {mandat_id} not found"
            )

        return mandat

    def list_by_client(self, client_id: int) -> list[Mandat]:
        self._ensure_client_exists(client_id)
        return self.repository.list_by_client(client_id)

    def list_by_chasseur(self, chasseur_id: int) -> list[Mandat]:
        self._ensure_chasseur_exists(chasseur_id)
        return self.repository.list_by_chasseur(chasseur_id)

    def create_mandat(self, payload: MandatCreate) -> Mandat:
        if self.repository.get_by_reference(payload.reference_mandat):
            raise MandatAlreadyExistsError(
                f"Mandat with reference {payload.reference_mandat} already exists"
            )

        self._ensure_client_exists(payload.id_client)
        self._ensure_chasseur_exists(payload.id_chasseur)

        self._validate_dates(
            payload.date_debut,
            payload.date_fin,
        )

        mandat = Mandat(
            reference_mandat=payload.reference_mandat,
            type_mandat=payload.type_mandat.value,
            date_signature=payload.date_signature,
            mode_signature=payload.mode_signature.value,
            date_debut=payload.date_debut,
            date_fin=payload.date_fin,
            statut=payload.statut.value,
            commentaire=payload.commentaire,
            id_client=payload.id_client,
            id_chasseur=payload.id_chasseur,
        )

        try:
            mandat = self.repository.create(mandat)
            self.session.commit()
            return mandat

        except IntegrityError as exc:
            self.session.rollback()
            raise MandatValidationError(
                "Mandat creation violates a database constraint"
            ) from exc

    def update_mandat(
        self,
        mandat_id: int,
        payload: MandatUpdate,
    ) -> Mandat:
        mandat = self.get_mandat(mandat_id)

        update_data = payload.model_dump(
            exclude_unset=True
        )

        if "reference_mandat" in update_data:
            reference = update_data["reference_mandat"]

            existing = self.repository.get_by_reference(reference)

            if (
                existing is not None
                and existing.id_mandat != mandat_id
            ):
                raise MandatAlreadyExistsError(
                    f"Mandat with reference {reference} already exists"
                )

        if "id_client" in update_data:
            self._ensure_client_exists(update_data["id_client"])

        if "id_chasseur" in update_data:
            self._ensure_chasseur_exists(update_data["id_chasseur"])

        new_date_debut = update_data.get(
            "date_debut",
            mandat.date_debut,
        )
        new_date_fin = update_data.get(
            "date_fin",
            mandat.date_fin,
        )

        self._validate_dates(
            new_date_debut,
            new_date_fin,
        )

        for enum_field in (
            "type_mandat",
            "mode_signature",
            "statut",
        ):
            if enum_field in update_data:
                update_data[enum_field] = update_data[
                    enum_field
                ].value

        for field_name, value in update_data.items():
            setattr(mandat, field_name, value)

        try:
            self.session.commit()
            self.session.refresh(mandat)
            return mandat

        except IntegrityError as exc:
            self.session.rollback()
            raise MandatValidationError(
                "Mandat update violates a database constraint"
            ) from exc

    def delete_mandat(self, mandat_id: int) -> None:
        mandat = self.get_mandat(mandat_id)

        try:
            self.repository.delete(mandat)
            self.session.commit()

        except IntegrityError as exc:
            self.session.rollback()
            raise MandatValidationError(
                "Mandat cannot be deleted because it is referenced by other records"
            ) from exc

    def _ensure_client_exists(self, client_id: int) -> None:
        statement = (
            select(Client.id_client)
            .where(Client.id_client == client_id)
        )

        if self.session.scalar(statement) is None:
            raise ClientNotFoundForMandatError(
                f"Client {client_id} not found"
            )

    def _ensure_chasseur_exists(
        self,
        chasseur_id: int,
    ) -> None:
        statement = (
            select(Chasseur.id_chasseur)
            .where(Chasseur.id_chasseur == chasseur_id)
        )

        if self.session.scalar(statement) is None:
            raise ChasseurNotFoundForMandatError(
                f"Chasseur {chasseur_id} not found"
            )

    @staticmethod
    def _validate_dates(
        date_debut: date,
        date_fin: date,
    ) -> None:
        if date_fin < date_debut:
            raise MandatValidationError(
                "date_fin must be greater than or equal to date_debut"
            )