"""
Example: Cross-Node File Federation
"""

import logging
from hypersync.federation.file_federation import (
    FileFederationManager,
    RemoteNode,
    SyncStrategy
)

logging.basicConfig(level=logging.INFO)


def main():
    print("=" * 80)
    print("Cross-Node File Federation Example")
    print("=" * 80)

    # Simulate two nodes
    print("\nSetting up nodes...")

    # Node 1
    manager1 = FileFederationManager("node-1")

    # Node 2
    manager2 = FileFederationManager("node-2")

    # Register each other
    manager1.register_node(RemoteNode("node-2", "node2.local", 8443))
    manager2.register_node(RemoteNode("node-1", "node1.local", 8443))

    # Node 1: Create and federate file
    print("\nNode 1: Creating federated file...")
    test_file = "/tmp/federated_example.txt"

    with open(test_file, 'w') as f:
        f.write("Hello from Node 1!")

    federated = manager1.federate_file(
        test_file,
        sync_strategy=SyncStrategy.BIDIRECTIONAL
    )

    print(f"Federated: {federated.path}")
    print(f"Owner: {federated.owner_node}")
    print(f"Replicas: {federated.replicas}")

    # Node 2: Access file
    print("\nNode 2: Accessing federated file...")
    content = manager2.read_file(test_file)
    print(f"Content: {content.decode()}")

    # Node 2: Modify file
    print("\nNode 2: Modifying file...")
    manager2.write_file(test_file, b"Modified by Node 2!")

    # Node 1: Read updated content
    print("\nNode 1: Reading updated content...")
    content = manager1.read_file(test_file)
    print(f"Content: {content.decode()}")

    # Statistics
    print("\nNode 1 Stats:")
    stats1 = manager1.get_stats()
    for key, value in stats1.items():
        print(f"  {key}: {value}")

    print("\nNode 2 Stats:")
    stats2 = manager2.get_stats()
    for key, value in stats2.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
