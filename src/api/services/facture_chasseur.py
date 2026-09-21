from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.facture_chasseur import FactureChasseur
from src.api.repositories.facture_chasseur import FactureChasseurRepository
from src.api.repositories.paiement import PaiementRepository
from src.api.schemas.facture_chasseur import (
    FactureChasseurCreate, FactureChasseurDecision, FactureChasseurRead,
)
from src.api.services.audit_log import AuditLogService
from src.api.services.paiement import PaiementError, PaiementService


class FactureChasseurNotFoundError(Exception):
    pass


class FactureChasseurConflictError(Exception):
    pass


class FactureChasseurValidationError(Exception):
    pass


class FactureChasseurService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = FactureChasseurRepository(session)
        self.payments = PaiementRepository(session)
        self.payment_service = PaiementService(session)
        self.audit = AuditLogService(session)

    def list_factures(self, chasseur_id: int | None = None) -> list[FactureChasseur]:
        return self.repository.list_accessible(chasseur_id)

    def get_facture(self, invoice_id: int, chasseur_id: int | None = None) -> FactureChasseur:
        invoice = self.repository.get_by_id(invoice_id, chasseur_id)
        if invoice is None:
            raise FactureChasseurNotFoundError("Resource not found")
        return invoice

    @staticmethod
    def _validate_payment(payment) -> None:
        today = datetime.now(timezone.utc).date()
        if (
            payment.statut not in {"RECU", "VERIFIE", "PROGRAMME"}
            or payment.droit_remuneration is not True
            or payment.id_chasseur_beneficiaire is None
            or payment.id_vente is None
            or payment.montant_chasseur is None or payment.montant_chasseur <= 0
            or payment.date_reception_honoraires is None
            or payment.date_acte_authentique is None
            or not payment.date_acte_authentique <= payment.date_reception_honoraires <= today
        ):
            raise FactureChasseurConflictError("Payment is not eligible for hunter invoicing")

    def submit(
        self, payload: FactureChasseurCreate, *, chasseur_id: int,
        utilisateur: str, id_utilisateur: int,
    ) -> FactureChasseur:
        try:
            # All writers lock payment first, then invoice, preventing lock inversion.
            payment = self.payments.get_by_id_for_update(payload.id_paiement)
            if payment is None or payment.id_chasseur_beneficiaire != chasseur_id:
                raise FactureChasseurNotFoundError("Resource not found")
            self._validate_payment(payment)
            today = datetime.now(timezone.utc).date()
            if not payment.date_reception_honoraires <= payload.date_facture <= today:
                raise FactureChasseurValidationError("Invoice date must be between fee receipt and today")
            latest = self.repository.get_latest(payment.id_paiement)
            if latest is not None and latest.statut != "REJETEE":
                raise FactureChasseurConflictError("A pending or conforming invoice already exists")
            invoice = self.repository.create(FactureChasseur(
                id_paiement=payment.id_paiement,
                id_chasseur=payment.id_chasseur_beneficiaire,
                numero_version=1 if latest is None else latest.numero_version + 1,
                numero_facture=payload.numero_facture, date_facture=payload.date_facture,
                montant=payload.montant, statut="SOUMISE",
                date_soumission=datetime.now(timezone.utc),
            ))
            self._audit(invoice, "INSERT", "submit_facture_chasseur", utilisateur,
                        id_utilisateur, expected_amount=payment.montant_chasseur)
            self.session.commit()
            self.session.refresh(invoice)
            return invoice
        except IntegrityError as exc:
            self._integrity_error(exc)
        except Exception:
            self.session.rollback()
            raise

    def decide(
        self, invoice_id: int, payload: FactureChasseurDecision, *,
        utilisateur: str, id_utilisateur: int,
    ) -> FactureChasseur:
        try:
            reference = self.get_facture(invoice_id)
            payment = self.payments.get_by_id_for_update(reference.id_paiement)
            if payment is None:
                raise FactureChasseurNotFoundError("Resource not found")
            invoice = self.repository.get_by_id_for_update(invoice_id)
            if invoice is None:
                raise FactureChasseurNotFoundError("Resource not found")
            if invoice.statut != "SOUMISE":
                raise FactureChasseurConflictError("Only a submitted invoice can be reviewed")
            if payment.statut in {"ANNULE", "PAYE"}:
                raise FactureChasseurConflictError("A terminal payment cannot be reviewed")
            if payload.statut == "CONFORME":
                self._validate_payment(payment)
                if (invoice.id_chasseur != payment.id_chasseur_beneficiaire
                        or invoice.montant != payment.montant_chasseur
                        or not payment.date_reception_honoraires <= invoice.date_facture <= datetime.now(timezone.utc).date()):
                    raise FactureChasseurValidationError("Invoice does not match the payment beneficiary, amount or dates")
            old = FactureChasseurRead.model_validate(invoice).model_dump(mode="json")
            invoice.statut = payload.statut
            invoice.date_verification = datetime.now(timezone.utc)
            invoice.id_verificateur = id_utilisateur
            invoice.motif_rejet = payload.motif_rejet
            self.session.flush()
            self._audit(invoice, "UPDATE", "decide_facture_chasseur", utilisateur,
                        id_utilisateur, old=old, expected_amount=payment.montant_chasseur)
            if invoice.statut == "CONFORME":
                if payment.statut == "RECU":
                    self.payment_service.transition(payment.id_paiement, statut_cible="VERIFIE",
                                                    utilisateur=utilisateur, commit=False)
                if payment.statut == "VERIFIE":
                    self.payment_service.transition(payment.id_paiement, statut_cible="PROGRAMME",
                                                    utilisateur=utilisateur, commit=False)
            self.session.commit()
            self.session.refresh(invoice)
            return invoice
        except IntegrityError as exc:
            self._integrity_error(exc)
        except PaiementError as exc:
            self.session.rollback()
            raise FactureChasseurConflictError(str(exc)) from exc
        except Exception:
            self.session.rollback()
            raise

    def _audit(self, invoice, operation, action, actor, actor_id, *, old=None, expected_amount):
        self.audit.log_change(
            table_name="facture_chasseur", operation=operation,
            record_id=invoice.id_facture_chasseur, utilisateur=actor,
            ancienne_valeur=old,
            nouvelle_valeur=FactureChasseurRead.model_validate(invoice).model_dump(mode="json"),
            contexte={"source": "api", "action": action, "id_utilisateur": actor_id,
                      "id_paiement": invoice.id_paiement, "numero_version": invoice.numero_version,
                      "montant_chasseur_attendu": str(expected_amount)},
        )

    def _integrity_error(self, exc):
        self.session.rollback()
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint in {"uq_facture_chasseur_active", "uq_facture_chasseur_paiement_version"}:
            raise FactureChasseurConflictError("Concurrent or duplicate invoice submission") from exc
        raise FactureChasseurValidationError("Hunter invoice violates database constraints") from exc
