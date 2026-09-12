from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Integer,
    Numeric,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class ParametresRemuneration(Base):
    __tablename__ = "parametres_remuneration"
    __table_args__ = (
        CheckConstraint(
            (
                "date_fin_validite IS NULL "
                "OR date_fin_validite >= date_debut_validite"
            ),
            name="ck_parametres_remuneration_dates",
        ),
        CheckConstraint(
            "fenetre_mois > 0",
            name="ck_parametres_remuneration_fenetre",
        ),
        CheckConstraint(
            (
                "poids_delai >= 0 "
                "AND poids_exclusivite >= 0 "
                "AND poids_ventes >= 0 "
                "AND poids_mandats >= 0 "
                "AND poids_visites >= 0 "
                "AND "
                "("
                "poids_delai + "
                "poids_exclusivite + "
                "poids_ventes + "
                "poids_mandats + "
                "poids_visites"
                ") = 1.000000"
            ),
            name="ck_parametres_remuneration_poids",
        ),
        CheckConstraint(
            (
                "note_exclusif >= 0 "
                "AND note_exclusif <= 100 "
                "AND note_non_exclusif >= 0 "
                "AND note_non_exclusif <= 100"
            ),
            name="ck_parametres_remuneration_notes",
        ),
        CheckConstraint(
            (
                "points_par_vente >= 0 "
                "AND points_par_mandat >= 0"
            ),
            name="ck_parametres_remuneration_points",
        ),
        CheckConstraint(
            (
                "taux_anciennete_par_annee >= 0 "
                "AND plafond_anciennete >= 0 "
                "AND plafond_anciennete <= 1"
            ),
            name="ck_parametres_remuneration_anciennete",
        ),
        CheckConstraint(
            (
                "score_pivot >= 0 "
                "AND score_pivot <= 100"
            ),
            name="ck_parametres_remuneration_score_pivot",
        ),
        CheckConstraint(
            (
                "amplitude_performance >= 0 "
                "AND amplitude_performance <= 1"
            ),
            name="ck_parametres_remuneration_amplitude",
        ),
        CheckConstraint(
            (
                "taux_plancher >= 0 "
                "AND taux_plafond <= 1 "
                "AND taux_plancher <= taux_plafond"
            ),
            name="ck_parametres_remuneration_taux",
        ),
        {"schema": "real_estate"},
    )

    id_parametres_remuneration: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    date_debut_validite: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    date_fin_validite: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    fenetre_mois: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    poids_delai: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    poids_exclusivite: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    poids_ventes: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    poids_mandats: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    poids_visites: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    note_exclusif: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    note_non_exclusif: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    points_par_vente: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    points_par_mandat: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    taux_anciennete_par_annee: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    plafond_anciennete: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    score_pivot: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    amplitude_performance: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    taux_plancher: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    taux_plafond: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    actif: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )