# VNES AI Interface Protocol (Enhanced)

## 1. AI-First, Policy-Governed Design

The **VNES AI Interface** treats AI agents as first-class operators while enforcing strict governance and determinism guarantees.

Design goals:

1. **Discoverability** – Agents can find relevant capsules using natural language and structured constraints.
2. **Composability** – Agents can assemble pipelines and workflows from capsules.
3. **Authoring** – Agents can propose new capsules by authoring specs.
4. **Safety** – All actions are mediated by policies, trust zones, and determinism tiers.
5. **Feedback** – Agents receive structured, machine-readable feedback for self-correction.

---

## 2. Capabilities Surface

At a high level, the AI Interface exposes the following capability groups:

1. **Registry operations**
   - `vnes.search_capsules(query, filters)` – semantic + faceted search.
   - `vnes.get_manifest(capsule_id, version)` – fetch manifest and summaries.
   - `vnes.list_capabilities(filters)` – enumerate available capabilities.

2. **Introspection**
   - `vnes.describe_capsule(capsule_id)` – docs, interfaces, examples.
   - `vnes.inspect_schema(ref)` – input/output schema details.
   - `vnes.explain_compatibility(a, b)` – why two capsules can or cannot be composed.

3. **Execution & orchestration**
   - `vnes.execute(capsule_id, inputs, context)` – invoke a single capsule.
   - `vnes.execute_pipeline(pipeline_spec, context)` – run a composed graph.
   - `vnes.subscribe(topic, filters)` – consume events from the event bus.

4. **Spec authoring & lifecycle**
   - `vnes.create_spec(draft)` – create a new spec capsule in a workspace.
   - `vnes.validate_spec(path_or_id)` – run structural and policy checks.
   - `vnes.build_capsule(path_or_id)` – invoke STUNIR to produce impl + receipt.
   - `vnes.publish_capsule(id, version, scope)` – register capsule in a namespace.

5. **Observability & feedback**
   - `vnes.get_receipt(execution_id)` – retrieve detailed execution receipts.
   - `vnes.stream_logs(execution_id)` – live or historical logs.
   - `vnes.report_issue(capsule_id, report)` – provide feedback or bug reports.

These operations can be exposed via function-calling, RPC, or REST, depending on deployment.

---

## 3. Semantic Registry – Read Interface

### 3.1 Query Shape

Agents typically issue queries of the form:

```json
{
  "intent": "I need to visualize a 4D tensor as a heatmap.",
  "constraints": {
    "latency_class": "interactive",
    "output_surface": "terminal_sixel",
    "determinism_min_tier": "D1_numerically_stable"
  },
  "filters": {
    "types": ["ui", "pipeline"],
    "namespaces": ["hypersync.core", "hypersync.platform"],
    "governance_tiers": ["core", "platform"]
  }
}
```

### 3.2 Response Shape

The registry responds with ranked matches:

```json
{
  "matches": [
    {
    "id": "hypersync.platform.viz.heatmap.tensor_sixel",
    "version": "1.2.0",
    "score": 0.98,
    "manifest_summary": { "type": "ui", "determinism_tier": "D1_numerically_stable" },
    "why": [
    "Matches intent: 'heatmap' and 'tensor' in description",
    "Compatible with output_surface: terminal_sixel",
    "Meets determinism_min_tier: D1_numerically_stable"
    ],
    "usage_example": "..."
    }
  ]
}
```

The `why` field is particularly important for transparency: it explains to both humans and AI *why* a capsule was selected.

---

## 4. Execution & Dynamic Composition – Execute Interface

Agents construct **ephemeral pipelines** by combining capsules.

### 4.1 Pipeline Specification

A minimal pipeline spec might look like:

```json
{
  "nodes": [
    {
    "id": "detector",
    "capsule": "hypersync.contrib.anomaly.detector.ts",
    "version": "0.4.0"
    },
    {
    "id": "plotter",
    "capsule": "hypersync.platform.viz.timeseries.anomaly",
    "version": "1.1.0"
    }
  ],
  "edges": [
    { "from": "input.timeseries", "to": "detector.input.data" },
    { "from": "detector.output.anomalies", "to": "plotter.input.anomalies" }
  ],
  "constraints": {
    "determinism_min_tier": "D1_numerically_stable",
    "latency_class": "interactive"
  }
}
```

