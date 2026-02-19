# HyperSync Tier Filter Tool

Extract and validate Core tier files from full HyperSync project for open source distribution.

## Purpose

The Tier Filter Tool enables clean separation of Core tier (open source) from higher tiers (proprietary) by:
- Scanning all files for tier metadata
- Extracting only Core tier components and specifications
- Validating tier boundaries
- Generating catalogs of Core tier operations

## Features

✅ **Metadata-Driven Filtering** - Uses tier fields in meta.json and STUNIR specs  
✅ **Partial Component Support** - Extracts Core portions of multi-tier components  
✅ **Validation** - Ensures no proprietary code leaks into Core tier  
✅ **Catalog Generation** - Creates comprehensive operation listings  
✅ **Configurable** - JSON-based rules for tier boundaries  

## Installation

No installation required - Python 3.7+ standard library only.

```bash
cd HyperSync/build/current/tools/tier-filter
python filter.py --help
```

## Usage

### Extract Core Tier

```bash
python filter.py \
  --source ../../ \
  --output ../../../core-tier-export \
  --tier core \
  --validate
```

### Verify Tier Compliance

```bash
python filter.py \
  --verify-tier ../../../core-tier-export \
  --tier core
```

### Generate Core Tier Catalog

```bash
python filter.py \
  --source ../../../core-tier-export \
  --output ../../../core-tier-export \
  --generate-catalog \
  --output-catalog CORE_TIER_CATALOG.json
```

## Configuration

### Tier Rules (`config/tier_rules.json`)

Defines filtering rules per tier:
- **complexity**: Allowed computational complexity classes
- **exclude_patterns**: File patterns to exclude
- **include_patterns**: File patterns to include
- **forbidden_keywords**: Keywords that indicate proprietary code
- **required_license**: License requirement for tier

### Component Mapping (`config/component_mapping.json`)

Defines tier assignment for each component:
- **tier**: `full`, `partial`, or `none`
- **core_subdirs**: Subdirectories to include for partial components
- **core_operations**: Operations included in Core tier
- **proprietary_operations**: Operations excluded from Core tier

## Output Structure

```
core-tier-export/
├── components/
│   ├── production/
│   │   ├── agua/              # PARTIAL - core ops only
│   │   ├── pct/               # PARTIAL - basic workflow only
│   │   ├── sdl/               # PARTIAL - simple indexing only
│   │   ├── hvs-nvm/           # FULL
│   │   └── vnes/              # FULL
│   └── experimental/
├── specifications/
│   └── core/                  # Core tier specs only
├── tools/
│   ├── component-creator/
│   ├── live-analyzer/
│   ├── stunir/
│   └── tier-filter/           # Self-contained
├── workspace/
├── shared/
└── docs/
```

## Validation

The tool validates:
- ✅ No `*/basic/*`, `*/pro/*`, `*/advanced/*`, `*/enterprise/*` paths
- ✅ No ML/AI/quantum keywords in Core tier code
- ✅ All STUNIR specs have `"tier": "core"` metadata
- ✅ Only O(n) complexity operations included
- ✅ No forbidden keywords in source files

## Examples

### Full Workflow: Extract and Validate

```bash
# Extract Core tier
python filter.py \
  --source ../../ \
  --output ../../../core-tier-export \
  --tier core \
  --validate

# Verify export
python filter.py \
  --verify-tier ../../../core-tier-export \
  --tier core

# Generate catalog
python filter.py \
  --source ../../../core-tier-export \
  --output ../../../core-tier-export \
  --generate-catalog
```

### Sync to GitHub

```bash
# After successful extraction
cd ../../../core-tier-export
git init
git remote add origin https://github.com/emstar-en/HyperSync.git
git add .
git commit -m "Initial Core tier export"
git push -u origin main
```

## Component Tier Assignments

| Component | Tier | Rationale |
|-----------|------|-----------|
| **AGUA** | Partial | Core geometric primitives (O(n)) vs ML-enhanced (proprietary) |
| **PCT** | Partial | Basic workflow (O(n)) vs distributed orchestration (proprietary) |
| **SDL** | Partial | Simple indexing (O(n)) vs ML embeddings (proprietary) |
| **HVS-NVM** | Full | Core runtime substrate - fully open source |
| **VNES** | Full | Plugin architecture - fully open source |
| **MOM** | None | Requires Basic tier or higher |
| **HAW** | None | UI layer - requires Basic tier |
| **ASCIF** | None | Ethics/safety requires ML - Advanced tier |
| **MXFY** | None | Synthesis requires ML - Pro tier |

## Error Handling

The tool reports:
- **Errors**: Tier boundary violations (exit code 1)
- **Warnings**: Missing components, validation skips (exit code 0)

## Exit Codes

- `0` - Success (or warnings only)
- `1` - Validation failed or errors occurred

## Development

To modify tier rules:
1. Edit `config/tier_rules.json`
2. Edit `config/component_mapping.json`
3. Run validation tests
4. Re-export Core tier

## Related Documentation

- [Core Tier GitHub Strategy](../../../.abacusai/plans/core_tier_github_strategy.md)
- [Component Refactoring Plan](../../../.abacusai/plans/hypersync_refactoring_plan.md)
- [Tier Hierarchy](../../specifications/HYPERSYNC_COMPLETE_TIER_HIERARCHY.md)
- [Core Tier Promotions](../../specifications/CORE_TIER_PROMOTIONS.md)

## License

The Tier Filter Tool itself is part of HyperSync Core and licensed under Apache 2.0.
