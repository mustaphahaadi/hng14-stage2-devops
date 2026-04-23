from pathlib import Path
import sys
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))
import main  # noqa: E402


def test_create_job_pushes_to_queue_and_sets_status(monkeypatch):
    mocked_redis = MagicMock()
    monkeypatch.setattr(main, "r", mocked_redis)
    monkeypatch.setattr(main, "QUEUE_NAME", "job")

    client = TestClient(main.app)
    response = client.post("/jobs")

    assert response.status_code == 200
    payload = response.json()
    assert "job_id" in payload

    mocked_redis.lpush.assert_called_once_with("job", payload["job_id"])
    mocked_redis.hset.assert_called_once_with(f"job:{payload['job_id']}", "status", "queued")


def test_get_job_returns_not_found_when_status_missing(monkeypatch):
    mocked_redis = MagicMock()
    mocked_redis.hget.return_value = None
    monkeypatch.setattr(main, "r", mocked_redis)

    client = TestClient(main.app)
    response = client.get("/jobs/missing")

    assert response.status_code == 200
    assert response.json() == {"error": "not found"}


def test_get_job_returns_status_when_found(monkeypatch):
    mocked_redis = MagicMock()
    mocked_redis.hget.return_value = "completed"
    monkeypatch.setattr(main, "r", mocked_redis)

    client = TestClient(main.app)
    response = client.get("/jobs/abc123")

    assert response.status_code == 200
    assert response.json() == {"job_id": "abc123", "status": "completed"}


def test_healthz_returns_ok_when_redis_ping_works(monkeypatch):
    mocked_redis = MagicMock()
    monkeypatch.setattr(main, "r", mocked_redis)

    client = TestClient(main.app)
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
