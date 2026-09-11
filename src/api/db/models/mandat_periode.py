from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.db.base import Base


class MandatPeriode(Base):
    __tablename__ = "mandat_periode"

    __table_args__ = (
        UniqueConstraint(
            "id_mandat",
            "numero_periode",
            name="uq_mandat_periode_numero",
        ),
        CheckConstraint(
            "numero_periode >= 1",
            name="ck_mandat_periode_numero",
        ),
        CheckConstraint(
            "type_periode IN ('INITIAL', 'RENOUVELLEMENT')",
            name="ck_mandat_periode_type",
        ),
        CheckConstraint(
            "date_fin >= date_debut",
            name="ck_mandat_periode_dates",
        ),
        CheckConstraint(
            (
                "est_historique_legacy = TRUE "
                "OR date_fin = "
                "(date_debut + INTERVAL '6 months')::date"
            ),
            name="ck_mandat_periode_duree",
        ),
        CheckConstraint(
            (
                "("
                "type_periode = 'INITIAL' "
                "AND date_renouvellement IS NULL"
                ") "
                "OR "
                "("
                "type_periode = 'RENOUVELLEMENT' "
                "AND date_renouvellement IS NOT NULL"
                ")"
            ),
            name="ck_mandat_periode_renouvellement",
        ),
        Index(
            "uq_mandat_periode_initial",
            "id_mandat",
            unique=True,
            postgresql_where=text("type_periode = 'INITIAL'"),
        ),
        Index(
            "idx_mandat_periode_mandat",
            "id_mandat",
        ),
        Index(
            "idx_mandat_periode_dates",
            "date_debut",
            "date_fin",
        ),
        {"schema": "real_estate"},
    )

    id_mandat_periode: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    id_mandat: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.mandat.id_mandat",
            ondelete="CASCADE",
            name="fk_mandat_periode_mandat",
        ),
        nullable=False,
    )

    numero_periode: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    type_periode: Mapped[str] = mapped_column(
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

    date_renouvellement: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    commentaire: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    est_historique_legacy: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("FALSE"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    mandat: Mapped["Mandat"] = relationship(
        "Mandat",
        lazy="selectin",
    )