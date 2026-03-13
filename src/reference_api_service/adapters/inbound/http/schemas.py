from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReferenceUpsertRequest(BaseModel):
    organization_id: str = Field(min_length=1)
    site_id: str = Field(min_length=1)
    device_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReferenceResponse(BaseModel):
    reference_id: str
    organization_id: str
    site_id: str
    device_id: str
    label: str
    metadata: dict[str, Any]
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MappingItemRequest(BaseModel):
    mapping_id: str = Field(min_length=1)
    source_key: str = Field(min_length=1)
    target_point_id: str = Field(min_length=1)
    transform: str = Field(default="identity", min_length=1)


class MappingReplaceRequest(BaseModel):
    organization_id: str = Field(min_length=1)
    site_id: str = Field(min_length=1)
    items: list[MappingItemRequest] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_mapping_ids(self) -> "MappingReplaceRequest":
        ids = [item.mapping_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("mapping_id values must be unique within a replace request")
        return self


class MappingResponse(BaseModel):
    mapping_id: str
    reference_id: str
    organization_id: str
    site_id: str
    source_key: str
    target_point_id: str
    transform: str

    model_config = ConfigDict(from_attributes=True)


class LinkUpsertRequest(BaseModel):
    organization_id: str = Field(min_length=1)
    site_id: str = Field(min_length=1)
    point_id: str = Field(min_length=1)
    relation: str = Field(default="observes", min_length=1)


class LinkResponse(BaseModel):
    link_id: str
    reference_id: str
    organization_id: str
    site_id: str
    point_id: str
    relation: str

    model_config = ConfigDict(from_attributes=True)
