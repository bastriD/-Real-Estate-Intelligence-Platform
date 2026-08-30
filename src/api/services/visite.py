from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.presentation import Presentation
from src.api.db.models.visite import Visite
from src.api.repositories.visite import VisiteRepository
from src.api.schemas.visite import VisiteCreate, VisiteUpdate


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

    def list_visites(
        self,
        presentation_id: int | None = None,
    ) -> list[Visite]:
        if presentation_id is not None:
            return self.repository.list_by_presentation(
                presentation_id
            )

        return self.repository.list_all()

    def get_visite(
        self,
        visite_id: int,
    ) -> Visite:
        visite = self.repository.get_by_id(visite_id)

        if visite is None:
            raise VisiteNotFoundError

        return visite

    def create_visite(
        self,
        payload: VisiteCreate,
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
            self.session.commit()
            self.session.refresh(visite)
            return visite

        except IntegrityError as exc:
            self.session.rollback()
            raise VisiteValidationError from exc

    def update_visite(
        self,
        visite_id: int,
        payload: VisiteUpdate,
    ) -> Visite:
        visite = self.get_visite(visite_id)

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
            self.session.commit()
            self.session.refresh(visite)
            return visite

        except IntegrityError as exc:
            self.session.rollback()
            raise VisiteValidationError from exc

    def delete_visite(
        self,
        visite_id: int,
    ) -> None:
        visite = self.get_visite(visite_id)

        try:
            self.repository.delete(visite)
            self.session.commit()

        except IntegrityError as exc:
            self.session.rollback()
            raise VisiteDeleteConflictError from exc

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