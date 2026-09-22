from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from src.api.schemas.vente import (
    VenteCreate,
    VenteOrigine,
)
from src.api.services.vente import (
    VenteAlreadyExistsError,
    VenteNotFoundError,
    VenteService,
    VenteValidationError,
)


class FakeVenteRepository:
    def __init__(self):
        self.ventes = []
        self.existing_by_presentation = {}
        self.next_id = 1

    def list_all(self):
        return list(self.ventes)

    def get_by_id(self, vente_id):
        for vente in self.ventes:
            if vente.id_vente == vente_id:
                return vente

        return None

    def get_by_presentation(
        self,
        presentation_id,
    ):
        return self.existing_by_presentation.get(
            presentation_id
        )

    def list_by_mandat(
        self,
        mandat_id,
    ):
        return [
            vente
            for vente in self.ventes
            if vente.id_mandat == mandat_id
        ]

    def list_by_chasseur(
        self,
        chasseur_id,
    ):
        return [
            vente
            for vente in self.ventes
            if (
                vente.id_chasseur_beneficiaire
                == chasseur_id
            )
        ]

    def create(
        self,
        vente,
    ):
        if getattr(
            vente,
            "id_vente",
            None,
        ) is None:
            vente.id_vente = self.next_id
            self.next_id += 1

        self.ventes.append(
            vente
        )

        if (
            vente.id_presentation
            is not None
        ):
            self.existing_by_presentation[
                vente.id_presentation
            ] = vente

        return vente


class FakeMandatRepository:
    def __init__(
        self,
        *,
        type_mandat="EXCLUSIF",
    ):
        self.mandat = SimpleNamespace(
            id_mandat=11,
            id_chasseur=1,
            type_mandat=type_mandat,
        )

        self.periods = [
            SimpleNamespace(
                id_mandat_periode=17,
                id_mandat=11,
                numero_periode=1,
                date_debut=date(
                    2026,
                    1,
                    5,
                ),
                date_fin=date(
                    2026,
                    7,
                    5,
                ),
            )
        ]

    def get_by_id(
        self,
        mandat_id,
    ):
        if (
            mandat_id
            == self.mandat.id_mandat
        ):
            return self.mandat

        return None

    def list_periods(
        self,
        mandat_id,
    ):
        if (
            mandat_id
            != self.mandat.id_mandat
        ):
            return []

        return list(
            self.periods
        )


class FakeAuditLogService:
    def __init__(self):
        self.entries = []

    def log_change(
        self,
        **kwargs,
    ):
        self.entries.append(
            kwargs
        )


class FakeSession:
    def __init__(
        self,
    ):
        self.commits = 0
        self.rollbacks = 0
        self.refreshes = 0

    def commit(
        self,
    ):
        self.commits += 1

    def rollback(
        self,
    ):
        self.rollbacks += 1

    def refresh(
        self,
        obj,
    ):
        self.refreshes += 1


def build_service(
    *,
    type_mandat="EXCLUSIF",
):
    service = VenteService.__new__(
        VenteService
    )

    service.session = FakeSession()

    service.repository = (
        FakeVenteRepository()
    )

    service.mandat_repository = (
        FakeMandatRepository(
            type_mandat=type_mandat
        )
    )

    service.audit = (
        FakeAuditLogService()
    )

    # These tests focus on the Vente
    # business service. Database lookup of
    # Bien is tested independently from the
    # business decision itself.
    service._resolve_bien = (
        lambda *,
        presentation,
        requested_bien_id: (
            (
                presentation.id_bien
                if presentation
                is not None
                else requested_bien_id
            )
        )
    )

    service._resolve_presentation = (
        lambda presentation_id: (
            None
            if presentation_id
            is None
            else SimpleNamespace(
                id_presentation=(
                    presentation_id
                ),
                id_bien=123,
            )
        )
    )

    return service


