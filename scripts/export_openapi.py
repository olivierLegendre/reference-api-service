import json
import os
from pathlib import Path


def _configure_env_for_contract_export() -> None:
    # OpenAPI export should not require a running PostgreSQL instance.
    os.environ.setdefault("REFERENCE_API_PERSISTENCE_BACKEND", "in_memory")
    os.environ.setdefault("REFERENCE_API_POSTGRES_AUTO_INIT", "false")


def main() -> None:
    _configure_env_for_contract_export()

    from reference_api_service.main import create_app

    app = create_app()
    schema = app.openapi()
    output = Path(__file__).resolve().parent.parent / "contracts" / "openapi-v1.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
