# NVM (Non-Volatile Memory) Specification
## Version 1.0.0 | HyperSync Persistent Storage Component

---

## Executive Summary

### What is NVM?

**NVM (Non-Volatile Memory)** is the persistent semantic storage layer of HyperSync. It provides:

- **Dense Semantic Blocks**: Structured blocks of semantic information
- **HVS Indexing**: All NVM content is indexed by HVS for geometric access
- **Manifold Hosting**: Content organized on the AGUA manifold structure
- **Cross-Manifold Sharing**: Blocks can be shared between multiple manifolds
- **Slow Bridge**: Functions as a communication bridge between separate manifolds

### Why NVM is Critical

1. **Persistent Storage**: Semantic information survives restarts and sessions
2. **Consistent Access**: Same geometric representation for all interacting models
3. **Shared Knowledge**: Multiple manifolds can access shared blocks
4. **Documentation Storage**: Read-only HyperSync documentation accessible to all
5. **Model Memory Extension**: Extends model context beyond token limits

### Key Capabilities

| Capability | Description | Characteristic |
|------------|-------------|----------------|
| Dense Blocks | Semantically rich information units | Structured, typed |
| HVS Indexed | Vector-indexed for semantic search | O(log n) queries |
| Manifold Hosted | Geometric organization | Curvature-aware |
| Slower Silicon | NVMe/disk storage | Persistent, large |
| Multi-Manifold | Shared across manifolds | Slow bridge |

### Role in HyperSync

```
┌─────────────────────────────────────────────────────────────────┐
│                    HyperSync Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐       │
│   │ Model A │   │ Model B │   │ Model C │   │ Model D │       │
│   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘       │
│        │             │             │             │              │
│        └─────────────┴─────────────┴─────────────┘              │
│                           │                                     │
│              ┌────────────▼────────────┐                       │
│              │          HVS            │                       │
│              │  (Fast Vector Index)    │                       │
│              └────────────┬────────────┘                       │
│                           │                                     │
│              ┌────────────▼────────────┐                       │
│              │          NVM            │  ◀── YOU ARE HERE     │
│              │  (Persistent Storage)   │                       │
│              │                         │                       │
│              │  ┌─────┐ ┌─────┐       │                       │
│              │  │Block│ │Block│ ...   │                       │
│              │  └─────┘ └─────┘       │                       │
│              └─────────────────────────┘                       │
│                           │                                     │
│              ┌────────────▼────────────┐                       │
│              │    Slower Silicon       │                       │
│              │   (NVMe, Disk, Cloud)   │                       │
│              └─────────────────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture Overview

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          NVM Architecture                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                       Block Manager                              │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │    │
│  │  │  Create  │  │   Get    │  │  Delete  │  │    List      │    │    │
│  │  │  Block   │  │  Block   │  │  Block   │  │   Blocks     │    │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│  ┌─────────────────────────────────▼───────────────────────────────┐    │
│  │                      Semantic Blocks                             │    │
│  │  ┌───────────────────────────────────────────────────────┐      │    │
│  │  │  Block Structure                                       │      │    │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │      │    │
│  │  │  │  Header │ │  Data   │ │ Vectors │ │Metadata │     │      │    │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘     │      │    │
│  │  └───────────────────────────────────────────────────────┘      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│  ┌─────────────────────────────────▼───────────────────────────────┐    │
│  │                      HVS Integration                             │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐    │    │
│  │  │  Index    │  │  Query    │  │  Update   │  │  Sync     │    │    │
│  │  │  Block    │  │ via HVS   │  │  Index    │  │  Index    │    │    │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│  ┌─────────────────────────────────▼───────────────────────────────┐    │
│  │                      Storage Layer                               │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐    │    │
│  │  │   NVMe    │  │   Disk    │  │   Cloud   │  │   Hybrid  │    │    │
│  │  │  Storage  │  │  Storage  │  │  Storage  │  │  Storage  │    │    │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│  ┌─────────────────────────────────▼───────────────────────────────┐    │
│  │                   Multi-Manifold Layer                           │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐    │    │
│  │  │ Manifold  │  │ Manifold  │  │ Manifold  │  │   Slow    │    │    │
│  │  │     A     │  │     B     │  │     C     │  │  Bridge   │    │    │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Purpose | Key Functions |
|-----------|---------|---------------|
| **Block Manager** | Create, manage, delete blocks | Lifecycle management |
| **Semantic Blocks** | Store dense semantic information | Structured data |
| **HVS Integration** | Index blocks in HVS | Semantic search |
| **Storage Layer** | Persist to slower silicon | Durability |
| **Multi-Manifold** | Cross-manifold access | Slow bridge |

---

## Semantic Blocks

### Block Structure

A semantic block is the fundamental unit of NVM storage:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Semantic Block Structure                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        Header                             │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │   │
│  │  │  Block ID  │ │   Name     │ │   Class    │            │   │
│  │  │  (UUID)    │ │  (string)  │ │   (enum)   │            │   │
│  │  └────────────┘ └────────────┘ └────────────┘            │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │   │
│  │  │  Version   │ │ Created At │ │ Read-Only  │            │   │
│  │  │   (int)    │ │ (datetime) │ │   (bool)   │            │   │
│  │  └────────────┘ └────────────┘ └────────────┘            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        Data                               │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  Dense Semantic Content                             │  │   │
│  │  │  - Documents, text, structured data                 │  │   │
│  │  │  - JSON, Markdown, binary formats                   │  │   │
│  │  │  - Compressed if large                              │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      Vector Index                         │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  Embedded vectors for semantic search               │  │   │
│  │  │  - One or more vectors per block                    │  │   │
│  │  │  - HVS-indexed for fast retrieval                   │  │   │
│  │  │  - Geometry-aware placement                         │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       Metadata                            │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  Custom key-value pairs                             │  │   │
│  │  │  - Tags, labels, attributes                         │  │   │
│  │  │  - Access control info                              │  │   │
│  │  │  - Manifold associations                            │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Block Data Structure

```python
@dataclass
class NVMBlock:
    """Semantic block in NVM"""
    
    # Header
    id: str                          # Unique block identifier (UUID)
    name: str                        # Human-readable name
    block_class: BlockClass          # Block type (documentation, state, etc.)
    version: int                     # Version number
    created_at: datetime             # Creation timestamp
    updated_at: datetime             # Last update timestamp
    readonly: bool                   # Is block read-only?
    
    # Data
    content_type: str                # MIME type of content
    content: bytes                   # Raw content (may be compressed)
    content_size: int                # Size in bytes
    compression: Optional[str]       # Compression algorithm used
    
    # Vector Index
    vectors: List[np.ndarray]        # Embedding vectors
    vector_dimension: int            # Dimension of vectors
    geometry: str                    # Geometry type (hyperboloid, etc.)
    manifold_positions: List[Tuple]  # Positions on manifold
    
    # Metadata
    metadata: Dict[str, Any]         # Custom metadata
    tags: List[str]                  # Tags for categorization
    permissions: Dict[str, List[str]] # Access permissions
    manifolds: List[str]             # Associated manifolds
    
    # Lifecycle
    status: BlockStatus              # active, archived, deleted
    access_count: int                # Number of accesses
    last_accessed: datetime          # Last access time

class BlockClass(Enum):
    """Types of NVM blocks"""
    DOCUMENTATION = "documentation"  # Read-only documentation
    PROGRAM_STATE = "program_state"  # Program state/memory
    KNOWLEDGE_GRAPH = "knowledge_graph"  # Knowledge graph data
    CACHE = "cache"                  # Temporary cache
    CONVERSATION = "conversation"    # Conversation history
    MODEL_MEMORY = "model_memory"    # Model-specific memory
    SHARED_KNOWLEDGE = "shared_knowledge"  # Cross-model knowledge
    CUSTOM = "custom"                # User-defined type
```

### Dense Semantic Information

Blocks contain dense, structured semantic content:

```python
class SemanticContent:
    """Dense semantic content within a block"""
    
    def __init__(self, content_type: str):
        self.content_type = content_type
        self.chunks = []
        self.relationships = []
        self.embeddings = []
    
    def add_chunk(self, text: str, metadata: Dict = None):
        """Add a semantic chunk"""
        chunk = {
            'id': generate_uuid(),
            'text': text,
            'metadata': metadata or {},
            'embedding': None  # Will be computed
        }
        self.chunks.append(chunk)
        return chunk['id']
    
    def add_relationship(self, source_id: str, target_id: str, 
                         relation_type: str, weight: float = 1.0):
        """Add relationship between chunks"""
        self.relationships.append({
            'source': source_id,
            'target': target_id,
            'type': relation_type,
            'weight': weight
        })
    
    def compute_embeddings(self, encoder: VectorEncoder):
        """Compute embeddings for all chunks"""
        for chunk in self.chunks:
            chunk['embedding'] = encoder.encode(chunk['text'])
            self.embeddings.append(chunk['embedding'])
    
    def to_block_data(self) -> bytes:
        """Serialize to block data format"""
        data = {
            'content_type': self.content_type,
            'chunks': self.chunks,
            'relationships': self.relationships
        }
        return msgpack.packb(data)
    
    @classmethod
    def from_block_data(cls, data: bytes) -> 'SemanticContent':
        """Deserialize from block data"""
        parsed = msgpack.unpackb(data)
        content = cls(parsed['content_type'])
        content.chunks = parsed['chunks']
        content.relationships = parsed['relationships']
        return content
```

### Geometric Structuring

Content is organized geometrically on the manifold:

```python
class GeometricBlockStructure:
    """Geometric organization of block content"""
    
    def __init__(self, geometry: str = 'hyperboloid', dimension: int = 12):
        self.geometry = geometry
        self.dimension = dimension
        self.positions = {}  # chunk_id -> manifold_position
    
    def place_chunk(self, chunk_id: str, embedding: np.ndarray, 
                    parent_id: Optional[str] = None):
        """Place chunk on manifold"""
        if parent_id and parent_id in self.positions:
            # Place relative to parent (hierarchical)
            parent_pos = self.positions[parent_id]
            position = self._place_child(parent_pos, embedding)
        else:
            # Place at root level
            position = self._project_to_manifold(embedding)
        
        self.positions[chunk_id] = position
        return position
    
    def _project_to_manifold(self, embedding: np.ndarray) -> np.ndarray:
        """Project embedding to manifold"""
        if self.geometry == 'hyperboloid':
            # Project to hyperboloid
            x_space = embedding[:self.dimension-1]
            x_time = np.sqrt(1 + np.dot(x_space, x_space))
            return np.concatenate([[x_time], x_space])
        elif self.geometry == 'poincare':
            # Project to Poincaré ball
            norm = np.linalg.norm(embedding)
            if norm >= 1:
                embedding = embedding / norm * (1 - 1e-5)
            return embedding[:self.dimension]
        else:
            return embedding[:self.dimension]
    
    def _place_child(self, parent_pos: np.ndarray, 
                     embedding: np.ndarray) -> np.ndarray:
        """Place child relative to parent"""
        # Use exponential map from parent
        tangent = self._project_to_tangent(parent_pos, embedding)
        return self._exp_map(parent_pos, tangent * 0.1)  # Small step
    
    def get_geodesic_distance(self, chunk_id1: str, chunk_id2: str) -> float:
        """Compute geodesic distance between chunks"""
        pos1 = self.positions[chunk_id1]
        pos2 = self.positions[chunk_id2]
        
        if self.geometry == 'hyperboloid':
            inner = -pos1[0]*pos2[0] + np.dot(pos1[1:], pos2[1:])
            return np.arccosh(max(1.0, -inner))
        else:
            return np.linalg.norm(pos1 - pos2)
