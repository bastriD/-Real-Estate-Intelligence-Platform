from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class PalierPerformance(Base):
    __tablename__ = "palier_performance"
    __table_args__ = (
        CheckConstraint(
            "critere IN ('DELAI_SEMAINES', 'VISITES')",
            name="ck_palier_performance_critere",
        ),
        CheckConstraint(
            "ordre >= 1",
            name="ck_palier_performance_ordre",
        ),
        CheckConstraint(
            "borne_max IS NULL OR borne_max >= 0",
            name="ck_palier_performance_borne",
        ),
        CheckConstraint(
            "note >= 0 AND note <= 100",
            name="ck_palier_performance_note",
        ),
        UniqueConstraint(
            "id_parametres_remuneration",
            "critere",
            "ordre",
            name="uq_palier_performance_ordre",
        ),
        {"schema": "real_estate"},
    )

    id_palier_performance: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_parametres_remuneration: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            (
                "real_estate.parametres_remuneration."
                "id_parametres_remuneration"
            ),
            ondelete="RESTRICT",
            name="fk_palier_performance_parametres",
        ),
        nullable=False,
        index=True,
    )

    critere: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    ordre: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    borne_max: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    note: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )