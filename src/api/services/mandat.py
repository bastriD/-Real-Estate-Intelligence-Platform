from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.chasseur import Chasseur
from src.api.db.models.client import Client
from src.api.db.models.mandat import Mandat
from src.api.repositories.mandat import MandatRepository
from src.api.schemas.mandat import MandatCreate, MandatUpdate
from src.api.services.audit_log import AuditLogService


class MandatNotFoundError(Exception):
    pass


class MandatAlreadyExistsError(Exception):
    pass


class ClientNotFoundForMandatError(Exception):
    pass


class ChasseurNotFoundForMandatError(Exception):
    pass


class MandatValidationError(Exception):
    pass


class MandatService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = MandatRepository(session)
        self.audit = AuditLogService(session)

    def list_mandats(self) -> list[Mandat]:
        return self.repository.list_all()

    def get_mandat(self, mandat_id: int) -> Mandat:
        mandat = self.repository.get_by_id(mandat_id)

        if mandat is None:
            raise MandatNotFoundError(
                f"Mandat {mandat_id} not found"
            )

        return mandat

    def list_by_client(
        self,
        client_id: int,
    ) -> list[Mandat]:
        self._ensure_client_exists(client_id)
        return self.repository.list_by_client(client_id)

    def list_by_chasseur(
        self,
        chasseur_id: int,
    ) -> list[Mandat]:
        self._ensure_chasseur_exists(chasseur_id)
        return self.repository.list_by_chasseur(chasseur_id)

    def create_mandat(
        self,
        payload: MandatCreate,
        utilisateur: str | None = None,
    ) -> Mandat:
        if self.repository.get_by_reference(
            payload.reference_mandat
        ):
            raise MandatAlreadyExistsError(
                f"Mandat with reference "
                f"{payload.reference_mandat} already exists"
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

            self.audit.log_change(
                table_name="mandat",
                operation="INSERT",
                record_id=mandat.id_mandat,
                utilisateur=utilisateur,
                nouvelle_valeur=self._mandat_snapshot(
                    mandat
                ),
                contexte={
                    "source": "api",
                    "action": "create_mandat",
                },
            )

            self.session.commit()
            return mandat

        except IntegrityError as exc:
            self.session.rollback()
            raise MandatValidationError(
                "Mandat creation violates a database constraint"
            ) from exc

        except Exception:
            self.session.rollback()
            raise

    def update_mandat(
        self,
        mandat_id: int,
        payload: MandatUpdate,
        utilisateur: str | None = None,
    ) -> Mandat:
        mandat = self.get_mandat(mandat_id)
        ancienne_valeur = self._mandat_snapshot(mandat)

        update_data = payload.model_dump(
            exclude_unset=True
        )

        if "reference_mandat" in update_data:
            reference = update_data["reference_mandat"]

            existing = self.repository.get_by_reference(
                reference
            )

            if (
                existing is not None
                and existing.id_mandat != mandat_id
            ):
                raise MandatAlreadyExistsError(
                    f"Mandat with reference "
                    f"{reference} already exists"
                )

        if "id_client" in update_data:
            self._ensure_client_exists(
                update_data["id_client"]
            )

        if "id_chasseur" in update_data:
            self._ensure_chasseur_exists(
                update_data["id_chasseur"]
            )

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
            self.audit.log_change(
                table_name="mandat",
                operation="UPDATE",
                record_id=mandat.id_mandat,
                utilisateur=utilisateur,
                ancienne_valeur=ancienne_valeur,
                nouvelle_valeur=self._mandat_snapshot(
                    mandat
                ),
                contexte={
                    "source": "api",
                    "action": "update_mandat",
                },
            )

            self.session.commit()
            self.session.refresh(mandat)
            return mandat

        except IntegrityError as exc:
            self.session.rollback()
            raise MandatValidationError(
                "Mandat update violates a database constraint"
            ) from exc

        except Exception:
            self.session.rollback()
            raise

    def delete_mandat(
        self,
        mandat_id: int,
        utilisateur: str | None = None,
    ) -> None:
        mandat = self.get_mandat(mandat_id)
        ancienne_valeur = self._mandat_snapshot(mandat)

        try:
            self.repository.delete(mandat)

            self.audit.log_change(
                table_name="mandat",
                operation="DELETE",
                record_id=mandat.id_mandat,
                utilisateur=utilisateur,
                ancienne_valeur=ancienne_valeur,
                contexte={
                    "source": "api",
                    "action": "delete_mandat",
                },
            )

            self.session.commit()

        except IntegrityError as exc:
            self.session.rollback()
            raise MandatValidationError(
                "Mandat cannot be deleted because "
                "it is referenced by other records"
            ) from exc

        except Exception:
            self.session.rollback()
            raise

    @staticmethod
    def _mandat_snapshot(
        mandat: Mandat,
    ) -> dict[str, object]:
        return {
            "id_mandat": mandat.id_mandat,
            "reference_mandat": mandat.reference_mandat,
            "type_mandat": mandat.type_mandat,
            "date_signature": (
                mandat.date_signature.isoformat()
                if mandat.date_signature is not None
                else None
            ),
            "mode_signature": mandat.mode_signature,
            "date_debut": (
                mandat.date_debut.isoformat()
                if mandat.date_debut is not None
                else None
            ),
            "date_fin": (
                mandat.date_fin.isoformat()
                if mandat.date_fin is not None
                else None
            ),
            "statut": mandat.statut,
            "commentaire": mandat.commentaire,
            "id_client": mandat.id_client,
            "id_chasseur": mandat.id_chasseur,
        }

    def _ensure_client_exists(
        self,
        client_id: int,
    ) -> None:
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
            .where(
                Chasseur.id_chasseur == chasseur_id
            )
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
                "date_fin must be greater than or equal "
                "to date_debut"
            )