```

### Block Types and Classes

#### 1. Documentation Blocks (Read-Only)

```python
class DocumentationBlock(NVMBlock):
    """Read-only documentation block"""
    
    def __init__(self, name: str, content: str):
        super().__init__(
            name=name,
            block_class=BlockClass.DOCUMENTATION,
            readonly=True
        )
        self.content = self._process_documentation(content)
    
    def _process_documentation(self, content: str) -> bytes:
        """Process and structure documentation"""
        # Parse markdown/text
        sections = self._parse_sections(content)
        
        # Create semantic chunks
        chunks = []
        for section in sections:
            chunks.append({
                'title': section['title'],
                'content': section['content'],
                'level': section['level']
            })
        
        return msgpack.packb(chunks)
    
    def get_section(self, title: str) -> Optional[Dict]:
        """Get documentation section by title"""
        chunks = msgpack.unpackb(self.content)
        for chunk in chunks:
            if chunk['title'].lower() == title.lower():
                return chunk
        return None

# Example: HyperSync documentation
hypersync_docs = DocumentationBlock(
    name="hypersync_documentation",
    content=open("HYPERSYNC_DOCS.md").read()
)
```

#### 2. Program State Blocks

```python
class ProgramStateBlock(NVMBlock):
    """Block for storing program/model state"""
    
    def __init__(self, name: str, initial_state: Dict = None):
        super().__init__(
            name=name,
            block_class=BlockClass.PROGRAM_STATE,
            readonly=False
        )
        self.state = initial_state or {}
    
    def update_state(self, key: str, value: Any):
        """Update state value"""
        self.state[key] = value
        self.version += 1
        self.updated_at = datetime.now()
        self._recompute_embedding()
    
    def get_state(self, key: str) -> Any:
        """Get state value"""
        return self.state.get(key)
    
    def checkpoint(self) -> str:
        """Create checkpoint of current state"""
        checkpoint_id = f"{self.id}:v{self.version}"
        # Store checkpoint...
        return checkpoint_id
    
    def restore(self, checkpoint_id: str):
        """Restore from checkpoint"""
        # Restore from checkpoint...
        pass
```

#### 3. Knowledge Graph Blocks

```python
class KnowledgeGraphBlock(NVMBlock):
    """Block for storing knowledge graph data"""
    
    def __init__(self, name: str):
        super().__init__(
            name=name,
            block_class=BlockClass.KNOWLEDGE_GRAPH,
            readonly=False
        )
        self.nodes = {}
        self.edges = []
    
    def add_node(self, node_id: str, label: str, properties: Dict = None):
        """Add knowledge graph node"""
        self.nodes[node_id] = {
            'label': label,
            'properties': properties or {},
            'embedding': None
        }
    
    def add_edge(self, source: str, target: str, relation: str, 
                 properties: Dict = None):
        """Add knowledge graph edge"""
        self.edges.append({
            'source': source,
            'target': target,
            'relation': relation,
            'properties': properties or {}
        })
    
    def query_subgraph(self, query_vector: np.ndarray, k: int = 10) -> Dict:
        """Query subgraph by semantic similarity"""
        # Find nearest nodes
        nearest = self._find_nearest_nodes(query_vector, k)
        
        # Extract induced subgraph
        node_ids = set(n['id'] for n in nearest)
        relevant_edges = [
            e for e in self.edges 
            if e['source'] in node_ids or e['target'] in node_ids
        ]
        
        return {
            'nodes': nearest,
            'edges': relevant_edges
        }
```

#### 4. Cache Blocks

```python
class CacheBlock(NVMBlock):
    """Temporary cache block with TTL"""
    
    def __init__(self, name: str, ttl_seconds: int = 3600):
        super().__init__(
            name=name,
            block_class=BlockClass.CACHE,
            readonly=False
        )
        self.ttl = ttl_seconds
        self.cache = {}
        self.expiry_times = {}
    
    def set(self, key: str, value: Any, vector: np.ndarray = None):
        """Set cache value with optional vector"""
        self.cache[key] = {
            'value': value,
            'vector': vector,
            'created_at': time.time()
        }
        self.expiry_times[key] = time.time() + self.ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value if not expired"""
        if key in self.cache:
            if time.time() < self.expiry_times[key]:
                return self.cache[key]['value']
            else:
                # Expired
                del self.cache[key]
                del self.expiry_times[key]
        return None
    
    def semantic_get(self, query_vector: np.ndarray, threshold: float = 0.9):
        """Get cache entry by semantic similarity"""
        best_match = None
        best_score = 0
        
        for key, entry in self.cache.items():
            if entry['vector'] is not None:
                score = self._similarity(query_vector, entry['vector'])
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = entry
        
        return best_match
    
    def cleanup_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            k for k, exp in self.expiry_times.items() 
            if current_time >= exp
        ]
        for key in expired_keys:
            del self.cache[key]
            del self.expiry_times[key]
```

### Block Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                     Block Lifecycle                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│  │ Created │ ──▶│ Active  │ ──▶│Archived │ ──▶│ Deleted │      │
│  └─────────┘    └────┬────┘    └────┬────┘    └─────────┘      │
│                      │              │                            │
│                      │              │                            │
│                 ┌────▼────┐   ┌────▼────┐                       │
│                 │ Updated │   │Restored │                       │
│                 └────┬────┘   └────┬────┘                       │
│                      │              │                            │
│                      └──────────────┘                            │
│                             │                                    │
│                        (loop back)                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

```python
class BlockLifecycleManager:
    """Manage block lifecycle"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
    
    def create(self, name: str, block_class: BlockClass, 
               content: Any, readonly: bool = False) -> NVMBlock:
        """Create new block"""
        block = NVMBlock(
            id=generate_uuid(),
            name=name,
            block_class=block_class,
            version=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            readonly=readonly,
            content=self._serialize_content(content),
            status=BlockStatus.ACTIVE
        )
        
        # Index in HVS
        self._index_block(block)
        
        # Persist
        self._persist_block(block)
        
        return block
    
    def update(self, block_id: str, content: Any):
        """Update block content"""
        block = self.nvm.get_block(block_id)
        
        if block.readonly:
            raise ReadOnlyBlockError(f"Block {block_id} is read-only")
        
        block.content = self._serialize_content(content)
        block.version += 1
        block.updated_at = datetime.now()
        
        # Re-index in HVS
        self._reindex_block(block)
        
        # Persist
        self._persist_block(block)
    
    def archive(self, block_id: str):
        """Archive block (keep but mark inactive)"""
        block = self.nvm.get_block(block_id)
        block.status = BlockStatus.ARCHIVED
        self._persist_block(block)
    
    def restore(self, block_id: str):
        """Restore archived block"""
        block = self.nvm.get_block(block_id)
        block.status = BlockStatus.ACTIVE
        self._persist_block(block)
    
    def delete(self, block_id: str, hard_delete: bool = False):
        """Delete block"""
        if hard_delete:
            # Permanent deletion
            self._remove_from_hvs(block_id)
            self._remove_from_storage(block_id)
        else:
            # Soft delete
            block = self.nvm.get_block(block_id)
            block.status = BlockStatus.DELETED
            self._persist_block(block)
```

---

## HVS Indexing

### How NVM is Indexed by HVS

Every NVM block is indexed in HVS for semantic search:

```
┌─────────────────────────────────────────────────────────────────┐
│                   NVM-HVS Indexing Relationship                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      NVM Block                            │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ Content: "HyperSync is a distributed AI system..."  │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                           │                               │   │
│  │                     Embedding                             │   │
│  │                           │                               │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ Vector: [0.123, -0.456, 0.789, ...]                 │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                               │                                  │
│                          Index in HVS                            │
│                               │                                  │
│                               ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                         HVS                               │   │
│  │                                                           │   │
│  │     ● block_1 vector                                     │   │
│  │        ● block_2 vector                                  │   │
│  │           ● block_3 vector                               │   │
│  │              ● (query vector)                            │   │
│  │                                                           │   │
│  │  Query: "What is HyperSync?"                             │   │
│  │  → Returns block_1 (closest match)                       │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Vector Indexing Strategy

```python
class NVMHVSIndex:
    """Index NVM blocks in HVS"""
    
    def __init__(self, hvs: HVS, encoder: VectorEncoder):
        self.hvs = hvs
        self.encoder = encoder
        self.block_vectors = {}  # block_id -> List[vector_id]
    
    def index_block(self, block: NVMBlock):
        """Index a block in HVS"""
        # Extract content chunks
        chunks = self._extract_chunks(block)
        
        vector_ids = []
        for i, chunk in enumerate(chunks):
            # Encode chunk to vector
            vector = self.encoder.encode(chunk['text'])
            
            # Store in HVS
            vector_id = self.hvs.store_vector(
                vector=vector,
                metadata={
                    'block_id': block.id,
                    'block_name': block.name,
                    'block_class': block.block_class.value,
                    'chunk_index': i,
                    'chunk_text': chunk['text'][:500],  # Preview
                    'readonly': block.readonly
                }
            )
            vector_ids.append(vector_id)
        
        self.block_vectors[block.id] = vector_ids
    
    def _extract_chunks(self, block: NVMBlock) -> List[Dict]:
        """Extract semantic chunks from block content"""
        if block.content_type == 'text/markdown':
            return self._chunk_markdown(block.content)
        elif block.content_type == 'application/json':
            return self._chunk_json(block.content)
        else:
            return self._chunk_text(block.content)
    
    def _chunk_markdown(self, content: bytes) -> List[Dict]:
        """Chunk markdown content by sections"""
        text = content.decode('utf-8')
        sections = []
        current_section = {'title': '', 'text': ''}
        
        for line in text.split('\n'):
            if line.startswith('#'):
                if current_section['text']:
                    sections.append(current_section)
                current_section = {'title': line.lstrip('#').strip(), 'text': ''}
            else:
                current_section['text'] += line + '\n'
        
        if current_section['text']:
            sections.append(current_section)
        
        return sections
    
    def update_block_index(self, block: NVMBlock):
        """Update index when block changes"""
        # Remove old vectors
        if block.id in self.block_vectors:
            for vector_id in self.block_vectors[block.id]:
                self.hvs.delete_vector(vector_id)
        
        # Re-index
        self.index_block(block)
    
    def remove_block_index(self, block_id: str):
        """Remove block from index"""
        if block_id in self.block_vectors:
            for vector_id in self.block_vectors[block_id]:
                self.hvs.delete_vector(vector_id)
            del self.block_vectors[block_id]
```

