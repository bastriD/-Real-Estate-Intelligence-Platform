from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.api.v1.endpoints import factures_clients as endpoints
from src.api.core.dependencies import get_current_user
from src.api.db.models.facture_client import FactureClient
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.services.facture_client import (
    FactureClientAlreadyExistsError, FactureClientNotFoundError, FactureClientValidationError,
)


@pytest.fixture
def api(monkeypatch):
    app = FastAPI()
    app.include_router(endpoints.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: MagicMock()
    service = MagicMock()
    invoice = FactureClient(
        id_facture_client=1, id_vente=2, id_client=3, id_parametres_honoraires=4,
        numero_facture="FC-0000000002", date_emission=date(2026, 1, 2),
        montant_achat=Decimal("420000.00"), montant_fixe_applique=Decimal("3000.00"),
        taux_pourcentage_applique=Decimal("0.0250"), montant_honoraires_ht=Decimal("13500.00"),
        date_creation=datetime.now(timezone.utc),
    )
    service.create_facture.return_value = invoice
    service.get_facture.return_value = invoice
    service.list_factures.return_value = [invoice]
    monkeypatch.setattr(endpoints, "FactureClientService", lambda db: service)
    with TestClient(app) as client:
        yield app, client, service


def login(app, role, identity=3):
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        id_utilisateur=1, email="actor@example.com", role=role,
        id_client=identity if role == "CLIENT" else None,
        id_chasseur=identity if role == "CHASSEUR" else None,
    )


URL = "/api/v1/factures-clients"


def test_admin_issues_invoice_and_propagates_actor(api):
    app, client, service = api
    login(app, "ADMIN")
    response = client.post(URL, json={"id_vente": 2})
    assert response.status_code == 201
    assert response.json()["montant_honoraires_ht"] == "13500.00"
    assert response.json()["id_client"] == 3
    assert service.create_facture.call_args.kwargs == {
        "utilisateur": "actor@example.com", "id_utilisateur": 1,
    }


@pytest.mark.parametrize("role", ["ADMIN", "CLIENT", "CHASSEUR"])
def test_reads_use_only_authenticated_scope(api, role):
    app, client, service = api
    login(app, role)
    assert client.get(URL + "?id_client=999&chasseur_id=999").status_code == 200
    expected = {"client_id": 3 if role == "CLIENT" else None,
                "chasseur_id": 3 if role == "CHASSEUR" else None}
    service.list_factures.assert_called_once_with(**expected)
    assert client.get(URL + "/1").status_code == 200
    service.get_facture.assert_called_once_with(1, **expected)


@pytest.mark.parametrize("role", ["CLIENT", "CHASSEUR"])
def test_missing_business_identity_fails_closed(api, role):
    app, client, service = api
    login(app, role, None)
    assert client.get(URL).status_code == 403
    assert client.get(URL + "/1").status_code == 403
    service.list_factures.assert_not_called()
    service.get_facture.assert_not_called()


@pytest.mark.parametrize("role", ["CLIENT", "CHASSEUR"])
def test_cross_owner_and_absent_have_identical_not_found(api, role):
    app, client, service = api
    login(app, role)
    service.get_facture.side_effect = FactureClientNotFoundError("Resource not found")
    foreign = client.get(URL + "/42")
    absent = client.get(URL + "/9999")
    assert foreign.status_code == absent.status_code == 404
    assert foreign.json() == absent.json() == {"detail": "Resource not found"}


@pytest.mark.parametrize("role", ["CLIENT", "CHASSEUR", "SERVICE"])
def test_only_admin_can_issue(api, role):
    app, client, service = api
    login(app, role)
    assert client.post(URL, json={"id_vente": 2}).status_code == 403
    service.create_facture.assert_not_called()


def test_service_cannot_read_financial_invoices(api):
    app, client, service = api
    login(app, "SERVICE")
    assert client.get(URL).status_code == 403
    assert client.get(URL + "/1").status_code == 403
    service.list_factures.assert_not_called()


def test_unauthenticated_requests_are_rejected(api):
    _, client, service = api
    assert client.get(URL).status_code == 401
    assert client.get(URL + "/1").status_code == 401
    assert client.post(URL, json={"id_vente": 2}).status_code == 401
    service.create_facture.assert_not_called()


@pytest.mark.parametrize("error,code", [
    (FactureClientNotFoundError, 404),
    (FactureClientAlreadyExistsError, 409),
    (FactureClientValidationError, 422),
])
def test_creation_domain_errors(api, error, code):
    app, client, service = api
    login(app, "ADMIN")
    service.create_facture.side_effect = error("rejected")
    assert client.post(URL, json={"id_vente": 2}).status_code == code


@pytest.mark.parametrize("field", [
    "id_client", "id_parametres_honoraires", "montant_achat", "montant_fixe_applique",
    "taux_pourcentage_applique", "montant_honoraires_ht", "numero_facture", "date_emission",
    "statut", "date_reception_honoraires",
])
def test_creation_rejects_forged_authoritative_fields(api, field):
    app, client, service = api
    login(app, "ADMIN")
    assert client.post(URL, json={"id_vente": 2, field: "1"}).status_code == 422
    service.create_facture.assert_not_called()


@pytest.mark.parametrize("body", [{}, {"id_vente": 0}, {"id_vente": -1}, {"id_vente": "invalid"}])
def test_invalid_creation_payload(api, body):
    app, client, service = api
    login(app, "ADMIN")
    assert client.post(URL, json=body).status_code == 422
    service.create_facture.assert_not_called()


def test_no_generic_mutation_routes_and_router_registered():
    from src.api.main import app

    paths = app.openapi()["paths"]
    assert set(paths[URL]) == {"get", "post"}
    assert set(paths[URL + "/{invoice_id}"]) == {"get"}
