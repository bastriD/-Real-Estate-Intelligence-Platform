from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.api.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (
        CheckConstraint(
            "operation IN ('INSERT', 'UPDATE', 'DELETE')",
            name="ck_audit_log_operation",
        ),
        CheckConstraint(
            "jsonb_typeof(contexte) = 'object'",
            name="ck_audit_log_contexte_object",
        ),
        {"schema": "real_estate"},
    )

    id_audit: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    date_evenement: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    schema_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        server_default=text("'real_estate'"),
    )

    table_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    operation: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    record_id: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    utilisateur: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    ancienne_valeur: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    nouvelle_valeur: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    contexte: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )