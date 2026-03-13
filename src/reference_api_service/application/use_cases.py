from collections.abc import Sequence
from datetime import UTC, datetime

from reference_api_service.application.uow import UnitOfWork
from reference_api_service.domain.entities import DeviceReference, Link, Mapping
from reference_api_service.domain.errors import NotFoundError


class ReferenceApiUseCases:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def upsert_reference(
        self,
        *,
        reference_id: str,
        organization_id: str,
        site_id: str,
        device_id: str,
        label: str,
        metadata: dict,
    ) -> DeviceReference:
        item = DeviceReference(
            reference_id=reference_id,
            organization_id=organization_id,
            site_id=site_id,
            device_id=device_id,
            label=label,
            metadata=metadata,
            updated_at=datetime.now(UTC),
        )
        with self._uow as uow:
            saved = uow.references.upsert(item)
            uow.commit()
            return saved

    def get_reference(
        self,
        *,
        organization_id: str,
        site_id: str,
        reference_id: str,
    ) -> DeviceReference:
        with self._uow as uow:
            item = uow.references.get(organization_id, site_id, reference_id)
            if item is None:
                raise NotFoundError("reference not found")
            return item

    def list_references(self, *, organization_id: str, site_id: str) -> Sequence[DeviceReference]:
        with self._uow as uow:
            return uow.references.list(organization_id, site_id)

    def replace_mappings(
        self,
        *,
        organization_id: str,
        site_id: str,
        reference_id: str,
        items: Sequence[Mapping],
    ) -> Sequence[Mapping]:
        self.get_reference(
            organization_id=organization_id,
            site_id=site_id,
            reference_id=reference_id,
        )
        with self._uow as uow:
            saved = uow.mappings.replace_for_reference(
                organization_id=organization_id,
                site_id=site_id,
                reference_id=reference_id,
                items=items,
            )
            uow.commit()
            return saved

    def list_mappings(
        self,
        *,
        organization_id: str,
        site_id: str,
        reference_id: str,
    ) -> Sequence[Mapping]:
        self.get_reference(
            organization_id=organization_id,
            site_id=site_id,
            reference_id=reference_id,
        )
        with self._uow as uow:
            return uow.mappings.list_for_reference(organization_id, site_id, reference_id)

    def upsert_link(
        self,
        *,
        organization_id: str,
        site_id: str,
        reference_id: str,
        link_id: str,
        point_id: str,
        relation: str,
    ) -> Link:
        self.get_reference(
            organization_id=organization_id,
            site_id=site_id,
            reference_id=reference_id,
        )
        item = Link(
            link_id=link_id,
            reference_id=reference_id,
            organization_id=organization_id,
            site_id=site_id,
            point_id=point_id,
            relation=relation,
        )
        with self._uow as uow:
            saved = uow.links.upsert(item)
            uow.commit()
            return saved

    def list_links(
        self,
        *,
        organization_id: str,
        site_id: str,
        reference_id: str,
    ) -> Sequence[Link]:
        self.get_reference(
            organization_id=organization_id,
            site_id=site_id,
            reference_id=reference_id,
        )
        with self._uow as uow:
            return uow.links.list_for_reference(organization_id, site_id, reference_id)
