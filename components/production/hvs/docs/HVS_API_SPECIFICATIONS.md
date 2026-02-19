# HVS-NVM API Specifications
## Version 1.0.0 | Complete API Reference

---

## HVS API

### Core Operations

#### `hvs.store_vector(vector, metadata=None, geometry='hyperboloid')`

Store a vector in HVS.

**Parameters:**
- `vector`: `np.ndarray` - Vector data (dimension must match HVS config)
- `metadata`: `Dict` - Optional metadata to store with vector
- `geometry`: `str` - Geometry type ('hyperboloid', 'poincare', 'euclidean')

**Returns:**
- `str` - Unique vector ID

**Example:**
```python
vector = np.random.randn(12)
vector_id = hvs.store_vector(vector, metadata={'source': 'doc1'})
```

---

#### `hvs.retrieve_vector(vector_id)`

Retrieve a vector by ID.

**Parameters:**
- `vector_id`: `str` - Vector ID

**Returns:**
- `Vector` - Vector object with data and metadata, or `None` if not found

**Example:**
```python
vector = hvs.retrieve_vector('abc-123')
print(vector.data, vector.metadata)
```

---

#### `hvs.update_vector(vector_id, new_vector=None, new_metadata=None)`

Update a stored vector.

**Parameters:**
- `vector_id`: `str` - Vector ID
- `new_vector`: `np.ndarray` - New vector data (optional)
- `new_metadata`: `Dict` - New metadata (merged with existing)

**Returns:**
- `bool` - Success status

---

#### `hvs.delete_vector(vector_id)`

Delete a vector.

**Parameters:**
- `vector_id`: `str` - Vector ID

**Returns:**
- `bool` - Success status

---

### Search Operations

#### `hvs.semantic_search(query_vector, k=10, filter=None, geometry='hyperboloid')`

Find k-nearest neighbors to query vector.

**Parameters:**
- `query_vector`: `np.ndarray` - Query vector
- `k`: `int` - Number of results
- `filter`: `Dict` - Metadata filter
- `geometry`: `str` - Distance geometry

**Returns:**
- `List[SearchResult]` - Ranked search results

**Example:**
```python
query = encoder.encode("What is HyperSync?")
results = hvs.semantic_search(query, k=10)
for r in results:
    print(f"Distance: {r.distance}, ID: {r.vector.id}")
```

---

#### `hvs.range_search(query_vector, radius, max_results=100)`

Find all vectors within geodesic radius.

**Parameters:**
- `query_vector`: `np.ndarray` - Query vector
- `radius`: `float` - Search radius
- `max_results`: `int` - Maximum results

**Returns:**
- `List[SearchResult]` - Results within radius

---

### Model Communication

#### `hvs.connect_model(model_id, region=None)`

Connect a model to HVS.

**Parameters:**
- `model_id`: `str` - Unique model identifier
- `region`: `VectorRegion` - Optional region for this model

**Returns:**
- `Connection` - Connection object

---

#### `hvs.send_message(from_model, to_model, message)`

Send message between models.

**Parameters:**
- `from_model`: `str` - Sender model ID
- `to_model`: `str` - Receiver model ID
- `message`: `Any` - Message content

**Returns:**
- `str` - Message ID

---

#### `hvs.receive_messages(model_id)`

Receive pending messages for a model.

**Parameters:**
- `model_id`: `str` - Model ID

**Returns:**
- `List[Message]` - Pending messages

---

### Geometry Operations

#### `hvs.distance(vector1, vector2, geometry='hyperboloid')`

Compute geodesic distance between vectors.

**Parameters:**
- `vector1`: `np.ndarray` - First vector
- `vector2`: `np.ndarray` - Second vector
- `geometry`: `str` - Geometry type

**Returns:**
- `float` - Geodesic distance

---

#### `hvs.transform(vector, from_geometry, to_geometry)`

Transform vector between geometries.

**Parameters:**
- `vector`: `np.ndarray` - Input vector
- `from_geometry`: `str` - Source geometry
- `to_geometry`: `str` - Target geometry

**Returns:**
- `np.ndarray` - Transformed vector

---

