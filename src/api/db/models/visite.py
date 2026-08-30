from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class Visite(Base):
    __tablename__ = "visite"
    __table_args__ = (
        CheckConstraint(
            "note IS NULL OR (note >= 0 AND note <= 5)",
            name="ck_visite_note",
        ),
        CheckConstraint(
            "jsonb_typeof(photos) = 'array'",
            name="ck_visite_photos_array",
        ),
        CheckConstraint(
            (
                "statut IN ("
                "'PLANIFIEE', "
                "'REALISEE', "
                "'ANNULEE', "
                "'REPORTEE'"
                ")"
            ),
            name="ck_visite_statut",
        ),
        {"schema": "real_estate"},
    )

    id_visite: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    date_visite: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'PLANIFIEE'"),
    )

    compte_rendu: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    note: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    photos: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    id_presentation: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.presentation.id_presentation",
            ondelete="RESTRICT",
            name="fk_visite_presentation",
        ),
        nullable=False,
        index=True,
    )