def make_payload(
    *,
    id_mandat=11,
    id_presentation=None,
    id_bien=123,
    origine_vente=(
        VenteOrigine.CHASSEUR
    ),
    date_acte_authentique=(
        date(2026, 4, 10)
    ),
    montant_achat=(
        Decimal("420000.00")
    ),
):
    return VenteCreate(
        id_mandat=id_mandat,
        id_presentation=(
            id_presentation
        ),
        id_bien=id_bien,
        origine_vente=(
            origine_vente
        ),
        date_acte_authentique=(
            date_acte_authentique
        ),
        montant_achat=(
            montant_achat
        ),
    )


def test_get_vente_returns_existing_sale():
    service = build_service()

    existing = SimpleNamespace(
        id_vente=7,
        id_mandat=11,
        id_chasseur_beneficiaire=1,
    )

    service.repository.ventes.append(
        existing
    )

    result = service.get_vente(
        7
    )

    assert result is existing


def test_get_vente_unknown_sale_is_rejected():
    service = build_service()

    with pytest.raises(
        VenteNotFoundError,
        match="Vente 999 not found",
    ):
        service.get_vente(
            999
        )


def test_find_contractual_period():
    service = build_service()

    mandat = (
        service
        .mandat_repository
        .mandat
    )

    result = (
        service
        ._find_contractual_period(
            mandat=mandat,
            date_acte_authentique=(
                date(2026, 4, 10)
            ),
        )
    )

    assert result is not None
    assert (
        result.id_mandat_periode
        == 17
    )


def test_find_contractual_period_renewal_boundary_uses_newest_period():
    service = build_service()

    service.mandat_repository.periods.append(
        SimpleNamespace(
            id_mandat_periode=18,
            id_mandat=11,
            numero_periode=2,
            date_debut=date(
                2026,
                7,
                5,
            ),
            date_fin=date(
                2027,
                1,
                5,
            ),
        )
    )

    mandat = (
        service
        .mandat_repository
        .mandat
    )

    result = (
        service
        ._find_contractual_period(
            mandat=mandat,
            date_acte_authentique=(
                date(2026, 7, 5)
            ),
        )
    )

    assert result is not None
    assert (
        result.id_mandat_periode
        == 18
    )
    assert (
        result.numero_periode
        == 2
    )


@pytest.mark.parametrize(
    (
        "mandat_type",
        "origin",
        "expected",
    ),
    [
        (
            "EXCLUSIF",
            VenteOrigine.CHASSEUR,
            1,
        ),
        (
            "EXCLUSIF",
            VenteOrigine.CLIENT_SEUL,
            1,
        ),
        (
            "EXCLUSIF",
            VenteOrigine.AUTRE_AGENCE,
            1,
        ),
        (
            "NON_EXCLUSIF",
            VenteOrigine.CHASSEUR,
            1,
        ),
        (
            "NON_EXCLUSIF",
            VenteOrigine.CLIENT_SEUL,
            None,
        ),
        (
            "NON_EXCLUSIF",
            VenteOrigine.AUTRE_AGENCE,
            None,
        ),
    ],
)
def test_determine_beneficiary(
    mandat_type,
    origin,
    expected,
):
    service = build_service(
        type_mandat=mandat_type
    )

    mandat = (
        service
        .mandat_repository
        .mandat
    )

    period = (
        service
        .mandat_repository
        .periods[0]
    )

    result = (
        service
        ._determine_beneficiary(
            mandat=mandat,
            contractual_period=period,
            origine_vente=origin,
        )
    )

    assert result == expected


def test_no_contractual_period_means_no_beneficiary():
    service = build_service(
        type_mandat="EXCLUSIF"
    )

    mandat = (
        service
        .mandat_repository
        .mandat
    )

    result = (
        service
        ._determine_beneficiary(
            mandat=mandat,
            contractual_period=None,
            origine_vente=(
                VenteOrigine.CHASSEUR
            ),
        )
    )

    assert result is None


