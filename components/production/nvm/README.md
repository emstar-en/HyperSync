# NVM (Non-Volatile Memory)

**Component Type:** Foundation  
**Layer:** Persistent Storage  
**Version:** 2.0.0  
**Status:** Production

---

## Overview

NVM is the **Persistent Semantic Storage Layer** of HyperSync. It provides dense semantic blocks with HVS indexing for long-term knowledge storage, cross-manifold sharing, and documentation hosting. NVM operates at disk-speed (10-100ms) and serves as the "slow bridge" for cross-manifold communication.

### Key Capabilities

| Feature | Description | Performance |
|---------|-------------|-------------|
| **Semantic Blocks** | Dense, structured information units | Typed, metadata-rich |
| **HVS Indexed** | Vector-indexed for semantic search | O(log n) queries |
| **Multi-Manifold** | Shared across manifolds | Slow bridge |
| **Persistent Storage** | NVMe/Disk storage | Survives restarts |
| **Block Classes** | Documentation, State, Knowledge Graph, Cache | Read-only support |

### Why NVM?

1. **Persistent Storage** - Semantic information survives restarts and sessions
2. **Consistent Access** - Same geometric representation for all interacting models
3. **Shared Knowledge** - Multiple manifolds can access shared blocks
4. **Documentation Storage** - Read-only HyperSync documentation accessible to all
5. **Model Memory Extension** - Extends model context beyond token limits

---

## Architecture

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

### Core Components

- **Block Manager** - Create, manage, delete semantic blocks (lifecycle management)
- **Semantic Blocks** - Store dense semantic information (structured data)
- **HVS Integration** - Index blocks in HVS (semantic search)
- **Storage Layer** - Persist to slower silicon (durability)
- **Multi-Manifold Layer** - Cross-manifold access (slow bridge)

---

## Documentation

### Specifications
- **[NVM_SPECIFICATION.md](docs/NVM_SPECIFICATION.md)** - Complete NVM specification (3,080 lines)
- **[HVS_NVM_INTEGRATION.md](docs/HVS_NVM_INTEGRATION.md)** - Integration with HVS
- **[IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md)** - Implementation plan

---

## Quick Start

### Basic Block Storage

```python
from nvm import NVM, BlockClass

# Initialize NVM
nvm = NVM(storage_path="/data/nvm")

# Create a semantic block
block = nvm.create_block(
    name="project_documentation",
    block_class=BlockClass.DOCUMENTATION,
    content="Dense semantic content here...",
    metadata={'tags': ['docs', 'api'], 'version': '2.0'}
)

# Retrieve block
retrieved = nvm.get_block(block.id)
```

### Semantic Query

```python
from nvm import NVM

nvm = NVM(storage_path="/data/nvm")

# Query using semantic search (via HVS index)
results = nvm.semantic_query(
    query="How does model communication work?",
    k=5,
    filter_class=BlockClass.DOCUMENTATION
)

for result in results:
    print(f"Block: {result.name}")
    print(f"Content: {result.content[:200]}...")
```

### Cross-Manifold Sharing

```python
from nvm import NVM

nvm = NVM(storage_path="/data/nvm")

# Create shared block accessible from multiple manifolds
block = nvm.create_block(
    name="shared_knowledge",
    block_class=BlockClass.KNOWLEDGE_GRAPH,
    content=knowledge_data,
    manifolds=["manifold_a", "manifold_b"],  # Share across manifolds
    shared=True
)
```

---

## Block Classes

NVM supports four primary block classes:

### 1. Documentation Blocks
- **Purpose:** Read-only HyperSync documentation
- **Read-Only:** Yes
- **Shared:** Yes (accessible from all manifolds)
- **Use Case:** System documentation, API references

### 2. Program State Blocks
- **Purpose:** Persistent program state
- **Read-Only:** No
- **Shared:** No (private to manifold)
- **Use Case:** Checkpoints, session state

### 3. Knowledge Graph Blocks
- **Purpose:** Structured knowledge graphs
- **Read-Only:** No
- **Shared:** Yes (configurable)
- **Use Case:** Shared knowledge, semantic networks

### 4. Cache Blocks
- **Purpose:** Persistent cache storage
- **Read-Only:** No
- **Shared:** No
- **Use Case:** Computation caching, temporary storage

---

## Block Structure

Each semantic block contains:

