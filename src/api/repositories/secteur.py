from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.secteur import Secteur


class SecteurRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_active(self) -> list[Secteur]:
        return list(self.session.scalars(select(Secteur).where(Secteur.actif.is_(True))
            .order_by(Secteur.ville, Secteur.quartier, Secteur.id_secteur)).all())

    def get_active(self, sector_id: int) -> Secteur | None:
        return self.session.scalar(select(Secteur).where(
            Secteur.id_secteur == sector_id, Secteur.actif.is_(True)))
