"""Record a notary's actions; collection is never company receipt."""
from datetime import datetime, timezone
from decimal import Decimal
from functools import wraps

from sqlalchemy.exc import IntegrityError

from src.api.db.models.notaire import DossierNotarial, MouvementNotarial, Notaire
from src.api.repositories.notaire import NotaireRepository
from src.api.schemas.notaire import DossierNotarialRead, MouvementNotarialRead, NotaireRead
from src.api.schemas.vente import VenteCreate, VenteOrigine
from src.api.services.audit_log import AuditLogService
from src.api.services.vente import VenteService
from src.api.services.paiement import PaiementService


class NotarialNotFoundError(Exception):
    pass


class NotarialConflictError(Exception):
    pass


class NotarialValidationError(Exception):
    pass


def atomic(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        try:
            result = method(self, *args, **kwargs)
            self.session.commit()
            self.session.refresh(result)
            return result
        except IntegrityError as exc:
            self.session.rollback()
            raise NotarialConflictError("Notarial record conflicts with persisted financial or sale data") from exc
        except Exception:
            self.session.rollback()
            raise
    return wrapped


class NotaireService:
    def __init__(self, session):
        self.session = session
        self.repository = NotaireRepository(session)
        self.audit = AuditLogService(session)

    def get_dossier(self, identifier, *, lock=False):
        dossier = self.repository.dossier(identifier, lock=lock)
        if dossier is None:
            raise NotarialNotFoundError("Resource not found")
        return dossier

    def _audit(self, table, record, schema, actor, action):
        self.audit.log_change(
            table_name=table, operation="INSERT" if action != "SIGNATURE" else "UPDATE",
            record_id=getattr(record, "id_" + table), utilisateur=actor,
            nouvelle_valeur=schema.model_validate(record).model_dump(mode="json"),
            contexte={"source": "api", "action": action},
        )

    @atomic
    def create_notaire(self, payload, *, utilisateur):
        record = self.repository.add(Notaire(**payload.model_dump()))
        self._audit("notaire", record, NotaireRead, utilisateur, "CREATE_NOTAIRE")
        return record

    def _accepted_offer(self, identifier):
        context = self.repository.offer_context(identifier)
        if context is None:
            raise NotarialNotFoundError("Resource not found")
        offer, mandat_id = context
        if offer.statut != "ACCEPTEE" or mandat_id is None:
            raise NotarialValidationError("An accepted offer linked to a mandate is required")
        return offer, mandat_id

    @atomic
    def create_dossier(self, payload, *, utilisateur):
        self._accepted_offer(payload.id_offre)
        if self.session.get(Notaire, payload.id_notaire) is None:
            raise NotarialNotFoundError("Resource not found")
        record = self.repository.add(DossierNotarial(**payload.model_dump()))
        self._audit("dossier_notarial", record, DossierNotarialRead, utilisateur, "CREATE_DOSSIER")
        return record

    @atomic
    def sign(self, identifier, payload, *, utilisateur):
        dossier = self.get_dossier(identifier, lock=True)
        if dossier.id_vente is not None:
            raise NotarialConflictError("The authentic deed has already been recorded")
        offer, mandat_id = self._accepted_offer(dossier.id_offre)
        today = datetime.now(timezone.utc).date()
        if not dossier.date_rendez_vous.astimezone(timezone.utc).date() <= payload.date_acte_authentique <= today:
            raise NotarialValidationError("Signing must follow the appointment and cannot be in the future")
        if offer.date_decision is None or payload.date_acte_authentique < offer.date_decision.date():
            raise NotarialValidationError("Signing cannot precede the accepted offer")
        sale = VenteService(self.session).create_vente(VenteCreate(
            id_mandat=mandat_id, id_presentation=offer.id_presentation,
            origine_vente=VenteOrigine.CHASSEUR,
            date_acte_authentique=payload.date_acte_authentique,
            montant_achat=payload.montant_achat,
        ), utilisateur=utilisateur, commit=False)
        dossier.id_vente = sale.id_vente
        dossier.reference_acte = payload.reference_acte
        dossier.reference_document = payload.reference_document
        self.session.flush()
        self._audit("dossier_notarial", dossier, DossierNotarialRead, utilisateur, "SIGNATURE")
        return dossier

    @atomic
    def record_movement(self, identifier, payload, *, utilisateur):
        # Same lock order as payment transitions: payment then dossier. The sale
        # link is immutable once signed; the first read does not acquire a lock.
        dossier = self.get_dossier(identifier)
        if dossier.id_vente is None:
            raise NotarialValidationError("The authentic deed must be recorded first")
        payment = self.repository.payment(dossier.id_vente)
        if payment is None:
            raise NotarialValidationError("Calculate the existing sale remuneration snapshot first")
        dossier = self.get_dossier(identifier, lock=True)
        movements = self.repository.movements(identifier)
        for existing in movements:
            if existing.reference == payload.reference:
                if (existing.nature, existing.montant, existing.date_operation) == (payload.nature, payload.montant, payload.date_operation):
                    return existing
                raise NotarialConflictError("This reference already identifies a different movement")
        if payment.statut != "ATTENDU" or payment.montant_honoraires is None:
            raise NotarialConflictError("Movements require an expected agency-fee payment")
        today = datetime.now(timezone.utc).date()
        if not payment.date_acte_authentique <= payload.date_operation <= today:
            raise NotarialValidationError("Movement must follow signing and cannot be in the future")
        if movements and payload.date_operation < max(m.date_operation for m in movements):
            raise NotarialValidationError("Movements must be recorded in chronological order")
        collected = sum((m.montant for m in movements if m.nature == "COLLECTE_NOTAIRE"), Decimal(0))
        received = sum((m.montant for m in movements if m.nature == "RECEPTION_ENTREPRISE"), Decimal(0))
        if payload.nature == "COLLECTE_NOTAIRE":
            collected += payload.montant
        else:
            received += payload.montant
        if not received <= collected <= payment.montant_honoraires:
            raise NotarialValidationError("Receipt cannot exceed collection; collection cannot exceed agency fees")
        record = self.repository.add(MouvementNotarial(
            id_dossier_notarial=identifier, **payload.model_dump(),
        ))
        self._audit("mouvement_notarial", record, MouvementNotarialRead, utilisateur, "RECORD_AGENCY_FEE_MOVEMENT")
        if received == payment.montant_honoraires:
            PaiementService(self.session).transition(
                payment.id_paiement, statut_cible="RECU", utilisateur=utilisateur,
                date_reception_honoraires=payload.date_operation, commit=False,
            )
        return record
