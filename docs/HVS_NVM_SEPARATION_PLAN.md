# HVS and NVM Component Separation Plan

**Created:** 2026-02-19  
**Status:** Proposed  
**Priority:** High - Core architectural correction

---

## Executive Summary

**Current State:** HVS and NVM are merged into a single `hvs-nvm` component

**Problem:** This violates the architectural separation of concerns documented in the backup specifications. HVS and NVM are distinct layers with different responsibilities and performance characteristics.

**Solution:** Separate into two independent components that integrate cleanly.

---

## Architectural Analysis

### From Backup Specifications

#### HVS (Hyper Vector System)
**Role:** "THE BACKBONE of HyperSync"

**Purpose:**
- Multi-geometry vector system for model-to-model communication
- RAM-speed vector operations (sub-millisecond)
- Network bridging and synchronization
- Fast semantic search and indexing

**Key Characteristics:**
- Fast (RAM-speed)
- In-memory operations
- Multi-geometry support (Hyperboloid, Poincaré, Euclidean, Lorentzian)
- Model communication substrate
- Synchronization engine

**Documented Name:** "HyperVector/Visual System" or "Hyper Vector System"

#### NVM (Non-Volatile Memory)
**Role:** "Persistent Semantic Storage Layer"

**Purpose:**
- Dense semantic blocks with persistent storage
- Disk-based storage (NVMe, SSD, Cloud)
- Cross-manifold knowledge sharing
- Documentation and knowledge base storage

**Key Characteristics:**
- Slow (disk-speed)
- Persistent storage
- HVS-indexed for semantic search
- Semantic blocks with metadata
- Multi-manifold "slow bridge"

**Documented Name:** "Non-Volatile Memory"

### Architectural Relationship

```
┌────────────────────────────────────────┐
│          AI Models Layer               │
└───────────────┬────────────────────────┘
                │
                ▼
┌────────────────────────────────────────┐
│     HVS (Hyper Vector System)          │
│  • Model-to-model communication        │
│  • Multi-geometry operations           │
│  • RAM-speed vector index              │
│  • Network bridging                    │
└───────────────┬────────────────────────┘
                │ (uses for persistence)
                ▼
┌────────────────────────────────────────┐
│     NVM (Non-Volatile Memory)          │
│  • Persistent semantic blocks          │
│  • Disk-based storage                  │
│  • HVS-indexed content                 │
│  • Cross-manifold sharing              │
└────────────────────────────────────────┘
```

**Key Insight:** HVS sits ABOVE NVM in the architecture. HVS uses NVM for persistence, but they are separate concerns.

---

## Why Separation is Critical

### 1. **Performance Characteristics**
- **HVS:** RAM-speed (< 1ms operations) - critical for real-time model communication
- **NVM:** Disk-speed (10-100ms operations) - optimized for persistence

Merging them obscures these distinct performance profiles.

### 2. **Deployment Scenarios**
- **HVS-only deployment:** Fast vector operations without persistence (ephemeral workloads)
- **NVM-only deployment:** Persistent storage accessed by external HVS instances
- **Integrated deployment:** Both components working together

Separation enables flexible deployment.

### 3. **Scaling Patterns**
- **HVS:** Scale horizontally with more RAM and CPU cores
- **NVM:** Scale with storage capacity and I/O throughput

Different scaling strategies require separate components.

### 4. **Testing and Development**
- **HVS:** Test vector operations, geometry transformations, synchronization
- **NVM:** Test persistence, semantic blocks, cross-manifold access

Separation enables focused testing.

### 5. **Specification Clarity**
The backup documentation clearly separates:
- `HVS_CORE_SPECIFICATION.md` (2,291 lines)
- `NVM_SPECIFICATION.md` (3,080 lines)
- `HVS_NVM_INTEGRATION.md` (integration layer)

This indicates they were always intended as separate components.

---

## Proposed Separation Plan

### Phase 1: Component Structure Creation

