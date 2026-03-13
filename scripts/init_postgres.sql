CREATE TABLE IF NOT EXISTS device_references (
  organization_id TEXT NOT NULL,
  site_id TEXT NOT NULL,
  reference_id TEXT NOT NULL,
  device_id TEXT NOT NULL,
  label TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (organization_id, site_id, reference_id)
);

CREATE TABLE IF NOT EXISTS mappings (
  organization_id TEXT NOT NULL,
  site_id TEXT NOT NULL,
  reference_id TEXT NOT NULL,
  mapping_id TEXT NOT NULL,
  source_key TEXT NOT NULL,
  target_point_id TEXT NOT NULL,
  transform TEXT NOT NULL,
  PRIMARY KEY (organization_id, site_id, reference_id, mapping_id),
  FOREIGN KEY (organization_id, site_id, reference_id)
    REFERENCES device_references (organization_id, site_id, reference_id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS links (
  organization_id TEXT NOT NULL,
  site_id TEXT NOT NULL,
  reference_id TEXT NOT NULL,
  link_id TEXT NOT NULL,
  point_id TEXT NOT NULL,
  relation TEXT NOT NULL,
  PRIMARY KEY (organization_id, site_id, reference_id, link_id),
  FOREIGN KEY (organization_id, site_id, reference_id)
    REFERENCES device_references (organization_id, site_id, reference_id)
    ON DELETE CASCADE
);
