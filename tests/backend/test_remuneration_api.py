from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.api.v1.endpoints import remunerations
from src.api.core.dependencies import require_roles
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.services.remuneration import (
    RemunerationAlreadyCalculatedError,
    RemunerationConfigurationError,
    RemunerationNotFoundError,
)


app = FastAPI()
app.include_router(remunerations.router)


def make_user(
    *,
    role: str,
    id_chasseur: int | None = None,
):
    return AuthenticatedUser(
        id_utilisateur=1,
        email="test@example.com",
        role=role,
        id_client=None,
        id_chasseur=id_chasseur,
    )


def make_paiement(
    *,
    paiement_id=10,
    vente_id=100,
    mandat_id=20,
):
    return SimpleNamespace(
        id_paiement=paiement_id,
        id_mandat=mandat_id,
        id_bareme=3,
        date_acte_authentique="2026-09-01",
        montant_achat="420000.00",
        montant_honoraires="13500.00",
        montant_chasseur="6231.60",
        statut="ATTENDU",
        id_vente=vente_id,
        id_chasseur_beneficiaire=1,
        id_parametres_honoraires=1,
        id_parametres_remuneration=2,
        date_calcul=None,
        droit_remuneration=True,
        motif_refus=None,
        semaines_mandat_acte=20,
        nb_visites_calcul=5,
        annees_anciennete_calcul=3,
        nb_ventes_fenetre=3,
        nb_mandats_fenetre=4,
        note_delai="80",
        note_exclusivite="100",
        note_ventes="60",
        note_mandats="40",
        note_visites="90",
        score_performance="73.5",
        taux_base="0.4000",
        majoration_anciennete="0.0600",
        modulation_performance="0.0940",
        taux_final="0.4616",
    )


def override_db():
    db = MagicMock()
    yield db


app.dependency_overrides[get_db] = override_db


def override_admin():
    return make_user(
        role="ADMIN",
    )


def override_chasseur():
    return make_user(
        role="CHASSEUR",
        id_chasseur=1,
    )


def override_other_chasseur():
    return make_user(
        role="CHASSEUR",
        id_chasseur=2,
    )


def _override_auth(user_factory):
    for route in app.routes:
        if not hasattr(route, "dependant"):
            continue

        for dependency in route.dependant.dependencies:
            call = dependency.call

            if getattr(call, "__name__", "") == "dependency":
                app.dependency_overrides[call] = user_factory


def reset_auth_overrides():
    keys = list(
        app.dependency_overrides.keys()
    )

    for key in keys:
        if key is not get_db:
            del app.dependency_overrides[key]


def setup_function():
    reset_auth_overrides()


def teardown_function():
    reset_auth_overrides()


def test_admin_can_calculate_remuneration(
    monkeypatch,
):
    _override_auth(
        override_admin
    )

    service = MagicMock()

    service._get_vente.return_value = (
        SimpleNamespace(
            id_vente=100,
            id_mandat=20,
        )
    )

    service.calculate_for_vente.return_value = (
        make_paiement()
    )

    monkeypatch.setattr(
        remunerations,
        "RemunerationService",
        lambda db: service,
    )

    mandat_repository = MagicMock()
    mandat_repository.get_by_id.return_value = (
        SimpleNamespace(
            id_mandat=20,
            id_chasseur=1,
        )
    )

    monkeypatch.setattr(
        remunerations,
        "MandatRepository",
        lambda db: mandat_repository,
    )

    client = TestClient(app)

    response = client.post(
        "/remunerations/ventes/100/calcul"
    )

    assert response.status_code == 201

    body = response.json()

    assert body["id_paiement"] == 10
    assert body["id_vente"] == 100
    assert body["droit_remuneration"] is True
    assert body["score_performance"] == "73.5"
    assert body["taux_final"] == "0.4616"
    assert body["montant_chasseur"] == "6231.60"


def test_duplicate_calculation_returns_409(
    monkeypatch,
):
    _override_auth(
        override_admin
    )

    service = MagicMock()

    service._get_vente.return_value = (
        SimpleNamespace(
            id_vente=100,
            id_mandat=20,
        )
    )

    service.calculate_for_vente.side_effect = (
        RemunerationAlreadyCalculatedError(
            "already calculated"
        )
    )

    monkeypatch.setattr(
        remunerations,
        "RemunerationService",
        lambda db: service,
    )

    monkeypatch.setattr(
        remunerations,
        "MandatRepository",
        lambda db: MagicMock(),
    )

    client = TestClient(app)

    response = client.post(
        "/remunerations/ventes/100/calcul"
    )

    assert response.status_code == 409


