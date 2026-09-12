from calendar import monthrange
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.db.models.chasseur import Chasseur
from src.api.db.models.mandat import Mandat
from src.api.db.models.paiement import Paiement
from src.api.db.models.vente import Vente
from src.api.db.models.visite import Visite
from src.api.repositories.bareme_commission import (
    BaremeCommissionRepository,
)
from src.api.repositories.paiement import (
    PaiementRepository,
)
from src.api.repositories.palier_performance import (
    PalierPerformanceRepository,
)
from src.api.repositories.parametres_honoraires import (
    ParametresHonorairesRepository,
)
from src.api.repositories.parametres_remuneration import (
    ParametresRemunerationRepository,
)
from src.api.repositories.vente import VenteRepository
from src.api.services.audit_log import AuditLogService
from src.api.services.remuneration_calculator import (
    PerformanceScores,
    PerformanceWeights,
    RemunerationCalculationInput,
    RemunerationCalculationResult,
    calculate_company_fees,
    calculate_remuneration,
)


class RemunerationError(Exception):
    pass


class RemunerationNotFoundError(RemunerationError):
    pass


class RemunerationAlreadyCalculatedError(RemunerationError):
    pass


class RemunerationConfigurationError(RemunerationError):
    pass


class RemunerationDataError(RemunerationError):
    pass


