# Kernel Capsule

The Kernel capsule is the heart of the HyperSync runtime environment. It provides the fundamental execution engines for both single-intent operations and multi-step programs.

## Components

- **Runtime**: Manages the execution of individual intents. It handles:
    - Intent validation
    - Policy gating (via Policy capsule)
    - Operator resolution and routing
    - Execution and receipt generation
    - Artifact storage

- **ProgramEngine**: Orchestrates the execution of complex tasks. It:
    - Builds the hypergraph from specifications
    - Initializes the Coordinator (from Coordination capsule)
    - Manages the lifecycle of a program execution session

## Usage

The Kernel is typically initialized with a `spec_root` path, which points to the directory containing the system specifications. It then serves as the entry point for executing tasks and intents.
