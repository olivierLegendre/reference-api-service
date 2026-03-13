import os

import pytest
from fastapi.testclient import TestClient

from reference_api_service.main import create_app


@pytest.mark.postgres_integration
def test_postgres_backend_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    dsn = os.getenv("REFERENCE_API_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("REFERENCE_API_TEST_POSTGRES_DSN is not set")

    monkeypatch.setenv("REFERENCE_API_PERSISTENCE_BACKEND", "postgres")
    monkeypatch.setenv("REFERENCE_API_POSTGRES_DSN", dsn)
    monkeypatch.setenv("REFERENCE_API_POSTGRES_AUTO_INIT", "true")

    client = TestClient(create_app())

    create = client.put(
        "/api/v1/device-references/ref-pg-1",
        json={
            "organization_id": "org-pg",
            "site_id": "site-pg",
            "device_id": "dev-pg",
            "label": "PG Device",
            "metadata": {"driver": "postgres"},
        },
    )
    assert create.status_code == 200

    read = client.get(
        "/api/v1/device-references/ref-pg-1",
        params={"organization_id": "org-pg", "site_id": "site-pg"},
    )
    assert read.status_code == 200
    assert read.json()["metadata"]["driver"] == "postgres"

    replace = client.put(
        "/api/v1/device-references/ref-pg-1/mappings",
        json={
            "organization_id": "org-pg",
            "site_id": "site-pg",
            "items": [
                {
                    "mapping_id": "m-pg-1",
                    "source_key": "temperature",
                    "target_point_id": "point-pg-1",
                    "transform": "identity",
                }
            ],
        },
    )
    assert replace.status_code == 200
    assert replace.json()[0]["mapping_id"] == "m-pg-1"

    duplicate_mapping_id = client.put(
        "/api/v1/device-references/ref-pg-1/mappings",
        json={
            "organization_id": "org-pg",
            "site_id": "site-pg",
            "items": [
                {
                    "mapping_id": "m-pg-dup",
                    "source_key": "temperature",
                    "target_point_id": "point-a",
                    "transform": "identity",
                },
                {
                    "mapping_id": "m-pg-dup",
                    "source_key": "humidity",
                    "target_point_id": "point-b",
                    "transform": "identity",
                },
            ],
        },
    )
    assert duplicate_mapping_id.status_code == 422
