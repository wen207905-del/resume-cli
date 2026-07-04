"""Web API tests."""

from fastapi.testclient import TestClient

from resume_cli.web_app import create_app


def test_health() -> None:
    client = TestClient(create_app(mock=True))
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_index() -> None:
    client = TestClient(create_app(mock=True))
    res = client.get("/")
    assert res.status_code == 200
    assert "Resume CLI" in res.text
