from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.parametres_honoraires import ParametresHonoraires


class ParametresHonorairesRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_effective(self, effective_date: date) -> ParametresHonoraires | None:
        stmt = (
            select(ParametresHonoraires)
            .where(
                ParametresHonoraires.actif.is_(True),
                ParametresHonoraires.date_debut_validite <= effective_date,
                (
                    ParametresHonoraires.date_fin_validite.is_(None)
                    | (ParametresHonoraires.date_fin_validite >= effective_date)
                ),
            )
            .order_by(
                ParametresHonoraires.date_debut_validite.desc(),
                ParametresHonoraires.id_parametres_honoraires.desc(),
            )
            .limit(1)
        )
        return self.db.scalar(stmt)