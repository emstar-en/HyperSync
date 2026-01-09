# Session & Basepoint Caching Specification

## Overview
This document specifies the caching strategy for HyperSync sessions, focusing on the reuse of expensive geometric computations (transport maps) and basepoint-dependent terms.

## Cache Keys
The primary cache key is a composite tuple uniquely identifying the context of the computation:
`Key = (tenant_id, session_id, basepoint_hash, domain_id)`

- **tenant_id**: Multi-tenancy isolation.
- **session_id**: Unique identifier for the active synchronization session.
- **basepoint_hash**: SHA-256 hash of the current geometric basepoint (origin or reference frame).
- **domain_id**: The specific hyperbolic domain (e.g., `H^2_Poincare`).

## Invalidation Policy
Cache entries are invalidated based on geometric drift and policy changes.

### 1. Geometric Drift
Invalidation occurs if the basepoint moves beyond the defined tolerance $\delta$:
$$ d(basepoint_{current}, basepoint_{cached}) > \delta $$
Where $d$ is the Poincaré distance metric.

### 2. Policy Change
Any update to the `numeric_policy` (e.g., precision changes, tolerance adjustments) triggers an immediate invalidation of all associated cache entries.

### 3. Time-to-Live (TTL)
If no geometric or policy invalidation occurs, entries expire after a default TTL (e.g., 300 seconds) to prevent stale state accumulation.

## Reuse Strategy
### Transport Maps
Parallel transport maps used to move vectors between tangent spaces are cached. If the basepoint remains within $\delta$, the cached map is reused, applying a first-order correction if necessary.

### Basepoint-Dependent Terms
Pre-computed values dependent solely on the basepoint (e.g., metric tensors at $p$, Christoffel symbols) are cached and reused across the batch/stream until invalidation.
