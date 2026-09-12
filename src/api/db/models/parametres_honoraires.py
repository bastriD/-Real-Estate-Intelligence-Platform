from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Numeric,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class ParametresHonoraires(Base):
    __tablename__ = "parametres_honoraires"
    __table_args__ = (
        CheckConstraint(
            (
                "date_fin_validite IS NULL "
                "OR date_fin_validite >= date_debut_validite"
            ),
            name="ck_parametres_honoraires_dates",
        ),
        CheckConstraint(
            "montant_fixe >= 0",
            name="ck_parametres_honoraires_montant_fixe",
        ),
        CheckConstraint(
            (
                "taux_pourcentage >= 0 "
                "AND taux_pourcentage <= 1"
            ),
            name="ck_parametres_honoraires_taux",
        ),
        {"schema": "real_estate"},
    )

    id_parametres_honoraires: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    date_debut_validite: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    date_fin_validite: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    montant_fixe: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    taux_pourcentage: Mapped[Decimal] = mapped_column(
        Numeric(7, 4),
        nullable=False,
    )

    actif: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )