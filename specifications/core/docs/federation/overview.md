# ICO Network Federation

Connect multiple ICO networks and create bridges between Lorentzian Domains.

## Quick Start

### Create a Federation

```bash
hypersync federation create \
 --name "global-network" \
 --network ico-us-east \
 --network ico-eu-west \
 --network ico-asia-pacific
```

### Create LD Bridges

```bash
# Direct bridge
hypersync federation bridge \
 --source ld-us-prod-001 \
 --target ld-eu-prod-001 \
 --type direct

# Gateway bridge
hypersync federation bridge \
 --source ld-eu-prod-001 \
 --target ld-asia-prod-001 \
 --type gateway
```

### Find Routes

```bash
hypersync federation route \
 --from ld-us-prod-001 \
 --to ld-asia-prod-001
```

## Bridge Types

- **direct**: Direct connection between LDs
- **relay**: Relayed through intermediate LD
- **gateway**: Gateway with protocol translation

## Use Cases

- Multi-region deployments
- Cross-network model sharing
- Disaster recovery
- Load distribution