def test_missing_configuration_returns_422(
    monkeypatch,
):
    _override_auth(
        override_admin
    )

    service = MagicMock()

    service._get_vente.return_value = (
        SimpleNamespace(
            id_vente=100,
            id_mandat=20,
        )
    )

    service.calculate_for_vente.side_effect = (
        RemunerationConfigurationError(
            "configuration missing"
        )
    )

    monkeypatch.setattr(
        remunerations,
        "RemunerationService",
        lambda db: service,
    )

    monkeypatch.setattr(
        remunerations,
        "MandatRepository",
        lambda db: MagicMock(),
    )

    client = TestClient(app)

    response = client.post(
        "/remunerations/ventes/100/calcul"
    )

    assert response.status_code == 422


def test_admin_can_get_by_vente(
    monkeypatch,
):
    _override_auth(
        override_admin
    )

    service = MagicMock()

    service.get_by_vente.return_value = (
        make_paiement()
    )

    monkeypatch.setattr(
        remunerations,
        "RemunerationService",
        lambda db: service,
    )

    client = TestClient(app)

    response = client.get(
        "/remunerations/ventes/100"
    )

    assert response.status_code == 200
    assert response.json()["id_vente"] == 100


def test_missing_remuneration_returns_404(
    monkeypatch,
):
    _override_auth(
        override_admin
    )

    service = MagicMock()

    service.get_by_vente.side_effect = (
        RemunerationNotFoundError(
            "not found"
        )
    )

    monkeypatch.setattr(
        remunerations,
        "RemunerationService",
        lambda db: service,
    )

    client = TestClient(app)

    response = client.get(
        "/remunerations/ventes/999"
    )

    assert response.status_code == 404


def test_chasseur_can_get_own_remuneration(
    monkeypatch,
):
    _override_auth(
        override_chasseur
    )

    service = MagicMock()

    service.get_by_vente.return_value = (
        make_paiement(
            mandat_id=20
        )
    )

    monkeypatch.setattr(
        remunerations,
        "RemunerationService",
        lambda db: service,
    )

    mandat_repository = MagicMock()

    mandat_repository.get_by_id.return_value = (
        SimpleNamespace(
            id_mandat=20,
            id_chasseur=1,
        )
    )

    monkeypatch.setattr(
        remunerations,
        "MandatRepository",
        lambda db: mandat_repository,
    )

    client = TestClient(app)

    response = client.get(
        "/remunerations/ventes/100"
    )

    assert response.status_code == 200


def test_cross_owner_hidden_as_404(
    monkeypatch,
):
    _override_auth(
        override_other_chasseur
    )

    service = MagicMock()

    service.get_by_vente.return_value = (
        make_paiement(
            mandat_id=20
        )
    )

    monkeypatch.setattr(
        remunerations,
        "RemunerationService",
        lambda db: service,
    )

    mandat_repository = MagicMock()

    mandat_repository.get_by_id.return_value = (
        SimpleNamespace(
            id_mandat=20,
            id_chasseur=1,
        )
    )

    monkeypatch.setattr(
        remunerations,
        "MandatRepository",
        lambda db: mandat_repository,
    )

    client = TestClient(app)

    response = client.get(
        "/remunerations/ventes/100"
    )

    assert response.status_code == 404


def test_chasseur_without_identity_is_403(
    monkeypatch,
):
    _override_auth(
        lambda: make_user(
            role="CHASSEUR",
            id_chasseur=None,
        )
    )

    service = MagicMock()

    service.get_by_vente.return_value = (
        make_paiement()
    )

    monkeypatch.setattr(
        remunerations,
        "RemunerationService",
        lambda db: service,
    )

    client = TestClient(app)

    response = client.get(
        "/remunerations/ventes/100"
    )

    assert response.status_code == 403


def test_admin_can_get_paiement_by_id(
    monkeypatch,
):
    _override_auth(
        override_admin
    )

    service = MagicMock()

    service.get_paiement.return_value = (
        make_paiement(
            paiement_id=77
        )
    )

    monkeypatch.setattr(
        remunerations,
        "RemunerationService",
        lambda db: service,
    )

    client = TestClient(app)

    response = client.get(
        "/remunerations/77"
    )

    assert response.status_code == 200
    assert response.json()["id_paiement"] == 77