#### Create HVS Component
```
components/production/hvs/
├── meta.json                    # HVS metadata
├── specs/                       # HVS specifications
│   ├── geometry/               # Multi-geometry operations
│   ├── communication/          # Model-to-model communication
│   ├── synchronization/        # Sync engine specs
│   ├── indexing/               # Vector indexing specs
│   └── bridging/               # Network bridging specs
├── docs/
│   ├── README.md
│   ├── HVS_ARCHITECTURE.md
│   ├── GEOMETRY_GUIDE.md
│   └── COMMUNICATION_GUIDE.md
├── reference/                  # Reference implementations
├── generated/                  # STUNIR-generated code
└── tests/
```

#### Create NVM Component
```
components/production/nvm/
├── meta.json                    # NVM metadata
├── specs/                       # NVM specifications
│   ├── blocks/                 # Semantic block specs
│   ├── storage/                # Storage layer specs
│   ├── indexing/               # HVS integration specs
│   └── manifold/               # Multi-manifold specs
├── docs/
│   ├── README.md
│   ├── NVM_ARCHITECTURE.md
│   ├── BLOCK_SPECIFICATION.md
│   └── STORAGE_GUIDE.md
├── reference/                  # Reference implementations
├── generated/                  # STUNIR-generated code
└── tests/
```

#### Create Integration Component (Optional)
```
components/production/hvs-nvm-integration/
├── meta.json
├── specs/                       # Integration specs
│   └── hvs_nvm_integration_spec.json
├── docs/
│   └── INTEGRATION_GUIDE.md
└── tests/
```

### Phase 2: Specification Migration

#### From Current hvs-nvm/specs → HVS specs
**Current files that belong to HVS:**
- `consensus/geometric_bft_mechanisms_spec.json` → hvs/specs/consensus/
- `domains/lorentzian_*.json` → hvs/specs/geometry/
- `domains/domain_*.json` → hvs/specs/bridging/

**Rationale:** These deal with geometry, domains, and network bridging - core HVS concerns.

#### From Current hvs-nvm/specs → NVM specs
**Current files that belong to NVM:**
- `data/database_manifold_mapping.json` → nvm/specs/storage/
- `data/data_integration_system.json` → nvm/specs/blocks/
- `data/streaming_data_system.json` → nvm/specs/storage/
- `data/*_integration.json` → nvm/specs/storage/

**Rationale:** These deal with persistent storage, databases, and data integration - core NVM concerns.

#### Test Data Files
**Current test files (data/test_*.json):**
- Should be moved to `work_artifacts/test_results/` (not component specs)
- These are test outputs, not specifications

**Rationale:** Test data doesn't belong in specs/ directory.

### Phase 3: Metadata Updates

#### HVS meta.json
```json
{
  "component": {
    "name": "hvs",
    "full_name": "HyperVector/Visual System",
    "version": "2.0.0",
    "status": "production",
    "maturity": "stable"
  },
  "classification": {
    "type": "foundation",
    "layer": "communication-substrate",
    "domain": ["vectors", "geometry", "model-communication", "synchronization"]
  },
  "relationships": {
    "depends_on": ["agua"],
    "used_by": ["pct", "mom", "haw", "ascif", "sdl", "vnes", "mxfy"],
    "integrates_with": ["nvm", "stunir"],
    "performance_tier": "fast"
  },
  "performance": {
    "target_latency": "sub-millisecond",
    "storage_type": "RAM",
    "scalability": "horizontal"
  }
}
```

#### NVM meta.json
```json
{
  "component": {
    "name": "nvm",
    "full_name": "Non-Volatile Memory",
    "version": "2.0.0",
    "status": "production",
    "maturity": "stable"
  },
  "classification": {
    "type": "foundation",
    "layer": "persistent-storage",
    "domain": ["storage", "persistence", "semantic-blocks", "knowledge-base"]
  },
  "relationships": {
    "depends_on": ["hvs"],
    "used_by": ["pct", "sdl", "haw"],
    "integrates_with": ["hvs", "stunir"],
    "performance_tier": "slow"
  },
  "performance": {
    "target_latency": "10-100ms",
    "storage_type": "NVMe/Disk",
    "scalability": "vertical"
  }
}
```

