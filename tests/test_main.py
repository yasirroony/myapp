from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_root_returns_greeting(monkeypatch):
    monkeypatch.setenv("GREETING", "hi")
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "hi"


def test_healthz():
    assert client.get("/healthz").json() == {"status": "alive"}


def test_readyz():
    assert client.get("/readyz").status_code == 200


def test_metrics_endpoint():
    client.get("/")
    response = client.get("/metrics/")
    assert response.status_code == 200
    assert "myapp_requests_total" in response.text
