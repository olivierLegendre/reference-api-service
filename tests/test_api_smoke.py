from fastapi.testclient import TestClient


def test_healthz(in_memory_client: TestClient) -> None:
    response = in_memory_client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "reference-api-service"
    assert body["persistence_backend"] == "in_memory"


def test_reference_mapping_link_flow(in_memory_client: TestClient) -> None:
    ref_payload = {
        "organization_id": "org-1",
        "site_id": "site-1",
        "device_id": "dev-42",
        "label": "HVAC Sensor",
        "metadata": {"vendor": "demo"},
    }

    upsert = in_memory_client.put("/api/v1/device-references/ref-1", json=ref_payload)
    assert upsert.status_code == 200

    get_ref = in_memory_client.get(
        "/api/v1/device-references/ref-1",
        params={"organization_id": "org-1", "site_id": "site-1"},
    )
    assert get_ref.status_code == 200
    assert get_ref.json()["device_id"] == "dev-42"

    replace_mappings = in_memory_client.put(
        "/api/v1/device-references/ref-1/mappings",
        json={
            "organization_id": "org-1",
            "site_id": "site-1",
            "items": [
                {
                    "mapping_id": "m-1",
                    "source_key": "temperature",
                    "target_point_id": "point-123",
                    "transform": "identity",
                }
            ],
        },
    )
    assert replace_mappings.status_code == 200
    assert replace_mappings.json()[0]["mapping_id"] == "m-1"

    upsert_link = in_memory_client.put(
        "/api/v1/device-references/ref-1/links/l-1",
        json={
            "organization_id": "org-1",
            "site_id": "site-1",
            "point_id": "point-abc",
            "relation": "observes",
        },
    )
    assert upsert_link.status_code == 200
    assert upsert_link.json()["link_id"] == "l-1"


def test_mapping_replace_rejects_empty_payload(in_memory_client: TestClient) -> None:
    create = in_memory_client.put(
        "/api/v1/device-references/ref-empty",
        json={
            "organization_id": "org-1",
            "site_id": "site-1",
            "device_id": "dev-empty",
            "label": "EmptyGuard",
            "metadata": {},
        },
    )
    assert create.status_code == 200

    replace = in_memory_client.put(
        "/api/v1/device-references/ref-empty/mappings",
        json={
            "organization_id": "org-1",
            "site_id": "site-1",
            "items": [],
        },
    )
    assert replace.status_code == 422


def test_cross_tenant_get_is_not_found(in_memory_client: TestClient) -> None:
    create = in_memory_client.put(
        "/api/v1/device-references/ref-tenant",
        json={
            "organization_id": "org-a",
            "site_id": "site-a",
            "device_id": "dev-a",
            "label": "TenantA",
            "metadata": {},
        },
    )
    assert create.status_code == 200

    read_other_tenant = in_memory_client.get(
        "/api/v1/device-references/ref-tenant",
        params={"organization_id": "org-b", "site_id": "site-b"},
    )
    assert read_other_tenant.status_code == 404
