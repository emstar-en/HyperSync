"""
HyperSync Gold Sample Manager

Manages gold samples for regression testing and validation.
"""

import json
import uuid
import sqlite3
import hashlib
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class GoldSampleManager:
    """Manages gold samples for CI/CD validation."""

    def __init__(self, db_path: str = "hypersync_cicd.db", 
                 storage_path: str = "./cicd_storage/gold_samples"):
        self.db_path = db_path
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize gold sample database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Gold samples table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gold_samples (
                sample_id TEXT PRIMARY KEY,
                pipeline_id TEXT NOT NULL,
                stage TEXT NOT NULL,
                step TEXT,
                version TEXT,
                git_commit TEXT,
                timestamp TIMESTAMP NOT NULL,
                data_path TEXT NOT NULL,
                metadata JSON,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Validation results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gold_sample_validations (
                validation_id TEXT PRIMARY KEY,
                sample_id TEXT NOT NULL,
                run_id TEXT,
                timestamp TIMESTAMP NOT NULL,
                similarity_score REAL,
                passed BOOLEAN NOT NULL,
                differences JSON,
                metrics_comparison JSON,
                FOREIGN KEY (sample_id) REFERENCES gold_samples(sample_id)
            )
        """)

        # Sample lineage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gold_sample_lineage (
                sample_id TEXT PRIMARY KEY,
                parent_sample_id TEXT,
                derivation TEXT,
                FOREIGN KEY (sample_id) REFERENCES gold_samples(sample_id),
                FOREIGN KEY (parent_sample_id) REFERENCES gold_samples(sample_id)
            )
        """)

        conn.commit()
        conn.close()

    def create_sample(self, pipeline_id: str, stage: str, data: Dict[str, Any],
                     step: Optional[str] = None, version: Optional[str] = None,
                     git_commit: Optional[str] = None, metadata: Optional[Dict] = None,
                     parent_sample_id: Optional[str] = None,
                     derivation: str = "baseline") -> str:
        """Create a new gold sample."""
        sample_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        # Save data to file
        data_filename = f"{sample_id}.json"
        data_path = self.storage_path / data_filename

        with open(data_path, 'w') as f:
            json.dump(data, f, indent=2)

        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO gold_samples 
            (sample_id, pipeline_id, stage, step, version, git_commit, 
             timestamp, data_path, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sample_id, pipeline_id, stage, step, version, git_commit,
            timestamp, str(data_path), json.dumps(metadata) if metadata else None
        ))

        # Record lineage if parent exists
        if parent_sample_id:
            cursor.execute("""
                INSERT INTO gold_sample_lineage (sample_id, parent_sample_id, derivation)
                VALUES (?, ?, ?)
            """, (sample_id, parent_sample_id, derivation))

        conn.commit()
        conn.close()

        return sample_id

    def get_sample(self, sample_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a gold sample."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT sample_id, pipeline_id, stage, step, version, git_commit,
                   timestamp, data_path, metadata
            FROM gold_samples WHERE sample_id = ? AND active = 1
        """, (sample_id,))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        # Load data from file
        data_path = Path(result[7])
        if data_path.exists():
            with open(data_path, 'r') as f:
                data = json.load(f)
        else:
            data = {}

        return {
            'sample_id': result[0],
            'pipeline_id': result[1],
            'stage': result[2],
            'step': result[3],
            'version': result[4],
            'git_commit': result[5],
            'timestamp': result[6],
            'data': data,
            'metadata': json.loads(result[8]) if result[8] else {}
        }

    def list_samples(self, pipeline_id: Optional[str] = None,
                    stage: Optional[str] = None,
                    version: Optional[str] = None) -> List[Dict[str, Any]]:
        """List gold samples with optional filters."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT sample_id, pipeline_id, stage, step, version, timestamp
            FROM gold_samples WHERE active = 1
        """
        params = []

        if pipeline_id:
            query += " AND pipeline_id = ?"
            params.append(pipeline_id)

        if stage:
            query += " AND stage = ?"
            params.append(stage)

        if version:
            query += " AND version = ?"
            params.append(version)

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        samples = []
        for row in results:
            samples.append({
                'sample_id': row[0],
                'pipeline_id': row[1],
                'stage': row[2],
                'step': row[3],
                'version': row[4],
                'timestamp': row[5]
            })

        return samples

    def validate_against_sample(self, sample_id: str, test_data: Dict[str, Any],
                               run_id: Optional[str] = None,
                               comparison_method: str = "fuzzy",
                               threshold: float = 0.95) -> Tuple[bool, float, Dict]:
        """Validate test data against a gold sample."""
        sample = self.get_sample(sample_id)
        if not sample:
            raise ValueError(f"Gold sample {sample_id} not found")

        gold_data = sample['data']

        # Perform comparison based on method
        if comparison_method == "exact":
            passed, score, differences = self._exact_comparison(gold_data, test_data)
        elif comparison_method == "fuzzy":
            passed, score, differences = self._fuzzy_comparison(gold_data, test_data, threshold)
        elif comparison_method == "metric_based":
            passed, score, differences = self._metric_comparison(gold_data, test_data, threshold)
        elif comparison_method == "hyperbolic_distance":
            passed, score, differences = self._hyperbolic_comparison(gold_data, test_data, threshold)
        else:
            raise ValueError(f"Unknown comparison method: {comparison_method}")

        # Record validation result
        validation_id = str(uuid.uuid4())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO gold_sample_validations
            (validation_id, sample_id, run_id, timestamp, similarity_score, 
             passed, differences)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            validation_id, sample_id, run_id, datetime.utcnow(),
            score, passed, json.dumps(differences)
        ))

        conn.commit()
        conn.close()

        return passed, score, differences

    def _exact_comparison(self, gold: Dict, test: Dict) -> Tuple[bool, float, Dict]:
        """Exact comparison of data."""
        gold_str = json.dumps(gold, sort_keys=True)
        test_str = json.dumps(test, sort_keys=True)

        passed = gold_str == test_str
        score = 1.0 if passed else 0.0

        differences = {}
        if not passed:
            differences = self._find_differences(gold, test)

        return passed, score, differences

    def _fuzzy_comparison(self, gold: Dict, test: Dict, 
                         threshold: float) -> Tuple[bool, float, Dict]:
        """Fuzzy comparison allowing small differences."""
        differences = self._find_differences(gold, test)

        # Calculate similarity score
        total_fields = self._count_fields(gold)
        different_fields = len(differences)

        score = 1.0 - (different_fields / max(total_fields, 1))
        passed = score >= threshold

        return passed, score, differences

    def _metric_comparison(self, gold: Dict, test: Dict,
                          threshold: float) -> Tuple[bool, float, Dict]:
        """Compare based on metrics."""
        gold_metrics = gold.get('metrics', {})
        test_metrics = test.get('metrics', {})

        if not gold_metrics or not test_metrics:
            return self._fuzzy_comparison(gold, test, threshold)

        # Compare each metric
        metric_scores = []
        differences = {}

        for metric_name, gold_value in gold_metrics.items():
            if metric_name not in test_metrics:
                differences[f"metrics.{metric_name}"] = {
                    'gold': gold_value,
                    'test': None,
                    'missing': True
                }
                metric_scores.append(0.0)
            else:
                test_value = test_metrics[metric_name]

                # Calculate relative difference
                if isinstance(gold_value, (int, float)) and isinstance(test_value, (int, float)):
                    if gold_value == 0:
                        rel_diff = 0.0 if test_value == 0 else 1.0
                    else:
                        rel_diff = abs(gold_value - test_value) / abs(gold_value)

                    metric_score = max(0.0, 1.0 - rel_diff)
                    metric_scores.append(metric_score)

                    if metric_score < threshold:
                        differences[f"metrics.{metric_name}"] = {
                            'gold': gold_value,
                            'test': test_value,
                            'relative_diff': rel_diff
                        }
                else:
                    # Non-numeric comparison
                    if gold_value == test_value:
                        metric_scores.append(1.0)
                    else:
                        metric_scores.append(0.0)
                        differences[f"metrics.{metric_name}"] = {
                            'gold': gold_value,
                            'test': test_value
                        }

        # Overall score is average of metric scores
        score = sum(metric_scores) / len(metric_scores) if metric_scores else 0.0
        passed = score >= threshold

        return passed, score, differences

    def _hyperbolic_comparison(self, gold: Dict, test: Dict,
                              threshold: float) -> Tuple[bool, float, Dict]:
        """Compare using hyperbolic distance."""
        # Extract embeddings if available
        gold_embedding = gold.get('outputs', {}).get('embedding')
        test_embedding = test.get('outputs', {}).get('embedding')

        if gold_embedding is None or test_embedding is None:
            # Fall back to fuzzy comparison
            return self._fuzzy_comparison(gold, test, threshold)

        # Convert to numpy arrays
        gold_vec = np.array(gold_embedding)
        test_vec = np.array(test_embedding)

        # Calculate hyperbolic distance (Poincaré ball model)
        # d(x,y) = arcosh(1 + 2 * ||x-y||^2 / ((1-||x||^2)(1-||y||^2)))

        diff_norm_sq = np.sum((gold_vec - test_vec) ** 2)
        gold_norm_sq = np.sum(gold_vec ** 2)
        test_norm_sq = np.sum(test_vec ** 2)

        # Ensure points are in the unit ball
        gold_norm_sq = min(gold_norm_sq, 0.999)
        test_norm_sq = min(test_norm_sq, 0.999)

        numerator = 2 * diff_norm_sq
        denominator = (1 - gold_norm_sq) * (1 - test_norm_sq)

        distance = np.arccosh(1 + numerator / denominator)

        # Convert distance to similarity score (0-1)
        # Normalize by a reasonable max distance (e.g., 5)
        max_distance = 5.0
        score = max(0.0, 1.0 - (distance / max_distance))

        passed = score >= threshold

        differences = {}
        if not passed:
            differences['hyperbolic_distance'] = float(distance)
            differences['similarity_score'] = float(score)

        return passed, score, differences

    def _find_differences(self, gold: Dict, test: Dict, prefix: str = "") -> Dict:
        """Recursively find differences between two dictionaries."""
        differences = {}

        # Check for missing keys in test
        for key in gold:
            full_key = f"{prefix}.{key}" if prefix else key

            if key not in test:
                differences[full_key] = {
                    'gold': gold[key],
                    'test': None,
                    'missing': True
                }
            elif isinstance(gold[key], dict) and isinstance(test[key], dict):
                # Recurse into nested dicts
                nested_diffs = self._find_differences(gold[key], test[key], full_key)
                differences.update(nested_diffs)
            elif gold[key] != test[key]:
                differences[full_key] = {
                    'gold': gold[key],
                    'test': test[key]
                }

        # Check for extra keys in test
        for key in test:
            if key not in gold:
                full_key = f"{prefix}.{key}" if prefix else key
                differences[full_key] = {
                    'gold': None,
                    'test': test[key],
                    'extra': True
                }

        return differences

    def _count_fields(self, data: Dict, count: int = 0) -> int:
        """Count total number of fields in nested dict."""
        for value in data.values():
            count += 1
            if isinstance(value, dict):
                count = self._count_fields(value, count)
        return count

    def get_validation_history(self, sample_id: str) -> List[Dict[str, Any]]:
        """Get validation history for a gold sample."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT validation_id, run_id, timestamp, similarity_score, 
                   passed, differences
            FROM gold_sample_validations
            WHERE sample_id = ?
            ORDER BY timestamp DESC
        """, (sample_id,))

        results = cursor.fetchall()
        conn.close()

        history = []
        for row in results:
            history.append({
                'validation_id': row[0],
                'run_id': row[1],
                'timestamp': row[2],
                'similarity_score': row[3],
                'passed': bool(row[4]),
                'differences': json.loads(row[5]) if row[5] else {}
            })

        return history

    def get_lineage(self, sample_id: str) -> Dict[str, Any]:
        """Get lineage information for a sample."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT parent_sample_id, derivation
            FROM gold_sample_lineage
            WHERE sample_id = ?
        """, (sample_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'parent_sample_id': result[0],
                'derivation': result[1]
            }
        return {}

    def deactivate_sample(self, sample_id: str):
        """Deactivate a gold sample."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE gold_samples SET active = 0
            WHERE sample_id = ?
        """, (sample_id,))

        conn.commit()
        conn.close()

    def cleanup_old_samples(self, max_age_days: int = 365, max_samples: int = 100):
        """Clean up old gold samples based on retention policy."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Deactivate samples older than max_age_days
        cursor.execute("""
            UPDATE gold_samples SET active = 0
            WHERE julianday('now') - julianday(timestamp) > ?
        """, (max_age_days,))

        # Keep only the most recent max_samples per pipeline
        cursor.execute("""
            SELECT pipeline_id FROM gold_samples WHERE active = 1
            GROUP BY pipeline_id
        """)

        pipelines = [row[0] for row in cursor.fetchall()]

        for pipeline_id in pipelines:
            cursor.execute("""
                SELECT sample_id FROM gold_samples
                WHERE pipeline_id = ? AND active = 1
                ORDER BY timestamp DESC
                LIMIT -1 OFFSET ?
            """, (pipeline_id, max_samples))

            old_samples = [row[0] for row in cursor.fetchall()]

            for sample_id in old_samples:
                cursor.execute("""
                    UPDATE gold_samples SET active = 0
                    WHERE sample_id = ?
                """, (sample_id,))

        conn.commit()
        conn.close()
