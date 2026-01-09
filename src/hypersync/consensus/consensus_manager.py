"""
Consensus & Attestation Manager

Manages consensus mechanisms and attestation protocols.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConsensusMechanism:
    """Represents a consensus mechanism"""
    mechanism_id: str
    name: str
    mechanism_type: str
    created_at: str
    description: Optional[str] = None
    parameters: Optional[Dict] = None
    tier_requirements: Optional[Dict] = None
    performance: Optional[Dict] = None
    status: str = "active"
    updated_at: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class AttestationProtocol:
    """Represents an attestation protocol"""
    protocol_id: str
    name: str
    protocol_type: str
    created_at: str
    description: Optional[str] = None
    verification: Optional[Dict] = None
    tier_requirements: Optional[Dict] = None
    cryptographic: Optional[Dict] = None
    status: str = "active"
    updated_at: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class ConsensusConfiguration:
    """Applied consensus configuration"""
    config_id: str
    target_type: str
    target_id: str
    mechanism_id: str
    created_at: str
    parameters: Optional[Dict] = None
    nodes: Optional[List[str]] = None
    status: str = "pending"
    metrics: Optional[Dict] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class AttestationConfiguration:
    """Applied attestation configuration"""
    config_id: str
    target_type: str
    target_id: str
    protocol_id: str
    created_at: str
    verification_level: Optional[str] = None
    parameters: Optional[Dict] = None
    attestation_frequency: Optional[Dict] = None
    receipts: Optional[List[Dict]] = None
    status: str = "active"
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    metadata: Optional[Dict] = None


class ConsensusAttestationManager:
    """Manages consensus and attestation configurations"""

    def __init__(self, db_path: str = "consensus_attestation.db"):
        self.db_path = db_path
        self._init_db()
        self._seed_default_mechanisms()

    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Consensus mechanisms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consensus_mechanisms (
                mechanism_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                mechanism_type TEXT NOT NULL,
                parameters TEXT,
                tier_requirements TEXT,
                performance TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                metadata TEXT
            )
        """)

        # Attestation protocols table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attestation_protocols (
                protocol_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                protocol_type TEXT NOT NULL,
                verification TEXT,
                tier_requirements TEXT,
                cryptographic TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                metadata TEXT
            )
        """)

        # Consensus configurations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consensus_configurations (
                config_id TEXT PRIMARY KEY,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                mechanism_id TEXT NOT NULL,
                parameters TEXT,
                nodes TEXT,
                status TEXT NOT NULL,
                metrics TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                created_by TEXT,
                metadata TEXT,
                FOREIGN KEY (mechanism_id) REFERENCES consensus_mechanisms(mechanism_id)
            )
        """)

        # Attestation configurations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attestation_configurations (
                config_id TEXT PRIMARY KEY,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                protocol_id TEXT NOT NULL,
                verification_level TEXT,
                parameters TEXT,
                attestation_frequency TEXT,
                receipts TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                created_by TEXT,
                metadata TEXT,
                FOREIGN KEY (protocol_id) REFERENCES attestation_protocols(protocol_id)
            )
        """)

        # Indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_consensus_mech_type ON consensus_mechanisms(mechanism_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attest_proto_type ON attestation_protocols(protocol_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_consensus_config_target ON consensus_configurations(target_type, target_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attest_config_target ON attestation_configurations(target_type, target_id)")

        conn.commit()
        conn.close()

    def _seed_default_mechanisms(self):
        """Seed default consensus mechanisms and attestation protocols"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if already seeded
        cursor.execute("SELECT COUNT(*) FROM consensus_mechanisms")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return

        now = datetime.utcnow().isoformat() + "Z"

        # Default consensus mechanisms
        default_mechanisms = [
            {
                "mechanism_id": "mech-bft",
                "name": "Byzantine Fault Tolerance",
                "mechanism_type": "bft",
                "description": "BFT consensus for fault-tolerant agreement",
                "parameters": {"quorum_size": 4, "threshold": 0.67, "fault_tolerance": 1},
                "tier_requirements": {"min_tier": "PRO"},
                "performance": {"latency_ms": 100, "throughput_tps": 1000}
            },
            {
                "mechanism_id": "mech-raft",
                "name": "Raft Consensus",
                "mechanism_type": "raft",
                "description": "Leader-based consensus protocol",
                "parameters": {"quorum_size": 3, "timeout_seconds": 5},
                "tier_requirements": {"min_tier": "CORE"},
                "performance": {"latency_ms": 50, "throughput_tps": 5000}
            },
            {
                "mechanism_id": "mech-quorum",
                "name": "Quorum Voting",
                "mechanism_type": "quorum",
                "description": "Simple quorum-based voting",
                "parameters": {"quorum_size": 3, "threshold": 0.5},
                "tier_requirements": {"min_tier": "CORE"},
                "performance": {"latency_ms": 30, "throughput_tps": 10000}
            },
            {
                "mechanism_id": "mech-threshold",
                "name": "Threshold Consensus",
                "mechanism_type": "threshold",
                "description": "Threshold-based agreement",
                "parameters": {"threshold": 0.75},
                "tier_requirements": {"min_tier": "CORE"},
                "performance": {"latency_ms": 40, "throughput_tps": 8000}
            },
            {
                "mechanism_id": "mech-unanimous",
                "name": "Unanimous Agreement",
                "mechanism_type": "unanimous",
                "description": "Requires all nodes to agree",
                "parameters": {},
                "tier_requirements": {"min_tier": "CORE"},
                "performance": {"latency_ms": 200, "throughput_tps": 500}
            },
            {
                "mechanism_id": "mech-transfinite",
                "name": "Transfinite Consensus",
                "mechanism_type": "transfinite",
                "description": "Advanced transfinite consensus for complex scenarios",
                "parameters": {"epochs": 3, "stop_condition": "convergence"},
                "tier_requirements": {"min_tier": "QM Imperium"},
                "performance": {"latency_ms": 500, "throughput_tps": 100}
            }
        ]

        for mech in default_mechanisms:
            cursor.execute("""
                INSERT INTO consensus_mechanisms (
                    mechanism_id, name, description, mechanism_type, parameters,
                    tier_requirements, performance, status, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mech["mechanism_id"],
                mech["name"],
                mech["description"],
                mech["mechanism_type"],
                json.dumps(mech["parameters"]),
                json.dumps(mech["tier_requirements"]),
                json.dumps(mech["performance"]),
                "active",
                now,
                json.dumps({})
            ))

        # Default attestation protocols
        default_protocols = [
            {
                "protocol_id": "proto-geometric",
                "name": "Geometric Proof",
                "protocol_type": "geometric_proof",
                "description": "Geometric attestation with curvature verification",
                "verification": {"method": "geometric", "verification_level": "high"},
                "tier_requirements": {"min_tier": "PRO"}
            },
            {
                "protocol_id": "proto-receipt",
                "name": "Receipt Attestation",
                "protocol_type": "receipt",
                "description": "Receipt-based attestation",
                "verification": {"method": "receipt", "verification_level": "medium"},
                "tier_requirements": {"min_tier": "CORE"}
            },
            {
                "protocol_id": "proto-signature",
                "name": "Digital Signature",
                "protocol_type": "signature",
                "description": "Cryptographic signature attestation",
                "verification": {"method": "signature", "verification_level": "high"},
                "cryptographic": {"algorithm": "ECDSA", "key_size": 256},
                "tier_requirements": {"min_tier": "CORE"}
            },
            {
                "protocol_id": "proto-merkle",
                "name": "Merkle Tree",
                "protocol_type": "merkle_tree",
                "description": "Merkle tree-based attestation",
                "verification": {"method": "merkle", "verification_level": "high"},
                "cryptographic": {"hash_function": "SHA-256"},
                "tier_requirements": {"min_tier": "PRO"}
            },
            {
                "protocol_id": "proto-zkproof",
                "name": "Zero-Knowledge Proof",
                "protocol_type": "zk_proof",
                "description": "Zero-knowledge proof attestation",
                "verification": {"method": "zk", "verification_level": "cryptographic"},
                "tier_requirements": {"min_tier": "QM Campaign"}
            },
            {
                "protocol_id": "proto-tpm",
                "name": "TPM Attestation",
                "protocol_type": "tpm",
                "description": "Trusted Platform Module attestation",
                "verification": {"method": "tpm", "verification_level": "cryptographic"},
                "tier_requirements": {"min_tier": "PRO"}
            }
        ]

        for proto in default_protocols:
            cursor.execute("""
                INSERT INTO attestation_protocols (
                    protocol_id, name, description, protocol_type, verification,
                    tier_requirements, cryptographic, status, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                proto["protocol_id"],
                proto["name"],
                proto["description"],
                proto["protocol_type"],
                json.dumps(proto["verification"]),
                json.dumps(proto["tier_requirements"]),
                json.dumps(proto.get("cryptographic", {})),
                "active",
                now,
                json.dumps({})
            ))

        conn.commit()
        conn.close()

        logger.info("Seeded default consensus mechanisms and attestation protocols")

    # ========================================================================
    # Consensus Mechanism Operations
    # ========================================================================

    def list_consensus_mechanisms(
        self,
        mechanism_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[ConsensusMechanism]:
        """List available consensus mechanisms"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM consensus_mechanisms WHERE 1=1"
        params = []

        if mechanism_type:
            query += " AND mechanism_type = ?"
            params.append(mechanism_type)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY name LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_mechanism(row) for row in rows]

    def get_consensus_mechanism(self, mechanism_id: str) -> Optional[ConsensusMechanism]:
        """Get a consensus mechanism by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM consensus_mechanisms WHERE mechanism_id = ?", (mechanism_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_mechanism(row)

    # ========================================================================
    # Attestation Protocol Operations
    # ========================================================================

    def list_attestation_protocols(
        self,
        protocol_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[AttestationProtocol]:
        """List available attestation protocols"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM attestation_protocols WHERE 1=1"
        params = []

        if protocol_type:
            query += " AND protocol_type = ?"
            params.append(protocol_type)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY name LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_protocol(row) for row in rows]

    def get_attestation_protocol(self, protocol_id: str) -> Optional[AttestationProtocol]:
        """Get an attestation protocol by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM attestation_protocols WHERE protocol_id = ?", (protocol_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_protocol(row)

    # ========================================================================
    # Consensus Configuration Operations
    # ========================================================================

    def apply_consensus(
        self,
        target_type: str,
        target_id: str,
        mechanism_id: str,
        parameters: Optional[Dict] = None,
        nodes: Optional[List[str]] = None,
        created_by: Optional[str] = None
    ) -> ConsensusConfiguration:
        """Apply consensus mechanism to a target"""
        # Verify mechanism exists
        mechanism = self.get_consensus_mechanism(mechanism_id)
        if not mechanism:
            raise ValueError(f"Consensus mechanism not found: {mechanism_id}")

        config_id = f"consensus-config-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        # Merge parameters with mechanism defaults
        final_params = mechanism.parameters.copy() if mechanism.parameters else {}
        if parameters:
            final_params.update(parameters)

        config = ConsensusConfiguration(
            config_id=config_id,
            target_type=target_type,
            target_id=target_id,
            mechanism_id=mechanism_id,
            parameters=final_params,
            nodes=nodes or [],
            status="active",
            metrics={
                "rounds_completed": 0,
                "agreements_reached": 0,
                "disagreements": 0
            },
            created_at=now,
            updated_at=now,
            created_by=created_by,
            metadata={}
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO consensus_configurations (
                config_id, target_type, target_id, mechanism_id, parameters,
                nodes, status, metrics, created_at, updated_at, created_by, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            config.config_id,
            config.target_type,
            config.target_id,
            config.mechanism_id,
            json.dumps(config.parameters),
            json.dumps(config.nodes),
            config.status,
            json.dumps(config.metrics),
            config.created_at,
            config.updated_at,
            config.created_by,
            json.dumps(config.metadata)
        ))

        conn.commit()
        conn.close()

        logger.info(f"Applied consensus {mechanism_id} to {target_type}:{target_id}")
        return config

    def get_consensus_config(
        self,
        target_type: str,
        target_id: str
    ) -> Optional[ConsensusConfiguration]:
        """Get consensus configuration for a target"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM consensus_configurations
            WHERE target_type = ? AND target_id = ?
            ORDER BY created_at DESC LIMIT 1
        """, (target_type, target_id))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_consensus_config(row)

    def list_consensus_configs(
        self,
        target_type: Optional[str] = None,
        mechanism_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ConsensusConfiguration]:
        """List consensus configurations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM consensus_configurations WHERE 1=1"
        params = []

        if target_type:
            query += " AND target_type = ?"
            params.append(target_type)

        if mechanism_id:
            query += " AND mechanism_id = ?"
            params.append(mechanism_id)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_consensus_config(row) for row in rows]

    # ========================================================================
    # Attestation Configuration Operations
    # ========================================================================

    def apply_attestation(
        self,
        target_type: str,
        target_id: str,
        protocol_id: str,
        verification_level: Optional[str] = None,
        parameters: Optional[Dict] = None,
        attestation_frequency: Optional[Dict] = None,
        created_by: Optional[str] = None
    ) -> AttestationConfiguration:
        """Apply attestation protocol to a target"""
        # Verify protocol exists
        protocol = self.get_attestation_protocol(protocol_id)
        if not protocol:
            raise ValueError(f"Attestation protocol not found: {protocol_id}")

        config_id = f"attest-config-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        # Use protocol's default verification level if not specified
        if not verification_level and protocol.verification:
            verification_level = protocol.verification.get("verification_level", "medium")

        config = AttestationConfiguration(
            config_id=config_id,
            target_type=target_type,
            target_id=target_id,
            protocol_id=protocol_id,
            verification_level=verification_level,
            parameters=parameters or {},
            attestation_frequency=attestation_frequency or {"interval_seconds": 3600},
            receipts=[],
            status="active",
            created_at=now,
            updated_at=now,
            created_by=created_by,
            metadata={}
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO attestation_configurations (
                config_id, target_type, target_id, protocol_id, verification_level,
                parameters, attestation_frequency, receipts, status,
                created_at, updated_at, created_by, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            config.config_id,
            config.target_type,
            config.target_id,
            config.protocol_id,
            config.verification_level,
            json.dumps(config.parameters),
            json.dumps(config.attestation_frequency),
            json.dumps(config.receipts),
            config.status,
            config.created_at,
            config.updated_at,
            config.created_by,
            json.dumps(config.metadata)
        ))

        conn.commit()
        conn.close()

        logger.info(f"Applied attestation {protocol_id} to {target_type}:{target_id}")
        return config

    def get_attestation_config(
        self,
        target_type: str,
        target_id: str
    ) -> Optional[AttestationConfiguration]:
        """Get attestation configuration for a target"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM attestation_configurations
            WHERE target_type = ? AND target_id = ?
            ORDER BY created_at DESC LIMIT 1
        """, (target_type, target_id))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_attestation_config(row)

    def list_attestation_configs(
        self,
        target_type: Optional[str] = None,
        protocol_id: Optional[str] = None,
        limit: int = 100
    ) -> List[AttestationConfiguration]:
        """List attestation configurations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM attestation_configurations WHERE 1=1"
        params = []

        if target_type:
            query += " AND target_type = ?"
            params.append(target_type)

        if protocol_id:
            query += " AND protocol_id = ?"
            params.append(protocol_id)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_attestation_config(row) for row in rows]

    def add_attestation_receipt(
        self,
        config_id: str,
        receipt: Dict
    ):
        """Add an attestation receipt to a configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current receipts
        cursor.execute("SELECT receipts FROM attestation_configurations WHERE config_id = ?", (config_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            raise ValueError(f"Attestation configuration not found: {config_id}")

        receipts = json.loads(row[0]) if row[0] else []
        receipts.append(receipt)

        # Update
        cursor.execute("""
            UPDATE attestation_configurations
            SET receipts = ?, updated_at = ?
            WHERE config_id = ?
        """, (json.dumps(receipts), datetime.utcnow().isoformat() + "Z", config_id))

        conn.commit()
        conn.close()

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _row_to_mechanism(self, row) -> ConsensusMechanism:
        """Convert row to ConsensusMechanism"""
        return ConsensusMechanism(
            mechanism_id=row[0],
            name=row[1],
            description=row[2],
            mechanism_type=row[3],
            parameters=json.loads(row[4]) if row[4] else {},
            tier_requirements=json.loads(row[5]) if row[5] else {},
            performance=json.loads(row[6]) if row[6] else {},
            status=row[7],
            created_at=row[8],
            updated_at=row[9],
            metadata=json.loads(row[10]) if row[10] else {}
        )

    def _row_to_protocol(self, row) -> AttestationProtocol:
        """Convert row to AttestationProtocol"""
        return AttestationProtocol(
            protocol_id=row[0],
            name=row[1],
            description=row[2],
            protocol_type=row[3],
            verification=json.loads(row[4]) if row[4] else {},
            tier_requirements=json.loads(row[5]) if row[5] else {},
            cryptographic=json.loads(row[6]) if row[6] else {},
            status=row[7],
            created_at=row[8],
            updated_at=row[9],
            metadata=json.loads(row[10]) if row[10] else {}
        )

    def _row_to_consensus_config(self, row) -> ConsensusConfiguration:
        """Convert row to ConsensusConfiguration"""
        return ConsensusConfiguration(
            config_id=row[0],
            target_type=row[1],
            target_id=row[2],
            mechanism_id=row[3],
            parameters=json.loads(row[4]) if row[4] else {},
            nodes=json.loads(row[5]) if row[5] else [],
            status=row[6],
            metrics=json.loads(row[7]) if row[7] else {},
            created_at=row[8],
            updated_at=row[9],
            created_by=row[10],
            metadata=json.loads(row[11]) if row[11] else {}
        )

    def _row_to_attestation_config(self, row) -> AttestationConfiguration:
        """Convert row to AttestationConfiguration"""
        return AttestationConfiguration(
            config_id=row[0],
            target_type=row[1],
            target_id=row[2],
            protocol_id=row[3],
            verification_level=row[4],
            parameters=json.loads(row[5]) if row[5] else {},
            attestation_frequency=json.loads(row[6]) if row[6] else {},
            receipts=json.loads(row[7]) if row[7] else [],
            status=row[8],
            created_at=row[9],
            updated_at=row[10],
            created_by=row[11],
            metadata=json.loads(row[12]) if row[12] else {}
        )
