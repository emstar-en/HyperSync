# SDL (Semantic Data Lake) Specifications

## Overview

The **Semantic Data Lake (SDL)** is HyperSync's universal extensibility mechanism. It provides indexed, vectorized, semantically-searchable pools of ANY granular content—including code, data, models, and configurations.

### Core Value Proposition

| Feature | Description |
|---------|-------------|
| **Zero-Config Extensibility** | Drop content → automatically indexed → semantically discoverable |
| **Semantic Discovery** | Find by meaning, not by name or explicit path |
| **Universal Pattern** | Same mechanism for code, UI, docs, models, configs |
| **Capability-Based** | Query what something can do, not where it is |

## Specification Files

| File | Description | Operations |
|------|-------------|------------|
| `sdl_core_infrastructure.json` | Core SDL infrastructure, types, and architecture | Lake lifecycle, shard management |
| `sdl_indexing_system.json` | Indexing mechanism and metadata extraction | Index build, optimize, capability/dependency extraction |
| `sdl_vectorization_engine.json` | Text-to-vector conversion and AGUA manifold projection | Vectorize, batch vectorize, manifold projection |
| `sdl_semantic_search.json` | Query processing, similarity, and result fusion | Semantic search, capability search, similar search |
| `sdl_integration_layer.json` | Integration with HVS, VNES, NVM, Bootstrap | Subsystem coordination, events |
| `sdl_usage_patterns.json` | Usage patterns, best practices, and examples | Helper operations, patterns |
| `sdl_file_format.json` | SDL file format, serialization, and distribution | Export/import shard, lake, collection |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ "Make X      │  │ AI UI        │  │ Knowledge    │  │ VNES         │    │
│  │  for Y"      │  │ Generation   │  │ Search       │  │ Extensions   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
├─────────────────────────────────────────────────────────────────────────────┤
│                              SDL LAYER                                       │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────┐ │
│  │   Shard Management    │  │   Semantic Discovery  │  │  Lake Manager   │ │
│  │   • Ingest            │  │   • Search            │  │  • Index        │ │
│  │   • Activate          │  │   • Capability lookup │  │  • Optimize     │ │
│  │   • Deactivate        │  │   • Similar search    │  │  • Export/Import│ │
│  └───────────────────────┘  └───────────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│                              STORAGE LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     HVS (HyperSync Vector System)                    │   │
│  │                   AGUA 12D Manifold (H⁴ × S³ × E⁵)                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Data Structures

### SDLShard
The atomic unit of content in SDL:
- `id`: UUID - Unique identifier
- `name`: string - Human-readable name
- `type`: enum [code, data, model, config]
- `content`: bytes - Raw content
- `vector`: float64[] - Semantic embedding
- `capabilities`: SDLCapability[] - What this shard provides
- `dependencies`: UUID[] - Required shards
- `metadata`: dict - Custom metadata
- `active`: bool - Currently loaded in memory

### SDLCapability
Capability declaration:
- `name`: string - Capability name (e.g., 'parse_json')
- `type`: enum [function, model, data, config]
- `interface`: dict - Signature, schema, contract
- `vector`: float64[] - Capability-specific semantic vector

## Key Operations

### Shard Management
- `sdl_ingest_shard` - Add content to SDL
- `sdl_activate_shard` - Load shard into memory
- `sdl_deactivate_shard` - Unload shard from memory
- `sdl_remove_shard` - Delete shard from SDL

### Semantic Discovery
- `sdl_semantic_search` - Find shards by meaning
- `sdl_capability_search` - Find by capability name
- `sdl_similar_search` - Find similar shards
- `sdl_dependency_search` - Find shard dependencies

### Lake Management
- `sdl_index_lake` - Build/rebuild indices
- `sdl_optimize_lake` - Optimize storage
- `sdl_export_lake` - Export to .sdlx file
- `sdl_import_lake` - Import from .sdlx file

## File Formats

| Extension | Type | Use Case |
|-----------|------|----------|
| `.sdl` | Single shard | Individual code, data, model, or config |
| `.sdlx` | Lake export | Backup, migration, full distribution |
| `.sdlc` | Collection | Curated library for distribution |
| `.sdl.json` | Manifest | Metadata only, for catalogs |

## AGUA Manifold Integration

SDL vectors are projected onto the AGUA 12D product manifold:
- **H⁴ (Hyperbolic)**: Hierarchical, temporal, tree-structured content
- **S³ (Spherical)**: Cyclic, bounded, ontological content
- **E⁵ (Euclidean)**: Flat, linear, general-purpose content

## License

All specifications in this directory are licensed under **AGPLv3** (GNU Affero General Public License v3.0).

## Dependencies

- `hypersync_vector_storage@3.0.0` - HVS for storage backend
- `hypersync_geometric_integration@2.1.0` - AGUA manifold operations
- `hypersync_type_system@2.1.0` - Type definitions

## Related Documentation

- `/home/ubuntu/make_x_for_y_research/SDL_ARCHITECTURE_COMPREHENSIVE.md` - Detailed architecture
- `/home/ubuntu/make_x_for_y_research/SDL_IMPLEMENTATION_TECHNICAL_DEEP_DIVE.md` - Technical details
- `/home/ubuntu/make_x_for_y_research/SDL_COMPONENT_USAGE_MAP.md` - Component integration
