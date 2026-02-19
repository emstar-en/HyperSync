# PCT Workflow Guide
## Pathfinder → Cartographer → Trailblazer

**Version:** 1.0.0  
**Audience:** Developers, Process Engineers, AI Operators  
**Prerequisites:** Basic understanding of HyperSync architecture

---

## Table of Contents

1. [Overview](#overview)
2. [The Three Phases](#the-three-phases)
3. [Determinism Tiers](#determinism-tiers)
4. [Artifacts](#artifacts)
5. [Human Roles and Checkpoints](#human-roles-and-checkpoints)
6. [PCT + AGUA Integration](#pct--agua-integration)
7. [Workflow Examples](#workflow-examples)
8. [Troubleshooting](#troubleshooting)

---

## Overview

PCT is HyperSync's **workflow lifecycle methodology** that progressively constrains agent behavior from free exploration to strict deterministic execution.

### The Core Insight

> "First explore freely, then map what works, finally execute exactly."

### Why Three Phases?

| Problem | Solution |
|---------|----------|
| AI agents are unpredictable | Constrain them progressively |
| Good solutions need discovery | Allow exploration first |
| Production needs reliability | Enforce determinism eventually |
| Debugging needs traces | Record everything from the start |

### PCT in One Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PCT LIFECYCLE                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   PATHFINDER          CARTOGRAPHER           TRAILBLAZER            │
│   ───────────         ────────────           ──────────             │
│                                                                      │
│   🔍 EXPLORE          📍 MAP                 🚀 EXECUTE              │
│                                                                      │
│   "What works?"       "How to reproduce?"    "Run it exactly"       │
│                                                                      │
│   ┌─────────┐         ┌─────────┐           ┌─────────┐             │
│   │ Record  │   ──►   │ Analyze │    ──►    │ Replay  │             │
│   │ Actions │         │ Traces  │           │ Strict  │             │
│   │ Freely  │         │ Build   │           │ +Proofs │             │
│   │         │         │ Maps    │           │         │             │
│   └─────────┘         └─────────┘           └─────────┘             │
│                                                                      │
│   Tier: 1-2           Tier: 2-3             Tier: 4                 │
│   (loose)             (structured)          (strict)                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The Three Phases

### Phase 1: Pathfinder 🔍

**Purpose:** Explore solution space without constraints

**Motto:** *"Let the agent wander; record everything."*

#### Characteristics

| Property | Value |
|----------|-------|
| **Freedom Level** | Maximum |
| **Recording** | All actions traced |
| **Drift Handling** | Allowed (logged) |
| **External Calls** | Allowed (no receipts required) |
| **Human Oversight** | Post-hoc review |

#### What Happens

```
Agent                                    System
  │                                        │
  │──── try_action(A) ────────────────────→│
  │                                        │ (record A)
  │←──── result(A) ────────────────────────│
  │                                        │
  │──── try_action(B) ────────────────────→│
  │                                        │ (record B)
  │←──── result(B) ────────────────────────│
  │                                        │
  │──── try_action(C) [fails] ────────────→│
  │                                        │ (record C + failure)
  │←──── error(C) ─────────────────────────│
  │                                        │
  │──── try_action(D) ────────────────────→│
  │                                        │ (record D)
  │←──── result(D) ────────────────────────│
  │                                        │
  └──── END_EPISODE ───────────────────────│
                                           │
                              PathfinderEpisode artifact
```

#### Allowed Operations

- ✅ Arbitrary manifold exploration
- ✅ Cross-sector movement
- ✅ External API calls
- ✅ Dynamic capsule instantiation
- ✅ Curvature adjustments
- ✅ Backtracking and retrying

#### Output: PathfinderEpisode

A complete trace containing:
- Every action attempted
- Every state visited
- Every failure encountered
- Timing information
- Resource consumption

---

### Phase 2: Cartographer 📍

**Purpose:** Analyze traces and build reproducible maps

**Motto:** *"Convert exploration into navigation."*

#### Characteristics

| Property | Value |
|----------|-------|
| **Freedom Level** | Moderate |
| **Recording** | Structured graph building |
| **Drift Handling** | Penalized (not blocked) |
| **External Calls** | Allowed (logged with warnings) |
| **Human Oversight** | Review before proceeding |

#### What Happens

```
PathfinderEpisode                    Cartographer Process
       │                                    │
       │──── analyze_trace() ──────────────→│
       │                                    │ (extract successful paths)
       │                                    │ (identify decision points)
       │                                    │ (detect patterns)
       │                                    │
       │←──── preliminary_map ──────────────│
       │                                    │
       │──── validate_map() ───────────────→│
       │                                    │ (check reproducibility)
       │                                    │ (identify non-determinism)
       │                                    │
       │←──── validation_report ────────────│
       │                                    │
[HUMAN CHECKPOINT: Review map + validation] │
       │                                    │
       │──── refine_map() ─────────────────→│
       │                                    │ (resolve ambiguities)
       │                                    │ (add determinism)
       │                                    │
       │←──── CartographerMap ──────────────│
```

#### Allowed Operations

- ✅ Trace analysis
- ✅ Pattern extraction
- ✅ Limited exploration (to fill gaps)
- ⚠️ Sector boundary crossing (penalized)
- ⚠️ External calls (warned)
- ❌ Arbitrary wandering

#### Drift Penalties

When an agent strays from mapped paths:

```python
drift_penalty = base_penalty * (1 + drift_distance / sector_radius)

# Consequences:
# - Logged for human review
# - May trigger automatic map refinement
# - Accumulated drift can block phase transition
```

#### Output: CartographerMap

A directed graph containing:
- Nodes: Valid states
- Edges: Allowed transitions
- Annotations: Decision conditions
- Warnings: Non-deterministic elements flagged

---

### Phase 3: Trailblazer 🚀

**Purpose:** Execute mapped workflows with strict determinism

**Motto:** *"Follow the map exactly; prove everything."*

#### Characteristics

| Property | Value |
|----------|-------|
| **Freedom Level** | Minimal |
| **Recording** | Execution + cryptographic receipts |
| **Drift Handling** | Blocked (violation error) |
| **External Calls** | Receipts required |
| **Human Oversight** | Exception handling only |

#### What Happens

```
CartographerMap                      Trailblazer Execution
       │                                    │
       │──── compile_to_binary() ──────────→│
       │                                    │ (generate strict execution plan)
       │                                    │ (pre-compute all paths)
       │                                    │
       │←──── executable_workflow ──────────│
       │                                    │
       │──── execute(input) ───────────────→│
       │                                    │ (follow map exactly)
       │                                    │ (generate receipts)
       │                                    │ (block any deviation)
       │                                    │
       │←──── result + receipt_chain ───────│
       │                                    │
[VERIFICATION: Receipts can be independently validated]
```

#### Allowed Operations

- ✅ Mapped transitions only
- ✅ Pre-approved external calls (with receipts)
- ✅ Deterministic computations
- ❌ Unmapped states
- ❌ Unreceipted external calls
- ❌ Dynamic capsule changes
- ❌ Curvature modifications

#### Receipt Requirements

Every external interaction requires:

```json
{
  "receipt_id": "uuid-v4",
  "timestamp": "ISO-8601",
  "operation": "api_call",
  "target": "https://api.example.com/endpoint",
  "request_hash": "sha256:...",
  "response_hash": "sha256:...",
  "signature": "ed25519:...",
  "verifiable": true
}
```

#### Output: TrailblazerExecution

A cryptographically verifiable execution record:
- Complete execution trace
- All receipts in chain
- Final result
- Performance metrics
- Verification proof

---

## Determinism Tiers

Each PCT phase operates within specific determinism tiers:

### Tier Definitions

| Tier | Name | Description | Allowed Operations |
|------|------|-------------|-------------------|
| **1** | Exploratory | Maximum freedom | Everything |
| **2** | Guided | Soft constraints | Most operations + logging |
| **3** | Structured | Moderate constraints | Mapped operations + penalties |
| **4** | Strict | Minimum freedom | Only pre-approved operations |

### Phase-Tier Mapping

```
         Tier 1      Tier 2      Tier 3      Tier 4
         ──────      ──────      ──────      ──────
         
Pathfinder:
         ████████████████████
         [───── operates here ─────]
         
Cartographer:
                     ████████████████████
                     [─── operates here ───]
                     
Trailblazer:
                                         ████████
                                         [here]
```

### Tier Transition Rules

```python
# Moving to higher tier (more strict)
def can_increase_tier(current_tier, target_tier, validation_results):
    if target_tier <= current_tier:
        return True  # Can always go back
    
    # Each tier increase requires validation
    required_checks = {
        1 → 2: "all_actions_recorded",
        2 → 3: "map_validated",
        3 → 4: "determinism_proven"
    }
    
    return validation_results[required_checks[current_tier → target_tier]]
```

---

## Artifacts

### Artifact Flow

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ PathfinderEpisode│────►│ CartographerMap  │────►│TrailblazerBinary │
└──────────────────┘     └──────────────────┘     └──────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
   Raw trace data          Structured graph         Executable + proofs
```

### PathfinderEpisode Schema

```json
{
  "episode_id": "uuid",
  "started_at": "timestamp",
  "ended_at": "timestamp",
  "initial_state": { "manifold": "...", "position": [...] },
  "actions": [
    {
      "sequence": 1,
      "action_type": "move",
      "parameters": {...},
      "pre_state": {...},
      "post_state": {...},
      "result": "success|failure",
      "duration_ms": 42
    }
  ],
  "final_state": {...},
  "metadata": {
    "agent_id": "...",
    "capsules_used": [...],
    "resources_consumed": {...}
  }
}
```

### CartographerMap Schema

```json
{
  "map_id": "uuid",
  "source_episodes": ["episode_id_1", "episode_id_2"],
  "created_at": "timestamp",
  "nodes": [
    {
      "node_id": "n1",
      "state_signature": "hash",
      "state_description": {...},
      "determinism_level": 3
    }
  ],
  "edges": [
    {
      "from": "n1",
      "to": "n2",
      "action": {...},
      "conditions": [...],
      "probability": 1.0
    }
  ],
  "warnings": [
    {
      "type": "non_deterministic_branch",
      "location": "n5",
      "resolution_required": true
    }
  ],
  "validation_status": "validated|pending|failed"
}
```

### TrailblazerBinary Schema

```json
{
  "binary_id": "uuid",
  "source_map": "map_id",
  "compiled_at": "timestamp",
  "execution_plan": {
    "steps": [...],
    "branch_table": {...},
    "receipt_requirements": [...]
  },
  "executions": [
    {
      "execution_id": "uuid",
      "input": {...},
      "output": {...},
      "receipt_chain": [...],
      "verification_hash": "sha256:..."
    }
  ]
}
```

---

## Human Roles and Checkpoints

### Role Definitions

| Role | Phase | Responsibilities |
|------|-------|------------------|
| **Explorer** | Pathfinder | Review episode quality, identify promising paths |
| **Analyst** | Cartographer | Validate maps, resolve ambiguities, approve transitions |
| **Operator** | Trailblazer | Monitor executions, handle exceptions |
| **Auditor** | All | Verify receipts, compliance checking |

### Checkpoint Matrix

```
PHASE TRANSITION CHECKPOINTS
═══════════════════════════════════════════════════════════════

    Pathfinder ──────► Cartographer
                 │
                 ├── Human Review: Episode Quality
                 │   - Are explorations meaningful?
                 │   - Did agent find working paths?
                 │   - Any concerning behaviors?
                 │
                 └── Approval Required: YES
                     
    Cartographer ────► Trailblazer
                 │
                 ├── Human Review: Map Validation
                 │   - Is the map complete?
                 │   - Are non-deterministic elements resolved?
                 │   - External call inventory approved?
                 │
                 ├── Approval Required: YES
                 │
                 └── Additional: Sign-off on receipt requirements

    Trailblazer ─────► Production
                 │
                 ├── Human Review: Verification
                 │   - Receipt chain valid?
                 │   - Test executions successful?
                 │   - Performance acceptable?
                 │
                 └── Approval Required: YES (for initial deployment)
```

### Checkpoint Actions

```python
# At each checkpoint, humans can:

class CheckpointActions:
    APPROVE = "approve"           # Proceed to next phase
    REJECT = "reject"             # Go back, try again
    MODIFY = "modify"             # Edit artifact before proceeding
    ESCALATE = "escalate"         # Bring in additional reviewers
    ANNOTATE = "annotate"         # Add notes without blocking
```

---

## PCT + AGUA Integration

### How They Work Together

```
┌─────────────────────────────────────────────────────────────┐
│                    PCT (Workflow Rules)                      │
│  ┌─────────────┬─────────────────┬───────────────────────┐  │
│  │ Pathfinder  │  Cartographer   │     Trailblazer       │  │
│  │ Rules       │  Rules          │     Rules             │  │
│  └─────────────┴─────────────────┴───────────────────────┘  │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 AGUA (Enforcement)                    │   │
│  │                                                       │   │
│  │   Intercept ──► Check Phase ──► Apply Rules ──► Act  │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Geometric Infrastructure                 │   │
│  │         (Manifolds, Sectors, Geodesics)              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

| PCT Event | AGUA Action |
|-----------|-------------|
| Episode starts | Initialize fresh manifold sector |
| Action attempted | Intercept, check phase rules, allow/block |
| Sector boundary | Enforce drift policy (allow/penalize/block) |
| External call | Check receipt requirements |
| Phase transition | Reconfigure enforcement strictness |
| Artifact generated | Store with geometric metadata |

### Code Example: AGUA Enforcing PCT

```python
class AguaPctEnforcer:
    def __init__(self, current_phase: str):
        self.phase = current_phase
        self.policies = load_phase_policies(current_phase)
    
    def intercept_action(self, agent_id: str, action: Action) -> ActionResult:
        # Step 1: Record (always)
        self.trace_recorder.record(agent_id, action)
        
        # Step 2: Phase-specific checks
        if self.phase == "pathfinder":
            # Almost everything allowed
            return self.execute_and_record(action)
        
        elif self.phase == "cartographer":
            # Check for drift
            drift = self.calculate_drift(agent_id, action)
            if drift > 0:
                self.apply_drift_penalty(agent_id, drift)
            return self.execute_and_record(action)
        
        elif self.phase == "trailblazer":
            # Strict checks
            if not self.is_mapped_action(action):
                raise UnmappedActionError(action)
            
            if action.is_external and not action.has_valid_receipt:
                raise ReceiptRequiredError(action)
            
            return self.execute_with_receipt(action)
    
    def transition_phase(self, target_phase: str, approval: HumanApproval):
        if not approval.is_valid:
            raise PhaseTransitionBlocked("Human approval required")
        
        self.validate_transition_requirements(target_phase)
        self.phase = target_phase
        self.policies = load_phase_policies(target_phase)
        self.reconfigure_manifold_permissions()
```

---

## Workflow Examples

### Example 1: Building a Customer Support Agent

#### Phase 1: Pathfinder

```
Goal: Explore how to handle customer inquiries

Episode 1: Try various response strategies
  - Action: Query knowledge base → Success
  - Action: Generate response → Success
  - Action: Ask clarifying question → Success
  - Action: Escalate to human → Success

Episode 2: Test edge cases
  - Action: Handle angry customer → Partial success
  - Action: Process refund request → Failed (need API)
  - Action: Multi-turn conversation → Success

Artifact: PathfinderEpisode with 47 actions, 3 failures
```

#### Phase 2: Cartographer

```
Input: 2 PathfinderEpisodes

Analysis:
  - Identified 5 main conversation flows
  - Found 2 external API dependencies (CRM, Payment)
  - Detected 1 non-deterministic branch (sentiment analysis)

Map Construction:
  - Node: InitialGreeting
  - Node: IssueIdentification  
  - Node: KnowledgeBaseLookup
  - Node: ResponseGeneration
  - Node: EscalationDecision
  - Node: Closure

Warnings:
  - ⚠️ Sentiment analysis not deterministic
  - Resolution: Use threshold-based classification

Human Checkpoint: Analyst approves map, signs off on API list

Artifact: CartographerMap with 12 nodes, 18 edges
```

#### Phase 3: Trailblazer

```
Input: Validated CartographerMap

Compilation:
  - Generated execution binary
  - Pre-computed all decision paths
  - Registered receipt requirements:
    - CRM API: customer_lookup, update_ticket
    - Payment API: process_refund

Execution:
  Input: "I want a refund for order #12345"
  
  Step 1: InitialGreeting → "Hello! I'll help with that."
  Step 2: IssueIdentification → refund_request detected
  Step 3: CRM API call → receipt_001 generated
  Step 4: Payment API call → receipt_002 generated
  Step 5: ResponseGeneration → "Refund processed!"
  Step 6: Closure → satisfaction survey sent
  
  Output: Refund completed
  Receipt Chain: [receipt_001, receipt_002]
  Verification: All receipts valid ✓

Artifact: TrailblazerExecution with full audit trail
```

### Example 2: Data Pipeline Automation

```
┌─────────────────────────────────────────────────────────────┐
│ PATHFINDER: Explore data transformations                    │
│   - Try different cleaning approaches                       │
│   - Test aggregation strategies                             │
│   - Experiment with output formats                          │
│   Artifact: 5 episodes, 200+ actions                        │
├─────────────────────────────────────────────────────────────┤
│ CARTOGRAPHER: Build transformation map                      │
│   - Extract successful cleaning sequence                    │
│   - Document aggregation logic                              │
│   - Define output schema                                    │
│   Human Checkpoint: Data engineer reviews                   │
│   Artifact: Transformation DAG with 8 stages                │
├─────────────────────────────────────────────────────────────┤
│ TRAILBLAZER: Production pipeline                            │
│   - Deterministic execution daily at 2 AM                   │
│   - Receipts for all external data fetches                  │
│   - Alerts on any deviation                                 │
│   Artifact: 30 days of verified executions                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Common Issues

| Problem | Phase | Solution |
|---------|-------|----------|
| Episode too short | Pathfinder | Increase exploration budget |
| Map has loops | Cartographer | Add termination conditions |
| Receipt validation fails | Trailblazer | Check timestamp sync |
| Drift penalties too high | Cartographer | Refine sector boundaries |
| Human checkpoint stuck | Any | Escalate to supervisor |

### Error Recovery

```python
# Phase-specific recovery strategies

def recover_from_error(phase: str, error: PCTError):
    if phase == "pathfinder":
        # Just log and continue - exploration should try failures
        log_and_continue(error)
        
    elif phase == "cartographer":
        # May need to re-explore or refine map
        if error.type == "unmappable_behavior":
            request_additional_pathfinder_episode()
        else:
            refine_map_at_error_location(error)
            
    elif phase == "trailblazer":
        # Serious - must halt and alert
        halt_execution()
        generate_incident_report(error)
        notify_human_operator(error)
```

### Metrics to Monitor

| Metric | Healthy Range | Alert Threshold |
|--------|---------------|-----------------|
| Pathfinder success rate | 30-70% | <10% |
| Cartographer map coverage | 90%+ | <80% |
| Trailblazer receipt validity | 100% | <100% |
| Phase transition approval rate | 80%+ | <50% |
| Drift penalty accumulation | <10/episode | >50/episode |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    PCT QUICK REFERENCE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PATHFINDER     → CARTOGRAPHER    → TRAILBLAZER             │
│  ══════════       ════════════      ═══════════             │
│  Explore          Map               Execute                  │
│  Record           Validate          Prove                    │
│  Tier 1-2         Tier 2-3          Tier 4                  │
│                                                              │
│  Artifacts:                                                  │
│  Episode      →   Map           →   Binary + Receipts       │
│                                                              │
│  Human Checkpoints:                                          │
│  Review       →   Approve       →   Monitor                  │
│                                                              │
│  AGUA Integration:                                           │
│  Allow all   →   Penalize drift →   Block violations        │
│                                                              │
│  Commands:                                                   │
│  start_episode    map_trace         canonize                │
│  end_episode      validate_map      replay                  │
│                   approve           verify_receipts         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

*PCT: From exploration to production, safely and verifiably.*
