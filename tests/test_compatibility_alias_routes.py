from fastapi.testclient import TestClient


def test_legacy_alias_reference_routes_are_compatible(in_memory_client: TestClient) -> None:
    payload = {
        "organization_id": "org-legacy",
        "site_id": "site-legacy",
        "device_id": "dev-legacy",
        "label": "Legacy Device",
        "metadata": {"origin": "poc"},
    }

    put_legacy = in_memory_client.put("/api/v1/references/ref-legacy", json=payload)
    assert put_legacy.status_code == 200

    get_legacy = in_memory_client.get(
        "/api/v1/references/ref-legacy",
        params={"organization_id": "org-legacy", "site_id": "site-legacy"},
    )
    assert get_legacy.status_code == 200
    assert get_legacy.json()["reference_id"] == "ref-legacy"

    get_canonical = in_memory_client.get(
        "/api/v1/device-references/ref-legacy",
        params={"organization_id": "org-legacy", "site_id": "site-legacy"},
    )
    assert get_canonical.status_code == 200
    assert get_canonical.json()["device_id"] == "dev-legacy"


def test_legacy_alias_mapping_and_link_routes_are_compatible(in_memory_client: TestClient) -> None:
    ref_payload = {
        "organization_id": "org-legacy",
        "site_id": "site-legacy",
        "device_id": "dev-legacy-2",
        "label": "Legacy Device 2",
        "metadata": {},
    }
    create = in_memory_client.put("/api/v1/references/ref-legacy-2", json=ref_payload)
    assert create.status_code == 200

    replace_legacy = in_memory_client.put(
        "/api/v1/references/ref-legacy-2/mappings",
        json={
            "organization_id": "org-legacy",
            "site_id": "site-legacy",
            "items": [
                {
                    "mapping_id": "m-legacy",
                    "source_key": "humidity",
                    "target_point_id": "point-legacy",
                    "transform": "identity",
                }
            ],
        },
    )
    assert replace_legacy.status_code == 200

    upsert_link_legacy = in_memory_client.put(
        "/api/v1/references/ref-legacy-2/links/l-legacy",
        json={
            "organization_id": "org-legacy",
            "site_id": "site-legacy",
            "point_id": "point-legacy",
            "relation": "observes",
        },
    )
    assert upsert_link_legacy.status_code == 200

    list_links_canonical = in_memory_client.get(
        "/api/v1/device-references/ref-legacy-2/links",
        params={"organization_id": "org-legacy", "site_id": "site-legacy"},
    )
    assert list_links_canonical.status_code == 200
    assert list_links_canonical.json()[0]["link_id"] == "l-legacy"
