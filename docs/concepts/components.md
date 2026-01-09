# HyperSync Components

## Component Architecture

HyperSync is composed of several major subsystems:

### 1. Core Engine (`05_implementation/core/`)
- **Hyperbolic Geometry**: Geometric computations and transformations
- **BFT Consensus**: Byzantine fault-tolerant consensus
- **Consensus**: General consensus mechanisms
- **ICO Network**: Inter-component orchestration network
- **ICO Sync**: ICO synchronization layer
- **NVM**: Non-volatile memory management
- **Planner**: Execution planning and optimization
- **Receipts**: Receipt generation and verification
- **Surreal**: Surreal systems integration

### 2. Component Definitions (`04_components/`)
- **Agents**: Autonomous orchestration agents
- **Operators**: Atomic computational operators
- **Policies**: Declarative policy definitions
- **Governance**: Governance policies and rules
- **Capabilities**: System capability definitions

### 3. Specifications (`03_specifications/`)
- **Core Specs**: Formal system specifications
- **Schemas**: JSON schemas for validation
- **Extensions**: Extension specifications

### 4. Code Generation (`05_implementation/codegen/`)
- **Templates**: Code generation templates
- **Implementations**: Generated implementations
- **CLI**: Code generation CLI tools

### 5. APIs (`06_apis/`)
- **REST**: REST API definitions
- **gRPC**: gRPC service definitions
- **Internal**: Internal API specifications

### 6. Testing (`08_tests/`)
- **Unit Tests**: Component unit tests
- **Conformance Tests**: Specification conformance tests
- **Integration Tests**: System integration tests
- **Benchmarks**: Performance benchmarks

### 7. Tools (`10_tools/`)
- **Validators**: Specification validators
- **Generators**: Code and documentation generators
- **Scripts**: Build and utility scripts
- **CI**: Continuous integration tools

### 8. Extensions (`11_extensions/`)
- **Contrib**: Community contributions
- **UI**: User interface extensions
- **Experimental**: Experimental features

## Component Interactions

Components interact through:
- **Operator invocation**: Agents invoke operators
- **Policy enforcement**: Policies constrain behavior
- **Receipt generation**: All operations generate receipts
- **API calls**: Components communicate via APIs
- **Event system**: Asynchronous event propagation

## Bootstrap-Critical Components

The following components are considered critical to a successful first-run
bootstrap sequence:

- **NVM**: Provides durable storage for hardware profiles, system docs,
  user workspace, and system experience.
- **SDL**: Discovers hardware-appropriate patterns and configuration
  shards.
- **VNES**: Selects and activates extensions consistent with the detected
  hardware profile and governance/policy constraints.
- **IAM (Initialization Assistant Model)**: Orchestrates the first-run
  experience, using NVM, SDL, and VNES to present and apply sensible
  defaults for this installation.