### Phase 4: AI Development Guide Updates

Update `AI_DEVELOPMENT_GUIDE.md` lines 73-82 to reflect separation:

```markdown
components/
├── production/
│   ├── agua/           # Automated Geometric Universal Architecture
│   ├── pct/            # Pathfinder → Cartographer → Trailblazer
│   ├── sdl/            # Semantic Data Lake
│   ├── hvs/            # HyperVector/Visual System (RAM-speed vectors)
│   ├── nvm/            # Non-Volatile Memory (persistent storage)
│   ├── vnes/           # Vector Native Extension System
│   ├── mom/            # Machine Orchestration Management
│   ├── haw/            # Human-AI Workspace
│   ├── ascif/          # Adaptive Social-Consciousness Integration Framework
│   └── mxfy/           # Make X for Y
```

### Phase 5: Documentation Updates

#### Create HVS Documentation
**Based on:** `HVS_CORE_SPECIFICATION.md` (backup)

**New files:**
1. `components/production/hvs/docs/README.md`
2. `components/production/hvs/docs/HVS_ARCHITECTURE.md`
3. `components/production/hvs/docs/GEOMETRY_GUIDE.md`
4. `components/production/hvs/docs/COMMUNICATION_GUIDE.md`
5. `docs/04_COMPONENTS/HVS.md`

#### Create NVM Documentation
**Based on:** `NVM_SPECIFICATION.md` (backup)

**New files:**
1. `components/production/nvm/docs/README.md`
2. `components/production/nvm/docs/NVM_ARCHITECTURE.md`
3. `components/production/nvm/docs/BLOCK_SPECIFICATION.md`
4. `components/production/nvm/docs/STORAGE_GUIDE.md`
5. `docs/04_COMPONENTS/NVM.md`

#### Update Integration Documentation
**Based on:** `HVS_NVM_INTEGRATION.md` (backup)

**New file:**
- `docs/04_COMPONENTS/HVS_NVM_INTEGRATION.md`

### Phase 6: README.md Updates

Update main README component list:

```markdown
### Foundation Layer
- **AGUA** (Automated Geometric Universal Architecture) - Geometric substrate
- **PCT** (Pathfinder → Cartographer → Trailblazer) - Spatial reasoning
- **SDL** (Semantic Data Lake) - Unified semantic data management

### Memory & Communication
- **HVS** (HyperVector/Visual System) - Fast vector operations and model communication
- **NVM** (Non-Volatile Memory) - Persistent semantic storage
- **VNES** (Vector Native Extension System) - Vector-based extensibility

### Orchestration & Ethics
- **MOM** (Machine Orchestration Management) - Multi-model coordination
- **HAW** (Human-AI Workspace) - Human-agent interaction
- **ASCIF** (Adaptive Social-Consciousness Integration Framework) - Ethical guidelines
- **MXFY** (Make X for Y) - Intent parsing and synthesis
```

---

## Implementation Steps

### Step 1: Create Component Directories (Week 1, Days 1-2)
- [ ] Create `components/production/hvs/` structure
- [ ] Create `components/production/nvm/` structure
- [ ] Copy backup specifications to new locations

### Step 2: Migrate Specifications (Week 1, Days 3-4)
- [ ] Analyze current hvs-nvm specs
- [ ] Classify each spec as HVS or NVM
- [ ] Move/copy specs to appropriate locations
- [ ] Move test data to work_artifacts/

### Step 3: Create Component Metadata (Week 1, Day 5)
- [ ] Create hvs/meta.json
- [ ] Create nvm/meta.json
- [ ] Update dependency relationships

### Step 4: Create Component Documentation (Week 2, Days 1-3)
- [ ] Extract HVS docs from backup specs
- [ ] Extract NVM docs from backup specs
- [ ] Create component README files
- [ ] Create architecture documentation
- [ ] Create usage guides

### Step 5: Update Project Documentation (Week 2, Days 4-5)
- [ ] Update AI_DEVELOPMENT_GUIDE.md
- [ ] Update README.md
- [ ] Update CORE_CATALOG.json
- [ ] Create HVS.md and NVM.md in docs/04_COMPONENTS/
- [ ] Update cross-references

