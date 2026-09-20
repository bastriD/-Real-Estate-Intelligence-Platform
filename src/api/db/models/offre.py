from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class Offre(Base):
    __tablename__ = "offre"
    __table_args__ = (
        UniqueConstraint(
            "id_presentation",
            "numero_version",
            name="uq_offre_presentation_version",
        ),
        CheckConstraint(
            "numero_version > 0",
            name="ck_offre_numero_version",
        ),
        CheckConstraint(
            "montant > 0",
            name="ck_offre_montant",
        ),
        CheckConstraint(
            (
                "statut IN ("
                "'SOUMISE', "
                "'ACCEPTEE', "
                "'REFUSEE', "
                "'RETIREE', "
                "'EXPIREE', "
                "'REVISEE'"
                ")"
            ),
            name="ck_offre_statut",
        ),
        CheckConstraint(
            (
                "date_expiration IS NULL "
                "OR date_expiration > date_offre"
            ),
            name="ck_offre_expiration",
        ),
        CheckConstraint(
            """
            (
                statut IN ('SOUMISE', 'EXPIREE')
                AND date_decision IS NULL
            )
            OR
            (
                statut IN (
                    'ACCEPTEE',
                    'REFUSEE',
                    'RETIREE',
                    'REVISEE'
                )
                AND date_decision IS NOT NULL
            )
            """,
            name="ck_offre_decision",
        ),
        Index(
            "idx_offre_presentation",
            "id_presentation",
        ),
        Index(
            "idx_offre_statut",
            "statut",
        ),
        Index(
            "idx_offre_date_offre",
            "date_offre",
        ),
        Index(
            "uq_offre_presentation_acceptee",
            "id_presentation",
            unique=True,
            postgresql_where=text("statut = 'ACCEPTEE'"),
        ),
        {"schema": "real_estate"},
    )

    id_offre: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_presentation: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.presentation.id_presentation",
            ondelete="RESTRICT",
            name="fk_offre_presentation",
        ),
        nullable=False,
    )

    numero_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    montant: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    date_offre: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    date_expiration: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    date_decision: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'SOUMISE'"),
    )

    commentaire: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )