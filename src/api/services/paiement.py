from datetime import date
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.paiement import Paiement
from src.api.repositories.paiement import (
    PaiementRepository,
)
from src.api.services.audit_log import (
    AuditLogService,
)


class PaiementError(Exception):
    pass


class PaiementNotFoundError(
    PaiementError
):
    pass


class PaiementTransitionError(
    PaiementError
):
    pass


class PaiementValidationError(
    PaiementError
):
    pass


class PaiementService:
    TRANSITIONS = {
        "ATTENDU": {
            "RECU",
            "ANNULE",
        },
        "RECU": {
            "VERIFIE",
            "ANNULE",
        },
        "VERIFIE": {
            "PROGRAMME",
            "ANNULE",
        },
        "PROGRAMME": {
            "PAYE",
            "ANNULE",
        },
        "PAYE": set(),
        "ANNULE": set(),
    }

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

        self.repository = (
            PaiementRepository(
                session
            )
        )

        self.audit = (
            AuditLogService(
                session
            )
        )

    def get_paiement(
        self,
        paiement_id: int,
    ) -> Paiement:
        paiement = (
            self.repository.get_by_id(
                paiement_id
            )
        )

        if paiement is None:
            raise PaiementNotFoundError(
                (
                    f"Paiement {paiement_id} "
                    "not found"
                )
            )

        return paiement

    def transition(
        self,
        paiement_id: int,
        *,
        statut_cible: str,
        utilisateur: str,
        date_reception_honoraires: (
            date | None
        ) = None,
        date_paiement_chasseur: (
            date | None
        ) = None,
        motif_annulation: (
            str | None
        ) = None,
        commit: bool = True,
    ) -> Paiement:
        statut_cible = (
            statut_cible
            .strip()
            .upper()
        )

        paiement = (
            self.repository
            .get_by_id_for_update(
                paiement_id
            )
        )

        if paiement is None:
            raise PaiementNotFoundError(
                (
                    f"Paiement {paiement_id} "
                    "not found"
                )
            )

        statut_source = (
            paiement.statut
        )

        if statut_cible == statut_source:
            return paiement

        self._validate_transition(
            paiement=paiement,
            statut_source=statut_source,
            statut_cible=statut_cible,
            date_reception_honoraires=(
                date_reception_honoraires
            ),
            date_paiement_chasseur=(
                date_paiement_chasseur
            ),
            motif_annulation=(
                motif_annulation
            ),
        )

        if statut_cible in {"VERIFIE", "PROGRAMME", "PAYE"}:
            if not self.repository.has_conforming_invoice(paiement_id):
                raise PaiementTransitionError(
                    "A conforming hunter invoice matching the payment is required"
                )

        ancienne_valeur = (
            self._paiement_snapshot(
                paiement
            )
        )

        if statut_cible == "RECU":
            paiement.date_reception_honoraires = (
                date_reception_honoraires
            )

        if statut_cible == "PAYE":
            paiement.date_paiement_chasseur = (
                date_paiement_chasseur
            )

        paiement.statut = (
            statut_cible
        )

        nouvelle_valeur = (
            self._paiement_snapshot(
                paiement
            )
        )

        try:
            self.audit.log_change(
                table_name="paiement",
                operation="UPDATE",
                record_id=(
                    paiement.id_paiement
                ),
                utilisateur=utilisateur,
                ancienne_valeur=(
                    ancienne_valeur
                ),
                nouvelle_valeur=(
                    nouvelle_valeur
                ),
                contexte={
                    "source": "api",
                    "action": (
                        "transition_paiement"
                    ),
                    "from_status": (
                        statut_source
                    ),
                    "to_status": (
                        statut_cible
                    ),
                    "id_vente": (
                        paiement.id_vente
                    ),
                    (
                        "id_chasseur_"
                        "beneficiaire"
                    ): (
                        paiement
                        .id_chasseur_beneficiaire
                    ),
                    "motif_annulation": (
                        motif_annulation
                        if (
                            statut_cible
                            == "ANNULE"
                        )
                        else None
                    ),
                },
            )

            if commit:
                self.session.commit()
            else:
                # The invoice service owns the enclosing invoice/payment/audit transaction.
                self.session.flush()

            self.session.refresh(
                paiement
            )

            return paiement

        except IntegrityError as exc:
            self.session.rollback()

            raise PaiementValidationError(
                (
                    "Payment transition "
                    "violates database "
                    "constraints"
                )
            ) from exc

        except Exception:
            self.session.rollback()
            raise

    def _validate_transition(
        self,
        *,
        paiement: Paiement,
        statut_source: str,
        statut_cible: str,
        date_reception_honoraires: (
            date | None
        ),
        date_paiement_chasseur: (
            date | None
        ),
        motif_annulation: (
            str | None
        ),
    ) -> None:
        if (
            statut_source
            not in self.TRANSITIONS
        ):
            raise PaiementTransitionError(
                (
                    "Unknown current payment "
                    f"status: {statut_source}"
                )
            )

        if (
            statut_cible
            not in self.TRANSITIONS
        ):
            raise PaiementTransitionError(
                (
                    "Unknown target payment "
                    f"status: {statut_cible}"
                )
            )

        allowed = (
            self.TRANSITIONS[
                statut_source
            ]
        )

        if statut_cible not in allowed:
            raise PaiementTransitionError(
                (
                    "Invalid payment transition: "
                    f"{statut_source} -> "
                    f"{statut_cible}"
                )
            )

        if (
            paiement.droit_remuneration
            is False
            and statut_cible
            not in {"RECU", "ANNULE"}
        ):
            raise PaiementTransitionError(
                (
                    "A payment without "
                    "remuneration entitlement "
                    "can only record company-fee receipt or be cancelled"
                )
            )

        if statut_cible == "RECU":
            if (
                date_reception_honoraires
                is None
            ):
                raise PaiementValidationError(
                    (
                        "date_reception_honoraires "
                        "is required when payment "
                        "status becomes RECU"
                    )
                )

            if (
                date_reception_honoraires
                < paiement.date_acte_authentique
            ):
                raise PaiementValidationError(
                    (
                        "Company-fee reception "
                        "date cannot precede the "
                        "authentic-deed date"
                    )
                )

        elif (
            date_reception_honoraires
            is not None
        ):
            raise PaiementValidationError(
                (
                    "date_reception_honoraires "
                    "may only be supplied when "
                    "target status is RECU"
                )
            )

        if statut_cible == "PAYE":
            if (
                date_paiement_chasseur
                is None
            ):
                raise PaiementValidationError(
                    (
                        "date_paiement_chasseur "
                        "is required when payment "
                        "status becomes PAYE"
                    )
                )

            if (
                paiement
                .date_reception_honoraires
                is None
            ):
                raise PaiementValidationError(
                    (
                        "Company fees must have "
                        "been received before "
                        "hunter payment"
                    )
                )

            if (
                date_paiement_chasseur
                < paiement
                .date_reception_honoraires
            ):
                raise PaiementValidationError(
                    (
                        "Hunter payment date "
                        "cannot precede company-"
                        "fee reception date"
                    )
                )

        elif (
            date_paiement_chasseur
            is not None
        ):
            raise PaiementValidationError(
                (
                    "date_paiement_chasseur "
                    "may only be supplied when "
                    "target status is PAYE"
                )
            )

        if statut_cible == "ANNULE":
            if (
                motif_annulation is None
                or not motif_annulation.strip()
            ):
                raise PaiementValidationError(
                    (
                        "motif_annulation is "
                        "required when cancelling "
                        "a payment"
                    )
                )

        elif (
            motif_annulation
            is not None
        ):
            raise PaiementValidationError(
                (
                    "motif_annulation may only "
                    "be supplied when target "
                    "status is ANNULE"
                )
            )

    @staticmethod
    def _paiement_snapshot(
        paiement: Paiement,
    ) -> dict[str, Any]:
        def date_string(
            value: date | None,
        ) -> str | None:
            if value is None:
                return None

            return value.isoformat()

        return {
            "id_paiement": (
                paiement.id_paiement
            ),
            "id_vente": (
                paiement.id_vente
            ),
            "id_mandat": (
                paiement.id_mandat
            ),
            (
                "id_chasseur_"
                "beneficiaire"
            ): (
                paiement
                .id_chasseur_beneficiaire
            ),
            "droit_remuneration": (
                paiement
                .droit_remuneration
            ),
            "statut": (
                paiement.statut
            ),
            (
                "date_reception_"
                "honoraires"
            ): (
                date_string(
                    paiement
                    .date_reception_honoraires
                )
            ),
            (
                "date_paiement_"
                "chasseur"
            ): (
                date_string(
                    paiement
                    .date_paiement_chasseur
                )
            ),
        }