## NVM API

### Block Operations

#### `nvm.create_block(name, block_class, content, **kwargs)`

Create a new block.

**Parameters:**
- `name`: `str` - Block name
- `block_class`: `BlockClass` - Block type
- `content`: `bytes | str | Any` - Block content
- `readonly`: `bool` - Read-only flag
- `metadata`: `Dict` - Custom metadata
- `permissions`: `Dict` - Access permissions

**Returns:**
- `NVMBlock` - Created block

**Example:**
```python
block = nvm.create_block(
    name="my_doc",
    block_class=BlockClass.DOCUMENTATION,
    content="# Hello World",
    readonly=True
)
```

---

#### `nvm.get_block(block_id)`

Get block by ID.

**Parameters:**
- `block_id`: `str` - Block ID

**Returns:**
- `NVMBlock` - Block object or `None`

---

#### `nvm.update_block(block_id, content=None, metadata=None)`

Update block content or metadata.

**Parameters:**
- `block_id`: `str` - Block ID
- `content`: `Any` - New content (optional)
- `metadata`: `Dict` - New metadata (optional)

**Returns:**
- `bool` - Success status

**Raises:**
- `ReadOnlyBlockError` - If block is read-only

---

#### `nvm.delete_block(block_id, confirm=False)`

Delete a block.

**Parameters:**
- `block_id`: `str` - Block ID
- `confirm`: `bool` - Confirmation required

**Returns:**
- `bool` - Success status

---

### Query Operations

#### `nvm.semantic_query(query, k=10, block_class=None)`

Query blocks semantically.

**Parameters:**
- `query`: `str` - Natural language query
- `k`: `int` - Number of results
- `block_class`: `BlockClass` - Filter by block class

**Returns:**
- `List[Dict]` - Query results with blocks and scores

**Example:**
```python
results = nvm.semantic_query("How does HVS work?", k=5)
for r in results:
    print(f"Block: {r['block'].name}, Score: {r['score']}")
```

---

#### `nvm.query_documentation(query, k=10)`

Query documentation blocks only.

**Parameters:**
- `query`: `str` - Query string
- `k`: `int` - Number of results

**Returns:**
- `List[Dict]` - Documentation results

---

### Multi-Manifold Operations

#### `nvm.share_block(block_id, manifold_ids)`

Share block across manifolds.

**Parameters:**
- `block_id`: `str` - Block ID
- `manifold_ids`: `List[str]` - Manifold IDs to share with

**Returns:**
- `bool` - Success status

---

#### `nvm.get_manifold_blocks(manifold_id)`

Get all blocks accessible to a manifold.

**Parameters:**
- `manifold_id`: `str` - Manifold ID

**Returns:**
- `List[NVMBlock]` - Accessible blocks

---

## Integrated API

### `HVSNVMIntegration`

#### `integration.store(content, persist=True)`

Store content in integrated system.

**Parameters:**
- `content`: `Any` - Content to store
- `persist`: `bool` - Persist to NVM

**Returns:**
- `str` - Content ID

---

#### `integration.query(query, k=10)`

Query integrated system.

**Parameters:**
- `query`: `str` - Query string
- `k`: `int` - Number of results

**Returns:**
- `List[Dict]` - Results from both HVS and NVM

---

#### `integration.verify_consistency()`

Verify HVS-NVM consistency.

**Returns:**
- `Dict` - Consistency report

---

## Error Codes

| Code | Name | Description |
|------|------|-------------|
| `VECTOR_NOT_FOUND` | Vector not found | Vector ID does not exist |
| `BLOCK_NOT_FOUND` | Block not found | Block ID does not exist |
| `INVALID_VECTOR` | Invalid vector | Vector has invalid values |
| `READ_ONLY_ERROR` | Read-only block | Cannot modify read-only block |
| `PERMISSION_DENIED` | Permission denied | Insufficient permissions |
| `GEOMETRY_MISMATCH` | Geometry mismatch | Incompatible geometries |
| `CAPACITY_EXCEEDED` | Capacity exceeded | Storage limit reached |

---

*Document Version: 1.0.0*
*Last Updated: January 2026*
