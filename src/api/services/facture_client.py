from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.facture_client import FactureClient
from src.api.repositories.facture_client import FactureClientRepository
from src.api.repositories.parametres_honoraires import ParametresHonorairesRepository
from src.api.schemas.facture_client import FactureClientCreate, FactureClientRead
from src.api.services.audit_log import AuditLogService
from src.api.services.remuneration_calculator import calculate_company_fees


class FactureClientNotFoundError(Exception):
    pass


class FactureClientAlreadyExistsError(Exception):
    pass


class FactureClientValidationError(Exception):
    pass


class FactureClientService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = FactureClientRepository(session)
        self.honoraires = ParametresHonorairesRepository(session)
        self.audit = AuditLogService(session)

    def list_factures(
        self, *, client_id: int | None = None, chasseur_id: int | None = None,
    ) -> list[FactureClient]:
        return self.repository.list_accessible(client_id=client_id, chasseur_id=chasseur_id)

    def get_facture(
        self, invoice_id: int, *, client_id: int | None = None,
        chasseur_id: int | None = None,
    ) -> FactureClient:
        invoice = self.repository.get_by_id(
            invoice_id, client_id=client_id, chasseur_id=chasseur_id,
        )
        if invoice is None:
            # Identical response for absent and foreign-owned invoices.
            raise FactureClientNotFoundError("Resource not found")
        return invoice

    def create_facture(
        self, payload: FactureClientCreate, *, utilisateur: str,
        id_utilisateur: int,
    ) -> FactureClient:
        try:
            context = self.repository.get_sale_context(payload.id_vente)
            if context is None:
                raise FactureClientNotFoundError("Resource not found")
            vente, mandat = context
            if self.repository.get_by_vente(vente.id_vente) is not None:
                raise FactureClientAlreadyExistsError("A client invoice already exists for this sale")

            today = datetime.now(timezone.utc).date()
            if vente.date_acte_authentique > today:
                raise FactureClientValidationError("The authentic deed must have occurred before invoice issuance")

            payment = self.repository.get_payment_for_update(vente.id_vente)
            if (
                payment is None
                or payment.statut not in {"RECU", "VERIFIE", "PROGRAMME", "PAYE"}
                or payment.date_reception_honoraires is None
                or not vente.date_acte_authentique <= payment.date_reception_honoraires <= today
            ):
                raise FactureClientValidationError("Company fees must have been received before invoice issuance")

            parameters = self.honoraires.get_effective(vente.date_acte_authentique)
            if parameters is None:
                raise FactureClientValidationError("No active company-fee parameters are valid on the authentic-deed date")
            fees = calculate_company_fees(
                montant_achat=vente.montant_achat,
                montant_fixe=parameters.montant_fixe,
                taux_pourcentage=parameters.taux_pourcentage,
            )
            if fees > Decimal("999999999999.99"):
                raise FactureClientValidationError("Company fees exceed the invoice amount precision")
            if (
                payment.id_mandat != vente.id_mandat
                or payment.date_acte_authentique != vente.date_acte_authentique
                or payment.montant_achat != vente.montant_achat
                or payment.id_parametres_honoraires != parameters.id_parametres_honoraires
                or payment.montant_honoraires != fees
            ):
                raise FactureClientValidationError("Received-fee snapshot differs from the sale or applicable configuration")

            invoice = self.repository.create(FactureClient(
                id_vente=vente.id_vente,
                id_client=mandat.id_client,
                id_parametres_honoraires=parameters.id_parametres_honoraires,
                # One immutable invoice per sale; no max()+1 race or UUID.
                numero_facture=f"FC-{vente.id_vente:010d}",
                date_emission=today,
                montant_achat=vente.montant_achat,
                montant_fixe_applique=parameters.montant_fixe,
                taux_pourcentage_applique=parameters.taux_pourcentage,
                montant_honoraires_ht=fees,
            ))
            self.audit.log_change(
                table_name="facture_client", operation="INSERT",
                record_id=invoice.id_facture_client, utilisateur=utilisateur,
                nouvelle_valeur=FactureClientRead.model_validate(invoice).model_dump(mode="json"),
                contexte={
                    "source": "api", "action": "ISSUE_FACTURE_CLIENT",
                    "id_utilisateur": id_utilisateur, "id_mandat": mandat.id_mandat,
                    "id_vente": vente.id_vente, "id_paiement": payment.id_paiement,
                    "date_acte_authentique": vente.date_acte_authentique.isoformat(),
                    "date_reception_honoraires": payment.date_reception_honoraires.isoformat(),
                },
            )
            self.session.commit()
            self.session.refresh(invoice)
            return invoice
        except IntegrityError as exc:
            self.session.rollback()
            constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
            if constraint in {"uq_facture_client_vente", "uq_facture_client_numero"}:
                raise FactureClientAlreadyExistsError("A client invoice already exists for this sale") from exc
            raise FactureClientValidationError("Invoice creation violates database constraints") from exc
        except Exception:
            self.session.rollback()
            raise
