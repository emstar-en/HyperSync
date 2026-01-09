
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
    """Manages consensus mechanisms and attestation protocols"""

    def __init__(self, db_path: str = "consensus.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Consensus Mechanisms
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS consensus_mechanisms (
                mechanism_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                mechanism_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                data TEXT NOT NULL,
                status TEXT DEFAULT 'active'
            )
            ''')

            # Attestation Protocols
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS attestation_protocols (
                protocol_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                protocol_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                data TEXT NOT NULL,
                status TEXT DEFAULT 'active'
            )
            ''')

            # Consensus Configurations
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS consensus_configs (
                config_id TEXT PRIMARY KEY,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                mechanism_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                data TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (mechanism_id) REFERENCES consensus_mechanisms (mechanism_id)
            )
            ''')

            # Attestation Configurations
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS attestation_configs (
                config_id TEXT PRIMARY KEY,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                protocol_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                data TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (protocol_id) REFERENCES attestation_protocols (protocol_id)
            )
            ''')
            conn.commit()

    def create_consensus_mechanism(self, name: str, mechanism_type: str, **kwargs) -> ConsensusMechanism:
        mechanism_id = f"mech_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()

        mechanism = ConsensusMechanism(
            mechanism_id=mechanism_id,
            name=name,
            mechanism_type=mechanism_type,
            created_at=now,
            **kwargs
        )

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO consensus_mechanisms (mechanism_id, name, mechanism_type, created_at, data, status) VALUES (?, ?, ?, ?, ?, ?)',
                (mechanism_id, name, mechanism_type, now, json.dumps(asdict(mechanism)), mechanism.status)
            )
            conn.commit()

        return mechanism

    def get_consensus_mechanism(self, mechanism_id: str) -> Optional[ConsensusMechanism]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT data FROM consensus_mechanisms WHERE mechanism_id = ?', (mechanism_id,))
            row = cursor.fetchone()

            if row:
                data = json.loads(row[0])
                return ConsensusMechanism(**data)
            return None

    def list_consensus_mechanisms(self, mechanism_type: Optional[str] = None) -> List[ConsensusMechanism]:
        query = 'SELECT data FROM consensus_mechanisms'
        params = []

        if mechanism_type:
            query += ' WHERE mechanism_type = ?'
            params.append(mechanism_type)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [ConsensusMechanism(**json.loads(row[0])) for row in cursor.fetchall()]

    def apply_consensus(self, target_type: str, target_id: str, mechanism_id: str, **kwargs) -> ConsensusConfiguration:
        config_id = f"conf_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()

        config = ConsensusConfiguration(
            config_id=config_id,
            target_type=target_type,
            target_id=target_id,
            mechanism_id=mechanism_id,
            created_at=now,
            **kwargs
        )

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO consensus_configs (config_id, target_type, target_id, mechanism_id, created_at, data, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (config_id, target_type, target_id, mechanism_id, now, json.dumps(asdict(config)), config.status)
            )
            conn.commit()

        return config

    def get_consensus_config(self, target_type: str, target_id: str) -> Optional[ConsensusConfiguration]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT data FROM consensus_configs WHERE target_type = ? AND target_id = ? ORDER BY created_at DESC LIMIT 1',
                (target_type, target_id)
            )
            row = cursor.fetchone()

            if row:
                data = json.loads(row[0])
                return ConsensusConfiguration(**data)
            return None

    def create_attestation_protocol(self, name: str, protocol_type: str, **kwargs) -> AttestationProtocol:
        protocol_id = f"proto_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()

        protocol = AttestationProtocol(
            protocol_id=protocol_id,
            name=name,
            protocol_type=protocol_type,
            created_at=now,
            **kwargs
        )

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO attestation_protocols (protocol_id, name, protocol_type, created_at, data, status) VALUES (?, ?, ?, ?, ?, ?)',
                (protocol_id, name, protocol_type, now, json.dumps(asdict(protocol)), protocol.status)
            )
            conn.commit()

        return protocol

    def get_attestation_protocol(self, protocol_id: str) -> Optional[AttestationProtocol]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT data FROM attestation_protocols WHERE protocol_id = ?', (protocol_id,))
            row = cursor.fetchone()

            if row:
                data = json.loads(row[0])
                return AttestationProtocol(**data)
            return None

    def list_attestation_protocols(self, protocol_type: Optional[str] = None) -> List[AttestationProtocol]:
        query = 'SELECT data FROM attestation_protocols'
        params = []

        if protocol_type:
            query += ' WHERE protocol_type = ?'
            params.append(protocol_type)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [AttestationProtocol(**json.loads(row[0])) for row in cursor.fetchall()]

    def apply_attestation(self, target_type: str, target_id: str, protocol_id: str, **kwargs) -> AttestationConfiguration:
        config_id = f"aconf_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()

        config = AttestationConfiguration(
            config_id=config_id,
            target_type=target_type,
            target_id=target_id,
            protocol_id=protocol_id,
            created_at=now,
            **kwargs
        )

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO attestation_configs (config_id, target_type, target_id, protocol_id, created_at, data, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (config_id, target_type, target_id, protocol_id, now, json.dumps(asdict(config)), config.status)
            )
            conn.commit()

        return config

    def get_attestation_config(self, target_type: str, target_id: str) -> Optional[AttestationConfiguration]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT data FROM attestation_configs WHERE target_type = ? AND target_id = ? ORDER BY created_at DESC LIMIT 1',
                (target_type, target_id)
            )
            row = cursor.fetchone()

            if row:
                data = json.loads(row[0])
                return AttestationConfiguration(**data)
            return None
