from typing import Any

from sqlalchemy.orm import Session

from src.api.db.models.audit_log import AuditLog
from src.api.repositories.audit_log import AuditLogRepository


class AuditLogService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = AuditLogRepository(session)

    def log_change(
        self,
        *,
        table_name: str,
        operation: str,
        record_id: str | int | None = None,
        utilisateur: str | None = None,
        ancienne_valeur: dict[str, Any] | None = None,
        nouvelle_valeur: dict[str, Any] | None = None,
        contexte: dict[str, Any] | None = None,
        schema_name: str = "real_estate",
    ) -> AuditLog:
        return self.repository.create(
            schema_name=schema_name,
            table_name=table_name,
            operation=operation,
            record_id=str(record_id) if record_id is not None else None,
            utilisateur=utilisateur,
            ancienne_valeur=ancienne_valeur,
            nouvelle_valeur=nouvelle_valeur,
            contexte=contexte,
        )