from datetime import datetime

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class Client(Base):
    __tablename__ = "client"
    __table_args__ = (
        CheckConstraint(
            "statut IN ('ACTIF', 'INACTIF', 'ARCHIVE')",
            name="ck_client_statut",
        ),
        {"schema": "real_estate"},
    )

    id_client: Mapped[int] = mapped_column(
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

    ville: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIF",
    )

    consentement_contact: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )