"""
Federation Manager

Manages ICO network federation and LD bridges.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Federation:
    """ICO network federation"""
    federation_id: str
    name: str
    networks: List[str]
    created_at: str
    description: Optional[str] = None
    bridges: Optional[List[str]] = None
    routing_policy: Optional[Dict] = None
    security_policy: Optional[Dict] = None
    status: str = "active"
    metadata: Optional[Dict] = None


@dataclass
class LDBridge:
    """Bridge between LDs"""
    bridge_id: str
    source_ld: str
    target_ld: str
    created_at: str
    name: Optional[str] = None
    bridge_type: str = "direct"
    bandwidth_mbps: Optional[int] = None
    latency_ms: Optional[float] = None
    status: str = "active"
    metrics: Optional[Dict] = None
    metadata: Optional[Dict] = None


class FederationManager:
    """Manages ICO network federation"""

    def __init__(self, db_path: str = "federation.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS federations (
                federation_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                networks TEXT NOT NULL,
                bridges TEXT,
                routing_policy TEXT,
                security_policy TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bridges (
                bridge_id TEXT PRIMARY KEY,
                name TEXT,
                source_ld TEXT NOT NULL,
                target_ld TEXT NOT NULL,
                bridge_type TEXT NOT NULL,
                bandwidth_mbps INTEGER,
                latency_ms REAL,
                status TEXT NOT NULL,
                metrics TEXT,
                created_at TEXT NOT NULL,
                metadata TEXT
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bridges_source ON bridges(source_ld)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bridges_target ON bridges(target_ld)")

        conn.commit()
        conn.close()

    def create_federation(
        self,
        name: str,
        networks: List[str],
        description: Optional[str] = None,
        routing_policy: Optional[Dict] = None,
        security_policy: Optional[Dict] = None
    ) -> Federation:
        """Create a new federation"""
        federation_id = f"fed-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        federation = Federation(
            federation_id=federation_id,
            name=name,
            description=description,
            networks=networks,
            bridges=[],
            routing_policy=routing_policy or {"default": "shortest_path"},
            security_policy=security_policy or {"require_auth": True},
            status="active",
            created_at=now,
            metadata={}
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO federations (
                federation_id, name, description, networks, bridges,
                routing_policy, security_policy, status, created_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            federation.federation_id,
            federation.name,
            federation.description,
            json.dumps(federation.networks),
            json.dumps(federation.bridges),
            json.dumps(federation.routing_policy),
            json.dumps(federation.security_policy),
            federation.status,
            federation.created_at,
            json.dumps(federation.metadata)
        ))

        conn.commit()
        conn.close()

        logger.info(f"Created federation: {federation_id}")
        return federation

    def create_bridge(
        self,
        source_ld: str,
        target_ld: str,
        name: Optional[str] = None,
        bridge_type: str = "direct",
        bandwidth_mbps: Optional[int] = None
    ) -> LDBridge:
        """Create a bridge between LDs"""
        bridge_id = f"bridge-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        bridge = LDBridge(
            bridge_id=bridge_id,
            name=name or f"{source_ld}-to-{target_ld}",
            source_ld=source_ld,
            target_ld=target_ld,
            bridge_type=bridge_type,
            bandwidth_mbps=bandwidth_mbps,
            status="active",
            created_at=now,
            metrics={},
            metadata={}
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bridges (
                bridge_id, name, source_ld, target_ld, bridge_type,
                bandwidth_mbps, latency_ms, status, metrics, created_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bridge.bridge_id,
            bridge.name,
            bridge.source_ld,
            bridge.target_ld,
            bridge.bridge_type,
            bridge.bandwidth_mbps,
            bridge.latency_ms,
            bridge.status,
            json.dumps(bridge.metrics),
            bridge.created_at,
            json.dumps(bridge.metadata)
        ))

        conn.commit()
        conn.close()

        logger.info(f"Created bridge: {bridge_id}")
        return bridge

    def route_between_lds(
        self,
        source_ld: str,
        target_ld: str
    ) -> List[str]:
        """Find route between LDs"""
        # Simple implementation - find direct bridge or single hop
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check for direct bridge
        cursor.execute("""
            SELECT bridge_id FROM bridges
            WHERE source_ld = ? AND target_ld = ? AND status = 'active'
        """, (source_ld, target_ld))

        direct = cursor.fetchone()
        if direct:
            conn.close()
            return [source_ld, target_ld]

        # Check for single-hop route
        cursor.execute("""
            SELECT DISTINCT b1.target_ld
            FROM bridges b1
            JOIN bridges b2 ON b1.target_ld = b2.source_ld
            WHERE b1.source_ld = ? AND b2.target_ld = ?
            AND b1.status = 'active' AND b2.status = 'active'
        """, (source_ld, target_ld))

        hop = cursor.fetchone()
        conn.close()

        if hop:
            return [source_ld, hop[0], target_ld]

        return []  # No route found

    def list_bridges(
        self,
        source_ld: Optional[str] = None,
        target_ld: Optional[str] = None,
        limit: int = 100
    ) -> List[LDBridge]:
        """List bridges"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM bridges WHERE 1=1"
        params = []

        if source_ld:
            query += " AND source_ld = ?"
            params.append(source_ld)

        if target_ld:
            query += " AND target_ld = ?"
            params.append(target_ld)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_bridge(row) for row in rows]

    def _row_to_bridge(self, row) -> LDBridge:
        """Convert row to LDBridge"""
        return LDBridge(
            bridge_id=row[0],
            name=row[1],
            source_ld=row[2],
            target_ld=row[3],
            bridge_type=row[4],
            bandwidth_mbps=row[5],
            latency_ms=row[6],
            status=row[7],
            metrics=json.loads(row[8]) if row[8] else {},
            created_at=row[9],
            metadata=json.loads(row[10]) if row[10] else {}
        )
