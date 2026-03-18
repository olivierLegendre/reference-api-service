# Incident / Rollback / Recovery Runbook

## Scope

Service: `reference-api-service`
Critical path: reference/mapping CRUD APIs.

## Incident Response

1. Confirm impacted org/site and endpoint(s).
2. Capture request IDs and failing route examples.
3. Check API + DB connectivity before rollback.

## Rollback

1. Re-deploy last known good release artifact for `reference-api-service`.
2. Re-apply `scripts/init_postgres.sql` only if schema drift occurred.
3. Keep traffic read-only until validation passes.

## Recovery Validation

```bash
source .venv/bin/activate
python scripts/export_openapi.py
ruff check .
mypy src
pytest -m "not postgres_integration"
./scripts/run_postgres_integration_tests.sh
```

## Post-Incident

1. Record root cause and affected endpoints.
2. Add regression test for failing API behavior.
3. Update migration checklist if Node-RED parity gap was involved.
