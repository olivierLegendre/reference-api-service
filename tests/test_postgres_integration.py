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
    monkeypatch.setenv("REFERENCE_API_POSTGRES_AUTO_INIT", "false")

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


@pytest.mark.postgres_integration
def test_postgres_tenant_scope_isolation(monkeypatch: pytest.MonkeyPatch) -> None:
    dsn = os.getenv("REFERENCE_API_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("REFERENCE_API_TEST_POSTGRES_DSN is not set")

    monkeypatch.setenv("REFERENCE_API_PERSISTENCE_BACKEND", "postgres")
    monkeypatch.setenv("REFERENCE_API_POSTGRES_DSN", dsn)
    monkeypatch.setenv("REFERENCE_API_POSTGRES_AUTO_INIT", "false")

    client = TestClient(create_app())

    # Same reference_id is allowed across tenant boundaries.
    primary = client.put(
        "/api/v1/device-references/ref-tenant-1",
        json={
            "organization_id": "org-a",
            "site_id": "site-a",
            "device_id": "dev-a",
            "label": "Device A",
            "metadata": {"tenant": "a"},
        },
    )
    assert primary.status_code == 200

    secondary = client.put(
        "/api/v1/device-references/ref-tenant-1",
        json={
            "organization_id": "org-b",
            "site_id": "site-b",
            "device_id": "dev-b",
            "label": "Device B",
            "metadata": {"tenant": "b"},
        },
    )
    assert secondary.status_code == 200

    wrong_org = client.get(
        "/api/v1/device-references/ref-tenant-1",
        params={"organization_id": "org-x", "site_id": "site-a"},
    )
    assert wrong_org.status_code == 404

    wrong_site = client.get(
        "/api/v1/device-references/ref-tenant-1",
        params={"organization_id": "org-a", "site_id": "site-x"},
    )
    assert wrong_site.status_code == 404

    list_a = client.get(
        "/api/v1/device-references",
        params={"organization_id": "org-a", "site_id": "site-a"},
    )
    assert list_a.status_code == 200
    assert [row["device_id"] for row in list_a.json()] == ["dev-a"]

    list_b = client.get(
        "/api/v1/device-references",
        params={"organization_id": "org-b", "site_id": "site-b"},
    )
    assert list_b.status_code == 200
    assert [row["device_id"] for row in list_b.json()] == ["dev-b"]
