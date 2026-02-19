# Acceptance Gates and Information Thermodynamics

Acceptance Gates regulate what information is allowed to cross a Holon's
boundaries. They are the primary tool for turning raw exploratory noise
into structured, trustable signal.

## 1. The problem of noise

In a loose or exploratory Holon, agents (scouts) generate a high volume
of data. Much of this is noise.

How does the orchestrator (lead) filter this without manually reviewing
every bit, while still allowing rare but important outliers to surface?

---

## 2. The geometric solution: signal attenuation

We utilize the properties of hyperbolic space to naturally filter
information.

### 2.1 Distance-based decay

In the Poincare disk, space expands exponentially. The signal strength S
of a report sent from a scout at u to the lead at v decays according to
hyperbolic distance d(u, v):

  S = S_initial * exp(-lambda * d(u, v))

- lambda: the decay constant (a property of the medium and/or policy).
- Implication: scouts far away (deep in the weeds) must generate very
  high energy (high confidence or importance) reports for the signal to
  reach the lead with sufficient strength.
- Result: trivial findings from the fringe naturally fade out before
  reaching the center.

### 2.2 Geometry-aware policy knobs

A Holon can parameterize its geometric gating via:

- metric policy (which distance function and curvature to use),
- decay profile (pure exponential, clipped, piecewise),
- region selectors (stronger or weaker gating in specific sectors).

These parameters live in either the Holon's acceptance_gates configuration
or a reusable metric or geometry policy referenced by id.

---

## 3. The thermodynamic solution: Metropolis-Hastings gates

We model an acceptance gate on the lead's inbox as a thermodynamic system.

### 3.1 Information energy E

Every report R has an information energy E(R), calculated by the scout
or by the system:

  E(R) = relevance * confidence

Additional factors may be folded in (for example cost, risk, recency),
but the core idea is that interesting, well supported reports have high
energy.

### 3.2 Acceptance probability P

The lead accepts the report with probability P governed by a Boltzmann
style rule:

  P(accept) = min(1, exp(-(E_threshold - E(R)) / T))

- E_threshold: the target energy for admission.
- T: the temperature of the Holon (set by the user or a policy).

### 3.3 Dynamics

- High temperature (brainstorming): T is high. The lead accepts almost
  everything, even low energy reports. The system is creative but noisy.
- Low temperature (convergence): T is low. The lead only accepts reports
  with energy above the threshold. The system is strict and precise.

The same mathematical gate can be applied at multiple boundaries:
scout to lead, Holon to parent Holon, or Holon to external world.

---

## 4. Gate specification

To make acceptance gates programmable, we define a generic GateSpec
structure (conceptual, not strictly tied to any single schema):

{
  "gate_id": "gate:lead_inbox",
  "scope": "orchestrator_inbox",
  "strategy": "metropolis_hastings",
  "geometry": {
    "metric_policy_id": "metric:research_default",
    "distance_decay_lambda": 1.0
  },
  "thermodynamics": {
    "temperature": 0.75,
    "energy_barrier": 0.4
  },
  "limits": {
    "max_queue": 512,
    "max_rate_per_tick": 64
  }
}

This can be attached to a Holon's acceptance_gates.ingress, egress, or
internal configuration, or referenced by id from multiple Holons.

---

## 5. Implementation in the research Holon

In the Deep_Research_Unit_Alpha example:

1. Scout behavior:
   - a scout finds a data point,
   - it calculates local energy E_local (from relevance, confidence, etc.),
   - it attempts to push the data toward the lead.

2. The gate check:
   - the system calculates distance d between scout and lead,
   - it applies decay: E_received = E_local * exp(-lambda * d),
   - it evaluates the Metropolis-Hastings rule using the current
     temperature T of the Holon,
   - if accepted, the data enters the lead's context window,
   - if rejected, the data is discarded or stored in a local rejected
     buffer for later audit.

3. Multi-stage gating (optional):
   - first, a cheap geometric gate discards messages that are obviously
     low energy given their distance,
   - second, a more expensive semantic or risk-aware gate examines the
     remaining candidates.

---

## 6. Why this is geometry-aware

This is not just a simple if value > 5 check. It is spatial and
thermodynamic:

- a scout close to the lead (working on core tasks) has a louder voice,
- a scout far from the lead (working on fringe theories) needs
  extraordinary evidence to be heard,
- the Holon's temperature and gate settings allow the user to dial the
  exploration or exploitation trade-off.

This mimics how real-world organizations work and encodes the idea into
explicit geometric and probabilistic laws.