### Step 6: Handle hvs-nvm Component (Week 3)
**Decision Point:** What to do with `components/production/hvs-nvm/`?

**Option A: Delete (Recommended)**
- Mark as deprecated
- Remove from production
- Update all references to use hvs or nvm

**Option B: Keep as Integration Component**
- Rename to `hvs-nvm-integration`
- Move to experimental
- Document as integration layer only

**Recommendation:** Option A - Clean separation is clearer

### Step 7: Update CORE_CATALOG.json (Week 3)
```json
{
  "hvs": {
    "component": {"name": "hvs", "version": "2.0.0"},
    "relationships": {
      "depends_on": ["agua"],
      "used_by": ["pct", "mom", "haw", "ascif", "sdl", "vnes", "mxfy"],
      "integrates_with": ["nvm"]
    }
  },
  "nvm": {
    "component": {"name": "nvm", "version": "2.0.0"},
    "relationships": {
      "depends_on": ["hvs"],
      "used_by": ["pct", "sdl", "haw"],
      "integrates_with": ["hvs"]
    }
  }
}
```

### Step 8: Create STUNIR Machine Plans (Week 4)
- [ ] Create hvs/specs/stunir_machine_plan.json
- [ ] Create nvm/specs/stunir_machine_plan.json
- [ ] Define generation targets (Rust, Python, C)

---

## Updated Component Count

**Before Separation:** 9 production components
- agua, pct, sdl, hvs-nvm, vnes, mom, haw, ascif, mxfy

**After Separation:** 10 production components
- agua, pct, sdl, **hvs, nvm**, vnes, mom, haw, ascif, mxfy

---

## Benefits of Separation

### 1. **Architectural Clarity**
- HVS role as "THE BACKBONE" is clear
- NVM role as persistent storage is clear
- Performance characteristics are explicit

### 2. **Better Specifications**
- Focused specs for each layer
- Clearer dependencies
- Easier to understand and maintain

### 3. **Flexible Deployment**
- Deploy HVS without NVM for ephemeral workloads
- Deploy NVM with lightweight HVS for storage-focused use
- Scale components independently

### 4. **Development Efficiency**
- Teams can work on HVS and NVM independently
- Faster iteration on each layer
- Clearer testing boundaries

### 5. **STUNIR Code Generation**
- Separate code generation for HVS and NVM
- Different optimization targets (RAM vs disk)
- Clearer generated code structure

---

## Risks and Mitigation

### Risk 1: Breaking Existing References
**Impact:** High  
**Mitigation:** 
- Update all documentation references
- Update CORE_CATALOG.json
- Create migration guide
- Test all component interactions

### Risk 2: Specification Overlap
**Impact:** Medium  
**Mitigation:**
- Carefully classify each spec file
- Document integration points
- Create clear interface definitions

### Risk 3: Performance Regression
**Impact:** Medium  
**Mitigation:**
- Maintain integration tests
- Profile performance before/after
- Optimize HVS-NVM communication path

---

## Success Criteria

- ✅ HVS and NVM have separate component directories
- ✅ All specifications correctly classified
- ✅ Component metadata accurately reflects dependencies
- ✅ Documentation clearly explains architecture
- ✅ AI Development Guide updated
- ✅ README.md reflects separation
- ✅ CORE_CATALOG.json updated
- ✅ No broken references in documentation

---

## Timeline

**Total Duration:** 4 weeks

- **Week 1:** Component structure and specification migration
- **Week 2:** Documentation creation and updates
- **Week 3:** Integration and testing
- **Week 4:** STUNIR machine plans and validation

---

## Next Immediate Actions

1. **Get user approval** for separation plan
2. **Create hvs/ and nvm/ directories** in components/production/
3. **Migrate backup specifications** to new locations
4. **Create component metadata** (meta.json files)
5. **Begin documentation extraction** from backup specs

---

**Document Status:** Draft  
**Review Required:** Yes  
**User Approval Needed:** Yes  
**Last Updated:** 2026-02-19