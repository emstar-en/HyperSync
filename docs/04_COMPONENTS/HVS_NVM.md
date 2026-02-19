# Hyperbolic Vector Storage (HVS) System

## Overview

The HVS system provides persistent, geometry-aware vector storage that can be attached to models, stacks, trunks, or networks. It supports dimension-specific synchronization and network bridging capabilities.

## Key Features

### 1. Flexible Attachment
- **Model**: Single-model non-volatile memory
- **Stack**: Shared memory across model stack
- **Trunk**: Main network trunk storage
- **Network**: Network-wide storage
- **Bridge**: Cross-network bridge storage

### 2. Geometry Support
- Euclidean
- Spherical
- Poincaré Ball (hyperbolic)
- Hyperboloid (hyperbolic)
- SPD Log-Euclidean

### 3. Dimension-Specific Synchronization
- Sync specific dimensions across HVS instances
- Three sync modes: full, partial, selective
- Conflict resolution strategies: last_write_wins, vector_merge, manual

### 4. Network Bridging
- Connect multiple networks through shared HVS
- Isolation policies: full_share, read_only, write_through, isolated_namespaces
- Dimension-specific sharing

## CLI Usage

### Create HVS
```bash
hypersync hvs create \
 --name "my_memory" \
 --vector-dim 768 \
 --geometry poincare_ball \
 --attach-type model \
 --attach-id model_123
```

### List HVS Instances
```bash
# List all
hypersync hvs list

# Filter by attachment
hypersync hvs list --attach-type model --attach-id model_123

# Show only bridges
hypersync hvs list --bridges-only
```

### Get HVS Details
```bash
hypersync hvs get hvs_abc123
```

### Attach to Entity
```bash
hypersync hvs attach hvs_abc123 \
 --attach-type stack \
 --attach-id stack_456 \
 --attach-name "shared_embeddings"
```

### Configure Synchronization
```bash
# Sync specific dimensions
hypersync hvs sync hvs_abc123 \
 --enable \
 --sync-dims "0,1,2,10,11,12" \
 --sync-mode selective \
 --conflict-resolution vector_merge

# Disable sync
hypersync hvs sync hvs_abc123 --disable
```

### Create Network Bridge
```bash
hypersync hvs bridge hvs_abc123 \
 --network-ids "net_1,net_2,net_3" \
 --shared-dims "0,1,2" \
 --isolation isolated_namespaces
```

### Delete HVS
```bash
hypersync hvs delete hvs_abc123 --confirm
```

## API Usage

### Create HVS
```python
POST /hvs/create
{
 "name": "my_memory",
 "vector_dim": 768,
 "geometry_space": "poincare_ball",
 "attach_type": "model",
 "attach_id": "model_123"
}
```

### List HVS
```python
GET /hvs/list?attach_type=model&attach_id=model_123
```

### Configure Sync
```python
POST /hvs/sync
{
 "hvs_id": "hvs_abc123",
 "enabled": true,
 "sync_dims": [0, 1, 2, 10, 11, 12],
 "sync_mode": "selective",
 "conflict_resolution": "vector_merge"
}
```

### Create Bridge
```python
POST /hvs/bridge
{
 "hvs_id": "hvs_abc123",
 "network_ids": ["net_1", "net_2", "net_3"],
 "shared_dims": [0, 1, 2],
 "isolation_policy": "isolated_namespaces"
}
```

## Model Tool Usage

Models can use HVS through the following tools:

### hvs_create
```json
{
 "name": "my_memory",
 "vector_dim": 768,
 "geometry_space": "poincare_ball",
 "attach_type": "model",
 "attach_id": "self"
}
```

### hvs_list
```json
{
 "attach_type": "model",
 "attach_id": "self"
}
```

### hvs_configure_sync
```json
{
 "hvs_id": "hvs_abc123",
 "enabled": true,
 "sync_dims": [0, 1, 2],
 "sync_mode": "selective"
}
```

### hvs_create_bridge
```json
{
 "hvs_id": "hvs_abc123",
 "network_ids": ["net_1", "net_2"],
 "shared_dims": [0, 1, 2],
 "isolation_policy": "isolated_namespaces"
}
```

## Use Cases

### 1. Single Model Memory
Create persistent memory for a single model:
```bash
hypersync hvs create \
 --name "model_memory" \
 --vector-dim 768 \
 --attach-type model \
 --attach-id model_123
```

### 2. Shared Stack Memory
Create shared embeddings across a model stack:
```bash
hypersync hvs create \
 --name "stack_embeddings" \
 --vector-dim 1024 \
 --attach-type stack \
 --attach-id stack_456
```

### 3. Dimension-Specific Sync
Sync only semantic dimensions across instances:
```bash
hypersync hvs sync hvs_abc123 \
 --sync-dims "0,1,2,3,4" \
 --sync-mode selective
```

### 4. Network Bridge
Bridge two networks through shared HVS:
```bash
# Create bridge HVS
hypersync hvs create \
 --name "network_bridge" \
 --vector-dim 512 \
 --attach-type bridge

# Configure bridge
hypersync hvs bridge hvs_bridge123 \
 --network-ids "net_1,net_2" \
 --shared-dims "0,1,2,3" \
 --isolation isolated_namespaces
```

## Best Practices

1. **Geometry Selection**
 - Use `poincare_ball` for hierarchical data
 - Use `euclidean` for standard embeddings
 - Use `spherical` for normalized vectors

2. **Capacity Planning**
 - Set `max_vectors` to prevent unbounded growth
 - Use `auto_expand` growth policy for flexibility

3. **Synchronization**
 - Sync only necessary dimensions to reduce overhead
 - Use `selective` mode for fine-grained control
 - Choose appropriate conflict resolution strategy

4. **Network Bridging**
 - Use `isolated_namespaces` for security
 - Share only necessary dimensions
 - Monitor bridge performance

5. **Attachment Strategy**
 - Attach to `model` for single-model memory
 - Attach to `stack` for shared memory
 - Attach to `trunk` for network-wide storage
 - Use `bridge` for cross-network communication

## Schema Reference

### HVSSchema
- `hvs_id`: Unique identifier
- `name`: Human-readable name
- `geometry`: Geometry configuration
- `index`: Index configuration
- `capacity`: Capacity limits
- `attachments`: List of attachments
- `sync`: Synchronization config
- `bridges`: Network bridges
- `status`: Current status

### HVSSyncConfig
- `enabled`: Enable/disable sync
- `sync_dims`: Dimension indices to sync
- `sync_mode`: full, partial, selective
- `conflict_resolution`: Strategy for conflicts

### HVSNetworkBridge
- `bridge_id`: Unique bridge ID
- `network_ids`: Connected networks
- `shared_dims`: Shared dimensions
- `isolation_policy`: Data isolation policy