class RemunerationService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

        self.vente_repository = VenteRepository(
            session
        )

        self.paiement_repository = (
            PaiementRepository(session)
        )

        self.honoraires_repository = (
            ParametresHonorairesRepository(
                session
            )
        )

        self.remuneration_repository = (
            ParametresRemunerationRepository(
                session
            )
        )

        self.palier_repository = (
            PalierPerformanceRepository(
                session
            )
        )

        self.bareme_repository = (
            BaremeCommissionRepository(
                session
            )
        )

        self.audit = AuditLogService(
            session
        )

    # ======================================================================
    # PUBLIC API
    # ======================================================================

    def calculate_for_vente(
        self,
        vente_id: int,
        *,
        utilisateur: str = "system",
    ) -> Paiement:
        """
        Create the immutable remuneration snapshot
        associated with one completed sale.

        The sale is the source of truth for:
        - mandate
        - contractual period
        - beneficiary
        - origin
        - authentic-deed date
        - purchase amount

        A vente may only be calculated once.
        """

        vente = self._get_vente(
            vente_id
        )

        existing = (
            self.paiement_repository
            .get_by_vente(
                vente.id_vente
            )
        )

        if existing is not None:
            raise (
                RemunerationAlreadyCalculatedError(
                    (
                        "Remuneration has already "
                        "been calculated for vente "
                        f"{vente.id_vente}"
                    )
                )
            )

        mandat = self._get_mandat(
            vente.id_mandat
        )

        honoraires_parameters = (
            self.honoraires_repository
            .get_effective(
                vente.date_acte_authentique
            )
        )

        if honoraires_parameters is None:
            raise (
                RemunerationConfigurationError(
                    (
                        "No active company-fee "
                        "parameters are valid on "
                        f"{vente.date_acte_authentique}"
                    )
                )
            )

        droit_remuneration = (
            vente.id_chasseur_beneficiaire
            is not None
        )

        if not droit_remuneration:
            return self._create_without_entitlement(
                vente=vente,
                mandat=mandat,
                honoraires_parameters=(
                    honoraires_parameters
                ),
                utilisateur=utilisateur,
            )

        return self._create_with_entitlement(
            vente=vente,
            mandat=mandat,
            honoraires_parameters=(
                honoraires_parameters
            ),
            utilisateur=utilisateur,
        )

    def get_paiement(
        self,
        paiement_id: int,
    ) -> Paiement:
        paiement = (
            self.paiement_repository
            .get_by_id(
                paiement_id
            )
        )

        if paiement is None:
            raise RemunerationNotFoundError(
                (
                    f"Paiement {paiement_id} "
                    "not found"
                )
            )

        return paiement

    def get_by_vente(
        self,
        vente_id: int,
    ) -> Paiement:
        paiement = (
            self.paiement_repository
            .get_by_vente(
                vente_id
            )
        )

        if paiement is None:
            raise RemunerationNotFoundError(
                (
                    "No remuneration calculation "
                    "exists for vente "
                    f"{vente_id}"
                )
            )

        return paiement

    # ======================================================================
    # ENTITLED SALE
    # ======================================================================

    def _create_with_entitlement(
        self,
        *,
        vente: Vente,
        mandat: Mandat,
        honoraires_parameters,
        utilisateur: str,
    ) -> Paiement:
        chasseur = self._get_chasseur(
            vente.id_chasseur_beneficiaire
        )

        remuneration_parameters = (
            self.remuneration_repository
            .get_effective(
                vente.date_acte_authentique
            )
        )

        if remuneration_parameters is None:
            raise (
                RemunerationConfigurationError(
                    (
                        "No active remuneration "
                        "parameters are valid on "
                        f"{vente.date_acte_authentique}"
                    )
                )
            )

        bareme = (
            self.bareme_repository
            .get_effective_for_amount(
                id_chasseur=(
                    chasseur.id_chasseur
                ),
                amount=vente.montant_achat,
                effective_date=(
                    vente.date_acte_authentique
                ),
            )
        )

        if bareme is None:
            raise (
                RemunerationConfigurationError(
                    (
                        "No approved commission "
                        "grid applies to hunter "
                        f"{chasseur.id_chasseur} "
                        "for purchase amount "
                        f"{vente.montant_achat} "
                        "on "
                        f"{vente.date_acte_authentique}"
                    )
                )
            )

        (
            semaines_mandat_acte,
            nb_visites,
            annees_anciennete,
            nb_ventes,
            nb_mandats,
        ) = self._calculate_business_inputs(
            vente=vente,
            mandat=mandat,
            chasseur=chasseur,
            fenetre_mois=(
                remuneration_parameters
                .fenetre_mois
            ),
        )

        note_delai = self._performance_note(
            id_parametres_remuneration=(
                remuneration_parameters
                .id_parametres_remuneration
            ),
            critere="DELAI_SEMAINES",
            value=semaines_mandat_acte,
        )

        note_visites = self._performance_note(
            id_parametres_remuneration=(
                remuneration_parameters
                .id_parametres_remuneration
            ),
            critere="VISITES",
            value=nb_visites,
        )

        note_exclusivite = (
            remuneration_parameters
            .note_exclusif
            if (
                mandat.type_mandat
                == "EXCLUSIF"
            )
            else remuneration_parameters
            .note_non_exclusif
        )

        note_ventes = min(
            Decimal("100"),
            (
                Decimal(nb_ventes)
                * remuneration_parameters
                .points_par_vente
            ),
        )

        note_mandats = min(
            Decimal("100"),
            (
                Decimal(nb_mandats)
                * remuneration_parameters
                .points_par_mandat
            ),
        )

        calculation_input = (
            RemunerationCalculationInput(
                montant_achat=(
                    vente.montant_achat
                ),
                montant_fixe_honoraires=(
                    honoraires_parameters
                    .montant_fixe
                ),
                taux_honoraires=(
                    honoraires_parameters
                    .taux_pourcentage
                ),
                scores=PerformanceScores(
                    delai=note_delai,
                    exclusivite=(
                        note_exclusivite
                    ),
                    ventes=note_ventes,
                    mandats=note_mandats,
                    visites=note_visites,
                ),
                weights=PerformanceWeights(
                    delai=(
                        remuneration_parameters
                        .poids_delai
                    ),
                    exclusivite=(
                        remuneration_parameters
                        .poids_exclusivite
                    ),
                    ventes=(
                        remuneration_parameters
                        .poids_ventes
                    ),
                    mandats=(
                        remuneration_parameters
                        .poids_mandats
                    ),
                    visites=(
                        remuneration_parameters
                        .poids_visites
                    ),
                ),
                taux_base=(
                    bareme.taux_commission
                ),
                annees_anciennete=(
                    annees_anciennete
                ),
                taux_anciennete_par_annee=(
                    remuneration_parameters
                    .taux_anciennete_par_annee
                ),
                plafond_anciennete=(
                    remuneration_parameters
                    .plafond_anciennete
                ),
                score_pivot=(
                    remuneration_parameters
                    .score_pivot
                ),
                amplitude_performance=(
                    remuneration_parameters
                    .amplitude_performance
                ),
                taux_plancher=(
                    remuneration_parameters
                    .taux_plancher
                ),
                taux_plafond=(
                    remuneration_parameters
                    .taux_plafond
                ),
            )
        )

        result = calculate_remuneration(
            calculation_input
        )

        paiement = Paiement(
            date_acte_authentique=(
                vente.date_acte_authentique
            ),
            montant_achat=(
                result.montant_achat
            ),
            montant_honoraires=(
                result.montant_honoraires
            ),
            montant_chasseur=(
                result.montant_chasseur
            ),
            statut="ATTENDU",
            id_mandat=(
                vente.id_mandat
            ),
            id_bareme=(
                bareme.id_bareme
            ),
            id_vente=(
                vente.id_vente
            ),
            id_chasseur_beneficiaire=(
                chasseur.id_chasseur
            ),
            id_parametres_honoraires=(
                honoraires_parameters
                .id_parametres_honoraires
            ),
            id_parametres_remuneration=(
                remuneration_parameters
                .id_parametres_remuneration
            ),
            date_calcul=(
                datetime.now(
                    timezone.utc
                )
            ),
            droit_remuneration=True,
            motif_refus=None,
            semaines_mandat_acte=(
                semaines_mandat_acte
            ),
            nb_visites_calcul=(
                nb_visites
            ),
            annees_anciennete_calcul=(
                annees_anciennete
            ),
            nb_ventes_fenetre=(
                nb_ventes
            ),
            nb_mandats_fenetre=(
                nb_mandats
            ),
            note_delai=(
                note_delai
            ),
            note_exclusivite=(
                note_exclusivite
            ),
            note_ventes=(
                note_ventes
            ),
            note_mandats=(
                note_mandats
            ),
            note_visites=(
                note_visites
            ),
            score_performance=(
                result.score_performance
            ),
            taux_base=(
                result.taux_base
            ),
            majoration_anciennete=(
                result.majoration_anciennete
            ),
            modulation_performance=(
                result.modulation_performance
            ),
            taux_final=(
                result.taux_final
            ),
        )

        return self._persist(
            paiement=paiement,
            vente=vente,
            utilisateur=utilisateur,
            calculation_result=result,
        )

    # ======================================================================
    # SALE WITHOUT REMUNERATION RIGHT
    # ======================================================================

    def _create_without_entitlement(
        self,
        *,
        vente: Vente,
        mandat: Mandat,
        honoraires_parameters,
        utilisateur: str,
    ) -> Paiement:
        motif_refus = (
            "MANDAT_EXPIRE"
            if vente.id_mandat_periode is None
            else "HORS_DISPOSITIF"
        )

        montant_honoraires = (
            calculate_company_fees(
                montant_achat=(
                    vente.montant_achat
                ),
                montant_fixe=(
                    honoraires_parameters
                    .montant_fixe
                ),
                taux_pourcentage=(
                    honoraires_parameters
                    .taux_pourcentage
                ),
            )
        )

        semaines_mandat_acte = (
            self._weeks_between(
                mandat.date_debut,
                vente.date_acte_authentique,
            )
        )

        paiement = Paiement(
            date_acte_authentique=(
                vente.date_acte_authentique
            ),
            montant_achat=(
                vente.montant_achat
            ),
            montant_honoraires=(
                montant_honoraires
            ),
            montant_chasseur=(
                Decimal("0.00")
            ),
            statut="ATTENDU",
            id_mandat=(
                vente.id_mandat
            ),
            id_bareme=None,
            id_vente=(
                vente.id_vente
            ),
            id_chasseur_beneficiaire=None,
            id_parametres_honoraires=(
                honoraires_parameters
                .id_parametres_honoraires
            ),
            id_parametres_remuneration=None,
            date_calcul=(
                datetime.now(
                    timezone.utc
                )
            ),
            droit_remuneration=False,
            motif_refus=motif_refus,
            semaines_mandat_acte=(
                semaines_mandat_acte
            ),
            nb_visites_calcul=None,
            annees_anciennete_calcul=None,
            nb_ventes_fenetre=None,
            nb_mandats_fenetre=None,
            note_delai=None,
            note_exclusivite=None,
            note_ventes=None,
            note_mandats=None,
            note_visites=None,
            score_performance=None,
            taux_base=None,
            majoration_anciennete=None,
            modulation_performance=None,
            taux_final=None,
        )

        return self._persist(
            paiement=paiement,
            vente=vente,
            utilisateur=utilisateur,
            calculation_result=None,
        )

    # ======================================================================
    # BUSINESS INPUTS
    # ======================================================================

    def _calculate_business_inputs(
        self,
        *,
        vente: Vente,
        mandat: Mandat,
        chasseur: Chasseur,
        fenetre_mois: int,
    ) -> tuple[int, int, int, int, int]:
        semaines_mandat_acte = (
            self._weeks_between(
                mandat.date_debut,
                vente.date_acte_authentique,
            )
        )

        nb_visites = (
            self._count_visits(
                vente
            )
        )

        annees_anciennete = (
            self._completed_years(
                chasseur.date_entree,
                vente.date_acte_authentique,
            )
        )

        window_start = (
            self._subtract_months(
                vente.date_acte_authentique,
                fenetre_mois,
            )
        )

        nb_ventes = (
            self._count_previous_sales(
                id_chasseur=(
                    chasseur.id_chasseur
                ),
                current_vente_id=(
                    vente.id_vente
                ),
                window_start=window_start,
                window_end=(
                    vente.date_acte_authentique
                ),
            )
        )

        nb_mandats = (
            self._count_signed_mandates(
                id_chasseur=(
                    chasseur.id_chasseur
                ),
                window_start=window_start,
                window_end=(
                    vente.date_acte_authentique
                ),
            )
        )

        return (
            semaines_mandat_acte,
            nb_visites,
            annees_anciennete,
            nb_ventes,
            nb_mandats,
        )

    def _performance_note(
        self,
        *,
        id_parametres_remuneration: int,
        critere: str,
        value: int,
    ) -> Decimal:
        note = (
            self.palier_repository
            .get_note_for_value(
                id_parametres_remuneration,
                critere,
                value,
            )
        )

        if note is None:
            raise (
                RemunerationConfigurationError(
                    (
                        "No performance tier "
                        f"configured for {critere} "
                        f"with value {value}"
                    )
                )
            )

        return Decimal(note)

    def _count_visits(
        self,
        vente: Vente,
    ) -> int:
        if vente.id_presentation is None:
            return 0

        statement = (
            select(
                func.count(
                    Visite.id_visite
                )
            )
            .where(
                Visite.id_presentation
                == vente.id_presentation,
                Visite.statut
                == "REALISEE",
                func.date(
                    Visite.date_visite
                )
                <= vente.date_acte_authentique,
            )
        )

        return int(
            self.session.scalar(
                statement
            )
            or 0
        )

    def _count_previous_sales(
        self,
        *,
        id_chasseur: int,
        current_vente_id: int,
        window_start: date,
        window_end: date,
    ) -> int:
        statement = (
            select(
                func.count(
                    Vente.id_vente
                )
            )
            .where(
                Vente.id_chasseur_beneficiaire
                == id_chasseur,
                Vente.id_vente
                != current_vente_id,
                Vente.date_acte_authentique
                >= window_start,
                Vente.date_acte_authentique
                <= window_end,
            )
        )

        return int(
            self.session.scalar(
                statement
            )
            or 0
        )

    def _count_signed_mandates(
        self,
        *,
        id_chasseur: int,
        window_start: date,
        window_end: date,
    ) -> int:
        statement = (
            select(
                func.count(
                    Mandat.id_mandat
                )
            )
            .where(
                Mandat.id_chasseur
                == id_chasseur,
                Mandat.date_signature
                >= window_start,
                Mandat.date_signature
                <= window_end,
            )
        )

        return int(
            self.session.scalar(
                statement
            )
            or 0
        )

    # ======================================================================
    # LOOKUPS
    # ======================================================================

    def _get_vente(
        self,
        vente_id: int,
    ) -> Vente:
        vente = (
            self.vente_repository
            .get_by_id(
                vente_id
            )
        )

        if vente is None:
            raise RemunerationNotFoundError(
                (
                    f"Vente {vente_id} "
                    "not found"
                )
            )

        return vente

    def _get_mandat(
        self,
        mandat_id: int,
    ) -> Mandat:
        statement = (
            select(Mandat)
            .where(
                Mandat.id_mandat
                == mandat_id
            )
        )

        mandat = (
            self.session.scalar(
                statement
            )
        )

        if mandat is None:
            raise RemunerationDataError(
                (
                    f"Mandat {mandat_id} "
                    "not found"
                )
            )

        return mandat

    def _get_chasseur(
        self,
        chasseur_id: int | None,
    ) -> Chasseur:
        if chasseur_id is None:
            raise RemunerationDataError(
                (
                    "Sale has no remuneration "
                    "beneficiary"
                )
            )

        statement = (
            select(Chasseur)
            .where(
                Chasseur.id_chasseur
                == chasseur_id
            )
        )

        chasseur = (
            self.session.scalar(
                statement
            )
        )

        if chasseur is None:
            raise RemunerationDataError(
                (
                    f"Chasseur {chasseur_id} "
                    "not found"
                )
            )

        if chasseur.date_entree is None:
            raise RemunerationDataError(
                (
                    "Hunter entry date is "
                    "required to calculate "
                    "seniority"
                )
            )

        return chasseur

    # ======================================================================
    # PERSISTENCE / AUDIT
    # ======================================================================

    def _persist(
        self,
        *,
        paiement: Paiement,
        vente: Vente,
        utilisateur: str,
        calculation_result: (
            RemunerationCalculationResult
            | None
        ),
    ) -> Paiement:
        try:
            paiement = (
                self.paiement_repository
                .create(
                    paiement
                )
            )

            self.audit.log_change(
                table_name="paiement",
                operation="INSERT",
                record_id=(
                    paiement.id_paiement
                ),
                utilisateur=utilisateur,
                ancienne_valeur=None,
                nouvelle_valeur=(
                    self._paiement_snapshot(
                        paiement
                    )
                ),
                contexte={
                    "action": (
                        "CALCUL_REMUNERATION"
                    ),
                    "id_vente": (
                        vente.id_vente
                    ),
                    "droit_remuneration": (
                        paiement
                        .droit_remuneration
                    ),
                    "motif_refus": (
                        paiement.motif_refus
                    ),
                    (
                        "id_chasseur_"
                        "beneficiaire"
                    ): (
                        paiement
                        .id_chasseur_beneficiaire
                    ),
                    "score_performance": (
                        str(
                            calculation_result
                            .score_performance
                        )
                        if calculation_result
                        is not None
                        else None
                    ),
                    "taux_final": (
                        str(
                            calculation_result
                            .taux_final
                        )
                        if calculation_result
                        is not None
                        else None
                    ),
                },
            )

            self.session.commit()

            self.session.refresh(
                paiement
            )

            return paiement

        except IntegrityError as exc:
            self.session.rollback()

            raise (
                RemunerationAlreadyCalculatedError(
                    (
                        "Unable to persist "
                        "remuneration calculation. "
                        "A calculation may already "
                        "exist for vente "
                        f"{vente.id_vente}"
                    )
                )
            ) from exc

        except Exception:
            self.session.rollback()
            raise

    # ======================================================================
    # DATE HELPERS
    # ======================================================================

    @staticmethod
    def _weeks_between(
        start_date: date,
        end_date: date,
    ) -> int:
        if end_date < start_date:
            raise RemunerationDataError(
                (
                    "Authentic-deed date cannot "
                    "precede mandate start date"
                )
            )

        return (
            end_date - start_date
        ).days // 7

    @staticmethod
    def _completed_years(
        start_date: date | None,
        end_date: date,
    ) -> int:
        if start_date is None:
            raise RemunerationDataError(
                (
                    "Hunter entry date is "
                    "required"
                )
            )

        if end_date < start_date:
            raise RemunerationDataError(
                (
                    "Authentic-deed date cannot "
                    "precede hunter entry date"
                )
            )

        years = (
            end_date.year
            - start_date.year
        )

        anniversary_has_passed = (
            (
                end_date.month,
                end_date.day,
            )
            >= (
                start_date.month,
                start_date.day,
            )
        )

        if not anniversary_has_passed:
            years -= 1

        return years

    @staticmethod
    def _subtract_months(
        value: date,
        months: int,
    ) -> date:
        if months <= 0:
            raise RemunerationConfigurationError(
                (
                    "Performance window must "
                    "contain at least one month"
                )
            )

        total_months = (
            value.year * 12
            + value.month
            - 1
            - months
        )

        year = (
            total_months // 12
        )

        month = (
            total_months % 12
            + 1
        )

        day = min(
            value.day,
            monthrange(
                year,
                month,
            )[1],
        )

        return date(
            year,
            month,
            day,
        )

    # ======================================================================
    # SNAPSHOT
    # ======================================================================

    @staticmethod
    def _paiement_snapshot(
        paiement: Paiement,
    ) -> dict[str, Any]:
        def decimal_to_string(
            value,
        ):
            if value is None:
                return None

            return str(value)

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
            "id_bareme": (
                paiement.id_bareme
            ),
            (
                "id_parametres_"
                "honoraires"
            ): (
                paiement
                .id_parametres_honoraires
            ),
            (
                "id_parametres_"
                "remuneration"
            ): (
                paiement
                .id_parametres_remuneration
            ),
            "date_acte_authentique": (
                paiement
                .date_acte_authentique
                .isoformat()
                if (
                    paiement
                    .date_acte_authentique
                    is not None
                )
                else None
            ),
            "date_calcul": (
                paiement.date_calcul.isoformat()
                if paiement.date_calcul
                is not None
                else None
            ),
            "montant_achat": (
                decimal_to_string(
                    paiement.montant_achat
                )
            ),
            "montant_honoraires": (
                decimal_to_string(
                    paiement
                    .montant_honoraires
                )
            ),
            "montant_chasseur": (
                decimal_to_string(
                    paiement.montant_chasseur
                )
            ),
            "droit_remuneration": (
                paiement
                .droit_remuneration
            ),
            "motif_refus": (
                paiement.motif_refus
            ),
            "semaines_mandat_acte": (
                paiement
                .semaines_mandat_acte
            ),
            "nb_visites_calcul": (
                paiement.nb_visites_calcul
            ),
            (
                "annees_anciennete_"
                "calcul"
            ): (
                paiement
                .annees_anciennete_calcul
            ),
            "nb_ventes_fenetre": (
                paiement.nb_ventes_fenetre
            ),
            "nb_mandats_fenetre": (
                paiement.nb_mandats_fenetre
            ),
            "note_delai": (
                decimal_to_string(
                    paiement.note_delai
                )
            ),
            "note_exclusivite": (
                decimal_to_string(
                    paiement
                    .note_exclusivite
                )
            ),
            "note_ventes": (
                decimal_to_string(
                    paiement.note_ventes
                )
            ),
            "note_mandats": (
                decimal_to_string(
                    paiement.note_mandats
                )
            ),
            "note_visites": (
                decimal_to_string(
                    paiement.note_visites
                )
            ),
            "score_performance": (
                decimal_to_string(
                    paiement
                    .score_performance
                )
            ),
            "taux_base": (
                decimal_to_string(
                    paiement.taux_base
                )
            ),
            "majoration_anciennete": (
                decimal_to_string(
                    paiement
                    .majoration_anciennete
                )
            ),
            "modulation_performance": (
                decimal_to_string(
                    paiement
                    .modulation_performance
                )
            ),
            "taux_final": (
                decimal_to_string(
                    paiement.taux_final
                )
            ),
            "statut": paiement.statut,
        }