```
┌──────────────────────────────────────┐
│              Header                   │
│  - Block ID (UUID)                    │
│  - Name                               │
│  - Class (enum)                       │
│  - Version                            │
│  - Created/Updated timestamps         │
│  - Read-only flag                     │
└──────────────────────────────────────┘
┌──────────────────────────────────────┐
│              Data                     │
│  - Dense semantic content             │
│  - JSON, Markdown, binary formats     │
│  - Compressed if large                │
└──────────────────────────────────────┘
┌──────────────────────────────────────┐
│           Vector Index                │
│  - Embedded vectors                   │
│  - HVS-indexed                        │
│  - Geometry-aware placement           │
└──────────────────────────────────────┘
┌──────────────────────────────────────┐
│            Metadata                   │
│  - Tags, labels, attributes           │
│  - Access control                     │
│  - Manifold associations              │
└──────────────────────────────────────┘
```

---

## Performance

| Operation | Latency | Throughput |
|-----------|---------|------------|
| Block creation | 20-100ms | 1k ops/sec |
| Block retrieval | 10-50ms | 2k ops/sec |
| Semantic query (via HVS) | 50-200ms | 500 queries/sec |
| Cross-manifold access | 100-500ms | Slower bridge |

**Hardware:** NVMe/SSD recommended (HDD acceptable for cold storage)

---

## Integration with HVS

NVM integrates tightly with HVS:

1. **Automatic Indexing** - All blocks automatically indexed in HVS
2. **Semantic Search** - Query NVM content via HVS semantic search
3. **Geometric Placement** - Blocks placed on AGUA manifold structure
4. **Consistent Representation** - Same geometric view for all models

```python
from hvs_nvm import HVSNVMIntegration

# Unified interface
integration = HVSNVMIntegration(
    hvs_path="/data/hvs",
    nvm_path="/data/nvm"
)

# Store with automatic indexing and persistence
block_id = integration.store(
    content="HyperSync content",
    persist=True  # Store in NVM, index in HVS
)

# Query across both systems
results = integration.query("HyperSync architecture")
```

---

## Dependencies

- **HVS** - Vector indexing and semantic search

## Used By

- **PCT** - Pathfinder → Cartographer → Trailblazer (workflow persistence)
- **SDL** - Semantic data lake (persistent data)
- **HAW** - Human-AI workspace (session storage)
- **MOM** - Model orchestration (state management)

## Integrates With

- **HVS** - Fast vector index layer

---

## Development

### STUNIR Generation

NVM uses STUNIR for deterministic code generation:

```bash
cd STUNIR
./scripts/stunir_pipeline.py \
  --spec ../HyperSync/build/current/components/production/nvm/specs/ \
  --output ../HyperSync/build/current/components/production/nvm/generated/
```

**Generated Targets:**
- Rust (primary, tier A)
- Python (reference, tier A)
- C (performance, tier B)

### Directory Structure

```
nvm/
├── meta.json                    # Component metadata
├── specs/                       # STUNIR specifications
│   ├── blocks/                 # Semantic block specs
│   ├── storage/                # Storage layer specs
│   ├── indexing/               # HVS integration specs
│   ├── manifold/               # Multi-manifold specs
│   └── integration/            # Integration specs
├── docs/                       # Documentation
├── reference/                  # Reference implementations
├── generated/                  # STUNIR-generated code
├── tests/                      # Test suites
└── analysis/                   # Performance analysis
```

---

## Storage Backends

NVM supports multiple storage backends:

### 1. NVMe Storage (Recommended)
- High-performance SSD storage
- 10-50ms latency
- Best for production workloads

### 2. Disk Storage
- Traditional HDD storage
- 50-200ms latency
- Acceptable for cold storage

### 3. Cloud Storage (Future)
- S3, Azure Blob, GCS
- 100-500ms latency
- Best for distributed deployments

### 4. Hybrid Storage
- Hot data on NVMe, cold data on HDD/Cloud
- Tiered storage strategy
- Optimal cost/performance balance

---

## Next Steps

1. **Read the Specification** - [NVM_SPECIFICATION.md](docs/NVM_SPECIFICATION.md)
2. **Understand Integration** - [HVS_NVM_INTEGRATION.md](docs/HVS_NVM_INTEGRATION.md)
3. **Review Implementation Plan** - [IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md)

---

**Last Updated:** 2026-02-19  
**Status:** Production-ready  
**Maintainer:** HyperSync Core Team
