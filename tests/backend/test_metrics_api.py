from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_metrics_endpoint_exposes_custom_metrics() -> None:
    client.get("/health")

    response = client.get("/metrics")

    assert response.status_code == 200

    body = response.text

    # Generic FastAPI HTTP metrics
    assert "real_estate_api_requests_total" in body
    assert "real_estate_api_request_duration_seconds" in body
    assert "real_estate_api_errors_total" in body

    # Recommendation / matching business metrics
    assert "real_estate_recommendation_requests_total" in body
    assert "real_estate_recommendation_failures_total" in body
    assert "real_estate_recommendation_duration_seconds" in body
    assert "real_estate_recommendation_eligible_candidates" in body
    assert "real_estate_recommendation_selected_candidates" in body
    assert "real_estate_recommendation_presentations_created" in body
    assert "real_estate_recommendation_presentations_existing" in body