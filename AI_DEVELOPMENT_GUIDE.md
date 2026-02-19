# AI Development Guide for HyperSync

**For AI Models/Agents Working on This Project**

This guide helps AI assistants understand the HyperSync project structure, navigation patterns, and development workflow.

---

## 📂 Project Structure Overview

```
HyperSync/build/current/
├── components/           # Core components (production + experimental)
├── specifications/       # STUNIR specs and tier definitions
├── tools/               # Development utilities
├── workspace/           # Active development environment
├── shared/              # Common protocols and types
├── README.md            # Main project documentation
├── CORE_CATALOG.json    # Component metadata index
└── AI_DEVELOPMENT_GUIDE.md  # This file
```

---

## 🧭 Directory Reference

### 1. `/components/` - Core Components

**Purpose**: Contains all HyperSync components

**Structure**:
```
components/
├── production/          # 9 stable, production-ready components
│   ├── agua/           # Automated Geometric Universal Architecture
│   ├── pct/            # Pathfinder → Cartographer → Trailblazer
│   ├── sdl/            # Semantic Data Lake
│   ├── hvs/            # HyperVector/Visual System
│   ├── nvs/            # Non-Volatile Memory
│   ├── vnes/           # Vector Native Extension System
│   ├── mom/            # Machine Orchestration Management
│   ├── haw/            # Human-AI Workspace
│   ├── ascif/          # Adaptive Social-Consciousness Integration Framework
│   └── mxfy/           # Make X for Y
└── experimental/
    └── _template/      # Template for new components
```

**Each Component Directory Contains**:
- `meta.json` - Component metadata (name, version, tier, dependencies, operations)
- `specs/` - STUNIR specifications (JSON format)
- `docs/` - Component documentation
- `tests/` - Test cases
- `examples/` - Usage examples
- `reference/` - Reference implementations
- `analysis/` - Performance analysis

**How to Use**:
1. **Find a component**: Check `CORE_CATALOG.json` for complete metadata
2. **Read specs**: Start with `specs/` for formal specifications
3. **Check meta.json**: Understand dependencies and tier classification

**Example - Working with AGUA**:
```bash
# Read component metadata
components/production/agua/meta.json

# Review specifications
components/production/agua/specs/agua_geometry_spec.json

# Check documentation
components/production/agua/docs/AGUA_SYSTEM_DEFINITION.md
```

---

### 2. `/specifications/` - STUNIR Specs & Tier Definitions

**Purpose**: Formal specifications and tier system documentation

**Structure**:
```
specifications/
├── core/                           # Core tier specifications
│   ├── *.json                      # Individual operation specs
│   ├── *.tar.gz                    # Compressed spec bundles
│   └── CORE_TIER_PROMOTIONS_v2.md  # Component promotion history
├── CORE_TIER_PROMOTIONS.md         # Tier promotion guidelines
└── HYPERSYNC_COMPLETE_TIER_HIERARCHY.md  # Full tier system
```

**Key Files**:
- `HYPERSYNC_COMPLETE_TIER_HIERARCHY.md` - Understand tier boundaries (Core vs. Proprietary)
- `CORE_TIER_PROMOTIONS.md` - How components move between tiers
- `core/*.json` - Operation specifications in STUNIR format

**How to Use**:
1. **Understand tiers**: Read `HYPERSYNC_COMPLETE_TIER_HIERARCHY.md` first
2. **Review operations**: Check `core/` for specific operation specs
3. **Promotion process**: Consult `CORE_TIER_PROMOTIONS.md` for tier changes

---

### 3. `/tools/` - Development Utilities

**Purpose**: Tools for building, validating, and managing HyperSync

**Structure**:
```
tools/
├── component-creator/   # Bootstrap new components
├── live-analyzer/       # Usage analytics and performance tracking
├── stunir/             # STUNIR deterministic code generation
├── validators/         # Component validation tools
├── tier-filter/        # Tier isolation and export tool
└── index.json          # Tool registry
```

**Tool Descriptions**:

#### `component-creator/`
Creates new component scaffolding with proper structure.

**Usage**:
```bash
cd tools/component-creator
./create-component.sh --name my-component --type production
```

#### `live-analyzer/`
Tracks component usage, performance, and provides feedback.

**Usage**:
```python
cd tools/live-analyzer
python analyze.py --root ../..
```

