# VNES: The Efficiency Subsystem

## Overview
The **Vector-Native Extension System (VNES)** is HyperSync's "Standard Library" for AI Agents. It is designed to minimize token usage and maximize determinism.

## The "Capsule" Concept
A **Capsule** is a pre-loaded, pre-verified unit of capability.

### Why Capsules?
When an AI Agent needs to perform a complex task (e.g., "Calculate a Voronoi Tesselation"), it has two options:
1.  **Generative (Slow/Expensive):** Write the Python code for Voronoi Tesselation token-by-token.
2.  **VNES (Fast/Cheap):** Load the `hypersync.geo.voronoi` Capsule.

### Capsule Types
- **Logic Capsules:** Pre-compiled algorithms (Solvers, Parsers).
- **Data Capsules:** Static datasets (Reference tables, Embeddings).
- **Schema Capsules:** Data validation structures.

## Integration
VNES is **not** the operating system. It is a **Service** available to Agents.
- Agents query the VNES Registry to find tools.
- Agents "mount" Capsules to extend their capabilities.

## Bootstrap-Aware Efficiency

During first-run, VNES SHOULD favor extension profiles that:

- Match the detected `hardware_profile`.
- Respect constraints such as `no_large_models` or `power_saving_mode`.
- Minimize cold-start and memory footprint while keeping the system
  responsive.

The selection and activation of such profiles SHOULD be recorded via
bootstrap receipts and, where appropriate, SDL query receipts.
