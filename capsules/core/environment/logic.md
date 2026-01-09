# HyperSync Core Environment Capsules d Logic Specification (Enhanced)

## 1. Purpose and Scope

The **HyperSync Core Environment** capsule family (`hypersync.core.environment.*`) defines and manages the **virtual environments** in which:

- Users operate.
- AI agents run.
- HyperSync itself can recreate and re-home its own core services.

These environments are:

- **Deterministic** d every structural decision about templates, instances, and sessions must be reproducible (`D0_bit_exact`).
- **Self-describing** d fully specified via declarative templates, manifests, schemas, and policies.
- **Safety-first** d designed to contain AI behavior and protect users by default.

The environment capsule family composes the geometry and consensus capsules and acts as the **control plane** for generated instances HyperSync makes of itself.

---

## 2. Core Concepts

### 2.1 Environment Template

An **Environment Template** is a declarative, versioned description of a class of environments:

- Capsule and schema bundles to activate (geometry, consensus, routing, UI, drivers, AI agents).
- Policy bundles (security, resource limits, determinism constraints, data handling rules).
- Geometry descriptors (spaces, regions, safety fences) for the environment.
- Session and role models (user roles, AI agent roles, collaboration modes).

Templates are immutable once activated; new behavior requires a **new template version**.

### 2.2 Environment Instance

An **Environment Instance** is a concrete, running realization of a template:

- Bound to a specific `environment_id` and tenant (or system) scope.
- Has runtime state (active sessions, current view, attached resources).
- Emits receipts for lifecycle events (creation, modification, snapshot, restore, destruction).

Instances must be **fully reconstructable** from:

1. The template definition and its receipts.  
2. The sequence of consensus decisions affecting the environment.  
3. Environment and session receipts.

### 2.3 Session

A **Session** is the unit of interaction inside an environment instance:

- Represents one or more users and/or AI agents operating in the environment.  
- Carries identity, capabilities, and state (see TUI and sync-session schemas).  
- Is strictly contained by the environment's policies and geometry fences.

Sessions cannot directly mutate the template; they propose changes that flow through **environment + consensus** control paths.

---

## 3. Operations and APIs

Environment capsules expose deterministic operations over templates, instances, and sessions.

### 3.1 Template Management

- `DefineTemplate(template_descriptor, options)`  
  Create a new environment template. Returns a template ID and emits a template receipt.

- `UpdateTemplate(template_id, patch, options)`  
  Produce a new version of an existing template by applying a patch; old versions remain immutable and addressable.

- `GetTemplate(template_id)`  
  Return the full descriptor of an environment template.

- `ListTemplates(filter)`  
  Enumerate available templates by tenant, determinism tier, trust zone, or other attributes.

Templates reference:

- Capsule IDs and versions (geometry, consensus, routing, UI, audio, AI agents, drivers).  
- Policies and sandboxes.  
- Expected determinism tiers for each attached capsule.  
- Geometry spaces and regions used by the environment.

### 3.2 Environment Instance Lifecycle

- `InstantiateEnvironment(template_id, instance_params, options)`  
  Create a new environment instance from a template. Produces an instance ID and emits a lifecycle receipt.

- `ModifyEnvironment(environment_id, patch, options)`  
  Propose changes to an environment instance (e.g., adjusting resource quotas, enabling a feature flag). Changes that alter the structural view route through consensus.

- `SnapshotEnvironment(environment_id, options)`  
  Capture a consistent snapshot of the environment's structural and selected runtime state; returns a snapshot handle.

- `RestoreEnvironment(snapshot_id, options)`  
  Create a new environment instance from a snapshot, with clear lineage.

- `DestroyEnvironment(environment_id, options)`  
  Tear down an environment instance, emitting a destruction receipt and cleanup plan.

- `GetEnvironmentDescriptor(environment_id)`  
  Return a descriptor of the current environment view, including active capsules, policies, geometry, and sessions.

- `ListEnvironments(filter)`  
  Enumerate active and historical environment instances.

### 3.3 Session Management

- `AttachSession(environment_id, session_descriptor, options)`  
  Create or bind a session to an environment instance; returns a session ID.

- `DetachSession(environment_id, session_id, options)`  
  Cleanly detach a session from the environment, emitting a session receipt.

- `FreezeSession(environment_id, session_id, options)`  
  Temporarily suspend a session (e.g., for safety or backpressure), preserving state.

- `ThawSession(environment_id, session_id, options)`  
  Resume a frozen session.

Sessions are required to:

- Respect environment policies (determinism tiers, resource limits, network rules).  
- Operate only within geometry fences configured by the environment.  
- Use environment-sanctioned surfaces for I/O (TUI, audio, task APIs).

