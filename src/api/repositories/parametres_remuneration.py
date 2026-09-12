from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.parametres_remuneration import ParametresRemuneration


class ParametresRemunerationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_effective(self, effective_date: date) -> ParametresRemuneration | None:
        stmt = (
            select(ParametresRemuneration)
            .where(
                ParametresRemuneration.actif.is_(True),
                ParametresRemuneration.date_debut_validite <= effective_date,
                (
                    ParametresRemuneration.date_fin_validite.is_(None)
                    | (ParametresRemuneration.date_fin_validite >= effective_date)
                ),
            )
            .order_by(
                ParametresRemuneration.date_debut_validite.desc(),
                ParametresRemuneration.id_parametres_remuneration.desc(),
            )
            .limit(1)
        )
        return self.db.scalar(stmt)