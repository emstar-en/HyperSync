"""
HyperSync CLI - Operations Assistant Integration
Wires ops commands into main CLI
"""

from hypersync.cli.ops import ops


def register_ops_commands(cli):
    """
    Register operations assistant commands with main CLI.

    Args:
        cli: Click CLI group to register commands with
    """
    cli.add_command(ops, name='ops')


__all__ = ['register_ops_commands']
