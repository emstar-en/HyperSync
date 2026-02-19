# HyperSync Documentation Index

**Version:** 2.0.0  
**Last Updated:** 2026-02-19  
**Total Documents:** 63

Welcome to the HyperSync documentation index. This file provides a comprehensive cross-referenced guide to all available documentation.

---

## Quick Navigation

- [Getting Started](#getting-started) - New user onboarding
- [Core Concepts](#core-concepts) - Foundational principles
- [Architecture](#architecture) - System design
- [Components](#components) - Component deep dives
- [Internals](#internals) - Implementation details
- [Operations](#operations) - Running HyperSync
- [Security](#security) - Security considerations
- [Advanced Topics](#advanced-topics) - Advanced concepts
- [STUNIR](#stunir) - Code generation
- [Reference](#reference) - Reference materials
- [VNES](#vnes) - Extension system

---

## Getting Started

**Location:** `docs/01_GETTING_STARTED/`  
**Purpose:** Entry point for newcomers

| Document | Description | Key Topics |
|----------|-------------|------------|
| [OVERVIEW.md](01_GETTING_STARTED/OVERVIEW.md) | System overview and architecture layers | Geometry Engine, Consensus, Agents, Capsules |
| [VISION.md](01_GETTING_STARTED/VISION.md) | Project vision and philosophy | Geometric orchestration, autonomous swarms |
| [GLOSSARY.md](01_GETTING_STARTED/GLOSSARY.md) | Terms and definitions | Terminology reference |

**Start Here:** Read OVERVIEW.md → VISION.md → GLOSSARY.md

---

## Core Concepts

**Location:** `docs/02_CORE_CONCEPTS/`  
**Purpose:** Fundamental understanding of HyperSync

| Document | Description | Related Docs |
|----------|-------------|--------------|
| [GEOMETRIC_PRINCIPLES.md](02_CORE_CONCEPTS/GEOMETRIC_PRINCIPLES.md) | Complete guide to geometric physics architecture | Architecture → HIGH_LEVEL_ARCHITECTURE |
| [CORE_PRINCIPLES.md](02_CORE_CONCEPTS/CORE_PRINCIPLES.md) | Foundational design principles | Internals → ALGORITHMS |
| [DETERMINISM_TIERS.md](02_CORE_CONCEPTS/DETERMINISM_TIERS.md) | D0-D3 determinism levels and Merkle seed trees | Components → AGUA |
| [HOLONIC_ARCHITECTURE.md](02_CORE_CONCEPTS/HOLONIC_ARCHITECTURE.md) | Fractal/recursive orchestration | Architecture → EXECUTION_MODEL |
| [BOUNDARIES.md](02_CORE_CONCEPTS/BOUNDARIES.md) | System boundaries and constraints | Security → THREAT_MODEL |

**Critical Reading:** GEOMETRIC_PRINCIPLES.md is essential for understanding HyperSync's unique approach.

---

## Architecture

**Location:** `docs/03_ARCHITECTURE/`  
**Purpose:** System design and structure

| Document | Description | Related Docs |
|----------|-------------|--------------|
| [HIGH_LEVEL_ARCHITECTURE.md](03_ARCHITECTURE/HIGH_LEVEL_ARCHITECTURE.md) | Complete system architecture | Getting Started → OVERVIEW |
| [COMPONENT_MODEL.md](03_ARCHITECTURE/COMPONENT_MODEL.md) | How components interact | Components → * |
| [DATA_FLOW.md](03_ARCHITECTURE/DATA_FLOW.md) | Data flow patterns | Internals → PROTOCOLS |
| [STATE_MANAGEMENT.md](03_ARCHITECTURE/STATE_MANAGEMENT.md) | State handling strategies | Core Concepts → GEOMETRIC_PRINCIPLES |
| [EXECUTION_MODEL.md](03_ARCHITECTURE/EXECUTION_MODEL.md) | Execution patterns and phases | Core Concepts → HOLONIC_ARCHITECTURE |
| [DISTRIBUTION_MODEL.md](03_ARCHITECTURE/DISTRIBUTION_MODEL.md) | Distribution architecture | Operations → DEPLOYMENT |
| [SYNCHRONIZATION.md](03_ARCHITECTURE/SYNCHRONIZATION.md) | Sync mechanisms | Internals → PROTOCOLS |

---

## Components

**Location:** `docs/04_COMPONENTS/`  
**Purpose:** Individual component documentation

### Foundation Components

| Component | Document | Description | Dependencies |
|-----------|----------|-------------|--------------|
| **AGUA** | [AGUA.md](04_COMPONENTS/AGUA.md) | Determinism engine and execution supervisor | None (foundation) |
| **PCT** | Component docs in `components/production/pct/docs/` | Pathfinder → Cartographer → Trailblazer workflow | AGUA |
| **SDL** | Missing - needs creation | Semantic Data Lake | AGUA |

### Memory & State

| Component | Document | Description | Dependencies |
|-----------|----------|-------------|--------------|
| **HVS-NVM** | [HVS_NVM.md](04_COMPONENTS/HVS_NVM.md) | Hierarchical Vector Store / Non-Volatile Memory | None (substrate) |
| **VNES** | [VNES.md](04_COMPONENTS/VNES.md) | Vector-Native Extension System | AGUA |

### Orchestration

| Component | Document | Description | Dependencies |
|-----------|----------|-------------|--------------|
| **MOM** | [MOM.md](04_COMPONENTS/MOM.md) | Multi-Model Orchestration Manager | AGUA, PCT |
| **HAW** | Missing - needs creation | Human-AI Workspace | AGUA, PCT, MOM |
| **ASCIF** | Missing - needs creation | Adaptive Safety Framework | AGUA |
| **MXFY** | Missing - needs creation | Intent synthesis (Make X for Y) | AGUA, PCT, SDL |

**See Also:** Component-specific documentation in `components/production/*/docs/`

---

## Internals

**Location:** `docs/05_INTERNALS/`  
**Purpose:** Implementation details

### Core Implementation

| Document | Description | Related Docs |
|----------|-------------|--------------|
| [ALGORITHMS.md](05_INTERNALS/ALGORITHMS.md) | Core algorithms | Core Concepts → CORE_PRINCIPLES |
| [DATA_STRUCTURES.md](05_INTERNALS/DATA_STRUCTURES.md) | Data structure designs | Architecture → STATE_MANAGEMENT |
| [PROTOCOLS.md](05_INTERNALS/PROTOCOLS.md) | Communication protocols | Architecture → SYNCHRONIZATION |
| [RUNTIME_BEHAVIOR.md](05_INTERNALS/RUNTIME_BEHAVIOR.md) | Runtime characteristics | Operations → STARTUP_SEQUENCE |
| [ERROR_HANDLING.md](05_INTERNALS/ERROR_HANDLING.md) | Error handling patterns | Operations → DEBUGGING |
| [LOGGING.md](05_INTERNALS/LOGGING.md) | Logging system | Operations → MONITORING_GUIDE |
| [OPTIMIZATION.md](05_INTERNALS/OPTIMIZATION.md) | Performance optimization | Advanced Topics → * |

### Component Internals

**AGUA Internals:** `05_INTERNALS/agua/`
- [INTERCEPTOR_LOGIC.md](05_INTERNALS/agua/INTERCEPTOR_LOGIC.md) - Request interception and determinism enforcement

**PCT Internals:** `05_INTERNALS/pct/`
- [STATE_MACHINE.md](05_INTERNALS/pct/STATE_MACHINE.md) - PCT phase state machine

### Geometry Mathematics

**Location:** `05_INTERNALS/geometry/`

| Document | Description | Prerequisites |
|----------|-------------|---------------|
| [RIEMANNIAN_GEOMETRY.md](05_INTERNALS/geometry/RIEMANNIAN_GEOMETRY.md) | Manifold mathematics | Core Concepts → GEOMETRIC_PRINCIPLES |
| [DIFFERENTIAL_FORMS.md](05_INTERNALS/geometry/DIFFERENTIAL_FORMS.md) | Differential geometry | RIEMANNIAN_GEOMETRY |
| [TENSOR_CALCULUS.md](05_INTERNALS/geometry/TENSOR_CALCULUS.md) | Tensor operations | RIEMANNIAN_GEOMETRY |
| [FIBER_BUNDLES.md](05_INTERNALS/geometry/FIBER_BUNDLES.md) | Fiber bundle theory | DIFFERENTIAL_FORMS |
| [GAUGE_THEORY.md](05_INTERNALS/geometry/GAUGE_THEORY.md) | Gauge theory applications | FIBER_BUNDLES |
| [LIE_GROUPS.md](05_INTERNALS/geometry/LIE_GROUPS.md) | Lie group mathematics | TENSOR_CALCULUS |

---

## Operations

**Location:** `docs/06_OPERATIONS/`  
**Purpose:** Running and maintaining HyperSync

| Document | Description | Related Docs |
|----------|-------------|--------------|
| [STARTUP_SEQUENCE.md](06_OPERATIONS/STARTUP_SEQUENCE.md) | System initialization | Architecture → EXECUTION_MODEL |
| [SHUTDOWN_SEQUENCE.md](06_OPERATIONS/SHUTDOWN_SEQUENCE.md) | Graceful shutdown | STARTUP_SEQUENCE |
| [MONITORING_GUIDE.md](06_OPERATIONS/MONITORING_GUIDE.md) | Operational monitoring | Internals → LOGGING |
| [SANDBOXING.md](06_OPERATIONS/SANDBOXING.md) | Isolation and sandboxing | Security → THREAT_MODEL |

**Missing:** DEPLOYMENT.md, DEBUGGING.md, TROUBLESHOOTING.md (to be created)

---

## Security

**Location:** `docs/07_SECURITY/`  
**Purpose:** Security considerations

| Document | Description | Related Docs |
|----------|-------------|--------------|
| [threat_model.md](07_SECURITY/threat_model.md) | Threat modeling | Core Concepts → BOUNDARIES |
| [access_control.md](07_SECURITY/access_control.md) | Access control mechanisms | ASCIF component |
| [data_protection.md](07_SECURITY/data_protection.md) | Data protection strategies | HVS-NVM component |
| [audit_trail.md](07_SECURITY/audit_trail.md) | Audit logging | Internals → LOGGING |
| [PRIVACY_GEOMETRY.md](07_SECURITY/PRIVACY_GEOMETRY.md) | Geometric privacy models | Core Concepts → GEOMETRIC_PRINCIPLES |

**Missing:** OVERVIEW.md (security overview to be created)

---

## Advanced Topics

**Location:** `docs/08_ADVANCED_TOPICS/`  
**Purpose:** Advanced concepts and patterns

| Document | Description | Prerequisites |
|----------|-------------|---------------|
| [THERMODYNAMIC_LOGIC.md](08_ADVANCED_TOPICS/THERMODYNAMIC_LOGIC.md) | Thermodynamic principles in orchestration | Core Concepts → GEOMETRIC_PRINCIPLES |
| [EXPLORATORY_DYNAMICS.md](08_ADVANCED_TOPICS/EXPLORATORY_DYNAMICS.md) | Exploration strategies | Core Concepts → DETERMINISM_TIERS |
| [DECISION_LOGIC.md](08_ADVANCED_TOPICS/DECISION_LOGIC.md) | Decision-making patterns | Architecture → EXECUTION_MODEL |
| [ACCEPTANCE_GATES.md](08_ADVANCED_TOPICS/ACCEPTANCE_GATES.md) | Gate mechanisms and validation | Core Concepts → HOLONIC_ARCHITECTURE |
| [EPISODE_RECORDER.md](08_ADVANCED_TOPICS/EPISODE_RECORDER.md) | Episode recording for replay | Core Concepts → DETERMINISM_TIERS |
| [PSYCHOMETRIC_TENSOR.md](08_ADVANCED_TOPICS/PSYCHOMETRIC_TENSOR.md) | Psychometric concepts | Internals/geometry → TENSOR_CALCULUS |

---

## STUNIR

**Location:** `docs/09_STUNIR/`  
**Purpose:** Code generation system

| Document | Description | Related Docs |
|----------|-------------|--------------|
| [OVERVIEW.md](09_STUNIR/OVERVIEW.md) | STUNIR system overview | Components → specs/ |

**Missing:** SPECIFICATION_FORMAT.md, CODE_GENERATION.md, EXAMPLES.md (to be created)

**See Also:** `tools/stunir/` for implementation

---

## Reference

**Location:** `docs/10_REFERENCE/`  
**Purpose:** Reference materials

| Document | Description | Use Case |
|----------|-------------|----------|
| [BIBLIOGRAPHY.md](10_REFERENCE/BIBLIOGRAPHY.md) | References and citations | Research background |
| [MODEL_CONTEXT.md](10_REFERENCE/MODEL_CONTEXT.md) | Context for AI models | AI agent development |
| [TUI_INTEGRATION.md](10_REFERENCE/TUI_INTEGRATION.md) | Terminal UI integration | HAW component |
| [NON_FUNCTIONAL_REQUIREMENTS.md](10_REFERENCE/NON_FUNCTIONAL_REQUIREMENTS.md) | NFRs | Architecture decisions |
| [MACHINE_GUIDELINES.md](10_REFERENCE/MACHINE_GUIDELINES.md) | Guidelines for AI agents | AI agent development |
| [CAPABILITIES.md](10_REFERENCE/CAPABILITIES.md) | System capabilities | Feature discovery |

---

## VNES

**Location:** `docs/11_VNES/`  
**Purpose:** Extension system details

| Document | Description | Related Docs |
|----------|-------------|--------------|
| [VNES_OVERVIEW.md](11_VNES/VNES_OVERVIEW.md) | VNES system overview | Components → VNES |
| [CAPSULE_SPEC.md](11_VNES/CAPSULE_SPEC.md) | Capsule specification format | Getting Started → OVERVIEW |
| [AI_INTERFACE.md](11_VNES/AI_INTERFACE.md) | AI integration patterns | Reference → MODEL_CONTEXT |
| [RUNTIME_ARCHITECTURE.md](11_VNES/RUNTIME_ARCHITECTURE.md) | VNES runtime details | Architecture → EXECUTION_MODEL |
| [psychometric_tensor.md](11_VNES/psychometric_tensor.md) | Psychometric concepts | Advanced Topics → PSYCHOMETRIC_TENSOR |

**See Also:** Component documentation in `components/production/vnes/`

---

## Cross-Cutting Concerns

### Determinism

**Primary:** Core Concepts → DETERMINISM_TIERS  
**Related:**
- Components → AGUA
- Internals/agua → INTERCEPTOR_LOGIC
- Advanced Topics → EPISODE_RECORDER
- Core Concepts → HOLONIC_ARCHITECTURE (Merkle seed trees)

### Geometry

**Primary:** Core Concepts → GEOMETRIC_PRINCIPLES  
**Related:**
- Internals/geometry → All geometry mathematics
- Architecture → STATE_MANAGEMENT
- Security → PRIVACY_GEOMETRY
- Components → AGUA

### Orchestration

**Primary:** Core Concepts → HOLONIC_ARCHITECTURE  
**Related:**
- Components → MOM
- Architecture → EXECUTION_MODEL
- Advanced Topics → THERMODYNAMIC_LOGIC

### Capsules

**Primary:** VNES → CAPSULE_SPEC  
**Related:**
- Getting Started → OVERVIEW
- Components → VNES

---

## Documentation Gaps

The following documentation needs to be created:

### High Priority
- [ ] Quick Start Guide (`01_GETTING_STARTED/QUICK_START.md`)
- [ ] Component docs for SDL, HAW, ASCIF, MXFY
- [ ] Deployment Guide (`06_OPERATIONS/DEPLOYMENT.md`)
- [ ] Security Overview (`07_SECURITY/OVERVIEW.md`)

### Medium Priority
- [ ] Debugging Guide (`06_OPERATIONS/DEBUGGING.md`)
- [ ] Troubleshooting Guide (`06_OPERATIONS/TROUBLESHOOTING.md`)
- [ ] STUNIR Specification Format (`09_STUNIR/SPECIFICATION_FORMAT.md`)
- [ ] STUNIR Code Generation (`09_STUNIR/CODE_GENERATION.md`)
- [ ] STUNIR Examples (`09_STUNIR/EXAMPLES.md`)

### Component-Specific Docs
Each component should have:
- [ ] `components/production/sdl/docs/` - SDL documentation
- [ ] `components/production/hvs-nvm/docs/` - HVS-NVM documentation  
- [ ] `components/production/vnes/docs/` - VNES documentation
- [ ] `components/production/mom/docs/` - MOM documentation
- [ ] `components/production/haw/docs/` - HAW documentation
- [ ] `components/production/ascif/docs/` - ASCIF documentation
- [ ] `components/production/mxfy/docs/` - MXFY documentation

---

## Navigation Tips

### For Newcomers
1. Start with `01_GETTING_STARTED/OVERVIEW.md`
2. Read `02_CORE_CONCEPTS/GEOMETRIC_PRINCIPLES.md`
3. Review `03_ARCHITECTURE/HIGH_LEVEL_ARCHITECTURE.md`
4. Explore component docs in `04_COMPONENTS/`

### For Developers
1. Review `02_CORE_CONCEPTS/` for principles
2. Study `03_ARCHITECTURE/` for system design
3. Deep dive into `05_INTERNALS/` for implementation
4. Reference `components/production/*/docs/` for specifics

### For Operators
1. Read `06_OPERATIONS/STARTUP_SEQUENCE.md`
2. Review `06_OPERATIONS/MONITORING_GUIDE.md`
3. Study `07_SECURITY/` for security practices
4. Check `10_REFERENCE/NON_FUNCTIONAL_REQUIREMENTS.md`

### For AI Models
1. Read `10_REFERENCE/MODEL_CONTEXT.md`
2. Review `10_REFERENCE/MACHINE_GUIDELINES.md`
3. Study `02_CORE_CONCEPTS/GEOMETRIC_PRINCIPLES.md`
4. Reference `AI_DEVELOPMENT_GUIDE.md` in project root

---

## External Documentation

- **Component Catalog:** `../../CORE_CATALOG.json` - Complete component metadata
- **AI Development Guide:** `../../AI_DEVELOPMENT_GUIDE.md` - For AI agents
- **README:** `../../README.md` - Project overview
- **Tier Hierarchy:** `../../specifications/HYPERSYNC_COMPLETE_TIER_HIERARCHY.md`

---

## Contributing to Documentation

When adding or updating documentation:

1. **Follow the structure** - Place docs in the appropriate category
2. **Update this index** - Add cross-references
3. **Link related docs** - Create connections between topics
4. **Use consistent naming** - UPPERCASE for titles
5. **Add to navigation** - Update relevant navigation sections

---

**Last Updated:** 2026-02-19  
**Maintained By:** HyperSync Core Team

For questions or suggestions, please refer to the main project README.
