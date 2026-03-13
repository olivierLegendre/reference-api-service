from typing import Protocol

from reference_api_service.domain.repositories import (
    DeviceReferenceRepository,
    LinkRepository,
    MappingRepository,
)


class UnitOfWork(Protocol):
    references: DeviceReferenceRepository
    mappings: MappingRepository
    links: LinkRepository

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, exc_type, exc, tb) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
