"""Replication CLI commands"""
import click
import json
import numpy as np
from hypersync.replication.replication_planner import ReplicationPlanner

@click.group()
def replication():
    """Replication commands"""
    pass

@replication.command()
@click.argument('service_id')
@click.option('--tier', type=int, required=True)
@click.option('--radius', type=float, required=True)
def plan(service_id, tier, radius):
    """Plan replication for a service"""
    planner = ReplicationPlanner()

    # Dummy position for CLI
    position = np.array([np.sqrt(1 + radius**2), radius, 0, 0])

    replica_set = planner.plan_replicas(service_id, position, tier, radius)

    click.echo(f"Replication plan for {service_id}:")
    click.echo(f"  RF: {replica_set.replication_factor}")
    click.echo(f"  Consistency: {replica_set.consistency_level}")
    click.echo(f"  Replicas: {len(replica_set.replica_ids)}")

@replication.command()
@click.argument('service_id')
def status(service_id):
    """Check replica status"""
    planner = ReplicationPlanner()
    replica_set = planner.get_replica_set(service_id)

    if replica_set:
        click.echo(f"Service: {service_id}")
        click.echo(f"  RF: {replica_set.replication_factor}")
        click.echo(f"  Tier: {replica_set.tier}")
        click.echo(f"  Replicas: {', '.join(replica_set.replica_ids)}")
    else:
        click.echo(f"Service {service_id} not found")

@replication.command()
@click.option('--hosts', required=True, help='Cassandra hosts (comma-separated)')
@click.option('--keyspace', default='hypersync')
def backend(hosts, keyspace):
    """Configure Cassandra backend"""
    from hypersync.replication.replication_planner import CassandraAdapter

    host_list = hosts.split(',')
    adapter = CassandraAdapter(host_list, keyspace)
    adapter.connect()

    click.echo(f"Connected to Cassandra: {hosts}")
    click.echo(f"Keyspace: {keyspace}")
