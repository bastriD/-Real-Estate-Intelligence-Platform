from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.api.v1.endpoints import secteurs, demandes
from src.api.core.dependencies import get_current_user
from src.api.db.models.bien import Bien
from src.api.db.session import get_db
from src.api.schemas.auth import AuthenticatedUser
from src.api.services.bien import BienNotFoundError
from src.api.services.secteur import SecteurService, SecteurValidationError
from tests.backend.test_demande_api import build_demande, build_version


def setup_service():
    db = MagicMock()
    service = SecteurService(db)
    service.repository = MagicMock()
    service.biens = MagicMock()
    service.audit = MagicMock()
    bien = SimpleNamespace(id_bien=1, id_secteur=None, ville="Montpellier")
    service.biens.get_for_update.return_value = bien
    service.repository.get_active.return_value = SimpleNamespace(id_secteur=3, ville="Montpellier")
    return service, db, bien


def test_assignment_audits_and_commits_verified_sector():
    service, db, bien = setup_service()
    assert service.assign_bien(1, 3, actor="admin@example.com", actor_id=7) is bien
    assert bien.id_secteur == 3
    event = service.audit.log_change.call_args.kwargs
    assert event["ancienne_valeur"] == {"id_secteur": None}
    assert event["nouvelle_valeur"] == {"id_secteur": 3}
    assert event["contexte"]["id_utilisateur"] == 7
    db.commit.assert_called_once()


@pytest.mark.parametrize("case", ["missing_property", "missing_sector", "other_city", "unknown_city", "audit_failure"])
def test_bad_assignment_cannot_commit(case):
    service, db, bien = setup_service()
    if case == "missing_property":
        service.biens.get_for_update.return_value = None
    elif case == "missing_sector":
        service.repository.get_active.return_value = None
    elif case == "other_city":
        bien.ville = "Lyon"
    elif case == "unknown_city":
        bien.ville = None
    else:
        service.audit.log_change.side_effect = RuntimeError("audit failure")
    with pytest.raises((BienNotFoundError, SecteurValidationError, RuntimeError)):
        service.assign_bien(1, 3, actor="admin@example.com", actor_id=7)
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_clear_and_idempotent_assignment():
    service, db, bien = setup_service()
    service.assign_bien(1, None, actor="admin@example.com", actor_id=7)
    db.commit.assert_not_called()
    bien.id_secteur = 3
    service.assign_bien(1, None, actor="admin@example.com", actor_id=7)
    assert bien.id_secteur is None
    db.commit.assert_called_once()


@pytest.fixture
def api(monkeypatch):
    app = FastAPI()
    app.include_router(secteurs.router, prefix="/api/v1")
    app.include_router(demandes.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: MagicMock()
    service = MagicMock()
    service.list_active.return_value = [dict(id_secteur=3, pays="France", ville="Montpellier",
        quartier="Beaux-Arts", code_postal="34000", actif=True)]
    service.assign_bien.return_value = Bien(id_bien=1, reference_externe="TEST-1",
        type_bien="Appartement", ville="Montpellier", id_secteur=3,
        date_collecte=datetime.now(timezone.utc), statut="ACTIF", id_source=1)
    monkeypatch.setattr(secteurs, "SecteurService", lambda db: service)
    with TestClient(app) as client:
        yield app, client, service


def login(app, role):
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        id_utilisateur=7, role=role, email="actor@example.com",
        id_client=4 if role == "CLIENT" else None, id_chasseur=3 if role == "CHASSEUR" else None)


@pytest.mark.parametrize("role", ["ADMIN", "CHASSEUR", "CLIENT", "SERVICE"])
def test_catalogue_and_assignment_roles(api, role):
    app, client, service = api
    login(app, role)
    result = client.get("/api/v1/secteurs")
    assert result.status_code == 200 and result.json()[0]["quartier"] == "Beaux-Arts"
    response = client.put("/api/v1/biens/1/secteur", json={"id_secteur": 3})
    assert response.status_code == (200 if role == "ADMIN" else 403)
    if role == "ADMIN":
        assert response.json()["id_secteur"] == 3
        service.assign_bien.assert_called_once_with(1, 3, actor="actor@example.com", actor_id=7)
    else:
        service.assign_bien.assert_not_called()


def test_unauthenticated_catalogue_and_assignment(api):
    _, client, service = api
    assert client.get("/api/v1/secteurs").status_code == 401
    assert client.put("/api/v1/biens/1/secteur", json={"id_secteur": 3}).status_code == 401
    service.assign_bien.assert_not_called()


@pytest.mark.parametrize("body", [{}, {"id_secteur": 0}, {"id_secteur": 3, "actor_id": 4}])
def test_assignment_payload_validation(api, body):
    app, client, service = api
    login(app, "ADMIN")
    assert client.put("/api/v1/biens/1/secteur", json=body).status_code == 422
    service.assign_bien.assert_not_called()


@pytest.mark.parametrize("error,status", [(BienNotFoundError(), 404), (SecteurValidationError("Invalid sector"), 422)])
def test_assignment_error_mapping(api, error, status):
    app, client, service = api
    login(app, "ADMIN")
    service.assign_bien.side_effect = error
    assert client.put("/api/v1/biens/1/secteur", json={"id_secteur": 3}).status_code == status


def test_demande_api_passes_and_returns_version_sectors(api, monkeypatch):
    app, client, _ = api
    login(app, "ADMIN")
    service = MagicMock()
    service.create_demande.return_value = (build_demande(), build_version().model_copy(update={"secteur_ids": [1, 3]}))
    monkeypatch.setattr(demandes, "DemandeService", lambda db: service)
    response = client.post("/api/v1/demandes", json={"id_client": 4, "motif_modification": "Initial",
        "auteur_systeme": True, "secteur_ids": [1, 3]})
    assert response.status_code == 201
    assert response.json()["current_version"]["secteur_ids"] == [1, 3]
    assert service.create_demande.call_args.args[0].secteur_ids == [1, 3]


def test_openapi_registers_sector_discovery_and_assignment():
    from src.api.main import app
    paths = app.openapi()["paths"]
    assert set(paths["/api/v1/secteurs"]) == {"get"}
    assert set(paths["/api/v1/biens/{bien_id}/secteur"]) == {"put"}
