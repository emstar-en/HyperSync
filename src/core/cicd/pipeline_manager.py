"""
HyperSync CI/CD Pipeline Manager

Manages pipeline definitions, execution, and lifecycle.
"""

import json
import uuid
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class StageType(Enum):
    BUILD = "build"
    TEST = "test"
    VALIDATE = "validate"
    DEPLOY = "deploy"
    ROLLBACK = "rollback"
    GOLD_SAMPLE_COLLECTION = "gold_sample_collection"


class PipelineManager:
    """Manages CI/CD pipelines and their execution."""

    def __init__(self, db_path: str = "hypersync_cicd.db", storage_path: str = "./cicd_storage"):
        self.db_path = db_path
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize the CI/CD database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Pipelines table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipelines (
                pipeline_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                description TEXT,
                definition JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
        """)

        # Pipeline runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id TEXT PRIMARY KEY,
                pipeline_id TEXT NOT NULL,
                status TEXT NOT NULL,
                trigger_type TEXT,
                trigger_source TEXT,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                duration_seconds REAL,
                run_data JSON,
                FOREIGN KEY (pipeline_id) REFERENCES pipelines(pipeline_id)
            )
        """)

        # Stage executions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stage_executions (
                execution_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                stage_name TEXT NOT NULL,
                stage_type TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                logs TEXT,
                FOREIGN KEY (run_id) REFERENCES pipeline_runs(run_id)
            )
        """)

        # Artifacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                stage_name TEXT,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                size_bytes INTEGER,
                checksum TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES pipeline_runs(run_id)
            )
        """)

        conn.commit()
        conn.close()

    def create_pipeline(self, definition: Dict[str, Any]) -> str:
        """Create a new pipeline from definition."""
        pipeline_id = definition.get('pipeline_id', str(uuid.uuid4()))

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO pipelines (pipeline_id, name, version, description, definition)
            VALUES (?, ?, ?, ?, ?)
        """, (
            pipeline_id,
            definition['name'],
            definition['version'],
            definition.get('description', ''),
            json.dumps(definition)
        ))

        conn.commit()
        conn.close()

        return pipeline_id

    def get_pipeline(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a pipeline definition."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT definition FROM pipelines WHERE pipeline_id = ? AND active = 1
        """, (pipeline_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return json.loads(result[0])
        return None

    def list_pipelines(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """List all pipelines."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT pipeline_id, name, version, description, created_at FROM pipelines"
        if active_only:
            query += " WHERE active = 1"

        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        pipelines = []
        for row in results:
            pipelines.append({
                'pipeline_id': row[0],
                'name': row[1],
                'version': row[2],
                'description': row[3],
                'created_at': row[4]
            })

        return pipelines

    def start_run(self, pipeline_id: str, trigger_type: str = "manual", 
                  trigger_source: str = "user") -> str:
        """Start a new pipeline run."""
        run_id = str(uuid.uuid4())

        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        run_data = {
            'run_id': run_id,
            'pipeline_id': pipeline_id,
            'trigger': {
                'type': trigger_type,
                'source': trigger_source
            },
            'status': PipelineStatus.PENDING.value,
            'started_at': datetime.utcnow().isoformat(),
            'stages': [],
            'artifacts': [],
            'gold_samples_collected': [],
            'gold_sample_validations': []
        }

        cursor.execute("""
            INSERT INTO pipeline_runs (run_id, pipeline_id, status, trigger_type, 
                                      trigger_source, started_at, run_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            pipeline_id,
            PipelineStatus.PENDING.value,
            trigger_type,
            trigger_source,
            datetime.utcnow(),
            json.dumps(run_data)
        ))

        conn.commit()
        conn.close()

        return run_id

    def update_run_status(self, run_id: str, status: PipelineStatus, 
                         run_data: Optional[Dict] = None):
        """Update the status of a pipeline run."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if status in [PipelineStatus.SUCCESS, PipelineStatus.FAILED, 
                     PipelineStatus.CANCELLED, PipelineStatus.ROLLED_BACK]:
            completed_at = datetime.utcnow()

            # Calculate duration
            cursor.execute("SELECT started_at FROM pipeline_runs WHERE run_id = ?", (run_id,))
            started_at = datetime.fromisoformat(cursor.fetchone()[0])
            duration = (completed_at - started_at).total_seconds()

            cursor.execute("""
                UPDATE pipeline_runs 
                SET status = ?, completed_at = ?, duration_seconds = ?, run_data = ?
                WHERE run_id = ?
            """, (status.value, completed_at, duration, 
                  json.dumps(run_data) if run_data else None, run_id))
        else:
            cursor.execute("""
                UPDATE pipeline_runs 
                SET status = ?, run_data = ?
                WHERE run_id = ?
            """, (status.value, json.dumps(run_data) if run_data else None, run_id))

        conn.commit()
        conn.close()

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a pipeline run."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT run_id, pipeline_id, status, trigger_type, trigger_source,
                   started_at, completed_at, duration_seconds, run_data
            FROM pipeline_runs WHERE run_id = ?
        """, (run_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'run_id': result[0],
                'pipeline_id': result[1],
                'status': result[2],
                'trigger_type': result[3],
                'trigger_source': result[4],
                'started_at': result[5],
                'completed_at': result[6],
                'duration_seconds': result[7],
                'data': json.loads(result[8]) if result[8] else {}
            }
        return None

    def list_runs(self, pipeline_id: Optional[str] = None, 
                  limit: int = 50) -> List[Dict[str, Any]]:
        """List pipeline runs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if pipeline_id:
            cursor.execute("""
                SELECT run_id, pipeline_id, status, started_at, completed_at, duration_seconds
                FROM pipeline_runs WHERE pipeline_id = ?
                ORDER BY started_at DESC LIMIT ?
            """, (pipeline_id, limit))
        else:
            cursor.execute("""
                SELECT run_id, pipeline_id, status, started_at, completed_at, duration_seconds
                FROM pipeline_runs
                ORDER BY started_at DESC LIMIT ?
            """, (limit,))

        results = cursor.fetchall()
        conn.close()

        runs = []
        for row in results:
            runs.append({
                'run_id': row[0],
                'pipeline_id': row[1],
                'status': row[2],
                'started_at': row[3],
                'completed_at': row[4],
                'duration_seconds': row[5]
            })

        return runs

    def add_artifact(self, run_id: str, name: str, path: str, 
                    stage_name: Optional[str] = None) -> str:
        """Register an artifact from a pipeline run."""
        artifact_id = str(uuid.uuid4())

        artifact_path = Path(path)
        size_bytes = artifact_path.stat().st_size if artifact_path.exists() else 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO artifacts (artifact_id, run_id, stage_name, name, path, size_bytes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (artifact_id, run_id, stage_name, name, str(path), size_bytes))

        conn.commit()
        conn.close()

        return artifact_id

    def get_artifacts(self, run_id: str) -> List[Dict[str, Any]]:
        """Get all artifacts for a run."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT artifact_id, name, path, size_bytes, stage_name, created_at
            FROM artifacts WHERE run_id = ?
        """, (run_id,))

        results = cursor.fetchall()
        conn.close()

        artifacts = []
        for row in results:
            artifacts.append({
                'artifact_id': row[0],
                'name': row[1],
                'path': row[2],
                'size_bytes': row[3],
                'stage_name': row[4],
                'created_at': row[5]
            })

        return artifacts

    def delete_pipeline(self, pipeline_id: str):
        """Soft delete a pipeline."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE pipelines SET active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE pipeline_id = ?
        """, (pipeline_id,))

        conn.commit()
        conn.close()
