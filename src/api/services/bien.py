from sqlalchemy.orm import Session

from src.api.db.models.bien import Bien
from src.api.repositories.bien import BienRepository


class BienNotFoundError(Exception):
    pass


class BienService:
    def __init__(self, session: Session) -> None:
        self.repository = BienRepository(session)

    def list_biens(
        self,
        ville: str | None = None,
        statut: str | None = None,
        type_bien: str | None = None,
    ) -> list[Bien]:
        if ville is not None:
            return self.repository.list_by_ville(ville)

        if statut is not None:
            return self.repository.list_by_statut(statut)

        if type_bien is not None:
            return self.repository.list_by_type(type_bien)

        return self.repository.list_all()

    def get_bien(
        self,
        bien_id: int,
    ) -> Bien:
        bien = self.repository.get_by_id(bien_id)

        if bien is None:
            raise BienNotFoundError

        return bien