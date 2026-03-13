from collections.abc import Sequence
from typing import Protocol

from reference_api_service.domain.entities import DeviceReference, Link, Mapping


class DeviceReferenceRepository(Protocol):
    def upsert(self, item: DeviceReference) -> DeviceReference: ...

    def get(
        self,
        organization_id: str,
        site_id: str,
        reference_id: str,
    ) -> DeviceReference | None: ...

    def list(self, organization_id: str, site_id: str) -> Sequence[DeviceReference]: ...


class MappingRepository(Protocol):
    def replace_for_reference(
        self,
        organization_id: str,
        site_id: str,
        reference_id: str,
        items: Sequence[Mapping],
    ) -> Sequence[Mapping]: ...

    def list_for_reference(
        self,
        organization_id: str,
        site_id: str,
        reference_id: str,
    ) -> Sequence[Mapping]: ...


class LinkRepository(Protocol):
    def upsert(self, item: Link) -> Link: ...

    def list_for_reference(
        self,
        organization_id: str,
        site_id: str,
        reference_id: str,
    ) -> Sequence[Link]: ...
