from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger, CheckConstraint, Date, DateTime, ForeignKey, Identity, Index,
    Integer, Numeric, PrimaryKeyConstraint, String, Text, UniqueConstraint, text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class FactureChasseur(Base):
    __tablename__ = "facture_chasseur"
    __table_args__ = (
        PrimaryKeyConstraint("id_facture_chasseur", name="pk_facture_chasseur"),
        UniqueConstraint("id_paiement", "numero_version", name="uq_facture_chasseur_paiement_version"),
        CheckConstraint("numero_version > 0", name="ck_facture_chasseur_version"),
        CheckConstraint("LENGTH(TRIM(numero_facture)) > 0", name="ck_facture_chasseur_numero"),
        CheckConstraint("montant > 0", name="ck_facture_chasseur_montant"),
        CheckConstraint("statut IN ('SOUMISE', 'CONFORME', 'REJETEE')", name="ck_facture_chasseur_statut"),
        CheckConstraint("""
            (statut = 'SOUMISE' AND date_verification IS NULL AND id_verificateur IS NULL AND motif_rejet IS NULL)
            OR (statut = 'CONFORME' AND date_verification IS NOT NULL AND id_verificateur IS NOT NULL AND motif_rejet IS NULL)
            OR (statut = 'REJETEE' AND date_verification IS NOT NULL AND id_verificateur IS NOT NULL
                AND motif_rejet IS NOT NULL AND LENGTH(TRIM(motif_rejet)) > 0)
        """, name="ck_facture_chasseur_verification"),
        CheckConstraint("date_verification IS NULL OR date_verification >= date_soumission", name="ck_facture_chasseur_dates"),
        Index("uq_facture_chasseur_active", "id_paiement", unique=True,
              postgresql_where=text("statut IN ('SOUMISE', 'CONFORME')")),
        Index("idx_facture_chasseur_chasseur", "id_chasseur"),
        Index("idx_facture_chasseur_statut", "statut"),
        {"schema": "real_estate"},
    )

    id_facture_chasseur: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    id_paiement: Mapped[int] = mapped_column(BigInteger, ForeignKey(
        "real_estate.paiement.id_paiement", name="fk_facture_chasseur_paiement", ondelete="RESTRICT"))
    id_chasseur: Mapped[int] = mapped_column(BigInteger, ForeignKey(
        "real_estate.chasseur.id_chasseur", name="fk_facture_chasseur_chasseur", ondelete="RESTRICT"))
    numero_version: Mapped[int] = mapped_column(Integer)
    numero_facture: Mapped[str] = mapped_column(String(80))
    date_facture: Mapped[date] = mapped_column(Date)
    montant: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    date_soumission: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    statut: Mapped[str] = mapped_column(String(20), server_default=text("'SOUMISE'"))
    date_verification: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    id_verificateur: Mapped[int | None] = mapped_column(BigInteger, ForeignKey(
        "real_estate.utilisateur.id_utilisateur", name="fk_facture_chasseur_verificateur", ondelete="RESTRICT"))
    motif_rejet: Mapped[str | None] = mapped_column(Text)
