from fastapi import APIRouter, HTTPException, Query

from reference_api_service.application.use_cases import ReferenceApiUseCases
from reference_api_service.domain.entities import Mapping
from reference_api_service.domain.errors import NotFoundError
from reference_api_service.settings import Settings

from .schemas import (
    LinkResponse,
    LinkUpsertRequest,
    MappingReplaceRequest,
    MappingResponse,
    ReferenceResponse,
    ReferenceUpsertRequest,
)


def create_router(use_cases: ReferenceApiUseCases, settings: Settings) -> APIRouter:
    router = APIRouter()

    @router.get("/healthz")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": settings.app_name,
            "env": settings.app_env,
            "persistence_backend": settings.persistence_backend,
        }

    @router.put(
        "/api/v1/device-references/{reference_id}",
        response_model=ReferenceResponse,
    )
    @router.put(
        "/api/v1/references/{reference_id}",
        response_model=ReferenceResponse,
        include_in_schema=False,
    )
    def upsert_reference(reference_id: str, body: ReferenceUpsertRequest) -> ReferenceResponse:
        item = use_cases.upsert_reference(
            reference_id=reference_id,
            organization_id=body.organization_id,
            site_id=body.site_id,
            device_id=body.device_id,
            label=body.label,
            metadata=body.metadata,
        )
        return ReferenceResponse.model_validate(item)

    @router.get(
        "/api/v1/device-references/{reference_id}",
        response_model=ReferenceResponse,
    )
    @router.get(
        "/api/v1/references/{reference_id}",
        response_model=ReferenceResponse,
        include_in_schema=False,
    )
    def get_reference(
        reference_id: str,
        organization_id: str = Query(min_length=1),
        site_id: str = Query(min_length=1),
    ) -> ReferenceResponse:
        try:
            item = use_cases.get_reference(
                reference_id=reference_id,
                organization_id=organization_id,
                site_id=site_id,
            )
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return ReferenceResponse.model_validate(item)

    @router.get(
        "/api/v1/device-references",
        response_model=list[ReferenceResponse],
    )
    @router.get(
        "/api/v1/references",
        response_model=list[ReferenceResponse],
        include_in_schema=False,
    )
    def list_references(
        organization_id: str = Query(min_length=1),
        site_id: str = Query(min_length=1),
    ) -> list[ReferenceResponse]:
        rows = use_cases.list_references(organization_id=organization_id, site_id=site_id)
        return [ReferenceResponse.model_validate(row) for row in rows]

    @router.put(
        "/api/v1/device-references/{reference_id}/mappings",
        response_model=list[MappingResponse],
    )
    @router.put(
        "/api/v1/references/{reference_id}/mappings",
        response_model=list[MappingResponse],
        include_in_schema=False,
    )
    def replace_mappings(
        reference_id: str,
        body: MappingReplaceRequest,
    ) -> list[MappingResponse]:
        domain_rows = [
            Mapping(
                mapping_id=item.mapping_id,
                reference_id=reference_id,
                organization_id=body.organization_id,
                site_id=body.site_id,
                source_key=item.source_key,
                target_point_id=item.target_point_id,
                transform=item.transform,
            )
            for item in body.items
        ]
        try:
            rows = use_cases.replace_mappings(
                reference_id=reference_id,
                organization_id=body.organization_id,
                site_id=body.site_id,
                items=domain_rows,
            )
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return [MappingResponse.model_validate(row) for row in rows]

    @router.get(
        "/api/v1/device-references/{reference_id}/mappings",
        response_model=list[MappingResponse],
    )
    @router.get(
        "/api/v1/references/{reference_id}/mappings",
        response_model=list[MappingResponse],
        include_in_schema=False,
    )
    def list_mappings(
        reference_id: str,
        organization_id: str = Query(min_length=1),
        site_id: str = Query(min_length=1),
    ) -> list[MappingResponse]:
        try:
            rows = use_cases.list_mappings(
                reference_id=reference_id,
                organization_id=organization_id,
                site_id=site_id,
            )
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return [MappingResponse.model_validate(row) for row in rows]

    @router.put(
        "/api/v1/device-references/{reference_id}/links/{link_id}",
        response_model=LinkResponse,
    )
    @router.put(
        "/api/v1/references/{reference_id}/links/{link_id}",
        response_model=LinkResponse,
        include_in_schema=False,
    )
    def upsert_link(
        reference_id: str,
        link_id: str,
        body: LinkUpsertRequest,
    ) -> LinkResponse:
        try:
            item = use_cases.upsert_link(
                reference_id=reference_id,
                link_id=link_id,
                organization_id=body.organization_id,
                site_id=body.site_id,
                point_id=body.point_id,
                relation=body.relation,
            )
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return LinkResponse.model_validate(item)

    @router.get(
        "/api/v1/device-references/{reference_id}/links",
        response_model=list[LinkResponse],
    )
    @router.get(
        "/api/v1/references/{reference_id}/links",
        response_model=list[LinkResponse],
        include_in_schema=False,
    )
    def list_links(
        reference_id: str,
        organization_id: str = Query(min_length=1),
        site_id: str = Query(min_length=1),
    ) -> list[LinkResponse]:
        try:
            rows = use_cases.list_links(
                reference_id=reference_id,
                organization_id=organization_id,
                site_id=site_id,
            )
        except NotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return [LinkResponse.model_validate(row) for row in rows]

    return router
