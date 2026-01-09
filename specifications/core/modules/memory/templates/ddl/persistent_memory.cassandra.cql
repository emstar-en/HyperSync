// Cassandra/Scylla DDL for HyperSync persistent memory (optional)
CREATE KEYSPACE IF NOT EXISTS hypersync WITH replication = {'class':'SimpleStrategy','replication_factor':3};
USE hypersync;

CREATE TABLE IF NOT EXISTS mem_kv (
  actor text,
  k text,
  t timestamp,
  ttl_ms bigint,
  type text,
  mode text,
  val text,
  PRIMARY KEY ((actor), k, t)
) WITH CLUSTERING ORDER BY (k ASC, t DESC);

CREATE TABLE IF NOT EXISTS citations (
  id uuid PRIMARY KEY,
  address text,
  source text,
  quote text,
  added_at timestamp
);

CREATE TABLE IF NOT EXISTS receipts (
  rid text PRIMARY KEY,
  capsule_id text,
  purpose text,
  kept_records int,
  time timestamp,
  selectors_hash text,
  policy_hash text,
  enclave_measurement text,
  bundle_hash text
);

// Suggested table options
ALTER TABLE mem_kv WITH gc_grace_seconds = 86400; // 1 day
