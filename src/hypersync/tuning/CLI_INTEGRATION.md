# CLI Integration

# Add to hypersync/cli.py

from hypersync.tuning.stable_cli import register_cli as register_tuning_cli

# In main CLI setup:
register_tuning_cli(cli)
