from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.repositories.bien import BienRepository
from src.api.repositories.secteur import SecteurRepository
from src.api.services.audit_log import AuditLogService
from src.api.services.bien import BienNotFoundError


class SecteurValidationError(ValueError):
    pass


class SecteurService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = SecteurRepository(session)
        self.biens = BienRepository(session)
        self.audit = AuditLogService(session)

    def list_active(self):
        return self.repository.list_active()

    def assign_bien(self, bien_id: int, sector_id: int | None, *, actor: str, actor_id: int):
        try:
            bien = self.biens.get_for_update(bien_id)
            if bien is None:
                raise BienNotFoundError()
            if sector_id is not None:
                sector = self.repository.get_active(sector_id)
                if sector is None:
                    raise SecteurValidationError("Sector must exist and be active")
                if not bien.ville or bien.ville.strip().casefold() != sector.ville.strip().casefold():
                    raise SecteurValidationError("Property and sector must belong to the same city")
            previous = bien.id_secteur
            if previous == sector_id:
                return bien
            bien.id_secteur = sector_id
            self.audit.log_change(
                table_name="bien", operation="UPDATE", record_id=bien_id, utilisateur=actor,
                ancienne_valeur={"id_secteur": previous}, nouvelle_valeur={"id_secteur": sector_id},
                contexte={"source": "api", "action": "assign_bien_secteur", "id_utilisateur": actor_id},
            )
            self.session.commit()
            self.session.refresh(bien)
            return bien
        except IntegrityError as exc:
            self.session.rollback()
            raise SecteurValidationError("Property sector assignment violates a database constraint") from exc
        except Exception:
            self.session.rollback()
            raise
