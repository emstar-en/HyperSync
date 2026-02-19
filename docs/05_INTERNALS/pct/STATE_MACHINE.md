# PCT State Machine Logic

## Overview
This module manages the lifecycle of a workflow as it evolves from an experimental trace (Pathfinder) to a hardened artifact (Trailblazer).

## State Transitions

### 1. Pathfinder -> Cartographer (Promotion)
**Trigger**: `promote_to_cartographer(episode_ids)`
**Logic**:
1.  **Aggregation**: Combine multiple `PathfinderEpisode` traces.
2.  **Intersection**: Find the common graph of operations.
3.  **Parameterization**: Identify variable inputs vs. constants.
4.  **Validation**: Ensure success rate > Threshold (e.g., 80%).
5.  **Output**: Generate a `WorkflowMap` (JSON graph).

### 2. Cartographer -> Trailblazer (Canonization)
**Trigger**: `canonize_workflow(workflow_map_id)`
**Logic**:
1.  **Determinism Check**: Re-run the workflow 100 times with the same seed.
    *   If *any* output bit differs -> FAIL.
2.  **Security Audit**: Scan for unauthorized network/disk access.
3.  **Optimization**: Flatten the graph, remove debug steps.
4.  **Signing**: Cryptographically sign the artifact.
5.  **Output**: Generate `CanonizedWorkflow` (Binary).

### 3. Any -> Pathfinder (Demotion)
**Trigger**: `drift_alert` or `manual_override`
**Logic**:
1.  **Unlock**: Remove restrictions.
2.  **Fork**: Create a new mutable copy of the workflow.
3.  **Alert**: Notify operators that the "Golden Path" is broken.

## Pseudocode

```python
def promote_to_cartographer(episode_ids: List[str]) -> WorkflowMap:
    episodes = load_episodes(episode_ids)

    # 1. Validate Success Rate
    success_count = sum(1 for e in episodes if e.status == "SUCCESS")
    if success_count / len(episodes) < 0.8:
        raise QualityError("Insufficient success rate for promotion")

    # 2. Extract Common Graph
    graph = extract_common_subgraph(episodes)

    # 3. Create Map
    workflow_map = WorkflowMap(graph=graph, version="0.1.0-alpha")
    save_artifact(workflow_map)

    return workflow_map
```
