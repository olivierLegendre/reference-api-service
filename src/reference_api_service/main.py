from fastapi import FastAPI

from reference_api_service.adapters.inbound.http.router import create_router
from reference_api_service.adapters.outbound.in_memory import InMemoryUnitOfWork
from reference_api_service.adapters.outbound.postgres import PostgresUnitOfWork
from reference_api_service.application.uow import UnitOfWork
from reference_api_service.application.use_cases import ReferenceApiUseCases
from reference_api_service.settings import Settings


def create_app() -> FastAPI:
    settings = Settings()
    uow: UnitOfWork
    if settings.persistence_backend == "postgres":
        uow = PostgresUnitOfWork(
            settings.postgres_dsn,
            auto_init_schema=settings.postgres_auto_init,
        )
    else:
        uow = InMemoryUnitOfWork()

    use_cases = ReferenceApiUseCases(uow)

    app = FastAPI(
        title="Reference API Service",
        version="1.0.0",
        description=(
            "Wave 2 baseline for device references, mappings, and links. "
            "Path versioned endpoints under /api/v1."
        ),
    )
    app.include_router(create_router(use_cases, settings))
    return app


app = create_app()
