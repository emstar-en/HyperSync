# HyperSync Bridge API Logic (Enhanced)

## 1. Role in the HyperSync Fabric

The `hypersync.bridge.api` capsule is the **Boundary and Virtualization Gateway**. It connects:

- Untrusted external networks (users, TUIs, services, tools), and
- The virtualized, deterministic HyperSync world (environments, agents, diagnostics).

It is the **only** capsule allowed to:

- Bind public network ports and terminate TLS.
- Translate external protocols (HTTP, WebSocket, gRPC) into internal, receipt-friendly commands.
- Route traffic across multiple tenants and environments.

---

## 2. Planes of Interaction

The Bridge exposes three primary planes:

1. **Control Plane (REST / gRPC)**
   - Environment lifecycle: create, pause, resume, destroy.
   - Agent lifecycle: spawn, attach brain, retire.
   - Configuration: quotas, routing, virtual topologies.

2. **Data Plane (WebSocket / Streaming)**
   - High-frequency tick streams (e.g., 30Hz world updates).
   - Real-time user actions (avatar movement, signals).
   - Telemetry and event subscriptions.

3. **Introspection Plane (REST / Streaming)**
   - Receipts, audit trails, and conformance logs.
   - Diagnostic views of environments and agents.
   - Health and capacity reporting for the Bridge itself.

Each plane is logically separate but carried over shared infrastructure.

---

## 3. Ingress Path: External → Virtualized World

1. **Authenticate & Resolve Identity**
   - Validate JWT or mTLS credentials via `auth.identity.core`.
   - Construct a `UserContext` (user_id, tenant_id, roles, client_type).

2. **Schema-Validated Envelope**
   - Wrap the incoming request as a `BridgeRequestEnvelope`:
    - `trace_id`, `correlation_id`, `user`, `target_env`, `operation`, `payload`, `schema_id`.
   - Validate `payload` against the declared `schema_id`.

3. **Routing and Determinism Buffer**
   - Resolve `target_env` using `hypersync.core.environment_directory`.
   - Enqueue the request into a **per-(tenant, environment)** ordered queue.
   - Produce a deterministic ordering for downstream capsules, even if arrival order at the network boundary is noisy.

4. **Dispatch to Internal Capsules**
   - Map `operation` to environment or agent commands.
   - Attach `UserContext` and authorization decision to every message.

---

## 4. Egress Path: Virtualized World → External

1. **Subscribe to Internal Streams**
   - Environments publish receipts, state updates, and telemetry.
   - The Bridge subscribes with clear filters (tenant, environment, user, channel).

2. **Filter & Shape**
   - Apply authorization rules to hide data not visible to the requester.
   - Down-sample or aggregate high-frequency streams when required.

3. **Serialize and Deliver**
   - Convert internal events into `WsServerMessage` or `BridgeResponseEnvelope`.
   - Attach `trace_id`, `rate_limit` info, and relevant metadata.

---

## 5. Session and Channel Model

- Each client connection (REST or WebSocket) is bound to a **session** carrying:
  - `UserContext` (identity, tenant, roles).
  - Client capabilities (e.g., TUI bandwidth, preferred update rate).
  - Active subscriptions (channels, environments, agents).

- Channel patterns may include:
  - `env.{environment_id}.ticks`
  - `env.{environment_id}.receipts`
  - `agent.{agent_id}.state`
  - `tenant.{tenant_id}.audit`

- The Bridge enforces per-session and per-channel quotas.

---

## 6. Safety and Security Responsibilities

The Bridge is the **first line of defense**:

- **Input Validation**
  - All JSON payloads validated against schemas.
  - Unknown or oversized data rejected early.

- **Authentication and Authorization**
  - No internal message is created without a resolved `UserContext`.
  - Authorization decisions are cached but always revalidated on boundary changes (e.g., role update).

- **Rate Limiting and Abuse Detection**
  - Per-IP and per-user quotas.
  - Burst limits and backpressure signaling (`RATE_LIMIT_NOTICE`).

- **Virtualization Isolation**
  - Tenants and environments are strictly isolated by routing and authorization.
  - No cross-tenant or cross-environment leakage through shared channels.

---

## 7. Determinism and Observability

- The Bridge itself is `D2_statistical` because of network timing and availability.
- It improves core determinism by:
  - Normalizing and ordering requests per (tenant, environment).
  - Assigning stable `trace_id` and `correlation_id` fields.
  - Emitting receipts for retries, timeouts, and reorders.

- Observability:
  - Every boundary crossing can be reconstructed from receipts.
  - External clients can correlate their requests with internal events.

---

## 8. Relationship to Other Capsules

- **auth.identity.core**
  - Provides identity resolution and credential validation.

- **hypersync.core.environment_directory**
  - Maps logical environment references to running instances.

- **hypersync.core.environment / hypersync.agent.standard**
  - Consume commands and produce state/telemetry that the Bridge relays.

- **telemetry.core**
  - Records receipts and metrics for security, SLOs, and capacity planning.

The Bridge thus acts as a **unified, observable membrane** between the virtualized HyperSync world and everything outside it.
