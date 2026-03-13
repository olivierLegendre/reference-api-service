from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class DeviceReference:
    reference_id: str
    organization_id: str
    site_id: str
    device_id: str
    label: str
    metadata: dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class Mapping:
    mapping_id: str
    reference_id: str
    organization_id: str
    site_id: str
    source_key: str
    target_point_id: str
    transform: str = "identity"


@dataclass(slots=True)
class Link:
    link_id: str
    reference_id: str
    organization_id: str
    site_id: str
    point_id: str
    relation: str = "observes"
