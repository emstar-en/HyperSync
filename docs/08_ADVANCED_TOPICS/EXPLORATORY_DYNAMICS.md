# Exploratory Dynamics & Loose Objectives

## Overview
In HyperSync, not all agents are designed for efficient, direct pathfinding. Some tasks require **Exploration**—wandering through the data manifold to discover latent connections, anomalies, or creative insights. This behavior is governed by **Movement Policies** with high "Temperature".

## The Physics of Exploration

### 1. Temperature ($T$)
Temperature is a scalar value that introduces stochasticity into the agent's trajectory.
- **Low Temp ($T 	o 0$):** The agent follows the geodesic (shortest path) to its objective strictly. This is "Exploitation".
- **High Temp ($T 	o 1$):** The agent takes probabilistic detours. It is more likely to jump to high-entropy regions or cross "energy barriers" in the semantic landscape. This is "Exploration".

### 2. Movement Models

#### A. Gradient Descent (Strict)
*   **Use Case:** Specific task execution (e.g., "Retrieve file X").
*   **Behavior:** Moves directly towards the target coordinate minimizing distance.

#### B. Langevin Dynamics (Loose)
*   **Use Case:** Creative writing, brainstorming, broad research.
*   **Behavior:** Adds Gaussian noise to the gradient. The agent "wobbles" around the optimal path, potentially stumbling upon adjacent relevant concepts.

#### C. Lévy Flights (Discovery)
*   **Use Case:** Anomaly detection, "Unknown Unknowns".
*   **Behavior:** Mostly small steps with occasional long-distance jumps. This prevents the agent from getting stuck in local optima (echo chambers).

## Configuring "Loose" Agents

To create an agent with a "Loose" objective, you configure its `MovementPolicy` in the `AgentStack`:

```json
{
  "stack_id": "creative_writer",
  "geometry_config": {
    "movement_policy": {
      "type": "langevin",
      "parameters": {
        "temperature": 0.8,
        "exploration_bias": 0.5
      }
    }
  }
}
```

## Application: The "Muse" Agent
A "Muse" agent might be spawned with a high temperature and no specific target coordinate. Its goal is simply to traverse the manifold, picking up concepts from different sectors and synthesizing them into new ideas. It "surfs" the curvature of the space.
