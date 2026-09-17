from fastapi.testclient import TestClient

from app.main import create_app


def test_api_creates_ticket_and_returns_analytics(tmp_path) -> None:
    app = create_app(str(tmp_path / "api-support-tickets.db"))
    with TestClient(app) as client:
        created = client.post(
            "/tickets",
            json={
                "title": "Production API has a server error",
                "description": "Users receive a 500 error when submitting checkout requests.",
                "requester_email": "ops@example.com",
            },
        )
        assert created.status_code == 201
        ticket = created.json()
        assert ticket["category"] == "application_incident"

        invalid_transition = client.patch(
            f"/tickets/{ticket['id']}/status", json={"status": "resolved"}
        )
        assert invalid_transition.status_code == 409

        overview = client.get("/analytics/overview")
        assert overview.status_code == 200
        assert overview.json()["open"] == 1
