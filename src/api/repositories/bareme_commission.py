from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.db.models.bareme_commission import BaremeCommission


class BaremeCommissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_effective_for_amount(
        self,
        *,
        id_chasseur: int,
        amount: Decimal,
        effective_date: date,
    ) -> BaremeCommission | None:
        common_filters = (
            BaremeCommission.actif.is_(True),
            BaremeCommission.statut_usage == "APPROUVE",
            BaremeCommission.date_debut_validite <= effective_date,
            (
                BaremeCommission.date_fin_validite.is_(None)
                | (BaremeCommission.date_fin_validite >= effective_date)
            ),
            BaremeCommission.montant_min <= amount,
            (
                BaremeCommission.montant_max.is_(None)
                | (amount < BaremeCommission.montant_max)
            ),
        )

        hunter_stmt = (
            select(BaremeCommission)
            .where(
                *common_filters,
                BaremeCommission.id_chasseur == id_chasseur,
            )
            .order_by(
                BaremeCommission.date_debut_validite.desc(),
                BaremeCommission.montant_min.desc(),
            )
            .limit(1)
        )

        result = self.db.scalar(hunter_stmt)
        if result is not None:
            return result

        default_stmt = (
            select(BaremeCommission)
            .where(
                *common_filters,
                BaremeCommission.id_chasseur.is_(None),
            )
            .order_by(
                BaremeCommission.date_debut_validite.desc(),
                BaremeCommission.montant_min.desc(),
            )
            .limit(1)
        )

        return self.db.scalar(default_stmt)