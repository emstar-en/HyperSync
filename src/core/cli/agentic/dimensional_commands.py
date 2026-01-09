"""
HyperSync CLI Dimensional Commands

Provides command-line interface for inspecting and tuning dimensional configurations.
"""

import click
import json
import sys
from pathlib import Path
from typing import Optional
from tabulate import tabulate

# Import from dimensional module
try:
    from hypersync.dimensional.local_profile import LocalDimensionalProfile, DimensionalPreset
except ImportError:
    # Fallback for standalone execution
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from hypersync.dimensional.local_profile import LocalDimensionalProfile, DimensionalPreset


DEFAULT_CONFIG_PATH = Path.home() / ".hypersync" / "dimensional" / "local.json"


@click.group(name="dimensional")
def dimensional_cli():
    """Manage dimensional configuration for HyperSync stacks."""
    pass


@dimensional_cli.command(name="init")
@click.option("--stack-id", default="core", help="Stack identifier")
@click.option("--preset", 
              type=click.Choice(["minimal", "standard", "extended", "research"]),
              default="standard",
              help="Dimensional preset")
@click.option("--config-path", 
              type=click.Path(),
              default=str(DEFAULT_CONFIG_PATH),
              help="Configuration file path")
def init_config(stack_id: str, preset: str, config_path: str):
    """Initialize dimensional configuration for a stack."""
    try:
        profile = LocalDimensionalProfile(stack_id=stack_id, preset=preset)
        profile.persist(config_path)

        click.echo(f"✅ Initialized dimensional profile for stack '{stack_id}'")
        click.echo(f"   Preset: {preset}")
        click.echo(f"   Dimensions: {profile.base_dimensions} (base) / {profile.max_dimensions} (max)")
        click.echo(f"   Curvature: {profile.curvature:.3f}")
        click.echo(f"   Config: {config_path}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@dimensional_cli.command(name="show")
@click.option("--config-path",
              type=click.Path(exists=True),
              default=str(DEFAULT_CONFIG_PATH),
              help="Configuration file path")
@click.option("--format",
              type=click.Choice(["table", "json"]),
              default="table",
              help="Output format")
def show_config(config_path: str, format: str):
    """Display current dimensional configuration."""
    try:
        profile = LocalDimensionalProfile.load_from_file(config_path)

        if format == "json":
            data = {
                "stack_id": profile.stack_id,
                "preset": profile.preset_name,
                "base_dimensions": profile.base_dimensions,
                "max_dimensions": profile.max_dimensions,
                "curvature": profile.curvature,
                "stability_score": profile.curvature_guard.get_stability_score(),
                "agent_bindings": len(profile.agent_bindings)
            }
            click.echo(json.dumps(data, indent=2))
        else:
            # Table format
            click.echo(f"\n{'=' * 60}")
            click.echo(f"Dimensional Profile: {profile.stack_id}")
            click.echo(f"{'=' * 60}")

            config_data = [
                ["Preset", profile.preset_name],
                ["Base Dimensions", profile.base_dimensions],
                ["Max Dimensions", profile.max_dimensions],
                ["Curvature", f"{profile.curvature:.3f}"],
                ["Stability Score", f"{profile.curvature_guard.get_stability_score():.3f}"],
                ["Agent Bindings", len(profile.agent_bindings)]
            ]

            click.echo(tabulate(config_data, tablefmt="simple"))

            if profile.agent_bindings:
                click.echo(f"\n{'Agent Bindings':}")
                click.echo("-" * 60)
                agent_data = [
                    [
                        binding["agent_id"],
                        binding["dimensions"],
                        binding.get("curvature_override", "default")
                    ]
                    for binding in profile.agent_bindings.values()
                ]
                click.echo(tabulate(
                    agent_data,
                    headers=["Agent ID", "Dimensions", "Curvature"],
                    tablefmt="simple"
                ))

            click.echo(f"{'=' * 60}\n")

    except FileNotFoundError:
        click.echo(f"❌ Configuration not found: {config_path}", err=True)
        click.echo("   Run 'hypersync dimensional init' to create a configuration.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@dimensional_cli.command(name="tune")
@click.option("--config-path",
              type=click.Path(exists=True),
              default=str(DEFAULT_CONFIG_PATH),
              help="Configuration file path")
@click.option("--curvature",
              type=float,
              help="Set curvature value (range: -1.0 to 0.0)")
@click.option("--max-dims",
              type=int,
              help="Set maximum dimensions (range: 2 to 16)")
def tune_config(config_path: str, curvature: Optional[float], max_dims: Optional[int]):
    """Tune dimensional configuration parameters."""
    try:
        profile = LocalDimensionalProfile.load_from_file(config_path)

        changes = []
        if curvature is not None:
            old_curvature = profile.curvature
            profile.apply(curvature=curvature)
            changes.append(f"Curvature: {old_curvature:.3f} → {curvature:.3f}")

        if max_dims is not None:
            old_max = profile.max_dimensions
            profile.apply(max_dims=max_dims)
            changes.append(f"Max Dimensions: {old_max} → {max_dims}")

        if not changes:
            click.echo("⚠️  No changes specified. Use --curvature or --max-dims.", err=True)
            sys.exit(1)

        profile.persist(config_path)

        click.echo("✅ Configuration updated:")
        for change in changes:
            click.echo(f"   {change}")

        stability = profile.curvature_guard.get_stability_score()
        click.echo(f"   Stability Score: {stability:.3f}")

    except ValueError as e:
        click.echo(f"❌ Validation error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@dimensional_cli.command(name="bind-agent")
@click.argument("agent-id")
@click.option("--config-path",
              type=click.Path(exists=True),
              default=str(DEFAULT_CONFIG_PATH),
              help="Configuration file path")
@click.option("--dimensions",
              type=int,
              required=True,
              help="Number of dimensions for this agent")
@click.option("--curvature",
              type=float,
              help="Curvature override for this agent")
def bind_agent(agent_id: str, config_path: str, dimensions: int, curvature: Optional[float]):
    """Bind agent-specific dimensional configuration."""
    try:
        profile = LocalDimensionalProfile.load_from_file(config_path)
        profile.bind_agent(agent_id, dimensions, curvature)
        profile.persist(config_path)

        click.echo(f"✅ Bound agent '{agent_id}':")
        click.echo(f"   Dimensions: {dimensions}")
        if curvature is not None:
            click.echo(f"   Curvature: {curvature:.3f}")
        else:
            click.echo(f"   Curvature: {profile.curvature:.3f} (default)")

    except ValueError as e:
        click.echo(f"❌ Validation error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@dimensional_cli.command(name="stability")
@click.option("--config-path",
              type=click.Path(exists=True),
              default=str(DEFAULT_CONFIG_PATH),
              help="Configuration file path")
def stability_report(config_path: str):
    """Generate stability report for current configuration."""
    try:
        profile = LocalDimensionalProfile.load_from_file(config_path)
        report = profile.get_stability_report()

        click.echo(f"\n{'=' * 60}")
        click.echo(f"Stability Report: {report['stack_id']}")
        click.echo(f"{'=' * 60}")

        score = report['stability_score']
        status = "🟢 STABLE" if score >= 0.9 else "🟡 MODERATE" if score >= 0.7 else "🔴 UNSTABLE"

        report_data = [
            ["Status", status],
            ["Stability Score", f"{score:.3f}"],
            ["Current Curvature", f"{report['current_curvature']:.3f}"],
            ["Base Dimensions", report['dimensions']['base']],
            ["Max Dimensions", report['dimensions']['max']],
            ["Agent Count", report['agent_count']],
            ["History Size", report['history_size']]
        ]

        click.echo(tabulate(report_data, tablefmt="simple"))
        click.echo(f"{'=' * 60}\n")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@dimensional_cli.command(name="presets")
def list_presets():
    """List available dimensional presets."""
    click.echo(f"\n{'=' * 80}")
    click.echo("Available Dimensional Presets")
    click.echo(f"{'=' * 80}\n")

    for name, preset in LocalDimensionalProfile.PRESETS.items():
        click.echo(f"📦 {preset.name.upper()}")
        click.echo(f"   Description: {preset.description}")
        click.echo(f"   Dimensions: {preset.base_dimensions} (base) / {preset.max_dimensions} (max)")
        click.echo(f"   Curvature: {preset.default_curvature:.3f}")
        click.echo(f"   Use Cases: {', '.join(preset.use_cases)}")
        click.echo()

    click.echo(f"{'=' * 80}\n")


if __name__ == "__main__":
    dimensional_cli()
