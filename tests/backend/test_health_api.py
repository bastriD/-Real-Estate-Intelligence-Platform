from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ready_endpoint() -> None:
    mock_connection = MagicMock()

    mock_context_manager = MagicMock()
    mock_context_manager.__enter__.return_value = mock_connection
    mock_context_manager.__exit__.return_value = None

    with patch(
        "src.api.api.v1.endpoints.health.engine.connect",
        return_value=mock_context_manager,
    ):
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "available",
    }

    mock_connection.execute.assert_called_once()