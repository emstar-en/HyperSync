"""
Governance Proposal CLI
"""
import click
from governance.api.proposals import submit_proposal, approve_proposal, list_proposals


@click.group()
def proposals():
    """Manage governance proposals."""
    pass


@proposals.command()
@click.argument('title')
@click.argument('description')
@click.option('--proposer', default='cli-user')
def submit(title, description, proposer):
    """Submit a new proposal."""
    result = submit_proposal(title, description, proposer)
    if result["success"]:
        click.echo(f"✓ Proposal submitted: {result['proposal']['id']}")
    else:
        click.echo(f"✗ Failed to submit proposal")


@proposals.command()
@click.argument('proposal_id')
@click.option('--approver', default='cli-user')
def approve(proposal_id, approver):
    """Approve a proposal."""
    result = approve_proposal(proposal_id, approver)
    if result["success"]:
        status = result['proposal']['status']
        click.echo(f"✓ Proposal approved. Status: {status}")
    else:
        click.echo(f"✗ Failed to approve proposal")


@proposals.command()
@click.option('--status', default=None)
def list(status):
    """List proposals."""
    proposals_list = list_proposals(status=status)
    for p in proposals_list:
        click.echo(f"{p['id']}: {p['title']} [{p['status']}]")
