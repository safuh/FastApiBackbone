from fastapi.testclient import TestClient

from fastapi_backbone import create_app
from fastapi_backbone.core.config import Settings


def test_health_endpoints() -> None:
    settings = Settings(database_url="sqlite+aiosqlite:///./test.db")
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

        response = client.get("/api/health/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"
