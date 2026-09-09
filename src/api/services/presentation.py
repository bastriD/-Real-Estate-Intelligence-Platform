from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.demande import DemandeVersion
from src.api.db.models.presentation import Presentation
from src.api.repositories.presentation import PresentationRepository
from src.api.schemas.presentation import (
    PresentationCreate,
    PresentationUpdate,
)
from src.api.services.audit_log import AuditLogService


class PresentationNotFoundError(Exception):
    pass


class DemandeVersionNotFoundForPresentationError(Exception):
    pass


class BienNotFoundForPresentationError(Exception):
    pass


class PresentationAlreadyExistsError(Exception):
    pass


class PresentationValidationError(Exception):
    pass


class PresentationDeleteConflictError(Exception):
    pass


class PresentationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = PresentationRepository(session)
        self.audit = AuditLogService(session)

    def list_presentations(
        self,
        demande_version_id: int | None = None,
        bien_id: int | None = None,
    ) -> list[Presentation]:
        if demande_version_id is not None:
            return self.repository.list_by_demande_version(
                demande_version_id
            )

        if bien_id is not None:
            return self.repository.list_by_bien(bien_id)

        return self.repository.list_all()

    def get_presentation(
        self,
        presentation_id: int,
    ) -> Presentation:
        presentation = self.repository.get_by_id(
            presentation_id
        )

        if presentation is None:
            raise PresentationNotFoundError

        return presentation

    def create_presentation(
        self,
        payload: PresentationCreate,
        utilisateur: str | None = None,
    ) -> Presentation:
        self._ensure_demande_version_exists(
            payload.id_demande_version
        )
        self._ensure_bien_exists(payload.id_bien)

        existing = self.repository.get_by_demande_and_bien(
            demande_version_id=payload.id_demande_version,
            bien_id=payload.id_bien,
        )

        if existing is not None:
            raise PresentationAlreadyExistsError

        presentation = Presentation(
            id_demande_version=payload.id_demande_version,
            id_bien=payload.id_bien,
            score_matching=payload.score_matching,
            statut=payload.statut.value,
            date_presentation=payload.date_presentation,
        )

        try:
            presentation = self.repository.create(
                presentation
            )

            self.audit.log_change(
                table_name="presentation",
                operation="INSERT",
                record_id=presentation.id_presentation,
                utilisateur=utilisateur,
                nouvelle_valeur=self._presentation_snapshot(
                    presentation
                ),
                contexte={
                    "source": "api",
                    "action": "create_presentation",
                },
            )

            self.session.commit()
            self.session.refresh(presentation)

            return presentation

        except IntegrityError as exc:
            self.session.rollback()
            raise PresentationValidationError from exc

    def update_presentation(
        self,
        presentation_id: int,
        payload: PresentationUpdate,
        utilisateur: str | None = None,
    ) -> Presentation:
        presentation = self.get_presentation(
            presentation_id
        )

        ancienne_valeur = self._presentation_snapshot(
            presentation
        )

        update_data = payload.model_dump(
            exclude_unset=True
        )

        if "statut" in update_data:
            update_data["statut"] = update_data[
                "statut"
            ].value

        for field, value in update_data.items():
            setattr(presentation, field, value)

        nouvelle_valeur = self._presentation_snapshot(
            presentation
        )

        try:
            self.audit.log_change(
                table_name="presentation",
                operation="UPDATE",
                record_id=presentation.id_presentation,
                utilisateur=utilisateur,
                ancienne_valeur=ancienne_valeur,
                nouvelle_valeur=nouvelle_valeur,
                contexte={
                    "source": "api",
                    "action": "update_presentation",
                },
            )

            self.session.commit()
            self.session.refresh(presentation)

            return presentation

        except IntegrityError as exc:
            self.session.rollback()
            raise PresentationValidationError from exc

    def delete_presentation(
        self,
        presentation_id: int,
        utilisateur: str | None = None,
    ) -> None:
        presentation = self.get_presentation(
            presentation_id
        )

        ancienne_valeur = self._presentation_snapshot(
            presentation
        )

        try:
            self.repository.delete(presentation)

            self.audit.log_change(
                table_name="presentation",
                operation="DELETE",
                record_id=presentation.id_presentation,
                utilisateur=utilisateur,
                ancienne_valeur=ancienne_valeur,
                contexte={
                    "source": "api",
                    "action": "delete_presentation",
                },
            )

            self.session.commit()

        except IntegrityError as exc:
            self.session.rollback()
            raise PresentationDeleteConflictError from exc

    @staticmethod
    def _presentation_snapshot(
        presentation: Presentation,
    ) -> dict[str, object]:
        return {
            "id_presentation": presentation.id_presentation,
            "id_demande_version": presentation.id_demande_version,
            "id_bien": presentation.id_bien,
            "score_matching": (
                str(presentation.score_matching)
                if presentation.score_matching is not None
                else None
            ),
            "statut": presentation.statut,
            "date_presentation": (
                presentation.date_presentation.isoformat()
                if presentation.date_presentation is not None
                else None
            ),
        }

    def _ensure_demande_version_exists(
        self,
        demande_version_id: int,
    ) -> None:
        statement = select(
            DemandeVersion.id_demande_version
        ).where(
            DemandeVersion.id_demande_version
            == demande_version_id
        )

        result = self.session.scalar(statement)

        if result is None:
            raise DemandeVersionNotFoundForPresentationError

    def _ensure_bien_exists(
        self,
        bien_id: int,
    ) -> None:
        result = self.session.execute(
            select(1).where(
                self._bien_exists_condition(bien_id)
            )
        ).scalar_one_or_none()

        if result is None:
            raise BienNotFoundForPresentationError

    @staticmethod
    def _bien_exists_condition(
        bien_id: int,
    ):
        from src.api.db.models.bien import Bien

        return Bien.id_bien == bien_id