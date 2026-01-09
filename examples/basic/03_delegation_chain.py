#!/usr/bin/env python3
"""
Delegation Chain Example

Demonstrates delegation chain tracking and visualization.
"""

from hypersync.agents.delegation.tracker import DelegationChainTracker
from hypersync.visualization.chain_visualizer import visualize_chain


def main():
    """Demonstrate delegation chain tracking."""

    # Initialize tracker
    tracker = DelegationChainTracker(max_depth=5)

    # Start chain
    chain = tracker.start_chain(
        chain_id='chain-example',
        requester_id='user-alice',
        root_agent_id='agent-orchestrator'
    )

    print("Starting delegation chain...")

    # Add delegations
    tracker.add_delegation('chain-example', 'agent-worker-1', 'node-alpha')
    print("  ✓ Delegated to agent-worker-1")

    tracker.add_delegation('chain-example', 'agent-worker-2', 'node-beta')
    print("  ✓ Delegated to agent-worker-2")

    # Complete delegations
    tracker.complete_delegation('chain-example', 0, duration_ms=150.5)
    tracker.complete_delegation('chain-example', 1, duration_ms=200.3)

    # Complete chain
    tracker.complete_chain('chain-example')

    print("\nChain completed!")

    # Visualize
    print("\n" + "=" * 60)
    print(visualize_chain(chain, format='ascii'))
    print("=" * 60)

    # Get stats
    stats = tracker.get_stats()
    print(f"\nTracker Stats:")
    print(f"  Total chains: {stats['total_chains']}")
    print(f"  Total delegations: {stats['total_delegations']}")


if __name__ == '__main__':
    main()
