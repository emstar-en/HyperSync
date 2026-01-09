#!/usr/bin/env python3
"""
Example: Setting up an ICO network with multiple domains
"""

from hypersync.nvm.ld_manager import LDManager
from hypersync.nvm.ico_router import ICORouter

def main():
    # Initialize managers
    ld_manager = LDManager()
    router = ICORouter(ld_manager)

    # Create primary secure domain
    print("Creating primary secure domain...")
    primary_ld = ld_manager.create_domain(
        name="primary-secure",
        dimension=4,
        security_level="isolated",
        metric_type="minkowski"
    )
    print(f"✓ Created: {primary_ld.ld_id}")

    # Create secondary domain for external communication
    print("\nCreating secondary domain...")
    secondary_ld = ld_manager.create_domain(
        name="external-gateway",
        dimension=4,
        security_level="protected",
        metric_type="minkowski"
    )
    print(f"✓ Created: {secondary_ld.ld_id}")

    # Bridge the domains
    print("\nCreating bridge...")
    bridge = ld_manager.create_bridge(
        primary_ld.ld_id,
        secondary_ld.ld_id,
        bridge_type="wormhole",
        bandwidth=1e9,
        latency_bound=0.001
    )
    print(f"✓ Bridge created: {bridge['bridge_type']}")

    # Register model in primary domain
    print("\nRegistering model node...")
    model_addr = router.register_node(
        ld_id=primary_ld.ld_id,
        address_type="model",
        name="inference-model-1"
    )
    print(f"✓ Model registered: {model_addr.node_id}")

    # Register service in secondary domain
    print("\nRegistering service node...")
    service_addr = router.register_node(
        ld_id=secondary_ld.ld_id,
        address_type="service",
        name="api-gateway"
    )
    print(f"✓ Service registered: {service_addr.node_id}")

    # Compute route
    print("\nComputing route...")
    route = router.compute_route(model_addr.node_id, service_addr.node_id)
    print(f"✓ Route found:")
    print(f"  Path type: {route['path_type']}")
    print(f"  Crosses LD: {route['crosses_ld']}")
    print(f"  Hops: {len(route['hops'])}")

    print("\n✓ ICO network setup complete!")

if __name__ == "__main__":
    main()
