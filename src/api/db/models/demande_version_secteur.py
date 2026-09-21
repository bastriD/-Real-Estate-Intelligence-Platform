from sqlalchemy import BigInteger, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base
from src.api.db.models.secteur import Secteur  # Register the referenced canonical table.


class DemandeVersionSecteur(Base):
    __tablename__ = "demande_version_secteur"
    __table_args__ = (
        PrimaryKeyConstraint("id_demande_version", "id_secteur", name="pk_demande_version_secteur"),
        Index("idx_demande_version_secteur_secteur", "id_secteur"),
        {"schema": "real_estate"},
    )
    id_demande_version: Mapped[int] = mapped_column(BigInteger, ForeignKey(
        "real_estate.demande_version.id_demande_version", ondelete="CASCADE",
        name="fk_demande_version_secteur_version"), primary_key=True)
    id_secteur: Mapped[int] = mapped_column(BigInteger, ForeignKey(
        "real_estate.secteur.id_secteur", ondelete="RESTRICT",
        name="fk_demande_version_secteur_secteur"), primary_key=True)
