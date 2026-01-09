"""
HyperSync Initialization - Bootstrap Integration
Wires bootstrap into initialization sequence
"""

from hypersync.init.bootstrap import bootstrap_hypersync


async def run_bootstrap_sequence():
    """
    Run complete bootstrap sequence including preset knowledge loading.

    This is called during:
    - Initial installation
    - System initialization
    - After major upgrades
    """
    result = await bootstrap_hypersync()
    return result


__all__ = ['run_bootstrap_sequence']
