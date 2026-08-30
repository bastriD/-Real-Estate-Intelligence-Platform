from datetime import date

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class Chasseur(Base):
    __tablename__ = "chasseur"
    __table_args__ = (
        CheckConstraint(
            "statut IN ('ACTIF', 'INACTIF')",
            name="ck_chasseur_statut",
        ),
        {"schema": "real_estate"},
    )

    id_chasseur: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    nom: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    prenom: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    telephone: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
    )

    date_entree: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ACTIF'"),
    )