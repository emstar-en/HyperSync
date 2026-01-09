# Factory Logic (Make X for Y)

## Overview
The Factory is the realization of the `03_specifications/core/modules/factory/make_x_for_y.md` protocol.
It allows the system to generate new capabilities (Capsules) on the fly by leveraging local intelligence.

## The "Make X for Y" Protocol

### 1. Intent Analysis (The "Y")
*   **Input**: "I want a poker game (X) for the dev team (Y)."
*   **Process**: The Factory queries the `hypersync.core.catalogue` to find a "Reasoning Model" (e.g., Llama-3-8B).
*   **Prompt**: "Analyze the user intent. What components are needed to satisfy 'X'?"

### 2. Blueprint Generation
The Reasoning Model outputs a `FactorySpec` (JSON):
```json
{
  "target": "hypersync.contrib.poker_night",
  "components": ["logic", "tui_renderer", "agent_persona"],
  "constraints": ["low_latency", "8bit_graphics"]
}
```

### 3. Fabrication (The "X")
The Factory iterates through the components:
*   **Logic**: Generates Python code using a "Coding Model".
*   **Assets**: Generates TUI layouts and Persona prompts.
*   **Validation**: Runs the generated code against the `hypersync.core` API stubs to ensure safety.

### 4. Injection
*   The new capsule is compiled into an ephemeral package.
*   It is hot-loaded into the `hypersync.core.environment`.
*   A receipt is generated: `FactoryBuildReceipt`.

## Determinism
*   **D2 (Statistical)**: The *generation* process is statistical (LLM-based).
*   **D0 (Strict)**: The *execution* of the generated capsule is strict. Once built, the code is frozen and hashed.
