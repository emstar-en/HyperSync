# HVS-NVM Examples and Patterns
## Version 1.0.0 | Practical Usage Guide

---

## Quick Start Examples

### Basic HVS Usage

```python
import numpy as np
from hvs import HVS

# Initialize HVS
hvs = HVS(storage_path="/data/hvs", dimension=12)

# Store a vector
vector = np.random.randn(12)
vector_id = hvs.store_vector(
    vector=vector,
    metadata={'source': 'example', 'type': 'document'}
)
print(f"Stored vector: {vector_id}")

# Retrieve vector
retrieved = hvs.retrieve_vector(vector_id)
print(f"Retrieved: {retrieved.data}")

# Semantic search
query = np.random.randn(12)
results = hvs.semantic_search(query, k=5)
for r in results:
    print(f"ID: {r.vector.id}, Distance: {r.distance:.4f}")
```

### Basic NVM Usage

```python
from nvm import NVM, BlockClass

# Initialize NVM
nvm = NVM(storage_path="/data/nvm")

# Create a documentation block (read-only)
doc_block = nvm.create_block(
    name="example_doc",
    block_class=BlockClass.DOCUMENTATION,
    content="# Example\n\nThis is example documentation.",
    readonly=True
)
print(f"Created block: {doc_block.id}")

# Create a state block (read-write)
state_block = nvm.create_block(
    name="app_state",
    block_class=BlockClass.PROGRAM_STATE,
    content={'counter': 0, 'name': 'example'}
)

# Query blocks semantically
results = nvm.semantic_query("What is the example?")
for r in results:
    print(f"Found: {r['block'].name}, Score: {r['score']:.4f}")
```

### Integrated HVS-NVM Usage

```python
from hvs_nvm import HVSNVMIntegration

# Initialize integrated system
integration = HVSNVMIntegration(
    hvs_path="/data/hvs",
    nvm_path="/data/nvm"
)

# Store content (indexed in HVS, persisted in NVM)
id = integration.store(
    content="HyperSync is a distributed AI coordination system.",
    persist=True
)

# Query across both systems
results = integration.query("distributed AI")
for r in results:
    print(f"Source: {r['source']}, Content: {r['content'][:50]}...")
```

---

## Common Patterns

### Pattern 1: Document Storage and Retrieval

```python
class DocumentStore:
    """Pattern for storing and retrieving documents"""
    
    def __init__(self, hvs: HVS, nvm: NVM, encoder):
        self.hvs = hvs
        self.nvm = nvm
        self.encoder = encoder
    
    def store_document(self, doc_id: str, content: str, metadata: dict = None):
        """Store document with semantic indexing"""
        # Create NVM block
        block = self.nvm.create_block(
            name=f"doc_{doc_id}",
            block_class=BlockClass.DOCUMENTATION,
            content=content,
            metadata=metadata or {}
        )
        
        # Index in HVS
        vector = self.encoder.encode(content)
        hvs_id = self.hvs.store_vector(
            vector=vector,
            metadata={
                'doc_id': doc_id,
                'nvm_block_id': block.id,
                'type': 'document'
            }
        )
        
        return {'doc_id': doc_id, 'hvs_id': hvs_id, 'block_id': block.id}
    
    def search_documents(self, query: str, k: int = 10):
        """Search documents semantically"""
        query_vector = self.encoder.encode(query)
        results = self.hvs.semantic_search(query_vector, k=k)
        
        documents = []
        for r in results:
            block_id = r.vector.metadata.get('nvm_block_id')
            if block_id:
                block = self.nvm.get_block(block_id)
                documents.append({
                    'doc_id': r.vector.metadata['doc_id'],
                    'content': block.content,
                    'distance': r.distance,
                    'score': r.score
                })
        
        return documents

# Usage
store = DocumentStore(hvs, nvm, encoder)
store.store_document("doc1", "HyperSync uses hyperbolic geometry...")
results = store.search_documents("geometry")
```

### Pattern 2: Model State Persistence

```python
class ModelStatePersistence:
    """Pattern for persisting model state"""
    
    def __init__(self, nvm: NVM, model_id: str):
        self.nvm = nvm
        self.model_id = model_id
        self.state_block = self._init_state_block()
    
    def _init_state_block(self):
        """Initialize or load state block"""
        existing = self.nvm.get_block_by_name(f"state_{self.model_id}")
        if existing:
            return existing
        
        return self.nvm.create_block(
            name=f"state_{self.model_id}",
            block_class=BlockClass.PROGRAM_STATE,
            content={'initialized_at': time.time()},
            permissions={'read': [self.model_id], 'write': [self.model_id]}
        )
    
    def get_state(self, key: str = None):
        """Get state value(s)"""
        block = self.nvm.get_block(self.state_block.id)
        state = json.loads(block.content)
        
        if key:
            return state.get(key)
        return state
    
    def set_state(self, key: str, value):
        """Set state value"""
        state = self.get_state()
        state[key] = value
        state['last_updated'] = time.time()
        
        self.nvm.update_block(self.state_block.id, json.dumps(state))
    
    def checkpoint(self) -> str:
        """Create checkpoint"""
        state = self.get_state()
        checkpoint = self.nvm.create_block(
            name=f"checkpoint_{self.model_id}_{int(time.time())}",
            block_class=BlockClass.PROGRAM_STATE,
            content=state,
            readonly=True  # Checkpoints are immutable
        )
        return checkpoint.id

# Usage
state = ModelStatePersistence(nvm, "model_a")
state.set_state("conversation_count", 42)
checkpoint_id = state.checkpoint()
```

### Pattern 3: Multi-Model Communication

```python
class ModelCommunicationHub:
    """Pattern for multi-model communication via HVS"""
    
    def __init__(self, hvs: HVS):
        self.hvs = hvs
        self.models = {}
    
    def register_model(self, model_id: str):
        """Register a model"""
        connection = self.hvs.connect_model(model_id)
        self.models[model_id] = {
            'connection': connection,
            'mailbox': []
        }
        return connection
    
    def send_message(self, from_model: str, to_model: str, message: dict):
        """Send message between models"""
        return self.hvs.send_message(from_model, to_model, message)
    
    def broadcast(self, from_model: str, message: dict, exclude: list = None):
        """Broadcast to all models"""
        exclude = exclude or []
        for model_id in self.models:
            if model_id != from_model and model_id not in exclude:
                self.send_message(from_model, model_id, message)
    
    def receive_messages(self, model_id: str) -> list:
        """Receive all pending messages"""
        return self.hvs.receive_messages(model_id)
    
    def query_similar_states(self, model_id: str, state_vector, k: int = 5):
        """Find models with similar states"""
        results = self.hvs.semantic_search(
            query_vector=state_vector,
            k=k,
            filter={'type': 'model_state'}
        )
        return [r for r in results if r.vector.metadata['model_id'] != model_id]

# Usage
hub = ModelCommunicationHub(hvs)
hub.register_model("model_a")
hub.register_model("model_b")

hub.send_message("model_a", "model_b", {'task': 'analyze', 'data': 'xyz'})
messages = hub.receive_messages("model_b")
```

### Pattern 4: Shared Knowledge Base

```python
class SharedKnowledgeBase:
    """Pattern for shared knowledge across models/manifolds"""
    
    def __init__(self, nvm: NVM, hvs: HVS):
        self.nvm = nvm
        self.hvs = hvs
        self.kb_block = self._init_kb()
    
    def _init_kb(self):
        """Initialize knowledge base block"""
        return self.nvm.create_block(
            name="shared_knowledge_base",
            block_class=BlockClass.SHARED_KNOWLEDGE,
            content={'facts': [], 'relations': []},
            permissions={'read': ['*'], 'write': ['*']}
        )
    
    def add_fact(self, subject: str, predicate: str, obj: str, source: str):
        """Add fact to knowledge base"""
        block = self.nvm.get_block(self.kb_block.id)
        kb = json.loads(block.content)
        
        fact = {
            'subject': subject,
            'predicate': predicate,
            'object': obj,
            'source': source,
            'timestamp': time.time()
        }
        kb['facts'].append(fact)
        
        # Index in HVS
        fact_text = f"{subject} {predicate} {obj}"
        vector = self.encoder.encode(fact_text)
        self.hvs.store_vector(vector, metadata={
            'type': 'fact',
            'fact': fact,
            'kb_block_id': self.kb_block.id
        })
        
        self.nvm.update_block(self.kb_block.id, json.dumps(kb))
    
    def query_facts(self, query: str, k: int = 10):
        """Query facts semantically"""
        query_vector = self.encoder.encode(query)
        results = self.hvs.semantic_search(
            query_vector,
            k=k,
            filter={'type': 'fact'}
        )
        return [r.vector.metadata['fact'] for r in results]

# Usage
kb = SharedKnowledgeBase(nvm, hvs)
kb.add_fact("HyperSync", "uses", "hyperbolic geometry", "documentation")
kb.add_fact("HVS", "provides", "vector storage", "specification")

facts = kb.query_facts("geometry")
```

### Pattern 5: Semantic Cache

```python
class SemanticCache:
    """Pattern for semantic caching with TTL"""
    
    def __init__(self, nvm: NVM, hvs: HVS, ttl_seconds: int = 3600):
        self.nvm = nvm
        self.hvs = hvs
        self.ttl = ttl_seconds
        self.cache_block = self._init_cache()
    
    def _init_cache(self):
        return self.nvm.create_block(
            name="semantic_cache",
            block_class=BlockClass.CACHE,
            content={'entries': {}},
            metadata={'ttl_seconds': self.ttl}
        )
    
    def get(self, query: str, threshold: float = 0.9):
        """Get cached value by semantic similarity"""
        query_vector = self.encoder.encode(query)
        
        results = self.hvs.semantic_search(
            query_vector,
            k=1,
            filter={'type': 'cache_entry', 'cache_id': self.cache_block.id}
        )
        
        if results and results[0].score >= threshold:
            entry = results[0].vector.metadata['entry']
            
            # Check TTL
            if time.time() < entry['expires_at']:
                return entry['value']
            else:
                # Expired, remove
                self.hvs.delete_vector(results[0].vector.id)
        
        return None
    
    def set(self, key: str, value, query_vector=None):
        """Set cache entry"""
        if query_vector is None:
            query_vector = self.encoder.encode(key)
        
        entry = {
            'key': key,
            'value': value,
            'created_at': time.time(),
            'expires_at': time.time() + self.ttl
        }
        
        self.hvs.store_vector(
            vector=query_vector,
            metadata={
                'type': 'cache_entry',
                'cache_id': self.cache_block.id,
                'entry': entry
            }
        )

# Usage
cache = SemanticCache(nvm, hvs, ttl_seconds=3600)

# Cache miss
result = cache.get("What is HyperSync?")
if result is None:
    result = expensive_computation()
    cache.set("What is HyperSync?", result)

# Similar queries will hit cache
result = cache.get("Tell me about HyperSync")  # Semantic match!
```

---

## Best Practices

### 1. Choose the Right Geometry

```python
# Hierarchical data → Hyperboloid
hvs_hierarchical = HVS(geometry='hyperboloid')  # Best for trees, taxonomies

# Cyclic/directional data → Spherical
hvs_spherical = HVS(geometry='spherical')  # Best for angles, directions

# General embeddings → Euclidean
hvs_euclidean = HVS(geometry='euclidean')  # Default, most compatible
```

### 2. Use Appropriate Block Classes

