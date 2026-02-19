# HVS-NVM Specifications
## HyperSync Vector and Storage System

---

## Overview

This directory contains comprehensive specifications for **HVS (Hyper Vector System)** and **NVM (Non-Volatile Memory)** - the core storage and communication backbone of HyperSync.

### What is HyperSync?

HyperSync is a distributed AI coordination system that uses **hyperbolic geometry** for efficient model communication and synchronization. HVS and NVM form the foundational layer that enables:

- **Model-to-Model Communication**: Vectors as the universal communication substrate
- **Multi-Geometry Support**: Hyperbolic, Euclidean, Spherical, and Lorentzian spaces
- **Persistent Semantic Storage**: Dense blocks indexed by geometric position
- **Cross-Manifold Bridging**: Shared knowledge across multiple manifolds

---

## Documents

| Document | Description |
|----------|-------------|
| [HVS_CORE_SPECIFICATION.md](HVS_CORE_SPECIFICATION.md) | Complete HVS specification - geometry, communication, sync |
| [NVM_SPECIFICATION.md](NVM_SPECIFICATION.md) | Complete NVM specification - blocks, storage, access control |
| [HVS_NVM_INTEGRATION.md](HVS_NVM_INTEGRATION.md) | Integration between HVS and NVM |
| [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) | Phased implementation plan |
| [API_SPECIFICATIONS.md](API_SPECIFICATIONS.md) | Complete API reference |
| [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md) | Visual architecture diagrams |
| [EXAMPLES_AND_PATTERNS.md](EXAMPLES_AND_PATTERNS.md) | Usage examples and design patterns |

---

## Quick Reference

### HVS Key Concepts

- **Multi-Geometry Engine**: Support for Hyperboloid (Hⁿ), Poincaré Ball, Euclidean (Eⁿ), and Lorentzian spaces
- **Model Communication**: Models communicate through shared vector spaces
- **Synchronization**: Full, partial, and selective sync between HVS instances
- **RAM-Speed Operations**: Sub-millisecond vector operations

### NVM Key Concepts

- **Semantic Blocks**: Dense semantic information units with geometric placement
- **HVS Indexed**: All content indexed in HVS for semantic search
- **Block Classes**: Documentation (read-only), Program State, Knowledge Graph, Cache
- **Multi-Manifold**: Blocks shared across manifolds as "slow bridges"
- **Disk-Speed Storage**: Persistent storage on NVMe/disk

### Integration

```
┌───────────────────┐
│   Application   │
└─────────┬─────────┘
          │
┌─────────▼─────────┐
│   Unified API   │
└─────────┬─────────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼───┐ ┌────▼────┐
│  HVS   │ │   NVM    │
│ (Fast) │ │(Persist) │
└────────┘ └──────────┘
```

---

## Getting Started

### Basic Usage

```python
from hvs import HVS
from nvm import NVM, BlockClass

# Initialize
hvs = HVS(storage_path="/data/hvs", dimension=12)
nvm = NVM(storage_path="/data/nvm")

# Store vector in HVS
vector_id = hvs.store_vector(vector, metadata={'type': 'document'})

# Create block in NVM
block = nvm.create_block("my_doc", BlockClass.DOCUMENTATION, "content")

# Semantic search
results = hvs.semantic_search(query_vector, k=10)

# Query NVM
results = nvm.semantic_query("search query", k=5)
```

### Integrated Usage

```python
from hvs_nvm import HVSNVMIntegration

integration = HVSNVMIntegration(hvs_path="/data/hvs", nvm_path="/data/nvm")

# Store with automatic indexing and persistence
id = integration.store("HyperSync content", persist=True)

# Query across both systems
results = integration.query("HyperSync")
```