The runtime validates the pipeline:

- All referenced capsules exist and are admissible.
- Schemas on connected edges are compatible.
- Determinism and governance constraints are satisfied.

### 4.2 Execution Request

```json
{
  "op": "vnes.execute_pipeline",
  "pipeline": { /* as above */ },
  "inputs": {
    "input.timeseries": "<opaque reference or encoded data>"
  },
  "context": {
    "session_id": "sess-1234",
    "tenant_id": "tenant-acme",
    "priority": "normal"
  }
}
```

The runtime returns:

- A handle for the execution (`execution_id`).
- Final outputs (for synchronous runs) or references to topics where results will appear.
- Links to receipts and logs.

---

## 5. Spec Generation and Capsule Authoring – Write Interface

VNES encourages AI agents to **author specs, not ad-hoc code**.

### 5.1 Authoring Flow

1. **Draft** – The agent constructs:
   - `manifest.json` with capsule ID, type, determinism and governance metadata.
   - `spec/logic.md` with natural-language or pseudo-code description.
   - `spec/schema.json` with input/output schemas.
   - Optional: `policy.yaml`, tests, examples.

2. **Validate** – Call `vnes.validate_spec`:
   - Check against manifest and receipt schemas.
   - Enforce governance policies (e.g., restricted namespaces).
   - Ensure determinism claims are plausible for the capsule type.

3. **Build** – Call `vnes.build_capsule` or `stunirpack build`:
   - STUNIR generates implementation into `impl/`.
   - Tests are run (if present).
   - A receipt is produced, referencing hashes and toolchain details.

4. **Publish** – Call `vnes.publish_capsule`:
   - Capsule becomes available in selected namespaces (e.g., `user.*`, `tenant.*`).
   - Governance workflows may require human approval for higher-tier namespaces.

### 5.2 AI Collaboration Patterns

- **AI as proposer, human as approver** – For higher-trust tiers, AI drafts specs; humans review manifests, policies, and determinism claims before publication.
- **AI as maintainer** – AI agents can propose version bumps, migrations, or deprecations, subject to policy.

---

## 6. Observability, Errors, and Feedback

The AI Interface returns structured feedback objects rather than opaque strings.

### 6.1 Error Objects

Example of a schema mismatch error:

```json
{
  "error_type": "SCHEMA_MISMATCH",
  "message": "Input tensor shape mismatch.",
  "details": {
    "expected_shape": [3, 3],
    "actual_shape": [3, 4],
    "capsule_id": "hypersync.core.linalg.matmul",
    "port": "input.b"
  },
  "hint": "Consider inserting a reshape or projection capsule between the producer and this input."
}
```

### 6.2 Policy and Governance Feedback

When a requested action is denied by policy, the agent receives:

```json
{
  "error_type": "POLICY_DENIED",
  "message": "Capsule cannot be published to namespace 'hypersync.core'.",
  "details": {
    "required_role": "core_maintainer",
    "requested_namespace": "hypersync.core",
    "capsule_id": "tenant.acme.strategy.alpha"
  },
  "hint": "Publish to 'tenant.acme.*' or request an elevation workflow."
}
```

This allows agents to **self-correct** by adjusting their plans rather than blindly retrying.

---

## 7. Safety and Guardrails for AI Agents

To ensure safe operation in mixed-trust environments, the AI Interface is governed by:

- **Scopes and roles** – Each agent has an identity, roles, and allowed operations.
- **Namespaces** – Agents may be restricted to `user.*` and `tenant.*` namespaces.
- **Determinism constraints** – Agents may be prevented from lowering determinism tiers in critical paths.
- **Resource budgets** – Quotas on compute, memory, and I/O.

These guardrails ensure that powerful AI agents remain **constrained, auditable, and predictable** participants in the HyperSync ecosystem.


## 8. Key Consumers
### The Factory (hypersync.core.factory)
The Factory is the primary consumer of the AI Interface for 'Make X for Y' workflows. It uses the interface to:
1. **Analyze Intent:** Resolve semantic queries to find appropriate reasoning models.
2. **Synthesize Specs:** Dispatch generation tasks to coding models via the `vnes.execute` API.
3. **Register Capsules:** Publish generated artifacts back to the registry using `vnes.publish_capsule`.
