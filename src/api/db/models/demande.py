from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    text,
)

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class Demande(Base):
    __tablename__ = "demande"
    __table_args__ = (
        CheckConstraint(
            "statut IN ('ACTIVE', 'SUSPENDUE', 'CLOTUREE', 'ANNULEE')",
            name="ck_demande_statut",
        ),
        {"schema": "real_estate"},
    )
    id_client: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.client.id_client",
            ondelete="RESTRICT",
            name="fk_demande_client",
        ),
        nullable=True,
        index=True,
    )
    id_demande: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    reference_demande: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
        unique=True,
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ACTIVE'"),
    )

    id_mandat: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.mandat.id_mandat",
            ondelete="RESTRICT",
            name="fk_demande_mandat",
        ),
        nullable=True,
        index=True,
    )


class DemandeVersion(Base):
    __tablename__ = "demande_version"
    __table_args__ = (
        CheckConstraint(
            "numero_version > 0",
            name="ck_demande_version_numero",
        ),
        CheckConstraint(
            "budget_min IS NULL OR budget_min >= 0",
            name="ck_demande_version_budget_min",
        ),
        CheckConstraint(
            "budget_max IS NULL OR budget_max >= 0",
            name="ck_demande_version_budget_max",
        ),
        CheckConstraint(
            (
                "budget_min IS NULL OR "
                "budget_max IS NULL OR "
                "budget_min <= budget_max"
            ),
            name="ck_demande_version_budget_range",
        ),
        CheckConstraint(
            "surface_min IS NULL OR surface_min >= 0",
            name="ck_demande_version_surface",
        ),
        CheckConstraint(
            "nb_pieces_min IS NULL OR nb_pieces_min >= 0",
            name="ck_demande_version_pieces",
        ),
        CheckConstraint(
            "nb_chambres_min IS NULL OR nb_chambres_min >= 0",
            name="ck_demande_version_chambres",
        ),
        CheckConstraint(
            "dpe_max IS NULL OR dpe_max IN ('A','B','C','D','E','F','G')",
            name="ck_demande_version_dpe",
        ),
        CheckConstraint(
            """
            (
                CASE WHEN auteur_client_id IS NOT NULL THEN 1 ELSE 0 END
                +
                CASE WHEN auteur_chasseur_id IS NOT NULL THEN 1 ELSE 0 END
                +
                CASE WHEN auteur_systeme THEN 1 ELSE 0 END
            ) = 1
            """,
            name="ck_demande_version_auteur",
        ),
        {"schema": "real_estate"},
    )

    id_demande_version: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    numero_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    date_version: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    motif_modification: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    ville: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    code_postal: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    type_bien: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    budget_min: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    budget_max: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    surface_min: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    nb_pieces_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    nb_chambres_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    dpe_max: Mapped[str | None] = mapped_column(
        String(1),
        nullable=True,
    )

    criteres_souhaites: Mapped[list | dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    )

    description_recherche_legacy: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    id_demande: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.demande.id_demande",
            ondelete="RESTRICT",
            name="fk_demande_version_demande",
        ),
        nullable=False,
        index=True,
    )

    auteur_client_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.client.id_client",
            ondelete="RESTRICT",
            name="fk_demande_version_client",
        ),
        nullable=True,
        index=True,
    )

    auteur_chasseur_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.chasseur.id_chasseur",
            ondelete="RESTRICT",
            name="fk_demande_version_chasseur",
        ),
        nullable=True,
        index=True,
    )

    auteur_systeme: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
