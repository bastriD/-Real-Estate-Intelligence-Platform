from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_metrics_endpoint_exposes_custom_metrics() -> None:
    client.get("/health")

    response = client.get("/metrics")

    assert response.status_code == 200

    body = response.text

    assert "real_estate_api_requests_total" in body
    assert "real_estate_api_request_duration_seconds" in body
    assert "real_estate_api_errors_total" in body