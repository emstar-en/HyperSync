# Example: Deep Research Holon and General Pattern

This example demonstrates a hierarchical deployment of a self-contained
research unit. The same pattern generalizes to many other domains.

## 1. Concept

A department head wants to spin up a temporary research team to explore a
dataset. They do not want to manually manage every agent. Instead, they
define a Holon via a deployment manifest.

The manifest specifies:

- the Holon's geometry lease in the manifold,
- its resource quotas and model budgets,
- its determinism profile and acceptance gates,
- the agent stacks that will serve as orchestrator and workers.

## 2. Components (Research Sector Alpha)

### 2.1 The Holon (Research Sector Alpha)

- Geometry: a specific slice of the Poincare disk (for example radius 0.2
  at 45 degrees).
- Isolation: semi_permeable. It can read global data, but its internal
  messy thoughts are contained.
- Quota: limited to a small number of agents and compute units.
- Determinism: typically D(2) statistical internally, with a D(1) or D(0)
  orchestrator for reporting and summarization.

### 2.2 The orchestrator (Research Lead)

- Role: local manager of the Holon.
- Behavior: strict. Stays near the center of the Holon and waits for
  reports from scouts.
- Model: any high reasoning model (for example claude-3-opus).
- Capabilities:
  - spawns and retires worker agents,
  - adjusts acceptance gates (temperature, thresholds),
  - summarizes receipts into human-readable reports.

### 2.3 The workers (Idea Scouts)

- Role: explorers.
- Behavior: loose, Levy-flight style exploration of the data in the Holon.
- Models: a fast connection-making model (for example gpt-4-turbo) plus an
  embedding model for perception.
- Physics: use exploration-biased movement policies such as
  policy:langevin_exploration.

## 3. Deployment flow (concrete example)

1. The user submits research_team.json (a HolonDeployment manifest) to
   the system API.
2. The system validates quotas and reserves the geometric sector.
3. The system spawns the Research Lead at the Holon's center.
4. The system spawns several Idea Scouts distributed around the lead using
   a distribution strategy such as random_uniform.
5. The Holon runs autonomously. Scouts find data, move towards it, and send
   signals back to the lead through geometry-aware acceptance gates.
6. The Holon periodically emits summarized receipts back to its parent
   Holon or to the user.

## 4. Generalizing the pattern

The same pattern can be applied beyond research:

- Incident response cells: spin up a high-intensity diagnostic Holon when
  an anomaly is detected. Collapse it once the incident is resolved.
- Simulation campaigns: run many simulation Holons in parallel, each
  exploring a different parameter regime, while a control Holon
  coordinates and aggregates.
- Product development pods: organize mixed teams of language, vision, and
  code agents inside a Holon that owns a specific feature or product area.

In all cases, the Holon deployment manifest describes:

- who is in charge (orchestrator stack),
- who does the work (worker stacks),
- which physics and gates apply (geometry and thermodynamics),
- what determinism tier and replay guarantees are required.

## 5. Observability and lifecycle

A well-behaved Holon also specifies:

- Telemetry settings: sample rates, diagnostic sinks, and conformance
  vector profiles.
- Lifecycle policy: triggers for auto-collapse (idle timeout, budget
  exhaustion, goal completion) and restart strategies.
- UX hooks: which TUI or audio scenes to use for showing activity and
  explanations to users.

These hooks allow the diagnostic plane of HyperSync to present a coherent
story about what each Holon did, why it did it, and how confident it was
in its conclusions.
