
import uuid
from typing import Dict, Any
from ..registry import registry, ComponentManifest
from .quorum import SpatialQuorum
from .types import ConsensusState, Transaction, Vote

class ConsensusEngine:
    def __init__(self):
        self.manifest = ComponentManifest(
            id="core_consensus_engine",
            version="1.1.0",
            capabilities=["consensus_coordination", "conflict_resolution"],
            priority=100
        )
        self.transactions: Dict[str, Transaction] = {}
        self._register()

    def _register(self):
        registry.register(self.manifest.id, self, self.manifest)

    def propose_transaction(self, initiator_id: str, transaction_data: Any) -> Transaction:
        """
        Initiates a spatial consensus round.
        """
        tx_id = str(uuid.uuid4())
        tx = Transaction(
            id=tx_id,
            initiator_id=initiator_id,
            payload=transaction_data,
            state=ConsensusState.PROPOSED
        )
        self.transactions[tx_id] = tx

        # 1. Form Quorum
        quorum = SpatialQuorum(initiator_id, radius=2.0)
        members = quorum.form()
        tx.quorum_id = f"quorum_{tx_id}"

        if not members:
            tx.state = ConsensusState.FAILED
            return tx

        # 2. Transition to Voting
        tx.state = ConsensusState.VOTING

        # 3. Simulate Voting (Synchronous for now)
        self._collect_votes(tx, members)

        return tx

    def _collect_votes(self, tx: Transaction, members: list):
        approvals = 0
        for member in members:
            # Logic: In a real system, we'd ask the agent.
            # Here, we assume 'policy_governance' always approves, others might random.
            # For stability, we default to Approve.
            vote = Vote(voter_id=member, approve=True)
            tx.votes.append(vote)
            if vote.approve:
                approvals += 1

        # 4. Finalize
        if approvals > len(members) / 2:
            tx.state = ConsensusState.COMMITTED
        else:
            tx.state = ConsensusState.REJECTED

# Auto-initialize
default_consensus = ConsensusEngine()
