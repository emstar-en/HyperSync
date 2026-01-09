-- Postgres DDL for HyperSync persistent memory (optional)
CREATE SCHEMA IF NOT EXISTS hypersync;
SET search_path TO hypersync, public;

CREATE TABLE IF NOT EXISTS mem_kv (
  actor TEXT NOT NULL,
  k TEXT NOT NULL,
  t TIMESTAMPTZ NOT NULL,
  ttl_ms BIGINT NOT NULL,
  type TEXT NOT NULL,
  mode TEXT NOT NULL,
  val TEXT,
  PRIMARY KEY (actor, k, t)
);

CREATE TABLE IF NOT EXISTS citations (
  id UUID PRIMARY KEY,
  address TEXT,
  source TEXT,
  quote TEXT,
  added_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS receipts (
  rid TEXT PRIMARY KEY,
  capsule_id TEXT,
  purpose TEXT,
  kept_records INT,
  time TIMESTAMPTZ,
  selectors_hash TEXT,
  policy_hash TEXT,
  enclave_measurement TEXT,
  bundle_hash TEXT
);

CREATE INDEX IF NOT EXISTS mem_kv_not_expired_idx ON mem_kv (actor, k, t) INCLUDE (ttl_ms);
