from datetime import date

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    ForeignKey,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class Mandat(Base):
    __tablename__ = "mandat"
    __table_args__ = (
        CheckConstraint(
            "type_mandat IN ('EXCLUSIF', 'NON_EXCLUSIF')",
            name="ck_mandat_type",
        ),
        CheckConstraint(
            "mode_signature IN ('PAPIER', 'ELECTRONIQUE', 'AUTRE', 'INCONNU')",
            name="ck_mandat_mode_signature",
        ),
        CheckConstraint(
            (
                "statut IN ("
                "'BROUILLON', "
                "'ACTIF', "
                "'SUSPENDU', "
                "'TERMINE', "
                "'EXPIRE', "
                "'ANNULE'"
                ")"
            ),
            name="ck_mandat_statut",
        ),
        CheckConstraint(
            "date_fin >= date_debut",
            name="ck_mandat_dates",
        ),
        {"schema": "real_estate"},
    )

    id_mandat: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    reference_mandat: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
    )

    type_mandat: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    date_signature: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    mode_signature: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    date_debut: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    date_fin: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ACTIF'"),
    )

    commentaire: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    id_client: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.client.id_client",
            ondelete="RESTRICT",
            name="fk_mandat_client",
        ),
        nullable=False,
        index=True,
    )

    id_chasseur: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.chasseur.id_chasseur",
            ondelete="RESTRICT",
            name="fk_mandat_chasseur",
        ),
        nullable=False,
        index=True,
    )