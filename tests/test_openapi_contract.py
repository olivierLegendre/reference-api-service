import json
from pathlib import Path

import pytest

from reference_api_service.main import create_app

EXPECTED_PATHS = {
    "/healthz",
    "/api/v1/device-references",
    "/api/v1/device-references/{reference_id}",
    "/api/v1/device-references/{reference_id}/mappings",
    "/api/v1/device-references/{reference_id}/links",
    "/api/v1/device-references/{reference_id}/links/{link_id}",
}


def test_openapi_contains_expected_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REFERENCE_API_PERSISTENCE_BACKEND", "in_memory")
    app = create_app()
    schema = app.openapi()
    assert EXPECTED_PATHS.issubset(schema["paths"].keys())


def test_openapi_contract_file_exists_and_is_consistent(monkeypatch: pytest.MonkeyPatch) -> None:
    contract_path = Path(__file__).resolve().parent.parent / "contracts" / "openapi-v1.json"
    assert contract_path.exists(), "Run scripts/export_openapi.py to create the contract file"

    monkeypatch.setenv("REFERENCE_API_PERSISTENCE_BACKEND", "in_memory")
    app = create_app()
    current = app.openapi()
    baseline = json.loads(contract_path.read_text(encoding="utf-8"))

    assert set(current["paths"].keys()) == set(baseline["paths"].keys())
