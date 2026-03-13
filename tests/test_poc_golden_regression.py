import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def _load_fixture() -> dict:
    path = Path(__file__).resolve().parent / "fixtures" / "poc_reference_golden.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("base_path", ["/api/v1/device-references", "/api/v1/references"])
def test_reference_flow_matches_golden_fixture(
    in_memory_client: TestClient,
    base_path: str,
) -> None:
    fixture = _load_fixture()

    request_common = {
        "organization_id": fixture["organization_id"],
        "site_id": fixture["site_id"],
    }

    upsert_payload = {
        **request_common,
        **fixture["reference_upsert"],
    }

    upsert = in_memory_client.put(
        f"{base_path}/{fixture['reference_id']}",
        json=upsert_payload,
    )
    assert upsert.status_code == 200
    upsert_json = upsert.json()
    assert upsert_json["reference_id"] == fixture["reference_id"]
    assert upsert_json["organization_id"] == fixture["organization_id"]
    assert upsert_json["site_id"] == fixture["site_id"]
    assert upsert_json["device_id"] == fixture["reference_upsert"]["device_id"]
    assert upsert_json["label"] == fixture["reference_upsert"]["label"]
    assert upsert_json["metadata"] == fixture["reference_upsert"]["metadata"]
    assert "updated_at" in upsert_json

    get_ref = in_memory_client.get(
        f"{base_path}/{fixture['reference_id']}",
        params=request_common,
    )
    assert get_ref.status_code == 200
    assert get_ref.json()["device_id"] == fixture["reference_upsert"]["device_id"]

    initial_replace = in_memory_client.put(
        f"{base_path}/{fixture['reference_id']}/mappings",
        json={
            **request_common,
            "items": fixture["mappings_initial"],
        },
    )
    assert initial_replace.status_code == 200
    assert len(initial_replace.json()) == 2

    replacement = in_memory_client.put(
        f"{base_path}/{fixture['reference_id']}/mappings",
        json={
            **request_common,
            "items": fixture["mappings_replacement"],
        },
    )
    assert replacement.status_code == 200
    replacement_json = replacement.json()
    assert len(replacement_json) == 1
    assert replacement_json[0]["mapping_id"] == fixture["mappings_replacement"][0]["mapping_id"]
    assert (
        replacement_json[0]["target_point_id"]
        == fixture["mappings_replacement"][0]["target_point_id"]
    )

    list_mappings = in_memory_client.get(
        f"{base_path}/{fixture['reference_id']}/mappings",
        params=request_common,
    )
    assert list_mappings.status_code == 200
    listed = list_mappings.json()
    assert len(listed) == 1
    assert listed[0]["mapping_id"] == fixture["mappings_replacement"][0]["mapping_id"]

    link_create = in_memory_client.put(
        f"{base_path}/{fixture['reference_id']}/links/{fixture['link_upsert']['link_id']}",
        json={
            **request_common,
            "point_id": fixture["link_upsert"]["point_id"],
            "relation": fixture["link_upsert"]["relation"],
        },
    )
    assert link_create.status_code == 200

    links = in_memory_client.get(
        f"{base_path}/{fixture['reference_id']}/links",
        params=request_common,
    )
    assert links.status_code == 200
    links_json = links.json()
    assert len(links_json) == 1
    assert links_json[0]["link_id"] == fixture["link_upsert"]["link_id"]
