from collections import defaultdict
from collections.abc import Sequence

from reference_api_service.application.uow import UnitOfWork
from reference_api_service.domain.entities import DeviceReference, Link, Mapping


class InMemoryReferenceRepository:
    def __init__(self) -> None:
        self._store: dict[tuple[str, str, str], DeviceReference] = {}

    def upsert(self, item: DeviceReference) -> DeviceReference:
        self._store[(item.organization_id, item.site_id, item.reference_id)] = item
        return item

    def get(self, organization_id: str, site_id: str, reference_id: str) -> DeviceReference | None:
        return self._store.get((organization_id, site_id, reference_id))

    def list(self, organization_id: str, site_id: str) -> Sequence[DeviceReference]:
        return [
            value
            for key, value in self._store.items()
            if key[0] == organization_id and key[1] == site_id
        ]


class InMemoryMappingRepository:
    def __init__(self) -> None:
        self._store: dict[tuple[str, str, str], list[Mapping]] = defaultdict(list)

    def replace_for_reference(
        self,
        organization_id: str,
        site_id: str,
        reference_id: str,
        items: Sequence[Mapping],
    ) -> Sequence[Mapping]:
        key = (organization_id, site_id, reference_id)
        self._store[key] = list(items)
        return self._store[key]

    def list_for_reference(
        self,
        organization_id: str,
        site_id: str,
        reference_id: str,
    ) -> Sequence[Mapping]:
        return self._store.get((organization_id, site_id, reference_id), [])


class InMemoryLinkRepository:
    def __init__(self) -> None:
        self._store: dict[tuple[str, str, str], dict[str, Link]] = defaultdict(dict)

    def upsert(self, item: Link) -> Link:
        bucket = self._store[(item.organization_id, item.site_id, item.reference_id)]
        bucket[item.link_id] = item
        return item

    def list_for_reference(
        self,
        organization_id: str,
        site_id: str,
        reference_id: str,
    ) -> Sequence[Link]:
        bucket = self._store.get((organization_id, site_id, reference_id), {})
        return list(bucket.values())


class InMemoryUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.references = InMemoryReferenceRepository()
        self.mappings = InMemoryMappingRepository()
        self.links = InMemoryLinkRepository()

    def __enter__(self) -> "InMemoryUnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type:
            self.rollback()

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None
