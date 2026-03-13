from collections.abc import Sequence
from pathlib import Path

from psycopg import connect
from psycopg.connection import Connection
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from reference_api_service.application.uow import UnitOfWork
from reference_api_service.domain.entities import DeviceReference, Link, Mapping


def _sql_path() -> Path:
    return Path(__file__).resolve().parents[4] / "scripts" / "init_postgres.sql"


def ensure_schema(dsn: str) -> None:
    sql = _sql_path().read_text(encoding="utf-8")
    with connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


class PostgresReferenceRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def upsert(self, item: DeviceReference) -> DeviceReference:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO device_references (
                    organization_id,
                    site_id,
                    reference_id,
                    device_id,
                    label,
                    metadata,
                    updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (organization_id, site_id, reference_id)
                DO UPDATE SET
                    device_id = EXCLUDED.device_id,
                    label = EXCLUDED.label,
                    metadata = EXCLUDED.metadata,
                    updated_at = EXCLUDED.updated_at
                """,
                (
                    item.organization_id,
                    item.site_id,
                    item.reference_id,
                    item.device_id,
                    item.label,
                    Jsonb(item.metadata),
                    item.updated_at,
                ),
            )
        return item

    def get(
        self,
        organization_id: str,
        site_id: str,
        reference_id: str,
    ) -> DeviceReference | None:
        with self._conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    organization_id,
                    site_id,
                    reference_id,
                    device_id,
                    label,
                    metadata,
                    updated_at
                FROM device_references
                WHERE organization_id = %s
                  AND site_id = %s
                  AND reference_id = %s
                """,
                (organization_id, site_id, reference_id),
            )
            row = cur.fetchone()
        if row is None:
            return None
        return DeviceReference(
            reference_id=row["reference_id"],
            organization_id=row["organization_id"],
            site_id=row["site_id"],
            device_id=row["device_id"],
            label=row["label"],
            metadata=row["metadata"] or {},
            updated_at=row["updated_at"],
        )

    def list(self, organization_id: str, site_id: str) -> Sequence[DeviceReference]:
        with self._conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    organization_id,
                    site_id,
                    reference_id,
                    device_id,
                    label,
                    metadata,
                    updated_at
                FROM device_references
                WHERE organization_id = %s
                  AND site_id = %s
                ORDER BY reference_id
                """,
                (organization_id, site_id),
            )
            rows = cur.fetchall()
        return [
            DeviceReference(
                reference_id=row["reference_id"],
                organization_id=row["organization_id"],
                site_id=row["site_id"],
                device_id=row["device_id"],
                label=row["label"],
                metadata=row["metadata"] or {},
                updated_at=row["updated_at"],
            )
            for row in rows
        ]


class PostgresMappingRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def replace_for_reference(
        self,
        organization_id: str,
        site_id: str,
        reference_id: str,
        items: Sequence[Mapping],
    ) -> Sequence[Mapping]:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM mappings
                WHERE organization_id = %s
                  AND site_id = %s
                  AND reference_id = %s
                """,
                (organization_id, site_id, reference_id),
            )
            if items:
                rows = [
                    (
                        organization_id,
                        site_id,
                        reference_id,
                        item.mapping_id,
                        item.source_key,
                        item.target_point_id,
                        item.transform,
                    )
                    for item in items
                ]
                cur.executemany(
                    """
                    INSERT INTO mappings (
                        organization_id,
                        site_id,
                        reference_id,
                        mapping_id,
                        source_key,
                        target_point_id,
                        transform
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    rows,
                )
        return list(items)

    def list_for_reference(
        self,
        organization_id: str,
        site_id: str,
        reference_id: str,
    ) -> Sequence[Mapping]:
        with self._conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    organization_id,
                    site_id,
                    reference_id,
                    mapping_id,
                    source_key,
                    target_point_id,
                    transform
                FROM mappings
                WHERE organization_id = %s
                  AND site_id = %s
                  AND reference_id = %s
                ORDER BY mapping_id
                """,
                (organization_id, site_id, reference_id),
            )
            rows = cur.fetchall()
        return [
            Mapping(
                mapping_id=row["mapping_id"],
                reference_id=row["reference_id"],
                organization_id=row["organization_id"],
                site_id=row["site_id"],
                source_key=row["source_key"],
                target_point_id=row["target_point_id"],
                transform=row["transform"],
            )
            for row in rows
        ]


class PostgresLinkRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def upsert(self, item: Link) -> Link:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO links (
                    organization_id,
                    site_id,
                    reference_id,
                    link_id,
                    point_id,
                    relation
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (organization_id, site_id, reference_id, link_id)
                DO UPDATE SET
                    point_id = EXCLUDED.point_id,
                    relation = EXCLUDED.relation
                """,
                (
                    item.organization_id,
                    item.site_id,
                    item.reference_id,
                    item.link_id,
                    item.point_id,
                    item.relation,
                ),
            )
        return item

    def list_for_reference(
        self,
        organization_id: str,
        site_id: str,
        reference_id: str,
    ) -> Sequence[Link]:
        with self._conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    organization_id,
                    site_id,
                    reference_id,
                    link_id,
                    point_id,
                    relation
                FROM links
                WHERE organization_id = %s
                  AND site_id = %s
                  AND reference_id = %s
                ORDER BY link_id
                """,
                (organization_id, site_id, reference_id),
            )
            rows = cur.fetchall()
        return [
            Link(
                link_id=row["link_id"],
                reference_id=row["reference_id"],
                organization_id=row["organization_id"],
                site_id=row["site_id"],
                point_id=row["point_id"],
                relation=row["relation"],
            )
            for row in rows
        ]



class PostgresUnitOfWork(UnitOfWork):
    def __init__(self, dsn: str, auto_init_schema: bool = True) -> None:
        self._dsn = dsn
        self._auto_init_schema = auto_init_schema
        self._schema_initialized = False
        self._conn: Connection | None = None

    def __enter__(self) -> "PostgresUnitOfWork":
        if self._auto_init_schema and not self._schema_initialized:
            ensure_schema(self._dsn)
            self._schema_initialized = True

        self._conn = connect(self._dsn)
        self.references = PostgresReferenceRepository(self._conn)
        self.mappings = PostgresMappingRepository(self._conn)
        self.links = PostgresLinkRepository(self._conn)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._conn is None:
            return
        if exc_type:
            self.rollback()
        self._conn.close()
        self._conn = None

    def commit(self) -> None:
        if self._conn is not None:
            self._conn.commit()

    def rollback(self) -> None:
        if self._conn is not None:
            self._conn.rollback()
