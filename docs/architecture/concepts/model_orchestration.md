# Dynamic Model Orchestration

## Overview
HyperSync treats AI models not as static dependencies, but as **raw materials** that can be dynamically provisioned, stacked, and instantiated as geometric nodes. The System Operator (or the Orchestrator Agent) can query the `ModelRegistry`, assemble a `Stack`, and spawn a new Agent into the hyperbolic space to address emerging tasks.

## The Model Lifecycle

### 1. Cataloguing (The Registry)
The system maintains a live `ModelRegistry` (defined in `schemas/model_registry.schema.json`). This is the "Menu" of available intelligence.
- **Local Models:** Models available via local inference servers (vLLM, Ollama).
- **Remote APIs:** Models available via external providers.
- **Specialized Units:** Classifiers, Embedders, and Rerankers.

### 2. Stack Assembly (The Recipe)
When a task is identified (e.g., "Analyze this security log"), the system creates an **Agent Stack** (`schemas/agent_stack.schema.json`).
A Stack is a composition of layers:
- **Cognitive Layer:** The main LLM (e.g., Llama-3) for reasoning.
- **Memory Layer:** Vector store or context window management.
- **Action Layer:** Tools and API access.

### 3. Geometric Instantiation (The Spawn)
Once a Stack is defined, it is instantiated as a **Node** in the Hyperbolic Graph.
- **Positioning:** The node is placed in the geometric space based on its semantic relevance to the task.
- **Objective:** The node is assigned a `MetricPolicy` (Objective).
- **Lifecycle:** The node can be ephemeral (spin up, solve, spin down) or persistent.

## Dynamic Synthesis Example

**Scenario:** The system detects a complex anomaly requiring deep code analysis.

1.  **Trigger:** `Coordinator` agent detects anomaly.
2.  **Lookup:** `Coordinator` queries `ModelRegistry` for models with tag `["coding", "security"]`.
3.  **Selection:** Selects `deepseek-coder-33b` (Cognitive) and `embedding-v3` (Memory).
4.  **Assembly:** Creates a `SecurityAnalystStack` definition.
5.  **Provisioning:** Calls `InfrastructureLayer` to spin up the container for `deepseek-coder`.
6.  **Spawn:** Registers the new `SecurityAnalyst` agent at coordinates `(0.4, 120°)` (near the anomaly).
7.  **Execution:** The new agent performs the analysis.
8.  **Teardown:** Once the objective is met, the agent is dissolved, and resources are freed.

## "Loose" vs "Strict" Objectives
Agents can be configured with varying degrees of autonomy:
- **Strict:** "Classify these 100 items. Do nothing else."
- **Loose:** "Explore this data cluster and report anything interesting." (High temperature, exploratory movement policy).
