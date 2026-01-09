"""
HyperSync Model Catalogue Manager

Comprehensive model cataloguing with:
- Identity & lineage tracking
- Tuning history for internal models
- Family tree management
- nLD model tracking & security
- Multi-format support
"""

import sqlite3
import json
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import os
import logging

logger = logging.getLogger(__name__)


class ModelCatalogueManager:
    """Manages the model catalogue with full provenance tracking."""

    def __init__(self, db_path: str = "model_catalogue.db"):
        self.db_path = db_path
        self.conn = None
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with all tables."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        # Models table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                model_id TEXT PRIMARY KEY,
                content_hash TEXT NOT NULL,
                family_id TEXT NOT NULL,
                parent_id TEXT,
                generation INTEGER NOT NULL,
                lineage_path TEXT NOT NULL,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                format TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                added_date TEXT NOT NULL,
                updated_date TEXT NOT NULL,
                FOREIGN KEY (parent_id) REFERENCES models(model_id)
            )
        """)

        # Capabilities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS capabilities (
                model_id TEXT NOT NULL,
                capability TEXT NOT NULL,
                PRIMARY KEY (model_id, capability),
                FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
            )
        """)

        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                model_id TEXT NOT NULL,
                tag TEXT NOT NULL,
                PRIMARY KEY (model_id, tag),
                FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
            )
        """)

        # Tuning sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tuning_sessions (
                session_id TEXT PRIMARY KEY,
                model_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                method TEXT NOT NULL,
                dataset_hash TEXT,
                dataset_size INTEGER,
                hyperparameters TEXT,
                metrics TEXT,
                duration_seconds INTEGER,
                operator TEXT,
                notes TEXT,
                FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
            )
        """)

        # nLD profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nld_profiles (
                model_id TEXT PRIMARY KEY,
                is_nld_model BOOLEAN NOT NULL,
                nld_level INTEGER NOT NULL,
                training_domains TEXT,
                cross_boundary_capabilities TEXT,
                security_classification TEXT,
                stability_metrics TEXT,
                FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
            )
        """)

        # Model metadata table (JSON blob for flexibility)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_metadata (
                model_id TEXT PRIMARY KEY,
                requirements TEXT,
                performance TEXT,
                compatibility TEXT,
                provenance TEXT,
                usage_stats TEXT,
                notes TEXT,
                FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
            )
        """)

        # Families table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS families (
                family_id TEXT PRIMARY KEY,
                root_model_id TEXT NOT NULL,
                family_name TEXT NOT NULL,
                family_metadata TEXT,
                FOREIGN KEY (root_model_id) REFERENCES models(model_id)
            )
        """)

        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_family ON models(family_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_parent ON models(parent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_format ON models(format)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nld_level ON nld_profiles(nld_level)")

        self.conn.commit()

    def compute_file_hash(self, file_path: str) -> str:
        """Compute SHA256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return f"sha256:{sha256.hexdigest()}"

    def detect_format(self, file_path: str) -> str:
        """Auto-detect model format from file."""
        path = Path(file_path)
        ext = path.suffix.lower()

        # Extension-based detection
        if ext == '.gguf':
            return 'GGUF'
        elif ext == '.safetensors':
            return 'SafeTensors'
        elif ext in ['.pt', '.pth', '.bin']:
            # Check for PyTorch magic
            with open(file_path, 'rb') as f:
                magic = f.read(4)
                if magic == b'\x80\x02\x8a\n':  # Pickle magic
                    return 'PyTorch'
        elif ext == '.onnx':
            return 'ONNX'
        elif ext == '.pb':
            return 'TensorFlow'
        elif ext == '.pkl':
            return 'Pickle'

        # Magic byte detection for GGUF
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(4)
                if magic == b'GGUF':
                    return 'GGUF'
        except Exception as e:
            logger.debug(f"GGUF detection failed: {e}")

        return 'Custom'

    def scan_model(self, file_path: str, name: Optional[str] = None, 
                   auto_tag: bool = True) -> str:
        """
        Scan and add a model to the catalogue.
        Returns model_id.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model file not found: {file_path}")

        # Generate IDs
        model_id = str(uuid.uuid4())
        family_id = str(uuid.uuid4())  # New family for base models

        # Compute hash
        content_hash = self.compute_file_hash(file_path)

        # Check for duplicates
        cursor = self.conn.cursor()
        cursor.execute("SELECT model_id, name FROM models WHERE content_hash = ?", (content_hash,))
        existing = cursor.fetchone()
        if existing:
            return existing['model_id']  # Already catalogued

        # Detect format
        format_type = self.detect_format(file_path)

        # Get file info
        size_bytes = os.path.getsize(file_path)
        if name is None:
            name = Path(file_path).stem

        # Create entry
        now = datetime.utcnow().isoformat() + 'Z'
        lineage_path = json.dumps([model_id])

        cursor.execute("""
            INSERT INTO models (
                model_id, content_hash, family_id, parent_id, generation,
                lineage_path, name, path, format, size_bytes, added_date, updated_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (model_id, content_hash, family_id, None, 0, lineage_path,
              name, file_path, format_type, size_bytes, now, now))

        # Create family
        family_name = f"{name}-family"
        family_metadata = json.dumps({
            "primary_capability": "general",
            "specializations": [],
            "total_tuning_hours": 0,
            "total_samples_used": 0,
            "best_performing_member": model_id
        })

        cursor.execute("""
            INSERT INTO families (family_id, root_model_id, family_name, family_metadata)
            VALUES (?, ?, ?, ?)
        """, (family_id, model_id, family_name, family_metadata))

        # Initialize metadata
        provenance = json.dumps({
            "source_type": "external",
            "external_metadata": {
                "origin": file_path,
                "verified": False,
                "import_date": now,
                "user_notes": ""
            }
        })

        usage_stats = json.dumps({
            "times_used": 0,
            "last_used": None,
            "avg_user_rating": None
        })

        cursor.execute("""
            INSERT INTO model_metadata (model_id, provenance, usage_stats)
            VALUES (?, ?, ?)
        """, (model_id, provenance, usage_stats))

        # Auto-tag
        if auto_tag:
            tags = ['base-model', format_type.lower()]
            for tag in tags:
                cursor.execute("INSERT INTO tags (model_id, tag) VALUES (?, ?)",
                             (model_id, tag))

        self.conn.commit()
        return model_id

    def scan_directory(self, dir_path: str, recursive: bool = True) -> List[str]:
        """Scan directory for models and add them to catalogue."""
        model_ids = []
        path = Path(dir_path)

        # Supported extensions
        extensions = ['.gguf', '.safetensors', '.pt', '.pth', '.bin', 
                     '.onnx', '.pb', '.pkl']

        if recursive:
            files = [f for f in path.rglob('*') if f.suffix.lower() in extensions]
        else:
            files = [f for f in path.glob('*') if f.suffix.lower() in extensions]

        for file_path in files:
            try:
                model_id = self.scan_model(str(file_path))
                model_ids.append(model_id)
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")

        return model_ids

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get complete model entry."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM models WHERE model_id = ?", (model_id,))
        model = cursor.fetchone()

        if not model:
            raise ValueError(f"Model not found: {model_id}")

        # Build complete entry
        entry = dict(model)
        entry['lineage_path'] = json.loads(entry['lineage_path'])

        # Get capabilities
        cursor.execute("SELECT capability FROM capabilities WHERE model_id = ?", (model_id,))
        entry['capabilities'] = [row['capability'] for row in cursor.fetchall()]

        # Get tags
        cursor.execute("SELECT tag FROM tags WHERE model_id = ?", (model_id,))
        entry['tags'] = [row['tag'] for row in cursor.fetchall()]

        # Get metadata
        cursor.execute("SELECT * FROM model_metadata WHERE model_id = ?", (model_id,))
        metadata = cursor.fetchone()
        if metadata:
            for key in ['requirements', 'performance', 'compatibility', 
                       'provenance', 'usage_stats', 'notes']:
                if metadata[key]:
                    entry[key] = json.loads(metadata[key])

        # Get tuning history
        cursor.execute("SELECT * FROM tuning_sessions WHERE model_id = ? ORDER BY timestamp",
                      (model_id,))
        sessions = cursor.fetchall()
        if sessions:
            entry['tuning_sessions'] = [dict(s) for s in sessions]

        # Get nLD profile
        cursor.execute("SELECT * FROM nld_profiles WHERE model_id = ?", (model_id,))
        nld = cursor.fetchone()
        if nld:
            entry['nld_profile'] = dict(nld)
            for key in ['training_domains', 'cross_boundary_capabilities',
                       'security_classification', 'stability_metrics']:
                if entry['nld_profile'][key]:
                    entry['nld_profile'][key] = json.loads(entry['nld_profile'][key])

        return entry

    def list_models(self, filter_dict: Optional[Dict[str, Any]] = None,
                   sort_by: str = 'added_date', limit: int = 100) -> List[Dict[str, Any]]:
        """List models with optional filtering."""
        query = "SELECT model_id, name, format, size_bytes, added_date FROM models"
        params = []

        if filter_dict:
            conditions = []
            if 'format' in filter_dict:
                conditions.append("format = ?")
                params.append(filter_dict['format'])
            if 'family_id' in filter_dict:
                conditions.append("family_id = ?")
                params.append(filter_dict['family_id'])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        query += f" ORDER BY {sort_by} DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def add_tuning_session(self, model_id: str, parent_model_id: str,
                          method: str, dataset_hash: str, dataset_size: int,
                          hyperparameters: Dict, metrics: Dict,
                          duration_seconds: int, operator: str,
                          notes: str = "") -> str:
        """Record a tuning session and create new model entry."""
        # Get parent model
        parent = self.get_model(parent_model_id)
        if not parent:
            raise ValueError(f"Parent model not found: {parent_model_id}")

        # Create tuning session
        session_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + 'Z'

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tuning_sessions (
                session_id, model_id, timestamp, method, dataset_hash,
                dataset_size, hyperparameters, metrics, duration_seconds,
                operator, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_id, model_id, now, method, dataset_hash, dataset_size,
              json.dumps(hyperparameters), json.dumps(metrics), duration_seconds,
              operator, notes))

        self.conn.commit()
        return session_id

    def get_family_tree(self, model_id: str) -> Dict[str, Any]:
        """Get complete family tree for a model."""
        model = self.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")

        family_id = model['family_id']

        # Get all family members
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT model_id, name, parent_id, generation
            FROM models WHERE family_id = ?
            ORDER BY generation, added_date
        """, (family_id,))

        members = [dict(row) for row in cursor.fetchall()]

        # Get family metadata
        cursor.execute("SELECT * FROM families WHERE family_id = ?", (family_id,))
        family = dict(cursor.fetchone())
        family['family_metadata'] = json.loads(family['family_metadata'])

        # Build tree structure
        tree = {
            'family': family,
            'members': members,
            'generations': {}
        }

        for member in members:
            gen = member['generation']
            if gen not in tree['generations']:
                tree['generations'][gen] = []
            tree['generations'][gen].append(member)

        return tree

    def set_nld_profile(self, model_id: str, nld_level: int,
                       training_domains: List[Dict],
                       instability_score: float,
                       threat_level: str) -> None:
        """Set nLD profile for a model."""
        is_nld = nld_level > 1

        cross_boundary = {
            "can_bridge_domains": nld_level >= 2,
            "instability_score": instability_score,
            "requires_containment": instability_score > 0.5 or threat_level in ['high', 'critical'],
            "safe_deployment_contexts": ["isolated-ld"] if instability_score > 0.5 else ["any"]
        }

        security = {
            "threat_level": threat_level,
            "requires_authentication": threat_level in ['medium', 'high', 'critical'],
            "allowed_operators": ["admin"] if threat_level == 'critical' else ["any"],
            "audit_logging": "mandatory" if threat_level in ['high', 'critical'] else "optional",
            "containment_policy": None
        }

        stability = {
            "output_consistency": 1.0 - instability_score,
            "hallucination_rate": instability_score * 0.5,
            "domain_bleed": instability_score * 0.3,
            "last_stability_check": datetime.utcnow().isoformat() + 'Z'
        }

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO nld_profiles (
                model_id, is_nld_model, nld_level, training_domains,
                cross_boundary_capabilities, security_classification, stability_metrics
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (model_id, is_nld, nld_level, json.dumps(training_domains),
              json.dumps(cross_boundary), json.dumps(security), json.dumps(stability)))

        self.conn.commit()

    def search_models(self, query: str) -> List[Dict[str, Any]]:
        """Natural language search across models."""
        # Simple keyword search for now
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT m.model_id, m.name, m.format, m.size_bytes
            FROM models m
            LEFT JOIN capabilities c ON m.model_id = c.model_id
            LEFT JOIN tags t ON m.model_id = t.model_id
            WHERE m.name LIKE ? OR c.capability LIKE ? OR t.tag LIKE ?
            LIMIT 50
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))

        return [dict(row) for row in cursor.fetchall()]

    def add_tag(self, model_id: str, tag: str) -> None:
        """Add tag to model."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO tags (model_id, tag) VALUES (?, ?)",
                      (model_id, tag))
        self.conn.commit()

    def remove_tag(self, model_id: str, tag: str) -> None:
        """Remove tag from model."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tags WHERE model_id = ? AND tag = ?",
                      (model_id, tag))
        self.conn.commit()

    def update_metadata(self, model_id: str, field: str, value: Any) -> None:
        """Update model metadata field."""
        cursor = self.conn.cursor()

        if field in ['requirements', 'performance', 'compatibility', 'provenance', 'usage_stats']:
            cursor.execute(f"UPDATE model_metadata SET {field} = ? WHERE model_id = ?",
                          (json.dumps(value), model_id))
        elif field == 'notes':
            cursor.execute("UPDATE model_metadata SET notes = ? WHERE model_id = ?",
                          (value, model_id))
        else:
            raise ValueError(f"Unknown metadata field: {field}")

        self.conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        """Get catalogue statistics."""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM models")
        total = cursor.fetchone()['total']

        cursor.execute("SELECT format, COUNT(*) as count FROM models GROUP BY format")
        by_format = {row['format']: row['count'] for row in cursor.fetchall()}

        cursor.execute("SELECT COUNT(*) as total FROM families")
        families = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM nld_profiles WHERE is_nld_model = 1")
        nld_models = cursor.fetchone()['total']

        return {
            'total_models': total,
            'by_format': by_format,
            'total_families': families,
            'nld_models': nld_models
        }

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