### Geometric Addressing

```python
class GeometricAddressing:
    """Address NVM content via geometric coordinates"""
    
    def __init__(self, geometry: str = 'hyperboloid'):
        self.geometry = geometry
        self.address_map = {}  # geometric_address -> block_chunk
    
    def assign_address(self, block_id: str, chunk_index: int, 
                       manifold_position: np.ndarray) -> str:
        """Assign geometric address to chunk"""
        address = self._encode_address(manifold_position)
        self.address_map[address] = {
            'block_id': block_id,
            'chunk_index': chunk_index,
            'position': manifold_position
        }
        return address
    
    def _encode_address(self, position: np.ndarray) -> str:
        """Encode position as address string"""
        # Discretize position for addressing
        discretized = np.round(position * 1000).astype(int)
        return f"geo:{':'.join(map(str, discretized))}"
    
    def resolve_address(self, address: str) -> Dict:
        """Resolve geometric address to block chunk"""
        return self.address_map.get(address)
    
    def find_nearby_addresses(self, position: np.ndarray, 
                              radius: float) -> List[str]:
        """Find addresses within geodesic radius"""
        nearby = []
        for address, data in self.address_map.items():
            distance = self._geodesic_distance(position, data['position'])
            if distance <= radius:
                nearby.append((address, distance))
        
        nearby.sort(key=lambda x: x[1])
        return [addr for addr, _ in nearby]
```

### Query Interface

```python
class NVMQueryInterface:
    """Query NVM content via HVS"""
    
    def __init__(self, nvm: 'NVM', hvs: HVS, encoder: VectorEncoder):
        self.nvm = nvm
        self.hvs = hvs
        self.encoder = encoder
    
    def semantic_query(self, query: str, k: int = 10, 
                       block_class: BlockClass = None) -> List[Dict]:
        """Query NVM content semantically"""
        # Encode query
        query_vector = self.encoder.encode(query)
        
        # Build filter
        filter_dict = {}
        if block_class:
            filter_dict['block_class'] = block_class.value
        
        # Search HVS
        results = self.hvs.semantic_search(
            query_vector=query_vector,
            k=k,
            filter=filter_dict if filter_dict else None
        )
        
        # Enrich with full block data
        enriched = []
        for result in results:
            block = self.nvm.get_block(result.metadata['block_id'])
            enriched.append({
                'block': block,
                'chunk_index': result.metadata['chunk_index'],
                'chunk_preview': result.metadata['chunk_text'],
                'distance': result.distance,
                'score': result.score
            })
        
        return enriched
    
    def query_by_block(self, query: str, block_id: str, k: int = 10) -> List[Dict]:
        """Query within specific block"""
        query_vector = self.encoder.encode(query)
        
        results = self.hvs.semantic_search(
            query_vector=query_vector,
            k=k,
            filter={'block_id': block_id}
        )
        
        return self._format_results(results)
    
    def query_documentation(self, query: str, k: int = 10) -> List[Dict]:
        """Query documentation blocks only"""
        return self.semantic_query(
            query=query,
            k=k,
            block_class=BlockClass.DOCUMENTATION
        )
```

### Search Capabilities

| Search Type | Description | Use Case |
|-------------|-------------|----------|
| Semantic | Natural language query | "What is HyperSync?" |
| Filtered | Semantic + metadata | Docs from last week |
| Range | All within distance | Nearby concepts |
| Exact | By block ID/name | Known content |
| Hybrid | Semantic + keyword | Complex queries |

---

## Manifold Hosting

### Integration with Manifold Structure

NVM content is organized on the AGUA manifold:

```
┌─────────────────────────────────────────────────────────────────┐
│                   Manifold Hosting Structure                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│               AGUA Manifold: H⁴ × S³ × E⁵                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Hyperbolic (H⁴)                          │   │
│  │                                                           │   │
│  │     ● Documentation blocks (hierarchical)                 │   │
│  │        ● Concept A                                        │   │
│  │           ● Sub-concept A.1                               │   │
│  │           ● Sub-concept A.2                               │   │
│  │        ● Concept B                                        │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Spherical (S³)                           │   │
│  │                                                           │   │
│  │     ○ Directional/cyclic content                         │   │
│  │        ○ Temporal patterns                                │   │
│  │        ○ Periodic concepts                                │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Euclidean (E⁵)                           │   │
│  │                                                           │   │
│  │     □ Flat/linear content                                 │   │
│  │        □ Program state                                    │   │
│  │        □ Cache data                                       │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Geometric Placement

```python
class ManifoldPlacer:
    """Place NVM blocks on manifold"""
    
    def __init__(self, geometry: str = 'product'):
        self.geometry = geometry
        self.components = {
            'H4': HyperboloidComponent(dim=4),
            'S3': SphericalComponent(dim=3),
            'E5': EuclideanComponent(dim=5)
        }
    
    def place_block(self, block: NVMBlock) -> ManifoldPosition:
        """Place block on appropriate manifold component"""
        # Determine component based on block class
        component = self._select_component(block.block_class)
        
        # Compute placement
        embedding = self._get_block_embedding(block)
        position = component.project(embedding)
        
        return ManifoldPosition(
            component=component.name,
            coordinates=position,
            block_id=block.id
        )
    
    def _select_component(self, block_class: BlockClass) -> ManifoldComponent:
        """Select manifold component for block class"""
        mapping = {
            BlockClass.DOCUMENTATION: 'H4',      # Hierarchical
            BlockClass.KNOWLEDGE_GRAPH: 'H4',    # Hierarchical
            BlockClass.PROGRAM_STATE: 'E5',      # Flat
            BlockClass.CACHE: 'E5',              # Flat
            BlockClass.CONVERSATION: 'S3',       # Temporal/cyclic
            BlockClass.MODEL_MEMORY: 'H4',       # Hierarchical
        }
        return self.components[mapping.get(block_class, 'E5')]
    
    def get_neighbors(self, position: ManifoldPosition, 
                      radius: float) -> List[NVMBlock]:
        """Get blocks within geodesic radius"""
        component = self.components[position.component]
        nearby_positions = component.range_query(position.coordinates, radius)
        return [self._get_block_at(pos) for pos in nearby_positions]
```

### Coordinate System

```python
class ManifoldCoordinateSystem:
    """Coordinate system for NVM on manifold"""
    
    def __init__(self):
        self.origins = {
            'H4': np.array([1.0, 0.0, 0.0, 0.0, 0.0]),  # Hyperboloid origin
            'S3': np.array([1.0, 0.0, 0.0, 0.0]),       # Sphere north pole
            'E5': np.array([0.0, 0.0, 0.0, 0.0, 0.0])   # Euclidean origin
        }
    
    def get_coordinates(self, block: NVMBlock) -> Dict:
        """Get full coordinates for block"""
        position = block.manifold_positions[0] if block.manifold_positions else None
        
        if position is None:
            return None
        
        return {
            'component': position.component,
            'local': position.coordinates,
            'global': self._to_global(position),
            'geodesic_from_origin': self._distance_from_origin(position)
        }
    
    def _to_global(self, position: ManifoldPosition) -> np.ndarray:
        """Convert to global (product manifold) coordinates"""
        # Pad to full 12D product space
        global_coords = np.zeros(12)
        
        if position.component == 'H4':
            global_coords[:5] = position.coordinates
        elif position.component == 'S3':
            global_coords[5:9] = position.coordinates
        elif position.component == 'E5':
            global_coords[7:12] = position.coordinates
        
        return global_coords
    
    def _distance_from_origin(self, position: ManifoldPosition) -> float:
        """Compute geodesic distance from component origin"""
        origin = self.origins[position.component]
        
        if position.component == 'H4':
            inner = -origin[0]*position.coordinates[0] + \
                    np.dot(origin[1:], position.coordinates[1:])
            return np.arccosh(max(1.0, -inner))
        elif position.component == 'S3':
            inner = np.dot(origin, position.coordinates)
            return np.arccos(np.clip(inner, -1, 1))
        else:
            return np.linalg.norm(position.coordinates - origin)
```

### Spatial Organization

```python
class SpatialOrganizer:
    """Organize NVM content spatially on manifold"""
    
    def __init__(self, nvm: 'NVM', hvs: HVS):
        self.nvm = nvm
        self.hvs = hvs
        self.clusters = {}
    
    def organize_by_topic(self, blocks: List[NVMBlock]) -> Dict:
        """Organize blocks by semantic topic clusters"""
        # Get all embeddings
        embeddings = [self._get_embedding(b) for b in blocks]
        
        # Cluster on manifold
        clusters = self._hyperbolic_kmeans(embeddings, k=10)
        
        # Assign blocks to clusters
        organized = {}
        for i, (block, cluster_id) in enumerate(zip(blocks, clusters)):
            if cluster_id not in organized:
                organized[cluster_id] = []
            organized[cluster_id].append(block)
        
        self.clusters = organized
        return organized
    
    def _hyperbolic_kmeans(self, embeddings: List[np.ndarray], 
                           k: int) -> List[int]:
        """K-means clustering in hyperbolic space"""
        # Initialize centroids
        centroids = self._init_centroids(embeddings, k)
        
        for iteration in range(100):
            # Assign to nearest centroid
            assignments = []
            for emb in embeddings:
                distances = [self._hyperbolic_distance(emb, c) for c in centroids]
                assignments.append(np.argmin(distances))
            
            # Update centroids (hyperbolic Fréchet mean)
            new_centroids = []
            for i in range(k):
                cluster_points = [e for e, a in zip(embeddings, assignments) if a == i]
                if cluster_points:
                    new_centroids.append(self._frechet_mean(cluster_points))
                else:
                    new_centroids.append(centroids[i])
            
            # Check convergence
            if self._converged(centroids, new_centroids):
                break
            centroids = new_centroids
        
        return assignments
    
    def get_topic_neighbors(self, block: NVMBlock, k: int = 5) -> List[NVMBlock]:
        """Get topically related blocks"""
        embedding = self._get_embedding(block)
        
        # Find which cluster
        cluster_id = None
        for cid, blocks in self.clusters.items():
            if block in blocks:
                cluster_id = cid
                break
        
        if cluster_id is None:
            # Fall back to semantic search
            return self.nvm.semantic_query(block.content, k=k)
        
        # Return from same cluster
        return self.clusters[cluster_id][:k]
```

---

## Storage Layer

### Slower Silicon Storage (NVMe, Disk)

NVM uses persistent storage for durability:

```
┌─────────────────────────────────────────────────────────────────┐
│                    NVM Storage Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Hot Cache (RAM)                        │   │
│  │           Frequently accessed blocks                      │   │
│  │              Latency: < 1ms                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    NVMe Storage                           │   │
│  │           Primary persistent storage                      │   │
│  │              Latency: 1-10ms                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Disk/SSD Storage                       │   │
│  │           Archive and cold storage                        │   │
│  │              Latency: 10-100ms                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Cloud Storage                          │   │
│  │           Remote/backup storage                           │   │
│  │              Latency: 100ms+                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Persistence Mechanisms

