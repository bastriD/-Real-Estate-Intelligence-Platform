from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class Presentation(Base):
    __tablename__ = "presentation"
    __table_args__ = (
        UniqueConstraint(
            "id_demande_version",
            "id_bien",
            name="uq_presentation_demande_bien",
        ),
        CheckConstraint(
            (
                "score_matching IS NULL OR "
                "(score_matching >= 0 AND score_matching <= 100)"
            ),
            name="ck_presentation_score",
        ),
        CheckConstraint(
            (
                "statut IN ("
                "'IDENTIFIE', "
                "'QUALIFIE', "
                "'PRESENTE', "
                "'REJETE', "
                "'VISITE', "
                "'RETENU'"
                ")"
            ),
            name="ck_presentation_statut",
        ),
        {"schema": "real_estate"},
    )

    id_presentation: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    date_selection: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    date_presentation: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    score_matching: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'IDENTIFIE'"),
    )

    id_demande_version: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.demande_version.id_demande_version",
            ondelete="RESTRICT",
            name="fk_presentation_demande_version",
        ),
        nullable=False,
        index=True,
    )

    id_bien: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.bien.id_bien",
            ondelete="RESTRICT",
            name="fk_presentation_bien",
        ),
        nullable=False,
        index=True,
    )