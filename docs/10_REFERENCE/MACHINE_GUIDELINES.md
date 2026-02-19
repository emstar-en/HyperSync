# Machine Guidelines for Code Generation

## Target Audience
This document is for **STUNIR** (or any AI Code Generator) tasked with implementing HyperSync.

## Architectural Philosophy
1.  **Fractal:** The system is recursive. A `Holon` is just a container that can contain other `Holons`. Do not hardcode a flat hierarchy.
2.  **Geometric:** All state is spatial. "Distance" is not a metaphor; it is a calculation in the Poincaré disk. Use `core.geometry` for *everything*.
3.  **Deterministic:** The system must be replayable. Use the `determinism_tier` from the schemas. If Tier is D1 or D0, you MUST use seeded RNGs derived from the Holon ID.

## Implementation Directives

### A. Schema Adherence
- You MUST validate all inputs against the JSON Schemas in `03_specifications/schemas/`.
- Do not invent new fields. If a field is missing, check `extensions` or fail.

### B. The "Physics" Engine
- Implement the math defined in `02_program/internals/algorithms.md` and `thermodynamic_logic.md` EXACTLY.
- Do not approximate hyperbolic distance with Euclidean distance.

### C. Agent Construction
- Agents are composed of "Stacks" (see `agent_stack.schema.json`).
- Do not hardcode agent types (e.g., "WriterAgent"). Instead, build a generic `Agent` class that loads a `Stack` configuration to determine its behavior.

### D. Error Handling
- If a geometric calculation fails (e.g., point at infinity), raise a `GeometricSingularityError`.
- If a consensus round fails, trigger the `ConflictResolution` protocol defined in `consensus_mechanics.md`.

## File Structure Mapping
- `02_program/internals/` -> `src/core/` (The Math & Physics)
- `03_specifications/schemas/` -> `src/models/` (Pydantic/Data Classes)
- `04_components/` -> `src/agents/` (The Actors)
- `05_implementation/api/` -> `src/api/` (The Interface)
