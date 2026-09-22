"""Notarial actors, deed dossiers and append-only agency fee movements (019)."""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, ForeignKey, Identity, Numeric, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class Notaire(Base):
    __tablename__ = "notaire"
    __table_args__ = ({"schema": "real_estate"},)
    id_notaire: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    nom: Mapped[str] = mapped_column(String(200))
    office: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(254))


class DossierNotarial(Base):
    __tablename__ = "dossier_notarial"
    __table_args__ = (
        UniqueConstraint("id_offre", name="uq_dossier_notarial_offre"),
        UniqueConstraint("id_vente", name="uq_dossier_notarial_vente"),
        UniqueConstraint("id_notaire", "reference_acte", name="uq_dossier_notarial_acte"),
        CheckConstraint("(id_vente IS NULL AND reference_acte IS NULL AND reference_document IS NULL) OR (id_vente IS NOT NULL AND reference_acte IS NOT NULL AND reference_document IS NOT NULL)", name="ck_dossier_notarial_signature"),
        {"schema": "real_estate"},
    )
    id_dossier_notarial: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    id_notaire: Mapped[int] = mapped_column(ForeignKey("real_estate.notaire.id_notaire", ondelete="RESTRICT"))
    id_offre: Mapped[int] = mapped_column(ForeignKey("real_estate.offre.id_offre", ondelete="RESTRICT"))
    id_vente: Mapped[int | None] = mapped_column(ForeignKey("real_estate.vente.id_vente", ondelete="RESTRICT"))
    date_rendez_vous: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reference_acte: Mapped[str | None] = mapped_column(String(120))
    reference_document: Mapped[str | None] = mapped_column(String(500))
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))


class MouvementNotarial(Base):
    __tablename__ = "mouvement_notarial"
    __table_args__ = (
        UniqueConstraint("id_dossier_notarial", "reference", name="uq_mouvement_notarial_reference"),
        CheckConstraint("nature IN ('COLLECTE_NOTAIRE', 'RECEPTION_ENTREPRISE')", name="ck_mouvement_notarial_nature"),
        CheckConstraint("montant > 0", name="ck_mouvement_notarial_montant"),
        {"schema": "real_estate"},
    )
    id_mouvement_notarial: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    id_dossier_notarial: Mapped[int] = mapped_column(ForeignKey("real_estate.dossier_notarial.id_dossier_notarial", ondelete="RESTRICT"))
    nature: Mapped[str] = mapped_column(String(30))
    montant: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    date_operation: Mapped[date] = mapped_column(Date)
    reference: Mapped[str] = mapped_column(String(120))
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