```python
class NVMStorageEngine:
    """Storage engine for NVM"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.backends = {
            'hot': RAMCache(size_mb=config.hot_cache_mb),
            'primary': NVMeStorage(path=config.nvme_path),
            'archive': DiskStorage(path=config.archive_path),
            'cloud': CloudStorage(config=config.cloud_config) if config.cloud_enabled else None
        }
        self.placement_policy = TieredPlacementPolicy()
    
    def store(self, block: NVMBlock, tier: str = 'auto') -> str:
        """Store block at appropriate tier"""
        if tier == 'auto':
            tier = self.placement_policy.select_tier(block)
        
        # Serialize block
        serialized = self._serialize(block)
        
        # Store at selected tier
        backend = self.backends[tier]
        storage_id = backend.write(block.id, serialized)
        
        # Add to hot cache if frequently accessed
        if block.access_count > 10:
            self.backends['hot'].put(block.id, serialized)
        
        return storage_id
    
    def retrieve(self, block_id: str) -> Optional[NVMBlock]:
        """Retrieve block (checking tiers in order)"""
        # Check hot cache first
        cached = self.backends['hot'].get(block_id)
        if cached:
            return self._deserialize(cached)
        
        # Check primary storage
        primary = self.backends['primary'].read(block_id)
        if primary:
            block = self._deserialize(primary)
            # Promote to cache
            self.backends['hot'].put(block_id, primary)
            return block
        
        # Check archive
        archived = self.backends['archive'].read(block_id)
        if archived:
            block = self._deserialize(archived)
            # Promote to primary
            self.backends['primary'].write(block_id, archived)
            return block
        
        # Check cloud
        if self.backends['cloud']:
            cloud = self.backends['cloud'].read(block_id)
            if cloud:
                block = self._deserialize(cloud)
                # Promote to primary
                self.backends['primary'].write(block_id, cloud)
                return block
        
        return None
    
    def _serialize(self, block: NVMBlock) -> bytes:
        """Serialize block to bytes"""
        data = {
            'id': block.id,
            'name': block.name,
            'block_class': block.block_class.value,
            'version': block.version,
            'created_at': block.created_at.isoformat(),
            'updated_at': block.updated_at.isoformat(),
            'readonly': block.readonly,
            'content_type': block.content_type,
            'content': block.content,
            'metadata': block.metadata,
            'tags': block.tags
        }
        return msgpack.packb(data)
    
    def _deserialize(self, data: bytes) -> NVMBlock:
        """Deserialize bytes to block"""
        parsed = msgpack.unpackb(data)
        return NVMBlock(
            id=parsed['id'],
            name=parsed['name'],
            block_class=BlockClass(parsed['block_class']),
            version=parsed['version'],
            created_at=datetime.fromisoformat(parsed['created_at']),
            updated_at=datetime.fromisoformat(parsed['updated_at']),
            readonly=parsed['readonly'],
            content_type=parsed['content_type'],
            content=parsed['content'],
            metadata=parsed['metadata'],
            tags=parsed['tags']
        )
```

### Durability Guarantees

```python
class DurabilityManager:
    """Manage NVM durability guarantees"""
    
    LEVELS = {
        'memory': 0,        # RAM only (fastest, no durability)
        'buffered': 1,      # Buffered writes
        'sync': 2,          # Sync to NVMe
        'replicated': 3,    # Replicated to multiple nodes
        'geo_replicated': 4 # Geo-replicated
    }
    
    def __init__(self, storage: NVMStorageEngine, default_level: str = 'sync'):
        self.storage = storage
        self.default_level = default_level
        self.write_buffer = []
        self.buffer_flush_interval = 1.0  # seconds
    
    def write(self, block: NVMBlock, durability: str = None):
        """Write block with specified durability"""
        durability = durability or self.default_level
        
        if durability == 'memory':
            return self._write_memory_only(block)
        elif durability == 'buffered':
            return self._write_buffered(block)
        elif durability == 'sync':
            return self._write_sync(block)
        elif durability == 'replicated':
            return self._write_replicated(block)
        elif durability == 'geo_replicated':
            return self._write_geo_replicated(block)
    
    def _write_sync(self, block: NVMBlock):
        """Write with immediate sync to disk"""
        storage_id = self.storage.store(block, tier='primary')
        self.storage.backends['primary'].sync()
        return storage_id
    
    def _write_replicated(self, block: NVMBlock):
        """Write with replication to multiple nodes"""
        storage_id = self._write_sync(block)
        
        # Replicate to mirrors
        for mirror in self.storage.mirrors:
            mirror.write(block.id, self.storage._serialize(block))
        
        return storage_id
    
    async def flush_buffer(self):
        """Flush write buffer periodically"""
        while True:
            await asyncio.sleep(self.buffer_flush_interval)
            
            if self.write_buffer:
                batch = self.write_buffer[:]
                self.write_buffer.clear()
                
                for block in batch:
                    self._write_sync(block)
```

### Storage Formats

```python
class StorageFormat:
    """NVM storage format specification"""
    
    # Block file format:
    # [Header: 64 bytes][Content: variable][Vectors: variable][Metadata: variable]
    
    HEADER_SIZE = 64
    MAGIC_NUMBER = b'NVM1'
    
    @staticmethod
    def encode_header(block: NVMBlock) -> bytes:
        """Encode block header"""
        header = struct.pack(
            '!4sI32sIQQB7x',  # Format string
            StorageFormat.MAGIC_NUMBER,
            block.version,
            block.id.encode('utf-8')[:32],
            len(block.content),
            int(block.created_at.timestamp()),
            int(block.updated_at.timestamp()),
            1 if block.readonly else 0
        )
        return header.ljust(StorageFormat.HEADER_SIZE, b'\x00')
    
    @staticmethod
    def decode_header(data: bytes) -> Dict:
        """Decode block header"""
        magic, version, block_id, content_len, created, updated, readonly = \
            struct.unpack('!4sI32sIQQB7x', data[:StorageFormat.HEADER_SIZE])
        
        if magic != StorageFormat.MAGIC_NUMBER:
            raise ValueError("Invalid NVM block format")
        
        return {
            'version': version,
            'id': block_id.rstrip(b'\x00').decode('utf-8'),
            'content_length': content_len,
            'created_at': datetime.fromtimestamp(created),
            'updated_at': datetime.fromtimestamp(updated),
            'readonly': bool(readonly)
        }
```

### Compression and Optimization

```python
class CompressionManager:
    """Manage NVM content compression"""
    
    ALGORITHMS = {
        'none': lambda x: x,
        'lz4': lz4.frame.compress,
        'zstd': zstd.compress,
        'gzip': gzip.compress
    }
    
    DECOMPRESS = {
        'none': lambda x: x,
        'lz4': lz4.frame.decompress,
        'zstd': zstd.decompress,
        'gzip': gzip.decompress
    }
    
    def __init__(self, default_algorithm: str = 'lz4'):
        self.default_algorithm = default_algorithm
    
    def compress(self, data: bytes, algorithm: str = None) -> Tuple[bytes, str]:
        """Compress data"""
        algorithm = algorithm or self.default_algorithm
        
        # Don't compress small data
        if len(data) < 1024:
            return data, 'none'
        
        compressed = self.ALGORITHMS[algorithm](data)
        
        # Only use if actually smaller
        if len(compressed) < len(data) * 0.9:
            return compressed, algorithm
        else:
            return data, 'none'
    
    def decompress(self, data: bytes, algorithm: str) -> bytes:
        """Decompress data"""
        return self.DECOMPRESS[algorithm](data)
    
    def auto_select_algorithm(self, content_type: str) -> str:
        """Select best algorithm for content type"""
        if content_type.startswith('text/'):
            return 'zstd'  # Best for text
        elif content_type == 'application/json':
            return 'lz4'   # Fast, good for JSON
        else:
            return 'lz4'   # Default to fast
```

---

## Geometric Consistency

### Same Representation for All Models

All models see the same geometric representation of NVM content:

