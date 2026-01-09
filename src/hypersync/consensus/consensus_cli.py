"""
Consensus & Attestation CLI

Commands for managing consensus and attestation.
"""

import click
from rich.console import Console
from rich.table import Table
from .consensus_manager import ConsensusAttestationManager

console = Console()


# ============================================================================
# Consensus Commands
# ============================================================================

@click.group(name='consensus')
def consensus_cli():
    """Manage consensus mechanisms"""
    pass


@consensus_cli.command(name='list')
@click.option('--type', 'mechanism_type', help='Filter by mechanism type')
def list_mechanisms(mechanism_type):
    """List available consensus mechanisms"""
    manager = ConsensusAttestationManager()
    mechanisms = manager.list_consensus_mechanisms(mechanism_type=mechanism_type)

    if not mechanisms:
        console.print("[yellow]No consensus mechanisms found[/yellow]")
        return

    table = Table(title="Consensus Mechanisms")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="blue")
    table.add_column("Min Tier", style="magenta")
    table.add_column("Status", style="yellow")

    for mech in mechanisms:
        min_tier = mech.tier_requirements.get("min_tier", "N/A") if mech.tier_requirements else "N/A"
        table.add_row(
            mech.mechanism_id,
            mech.name,
            mech.mechanism_type,
            min_tier,
            mech.status
        )

    console.print(table)


@consensus_cli.command(name='info')
@click.argument('mechanism_id')
def mechanism_info(mechanism_id):
    """Show consensus mechanism details"""
    manager = ConsensusAttestationManager()
    mech = manager.get_consensus_mechanism(mechanism_id)

    if not mech:
        console.print(f"[red]Mechanism not found: {mechanism_id}[/red]")
        return

    console.print(f"
[bold cyan]{mech.name}[/bold cyan]")
    console.print(f"ID: {mech.mechanism_id}")
    console.print(f"Type: {mech.mechanism_type}")
    console.print(f"Status: {mech.status}")

    if mech.description:
        console.print(f"
{mech.description}")

    if mech.parameters:
        console.print("
[bold]Parameters:[/bold]")
        for key, value in mech.parameters.items():
            console.print(f"  {key}: {value}")

    if mech.tier_requirements:
        console.print("
[bold]Tier Requirements:[/bold]")
        for key, value in mech.tier_requirements.items():
            console.print(f"  {key}: {value}")

    if mech.performance:
        console.print("
[bold]Performance:[/bold]")
        for key, value in mech.performance.items():
            console.print(f"  {key}: {value}")


@consensus_cli.command(name='apply')
@click.option('--target-type', required=True, type=click.Choice(['stack', 'assembly', 'deployment', 'node_group']))
@click.option('--target-id', required=True, help='Target ID')
@click.option('--mechanism', 'mechanism_id', required=True, help='Consensus mechanism ID')
@click.option('--quorum', type=int, help='Quorum size')
@click.option('--threshold', type=float, help='Threshold (0-1)')
@click.option('--nodes', multiple=True, help='Node IDs participating in consensus')
def apply_consensus(target_type, target_id, mechanism_id, quorum, threshold, nodes):
    """Apply consensus mechanism to a target"""
    manager = ConsensusAttestationManager()

    # Build parameters
    parameters = {}
    if quorum:
        parameters['quorum_size'] = quorum
    if threshold:
        parameters['threshold'] = threshold

    try:
        config = manager.apply_consensus(
            target_type=target_type,
            target_id=target_id,
            mechanism_id=mechanism_id,
            parameters=parameters if parameters else None,
            nodes=list(nodes) if nodes else None
        )

        console.print(f"[green]✓[/green] Applied consensus to {target_type}:{target_id}")
        console.print(f"Configuration ID: {config.config_id}")
        console.print(f"Mechanism: {mechanism_id}")

        if config.parameters:
            console.print("
Parameters:")
            for key, value in config.parameters.items():
                console.print(f"  {key}: {value}")

        if config.nodes:
            console.print(f"
Nodes: {len(config.nodes)}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@consensus_cli.command(name='show')
@click.option('--target-type', required=True, type=click.Choice(['stack', 'assembly', 'deployment', 'node_group']))
@click.option('--target-id', required=True, help='Target ID')
def show_consensus(target_type, target_id):
    """Show consensus configuration for a target"""
    manager = ConsensusAttestationManager()
    config = manager.get_consensus_config(target_type, target_id)

    if not config:
        console.print(f"[yellow]No consensus configured for {target_type}:{target_id}[/yellow]")
        return

    console.print(f"
[bold]Consensus Configuration[/bold]")
    console.print(f"Config ID: {config.config_id}")
    console.print(f"Mechanism: {config.mechanism_id}")
    console.print(f"Status: {config.status}")

    if config.parameters:
        console.print("
[bold]Parameters:[/bold]")
        for key, value in config.parameters.items():
            console.print(f"  {key}: {value}")

    if config.nodes:
        console.print(f"
[bold]Nodes:[/bold] {len(config.nodes)}")
        for node in config.nodes:
            console.print(f"  - {node}")

    if config.metrics:
        console.print("
[bold]Metrics:[/bold]")
        for key, value in config.metrics.items():
            console.print(f"  {key}: {value}")


@consensus_cli.command(name='configs')
@click.option('--target-type', type=click.Choice(['stack', 'assembly', 'deployment', 'node_group']))
@click.option('--mechanism', 'mechanism_id', help='Filter by mechanism')
def list_configs(target_type, mechanism_id):
    """List consensus configurations"""
    manager = ConsensusAttestationManager()
    configs = manager.list_consensus_configs(
        target_type=target_type,
        mechanism_id=mechanism_id
    )

    if not configs:
        console.print("[yellow]No consensus configurations found[/yellow]")
        return

    table = Table(title="Consensus Configurations")
    table.add_column("Config ID", style="cyan")
    table.add_column("Target", style="green")
    table.add_column("Mechanism", style="blue")
    table.add_column("Nodes", style="magenta")
    table.add_column("Status", style="yellow")

    for config in configs:
        target = f"{config.target_type}:{config.target_id[:12]}..."
        nodes_count = str(len(config.nodes)) if config.nodes else "0"
        table.add_row(
            config.config_id[:20] + "...",
            target,
            config.mechanism_id,
            nodes_count,
            config.status
        )

    console.print(table)


# ============================================================================
# Attestation Commands
# ============================================================================

@click.group(name='attestation')
def attestation_cli():
    """Manage attestation protocols"""
    pass


@attestation_cli.command(name='list')
@click.option('--type', 'protocol_type', help='Filter by protocol type')
def list_protocols(protocol_type):
    """List available attestation protocols"""
    manager = ConsensusAttestationManager()
    protocols = manager.list_attestation_protocols(protocol_type=protocol_type)

    if not protocols:
        console.print("[yellow]No attestation protocols found[/yellow]")
        return

    table = Table(title="Attestation Protocols")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="blue")
    table.add_column("Verification", style="magenta")
    table.add_column("Status", style="yellow")

    for proto in protocols:
        verif_level = proto.verification.get("verification_level", "N/A") if proto.verification else "N/A"
        table.add_row(
            proto.protocol_id,
            proto.name,
            proto.protocol_type,
            verif_level,
            proto.status
        )

    console.print(table)


@attestation_cli.command(name='info')
@click.argument('protocol_id')
def protocol_info(protocol_id):
    """Show attestation protocol details"""
    manager = ConsensusAttestationManager()
    proto = manager.get_attestation_protocol(protocol_id)

    if not proto:
        console.print(f"[red]Protocol not found: {protocol_id}[/red]")
        return

    console.print(f"
[bold cyan]{proto.name}[/bold cyan]")
    console.print(f"ID: {proto.protocol_id}")
    console.print(f"Type: {proto.protocol_type}")
    console.print(f"Status: {proto.status}")

    if proto.description:
        console.print(f"
{proto.description}")

    if proto.verification:
        console.print("
[bold]Verification:[/bold]")
        for key, value in proto.verification.items():
            console.print(f"  {key}: {value}")

    if proto.tier_requirements:
        console.print("
[bold]Tier Requirements:[/bold]")
        for key, value in proto.tier_requirements.items():
            console.print(f"  {key}: {value}")

    if proto.cryptographic:
        console.print("
[bold]Cryptographic:[/bold]")
        for key, value in proto.cryptographic.items():
            console.print(f"  {key}: {value}")


@attestation_cli.command(name='apply')
@click.option('--target-type', required=True, type=click.Choice(['stack', 'assembly', 'deployment', 'node']))
@click.option('--target-id', required=True, help='Target ID')
@click.option('--protocol', 'protocol_id', required=True, help='Attestation protocol ID')
@click.option('--level', 'verification_level', type=click.Choice(['low', 'medium', 'high', 'cryptographic']))
@click.option('--interval', type=int, help='Attestation interval in seconds')
def apply_attestation(target_type, target_id, protocol_id, verification_level, interval):
    """Apply attestation protocol to a target"""
    manager = ConsensusAttestationManager()

    # Build frequency config
    attestation_frequency = None
    if interval:
        attestation_frequency = {"interval_seconds": interval}

    try:
        config = manager.apply_attestation(
            target_type=target_type,
            target_id=target_id,
            protocol_id=protocol_id,
            verification_level=verification_level,
            attestation_frequency=attestation_frequency
        )

        console.print(f"[green]✓[/green] Applied attestation to {target_type}:{target_id}")
        console.print(f"Configuration ID: {config.config_id}")
        console.print(f"Protocol: {protocol_id}")
        console.print(f"Verification Level: {config.verification_level}")

        if config.attestation_frequency:
            interval_sec = config.attestation_frequency.get("interval_seconds", "N/A")
            console.print(f"Interval: {interval_sec} seconds")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@attestation_cli.command(name='show')
@click.option('--target-type', required=True, type=click.Choice(['stack', 'assembly', 'deployment', 'node']))
@click.option('--target-id', required=True, help='Target ID')
def show_attestation(target_type, target_id):
    """Show attestation configuration for a target"""
    manager = ConsensusAttestationManager()
    config = manager.get_attestation_config(target_type, target_id)

    if not config:
        console.print(f"[yellow]No attestation configured for {target_type}:{target_id}[/yellow]")
        return

    console.print(f"
[bold]Attestation Configuration[/bold]")
    console.print(f"Config ID: {config.config_id}")
    console.print(f"Protocol: {config.protocol_id}")
    console.print(f"Verification Level: {config.verification_level}")
    console.print(f"Status: {config.status}")

    if config.attestation_frequency:
        console.print("
[bold]Frequency:[/bold]")
        for key, value in config.attestation_frequency.items():
            console.print(f"  {key}: {value}")

    if config.receipts:
        console.print(f"
[bold]Receipts:[/bold] {len(config.receipts)}")
        for i, receipt in enumerate(config.receipts[-5:], 1):  # Show last 5
            console.print(f"  {i}. {receipt.get('receipt_id', 'N/A')} - {receipt.get('timestamp', 'N/A')}")


@attestation_cli.command(name='configs')
@click.option('--target-type', type=click.Choice(['stack', 'assembly', 'deployment', 'node']))
@click.option('--protocol', 'protocol_id', help='Filter by protocol')
def list_attest_configs(target_type, protocol_id):
    """List attestation configurations"""
    manager = ConsensusAttestationManager()
    configs = manager.list_attestation_configs(
        target_type=target_type,
        protocol_id=protocol_id
    )

    if not configs:
        console.print("[yellow]No attestation configurations found[/yellow]")
        return

    table = Table(title="Attestation Configurations")
    table.add_column("Config ID", style="cyan")
    table.add_column("Target", style="green")
    table.add_column("Protocol", style="blue")
    table.add_column("Level", style="magenta")
    table.add_column("Receipts", style="yellow")

    for config in configs:
        target = f"{config.target_type}:{config.target_id[:12]}..."
        receipts_count = str(len(config.receipts)) if config.receipts else "0"
        table.add_row(
            config.config_id[:20] + "...",
            target,
            config.protocol_id,
            config.verification_level or "N/A",
            receipts_count
        )

    console.print(table)


def register_cli(cli_group):
    """Register consensus and attestation commands"""
    cli_group.add_command(consensus_cli)
    cli_group.add_command(attestation_cli)
