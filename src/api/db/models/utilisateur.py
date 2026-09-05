from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class Utilisateur(Base):
    __tablename__ = "utilisateur"
    __table_args__ = {"schema": "real_estate"}

    id_utilisateur: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    actif: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    id_client: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.client.id_client",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    id_chasseur: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.chasseur.id_chasseur",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    derniere_connexion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    date_modification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )