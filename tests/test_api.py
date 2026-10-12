import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Bulk Certificate Generator API is running"


def test_create_certificate_job():
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "issuer": "Tech Academy",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "testuser@example.com"
                }
            ],
        },
    )

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["total_count"] == 1


def test_create_job_without_recipients():
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "issuer": "Tech Academy",
            "recipients": [],
        },
    )

    assert response.status_code == 422
