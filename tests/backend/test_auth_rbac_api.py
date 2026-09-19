from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import jwt
from fastapi.testclient import TestClient

from src.api.core.config import settings
from src.api.db.session import get_db
from src.api.main import app
from src.api.repositories.utilisateur import UtilisateurRepository


def build_user(
    *,
    utilisateur_id: int,
    email: str,
    role: str,
    actif: bool = True,
    id_client: int | None = None,
    id_chasseur: int | None = None,
) -> MagicMock:
    user = MagicMock()
    user.id_utilisateur = utilisateur_id
    user.email = email
    user.role = role
    user.actif = actif
    user.id_client = id_client
    user.id_chasseur = id_chasseur
    return user


def build_token(
    *,
    utilisateur_id: int,
    email: str,
    role: str,
) -> str:
    now = datetime.now(timezone.utc)

    return jwt.encode(
        {
            "sub": email,
            "uid": utilisateur_id,
            "role": role,
            "iat": now,
            "exp": now + timedelta(minutes=30),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def override_db():
    yield MagicMock()


def test_clients_returns_401_without_token() -> None:
    app.dependency_overrides[get_db] = override_db

    client = TestClient(app)

    try:
        response = client.get("/api/v1/clients")

        assert response.status_code == 401
        assert response.json() == {
            "detail": "Authentication required"
        }
    finally:
        app.dependency_overrides.clear()


def test_clients_returns_200_for_admin(monkeypatch) -> None:
    admin_user = build_user(
        utilisateur_id=1,
        email="admin@example.com",
        role="ADMIN",
    )

    monkeypatch.setattr(
        UtilisateurRepository,
        "get_by_id",
        lambda self, utilisateur_id: admin_user,
    )

    token = build_token(
        utilisateur_id=1,
        email="admin@example.com",
        role="ADMIN",
    )

    app.dependency_overrides[get_db] = override_db

    client = TestClient(app)

    try:
        response = client.get(
            "/api/v1/clients",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_clients_returns_403_for_client_role(monkeypatch) -> None:
    client_user = build_user(
        utilisateur_id=2,
        email="client@example.com",
        role="CLIENT",
        id_client=1,
    )

    monkeypatch.setattr(
        UtilisateurRepository,
        "get_by_id",
        lambda self, utilisateur_id: client_user,
    )

    token = build_token(
        utilisateur_id=2,
        email="client@example.com",
        role="CLIENT",
    )

    app.dependency_overrides[get_db] = override_db

    client = TestClient(app)

    try:
        response = client.get(
            "/api/v1/clients",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Insufficient permissions"
        }
    finally:
        app.dependency_overrides.clear()

def test_demande_mandat_link_returns_403_for_client_role(
    monkeypatch,
) -> None:
    client_user = build_user(
        utilisateur_id=2,
        email="client@example.com",
        role="CLIENT",
        id_client=4,
    )

    monkeypatch.setattr(
        UtilisateurRepository,
        "get_by_id",
        lambda self, utilisateur_id: client_user,
    )

    token = build_token(
        utilisateur_id=2,
        email="client@example.com",
        role="CLIENT",
    )

    app.dependency_overrides[get_db] = override_db

    client = TestClient(app)

    try:
        response = client.patch(
            "/api/v1/demandes/4/mandat",
            json={
                "id_mandat": 18,
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Insufficient permissions"
        }
    finally:
        app.dependency_overrides.clear()