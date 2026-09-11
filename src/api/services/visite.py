from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.presentation import Presentation
from src.api.db.models.visite import Visite
from src.api.repositories.visite import VisiteRepository
from src.api.schemas.visite import VisiteCreate, VisiteUpdate
from src.api.services.audit_log import AuditLogService


class VisiteNotFoundError(Exception):
    pass


class PresentationNotFoundForVisiteError(Exception):
    pass


class VisiteValidationError(Exception):
    pass


class VisiteDeleteConflictError(Exception):
    pass


class VisiteService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = VisiteRepository(session)
        self.audit = AuditLogService(session)

    def list_visites(
        self,
        presentation_id: int | None = None,
    ) -> list[Visite]:
        if presentation_id is not None:
            return self.repository.list_by_presentation(
                presentation_id
            )

        return self.repository.list_all()

    def list_visites_for_chasseur(
        self,
        chasseur_id: int,
        presentation_id: int | None = None,
    ) -> list[Visite]:
        return self.repository.list_accessible_by_chasseur(
            chasseur_id=chasseur_id,
            presentation_id=presentation_id,
        )

    def get_visite(
        self,
        visite_id: int,
    ) -> Visite:
        visite = self.repository.get_by_id(visite_id)

        if visite is None:
            raise VisiteNotFoundError

        return visite

    def get_demande_id_for_visite(
        self,
        visite_id: int,
    ) -> int:
        demande_id = self.repository.get_demande_id(
            visite_id
        )

        if demande_id is None:
            raise VisiteNotFoundError

        return demande_id

    def get_demande_id_for_presentation(
        self,
        presentation_id: int,
    ) -> int:
        demande_id = (
            self.repository.get_demande_id_for_presentation(
                presentation_id
            )
        )

        if demande_id is None:
            raise PresentationNotFoundForVisiteError

        return demande_id

    def create_visite(
        self,
        payload: VisiteCreate,
        utilisateur: str | None = None,
    ) -> Visite:
        self._ensure_presentation_exists(
            payload.id_presentation
        )

        visite = Visite(
            date_visite=payload.date_visite,
            statut=payload.statut.value,
            compte_rendu=payload.compte_rendu,
            note=payload.note,
            photos=payload.photos,
            id_presentation=payload.id_presentation,
        )

        try:
            visite = self.repository.create(visite)

            self.audit.log_change(
                table_name="visite",
                operation="INSERT",
                record_id=visite.id_visite,
                utilisateur=utilisateur,
                nouvelle_valeur=self._visite_snapshot(
                    visite
                ),
                contexte={
                    "source": "api",
                    "action": "create_visite",
                },
            )

            self.session.commit()
            self.session.refresh(visite)

            return visite

        except IntegrityError as exc:
            self.session.rollback()
            raise VisiteValidationError from exc

        except Exception:
            self.session.rollback()
            raise

    def update_visite(
        self,
        visite_id: int,
        payload: VisiteUpdate,
        utilisateur: str | None = None,
    ) -> Visite:
        visite = self.get_visite(visite_id)

        ancienne_valeur = self._visite_snapshot(
            visite
        )

        update_data = payload.model_dump(
            exclude_unset=True
        )

        if "statut" in update_data:
            update_data["statut"] = update_data[
                "statut"
            ].value

        for field, value in update_data.items():
            setattr(visite, field, value)

        try:
            self.audit.log_change(
                table_name="visite",
                operation="UPDATE",
                record_id=visite.id_visite,
                utilisateur=utilisateur,
                ancienne_valeur=ancienne_valeur,
                nouvelle_valeur=self._visite_snapshot(
                    visite
                ),
                contexte={
                    "source": "api",
                    "action": "update_visite",
                },
            )

            self.session.commit()
            self.session.refresh(visite)

            return visite

        except IntegrityError as exc:
            self.session.rollback()
            raise VisiteValidationError from exc

        except Exception:
            self.session.rollback()
            raise

    def delete_visite(
        self,
        visite_id: int,
        utilisateur: str | None = None,
    ) -> None:
        visite = self.get_visite(visite_id)

        ancienne_valeur = self._visite_snapshot(
            visite
        )

        try:
            self.repository.delete(visite)

            self.audit.log_change(
                table_name="visite",
                operation="DELETE",
                record_id=visite.id_visite,
                utilisateur=utilisateur,
                ancienne_valeur=ancienne_valeur,
                contexte={
                    "source": "api",
                    "action": "delete_visite",
                },
            )

            self.session.commit()

        except IntegrityError as exc:
            self.session.rollback()
            raise VisiteDeleteConflictError from exc

        except Exception:
            self.session.rollback()
            raise

    @staticmethod
    def _visite_snapshot(
        visite: Visite,
    ) -> dict[str, object]:
        return {
            "id_visite": visite.id_visite,
            "id_presentation": visite.id_presentation,
            "date_visite": (
                visite.date_visite.isoformat()
                if visite.date_visite is not None
                else None
            ),
            "statut": visite.statut,
            "compte_rendu": visite.compte_rendu,
            "note": visite.note,
            "photos": (
                list(visite.photos)
                if visite.photos is not None
                else None
            ),
        }

    def _ensure_presentation_exists(
        self,
        presentation_id: int,
    ) -> None:
        statement = select(
            Presentation.id_presentation
        ).where(
            Presentation.id_presentation
            == presentation_id
        )

        result = self.session.scalar(statement)

        if result is None:
            raise PresentationNotFoundForVisiteError