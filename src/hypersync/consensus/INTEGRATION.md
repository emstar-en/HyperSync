# Integration with Assembly System

## Automatic Consensus Application

When creating an assembly with consensus requirements:

```python
from hypersync.assembly import AssemblyManager
from hypersync.consensus import ConsensusAttestationManager

assembly_mgr = AssemblyManager()
consensus_mgr = ConsensusAttestationManager()

# Create assembly
assembly = assembly_mgr.create_assembly(
 name="consensus-assembly",
 stack_id="stack-abc123",
 target_ld="ld-prod-001"
)

# Apply consensus
consensus_mgr.apply_consensus(
 target_type="assembly",
 target_id=assembly.assembly_id,
 mechanism_id="mech-bft",
 parameters={"quorum_size": 4}
)

# Deploy - consensus will be enforced
deployment = assembly_mgr.deploy_assembly(assembly.assembly_id)
```

## CLI Integration

Add to hypersync/cli.py:

```python
from hypersync.consensus.consensus_cli import register_cli as register_consensus_cli

# In main CLI setup:
register_consensus_cli(cli)
```

## API Integration

Add to hypersync API setup:

```python
from hypersync.consensus.consensus_api import register_api as register_consensus_api

# In FastAPI app setup:
register_consensus_api(app)
```