```
┌─────────────────────────────────────────────────────────────────┐
│              Geometric Consistency Guarantee                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│  │ Model A │    │ Model B │    │ Model C │    │ Model D │      │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘      │
│       │              │              │              │             │
│       │    Same geometric interface │              │             │
│       │              │              │              │             │
│       ▼              ▼              ▼              ▼             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   NVM Block (Read-Only)                   │   │
│  │                                                           │   │
│  │  Geometric Position: [1.5, 0.3, -0.2, ...] on H⁴         │   │
│  │  Content: "HyperSync Documentation..."                    │   │
│  │  Vector: [0.123, -0.456, 0.789, ...]                     │   │
│  │                                                           │   │
│  │  All models see IDENTICAL:                                │   │
│  │  - Geometric coordinates                                  │   │
│  │  - Distances to other blocks                              │   │
│  │  - Semantic relationships                                 │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Consistent Interface

```python
class ConsistentNVMInterface:
    """Ensure consistent NVM access across all models"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
        self._geometry_cache = {}
    
    def get_block_geometry(self, block_id: str) -> GeometricView:
        """Get consistent geometric view of block"""
        if block_id in self._geometry_cache:
            return self._geometry_cache[block_id]
        
        block = self.nvm.get_block(block_id)
        
        view = GeometricView(
            block_id=block_id,
            position=block.manifold_positions[0],
            geometry=block.geometry,
            curvature=self._get_curvature(block.geometry),
            vector=block.vectors[0] if block.vectors else None
        )
        
        self._geometry_cache[block_id] = view
        return view
    
    def compute_distance(self, block_id_1: str, block_id_2: str) -> float:
        """Compute consistent distance between blocks"""
        geo1 = self.get_block_geometry(block_id_1)
        geo2 = self.get_block_geometry(block_id_2)
        
        # Must be in same geometry for distance
        if geo1.geometry != geo2.geometry:
            raise GeometryMismatchError(
                f"Cannot compute distance between {geo1.geometry} and {geo2.geometry}"
            )
        
        return self._geodesic_distance(geo1.position, geo2.position, geo1.geometry)
    
    def get_neighborhood(self, block_id: str, radius: float) -> List[str]:
        """Get blocks within consistent geometric neighborhood"""
        center = self.get_block_geometry(block_id)
        
        neighbors = []
        for other_block in self.nvm.list_blocks():
            if other_block.id == block_id:
                continue
            
            try:
                distance = self.compute_distance(block_id, other_block.id)
                if distance <= radius:
                    neighbors.append(other_block.id)
            except GeometryMismatchError:
                pass  # Skip blocks in different geometry
        
        return neighbors
```

### Unified Access Patterns

```python
class UnifiedAccessPattern:
    """Unified access pattern for all models"""
    
    def __init__(self, nvm: 'NVM', hvs: HVS):
        self.nvm = nvm
        self.hvs = hvs
    
    def query(self, query: str, model_id: str = None) -> List[NVMBlock]:
        """Standard query pattern for any model"""
        # Same query logic regardless of which model is querying
        results = self.nvm.semantic_query(query)
        
        # Log access (but don't affect results)
        if model_id:
            self._log_access(model_id, query, results)
        
        return results
    
    def read_block(self, block_id: str, model_id: str = None) -> NVMBlock:
        """Standard read pattern for any model"""
        block = self.nvm.get_block(block_id)
        
        if model_id:
            self._log_access(model_id, f"read:{block_id}", [block])
        
        return block
    
    def get_distances(self, block_id: str, other_ids: List[str]) -> Dict[str, float]:
        """Get distances consistently for any model"""
        interface = ConsistentNVMInterface(self.nvm)
        
        distances = {}
        for other_id in other_ids:
            try:
                distances[other_id] = interface.compute_distance(block_id, other_id)
            except GeometryMismatchError:
                distances[other_id] = float('inf')
        
        return distances
```

### Geometric Invariants

```python
class GeometricInvariants:
    """Invariants that hold for all NVM access"""
    
    @staticmethod
    def triangle_inequality(nvm: 'NVM', a_id: str, b_id: str, c_id: str) -> bool:
        """Verify triangle inequality holds"""
        interface = ConsistentNVMInterface(nvm)
        
        d_ab = interface.compute_distance(a_id, b_id)
        d_bc = interface.compute_distance(b_id, c_id)
        d_ac = interface.compute_distance(a_id, c_id)
        
        return d_ac <= d_ab + d_bc + 1e-10  # Tolerance for numerical error
    
    @staticmethod
    def symmetry(nvm: 'NVM', a_id: str, b_id: str) -> bool:
        """Verify distance symmetry"""
        interface = ConsistentNVMInterface(nvm)
        
        d_ab = interface.compute_distance(a_id, b_id)
        d_ba = interface.compute_distance(b_id, a_id)
        
        return abs(d_ab - d_ba) < 1e-10
    
    @staticmethod
    def identity(nvm: 'NVM', a_id: str) -> bool:
        """Verify distance to self is zero"""
        interface = ConsistentNVMInterface(nvm)
        
        d_aa = interface.compute_distance(a_id, a_id)
        
        return d_aa < 1e-10
```

---

## Multi-Manifold Support

### Shared Block Access

NVM blocks can be shared across multiple manifolds:

```
┌─────────────────────────────────────────────────────────────────┐
│                  Multi-Manifold Block Sharing                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐              │
│  │   Manifold A     │         │   Manifold B     │              │
│  │                  │         │                  │              │
│  │  ┌───────────┐   │         │   ┌───────────┐  │              │
│  │  │  Block 1  │───┼─────────┼───│  Block 1  │  │  ◀─ Shared  │
│  │  └───────────┘   │         │   └───────────┘  │              │
│  │                  │         │                  │              │
│  │  ┌───────────┐   │         │   ┌───────────┐  │              │
│  │  │  Block 2  │   │         │   │  Block 3  │  │  ◀─ Local   │
│  │  └───────────┘   │         │   └───────────┘  │              │
│  │                  │         │                  │              │
│  └──────────────────┘         └──────────────────┘              │
│                                                                  │
│           ┌──────────────────────────────┐                      │
│           │     Shared NVM Storage       │                      │
│           │  ┌────────────────────────┐  │                      │
│           │  │       Block 1          │  │                      │
│           │  │  (shared, read-only)   │  │                      │
│           │  └────────────────────────┘  │                      │
│           └──────────────────────────────┘                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Cross-Manifold Bridging

```python
class CrossManifoldBridge:
    """Bridge NVM blocks across manifolds"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
        self.manifold_blocks = {}  # manifold_id -> set(block_id)
        self.shared_blocks = set()  # blocks shared across manifolds
    
    def register_manifold(self, manifold_id: str):
        """Register a manifold"""
        self.manifold_blocks[manifold_id] = set()
    
    def assign_block(self, block_id: str, manifold_id: str):
        """Assign block to manifold"""
        if manifold_id not in self.manifold_blocks:
            self.register_manifold(manifold_id)
        
        self.manifold_blocks[manifold_id].add(block_id)
    
    def share_block(self, block_id: str, manifold_ids: List[str]):
        """Share block across multiple manifolds"""
        for manifold_id in manifold_ids:
            self.assign_block(block_id, manifold_id)
        
        self.shared_blocks.add(block_id)
        
        # Mark as shared in block metadata
        block = self.nvm.get_block(block_id)
        block.metadata['shared_manifolds'] = manifold_ids
    
    def get_manifold_blocks(self, manifold_id: str) -> List[NVMBlock]:
        """Get all blocks accessible to manifold"""
        block_ids = self.manifold_blocks.get(manifold_id, set())
        return [self.nvm.get_block(bid) for bid in block_ids]
    
    def is_shared(self, block_id: str) -> bool:
        """Check if block is shared"""
        return block_id in self.shared_blocks
    
    def get_sharing_manifolds(self, block_id: str) -> List[str]:
        """Get manifolds sharing this block"""
        manifolds = []
        for mid, blocks in self.manifold_blocks.items():
            if block_id in blocks:
                manifolds.append(mid)
        return manifolds
```

### Slow Bridge Functionality

NVM can act as a slow bridge between manifolds:

```python
class SlowBridge:
    """NVM as slow bridge between manifolds"""
    
    def __init__(self, nvm: 'NVM', source_hvs: HVS, target_hvs: HVS):
        self.nvm = nvm
        self.source = source_hvs
        self.target = target_hvs
        self.bridge_blocks = {}  # Used for inter-manifold communication
    
    def create_bridge_block(self, name: str) -> NVMBlock:
        """Create a block for inter-manifold bridging"""
        block = self.nvm.create_block(
            name=name,
            block_class=BlockClass.SHARED_KNOWLEDGE,
            readonly=False
        )
        self.bridge_blocks[name] = block.id
        return block
    
    def send_via_bridge(self, bridge_name: str, data: Any):
        """Send data through slow bridge"""
        block_id = self.bridge_blocks[bridge_name]
        block = self.nvm.get_block(block_id)
        
        # Add to bridge queue
        queue = block.metadata.get('queue', [])
        queue.append({
            'data': data,
            'timestamp': time.time(),
            'source_manifold': self.source.id
        })
        block.metadata['queue'] = queue
        
        # Update block
        self.nvm.update_block(block_id, metadata=block.metadata)
        
        # Index new content in target HVS
        self._index_in_target(block, data)
    
    def receive_via_bridge(self, bridge_name: str) -> List[Dict]:
        """Receive data from slow bridge"""
        block_id = self.bridge_blocks[bridge_name]
        block = self.nvm.get_block(block_id)
        
        queue = block.metadata.get('queue', [])
        
        # Filter for messages to this manifold
        messages = [m for m in queue if m.get('target_manifold') == self.target.id]
        
        return messages
    
    def _index_in_target(self, block: NVMBlock, data: Any):
        """Index bridged content in target manifold's HVS"""
        vector = self._encode_data(data)
        self.target.store_vector(
            vector=vector,
            metadata={
                'bridge_block_id': block.id,
                'bridged': True,
                'source_manifold': self.source.id
            }
        )
```

### Synchronization Between Manifolds

```python
class ManifoldSynchronizer:
    """Synchronize NVM blocks between manifolds"""
    
    def __init__(self, nvm: 'NVM', bridge: CrossManifoldBridge):
        self.nvm = nvm
        self.bridge = bridge
        self.sync_log = []
    
    def sync_shared_blocks(self):
        """Synchronize all shared blocks"""
        for block_id in self.bridge.shared_blocks:
            manifolds = self.bridge.get_sharing_manifolds(block_id)
            
            # Get latest version
            block = self.nvm.get_block(block_id)
            
            # Update index in all manifolds
            for manifold_id in manifolds:
                self._update_manifold_index(manifold_id, block)
            
            self.sync_log.append({
                'block_id': block_id,
                'manifolds': manifolds,
                'version': block.version,
                'timestamp': time.time()
            })
    
    def _update_manifold_index(self, manifold_id: str, block: NVMBlock):
        """Update block index in manifold's HVS"""
        hvs = self._get_hvs_for_manifold(manifold_id)
        
        # Re-index block
        for i, vector in enumerate(block.vectors):
            hvs.store_vector(
                id=f"{block.id}:chunk:{i}",
                vector=vector,
                metadata={
                    'block_id': block.id,
                    'chunk_index': i,
                    'synced_at': time.time()
                }
            )
    
    def get_sync_status(self, block_id: str) -> Dict:
        """Get synchronization status for block"""
        relevant_logs = [
            log for log in self.sync_log 
            if log['block_id'] == block_id
        ]
        
        if not relevant_logs:
            return {'status': 'never_synced'}
        
        last_sync = relevant_logs[-1]
        block = self.nvm.get_block(block_id)
        
        if block.version > last_sync['version']:
            return {'status': 'out_of_sync', 'last_synced_version': last_sync['version']}
        else:
            return {'status': 'synced', 'last_sync': last_sync['timestamp']}
```

### Consistency Across Manifolds

```python
class CrossManifoldConsistency:
    """Ensure consistency across manifolds"""
    
    def __init__(self, nvm: 'NVM', bridge: CrossManifoldBridge):
        self.nvm = nvm
        self.bridge = bridge
    
    def verify_consistency(self, block_id: str) -> Dict:
        """Verify block is consistent across all manifolds"""
        manifolds = self.bridge.get_sharing_manifolds(block_id)
        
        if len(manifolds) < 2:
            return {'consistent': True, 'message': 'Block not shared'}
        
        # Get block hash from each manifold's perspective
        hashes = {}
        for manifold_id in manifolds:
            hvs = self._get_hvs_for_manifold(manifold_id)
            vectors = hvs.get_vectors_for_block(block_id)
            hashes[manifold_id] = self._compute_vector_hash(vectors)
        
        # Check all hashes match
        unique_hashes = set(hashes.values())
        if len(unique_hashes) == 1:
            return {'consistent': True, 'manifolds': manifolds}
        else:
            return {
                'consistent': False,
                'manifolds': manifolds,
                'hashes': hashes,
                'message': 'Vector representations differ across manifolds'
            }
    
    def repair_inconsistency(self, block_id: str):
        """Repair inconsistent block across manifolds"""
        manifolds = self.bridge.get_sharing_manifolds(block_id)
        
        # Use source block as truth
        block = self.nvm.get_block(block_id)
        
        # Re-index in all manifolds
        for manifold_id in manifolds:
            hvs = self._get_hvs_for_manifold(manifold_id)
            
            # Remove old vectors
            hvs.delete_vectors_for_block(block_id)
            
            # Re-index
            for i, vector in enumerate(block.vectors):
                hvs.store_vector(
                    id=f"{block_id}:chunk:{i}",
                    vector=vector,
                    metadata={'block_id': block_id, 'chunk_index': i}
                )
