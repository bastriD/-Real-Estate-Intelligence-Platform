from typing import Any

from sqlalchemy.orm import Session

from src.api.db.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        table_name: str,
        operation: str,
        record_id: str | None = None,
        utilisateur: str | None = None,
        ancienne_valeur: dict[str, Any] | None = None,
        nouvelle_valeur: dict[str, Any] | None = None,
        contexte: dict[str, Any] | None = None,
        schema_name: str = "real_estate",
    ) -> AuditLog:
        audit = AuditLog(
            schema_name=schema_name,
            table_name=table_name,
            operation=operation,
            record_id=record_id,
            utilisateur=utilisateur,
            ancienne_valeur=ancienne_valeur,
            nouvelle_valeur=nouvelle_valeur,
            contexte=contexte or {},
        )

        self.session.add(audit)
        self.session.flush()

        return audit