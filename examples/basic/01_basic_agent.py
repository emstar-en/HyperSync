#!/usr/bin/env python3
"""
Basic Agent Creation Example

Demonstrates creating and activating a simple agent.
"""

import asyncio
from hypersync.agents.profile_registry import AgentProfileRegistry
from hypersync.agents.composition_engine import CompositionEngine
from hypersync.agents.tasks.lifecycle import LifecycleTaskManager


async def main():
    """Create and activate a basic agent."""

    # Initialize components
    registry = AgentProfileRegistry()
    engine = CompositionEngine()
    lifecycle = LifecycleTaskManager(registry, engine)

    # Define agent profile
    profile = {
        'name': 'my-first-agent',
        'version': '1.0.0',
        'description': 'My first HyperSync agent',
        'nodes': ['node-alpha'],
        'routing_strategy': 'best_fit',
        'capabilities': {
            'required': ['text-generation']
        }
    }

    # Create and activate
    result = await lifecycle.create_agent(profile, auto_activate=True)

    if result['success']:
        print(f"✅ Agent created: {result['agent_id']}")
        print(f"   Activated: {result['activated']}")
    else:
        print(f"❌ Failed: {result.get('error')}")


if __name__ == '__main__':
    asyncio.run(main())