```

---

## Access Control

### Read-Only Blocks

```python
class ReadOnlyEnforcer:
    """Enforce read-only access for certain blocks"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
    
    def check_write_permission(self, block_id: str, model_id: str) -> bool:
        """Check if model can write to block"""
        block = self.nvm.get_block(block_id)
        
        if block.readonly:
            return False
        
        # Check permissions
        if model_id in block.permissions.get('write', []):
            return True
        
        if '*' in block.permissions.get('write', []):
            return True
        
        return False
    
    def create_readonly_block(self, name: str, content: Any) -> NVMBlock:
        """Create a read-only block"""
        return self.nvm.create_block(
            name=name,
            block_class=BlockClass.DOCUMENTATION,
            content=content,
            readonly=True,
            permissions={
                'read': ['*'],  # All can read
                'write': []     # None can write
            }
        )
```

### Read-Write Blocks

```python
class ReadWriteController:
    """Control read-write access to blocks"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
        self.access_log = []
    
    def grant_write_access(self, block_id: str, model_id: str):
        """Grant write access to model"""
        block = self.nvm.get_block(block_id)
        
        if block.readonly:
            raise ReadOnlyBlockError(f"Cannot grant write access to read-only block")
        
        writers = block.permissions.get('write', [])
        if model_id not in writers:
            writers.append(model_id)
            block.permissions['write'] = writers
            self.nvm.update_block_metadata(block_id, {'permissions': block.permissions})
    
    def revoke_write_access(self, block_id: str, model_id: str):
        """Revoke write access from model"""
        block = self.nvm.get_block(block_id)
        
        writers = block.permissions.get('write', [])
        if model_id in writers:
            writers.remove(model_id)
            block.permissions['write'] = writers
            self.nvm.update_block_metadata(block_id, {'permissions': block.permissions})
    
    def write(self, block_id: str, model_id: str, content: Any):
        """Write to block with access check"""
        if not self.nvm.enforcer.check_write_permission(block_id, model_id):
            raise PermissionDeniedError(f"Model {model_id} cannot write to block {block_id}")
        
        self.nvm.update_block(block_id, content)
        
        self.access_log.append({
            'block_id': block_id,
            'model_id': model_id,
            'action': 'write',
            'timestamp': time.time()
        })
```

### Permission System

```python
@dataclass
class Permission:
    """NVM permission structure"""
    read: List[str]      # Model IDs that can read
    write: List[str]     # Model IDs that can write
    admin: List[str]     # Model IDs that can change permissions
    inherit: bool = True # Inherit from parent block

class PermissionManager:
    """Manage NVM permissions"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
    
    def set_permissions(self, block_id: str, permissions: Permission):
        """Set permissions for block"""
        block = self.nvm.get_block(block_id)
        block.permissions = {
            'read': permissions.read,
            'write': permissions.write,
            'admin': permissions.admin
        }
        self.nvm.update_block_metadata(block_id, {'permissions': block.permissions})
    
    def check_permission(self, block_id: str, model_id: str, 
                         action: str) -> bool:
        """Check if model has permission for action"""
        block = self.nvm.get_block(block_id)
        
        # Check direct permission
        allowed = block.permissions.get(action, [])
        if model_id in allowed or '*' in allowed:
            return True
        
        # Check admin (admins can do anything)
        admins = block.permissions.get('admin', [])
        if model_id in admins or '*' in admins:
            return True
        
        return False
    
    def create_permission_template(self, template_name: str) -> Permission:
        """Create common permission templates"""
        templates = {
            'public_read': Permission(read=['*'], write=[], admin=[]),
            'model_private': Permission(read=['owner'], write=['owner'], admin=['owner']),
            'shared_write': Permission(read=['*'], write=['*'], admin=[]),
            'documentation': Permission(read=['*'], write=[], admin=['system'])
        }
        return templates.get(template_name)
```

### Security Model

```python
class NVMSecurityModel:
    """Security model for NVM"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
        self.audit_log = []
    
    def validate_access(self, request: AccessRequest) -> bool:
        """Validate access request"""
        # Check model identity
        if not self._verify_model(request.model_id):
            self._log_security_event('invalid_model', request)
            return False
        
        # Check permission
        if not self._check_permission(request):
            self._log_security_event('permission_denied', request)
            return False
        
        # Check rate limits
        if not self._check_rate_limit(request):
            self._log_security_event('rate_limited', request)
            return False
        
        return True
    
    def _verify_model(self, model_id: str) -> bool:
        """Verify model identity"""
        # Check model is registered
        return model_id in self.nvm.registered_models
    
    def _check_rate_limit(self, request: AccessRequest) -> bool:
        """Check rate limits"""
        # Get recent requests from this model
        recent = [
            r for r in self.audit_log
            if r['model_id'] == request.model_id
            and r['timestamp'] > time.time() - 60  # Last minute
        ]
        
        if request.action == 'write':
            return len(recent) < 100  # 100 writes/minute
        else:
            return len(recent) < 1000  # 1000 reads/minute
    
    def _log_security_event(self, event_type: str, request: AccessRequest):
        """Log security event"""
        self.audit_log.append({
            'event_type': event_type,
            'model_id': request.model_id,
            'block_id': request.block_id,
            'action': request.action,
            'timestamp': time.time()
        })
