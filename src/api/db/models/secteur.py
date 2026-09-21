from sqlalchemy import BigInteger, Boolean, Identity, PrimaryKeyConstraint, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class Secteur(Base):
    __tablename__ = "secteur"
    __table_args__ = (
        PrimaryKeyConstraint("id_secteur", name="pk_secteur"),
        UniqueConstraint("pays", "ville", "quartier", "code_postal", name="uq_secteur_localisation"),
        {"schema": "real_estate"},
    )
    id_secteur: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    pays: Mapped[str] = mapped_column(String(100), server_default=text("'France'"))
    ville: Mapped[str] = mapped_column(String(120))
    quartier: Mapped[str | None] = mapped_column(String(150))
    code_postal: Mapped[str | None] = mapped_column(String(20))
    actif: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