#### `stunir/`
Generates deterministic code from STUNIR specifications.

**Usage**:
```bash
cd tools/stunir
python stunir.py --spec ../../components/production/agua/specs/agua_spec.json --output generated/
```

#### `validators/`
Validates component structure, metadata, and specifications.

#### `tier-filter/`
Filters and exports specific tiers (used to create Core tier export).

**Configuration**:
- `config/tier_rules.json` - Tier boundary rules
- `config/component_mapping.json` - Component tier assignments

---

### 4. `/workspace/` - Active Development Environment

**Purpose**: Live development and experimentation area

**Structure**:
```
workspace/
├── active/     # Current development work
├── analysis/   # Performance analysis results
└── assembly/   # Component integration workspace
```

**How to Use**:
1. **Start new work**: Create subdirectory in `active/`
2. **Run analysis**: Output results to `analysis/`
3. **Integration tests**: Use `assembly/` for multi-component testing

**Example Workflow**:
```bash
# Create workspace for new feature
workspace/active/feature-xyz/

# Run analysis
workspace/analysis/feature-xyz-results/

# Test integration
workspace/assembly/agua-pct-integration/
```

---

### 5. `/shared/` - Common Protocols and Types

**Purpose**: Shared interfaces, protocols, and type definitions

**Structure**:
```
shared/
├── protocols/   # Communication protocols
└── types/       # Common type definitions
```

**How to Use**:
- Reference when implementing component interactions
- Check for existing types before creating new ones
- Use protocols for inter-component communication

---

## 🔍 Navigation Patterns for AI Models

### Finding Information Quickly

#### 1. **Component Metadata** → `CORE_CATALOG.json`
Complete index of all components with metadata.

```json
{
  "core_tier": {
    "components": {
      "agua": {
        "component": { "name": "agua", "version": "2.0.0" },
        "relationships": { "used_by": ["pct", "mom", "haw"] }
      }
    }
  }
}
```

#### 2. **Component Details** → `components/production/{name}/meta.json`
Detailed metadata for specific component.

#### 3. **Specifications** → `components/production/{name}/specs/`
Formal STUNIR specifications.

#### 4. **Documentation** → `components/production/{name}/docs/`
Human-readable documentation.

#### 5. **Tier Information** → `specifications/HYPERSYNC_COMPLETE_TIER_HIERARCHY.md`
Complete tier system and boundaries.

---

## 🎯 Common AI Development Tasks

### Task 1: Understanding a Component

**Steps**:
1. Read `CORE_CATALOG.json` - Get overview
2. Read `components/production/{name}/meta.json` - Get metadata
3. Read `components/production/{name}/docs/` - Understand concepts
4. Read `components/production/{name}/specs/` - Review formal specs

**Example - Understanding AGUA**:
```bash
# 1. Check catalog
CORE_CATALOG.json → "agua" entry

# 2. Read metadata
components/production/agua/meta.json

# 3. Read docs
components/production/agua/docs/AGUA_SYSTEM_DEFINITION.md

# 4. Review specs
components/production/agua/specs/agua_geometry_spec.json
```

---

### Task 2: Adding a New Component

**Steps**:
1. Use `tools/component-creator/` to scaffold
2. Update `meta.json` with metadata
3. Add specifications to `specs/`
4. Write documentation in `docs/`
5. Add to `CORE_CATALOG.json`

**Template Location**: `components/experimental/_template/`

---

### Task 3: Validating Changes

**Steps**:
1. Run validators: `tools/validators/`
2. Check tier compliance: `tools/tier-filter/`
3. Verify specifications: `tools/stunir/`
4. Update documentation

---

### Task 4: Checking Dependencies

**Where to Look**:
1. `meta.json` → `relationships.depends_on`
2. `meta.json` → `relationships.used_by`
3. `CORE_CATALOG.json` → Cross-reference components

**Example**:
```json
// components/production/pct/meta.json
{
  "relationships": {
    "depends_on": ["agua"],
    "used_by": ["mom", "ascif"],
    "integrates_with": ["stunir"]
  }
}
```

---

## 📊 Indexing System

### Primary Index: `CORE_CATALOG.json`

**Structure**:
```json
{
  "core_tier": {
    "components": {
      "{component_name}": {
        "component": { /* basic info */ },
        "lifecycle": { /* promotion history */ },
        "classification": { /* type, layer, domain */ },
        "relationships": { /* dependencies */ },
        "operations": { /* available operations */ },
        "metadata": { /* tier, license, etc */ }
      }
    }
  }
}
```

