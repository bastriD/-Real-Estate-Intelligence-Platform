from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class DemandeAffectation(Base):
    __tablename__ = "demande_affectation"
    __table_args__ = (
        CheckConstraint(
            "statut IN ('ASSIGNEE', 'ACCEPTEE', 'REFUSEE')",
            name="ck_demande_affectation_statut",
        ),
        CheckConstraint(
            """
            (
                statut = 'ASSIGNEE'
                AND date_decision IS NULL
                AND id_utilisateur_decision IS NULL
            )
            OR
            (
                statut IN ('ACCEPTEE', 'REFUSEE')
                AND date_decision IS NOT NULL
            )
            """,
            name="ck_demande_affectation_decision",
        ),
        CheckConstraint(
            "statut = 'REFUSEE' OR motif_refus IS NULL",
            name="ck_demande_affectation_motif_refus",
        ),
        CheckConstraint(
            "date_decision IS NULL OR date_decision >= date_affectation",
            name="ck_demande_affectation_dates",
        ),
        Index(
            "uq_demande_affectation_current",
            "id_demande",
            unique=True,
            postgresql_where=text(
                "statut IN ('ASSIGNEE', 'ACCEPTEE')"
            ),
        ),
        Index(
            "idx_demande_affectation_demande",
            "id_demande",
        ),
        Index(
            "idx_demande_affectation_chasseur",
            "id_chasseur",
        ),
        Index(
            "idx_demande_affectation_chasseur_statut",
            "id_chasseur",
            "statut",
        ),
        {"schema": "real_estate"},
    )

    id_affectation: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_demande: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.demande.id_demande",
            ondelete="RESTRICT",
            name="fk_demande_affectation_demande",
        ),
        nullable=False,
    )

    id_chasseur: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.chasseur.id_chasseur",
            ondelete="RESTRICT",
            name="fk_demande_affectation_chasseur",
        ),
        nullable=False,
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ASSIGNEE'"),
    )

    date_affectation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    date_decision: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    id_utilisateur_affectation: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.utilisateur.id_utilisateur",
            ondelete="RESTRICT",
            name="fk_demande_affectation_utilisateur_affectation",
        ),
        nullable=True,
    )

    id_utilisateur_decision: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.utilisateur.id_utilisateur",
            ondelete="RESTRICT",
            name="fk_demande_affectation_utilisateur_decision",
        ),
        nullable=True,
    )

    motif_refus: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )