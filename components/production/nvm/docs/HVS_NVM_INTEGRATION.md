# HVS-NVM Integration Specification
## Version 1.0.0 | HyperSync Integration Layer

---

## Overview

This document specifies how HVS (Hyper Vector System) and NVM (Non-Volatile Memory) integrate to form the HyperSync storage backbone.

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   HVS-NVM Integration                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    Application Layer                     │   │
│   │      Models, Agents, Tools, User Applications           │   │
│   └───────────────────────────┬─────────────────────────────┘   │
│                               │                                  │
│                               ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    Unified API Layer                     │   │
│   │              hvs_nvm.query(), hvs_nvm.store()           │   │
│   └───────────────────────────┬─────────────────────────────┘   │
│                               │                                  │
│               ┌───────────────┴───────────────┐                 │
│               │                               │                  │
│               ▼                               ▼                  │
│   ┌───────────────────────┐   ┌───────────────────────────┐    │
│   │         HVS           │   │          NVM              │    │
│   │   (Fast Index)        │◀─▶│   (Persistent Storage)    │    │
│   │   RAM-speed           │   │   Disk-speed              │    │
│   │   Vector operations   │   │   Block storage           │    │
│   └───────────────────────┘   └───────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Integration Points

| Integration Point | Description | Direction |
|-------------------|-------------|----------|
| Vector Indexing | NVM blocks indexed in HVS | NVM → HVS |
| Query Routing | Queries dispatched to both | Bidirectional |
| Persistence | HVS state backed by NVM | HVS → NVM |
| Consistency | Synchronized updates | Bidirectional |
| Caching | NVM content cached in HVS | NVM → HVS |

---

## Integration Components

### 1. Unified Interface

```python
class HVSNVMIntegration:
    """Unified interface for HVS and NVM"""
    
    def __init__(self, hvs: HVS, nvm: NVM):
        self.hvs = hvs
        self.nvm = nvm
        self.sync_manager = SyncManager(hvs, nvm)
        self.query_router = QueryRouter(hvs, nvm)
    
    def store(self, content: Any, persist: bool = True) -> str:
        """Store content in HVS with optional NVM persistence"""
        # Encode to vector
        vector = self.encoder.encode(content)
        
        # Store in HVS (fast index)
        hvs_id = self.hvs.store_vector(vector, metadata={'content': content})
        
        if persist:
            # Create NVM block for persistence
            block = self.nvm.create_block(
                name=f"content_{hvs_id}",
                content=content,
                metadata={'hvs_id': hvs_id}
            )
            
            # Link HVS entry to NVM block
            self.hvs.update_metadata(hvs_id, {'nvm_block_id': block.id})
        
        return hvs_id
    
    def query(self, query: str, k: int = 10) -> List[Dict]:
        """Query both HVS and NVM"""
        return self.query_router.route_query(query, k)
    
    def get(self, id: str) -> Optional[Any]:
        """Get content by ID (checks HVS cache first, then NVM)"""
        # Check HVS (fast)
        hvs_result = self.hvs.retrieve_vector(id)
        if hvs_result and 'content' in hvs_result.metadata:
            return hvs_result.metadata['content']
        
        # Check NVM (slower but persistent)
        nvm_result = self.nvm.get_block(id)
        if nvm_result:
            return nvm_result.content
        
        return None
```

### 2. Query Routing

```python
class QueryRouter:
    """Route queries between HVS and NVM"""
    
    def __init__(self, hvs: HVS, nvm: NVM):
        self.hvs = hvs
        self.nvm = nvm
    
    def route_query(self, query: str, k: int = 10) -> List[Dict]:
        """Determine optimal query path"""
        query_vector = self.encoder.encode(query)
        
        # Always query HVS first (fast)
        hvs_results = self.hvs.semantic_search(query_vector, k=k)
        
        # Check if HVS results reference NVM blocks
        enriched_results = []
        for result in hvs_results:
            nvm_block_id = result.metadata.get('nvm_block_id')
            if nvm_block_id:
                block = self.nvm.get_block(nvm_block_id)
                enriched_results.append({
                    'vector': result,
                    'block': block,
                    'source': 'hvs+nvm'
                })
            else:
                enriched_results.append({
                    'vector': result,
                    'block': None,
                    'source': 'hvs'
                })
        
        return enriched_results
```

### 3. Synchronization

```python
class SyncManager:
    """Synchronize HVS and NVM state"""
    
    def __init__(self, hvs: HVS, nvm: NVM):
        self.hvs = hvs
        self.nvm = nvm
        self.sync_queue = []
    
    def sync_hvs_to_nvm(self, hvs_ids: List[str] = None):
        """Persist HVS vectors to NVM"""
        if hvs_ids is None:
            hvs_ids = self.hvs.get_all_ids()
        
        for hvs_id in hvs_ids:
            vector = self.hvs.retrieve_vector(hvs_id)
            if not vector.metadata.get('nvm_block_id'):
                # Create NVM block
                block = self.nvm.create_block(
                    name=f"hvs_{hvs_id}",
                    content=vector.metadata.get('content'),
                    vectors=[vector.data]
                )
                self.hvs.update_metadata(hvs_id, {'nvm_block_id': block.id})
    
    def sync_nvm_to_hvs(self, block_ids: List[str] = None):
        """Index NVM blocks in HVS"""
        if block_ids is None:
            block_ids = [b.id for b in self.nvm.list_blocks()]
        
        for block_id in block_ids:
            block = self.nvm.get_block(block_id)
            if block.vectors:
                for i, vector in enumerate(block.vectors):
                    hvs_id = self.hvs.store_vector(
                        vector=vector,
                        metadata={
                            'nvm_block_id': block_id,
                            'chunk_index': i
                        }
                    )
    
    def verify_consistency(self) -> Dict:
        """Verify HVS and NVM are consistent"""
        inconsistencies = []
        
        # Check all HVS entries have valid NVM blocks
        for hvs_id in self.hvs.get_all_ids():
            vector = self.hvs.retrieve_vector(hvs_id)
            nvm_block_id = vector.metadata.get('nvm_block_id')
            if nvm_block_id:
                block = self.nvm.get_block(nvm_block_id)
                if not block:
                    inconsistencies.append({
                        'hvs_id': hvs_id,
                        'nvm_block_id': nvm_block_id,
                        'issue': 'nvm_block_missing'
                    })
        
        return {
            'consistent': len(inconsistencies) == 0,
            'inconsistencies': inconsistencies
        }
```

### 4. Caching Layer

```python
class HVSNVMCache:
    """Unified caching for HVS and NVM"""
    
    def __init__(self, hvs: HVS, nvm: NVM, cache_size_mb: int = 1024):
        self.hvs = hvs
        self.nvm = nvm
        self.vector_cache = LRUCache(max_size=cache_size_mb * 1024 * 1024 // 2)
        self.block_cache = LRUCache(max_size=cache_size_mb * 1024 * 1024 // 2)
    
    def get_vector(self, hvs_id: str) -> Optional[Vector]:
        """Get vector with caching"""
        if hvs_id in self.vector_cache:
            return self.vector_cache[hvs_id]
        
        vector = self.hvs.retrieve_vector(hvs_id)
        if vector:
            self.vector_cache[hvs_id] = vector
        return vector
    
    def get_block(self, block_id: str) -> Optional[NVMBlock]:
        """Get block with caching"""
        if block_id in self.block_cache:
            return self.block_cache[block_id]
        
        block = self.nvm.get_block(block_id)
        if block:
            self.block_cache[block_id] = block
        return block
    
    def invalidate(self, id: str):
        """Invalidate cached entry"""
        if id in self.vector_cache:
            del self.vector_cache[id]
        if id in self.block_cache:
            del self.block_cache[id]
```

---

## Data Flow

### Write Path

```
Application → HVSNVMIntegration.store()
    │
    ├──▶ Encode content to vector
    │
    ├──▶ HVS.store_vector() [Fast, RAM]
    │       │
    │       └──▶ Returns hvs_id
    │
    ├──▶ NVM.create_block() [Slower, Disk]
    │       │
    │       └──▶ Returns block_id
    │
    ├──▶ Link hvs_id ↔ block_id
    │
    └──▶ Return hvs_id
```

### Read Path

```
Application → HVSNVMIntegration.query()
    │
    ├──▶ Encode query to vector
    │
    ├──▶ HVS.semantic_search() [Fast]
    │       │
    │       └──▶ Returns top-k matches
    │
    ├──▶ For each match:
    │       │
    │       ├──▶ Check HVS metadata for content
    │       │
    │       └──▶ If needed, NVM.get_block() [Slower]
    │
    └──▶ Return enriched results
```

---

## Consistency Model

### Write-Ahead Logging

```python
class WALManager:
    """Write-ahead logging for consistency"""
    
    def __init__(self, wal_path: str):
        self.wal_path = wal_path
        self.wal_file = open(wal_path, 'ab')
    
    def log_operation(self, operation: Dict):
        """Log operation before execution"""
        entry = {
            'timestamp': time.time(),
            'operation': operation,
            'status': 'pending'
        }
        self.wal_file.write(msgpack.packb(entry))
        self.wal_file.flush()
        return entry
    
    def mark_complete(self, entry: Dict):
        """Mark operation as complete"""
        entry['status'] = 'complete'
        self.wal_file.write(msgpack.packb(entry))
        self.wal_file.flush()
    
    def recover(self):
        """Recover from incomplete operations"""
        with open(self.wal_path, 'rb') as f:
            entries = list(msgpack.Unpacker(f))
        
        pending = [e for e in entries if e['status'] == 'pending']
        for entry in pending:
            self._replay_operation(entry['operation'])
```

### Transactional Guarantees

```python
class TransactionManager:
    """Transactional operations across HVS and NVM"""
    
    def __init__(self, hvs: HVS, nvm: NVM, wal: WALManager):
        self.hvs = hvs
        self.nvm = nvm
        self.wal = wal
    
    @contextmanager
    def transaction(self):
        """Transactional context"""
        tx = Transaction()
        try:
            yield tx
            self._commit(tx)
        except Exception as e:
            self._rollback(tx)
            raise
    
    def _commit(self, tx: Transaction):
        """Commit transaction"""
        # Log to WAL
        for op in tx.operations:
            self.wal.log_operation(op)
        
        # Execute operations
        for op in tx.operations:
            self._execute(op)
            self.wal.mark_complete(op)
    
    def _rollback(self, tx: Transaction):
        """Rollback transaction"""
        for op in reversed(tx.operations):
            self._undo(op)
```

---

## Performance Optimization

### Tiered Access

| Tier | Storage | Latency | Capacity |
|------|---------|---------|----------|
| L1 | HVS Vector Cache | <1ms | ~1GB |
| L2 | HVS Index | 1-10ms | ~10GB |
| L3 | NVM Hot Cache | <10ms | ~10GB |
| L4 | NVM NVMe | 10-100ms | ~1TB |
| L5 | NVM Archive | 100ms+ | ~10TB+ |

### Query Optimization

```python
class QueryOptimizer:
    """Optimize queries across HVS and NVM"""
    
    def optimize(self, query: Query) -> ExecutionPlan:
        """Generate optimal execution plan"""
        plan = ExecutionPlan()
        
        # Always start with HVS (fast)
        plan.add_step('hvs_search', priority=1)
        
        # Add NVM if full content needed
        if query.needs_full_content:
            plan.add_step('nvm_fetch', priority=2)
        
        # Add caching for repeated queries
        if query.cacheable:
            plan.add_step('cache_result', priority=3)
        
        return plan
```

---

## Error Handling

### Recovery Procedures

```python
class RecoveryManager:
    """Recovery for HVS-NVM integration"""
    
    def recover_from_failure(self):
        """Full recovery procedure"""
        # 1. Recover NVM from disk
        self.nvm.recover()
        
        # 2. Rebuild HVS index from NVM
        self.rebuild_hvs_index()
        
        # 3. Verify consistency
        self.verify_consistency()
    
    def rebuild_hvs_index(self):
        """Rebuild HVS from NVM blocks"""
        for block in self.nvm.list_blocks():
            for i, vector in enumerate(block.vectors):
                self.hvs.store_vector(
                    vector=vector,
                    metadata={
                        'nvm_block_id': block.id,
                        'chunk_index': i
                    }
                )
```

---

*Document Version: 1.0.0*
*Last Updated: January 2026*
