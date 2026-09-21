from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class Bien(Base):
    __tablename__ = "bien"
    id_secteur: Mapped[int | None] = mapped_column(BigInteger, ForeignKey(
        "real_estate.secteur.id_secteur", name="fk_bien_secteur", ondelete="RESTRICT"))
    __table_args__ = (
        Index("idx_bien_secteur", "id_secteur", postgresql_where=text("id_secteur IS NOT NULL")),
        UniqueConstraint(
            "id_source",
            "reference_externe",
            name="uq_bien_source_reference",
        ),
        CheckConstraint(
            "prix IS NULL OR prix >= 0",
            name="ck_bien_prix",
        ),
        CheckConstraint(
            "surface IS NULL OR surface >= 0",
            name="ck_bien_surface",
        ),
        CheckConstraint(
            "nb_pieces IS NULL OR nb_pieces >= 0",
            name="ck_bien_pieces",
        ),
        CheckConstraint(
            "nb_chambres IS NULL OR nb_chambres >= 0",
            name="ck_bien_chambres",
        ),
        CheckConstraint(
            "latitude IS NULL OR (latitude >= -90 AND latitude <= 90)",
            name="ck_bien_latitude",
        ),
        CheckConstraint(
            "longitude IS NULL OR (longitude >= -180 AND longitude <= 180)",
            name="ck_bien_longitude",
        ),
        CheckConstraint(
            "dpe IS NULL OR dpe IN ('A','B','C','D','E','F','G')",
            name="ck_bien_dpe",
        ),
        CheckConstraint(
            (
                "statut IN ("
                "'ACTIF', "
                "'EXPIRE', "
                "'VENDU', "
                "'INDISPONIBLE'"
                ")"
            ),
            name="ck_bien_statut",
        ),
        {"schema": "real_estate"},
    )

    id_bien: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    reference_externe: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    type_bien: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    titre: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    adresse: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    code_postal: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    ville: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    latitude: Mapped[Decimal | None] = mapped_column(
        Numeric(9, 6),
        nullable=True,
    )

    longitude: Mapped[Decimal | None] = mapped_column(
        Numeric(9, 6),
        nullable=True,
    )

    prix: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    surface: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    nb_pieces: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    nb_chambres: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    dpe: Mapped[str | None] = mapped_column(
        String(1),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    date_publication: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    date_collecte: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ACTIF'"),
    )

    id_source: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.source.id_source",
            ondelete="RESTRICT",
            name="fk_bien_source",
        ),
        nullable=False,
        index=True,
    )
