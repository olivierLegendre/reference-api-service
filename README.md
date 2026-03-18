# reference-api-service

Wave 2 extraction service for canonical reference-domain APIs.

## Scope (Wave 2)

- `device references` lifecycle endpoints.
- `mappings` replace/list endpoints per reference.
- `links` upsert/list endpoints per reference.
- Path versioning via `/api/v1/...`.
- Legacy alias compatibility paths (`/api/v1/references/...`) during migration.
- Hexagonal structure with repository and Unit of Work boundaries.

## Architecture

```text
src/reference_api_service/
  domain/                  # entities + domain constraints
  application/             # use-cases + unit of work boundary
  adapters/
    inbound/http/          # FastAPI routers and schemas
    outbound/              # postgres and in-memory (tests only)
```

## Setup

```bash
PYTHON_BIN=python3.12 ./scripts/setup_dev.sh
source .venv/bin/activate
```

## Run

PostgreSQL backend (default):

```bash
export REFERENCE_API_POSTGRES_DSN='postgresql://postgres:postgres@localhost:5432/reference_api'
uvicorn reference_api_service.main:app --reload
```

In-memory backend is intended for tests/tooling only:

```bash
export REFERENCE_API_PERSISTENCE_BACKEND=in_memory
```

Schema SQL is tracked in `scripts/init_postgres.sql` and auto-applied by default.

## Test

Unit and contract checks:

```bash
python scripts/export_openapi.py
ruff check .
mypy src
pytest -m "not postgres_integration"
```

PostgreSQL integration tests:

```bash
./scripts/run_postgres_integration_tests.sh
```

Golden compatibility fixture regression:

- Fixture file: `tests/fixtures/poc_reference_golden.json`
- Coverage: canonical (`/api/v1/device-references/...`) and legacy alias (`/api/v1/references/...`) routes.

## Contract

The OpenAPI contract artifact is stored at `contracts/openapi-v1.json`.
Refresh it with:

```bash
python scripts/export_openapi.py
```

## Operations Runbook

- `docs/runbooks/incident-rollback-recovery.md`
