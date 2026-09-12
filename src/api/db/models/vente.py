from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class Vente(Base):
    __tablename__ = "vente"

    __table_args__ = (
        CheckConstraint(
            (
                "origine_vente IN ("
                "'CHASSEUR', "
                "'CLIENT_SEUL', "
                "'AUTRE_AGENCE'"
                ")"
            ),
            name="ck_vente_origine",
        ),
        CheckConstraint(
            "montant_achat > 0",
            name="ck_vente_montant_achat",
        ),
        {"schema": "real_estate"},
    )

    id_vente: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_mandat: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.mandat.id_mandat",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    id_mandat_periode: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.mandat_periode.id_mandat_periode",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    id_presentation: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.presentation.id_presentation",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    id_bien: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.bien.id_bien",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    id_chasseur_beneficiaire: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.chasseur.id_chasseur",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    origine_vente: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    date_acte_authentique: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    montant_achat: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )