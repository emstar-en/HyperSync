"""
HyperSync Security CLI
Commands for managing policies and scanning threats
"""

import click
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import Optional

from hypersync.security.policy_manager import (
    SecurityPolicyManager,
    ThreatLevel,
    LDTrainingRecord
)

console = Console()


@click.group(name="security")
def security_cli():
    """Security policy and threat management commands"""
    pass


@security_cli.command(name="policy-create")
@click.option("--policy-id", required=True, help="Unique policy identifier")
@click.option("--owner-type", required=True, type=click.Choice(["user", "model", "system"]))
@click.option("--owner-id", required=True, help="Owner identifier")
@click.option("--max-nld", default=6, type=int, help="Maximum allowed nLD score")
@click.option("--priority", default=50, type=int, help="Policy priority (0-100)")
@click.option("--rules", help="JSON file with policy rules")
def policy_create(policy_id, owner_type, owner_id, max_nld, priority, rules):
    """Create a new security policy"""
    manager = SecurityPolicyManager()

    # Load rules from file or use defaults
    if rules:
        with open(rules, 'r') as f:
            rules_data = json.load(f)
    else:
        rules_data = [
            {
                "rule_id": "default_allow",
                "action": "*",
                "effect": "allow"
            }
        ]

    policy = manager.create_policy(
        policy_id=policy_id,
        owner_type=owner_type,
        owner_id=owner_id,
        rules=rules_data,
        nld_max_score=max_nld,
        priority=priority
    )

    console.print(Panel(
        f"[green]✓[/green] Policy created: {policy_id}\n"
        f"Owner: {owner_type}/{owner_id}\n"
        f"Max nLD: {max_nld}\n"
        f"Priority: {priority}",
        title="Policy Created",
        border_style="green"
    ))


@security_cli.command(name="policy-get")
@click.argument("policy_id")
@click.option("--format", type=click.Choice(["json", "table"]), default="table")
def policy_get(policy_id, format):
    """Get policy details"""
    manager = SecurityPolicyManager()
    policy = manager.get_policy(policy_id)

    if not policy:
        console.print(f"[red]✗[/red] Policy not found: {policy_id}")
        return

    if format == "json":
        console.print_json(data=policy.to_dict())
    else:
        # Display as table
        table = Table(title=f"Policy: {policy_id}", box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Policy ID", policy.policy_id)
        table.add_row("Owner Type", policy.owner["type"])
        table.add_row("Owner ID", policy.owner["id"])
        table.add_row("Priority", str(policy.owner.get("priority", 0)))
        table.add_row("nLD Protection", "Enabled" if policy.nld_protection["enabled"] else "Disabled")
        table.add_row("Max nLD Score", str(policy.nld_protection["max_nld_score"]))
        table.add_row("Rules Count", str(len(policy.rules)))

        console.print(table)

        # Display rules
        if policy.rules:
            rules_table = Table(title="Policy Rules", box=box.SIMPLE)
            rules_table.add_column("Rule ID", style="cyan")
            rules_table.add_column("Action", style="yellow")
            rules_table.add_column("Effect", style="green")

            for rule in policy.rules:
                effect_color = "green" if rule["effect"] == "allow" else "red"
                rules_table.add_row(
                    rule["rule_id"],
                    rule["action"],
                    f"[{effect_color}]{rule['effect']}[/{effect_color}]"
                )

            console.print(rules_table)


@security_cli.command(name="policy-list")
@click.option("--owner-id", help="Filter by owner ID")
@click.option("--format", type=click.Choice(["json", "table"]), default="table")
def policy_list(owner_id, format):
    """List all policies"""
    manager = SecurityPolicyManager()
    policies = manager.list_policies(owner_id=owner_id)

    if not policies:
        console.print("[yellow]No policies found[/yellow]")
        return

    if format == "json":
        console.print_json(data=[p.to_dict() for p in policies])
    else:
        table = Table(title="Security Policies", box=box.ROUNDED)
        table.add_column("Policy ID", style="cyan")
        table.add_column("Owner", style="white")
        table.add_column("Priority", style="yellow")
        table.add_column("Max nLD", style="magenta")
        table.add_column("Rules", style="green")

        for policy in policies:
            table.add_row(
                policy.policy_id,
                f"{policy.owner['type']}/{policy.owner['id']}",
                str(policy.owner.get("priority", 0)),
                str(policy.nld_protection["max_nld_score"]),
                str(len(policy.rules))
            )

        console.print(table)


@security_cli.command(name="policy-update")
@click.argument("policy_id")
@click.option("--max-nld", type=int, help="Update max nLD score")
@click.option("--priority", type=int, help="Update priority")
@click.option("--enable-nld/--disable-nld", default=None, help="Enable/disable nLD protection")
def policy_update(policy_id, max_nld, priority, enable_nld):
    """Update an existing policy"""
    manager = SecurityPolicyManager()

    updates = {}
    if max_nld is not None:
        updates["nld_protection"] = {"max_nld_score": max_nld}
    if priority is not None:
        updates["owner"] = {"priority": priority}
    if enable_nld is not None:
        updates["nld_protection"] = {"enabled": enable_nld}

    policy = manager.update_policy(policy_id, updates)

    if policy:
        console.print(Panel(
            f"[green]✓[/green] Policy updated: {policy_id}",
            border_style="green"
        ))
    else:
        console.print(f"[red]✗[/red] Policy not found: {policy_id}")


@security_cli.command(name="policy-delete")
@click.argument("policy_id")
@click.confirmation_option(prompt="Are you sure you want to delete this policy?")
def policy_delete(policy_id):
    """Delete a policy"""
    manager = SecurityPolicyManager()

    if manager.delete_policy(policy_id):
        console.print(Panel(
            f"[green]✓[/green] Policy deleted: {policy_id}",
            border_style="green"
        ))
    else:
        console.print(f"[red]✗[/red] Policy not found: {policy_id}")


@security_cli.command(name="threat-scan")
@click.option("--agent-id", required=True, help="Agent/model identifier")
@click.option("--ld-history", required=True, help="JSON file with LD training history")
@click.option("--signals", help="JSON file with detection signals")
@click.option("--format", type=click.Choice(["json", "table"]), default="table")
def threat_scan(agent_id, ld_history, signals, format):
    """Scan an agent for nLD threats"""
    manager = SecurityPolicyManager()

    # Load LD training history
    with open(ld_history, 'r') as f:
        ld_data = json.load(f)

    # Load detection signals if provided
    signals_data = None
    if signals:
        with open(signals, 'r') as f:
            signals_data = json.load(f)

    # Scan for threats
    profile = manager.scan_threat(agent_id, ld_data, signals_data)

    if format == "json":
        console.print_json(data=profile.to_dict())
    else:
        # Determine color based on threat level
        level_colors = {
            ThreatLevel.SAFE: "green",
            ThreatLevel.LOW: "blue",
            ThreatLevel.MEDIUM: "yellow",
            ThreatLevel.HIGH: "orange",
            ThreatLevel.CRITICAL: "red"
        }
        color = level_colors.get(profile.threat_level, "white")

        # Display threat profile
        table = Table(title=f"nLD Threat Profile: {agent_id}", box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Agent ID", profile.agent_id)
        table.add_row("nLD Score", str(profile.nld_score))
        table.add_row("Threat Level", f"[{color}]{profile.threat_level.value.upper()}[/{color}]")
        table.add_row("LDs Trained", str(len(profile.ld_training_history)))
        table.add_row("Cross-Boundary", profile.risk_assessment["cross_boundary_capability"])
        table.add_row("Instability Risk", profile.risk_assessment["instability_risk"])
        table.add_row("Recommended Action", f"[bold]{profile.risk_assessment['recommended_action']}[/bold]")

        console.print(table)

        # Display LD training history
        if profile.ld_training_history:
            ld_table = Table(title="LD Training History", box=box.SIMPLE)
            ld_table.add_column("LD ID", style="cyan")
            ld_table.add_column("Geometry", style="yellow")
            ld_table.add_column("Epochs", style="green")
            ld_table.add_column("Curvature", style="magenta")

            for ld in profile.ld_training_history:
                ld_table.add_row(
                    ld.ld_id,
                    ld.geometry_type,
                    str(ld.training_epochs),
                    f"{ld.curvature:.4f}"
                )

            console.print(ld_table)

        # Display detection signals
        if profile.detection_signals:
            signals_table = Table(title="Detection Signals", box=box.SIMPLE)
            signals_table.add_column("Signal", style="cyan")
            signals_table.add_column("Value", style="white")

            for signal, value in profile.detection_signals.items():
                signals_table.add_row(signal, str(value))

            console.print(signals_table)


@security_cli.command(name="check-access")
@click.option("--agent-id", required=True, help="Agent identifier")
@click.option("--action", required=True, help="Action to check")
@click.option("--policy-id", required=True, help="Policy to check against")
@click.option("--threat-profile", help="JSON file with threat profile")
def check_access(agent_id, action, policy_id, threat_profile):
    """Check if an agent can perform an action"""
    manager = SecurityPolicyManager()

    # Load threat profile if provided
    profile = None
    if threat_profile:
        with open(threat_profile, 'r') as f:
            profile_data = json.load(f)
            # Reconstruct profile (simplified)
            ld_records = [LDTrainingRecord(**ld) for ld in profile_data["ld_training_history"]]
            profile = manager.scan_threat(agent_id, [ld.__dict__ for ld in ld_records])

    # Check access
    allowed, reason = manager.check_access(agent_id, action, policy_id, profile)

    if allowed:
        console.print(Panel(
            f"[green]✓ ACCESS GRANTED[/green]\n"
            f"Agent: {agent_id}\n"
            f"Action: {action}\n"
            f"Reason: {reason}",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"[red]✗ ACCESS DENIED[/red]\n"
            f"Agent: {agent_id}\n"
            f"Action: {action}\n"
            f"Reason: {reason}",
            border_style="red"
        ))


@security_cli.command(name="hierarchy-set")
@click.option("--node-id", required=True, help="Node identifier")
@click.option("--parent-id", help="Parent node identifier")
@click.option("--priority", default=50, type=int, help="Node priority (0-100)")
def hierarchy_set(node_id, parent_id, priority):
    """Set node hierarchy and priority"""
    manager = SecurityPolicyManager()
    manager.set_node_hierarchy(node_id, parent_id, priority)

    console.print(Panel(
        f"[green]✓[/green] Hierarchy updated\n"
        f"Node: {node_id}\n"
        f"Parent: {parent_id or 'None'}\n"
        f"Priority: {priority}",
        border_style="green"
    ))


@security_cli.command(name="init")
def init_security():
    """Initialize security system with default policy"""
    manager = SecurityPolicyManager()

    from hypersync.security.policy_manager import create_default_policy
    default_policy_data = create_default_policy()

    # Check if default policy exists
    if manager.get_policy("system_default"):
        console.print("[yellow]Default policy already exists[/yellow]")
        return

    # Create default policy
    manager.create_policy(
        policy_id=default_policy_data["policy_id"],
        owner_type=default_policy_data["owner"]["type"],
        owner_id=default_policy_data["owner"]["id"],
        rules=default_policy_data["rules"],
        nld_max_score=default_policy_data["nld_protection"]["max_nld_score"],
        priority=default_policy_data["owner"]["priority"]
    )

    console.print(Panel(
        "[green]✓[/green] Security system initialized\n"
        "Default policy created: system_default\n"
        "nLD protection: ENABLED (max score: 6)\n"
        "Authentication: DISABLED",
        title="Security Initialized",
        border_style="green"
    ))


if __name__ == "__main__":
    security_cli()
