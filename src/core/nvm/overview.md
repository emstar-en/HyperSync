# Node Version Manager

# HyperSync Spec Pack - NVM Schema 

## Overview

This system provides
- **Hyperbolic vector embedding by default** (Poincaré ball, κ=-1.0, d=768)
- **Assignment system** for models, stacks, networks, trunks, and model groups
- **Directory management** with automatic file embedding
- **Preloading capabilities** for documentation and training data
- **Full CRUD operations** via CLI and REST API

## Key Features

### 1. Hyperbolic Vector Embedding (Default)
All NVM blocks are hyperbolically embedded by default for efficient similarity search in curved spaces. Perfect for hierarchical data like documentation and knowledge graphs.

### 2. Assignment System
Assign NVM blocks to:
- Individual models
- Model stacks
- Networks and trunks
- Model groups
- Bridges
- Global scope

### 3. Directory Management
- Attach directories to NVM blocks
- Automatic embedding of files
- File watching for real-time updates
- Extension filtering and size limits

### 4. Preloading
- Preload blocks with documentation, training data, or other content
- Support for files, directories, URLs, and inline content
- Ideal for initial assistant models with HyperSync documentation

## Quick Start

### Create HyperSync Docs for Initial Assistant

```bash
python tools/nvm/nvm_cli.py create-preset \
 --preset hypersync_docs \
 --target-id model://assistant/initial \
 --target-name "Initial Network Setup Assistant"
```

This creates an NVM block preloaded with HyperSync documentation, perfect for the initial assistant model that helps with network setup.

### Create Model-Specific Cache

```bash
python tools/nvm/nvm_cli.py create-preset \
 --preset model_cache \
 --target-id model://compute/v1
```

## Model Contract Tools

Models and LLMs have access to these NVM tools:

1. `nvm_create_block` - Create new NVM block
2. `nvm_assign_block` - Assign block to entity
3. `nvm_add_directory` - Add directory for file management
4. `nvm_add_preload` - Configure preloading
5. `nvm_list_blocks` - List blocks with filtering
6. `nvm_get_block` - Get block details
7. `nvm_create_preset` - Create from preset

See `artifacts/model_contract_nvm.json` for complete specifications.

## Files integrated/Modified

### New Files
- `codegen/templates/runtime/hypersync/nvm/nvm_schema_manager.py`
- `codegen/templates/runtime/hypersync/nvm/nvm_enhanced_cli.py`
- `codegen/templates/runtime/hypersync/nvm/nvm_api.py`
- `artifacts/model_contract_nvm.json`
- `artifacts/nvm/examples/hypersync_docs.v2.json`
- `artifacts/nvm/examples/model_cache.v2.json`
- `artifacts/nvm/examples/shared_knowledge_graph.v2.json`
- `artifacts/nvm/examples/ico_service_docs.v2.json`
- `docs/nvm.md`

### Modified Files
- `tools/nvm/nvm_cli.py` (replaced with integrated version)
- `docs/nvm.md` (updated with v2 documentation)
- `MANIFEST.json` (integrated patch record)

## Relationship to Hardware Profiles and First-Run Flow

NVM blocks are a core part of the first-run bootstrap sequence described in
`07_documentation/first_run_nvm_bootstrap.md`.

The runtime MUST use NVM to persist the `hardware_profile` document (see
`03_specifications/environment/hardware_profile.schema.json`) and to
initialize the following blocks at minimum:

- A system spec/docs block, preloaded with HyperSync documentation.
- A user workspace block, bound to the default assistant/agent.
- A system experience block, used to capture what actually works on this
  specific device over time.

These blocks, combined with SDL shard descriptors and VNES policies, allow
HyperSync to tune its behavior for constrained or heterogeneous hardware
without hard-coding vendor-specific schemas.

## Storing Bootstrap Receipts (Optional)

Subject to local policy and privacy constraints, implementations MAY use NVM
blocks to store bootstrap receipts defined by
`03_specifications/environment/bootstrap_receipt.schema.json`.

When enabled, this allows the system to:

- Keep a local, queryable history of hardware profiles and first-run
  outcomes.
- Correlate changes in behavior with changes in hardware or configuration.

This MUST respect any `constraints` present in the hardware profile and
higher-level governance policies (e.g. `no_persistent_logs`).
