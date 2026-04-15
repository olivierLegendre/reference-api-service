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
2. Re-apply schema state with Alembic migrations (`./scripts/migrate_postgres.sh upgrade head`) if schema drift occurred.
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

## Wave 8 Hardening And Namespace Migration Notes

1. If release is blocked by vulnerability gate, capture the exact HIGH/CRITICAL finding list and either:
- patch and rebuild immediately; or
- apply documented risk acceptance exception before re-run.
2. If keyless OIDC signing/verification fails, treat this as release-blocking identity drift.
3. If namespace migration issues occur (`ghcr.io/ramery/...`), rollback by pinning the last known good immutable tag in deployment manifest and rerun pullability checks.
4. Always attach evidence artifacts (scan output, signature verify output, pullability check result) to incident record.
