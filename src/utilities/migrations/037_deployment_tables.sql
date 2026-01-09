-- Patch 037: Deployment tables

CREATE TABLE IF NOT EXISTS deployment_nodes (
    node_id TEXT PRIMARY KEY,
    service_name TEXT NOT NULL,
    position_coords TEXT NOT NULL,
    position_model TEXT NOT NULL,
    tier INTEGER NOT NULL,
    radius REAL NOT NULL,
    capability_vector TEXT NOT NULL,
    current_load REAL DEFAULT 0.0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_nodes_tier ON deployment_nodes(tier);
CREATE INDEX IF NOT EXISTS idx_nodes_service ON deployment_nodes(service_name);

CREATE TABLE IF NOT EXISTS node_replicas (
    primary_node_id TEXT REFERENCES deployment_nodes(node_id),
    replica_node_id TEXT REFERENCES deployment_nodes(node_id),
    replication_factor INTEGER NOT NULL,
    PRIMARY KEY (primary_node_id, replica_node_id)
);

CREATE TABLE IF NOT EXISTS tier_capacity (
    tier INTEGER PRIMARY KEY,
    total_compute REAL NOT NULL,
    total_memory REAL NOT NULL,
    total_storage REAL NOT NULL,
    used_compute REAL DEFAULT 0.0,
    used_memory REAL DEFAULT 0.0,
    used_storage REAL DEFAULT 0.0,
    node_count INTEGER DEFAULT 0
);

-- Initialize tier capacity
INSERT OR IGNORE INTO tier_capacity (tier, total_compute, total_memory, total_storage) VALUES
    (0, 1000, 10240, 100000),
    (1, 640, 5120, 50000),
    (2, 320, 2560, 20000),
    (3, 160, 1280, 10000),
    (4, 80, 640, 5000);
