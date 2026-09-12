from datetime import date
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class BaremeCommission(Base):
    __tablename__ = "bareme_commission"
    __table_args__ = (
        CheckConstraint(
            "montant_min >= 0",
            name="ck_bareme_montant_min",
        ),
        CheckConstraint(
            "montant_max IS NULL OR montant_max >= montant_min",
            name="ck_bareme_montant_max",
        ),
        CheckConstraint(
            "taux_commission >= 0 AND taux_commission <= 1",
            name="ck_bareme_taux",
        ),
        CheckConstraint(
            "montant_fixe >= 0",
            name="ck_bareme_montant_fixe",
        ),
        CheckConstraint(
            (
                "date_fin_validite IS NULL "
                "OR date_fin_validite >= date_debut_validite"
            ),
            name="ck_bareme_dates",
        ),
        CheckConstraint(
            "statut_usage IN ('HISTORIQUE', 'APPROUVE')",
            name="ck_bareme_commission_statut_usage",
        ),
        {"schema": "real_estate"},
    )

    id_bareme: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    montant_min: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    montant_max: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    taux_commission: Mapped[Decimal] = mapped_column(
        Numeric(7, 4),
        nullable=False,
    )

    montant_fixe: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default=text("0"),
    )

    date_debut_validite: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    date_fin_validite: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    actif: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    id_chasseur: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.chasseur.id_chasseur",
            ondelete="RESTRICT",
            name="fk_bareme_commission_chasseur",
        ),
        nullable=True,
        index=True,
    )

    statut_usage: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'HISTORIQUE'"),
    )