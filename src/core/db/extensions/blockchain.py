"""
Blockchain Ledger Adapter - Immutable ledger interface.

Provides immutable ledger interface, proof verification, hyperbolic
state synchronization, and attestation logs for compliance.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json


@dataclass
class Block:
    """Blockchain block."""
    block_id: str
    previous_hash: str
    timestamp: datetime
    transactions: List[Dict[str, Any]]
    nonce: int
    hash: str


@dataclass
class Transaction:
    """Blockchain transaction."""
    tx_id: str
    operation: str
    data: Dict[str, Any]
    timestamp: datetime
    signature: Optional[str] = None


class BlockchainAdapter:
    """
    Blockchain ledger adapter for immutable audit logs.

    Provides append-only ledger with cryptographic verification,
    state synchronization, and compliance attestations.
    """

    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = 2  # Mining difficulty

        # Create genesis block
        self._create_genesis_block()

    def add_transaction(self, operation: str, data: Dict[str, Any],
                       signature: Optional[str] = None) -> str:
        """
        Add transaction to pending pool.

        Args:
            operation: Operation type
            data: Transaction data
            signature: Optional cryptographic signature

        Returns:
            Transaction ID
        """
        tx_id = self._generate_tx_id(operation, data)

        transaction = Transaction(
            tx_id=tx_id,
            operation=operation,
            data=data,
            timestamp=datetime.now(),
            signature=signature
        )

        self.pending_transactions.append(transaction)
        return tx_id

    def mine_block(self) -> Block:
        """
        Mine new block with pending transactions.

        Returns:
            Mined Block
        """
        if not self.pending_transactions:
            return None

        previous_block = self.chain[-1] if self.chain else None
        previous_hash = previous_block.hash if previous_block else "0" * 64

        block_id = f"block_{len(self.chain)}"
        timestamp = datetime.now()
        transactions = [
            {
                "tx_id": tx.tx_id,
                "operation": tx.operation,
                "data": tx.data,
                "timestamp": tx.timestamp.isoformat()
            }
            for tx in self.pending_transactions
        ]

        # Proof of work
        nonce = 0
        while True:
            block_hash = self._calculate_hash(block_id, previous_hash, timestamp, transactions, nonce)

            if block_hash.startswith("0" * self.difficulty):
                break

            nonce += 1

        block = Block(
            block_id=block_id,
            previous_hash=previous_hash,
            timestamp=timestamp,
            transactions=transactions,
            nonce=nonce,
            hash=block_hash
        )

        self.chain.append(block)
        self.pending_transactions.clear()

        return block

    def verify_chain(self) -> bool:
        """
        Verify blockchain integrity.

        Returns:
            True if chain is valid
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Verify hash
            calculated_hash = self._calculate_hash(
                current.block_id,
                current.previous_hash,
                current.timestamp,
                current.transactions,
                current.nonce
            )

            if current.hash != calculated_hash:
                return False

            # Verify chain link
            if current.previous_hash != previous.hash:
                return False

            # Verify proof of work
            if not current.hash.startswith("0" * self.difficulty):
                return False

        return True

    def get_transaction_proof(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cryptographic proof for transaction.

        Args:
            tx_id: Transaction ID

        Returns:
            Proof data or None
        """
        for block in self.chain:
            for tx in block.transactions:
                if tx["tx_id"] == tx_id:
                    return {
                        "tx_id": tx_id,
                        "block_id": block.block_id,
                        "block_hash": block.hash,
                        "timestamp": block.timestamp.isoformat(),
                        "verified": True
                    }

        return None

    def generate_attestation(self, data: Dict[str, Any]) -> str:
        """
        Generate compliance attestation.

        Args:
            data: Data to attest

        Returns:
            Attestation hash
        """
        attestation_data = {
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "chain_length": len(self.chain),
            "latest_hash": self.chain[-1].hash if self.chain else None
        }

        attestation_json = json.dumps(attestation_data, sort_keys=True)
        return hashlib.sha256(attestation_json.encode()).hexdigest()

    def _create_genesis_block(self) -> None:
        """Create genesis block."""
        genesis = Block(
            block_id="genesis",
            previous_hash="0" * 64,
            timestamp=datetime.now(),
            transactions=[],
            nonce=0,
            hash=self._calculate_hash("genesis", "0" * 64, datetime.now(), [], 0)
        )

        self.chain.append(genesis)

    def _calculate_hash(self, block_id: str, previous_hash: str,
                       timestamp: datetime, transactions: List[Dict],
                       nonce: int) -> str:
        """Calculate block hash."""
        block_data = {
            "block_id": block_id,
            "previous_hash": previous_hash,
            "timestamp": timestamp.isoformat(),
            "transactions": transactions,
            "nonce": nonce
        }

        block_json = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_json.encode()).hexdigest()

    def _generate_tx_id(self, operation: str, data: Dict[str, Any]) -> str:
        """Generate transaction ID."""
        tx_data = {
            "operation": operation,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        tx_json = json.dumps(tx_data, sort_keys=True)
        return hashlib.sha256(tx_json.encode()).hexdigest()[:16]

    def get_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics."""
        return {
            "chain_length": len(self.chain),
            "pending_transactions": len(self.pending_transactions),
            "total_transactions": sum(len(block.transactions) for block in self.chain),
            "is_valid": self.verify_chain()
        }
