# HyperSync Standard Agent Logic (Enhanced)

## 1. Overview

The `hypersync.agent.standard` capsule defines the **canonical inhabitant model** inside a HyperSync environment. A standard agent may represent:

- A purely autonomous AI-controlled entity.
- A human user operating through a TUI/audio/other surface.
- A mixed-mode co-pilot (human + AI).
- A passive observer or monitor.

In all cases, the environment interacts with the agent through the same deterministic shell: the **Standard Agent Loop**.

---

## 2. The Standard Agent Loop (Tick)

The agent operates on a discrete tick cycle, orchestrated by the Environment capsule.

On each tick:

1. **Command & Context**  
   The environment sends a `TickRequest` containing:
   - A **command** (`TICK`, `INTROSPECT`, `SHUTDOWN`, `RESET`).
   - The agent's current **state**.
   - A local **observation** (nearby agents, geometry summary, messages).

2. **Sense & Interpret**  
   The agent:
   - Consumes the observation provided by the environment (no direct geometry calls).  
   - Updates or queries its internal memory as allowed by resource and policy limits.

3. **Decide**  
   The agent's decision logic selects:
   - A new `next_state` (e.g., updated velocity, mode, memory digest).  
   - An optional `ActionRequest` describing a desired action (e.g., `MOVE`, `SIGNAL`).

   The decision may use an attached cognitive module (LLM, FSM, human), but the outer shell is responsible for:
   - Enforcing invariants (e.g., max speed, energy non-negativity).  
   - Clamping or rejecting unsafe proposals.

4. **Act & Learn**  
   The environment:
   - Interprets the `ActionRequest` as a **request**, not a command.  
   - Applies geometry, consensus, and policy to decide what actually happens.  
   - Returns the resulting world state on the next tick.

The agent returns a deterministic `TickResult` for a given `TickRequest` and internal state snapshot.

---

## 3. Capabilities

### 3.1. Movement (Geometric Translation)

- The agent proposes movement via `ActionRequest` with `type = MOVE` and a desired velocity vector in the local tangent space.
- The environment supplies constraints (e.g., max speed, fences) via `constraints` in the action.
- The agent must:
  - Respect speed and energy limits.  
  - Never propose movement outside declared safety fences.
- The environment validates the path with geometry capsules and is the final arbiter of movement.

### 3.2. Local Sensing and Observation

- The environment constructs the `Observation` object using geometry and other capsules.  
- The agent does **not** directly query geometry; it trusts the observation it is given.  
- Observations may include:
  - Nearby agents and their public state.  
  - Geometry descriptors (obstacles, fences).  
  - Local messages and signals.

### 3.3. Interaction and Communication

- `SIGNAL` and `INTERACT` actions allow:
  - Sending short messages to nearby agents.  
  - Requesting public state or resource exchanges.
- All interactions remain subject to environment policy and identity/authorization constraints.

### 3.4. Introspection and Explanation

- Via `INTROSPECT` commands, the agent may:
  - Return richer introspection of its current state.  
  - Attach explanation references in `safety_context` describing why an action was chosen.
- This supports **human-readable proof mechanics** and activity visualization.

---

## 4. Modes and Cognitive Attachments

### 4.1. Agent Modes

The agent operates in one of several modes:

- `AUTONOMOUS` — decision logic driven primarily by an AI or classical controller.  
- `HUMAN_CONTROLLED` — human input drives decisions; the agent shells them into `ActionRequest`s.  
- `MIXED` — AI and human co-pilot, with the shell enforcing arbitration rules.  
- `OBSERVER` — read-only; the agent produces no actions, only observations and annotations.

Mode is part of `AgentState` and may be changed only under environment policy.

### 4.2. Cognitive Profile

The `cognitive_profile` describes how high-level decisions are made:

- Kind: `HUMAN`, `LLM`, `FSM`, or `HYBRID`.  
- Capsule-based brains (e.g., `hypersync.agent.brain.llm.standard`) declare their own determinism and policy.  
- The standard agent shell:
  - Calls brain capsules within strict resource budgets.  
  - Applies invariant checks before accepting brain-proposed actions.  
  - Records digests of decisions for receipts and auditing.

---

## 5. Determinism and Safety Invariants

### 5.1. Determinism

- The outer shell of the standard agent is `D1_platform_agnostic` deterministic.  
- Given the same `TickRequest` and internal memory snapshot, it must produce the same `TickResult` modulo allowed platform differences.
- Non-deterministic cognitive behavior (e.g., LLM sampling) must be:
  - Bounded by policy (e.g., temperature, token limits).  
  - Logged and, where necessary, replayable via receipts and seeds.

### 5.2. Safety Invariants

The standard agent must enforce at least the following invariants:

- **No direct environment mutation** — all changes go through `ActionRequest`s.  
- **Bounded movement** — cannot propose velocities beyond policy or energy limits.  
- **Fence respect** — cannot propose positions outside safety fences.  
- **Privilege boundaries** — cannot escalate its trust zone or access global state.  
- **Fail-safe behavior** — on invariant violation or resource exhaustion, follow `halt_and_reset` strategy.

---

## 6. Telemetry and Receipts

The agent emits telemetry via the environment and telemetry capsules:

- Per-tick counters and digests for debugging (optional).  
- Receipts for:
  - Denied actions.  
  - Resource exhaustion.  
  - Unsafe actions proposed by a cognitive module.

These receipts enable:

- Post-hoc analysis of agent behavior.  
- Conformance testing across versions.  
- Human-readable activity visualizations (e.g., abacus views, TUI panels).

---

## 7. Relationship to Environment and Geometry Capsules

- The standard agent is **fully contained** within an environment instance.  
- Geometry and consensus define the world; the agent only **proposes** changes to it.  
- Environment capsules mediate all interactions, ensuring:
  - Deterministic, auditable behavior.  
  - Strong containment of user and AI activity.  
  - A unified model for both human users and AI inhabitants.
