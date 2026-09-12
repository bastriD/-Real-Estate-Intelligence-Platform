from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class Paiement(Base):
    __tablename__ = "paiement"
    __table_args__ = (
        CheckConstraint(
            "montant_achat IS NULL OR montant_achat >= 0",
            name="ck_paiement_montant_achat",
        ),
        CheckConstraint(
            "montant_honoraires IS NULL OR montant_honoraires >= 0",
            name="ck_paiement_honoraires",
        ),
        CheckConstraint(
            "montant_chasseur IS NULL OR montant_chasseur >= 0",
            name="ck_paiement_chasseur",
        ),
        CheckConstraint(
            (
                "statut IN ("
                "'ATTENDU', "
                "'RECU', "
                "'VERIFIE', "
                "'PROGRAMME', "
                "'PAYE', "
                "'ANNULE'"
                ")"
            ),
            name="ck_paiement_statut",
        ),
        CheckConstraint(
            (
                "date_paiement_chasseur IS NULL "
                "OR date_reception_honoraires IS NULL "
                "OR date_paiement_chasseur "
                ">= date_reception_honoraires"
            ),
            name="ck_paiement_dates",
        ),
        CheckConstraint(
            (
                "droit_remuneration IS NULL "
                "OR ("
                "droit_remuneration = true "
                "AND motif_refus IS NULL"
                ") "
                "OR ("
                "droit_remuneration = false "
                "AND motif_refus IS NOT NULL"
                ")"
            ),
            name="ck_paiement_droit_motif",
        ),
        CheckConstraint(
            (
                "motif_refus IS NULL "
                "OR motif_refus IN ("
                "'MANDAT_EXPIRE', "
                "'HORS_DISPOSITIF'"
                ")"
            ),
            name="ck_paiement_motif_refus",
        ),
        CheckConstraint(
            (
                "semaines_mandat_acte IS NULL "
                "OR semaines_mandat_acte >= 0"
            ),
            name="ck_paiement_semaines_calcul",
        ),
        CheckConstraint(
            (
                "(nb_visites_calcul IS NULL "
                "OR nb_visites_calcul >= 0) "
                "AND "
                "(annees_anciennete_calcul IS NULL "
                "OR annees_anciennete_calcul >= 0) "
                "AND "
                "(nb_ventes_fenetre IS NULL "
                "OR nb_ventes_fenetre >= 0) "
                "AND "
                "(nb_mandats_fenetre IS NULL "
                "OR nb_mandats_fenetre >= 0)"
            ),
            name="ck_paiement_compteurs_calcul",
        ),
        CheckConstraint(
            (
                "(note_delai IS NULL "
                "OR note_delai BETWEEN 0 AND 100) "
                "AND "
                "(note_exclusivite IS NULL "
                "OR note_exclusivite BETWEEN 0 AND 100) "
                "AND "
                "(note_ventes IS NULL "
                "OR note_ventes BETWEEN 0 AND 100) "
                "AND "
                "(note_mandats IS NULL "
                "OR note_mandats BETWEEN 0 AND 100) "
                "AND "
                "(note_visites IS NULL "
                "OR note_visites BETWEEN 0 AND 100) "
                "AND "
                "(score_performance IS NULL "
                "OR score_performance BETWEEN 0 AND 100)"
            ),
            name="ck_paiement_notes_calcul",
        ),
        CheckConstraint(
            (
                "(taux_base IS NULL "
                "OR taux_base BETWEEN 0 AND 1) "
                "AND "
                "(majoration_anciennete IS NULL "
                "OR majoration_anciennete BETWEEN 0 AND 1) "
                "AND "
                "(modulation_performance IS NULL "
                "OR modulation_performance BETWEEN -1 AND 1) "
                "AND "
                "(taux_final IS NULL "
                "OR taux_final BETWEEN 0 AND 1)"
            ),
            name="ck_paiement_taux_calcul",
        ),
        Index(
            "uq_paiement_id_vente",
            "id_vente",
            unique=True,
            postgresql_where=text("id_vente IS NOT NULL"),
        ),
        {"schema": "real_estate"},
    )

    id_paiement: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    date_acte_authentique: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    montant_achat: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    montant_honoraires: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    montant_chasseur: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    date_reception_honoraires: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    date_paiement_chasseur: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ATTENDU'"),
    )

    id_mandat: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.mandat.id_mandat",
            ondelete="RESTRICT",
            name="fk_paiement_mandat",
        ),
        nullable=False,
        index=True,
    )

    id_bareme: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.bareme_commission.id_bareme",
            ondelete="RESTRICT",
            name="fk_paiement_bareme",
        ),
        nullable=True,
        index=True,
    )

    id_vente: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.vente.id_vente",
            ondelete="RESTRICT",
            name="fk_paiement_vente",
        ),
        nullable=True,
        index=True,
    )

    id_chasseur_beneficiaire: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "real_estate.chasseur.id_chasseur",
            ondelete="RESTRICT",
            name="fk_paiement_chasseur_beneficiaire",
        ),
        nullable=True,
        index=True,
    )

    id_parametres_honoraires: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            (
                "real_estate.parametres_honoraires."
                "id_parametres_honoraires"
            ),
            ondelete="RESTRICT",
            name="fk_paiement_parametres_honoraires",
        ),
        nullable=True,
    )

    id_parametres_remuneration: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            (
                "real_estate.parametres_remuneration."
                "id_parametres_remuneration"
            ),
            ondelete="RESTRICT",
            name="fk_paiement_parametres_remuneration",
        ),
        nullable=True,
    )

    date_calcul: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    droit_remuneration: Mapped[bool | None] = mapped_column(
        nullable=True,
    )

    motif_refus: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    semaines_mandat_acte: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    nb_visites_calcul: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    annees_anciennete_calcul: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    nb_ventes_fenetre: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    nb_mandats_fenetre: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    note_delai: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    note_exclusivite: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    note_ventes: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    note_mandats: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    note_visites: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    score_performance: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    taux_base: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    majoration_anciennete: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    modulation_performance: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    taux_final: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )