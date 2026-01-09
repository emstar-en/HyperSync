# Tools Guide

## Available Tools

### 1. ico.ld.create
**Purpose**: Create a new Lorentzian Domain (workspace)

**Parameters:**
- `name` (required): Domain name
- `security_level` (optional): "isolated", "shared", "public" (default: "isolated")
- `dimension` (optional): 4 (default)
- `curvature` (optional): 0.0 (default, flat spacetime)
- `metric_type` (optional): "minkowski", "schwarzschild", "kerr" (default: "minkowski")

**Returns:**
```json
{
 "ld_id": "ld_abc123",
 "name": "secure-workspace"
}
```

**Usage hints:**
- Always use "isolated" security for production workspaces
- Flat Minkowski metric is suitable for most use cases
- Curved metrics (Schwarzschild, Kerr) are for advanced routing scenarios

**Example calls:**
```python
# Basic secure workspace
create_ld({"name": "secure-workspace"})

# Custom configuration
create_ld({
 "name": "research-domain",
 "security_level": "shared",
 "curvature": -0.1
})
```

---

### 2. ico.node.register
**Purpose**: Register a node (model, agent, service) in a Lorentzian Domain

**Parameters:**
- `ld_id` (required): Target domain ID
- `node_id` (required): Unique node identifier
- `address_type` (optional): "model", "agent", "service" (default: "model")
- `coordinates` (optional): 4D coordinates (default: origin)

**Returns:**
```json
{
 "node_id": "gpt-4",
 "ld_id": "ld_abc123"
}
```

**Usage hints:**
- Node IDs must be unique within a domain
- Coordinates default to origin (t=0, x=0, y=0, z=0)
- Use descriptive node IDs for easier routing

**Example calls:**
```python
# Register a model at origin
register_node({
 "ld_id": "ld_abc123",
 "node_id": "text-summarizer",
 "address_type": "model"
})

# Register with custom coordinates
register_node({
 "ld_id": "ld_abc123",
 "node_id": "qa-assistant",
 "address_type": "model",
 "coordinates": {"t": 0, "x": 1, "y": 0, "z": 0}
})
```

---

### 3. ico.route.compute
**Purpose**: Compute a route between two nodes

**Parameters:**
- `src` (required): Source node ID
- `dst` (required): Destination node ID
- `constraints` (optional): Routing constraints

**Returns:**
```json
{
 "path": ["node_a", "bridge_1", "node_b"]
}
```

**Usage hints:**
- Nodes must be registered before routing
- Cross-domain routing requires bridges
- Routes are computed using geodesic paths in curved spacetime

**Example calls:**
```python
# Simple route
compute_route({
 "src": "text-summarizer",
 "dst": "qa-assistant"
})

# Route with constraints
compute_route({
 "src": "model_a",
 "dst": "model_b",
 "constraints": {"max_hops": 3, "avoid": ["node_x"]}
})
```

---

### 4. catalog.models
**Purpose**: Scan and catalog model descriptors from `.hypersync/models/`

**Parameters:**
- None (scans default directory)

**Returns:**
```json
{
 "count": 2,
 "models": [
 {
 "name": "text-summarizer",
 "type": "model",
 "capabilities": ["summarize:text"]
 },
 {
 "name": "qa-assistant",
 "type": "model",
 "capabilities": ["qa:text"]
 }
 ]
}
```

**Usage hints:**
- Automatically creates `.hypersync/models/` if missing
- Skips invalid JSON files
- Returns empty list if no descriptors found

**Example calls:**
```python
# Scan for models
catalog_models({})
```

---

### 5. agent.compose
**Purpose**: Compose a multi-model agent from existing nodes

**Parameters:**
- `name` (required): Agent name
- `capabilities` (required): List of capabilities
- `members` (required): List of member node IDs
- `ld_id` (optional): Target domain (uses default if not specified)

**Returns:**
```json
{
 "agent_id": "agent.network-operator",
 "ld_id": "ld_abc123"
}
```

**Usage hints:**
- Members must be registered nodes
- Agent is automatically registered as a node
- Capabilities should match member capabilities

**Example calls:**
```python
# Compose a network operator
compose_agent({
 "name": "network-operator",
 "capabilities": ["route", "orchestrate"],
 "members": ["text-summarizer", "qa-assistant"]
})

# Compose with specific domain
compose_agent({
 "name": "research-assistant",
 "capabilities": ["research", "summarize", "qa"],
 "members": ["model_a", "model_b", "model_c"],
 "ld_id": "ld_research"
})
```

---

### 6. status.summary
**Purpose**: Get a summary of the current HyperSync environment

**Parameters:**
- None

**Returns:**
```json
{
 "domains": [
 {
 "ld_id": "ld_abc123",
 "name": "secure-workspace",
 "node_count": 3
 }
 ],
 "total_nodes": 3,
 "total_agents": 1
}
```

**Usage hints:**
- Provides quick overview of setup
- Useful for debugging and verification
- Shows all domains and their contents

---

## Tool Execution Flow

1. **Policy Check**: Verify action is allowed
2. **Parameter Validation**: Check required parameters
3. **Execution**: Call underlying HyperSync modules
4. **Result Formatting**: Return structured response
5. **Telemetry**: Log action (with PII redaction)

## Error Handling

### Common Errors

**PolicyViolation:**
```
Action not allowed by current policy.
Check policies/nvm/iam.policy.json
```

**NodeNotFound:**
```
Node '{node_id}' not found in domain '{ld_id}'.
Register the node first with ico.node.register
```

**DomainNotFound:**
```
Domain '{ld_id}' does not exist.
Create it first with ico.ld.create
```

**InvalidParameters:**
```
Missing required parameter: {param_name}
```

## Best Practices

1. **Always check policy** before suggesting actions
2. **Validate node existence** before routing
3. **Use descriptive IDs** for better user experience
4. **Provide context** in error messages
5. **Log all operations** for debugging
