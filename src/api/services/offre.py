from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.offre import Offre
from src.api.repositories.offre import OffreRepository
from src.api.schemas.offre import (
    OffreCreate,
    OffreDecision,
    OffreRevision,
)
from src.api.services.audit_log import AuditLogService


class OffreError(Exception):
    pass


class OffreNotFoundError(OffreError):
    pass


class PresentationNotFoundForOffreError(
    OffreError
):
    pass


class OffreTransitionError(OffreError):
    pass


class OffreValidationError(OffreError):
    pass


class OffreService:
    TRANSITIONS = {
        "SOUMISE": {
            "ACCEPTEE",
            "REFUSEE",
            "RETIREE",
            "EXPIREE",
            "REVISEE",
        },
        "ACCEPTEE": set(),
        "REFUSEE": set(),
        "RETIREE": set(),
        "EXPIREE": set(),
        "REVISEE": set(),
    }

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session
        self.repository = OffreRepository(
            session
        )
        self.audit = AuditLogService(
            session
        )

    def list_offres(
        self,
        presentation_id: int | None = None,
    ) -> list[Offre]:
        if presentation_id is not None:
            return (
                self.repository
                .list_by_presentation(
                    presentation_id
                )
            )

        return self.repository.list_all()

    def list_offres_for_chasseur(
        self,
        chasseur_id: int,
        presentation_id: int | None = None,
    ) -> list[Offre]:
        return (
            self.repository
            .list_accessible_by_chasseur(
                chasseur_id=chasseur_id,
                presentation_id=(
                    presentation_id
                ),
            )
        )

    def get_offre(
        self,
        offre_id: int,
    ) -> Offre:
        offre = self.repository.get_by_id(
            offre_id
        )

        if offre is None:
            raise OffreNotFoundError(
                f"Offre {offre_id} not found"
            )

        return offre

    def get_demande_id_for_offre(
        self,
        offre_id: int,
    ) -> int:
        demande_id = (
            self.repository.get_demande_id(
                offre_id
            )
        )

        if demande_id is None:
            raise OffreNotFoundError(
                f"Offre {offre_id} not found"
            )

        return demande_id

    def get_demande_id_for_presentation(
        self,
        presentation_id: int,
    ) -> int:
        demande_id = (
            self.repository
            .get_demande_id_for_presentation(
                presentation_id
            )
        )

        if demande_id is None:
            raise PresentationNotFoundForOffreError(
                (
                    "Presentation "
                    f"{presentation_id} "
                    "not found"
                )
            )

        return demande_id

    def create_offre(
        self,
        payload: OffreCreate,
        utilisateur: str | None = None,
    ) -> Offre:
        self.get_demande_id_for_presentation(
            payload.id_presentation
        )

        existing = (
            self.repository
            .get_latest_for_presentation(
                payload.id_presentation
            )
        )

        if existing is not None:
            raise OffreValidationError(
                (
                    "Presentation "
                    f"{payload.id_presentation} "
                    "already has an offer history; "
                    "use the revision workflow"
                )
            )

        offre = Offre(
            id_presentation=(
                payload.id_presentation
            ),
            numero_version=1,
            montant=payload.montant,
            date_expiration=(
                payload.date_expiration
            ),
            statut="SOUMISE",
            commentaire=payload.commentaire,
        )

        try:
            offre = self.repository.create(
                offre
            )

            self.audit.log_change(
                table_name="offre",
                operation="INSERT",
                record_id=offre.id_offre,
                utilisateur=utilisateur,
                nouvelle_valeur=(
                    self._offre_snapshot(
                        offre
                    )
                ),
                contexte={
                    "source": "api",
                    "action": "create_offre",
                    "id_presentation": (
                        offre.id_presentation
                    ),
                    "numero_version": (
                        offre.numero_version
                    ),
                },
            )

            self.session.commit()
            self.session.refresh(offre)

            return offre

        except IntegrityError as exc:
            self.session.rollback()

            raise OffreValidationError(
                (
                    "Offer creation violates "
                    "database constraints"
                )
            ) from exc

        except Exception:
            self.session.rollback()
            raise

    def decide_offre(
        self,
        offre_id: int,
        payload: OffreDecision,
        utilisateur: str | None = None,
    ) -> Offre:
        offre = (
            self.repository
            .get_by_id_for_update(
                offre_id
            )
        )

        if offre is None:
            raise OffreNotFoundError(
                f"Offre {offre_id} not found"
            )

        statut_source = offre.statut
        statut_cible = payload.statut.value

        self._validate_transition(
            statut_source=statut_source,
            statut_cible=statut_cible,
        )

        ancienne_valeur = (
            self._offre_snapshot(
                offre
            )
        )

        offre.statut = statut_cible
        offre.date_decision = datetime.now(
            timezone.utc
        )

        if payload.commentaire is not None:
            offre.commentaire = (
                payload.commentaire
            )

        try:
            offre = self.repository.save(
                offre
            )

            self.audit.log_change(
                table_name="offre",
                operation="UPDATE",
                record_id=offre.id_offre,
                utilisateur=utilisateur,
                ancienne_valeur=(
                    ancienne_valeur
                ),
                nouvelle_valeur=(
                    self._offre_snapshot(
                        offre
                    )
                ),
                contexte={
                    "source": "api",
                    "action": "decide_offre",
                    "from_status": (
                        statut_source
                    ),
                    "to_status": (
                        statut_cible
                    ),
                    "id_presentation": (
                        offre.id_presentation
                    ),
                    "numero_version": (
                        offre.numero_version
                    ),
                },
            )

            self.session.commit()
            self.session.refresh(offre)

            return offre

        except IntegrityError as exc:
            self.session.rollback()

            raise OffreValidationError(
                (
                    "Offer decision violates "
                    "database constraints"
                )
            ) from exc

        except Exception:
            self.session.rollback()
            raise

    def revise_offre(
        self,
        offre_id: int,
        payload: OffreRevision,
        utilisateur: str | None = None,
    ) -> Offre:
        current = (
            self.repository
            .get_by_id_for_update(
                offre_id
            )
        )

        if current is None:
            raise OffreNotFoundError(
                f"Offre {offre_id} not found"
            )

        latest = (
            self.repository
            .get_latest_for_presentation(
                current.id_presentation,
                for_update=True,
            )
        )

        if (
            latest is None
            or latest.id_offre
            != current.id_offre
        ):
            raise OffreTransitionError(
                (
                    "Only the latest offer "
                    "version can be revised"
                )
            )

        self._validate_transition(
            statut_source=current.statut,
            statut_cible="REVISEE",
        )

        ancienne_valeur = (
            self._offre_snapshot(
                current
            )
        )

        decision_time = datetime.now(
            timezone.utc
        )

        current.statut = "REVISEE"
        current.date_decision = (
            decision_time
        )

        new_offre = Offre(
            id_presentation=(
                current.id_presentation
            ),
            numero_version=(
                current.numero_version + 1
            ),
            montant=payload.montant,
            date_expiration=(
                payload.date_expiration
            ),
            statut="SOUMISE",
            commentaire=payload.commentaire,
        )

        try:
            current = self.repository.save(
                current
            )

            new_offre = self.repository.create(
                new_offre
            )

            self.audit.log_change(
                table_name="offre",
                operation="UPDATE",
                record_id=current.id_offre,
                utilisateur=utilisateur,
                ancienne_valeur=(
                    ancienne_valeur
                ),
                nouvelle_valeur=(
                    self._offre_snapshot(
                        current
                    )
                ),
                contexte={
                    "source": "api",
                    "action": "revise_offre",
                    "from_status": (
                        ancienne_valeur[
                            "statut"
                        ]
                    ),
                    "to_status": "REVISEE",
                    "new_offre_id": (
                        new_offre.id_offre
                    ),
                    "new_numero_version": (
                        new_offre.numero_version
                    ),
                },
            )

            self.audit.log_change(
                table_name="offre",
                operation="INSERT",
                record_id=new_offre.id_offre,
                utilisateur=utilisateur,
                nouvelle_valeur=(
                    self._offre_snapshot(
                        new_offre
                    )
                ),
                contexte={
                    "source": "api",
                    "action": "revise_offre",
                    "previous_offre_id": (
                        current.id_offre
                    ),
                    "id_presentation": (
                        new_offre.id_presentation
                    ),
                    "numero_version": (
                        new_offre.numero_version
                    ),
                },
            )

            self.session.commit()
            self.session.refresh(
                new_offre
            )

            return new_offre

        except IntegrityError as exc:
            self.session.rollback()

            raise OffreValidationError(
                (
                    "Offer revision violates "
                    "database constraints"
                )
            ) from exc

        except Exception:
            self.session.rollback()
            raise

    def _validate_transition(
        self,
        *,
        statut_source: str,
        statut_cible: str,
    ) -> None:
        if statut_source not in self.TRANSITIONS:
            raise OffreTransitionError(
                (
                    "Unknown current offer "
                    f"status: {statut_source}"
                )
            )

        if statut_cible not in self.TRANSITIONS:
            raise OffreTransitionError(
                (
                    "Unknown target offer "
                    f"status: {statut_cible}"
                )
            )

        if (
            statut_cible
            not in self.TRANSITIONS[
                statut_source
            ]
        ):
            raise OffreTransitionError(
                (
                    "Invalid offer transition: "
                    f"{statut_source} -> "
                    f"{statut_cible}"
                )
            )

    @staticmethod
    def _offre_snapshot(
        offre: Offre,
    ) -> dict[str, object]:
        return {
            "id_offre": offre.id_offre,
            "id_presentation": (
                offre.id_presentation
            ),
            "numero_version": (
                offre.numero_version
            ),
            "montant": str(
                offre.montant
            ),
            "date_offre": (
                offre.date_offre.isoformat()
                if offre.date_offre is not None
                else None
            ),
            "date_expiration": (
                offre.date_expiration.isoformat()
                if offre.date_expiration
                is not None
                else None
            ),
            "date_decision": (
                offre.date_decision.isoformat()
                if offre.date_decision
                is not None
                else None
            ),
            "statut": offre.statut,
            "commentaire": (
                offre.commentaire
            ),
            "date_creation": (
                offre.date_creation.isoformat()
                if offre.date_creation
                is not None
                else None
            ),
        }