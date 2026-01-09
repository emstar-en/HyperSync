"""
Tuning Stable Manager

Manages continuous model tuning environments with gold sample validation
and CI/CD integration.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class TuningStable:
    """Represents a tuning stable environment"""
    stable_id: str
    name: str
    base_model: Dict[str, Any]
    status: str
    created_at: str
    description: Optional[str] = None
    tuning_config: Optional[Dict] = None
    dataset_config: Optional[Dict] = None
    validation_config: Optional[Dict] = None
    checkpoint_config: Optional[Dict] = None
    cicd_integration: Optional[Dict] = None
    runs: Optional[List[Dict]] = None
    current_run: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None


@dataclass
class TuningRun:
    """Represents a single tuning run"""
    run_id: str
    stable_id: str
    started_at: str
    status: str
    completed_at: Optional[str] = None
    progress: Optional[Dict] = None
    metrics: Optional[Dict] = None
    checkpoints: Optional[List[Dict]] = None
    validation_results: Optional[List[Dict]] = None
    resource_usage: Optional[Dict] = None
    error: Optional[Dict] = None


class TuningStableManager:
    """Manages tuning stables and runs"""

    def __init__(self, db_path: str = "tuning_stables.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Stables table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stables (
                stable_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                base_model TEXT NOT NULL,
                tuning_config TEXT,
                dataset_config TEXT,
                validation_config TEXT,
                checkpoint_config TEXT,
                cicd_integration TEXT,
                status TEXT NOT NULL,
                current_run TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                created_by TEXT,
                tags TEXT,
                metadata TEXT
            )
        """)

        # Runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                stable_id TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT NOT NULL,
                progress TEXT,
                metrics TEXT,
                checkpoints TEXT,
                validation_results TEXT,
                resource_usage TEXT,
                error TEXT,
                FOREIGN KEY (stable_id) REFERENCES stables(stable_id)
            )
        """)

        # Checkpoints table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                stable_id TEXT NOT NULL,
                epoch INTEGER,
                step INTEGER,
                path TEXT NOT NULL,
                metrics TEXT,
                is_best INTEGER DEFAULT 0,
                catalogue_entry TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs(run_id),
                FOREIGN KEY (stable_id) REFERENCES stables(stable_id)
            )
        """)

        # Indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stables_status ON stables(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stables_name ON stables(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_stable ON runs(stable_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_checkpoints_run ON checkpoints(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_checkpoints_stable ON checkpoints(stable_id)")

        conn.commit()
        conn.close()

    def create_stable(
        self,
        name: str,
        base_model: Dict[str, Any],
        description: Optional[str] = None,
        tuning_config: Optional[Dict] = None,
        dataset_config: Optional[Dict] = None,
        validation_config: Optional[Dict] = None,
        checkpoint_config: Optional[Dict] = None,
        cicd_integration: Optional[Dict] = None,
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> TuningStable:
        """Create a new tuning stable"""
        stable_id = f"stable-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        stable = TuningStable(
            stable_id=stable_id,
            name=name,
            description=description,
            base_model=base_model,
            tuning_config=tuning_config or self._default_tuning_config(),
            dataset_config=dataset_config,
            validation_config=validation_config or self._default_validation_config(),
            checkpoint_config=checkpoint_config or self._default_checkpoint_config(),
            cicd_integration=cicd_integration,
            status="idle",
            current_run=None,
            runs=[],
            created_at=now,
            updated_at=now,
            created_by=created_by,
            tags=tags or [],
            metadata=metadata or {}
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO stables (
                stable_id, name, description, base_model, tuning_config,
                dataset_config, validation_config, checkpoint_config,
                cicd_integration, status, current_run, created_at, updated_at,
                created_by, tags, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stable.stable_id,
            stable.name,
            stable.description,
            json.dumps(stable.base_model),
            json.dumps(stable.tuning_config),
            json.dumps(stable.dataset_config) if stable.dataset_config else None,
            json.dumps(stable.validation_config),
            json.dumps(stable.checkpoint_config),
            json.dumps(stable.cicd_integration) if stable.cicd_integration else None,
            stable.status,
            stable.current_run,
            stable.created_at,
            stable.updated_at,
            stable.created_by,
            json.dumps(stable.tags),
            json.dumps(stable.metadata)
        ))

        conn.commit()
        conn.close()

        logger.info(f"Created tuning stable: {stable_id} ({name})")
        return stable

    def start_run(
        self,
        stable_id: str,
        override_config: Optional[Dict] = None
    ) -> TuningRun:
        """Start a new tuning run"""
        stable = self.get_stable(stable_id)
        if not stable:
            raise ValueError(f"Stable not found: {stable_id}")

        if stable.status == "running":
            raise ValueError(f"Stable already has an active run: {stable.current_run}")

        run_id = f"run-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        run = TuningRun(
            run_id=run_id,
            stable_id=stable_id,
            started_at=now,
            status="initializing",
            progress={
                "current_epoch": 0,
                "total_epochs": stable.tuning_config.get("hyperparameters", {}).get("epochs", 10),
                "current_step": 0,
                "total_steps": 0,
                "samples_processed": 0,
                "percent_complete": 0.0
            },
            metrics={
                "training_loss": [],
                "validation_loss": [],
                "learning_rate": [],
                "perplexity": [],
                "gold_sample_scores": [],
                "custom_metrics": {}
            },
            checkpoints=[],
            validation_results=[],
            resource_usage={
                "gpu_hours": 0.0,
                "peak_memory_gb": 0.0,
                "avg_gpu_utilization": 0.0,
                "total_samples": 0
            }
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insert run
        cursor.execute("""
            INSERT INTO runs (
                run_id, stable_id, started_at, status, progress,
                metrics, checkpoints, validation_results, resource_usage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run.run_id,
            run.stable_id,
            run.started_at,
            run.status,
            json.dumps(run.progress),
            json.dumps(run.metrics),
            json.dumps(run.checkpoints),
            json.dumps(run.validation_results),
            json.dumps(run.resource_usage)
        ))

        # Update stable
        cursor.execute("""
            UPDATE stables
            SET status = 'running', current_run = ?, updated_at = ?
            WHERE stable_id = ?
        """, (run_id, now, stable_id))

        conn.commit()
        conn.close()

        logger.info(f"Started tuning run: {run_id} in stable {stable_id}")
        return run

    def update_run_progress(
        self,
        run_id: str,
        progress: Dict,
        metrics: Optional[Dict] = None
    ):
        """Update run progress and metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        update_fields = ["progress = ?"]
        params = [json.dumps(progress)]

        if metrics:
            update_fields.append("metrics = ?")
            params.append(json.dumps(metrics))

        params.append(run_id)

        cursor.execute(f"""
            UPDATE runs
            SET {', '.join(update_fields)}
            WHERE run_id = ?
        """, params)

        conn.commit()
        conn.close()

    def save_checkpoint(
        self,
        run_id: str,
        stable_id: str,
        epoch: int,
        step: int,
        path: str,
        metrics: Dict,
        is_best: bool = False,
        catalogue_entry: Optional[str] = None
    ) -> str:
        """Save a checkpoint"""
        checkpoint_id = f"ckpt-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO checkpoints (
                checkpoint_id, run_id, stable_id, epoch, step, path,
                metrics, is_best, catalogue_entry, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            checkpoint_id, run_id, stable_id, epoch, step, path,
            json.dumps(metrics), 1 if is_best else 0, catalogue_entry, now
        ))

        # If this is the best checkpoint, unmark previous best
        if is_best:
            cursor.execute("""
                UPDATE checkpoints
                SET is_best = 0
                WHERE stable_id = ? AND checkpoint_id != ? AND is_best = 1
            """, (stable_id, checkpoint_id))

        conn.commit()
        conn.close()

        logger.info(f"Saved checkpoint: {checkpoint_id} (epoch {epoch}, step {step})")
        return checkpoint_id

    def complete_run(
        self,
        run_id: str,
        status: str = "completed",
        error: Optional[Dict] = None
    ):
        """Complete a tuning run"""
        now = datetime.utcnow().isoformat() + "Z"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update run
        cursor.execute("""
            UPDATE runs
            SET status = ?, completed_at = ?, error = ?
            WHERE run_id = ?
        """, (status, now, json.dumps(error) if error else None, run_id))

        # Update stable
        cursor.execute("""
            UPDATE stables
            SET status = 'idle', current_run = NULL, updated_at = ?
            WHERE current_run = ?
        """, (now, run_id))

        conn.commit()
        conn.close()

        logger.info(f"Completed run: {run_id} with status {status}")

    def get_stable(self, stable_id: str) -> Optional[TuningStable]:
        """Get a stable by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM stables WHERE stable_id = ?", (stable_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Stable not found: {stable_id}")

        return self._row_to_stable(row)

    def list_stables(
        self,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[TuningStable]:
        """List stables with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM stables WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        stables = [self._row_to_stable(row) for row in rows]

        # Filter by tags if specified
        if tags:
            stables = [s for s in stables if any(t in (s.tags or []) for t in tags)]

        return stables

    def get_run(self, run_id: str) -> Optional[TuningRun]:
        """Get a run by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Stable not found: {stable_id}")

        return self._row_to_run(row)

    def list_runs(
        self,
        stable_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[TuningRun]:
        """List runs with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM runs WHERE 1=1"
        params = []

        if stable_id:
            query += " AND stable_id = ?"
            params.append(stable_id)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_run(row) for row in rows]

    def get_checkpoints(
        self,
        stable_id: Optional[str] = None,
        run_id: Optional[str] = None,
        best_only: bool = False
    ) -> List[Dict]:
        """Get checkpoints"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM checkpoints WHERE 1=1"
        params = []

        if stable_id:
            query += " AND stable_id = ?"
            params.append(stable_id)

        if run_id:
            query += " AND run_id = ?"
            params.append(run_id)

        if best_only:
            query += " AND is_best = 1"

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        checkpoints = []
        for row in rows:
            checkpoints.append({
                "checkpoint_id": row[0],
                "run_id": row[1],
                "stable_id": row[2],
                "epoch": row[3],
                "step": row[4],
                "path": row[5],
                "metrics": json.loads(row[6]) if row[6] else {},
                "is_best": bool(row[7]),
                "catalogue_entry": row[8],
                "created_at": row[9]
            })

        return checkpoints

    def delete_stable(self, stable_id: str):
        """Delete a stable and all its runs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM checkpoints WHERE stable_id = ?", (stable_id,))
        cursor.execute("DELETE FROM runs WHERE stable_id = ?", (stable_id,))
        cursor.execute("DELETE FROM stables WHERE stable_id = ?", (stable_id,))

        conn.commit()
        conn.close()

        logger.info(f"Deleted stable: {stable_id}")

    def _row_to_stable(self, row) -> TuningStable:
        """Convert database row to TuningStable"""
        return TuningStable(
            stable_id=row[0],
            name=row[1],
            description=row[2],
            base_model=json.loads(row[3]),
            tuning_config=json.loads(row[4]) if row[4] else None,
            dataset_config=json.loads(row[5]) if row[5] else None,
            validation_config=json.loads(row[6]) if row[6] else None,
            checkpoint_config=json.loads(row[7]) if row[7] else None,
            cicd_integration=json.loads(row[8]) if row[8] else None,
            status=row[9],
            current_run=row[10],
            created_at=row[11],
            updated_at=row[12],
            created_by=row[13],
            tags=json.loads(row[14]) if row[14] else [],
            metadata=json.loads(row[15]) if row[15] else {}
        )

    def _row_to_run(self, row) -> TuningRun:
        """Convert database row to TuningRun"""
        return TuningRun(
            run_id=row[0],
            stable_id=row[1],
            started_at=row[2],
            completed_at=row[3],
            status=row[4],
            progress=json.loads(row[5]) if row[5] else None,
            metrics=json.loads(row[6]) if row[6] else None,
            checkpoints=json.loads(row[7]) if row[7] else [],
            validation_results=json.loads(row[8]) if row[8] else [],
            resource_usage=json.loads(row[9]) if row[9] else None,
            error=json.loads(row[10]) if row[10] else None
        )

    def _default_tuning_config(self) -> Dict:
        """Default tuning configuration"""
        return {
            "method": "lora",
            "hyperparameters": {
                "learning_rate": 2e-4,
                "batch_size": 4,
                "epochs": 3,
                "warmup_steps": 100,
                "lora_r": 8,
                "lora_alpha": 16,
                "lora_dropout": 0.05
            },
            "target_modules": ["q_proj", "v_proj"],
            "optimization": {
                "optimizer": "adamw",
                "scheduler": "cosine",
                "gradient_accumulation_steps": 4,
                "max_grad_norm": 1.0
            }
        }

    def _default_validation_config(self) -> Dict:
        """Default validation configuration"""
        return {
            "validation_frequency": "every_epoch",
            "quality_gates": {
                "min_gold_sample_pass_rate": 0.8,
                "max_regression_tolerance": 0.05
            },
            "early_stopping": {
                "enabled": True,
                "patience": 3,
                "metric": "validation_loss"
            }
        }

    def _default_checkpoint_config(self) -> Dict:
        """Default checkpoint configuration"""
        return {
            "save_frequency": "on_improvement",
            "keep_best_n": 3,
            "keep_last_n": 2,
            "auto_catalogue": True
        }
