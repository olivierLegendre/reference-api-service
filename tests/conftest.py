import pytest
from fastapi.testclient import TestClient

from reference_api_service.main import create_app


@pytest.fixture
def in_memory_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("REFERENCE_API_PERSISTENCE_BACKEND", "in_memory")
    monkeypatch.setenv("REFERENCE_API_POSTGRES_AUTO_INIT", "false")

    app = create_app()
    with TestClient(app) as client:
        yield client
