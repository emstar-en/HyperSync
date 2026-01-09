# Logic Capsule

The Logic capsule (formerly Planner) is responsible for high-level decision making and routing within the HyperSync system. It translates abstract intents into concrete operator executions.

## Components

- **RulesPlanner**: A lightweight planner that uses a set of rules and built-in mappings to resolve intents to operators. It supports:
    - Direct task-to-operator mapping
    - Metadata-based routing
    - Advanced rule matching with conditions

- **Preferences**: Manages system-wide and session-specific preferences that influence routing decisions. It scores nodes based on:
    - Tags and flags
    - Estimated cost
    - Conformance availability

## Configuration

The capsule is configured via `schema.json`, which points to the location of the routing rules and plugins registry.