---

## 4. Determinism, Self-Recreation, and Receipts

### 4.1 Determinism Tier

Core environment capsules declare `determinism_tier = D0_bit_exact` for all **structural** operations:

- Template creation and resolution.  
- Environment instance creation, modification, and destruction.  
- Mapping of sessions to environments and capabilities.

Non-deterministic or heuristic behavior (e.g., placement optimization) must be:

- Implemented in **separate advisory capsules**.  
- Referenced explicitly in templates with clear determinism metadata.  
- Treated as suggestions; environment core makes the final deterministic decision.

### 4.2 Self-Recreation

Given:

- A set of environment templates and their receipts.  
- The sequence of consensus decisions that affected those environments.  
- Environment and session receipts.

HyperSync must be able to:

1. Reconstruct the exact environment views that previously existed.  
2. Instantiate new environment instances that behave identically under the same inputs.  
3. Verify that regenerated instances satisfy the same determinism and safety guarantees.

### 4.3 Environment Receipts

Environment operations emit **environment receipts** that record:

- Template and environment IDs, versions, and hashes.  
- Operation type and parameters (or hashed equivalents).  
- Referenced consensus and geometry receipts.  
- Determinism tier and policy pack hashes.  
- Capsule ID, version, and manifest hash.

Receipts enable:

- Full audit of environment evolution.  
- Reproducible tests and conformance checks.  
- Human-readable explanations of what environment users and AI agents actually saw.

---

## 5. Security, Isolation, and AI Containment

Environment capsules are the **primary enforcement point** for user and AI safety.

### 5.1 Isolation Boundaries

- All untrusted code (including user-provided AI agents) must run **inside an environment instance**, never directly on the host.  
- Templates declare **trust zones** (`system`, `tenant`, `user`, `ephemeral`) for:
  - Capsules.  
  - Sessions.  
  - External integrations.

Environment policies enforce that:

- Cross-tenant access is disabled by default.  
- Cross-environment access requires explicit bridge capsules with separate policies and receipts.  
- Network and filesystem exposure is defined at the template level and enforced at runtime.

### 5.2 Role and Capability Model

Environment capsules rely on identity and authorization services to distinguish:

- `environment_manager` d manages templates and instances.  
- `tenant_admin` d manages tenant-specific templates and environments.  
- `session_manager` d manages sessions and collaboration.  
- `experiment_manager` d manages experimental or ephemeral environments.  
- `untrusted_agent` d operates only inside environments and cannot directly call environment capsules.

### 5.3 Safety Policies

Policies (see `capsules_hypersync.core.environment_spec_policy.ENHANCED.yaml`) define:

- Allowed determinism tiers in different environment classes (e.g., core infra must be `D0_bit_exact`).  
- Maximum resource budgets per environment and per session.  
- Data classification rules (e.g., no PII outside specific trust zones).  
- Requirements for human oversight or multi-party approval for certain templates or changes.

---

## 6. Integration with Geometry, Consensus, and UX

### 6.1 Geometry Integration

Environment templates reference geometry spaces and regions:

- Each environment must bind to one or more `SpaceId` values.  
- Safety fences and regions of interest define where sessions and agents may operate.  
- Environment descriptors include geometry descriptors for visualization and routing.

Environment operations can:

- Request new spaces or regions from geometry capsules (subject to policy).  
- Clamp environment changes to safe geometric transformations.

### 6.2 Consensus Integration

Structural environment changes (templates, instance shape, critical policy updates) flow through **consensus capsules**:

- Environment capsules prepare well-formed proposals.  
- Consensus capsules decide on acceptance or rejection.  
- Environment capsules apply decisions and emit environment receipts.

This ensures that environment evolution is **globally consistent, auditable, and reversible**.

### 6.3 UX / TUI / Audio Integration

Environment descriptors provide a canonical view for UX integration:

- TUI surfaces can render environment topology, templates, and sessions.  
- Audio capsules can signal environment events (creation, safety warnings, transitions).  
- User activity mechanics (sessions, roles, states) are aligned with environment semantics.

---

## 7. Developer and AI Workflows

Developers and AI agents use the environment capsule family to:

1. **Discover** available templates and environments.  
2. **Instantiate** new environments for tenants, projects, or experiments.  
3. **Attach sessions** for users and AI agents.  
4. **Observe and debug** environment behavior via receipts and descriptors.  
5. **Propose changes** that flow through policy and consensus gates.

The environment capsule family thus forms the **spine** of HyperSync's self-generated instances and the default safety envelope for both humans and AI.