```python
# Read-only documentation
BlockClass.DOCUMENTATION  # For specs, docs, references

# Mutable state
BlockClass.PROGRAM_STATE  # For model state, counters

# Knowledge graphs
BlockClass.KNOWLEDGE_GRAPH  # For facts, relations

# Temporary data
BlockClass.CACHE  # With TTL expiration
```

### 3. Handle Errors Gracefully

```python
try:
    result = hvs.retrieve_vector(vector_id)
except VectorNotFoundError:
    # Handle missing vector
    result = None
except HVSError as e:
    logging.error(f"HVS error: {e}")
    raise

try:
    nvm.update_block(block_id, content)
except ReadOnlyBlockError:
    logging.warning(f"Cannot modify read-only block {block_id}")
except BlockNotFoundError:
    # Create block if it doesn't exist
    nvm.create_block(...)
```

### 4. Batch Operations for Performance

```python
# Bad: Individual stores (slow)
for item in items:
    hvs.store_vector(item)

# Good: Batch store (fast)
hvs.batch_store_vectors(items)

# Good: Batch retrieve
vectors = hvs.batch_retrieve_vectors(vector_ids)
```

### 5. Use Caching Wisely

```python
# Enable caching for read-heavy workloads
hvs = HVS(cache_size_mb=1024)

# Prefetch related vectors
hvs.prefetch(related_vector_ids)

# Invalidate cache on updates
hvs.invalidate_cache(updated_id)
```

---

## Error Handling

```python
from hvs import HVSError, VectorNotFoundError
from nvm import NVMError, BlockNotFoundError, ReadOnlyBlockError

class RobustHVSNVM:
    """Robust error handling pattern"""
    
    def safe_store(self, content, **kwargs):
        try:
            return self.integration.store(content, **kwargs)
        except HVSError as e:
            logging.error(f"HVS store failed: {e}")
            # Retry or fallback
            return self._retry_store(content, **kwargs)
        except NVMError as e:
            logging.error(f"NVM store failed: {e}")
            # Store without persistence
            return self.hvs.store_vector(self.encode(content))
    
    def safe_query(self, query, k=10):
        try:
            return self.integration.query(query, k=k)
        except Exception as e:
            logging.error(f"Query failed: {e}")
            return []  # Return empty results on error
    
    def _retry_store(self, content, max_retries=3, **kwargs):
        for i in range(max_retries):
            try:
                time.sleep(0.1 * (2 ** i))  # Exponential backoff
                return self.integration.store(content, **kwargs)
            except Exception:
                if i == max_retries - 1:
                    raise
```

---

## Testing Patterns

```python
import pytest
from hvs import HVS
from nvm import NVM

@pytest.fixture
def hvs():
    """Create test HVS instance"""
    hvs = HVS(storage_path=tempfile.mkdtemp())
    yield hvs
    hvs.close()

@pytest.fixture
def nvm():
    """Create test NVM instance"""
    nvm = NVM(storage_path=tempfile.mkdtemp())
    yield nvm
    nvm.close()

class TestHVSOperations:
    def test_store_and_retrieve(self, hvs):
        vector = np.random.randn(12)
        vector_id = hvs.store_vector(vector)
        
        retrieved = hvs.retrieve_vector(vector_id)
        assert np.allclose(vector, retrieved.data)
    
    def test_semantic_search(self, hvs):
        # Store vectors
        for _ in range(100):
            hvs.store_vector(np.random.randn(12))
        
        # Search
        query = np.random.randn(12)
        results = hvs.semantic_search(query, k=10)
        
        assert len(results) == 10
        assert results[0].distance <= results[1].distance

class TestNVMOperations:
    def test_readonly_block(self, nvm):
        block = nvm.create_block(
            "test", BlockClass.DOCUMENTATION, 
            "content", readonly=True
        )
        
        with pytest.raises(ReadOnlyBlockError):
            nvm.update_block(block.id, "new content")
```

---

*Document Version: 1.0.0*
*Last Updated: January 2026*
