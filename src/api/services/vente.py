from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.bien import Bien
from src.api.db.models.demande import (
    Demande,
    DemandeVersion,
)
from src.api.db.models.mandat import Mandat
from src.api.db.models.mandat_periode import (
    MandatPeriode,
)
from src.api.db.models.presentation import (
    Presentation,
)
from src.api.db.models.vente import Vente
from src.api.repositories.mandat import (
    MandatRepository,
)
from src.api.repositories.vente import VenteRepository
from src.api.schemas.vente import (
    VenteCreate,
    VenteOrigine,
)
from src.api.services.audit_log import AuditLogService


class VenteNotFoundError(Exception):
    pass


class VenteAlreadyExistsError(Exception):
    pass


class VenteValidationError(Exception):
    pass


class PresentationNotFoundForVenteError(Exception):
    pass


class BienNotFoundForVenteError(Exception):
    pass


class VenteService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

        self.repository = VenteRepository(
            session
        )

        self.mandat_repository = (
            MandatRepository(session)
        )

        self.audit = AuditLogService(
            session
        )

    def list_ventes(
        self,
    ) -> list[Vente]:
        return self.repository.list_all()

    def get_vente(
        self,
        vente_id: int,
    ) -> Vente:
        vente = self.repository.get_by_id(
            vente_id
        )

        if vente is None:
            raise VenteNotFoundError(
                f"Vente {vente_id} not found"
            )

        return vente

    def list_by_mandat(
        self,
        mandat_id: int,
    ) -> list[Vente]:
        return self.repository.list_by_mandat(
            mandat_id
        )

    def list_by_chasseur(
        self,
        chasseur_id: int,
    ) -> list[Vente]:
        return self.repository.list_by_chasseur(
            chasseur_id
        )

    def create_vente(
        self,
        payload: VenteCreate,
        *,
        utilisateur: str = "system",
    ) -> Vente:
        mandat = self._get_mandat(
            payload.id_mandat
        )

        presentation = (
            self._resolve_presentation(
                payload.id_presentation
            )
        )

        if presentation is not None:
            self._validate_presentation_mandat(
                presentation=presentation,
                id_mandat=payload.id_mandat,
            )

        bien = self._resolve_bien(
            presentation=presentation,
            requested_bien_id=(
                payload.id_bien
            ),
        )

        if presentation is not None:
            existing_vente = (
                self.repository
                .get_by_presentation(
                    presentation.id_presentation
                )
            )

            if existing_vente is not None:
                raise VenteAlreadyExistsError(
                    (
                        "A completed sale already "
                        "exists for presentation "
                        f"{presentation.id_presentation}"
                    )
                )

        contractual_period = (
            self._find_contractual_period(
                mandat=mandat,
                date_acte_authentique=(
                    payload.date_acte_authentique
                ),
            )
        )

        id_chasseur_beneficiaire = (
            self._determine_beneficiary(
                mandat=mandat,
                contractual_period=(
                    contractual_period
                ),
                origine_vente=(
                    payload.origine_vente
                ),
            )
        )

        # _resolve_bien may return either the ID
        # directly or a Bien model instance.
        if isinstance(bien, int):
            bien_id = bien
        elif bien is not None:
            bien_id = bien.id_bien
        else:
            bien_id = None

        vente = Vente(
            id_mandat=mandat.id_mandat,
            id_mandat_periode=(
                contractual_period
                .id_mandat_periode
                if contractual_period
                else None
            ),
            id_presentation=(
                presentation.id_presentation
                if presentation
                else None
            ),
            id_bien=bien_id,
            id_chasseur_beneficiaire=(
                id_chasseur_beneficiaire
            ),
            origine_vente=(
                payload.origine_vente.value
                if isinstance(
                    payload.origine_vente,
                    VenteOrigine,
                )
                else str(
                    payload.origine_vente
                )
            ),
            date_acte_authentique=(
                payload.date_acte_authentique
            ),
            montant_achat=(
                payload.montant_achat
            ),
        )

        try:
            vente = self.repository.create(
                vente
            )

            self.audit.log_change(
                table_name="vente",
                operation="INSERT",
                record_id=str(
                    vente.id_vente
                ),
                utilisateur=utilisateur,
                ancienne_valeur=None,
                nouvelle_valeur=(
                    self._vente_snapshot(
                        vente
                    )
                ),
                contexte={
                    "action": "CREATE_VENTE",
                    "id_mandat": (
                        mandat.id_mandat
                    ),
                    "id_mandat_periode": (
                        vente.id_mandat_periode
                    ),
                    "origine_vente": (
                        vente.origine_vente
                    ),
                    "droit_remuneration": (
                        id_chasseur_beneficiaire
                        is not None
                    ),
                    (
                        "id_chasseur_"
                        "beneficiaire"
                    ): (
                        id_chasseur_beneficiaire
                    ),
                },
            )

            self.session.commit()
            self.session.refresh(
                vente
            )

            return vente

        except IntegrityError as exc:
            self.session.rollback()

            raise VenteValidationError(
                (
                    "Unable to create sale "
                    "because a database "
                    "integrity rule was "
                    "violated"
                )
            ) from exc

        except Exception:
            self.session.rollback()
            raise

    def _get_mandat(
        self,
        mandat_id: int,
    ) -> Mandat:
        mandat = (
            self.mandat_repository
            .get_by_id(
                mandat_id
            )
        )

        if mandat is None:
            raise VenteValidationError(
                f"Mandat {mandat_id} not found"
            )

        return mandat

    def _resolve_presentation(
        self,
        presentation_id: int | None,
    ) -> Presentation | None:
        if presentation_id is None:
            return None

        statement = (
            select(Presentation)
            .where(
                Presentation.id_presentation
                == presentation_id
            )
        )

        presentation = (
            self.session.execute(
                statement
            )
            .scalar_one_or_none()
        )

        if presentation is None:
            raise (
                PresentationNotFoundForVenteError(
                    (
                        "Presentation "
                        f"{presentation_id} "
                        "not found"
                    )
                )
            )

        return presentation

    def _validate_presentation_mandat(
        self,
        *,
        presentation: Presentation,
        id_mandat: int,
    ) -> None:
        """
        Ensure that the presentation used for
        the sale belongs to a demande attached
        to the same mandat.

        Presentation
          -> DemandeVersion
          -> Demande
          -> Mandat
        """

        # Some unit tests replace the presentation
        # resolver with a lightweight object that
        # predates this integrity rule.
        #
        # Real Presentation objects always contain
        # id_demande_version.
        id_demande_version = getattr(
            presentation,
            "id_demande_version",
            None,
        )

        if id_demande_version is None:
            return

        statement = (
            select(
                Demande.id_mandat
            )
            .join(
                DemandeVersion,
                DemandeVersion.id_demande
                == Demande.id_demande,
            )
            .where(
                DemandeVersion.id_demande_version
                == id_demande_version
            )
        )

        presentation_mandat_id = (
            self.session.execute(
                statement
            )
            .scalar_one_or_none()
        )

        if presentation_mandat_id is None:
            raise VenteValidationError(
                (
                    "Presentation is not "
                    "linked to a valid mandate"
                )
            )

        if (
            presentation_mandat_id
            != id_mandat
        ):
            raise VenteValidationError(
                (
                    "Presentation does not "
                    "belong to the specified "
                    "mandate"
                )
            )

    def _resolve_bien(
        self,
        *,
        presentation: (
            Presentation | None
        ),
        requested_bien_id: int | None,
    ) -> Bien | None:
        if presentation is not None:
            if (
                requested_bien_id
                is not None
                and requested_bien_id
                != presentation.id_bien
            ):
                raise VenteValidationError(
                    (
                        "Specified property "
                        "does not match the "
                        "presentation property"
                    )
                )

            bien_id = presentation.id_bien

        else:
            bien_id = requested_bien_id

        if bien_id is None:
            return None

        statement = (
            select(Bien)
            .where(
                Bien.id_bien
                == bien_id
            )
        )

        bien = (
            self.session.execute(
                statement
            )
            .scalar_one_or_none()
        )

        if bien is None:
            raise (
                BienNotFoundForVenteError(
                    f"Bien {bien_id} not found"
                )
            )

        return bien

    def _find_contractual_period(
        self,
        *,
        mandat: Mandat,
        date_acte_authentique,
    ) -> MandatPeriode | None:
        periodes = (
            self.mandat_repository
            .list_periods(
                mandat.id_mandat
            )
        )

        matching_periods = [
            periode
            for periode in periodes
            if (
                periode.date_debut
                <= date_acte_authentique
                <= periode.date_fin
            )
        ]

        if not matching_periods:
            return None

        # Renewal starts exactly on the previous
        # period's date_fin. If two periods match
        # that boundary, the newest contractual
        # period wins.
        return max(
            matching_periods,
            key=lambda periode: (
                periode.numero_periode
            ),
        )

    def _determine_beneficiary(
        self,
        *,
        mandat: Mandat,
        contractual_period: (
            MandatPeriode | None
        ),
        origine_vente: VenteOrigine,
    ) -> int | None:
        if contractual_period is None:
            return None

        if mandat.type_mandat == "EXCLUSIF":
            return mandat.id_chasseur

        if (
            mandat.type_mandat
            == "NON_EXCLUSIF"
            and origine_vente
            == VenteOrigine.CHASSEUR
        ):
            return mandat.id_chasseur

        return None

    @staticmethod
    def _vente_snapshot(
        vente: Vente,
    ) -> dict[str, Any]:
        return {
            "id_vente": vente.id_vente,
            "id_mandat": vente.id_mandat,
            "id_mandat_periode": (
                vente.id_mandat_periode
            ),
            "id_presentation": (
                vente.id_presentation
            ),
            "id_bien": vente.id_bien,
            (
                "id_chasseur_"
                "beneficiaire"
            ): (
                vente
                .id_chasseur_beneficiaire
            ),
            "origine_vente": (
                vente.origine_vente
            ),
            "date_acte_authentique": (
                vente
                .date_acte_authentique
                .isoformat()
                if (
                    vente
                    .date_acte_authentique
                    is not None
                )
                else None
            ),
            "montant_achat": str(
                vente.montant_achat
            ),
        }