```

### Isolation Guarantees

```python
class IsolationManager:
    """Manage isolation between blocks and models"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
        self.isolation_policies = {}
    
    def set_isolation_policy(self, block_id: str, policy: str):
        """Set isolation policy for block"""
        policies = {
            'strict': self._strict_isolation,
            'shared': self._shared_isolation,
            'public': self._public_isolation
        }
        self.isolation_policies[block_id] = policies[policy]
    
    def _strict_isolation(self, block_id: str, model_id: str) -> bool:
        """Strict isolation: only owner can access"""
        block = self.nvm.get_block(block_id)
        return block.metadata.get('owner') == model_id
    
    def _shared_isolation(self, block_id: str, model_id: str) -> bool:
        """Shared isolation: explicit permission required"""
        block = self.nvm.get_block(block_id)
        return model_id in block.permissions.get('read', [])
    
    def _public_isolation(self, block_id: str, model_id: str) -> bool:
        """Public isolation: all can read"""
        return True
    
    def check_isolation(self, block_id: str, model_id: str) -> bool:
        """Check if model can access block under isolation policy"""
        policy = self.isolation_policies.get(block_id, self._public_isolation)
        return policy(block_id, model_id)
```

---

## Block Classes

### 1. Documentation Blocks (Read-Only)

```python
class DocumentationBlockManager:
    """Manage documentation blocks"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
    
    def create_documentation(self, name: str, markdown_content: str) -> NVMBlock:
        """Create documentation block from markdown"""
        block = self.nvm.create_block(
            name=name,
            block_class=BlockClass.DOCUMENTATION,
            content=markdown_content.encode('utf-8'),
            content_type='text/markdown',
            readonly=True,
            permissions={'read': ['*'], 'write': [], 'admin': ['system']}
        )
        return block
    
    def load_documentation_directory(self, dir_path: str):
        """Load all markdown files from directory as documentation blocks"""
        for filename in os.listdir(dir_path):
            if filename.endswith('.md'):
                filepath = os.path.join(dir_path, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                name = filename.replace('.md', '')
                self.create_documentation(name, content)
    
    def query_documentation(self, query: str, k: int = 5) -> List[Dict]:
        """Query documentation blocks"""
        return self.nvm.query_interface.query_documentation(query, k=k)

# Example: HyperSync documentation
doc_manager = DocumentationBlockManager(nvm)
doc_manager.create_documentation(
    name="hypersync_overview",
    markdown_content="""
# HyperSync Overview

HyperSync is a distributed AI coordination system using hyperbolic geometry...

## Key Components

- HVS: Hyper Vector System
- NVM: Non-Volatile Memory
- SDL: Schema Definition Language
    """
)
```

### 2. Program State Blocks

```python
class ProgramStateManager:
    """Manage program state blocks"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
    
    def create_state_block(self, name: str, model_id: str,
                          initial_state: Dict = None) -> NVMBlock:
        """Create state block for model"""
        block = self.nvm.create_block(
            name=name,
            block_class=BlockClass.PROGRAM_STATE,
            content=msgpack.packb(initial_state or {}),
            content_type='application/msgpack',
            readonly=False,
            permissions={
                'read': [model_id],
                'write': [model_id],
                'admin': [model_id]
            },
            metadata={'owner': model_id}
        )
        return block
    
    def update_state(self, block_id: str, key: str, value: Any):
        """Update state value"""
        block = self.nvm.get_block(block_id)
        state = msgpack.unpackb(block.content)
        state[key] = value
        self.nvm.update_block(block_id, msgpack.packb(state))
    
    def get_state(self, block_id: str, key: str = None) -> Any:
        """Get state value(s)"""
        block = self.nvm.get_block(block_id)
        state = msgpack.unpackb(block.content)
        
        if key:
            return state.get(key)
        return state
    
    def checkpoint(self, block_id: str) -> str:
        """Create checkpoint of current state"""
        block = self.nvm.get_block(block_id)
        
        checkpoint_name = f"{block.name}_checkpoint_{block.version}"
        checkpoint = self.nvm.create_block(
            name=checkpoint_name,
            block_class=BlockClass.PROGRAM_STATE,
            content=block.content,
            readonly=True,  # Checkpoint is immutable
            metadata={
                'checkpoint_of': block_id,
                'version': block.version
            }
        )
        return checkpoint.id
```

### 3. Knowledge Graph Blocks

```python
class KnowledgeGraphManager:
    """Manage knowledge graph blocks"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
    
    def create_knowledge_graph(self, name: str) -> NVMBlock:
        """Create empty knowledge graph block"""
        initial_graph = {'nodes': {}, 'edges': []}
        
        block = self.nvm.create_block(
            name=name,
            block_class=BlockClass.KNOWLEDGE_GRAPH,
            content=msgpack.packb(initial_graph),
            content_type='application/msgpack',
            readonly=False
        )
        return block
    
    def add_node(self, block_id: str, node_id: str, 
                 label: str, properties: Dict = None):
        """Add node to knowledge graph"""
        block = self.nvm.get_block(block_id)
        graph = msgpack.unpackb(block.content)
        
        graph['nodes'][node_id] = {
            'label': label,
            'properties': properties or {}
        }
        
        self.nvm.update_block(block_id, msgpack.packb(graph))
    
    def add_edge(self, block_id: str, source: str, target: str,
                 relation: str, properties: Dict = None):
        """Add edge to knowledge graph"""
        block = self.nvm.get_block(block_id)
        graph = msgpack.unpackb(block.content)
        
        graph['edges'].append({
            'source': source,
            'target': target,
            'relation': relation,
            'properties': properties or {}
        })
        
        self.nvm.update_block(block_id, msgpack.packb(graph))
    
    def query_graph(self, block_id: str, query: str) -> Dict:
        """Query knowledge graph semantically"""
        # Encode query
        query_vector = self.nvm.encoder.encode(query)
        
        # Get block
        block = self.nvm.get_block(block_id)
        graph = msgpack.unpackb(block.content)
        
        # Find relevant nodes
        relevant_nodes = []
        for node_id, node in graph['nodes'].items():
            node_text = f"{node['label']} {str(node['properties'])}"
            node_vector = self.nvm.encoder.encode(node_text)
            similarity = self._cosine_similarity(query_vector, node_vector)
            if similarity > 0.5:
                relevant_nodes.append((node_id, node, similarity))
        
        relevant_nodes.sort(key=lambda x: x[2], reverse=True)
        
        # Get induced subgraph
        node_ids = {n[0] for n in relevant_nodes[:10]}
        relevant_edges = [
            e for e in graph['edges']
            if e['source'] in node_ids or e['target'] in node_ids
        ]
        
        return {
            'nodes': relevant_nodes[:10],
            'edges': relevant_edges
        }
```

### 4. Cache Blocks

```python
class CacheBlockManager:
    """Manage cache blocks with TTL"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
    
    def create_cache(self, name: str, ttl_seconds: int = 3600) -> NVMBlock:
        """Create cache block"""
        initial_cache = {'entries': {}, 'expiry': {}}
        
        block = self.nvm.create_block(
            name=name,
            block_class=BlockClass.CACHE,
            content=msgpack.packb(initial_cache),
            content_type='application/msgpack',
            readonly=False,
            metadata={'ttl_seconds': ttl_seconds}
        )
        return block
    
    def set(self, block_id: str, key: str, value: Any,
            vector: np.ndarray = None):
        """Set cache entry"""
        block = self.nvm.get_block(block_id)
        cache = msgpack.unpackb(block.content)
        ttl = block.metadata.get('ttl_seconds', 3600)
        
        cache['entries'][key] = {
            'value': value,
            'vector': vector.tolist() if vector is not None else None,
            'created_at': time.time()
        }
        cache['expiry'][key] = time.time() + ttl
        
        self.nvm.update_block(block_id, msgpack.packb(cache))
    
    def get(self, block_id: str, key: str) -> Optional[Any]:
        """Get cache entry if not expired"""
        block = self.nvm.get_block(block_id)
        cache = msgpack.unpackb(block.content)
        
        if key not in cache['entries']:
            return None
        
        if time.time() > cache['expiry'].get(key, 0):
            # Expired
            self._remove_entry(block_id, key)
            return None
        
        return cache['entries'][key]['value']
    
    def semantic_get(self, block_id: str, query_vector: np.ndarray,
                     threshold: float = 0.8) -> Optional[Any]:
        """Get cache entry by semantic similarity"""
        block = self.nvm.get_block(block_id)
        cache = msgpack.unpackb(block.content)
        
        best_match = None
        best_score = 0
        
        for key, entry in cache['entries'].items():
            if entry['vector'] is None:
                continue
            
            if time.time() > cache['expiry'].get(key, 0):
                continue
            
            score = self._cosine_similarity(
                query_vector,
                np.array(entry['vector'])
            )
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = entry['value']
        
        return best_match
    
    def cleanup_expired(self, block_id: str) -> int:
        """Remove expired entries"""
        block = self.nvm.get_block(block_id)
        cache = msgpack.unpackb(block.content)
        
        current_time = time.time()
        expired_keys = [
            k for k, exp in cache['expiry'].items()
            if current_time > exp
        ]
        
        for key in expired_keys:
            del cache['entries'][key]
            del cache['expiry'][key]
        
        self.nvm.update_block(block_id, msgpack.packb(cache))
        return len(expired_keys)
```

### 5. Custom Block Types

```python
class CustomBlockManager:
    """Manage custom block types"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
        self.custom_handlers = {}
    
    def register_custom_type(self, type_name: str, 
                             handler: 'CustomBlockHandler'):
        """Register custom block type handler"""
        self.custom_handlers[type_name] = handler
    
    def create_custom_block(self, name: str, type_name: str,
                           content: Any, **kwargs) -> NVMBlock:
        """Create custom block"""
        handler = self.custom_handlers.get(type_name)
        
        if handler:
            processed_content = handler.process_content(content)
            metadata = handler.get_metadata(content)
        else:
            processed_content = msgpack.packb(content)
            metadata = {}
        
        block = self.nvm.create_block(
            name=name,
            block_class=BlockClass.CUSTOM,
            content=processed_content,
            metadata={**metadata, 'custom_type': type_name},
            **kwargs
        )
        return block
    
    def get_custom_block(self, block_id: str) -> Tuple[NVMBlock, Any]:
        """Get custom block with processed content"""
        block = self.nvm.get_block(block_id)
        type_name = block.metadata.get('custom_type')
        
        handler = self.custom_handlers.get(type_name)
        if handler:
            content = handler.parse_content(block.content)
        else:
            content = msgpack.unpackb(block.content)
        
        return block, content

# Example custom handler
class ConversationHandler(CustomBlockHandler):
    """Handle conversation blocks"""
    
    def process_content(self, content: List[Dict]) -> bytes:
        return msgpack.packb(content)
    
    def parse_content(self, data: bytes) -> List[Dict]:
        return msgpack.unpackb(data)
    
    def get_metadata(self, content: List[Dict]) -> Dict:
        return {
            'message_count': len(content),
            'participants': list(set(m.get('role') for m in content))
        }
```

---

## Use Cases

### 1. HyperSync Documentation Storage

```python
# Create documentation blocks for all HyperSync docs
doc_manager = DocumentationBlockManager(nvm)

# Load documentation
doc_manager.create_documentation(
    "hvs_specification",
    open("HVS_CORE_SPECIFICATION.md").read()
)
doc_manager.create_documentation(
    "nvm_specification",
    open("NVM_SPECIFICATION.md").read()
)

# Query documentation (any model can do this)
results = nvm.query_documentation("How does HVS handle synchronization?")
for result in results:
    print(f"Found in: {result['block'].name}")
    print(f"Content: {result['chunk_preview'][:200]}...")
```

### 2. Shared Knowledge Base

```python
# Create shared knowledge base
knowledge_graph = KnowledgeGraphManager(nvm)
kg_block = knowledge_graph.create_knowledge_graph("hypersync_concepts")

# Add concepts
knowledge_graph.add_node(kg_block.id, "HVS", "component", 
    {"description": "Hyper Vector System"})
knowledge_graph.add_node(kg_block.id, "NVM", "component",
    {"description": "Non-Volatile Memory"})
knowledge_graph.add_edge(kg_block.id, "HVS", "NVM", "indexes")

# Share across manifolds
bridge = CrossManifoldBridge(nvm)
bridge.share_block(kg_block.id, ["manifold_a", "manifold_b", "manifold_c"])

# Any manifold can query
results = knowledge_graph.query_graph(kg_block.id, "vector storage")
```

### 3. Project State Persistence

```python
# Create state block for project
state_manager = ProgramStateManager(nvm)
state_block = state_manager.create_state_block(
    "project_alpha_state",
    "model_a",
    initial_state={
        "phase": "development",
        "tasks_completed": [],
        "current_task": None
    }
)

# Update state as project progresses
state_manager.update_state(state_block.id, "current_task", "implement_hvs")
state_manager.update_state(state_block.id, "tasks_completed", 
    ["design", "planning"])

# Create checkpoint
checkpoint_id = state_manager.checkpoint(state_block.id)

# Restore from checkpoint if needed
# state = state_manager.restore_from_checkpoint(checkpoint_id)
```

### 4. Cross-Manifold Communication

```python
# Set up slow bridge between manifolds
slow_bridge = SlowBridge(nvm, hvs_a, hvs_b)
bridge_block = slow_bridge.create_bridge_block("ab_bridge")

# Manifold A sends message
slow_bridge.send_via_bridge("ab_bridge", {
    "type": "task_request",
    "task": "analyze_document",
    "document_id": "doc_123"
})

# Manifold B receives
messages = slow_bridge.receive_via_bridge("ab_bridge")
for msg in messages:
    if msg['data']['type'] == 'task_request':
        # Process task
        pass
```

### 5. Model Memory Extension

```python
# Create memory block for model
memory_block = nvm.create_block(
    name="model_a_memory",
    block_class=BlockClass.MODEL_MEMORY,
    readonly=False
)

# Store memories
nvm.write_to_block(memory_block.id, "model_a", {
    "conversations": [],
    "learned_facts": [],
    "preferences": {}
})

# Query memories semantically
memories = nvm.semantic_query(
    "What did the user say about hyperbolic geometry?",
    block_class=BlockClass.MODEL_MEMORY
)
```

---

## Performance Considerations

### Speed Characteristics (Disk-Speed)

NVM operates at disk/NVMe speed (slower than HVS/RAM):

| Operation | NVMe | SSD | HDD | Cloud |
|-----------|------|-----|-----|-------|
| Read block | 1-5ms | 5-20ms | 20-100ms | 100ms+ |
| Write block | 2-10ms | 10-50ms | 50-200ms | 200ms+ |
| Query (cached) | <1ms | <1ms | <1ms | <1ms |
| Query (cold) | 10-50ms | 50-200ms | 200ms+ | 500ms+ |

### Access Latency

```python
class LatencyOptimizer:
    """Optimize NVM access latency"""
    
    def __init__(self, nvm: 'NVM'):
        self.nvm = nvm
        self.access_times = {}
    
    def measure_latency(self, block_id: str) -> float:
        """Measure access latency for block"""
        start = time.time()
        _ = self.nvm.get_block(block_id)
        latency = time.time() - start
        
        self.access_times[block_id] = latency
        return latency
    
    def suggest_tier(self, block: NVMBlock) -> str:
        """Suggest optimal storage tier"""
        if block.access_count > 100:
            return 'hot'  # Frequently accessed, keep in RAM
        elif block.access_count > 10:
            return 'primary'  # Moderate access, NVMe
        elif block.status == BlockStatus.ARCHIVED:
            return 'archive'  # Rarely accessed
        else:
            return 'primary'  # Default
    
    def promote_hot_blocks(self):
        """Promote frequently accessed blocks to hot cache"""
        for block in self.nvm.list_blocks():
            if block.access_count > 100:
                self.nvm.storage.promote_to_cache(block.id)
```

### Caching Strategies

```python
class NVMCacheStrategy:
    """Caching strategies for NVM"""
    
    def __init__(self, nvm: 'NVM', cache_size_mb: int = 1024):
        self.nvm = nvm
        self.cache = LRUCache(max_size_bytes=cache_size_mb * 1024 * 1024)
        self.access_history = []
    
    def get_with_cache(self, block_id: str) -> NVMBlock:
        """Get block with caching"""
        # Check cache
        if block_id in self.cache:
            self._record_access(block_id, 'hit')
            return self.cache[block_id]
        
        # Cache miss - fetch from storage
        block = self.nvm.storage.retrieve(block_id)
        
        # Add to cache
        self._add_to_cache(block)
        self._record_access(block_id, 'miss')
        
        return block
    
    def _add_to_cache(self, block: NVMBlock):
        """Add block to cache with size check"""
        block_size = len(block.content)
        
        # Evict if necessary
        while not self.cache.has_space(block_size):
            evicted = self.cache.evict_lru()
        
        self.cache[block.id] = block
    
    def prefetch(self, block_ids: List[str]):
        """Prefetch blocks into cache"""
        for block_id in block_ids:
            if block_id not in self.cache:
                block = self.nvm.storage.retrieve(block_id)
                self._add_to_cache(block)
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        hits = sum(1 for a in self.access_history if a['type'] == 'hit')
        misses = sum(1 for a in self.access_history if a['type'] == 'miss')
        
        return {
            'hit_rate': hits / (hits + misses) if (hits + misses) > 0 else 0,
            'cache_size': self.cache.current_size,
            'cache_entries': len(self.cache),
            'total_accesses': len(self.access_history)
        }
```

### Prefetching

```python
class PrefetchManager:
    """Prefetch blocks based on access patterns"""
    
    def __init__(self, nvm: 'NVM', cache: NVMCacheStrategy):
        self.nvm = nvm
        self.cache = cache
        self.access_graph = {}  # block_id -> [next_block_ids]
    
    def record_access_sequence(self, block_ids: List[str]):
        """Record access sequence for pattern learning"""
        for i in range(len(block_ids) - 1):
            current = block_ids[i]
            next_block = block_ids[i + 1]
            
            if current not in self.access_graph:
                self.access_graph[current] = []
            self.access_graph[current].append(next_block)
    
    def predict_next(self, block_id: str, k: int = 3) -> List[str]:
        """Predict next blocks to be accessed"""
        if block_id not in self.access_graph:
            return []
        
        # Count frequencies
        next_blocks = self.access_graph[block_id]
        counts = {}
        for b in next_blocks:
            counts[b] = counts.get(b, 0) + 1
        
        # Return top k
        sorted_blocks = sorted(counts.items(), key=lambda x: -x[1])
        return [b for b, _ in sorted_blocks[:k]]
    
    async def prefetch_predicted(self, block_id: str):
        """Prefetch predicted next blocks"""
        predicted = self.predict_next(block_id)
        
        # Prefetch in background
        for pred_id in predicted:
            if pred_id not in self.cache.cache:
                asyncio.create_task(self._async_prefetch(pred_id))
    
    async def _async_prefetch(self, block_id: str):
        """Async prefetch single block"""
        try:
            block = self.nvm.storage.retrieve(block_id)
            self.cache._add_to_cache(block)
        except Exception as e:
            logging.warning(f"Prefetch failed for {block_id}: {e}")
```

### Optimization Techniques

```python
class NVMOptimizer:
    """Optimization techniques for NVM"""
    
    @staticmethod
    def optimize_for_read_heavy(nvm: 'NVM'):
        """Optimize for read-heavy workloads"""
        nvm.config.update({
            'cache_size_mb': 4096,  # Large cache
            'prefetch_enabled': True,
            'compression': 'lz4',  # Fast decompression
            'read_ahead': True
        })
    
    @staticmethod
    def optimize_for_write_heavy(nvm: 'NVM'):
        """Optimize for write-heavy workloads"""
        nvm.config.update({
            'cache_size_mb': 1024,
            'write_buffer_mb': 256,
            'compression': 'none',  # No compression overhead
            'sync_interval_seconds': 5  # Batch writes
        })
    
    @staticmethod
    def optimize_for_large_blocks(nvm: 'NVM'):
        """Optimize for large block storage"""
        nvm.config.update({
            'chunk_size_kb': 1024,
            'compression': 'zstd',  # Better compression ratio
            'streaming_enabled': True
        })
    
    @staticmethod
    def optimize_for_semantic_search(nvm: 'NVM'):
        """Optimize for semantic search workloads"""
        nvm.config.update({
            'hvs_integration': 'eager',  # Index immediately
            'vector_cache_size': 10000,
            'prefetch_similar': True
        })
```

---

## Implementation Requirements

### Core Components Needed

```
nvm/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── nvm.py                 # Main NVM class
│   ├── block.py               # Block data structure
│   ├── manager.py             # Block manager
│   └── lifecycle.py           # Lifecycle management
├── blocks/
│   ├── __init__.py
│   ├── documentation.py       # Documentation blocks
│   ├── program_state.py       # Program state blocks
│   ├── knowledge_graph.py     # Knowledge graph blocks
│   ├── cache.py               # Cache blocks
│   └── custom.py              # Custom blocks
├── hvs_integration/
│   ├── __init__.py
│   ├── index.py               # HVS indexing
│   ├── query.py               # Query interface
│   └── sync.py                # HVS synchronization
├── storage/
│   ├── __init__.py
│   ├── engine.py              # Storage engine
│   ├── nvme.py                # NVMe backend
│   ├── disk.py                # Disk backend
│   ├── cloud.py               # Cloud backend
│   └── compression.py         # Compression
├── manifold/
│   ├── __init__.py
│   ├── placer.py              # Manifold placement
│   ├── coordinates.py         # Coordinate system
│   └── spatial.py             # Spatial organization
├── multi_manifold/
│   ├── __init__.py
│   ├── bridge.py              # Cross-manifold bridge
│   ├── slow_bridge.py         # Slow bridge
│   └── sync.py                # Multi-manifold sync
├── access_control/
│   ├── __init__.py
│   ├── permissions.py         # Permission system
│   ├── readonly.py            # Read-only enforcement
│   └── security.py            # Security model
├── cache/
│   ├── __init__.py
│   ├── lru.py                 # LRU cache
│   ├── strategy.py            # Cache strategies
│   └── prefetch.py            # Prefetching
└── utils/
    ├── __init__.py
    ├── serialization.py       # Serialization utilities
    └── metrics.py             # Performance metrics
```

### Dependencies

```toml
# pyproject.toml
[project]
name = "nvm"
version = "1.0.0"
dependencies = [
    # Core
    "numpy>=1.24.0",
    
    # Serialization
    "msgpack>=1.0.0",
    "orjson>=3.8.0",
    
    # Compression
    "lz4>=4.0.0",
    "zstandard>=0.21.0",
    
    # Storage
    "aiofiles>=23.0.0",
    
    # HVS integration
    "hvs>=1.0.0",
    
    # Utilities
    "pydantic>=2.0.0",
    "structlog>=23.0.0",
]
```

### Data Structures

```python
@dataclass
class NVMConfig:
    """NVM configuration"""
    storage_path: str
    cache_size_mb: int = 1024
    compression: str = 'lz4'
    hvs_integration: str = 'eager'
    write_buffer_mb: int = 64
    sync_interval_seconds: float = 1.0

@dataclass
class BlockMetadata:
    """Block metadata structure"""
    owner: Optional[str]
    tags: List[str]
    permissions: Dict[str, List[str]]
    custom_type: Optional[str]
    manifolds: List[str]

@dataclass 
class AccessRequest:
    """Access request for security validation"""
    model_id: str
    block_id: str
    action: str  # read, write, delete, admin
    timestamp: float
```

### Storage Backend

```python
class StorageBackend(ABC):
    """Abstract storage backend"""
    
    @abstractmethod
    def write(self, block_id: str, data: bytes) -> str:
        """Write data to storage"""
        pass
    
    @abstractmethod
    def read(self, block_id: str) -> Optional[bytes]:
        """Read data from storage"""
        pass
    
    @abstractmethod
    def delete(self, block_id: str) -> bool:
        """Delete data from storage"""
        pass
    
    @abstractmethod
    def exists(self, block_id: str) -> bool:
        """Check if block exists"""
        pass
    
    @abstractmethod
    def sync(self):
        """Sync pending writes to disk"""
        pass
```

### Testing Requirements

```python
class TestNVMCore:
    """Core NVM tests"""
    
    def test_create_block(self, nvm):
        """Test block creation"""
        block = nvm.create_block("test", BlockClass.CUSTOM, b"content")
        assert block.id is not None
        assert block.name == "test"
    
    def test_readonly_enforcement(self, nvm):
        """Test read-only blocks can't be modified"""
        block = nvm.create_block("doc", BlockClass.DOCUMENTATION, 
                                 b"content", readonly=True)
        
        with pytest.raises(ReadOnlyBlockError):
            nvm.update_block(block.id, b"new content")
    
    def test_hvs_indexing(self, nvm, hvs):
        """Test blocks are indexed in HVS"""
        block = nvm.create_block("indexed", BlockClass.DOCUMENTATION,
                                 b"HyperSync is amazing")
        
        results = hvs.semantic_search(
            encoder.encode("What is HyperSync?"),
            filter={'block_id': block.id}
        )
        assert len(results) > 0

class TestMultiManifold:
    """Multi-manifold tests"""
    
    def test_shared_block(self, nvm, manifold_a, manifold_b):
        """Test blocks can be shared"""
        block = nvm.create_block("shared", BlockClass.SHARED_KNOWLEDGE, b"content")
        
        bridge = CrossManifoldBridge(nvm)
        bridge.share_block(block.id, [manifold_a.id, manifold_b.id])
        
        assert block.id in bridge.get_manifold_blocks(manifold_a.id)
        assert block.id in bridge.get_manifold_blocks(manifold_b.id)

class TestPerformance:
    """Performance tests"""
    
    @pytest.mark.benchmark
    def test_read_latency(self, nvm, benchmark):
        """Benchmark read latency"""
        block = nvm.create_block("perf_test", BlockClass.CUSTOM, b"x" * 10000)
        
        result = benchmark(nvm.get_block, block.id)
        assert result.mean < 0.01  # < 10ms
```

---

## Summary

NVM (Non-Volatile Memory) is the **persistent semantic storage layer** of HyperSync, providing:

1. **Dense Semantic Blocks**: Structured units of semantic information with geometric organization
2. **HVS Indexing**: All content indexed in HVS for fast semantic search
3. **Manifold Hosting**: Content organized on AGUA manifold (H⁴ × S³ × E⁵)
4. **Slower Silicon Storage**: Persistent storage on NVMe/disk/cloud
5. **Consistent Interface**: Same geometric representation for all models
6. **Multi-Manifold Support**: Blocks shared across manifolds as slow bridges
7. **Access Control**: Read-only documentation, read-write state, permissions

Key characteristics:
- **Persistence**: Survives restarts and sessions
- **Geometric Organization**: Content placed on manifold based on semantics
- **Shared Access**: Multiple models/manifolds can access same blocks
- **Tiered Storage**: Hot cache → NVMe → Disk → Cloud

---

*Document Version: 1.0.0*
*Last Updated: January 2026*
*Status: Specification Complete*
