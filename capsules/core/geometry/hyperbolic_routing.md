# Hyperbolic Geometry Routing (Poincaré Model)

## Overview
HyperSync utilizes **Hyperbolic Geometry** (specifically the Poincaré Disk model) as the fundamental substrate for orchestration. This allows for exponential expansion of resource space within a bounded region, ideal for hierarchical and fractal systems like HyperSync.

## Core Concepts

### The Poincaré Disk
We map the computational state space onto the unit disk $D = \{z \in \mathbb{C} : |z| < 1\}$.
- **Distance:** $d(u, v) = 	ext{arccosh}\left(1 + 2rac{|u-v|^2}{(1-|u|^2)(1-|v|^2)}ight)$
- **Geodesics:** Arcs of circles orthogonal to the boundary of the disk.

### Deterministic Routing
To satisfy `D0_bit_exact` requirements:
1.  **Fixed-Point Arithmetic:** All geometric calculations use a custom fixed-point library to ensure cross-platform consistency.
2.  **Seeded Metric Updates:** The metric tensor $g_{ij}$ evolves based on a hash-chain of telemetry data, ensuring that any two nodes replaying the same history derive the exact same geometry.

### Safety Fences & ROIs
- **Safety Fences:** Geodesic polygons that bound the valid state space for an agent. Attempting to route outside a fence triggers a `GeometricSingularityError`.
- **Regions of Interest (ROIs):** Dynamically allocated subspaces for specific tenants or workloads, isolated by high-curvature "ridges" that make cross-ROI routing prohibitively "expensive" (distant).

### HVS Integration
Routing decisions are tightly coupled with **Hyperbolic Vector Storage (HVS)**. The "location" of a datum in HVS corresponds to its coordinate in the routing manifold, ensuring data locality is a geometric property.