@pytest.mark.parametrize("commit", [True, False])
def test_create_exclusive_sale_freezes_period_and_beneficiary(commit):
    service = build_service(
        type_mandat="EXCLUSIF"
    )

    payload = make_payload(
        origine_vente=(
            VenteOrigine.CLIENT_SEUL
        )
    )

    result = service.create_vente(
        payload,
        commit=commit,
        utilisateur=(
            "admin@example.com"
        ),
    )

    assert result.id_vente == 1
    assert result.id_mandat == 11
    assert (
        result.id_mandat_periode
        == 17
    )
    assert result.id_bien == 123

    # Exclusive mandate:
    # hunter remains beneficiary even
    # when the client finds the property.
    assert (
        result.id_chasseur_beneficiaire
        == 1
    )

    assert (
        result.origine_vente
        == "CLIENT_SEUL"
    )

    assert (
        result.date_acte_authentique
        == date(2026, 4, 10)
    )

    assert (
        result.montant_achat
        == Decimal("420000.00")
    )

    assert (
        service.session.commits
        == int(commit)
    )

    assert (
        len(service.audit.entries)
        == 1
    )

    audit = (
        service.audit.entries[0]
    )

    assert (
        audit["table_name"]
        == "vente"
    )
    assert (
        audit["operation"]
        == "INSERT"
    )
    assert (
        audit["utilisateur"]
        == "admin@example.com"
    )
    assert (
        audit["contexte"][
            "droit_remuneration"
        ]
        is True
    )


def test_create_non_exclusive_client_sale_has_no_beneficiary():
    service = build_service(
        type_mandat="NON_EXCLUSIF"
    )

    payload = make_payload(
        origine_vente=(
            VenteOrigine.CLIENT_SEUL
        )
    )

    result = service.create_vente(
        payload
    )

    assert (
        result.id_mandat_periode
        == 17
    )

    assert (
        result.id_chasseur_beneficiaire
        is None
    )

    assert (
        result.origine_vente
        == "CLIENT_SEUL"
    )


def test_create_sale_after_expiry_has_no_period_or_beneficiary():
    service = build_service(
        type_mandat="EXCLUSIF"
    )

    payload = make_payload(
        date_acte_authentique=(
            date(2026, 8, 1)
        )
    )

    result = service.create_vente(
        payload
    )

    assert (
        result.id_mandat_periode
        is None
    )

    assert (
        result.id_chasseur_beneficiaire
        is None
    )


def test_create_rejects_duplicate_presentation():
    service = build_service()

    service.repository.existing_by_presentation[
        31
    ] = SimpleNamespace(
        id_vente=99
    )

    payload = make_payload(
        id_presentation=31,
        id_bien=None,
    )

    with pytest.raises(
        VenteAlreadyExistsError,
        match=(
            "A completed sale already "
            "exists for presentation 31"
        ),
    ):
        service.create_vente(
            payload
        )


def test_get_unknown_mandat_is_rejected():
    service = build_service()

    payload = make_payload(
        id_mandat=999,
        id_bien=None,
    )

    with pytest.raises(
        VenteValidationError,
        match="Mandat 999 not found",
    ):
        service.create_vente(
            payload
        )


def test_presentation_must_belong_to_same_mandat():
    service = build_service()

    presentation = SimpleNamespace(
        id_presentation=31,
        id_bien=123,
        id_demande_version=54,
    )

    service._resolve_presentation = (
        lambda presentation_id: (
            presentation
        )
    )

    class FakeScalarResult:
        def scalar_one_or_none(
            self,
        ):
            # Presentation belongs to
            # Mandat 99, while the Vente
            # payload requests Mandat 11.
            return 99

    class PresentationMandatSession(
        FakeSession
    ):
        def execute(
            self,
            statement,
        ):
            return FakeScalarResult()

    service.session = (
        PresentationMandatSession()
    )

    payload = make_payload(
        id_mandat=11,
        id_presentation=31,
        id_bien=123,
    )

    with pytest.raises(
        VenteValidationError,
        match=(
            "Presentation does not belong "
            "to the specified mandate"
        ),
    ):
        service.create_vente(
            payload,
            utilisateur=(
                "admin@example.com"
            ),
        )