**How to Use**:
1. **Find all components**: Iterate over `core_tier.components`
2. **Check dependencies**: Read `relationships.depends_on`
3. **Find operations**: Review `operations.categories`
4. **Verify tier**: Check `metadata.tier`

---

### Secondary Index: `tools/index.json`

Registry of available development tools.

---

## 🚀 Development Workflow for AI Models

### Standard Workflow

1. **Understand Context**
   - Read `README.md` for project overview
   - Check `CORE_CATALOG.json` for component registry
   - Review `AI_DEVELOPMENT_GUIDE.md` (this file)

2. **Locate Target Component**
   - Use `CORE_CATALOG.json` to find component
   - Navigate to `components/production/{name}/`
   - Read `meta.json` for metadata

3. **Review Specifications**
   - Check `specs/` for STUNIR specifications
   - Review `docs/` for documentation
   - Understand dependencies from `meta.json`

4. **Make Changes**
   - Edit component files
   - Update `meta.json` if needed
   - Regenerate code with STUNIR if applicable

5. **Validate**
   - Run `tools/validators/`
   - Check tier compliance with `tools/tier-filter/`
   - Update `CORE_CATALOG.json` if metadata changed

6. **Document**
   - Update component `docs/`
   - Update `README.md` if needed
   - Add to changelog

---

## 🔧 Key Configuration Files

### `meta.json` (Component Metadata)
Located in each component directory.

**Critical Fields**:
- `component.name` - Component identifier
- `component.version` - Semantic version
- `metadata.tier` - Tier classification (core, basic, pro, etc.)
- `relationships` - Dependencies and integrations
- `operations` - Available operations

### `tier_rules.json` (Tier Filter)
Located at `tools/tier-filter/config/tier_rules.json`

Defines tier boundaries and restrictions.

### `component_mapping.json` (Tier Assignments)
Located at `tools/tier-filter/config/component_mapping.json`

Maps components to tiers.

---

## 📝 Best Practices for AI Models

### DO:
✅ Always check `CORE_CATALOG.json` first for component overview
✅ Read `meta.json` to understand dependencies
✅ Use relative paths from project root
✅ Validate changes with `tools/validators/`
✅ Update `CORE_CATALOG.json` when adding/modifying components
✅ Follow existing patterns in component structure
✅ Check tier boundaries before making changes

### DON'T:
❌ Assume component locations without checking catalog
❌ Modify tier assignments without understanding tier system
❌ Add dependencies without checking compatibility
❌ Skip validation tools
❌ Create duplicate structures

---

## 🎓 Quick Reference

### Most Important Files (Read First)
1. `README.md` - Project overview
2. `CORE_CATALOG.json` - Component index
3. `specifications/HYPERSYNC_COMPLETE_TIER_HIERARCHY.md` - Tier system
4. `AI_DEVELOPMENT_GUIDE.md` - This file

### Component Discovery
```bash
# Find component metadata
→ CORE_CATALOG.json

# Get component details
→ components/production/{name}/meta.json

# Read specifications
→ components/production/{name}/specs/

# Check documentation
→ components/production/{name}/docs/
```

### Tool Usage
```bash
# Create component
→ tools/component-creator/

# Validate
→ tools/validators/

# Generate code
→ tools/stunir/

# Analyze
→ tools/live-analyzer/

# Export tier
→ tools/tier-filter/
```

---

## 🔗 Related Documentation

- **Project README**: `README.md`
- **Tier System**: `specifications/HYPERSYNC_COMPLETE_TIER_HIERARCHY.md`
- **Contribution Guidelines**: `CONTRIBUTING.md`
- **License**: `LICENSE`

---

## 💡 Tips for Efficient Navigation

1. **Start with the catalog**: `CORE_CATALOG.json` is your map
2. **Follow the structure**: Each component follows the same pattern
3. **Check dependencies first**: Avoid breaking existing integrations
4. **Use tools**: Don't manually validate - use `tools/validators/`
5. **Read meta.json**: It's the source of truth for each component

---

**Last Updated**: February 19, 2026  
**For**: AI Models/Agents working on HyperSync Core

**Questions?** Check `README.md` or component-specific `docs/` folders.
