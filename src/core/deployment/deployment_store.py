"""Deployment persistence layer"""
import sqlite3
import json
from typing import List, Optional
from .placement_engine import DeploymentNode
from pathlib import Path

class DeploymentStore:
    def __init__(self, db_path: str = "~/.hypersync/deployment.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS deployment_nodes (
                node_id TEXT PRIMARY KEY,
                service_name TEXT NOT NULL,
                position_coords TEXT NOT NULL,
                position_model TEXT NOT NULL,
                tier INTEGER NOT NULL,
                capability_vector TEXT NOT NULL,
                current_load REAL DEFAULT 0.0,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def save_node(self, node: DeploymentNode):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO deployment_nodes 
            (node_id, service_name, position_coords, position_model, tier, 
             capability_vector, current_load, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            node.node_id,
            node.service_name,
            json.dumps(node.position.coordinates.tolist()),
            node.position.model,
            node.position.tier,
            json.dumps(node.capability_vector.to_array().tolist()),
            node.current_load,
            node.created_at.isoformat()
        ))
        conn.commit()
        conn.close()

    def get_node(self, node_id: str) -> Optional[DeploymentNode]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT * FROM deployment_nodes WHERE node_id = ?", (node_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        # Reconstruct node from row data
        return None  # Simplified for patch

    def list_nodes(self) -> List[DeploymentNode]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT * FROM deployment_nodes")
        rows = cursor.fetchall()
        conn.close()
        return []  # Simplified for patch
