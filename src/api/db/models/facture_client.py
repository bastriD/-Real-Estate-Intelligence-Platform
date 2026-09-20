from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger, CheckConstraint, Date, DateTime, ForeignKey, Identity,
    Index, Numeric, PrimaryKeyConstraint, String, UniqueConstraint, text,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class FactureClient(Base):
    """Issued company-fee snapshot; physical contract is migration 015."""

    __tablename__ = "facture_client"
    __table_args__ = (
        PrimaryKeyConstraint("id_facture_client", name="pk_facture_client"),
        UniqueConstraint("id_vente", name="uq_facture_client_vente"),
        UniqueConstraint("numero_facture", name="uq_facture_client_numero"),
        CheckConstraint("LENGTH(TRIM(numero_facture)) > 0", name="ck_facture_client_numero"),
        CheckConstraint("montant_achat > 0", name="ck_facture_client_montant_achat"),
        CheckConstraint("montant_fixe_applique >= 0", name="ck_facture_client_montant_fixe"),
        CheckConstraint(
            "taux_pourcentage_applique >= 0 AND taux_pourcentage_applique <= 1",
            name="ck_facture_client_taux_honoraires",
        ),
        CheckConstraint("montant_honoraires_ht >= 0", name="ck_facture_client_honoraires_ht"),
        Index("idx_facture_client_client", "id_client"),
        Index("idx_facture_client_date_emission", "date_emission"),
        Index("idx_facture_client_parametres_honoraires", "id_parametres_honoraires"),
        {"schema": "real_estate"},
    )

    id_facture_client: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    id_vente: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("real_estate.vente.id_vente", ondelete="RESTRICT", name="fk_facture_client_vente"),
    )
    id_client: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("real_estate.client.id_client", ondelete="RESTRICT", name="fk_facture_client_client"),
    )
    id_parametres_honoraires: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(
            "real_estate.parametres_honoraires.id_parametres_honoraires",
            ondelete="RESTRICT", name="fk_facture_client_parametres_honoraires",
        ),
    )
    numero_facture: Mapped[str] = mapped_column(String(80))
    date_emission: Mapped[date] = mapped_column(Date)
    montant_achat: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    montant_fixe_applique: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    taux_pourcentage_applique: Mapped[Decimal] = mapped_column(Numeric(7, 4))
    montant_honoraires_ht: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"),
    )
