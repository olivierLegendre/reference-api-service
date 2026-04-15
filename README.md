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
export REFERENCE_API_POSTGRES_DSN='postgresql://svc_reference_api_app:dev_reference_api_app@localhost:55440/reference_api'
uvicorn reference_api_service.main:app --reload
```

In-memory backend is intended for tests/tooling only:

```bash
export REFERENCE_API_PERSISTENCE_BACKEND=in_memory
```

Schema migration is handled with Alembic (`alembic/` + `scripts/migrate_postgres.sh`).
`scripts/init_postgres.sql` remains as a bootstrap fallback, but production path should use Alembic upgrades.

Apply migrations (migrator role):

```bash
export REFERENCE_API_MIGRATOR_DSN='postgresql://svc_reference_api_migrator:dev_reference_api_migrator@localhost:55440/reference_api'
./scripts/migrate_postgres.sh upgrade head
```

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

Shared Postgres dependency:

- The integration script uses `platform-foundation` shared cluster provisioning (no local per-service Postgres container).
- Optional env override: `POSTGRES_SHARED_ENV_FILE=/path/to/postgres-shared.env`.
- Integration flow now applies Alembic migrations with the migrator role, then runs tests with the app role DSN.

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
