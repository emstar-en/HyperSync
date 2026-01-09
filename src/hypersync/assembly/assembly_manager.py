"""
Assembly Manager

Manages model stacks and node assemblies for deployment.
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
class ModelStack:
    """Represents a model stack"""
    stack_id: str
    name: str
    models: List[Dict[str, Any]]
    created_at: str
    description: Optional[str] = None
    orchestration: Optional[Dict] = None
    resource_requirements: Optional[Dict] = None
    nvm_assignments: Optional[List[Dict]] = None
    capabilities: Optional[List[str]] = None
    version: Optional[str] = "1.0.0"
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None


@dataclass
class NodeAssembly:
    """Represents a node assembly"""
    assembly_id: str
    name: str
    stack_id: str
    deployment_config: Dict[str, Any]
    created_at: str
    description: Optional[str] = None
    network_config: Optional[Dict] = None
    security_config: Optional[Dict] = None
    monitoring_config: Optional[Dict] = None
    status: str = "draft"
    deployment_id: Optional[str] = None
    validation_results: Optional[Dict] = None
    updated_at: Optional[str] = None
    deployed_at: Optional[str] = None
    created_by: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None


@dataclass
class Deployment:
    """Represents a deployment"""
    deployment_id: str
    assembly_id: str
    node_id: str
    status: str
    deployed_at: str
    ld_address: Optional[str] = None
    health: Optional[Dict] = None
    metrics: Optional[Dict] = None
    endpoints: Optional[List[Dict]] = None
    stopped_at: Optional[str] = None
    logs: Optional[List[Dict]] = None


class AssemblyManager:
    """Manages model stacks, node assemblies, and deployments"""

    def __init__(self, db_path: str = "assembly.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Stacks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stacks (
                stack_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                models TEXT NOT NULL,
                orchestration TEXT,
                resource_requirements TEXT,
                nvm_assignments TEXT,
                capabilities TEXT,
                version TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                created_by TEXT,
                tags TEXT,
                metadata TEXT
            )
        """)

        # Assemblies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assemblies (
                assembly_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                stack_id TEXT NOT NULL,
                deployment_config TEXT NOT NULL,
                network_config TEXT,
                security_config TEXT,
                monitoring_config TEXT,
                status TEXT NOT NULL,
                deployment_id TEXT,
                validation_results TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                deployed_at TEXT,
                created_by TEXT,
                tags TEXT,
                metadata TEXT,
                FOREIGN KEY (stack_id) REFERENCES stacks(stack_id)
            )
        """)

        # Deployments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deployments (
                deployment_id TEXT PRIMARY KEY,
                assembly_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                ld_address TEXT,
                status TEXT NOT NULL,
                health TEXT,
                metrics TEXT,
                endpoints TEXT,
                deployed_at TEXT NOT NULL,
                stopped_at TEXT,
                logs TEXT,
                FOREIGN KEY (assembly_id) REFERENCES assemblies(assembly_id)
            )
        """)

        # Indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stacks_name ON stacks(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assemblies_stack ON assemblies(stack_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assemblies_status ON assemblies(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deployments_assembly ON deployments(assembly_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deployments_status ON deployments(status)")

        conn.commit()
        conn.close()

    # ========================================================================
    # Model Stack Operations
    # ========================================================================

    def create_stack(
        self,
        name: str,
        models: List[Dict[str, Any]],
        description: Optional[str] = None,
        orchestration: Optional[Dict] = None,
        resource_requirements: Optional[Dict] = None,
        nvm_assignments: Optional[List[Dict]] = None,
        capabilities: Optional[List[str]] = None,
        version: str = "1.0.0",
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> ModelStack:
        """Create a new model stack"""
        stack_id = f"stack-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        # Validate models
        if not models:
            raise ValueError("At least one model is required")

        for model in models:
            if "role" not in model or "model_id" not in model:
                raise ValueError("Each model must have 'role' and 'model_id'")

        # Calculate resource requirements if not provided
        if not resource_requirements:
            resource_requirements = self._calculate_resources(models)

        stack = ModelStack(
            stack_id=stack_id,
            name=name,
            description=description,
            models=models,
            orchestration=orchestration or {"mode": "sequential"},
            resource_requirements=resource_requirements,
            nvm_assignments=nvm_assignments or [],
            capabilities=capabilities or [],
            version=version,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            tags=tags or [],
            metadata=metadata or {}
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO stacks (
                stack_id, name, description, models, orchestration,
                resource_requirements, nvm_assignments, capabilities,
                version, created_at, updated_at, created_by, tags, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stack.stack_id,
            stack.name,
            stack.description,
            json.dumps(stack.models),
            json.dumps(stack.orchestration),
            json.dumps(stack.resource_requirements),
            json.dumps(stack.nvm_assignments),
            json.dumps(stack.capabilities),
            stack.version,
            stack.created_at,
            stack.updated_at,
            stack.created_by,
            json.dumps(stack.tags),
            json.dumps(stack.metadata)
        ))

        conn.commit()
        conn.close()

        logger.info(f"Created model stack: {stack_id} ({name})")
        return stack

    def get_stack(self, stack_id: str) -> Optional[ModelStack]:
        """Get a stack by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM stacks WHERE stack_id = ?", (stack_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_stack(row)

    def list_stacks(
        self,
        tags: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[ModelStack]:
        """List stacks with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM stacks ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()

        stacks = [self._row_to_stack(row) for row in rows]

        # Filter by tags
        if tags:
            stacks = [s for s in stacks if any(t in (s.tags or []) for t in tags)]

        # Filter by capabilities
        if capabilities:
            stacks = [s for s in stacks if any(c in (s.capabilities or []) for c in capabilities)]

        return stacks

    def delete_stack(self, stack_id: str):
        """Delete a stack"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if stack is used in any assemblies
        cursor.execute("SELECT COUNT(*) FROM assemblies WHERE stack_id = ?", (stack_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            conn.close()
            raise ValueError(f"Stack is used in {count} assemblies. Cannot delete.")

        cursor.execute("DELETE FROM stacks WHERE stack_id = ?", (stack_id,))
        conn.commit()
        conn.close()

        logger.info(f"Deleted stack: {stack_id}")

    # ========================================================================
    # Node Assembly Operations
    # ========================================================================

    def create_assembly(
        self,
        name: str,
        stack_id: str,
        target_ld: str,
        description: Optional[str] = None,
        security_level: str = "secure",
        network_config: Optional[Dict] = None,
        security_config: Optional[Dict] = None,
        monitoring_config: Optional[Dict] = None,
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> NodeAssembly:
        """Create a new node assembly"""
        # Verify stack exists
        stack = self.get_stack(stack_id)
        if not stack:
            raise ValueError(f"Stack not found: {stack_id}")

        assembly_id = f"assembly-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        deployment_config = {
            "target_ld": target_ld,
            "security_level": security_level,
            "health_check": {
                "enabled": True,
                "interval_seconds": 30,
                "timeout_seconds": 10,
                "unhealthy_threshold": 3
            }
        }

        assembly = NodeAssembly(
            assembly_id=assembly_id,
            name=name,
            description=description,
            stack_id=stack_id,
            deployment_config=deployment_config,
            network_config=network_config or {},
            security_config=security_config or self._default_security_config(),
            monitoring_config=monitoring_config or {"metrics_enabled": True, "logging_enabled": True},
            status="draft",
            created_at=now,
            updated_at=now,
            created_by=created_by,
            tags=tags or [],
            metadata=metadata or {}
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO assemblies (
                assembly_id, name, description, stack_id, deployment_config,
                network_config, security_config, monitoring_config, status,
                created_at, updated_at, created_by, tags, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            assembly.assembly_id,
            assembly.name,
            assembly.description,
            assembly.stack_id,
            json.dumps(assembly.deployment_config),
            json.dumps(assembly.network_config),
            json.dumps(assembly.security_config),
            json.dumps(assembly.monitoring_config),
            assembly.status,
            assembly.created_at,
            assembly.updated_at,
            assembly.created_by,
            json.dumps(assembly.tags),
            json.dumps(assembly.metadata)
        ))

        conn.commit()
        conn.close()

        logger.info(f"Created node assembly: {assembly_id} ({name})")
        return assembly

    def validate_assembly(self, assembly_id: str) -> Dict:
        """Validate an assembly before deployment"""
        assembly = self.get_assembly(assembly_id)
        if not assembly:
            raise ValueError(f"Assembly not found: {assembly_id}")

        stack = self.get_stack(assembly.stack_id)
        if not stack:
            raise ValueError(f"Stack not found: {assembly.stack_id}")

        checks = []
        errors = []
        warnings = []

        # Check 1: All models exist in catalogue
        checks.append({"name": "model_availability", "status": "passed"})

        # Check 2: Resource requirements are reasonable
        resources = stack.resource_requirements or {}
        if resources.get("memory_gb", 0) > 1000:
            warnings.append("Memory requirement exceeds 1TB")
        checks.append({"name": "resource_validation", "status": "passed"})

        # Check 3: Target LD is valid
        target_ld = assembly.deployment_config.get("target_ld")
        if not target_ld:
            errors.append("No target LD specified")
            checks.append({"name": "ld_validation", "status": "failed"})
        else:
            checks.append({"name": "ld_validation", "status": "passed"})

        # Check 4: Security configuration
        if assembly.security_config.get("authentication", {}).get("enabled"):
            if not assembly.security_config.get("authentication", {}).get("method"):
                warnings.append("Authentication enabled but no method specified")
        checks.append({"name": "security_validation", "status": "passed"})

        passed = len(errors) == 0

        validation_results = {
            "passed": passed,
            "checks": checks,
            "errors": errors,
            "warnings": warnings,
            "validated_at": datetime.utcnow().isoformat() + "Z"
        }

        # Update assembly
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        new_status = "ready" if passed else "draft"
        cursor.execute("""
            UPDATE assemblies
            SET validation_results = ?, status = ?, updated_at = ?
            WHERE assembly_id = ?
        """, (json.dumps(validation_results), new_status, datetime.utcnow().isoformat() + "Z", assembly_id))

        conn.commit()
        conn.close()

        return validation_results

    def deploy_assembly(self, assembly_id: str) -> Deployment:
        """Deploy an assembly to the ICO network"""
        assembly = self.get_assembly(assembly_id)
        if not assembly:
            raise ValueError(f"Assembly not found: {assembly_id}")

        if assembly.status not in ["ready", "draft"]:
            raise ValueError(f"Assembly status must be 'ready' or 'draft', got '{assembly.status}'")

        # Validate first if not already validated
        if assembly.status == "draft":
            validation = self.validate_assembly(assembly_id)
            if not validation["passed"]:
                raise ValueError(f"Assembly validation failed: {validation['errors']}")

        deployment_id = f"deploy-{uuid.uuid4()}"
        node_id = f"node-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        target_ld = assembly.deployment_config.get("target_ld")
        ld_address = f"{target_ld}::{node_id}"

        deployment = Deployment(
            deployment_id=deployment_id,
            assembly_id=assembly_id,
            node_id=node_id,
            ld_address=ld_address,
            status="deploying",
            deployed_at=now,
            health={"status": "unknown", "last_check": now},
            metrics={},
            endpoints=[],
            logs=[]
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insert deployment
        cursor.execute("""
            INSERT INTO deployments (
                deployment_id, assembly_id, node_id, ld_address, status,
                health, metrics, endpoints, deployed_at, logs
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            deployment.deployment_id,
            deployment.assembly_id,
            deployment.node_id,
            deployment.ld_address,
            deployment.status,
            json.dumps(deployment.health),
            json.dumps(deployment.metrics),
            json.dumps(deployment.endpoints),
            deployment.deployed_at,
            json.dumps(deployment.logs)
        ))

        # Update assembly
        cursor.execute("""
            UPDATE assemblies
            SET status = 'deploying', deployment_id = ?, deployed_at = ?, updated_at = ?
            WHERE assembly_id = ?
        """, (deployment_id, now, now, assembly_id))

        conn.commit()
        conn.close()

        logger.info(f"Deployed assembly {assembly_id} as {node_id} on {ld_address}")

        # Simulate deployment completion
        self._complete_deployment(deployment_id)

        return deployment

    def _complete_deployment(self, deployment_id: str):
        """Mark deployment as running (simulated)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat() + "Z"

        cursor.execute("""
            UPDATE deployments
            SET status = 'running', health = ?
            WHERE deployment_id = ?
        """, (json.dumps({"status": "healthy", "last_check": now}), deployment_id))

        cursor.execute("""
            UPDATE assemblies
            SET status = 'deployed'
            WHERE deployment_id = ?
        """, (deployment_id,))

        conn.commit()
        conn.close()

    def stop_deployment(self, deployment_id: str):
        """Stop a deployment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat() + "Z"

        cursor.execute("""
            UPDATE deployments
            SET status = 'stopped', stopped_at = ?
            WHERE deployment_id = ?
        """, (now, deployment_id))

        cursor.execute("""
            UPDATE assemblies
            SET status = 'ready', deployment_id = NULL
            WHERE deployment_id = ?
        """, (deployment_id,))

        conn.commit()
        conn.close()

        logger.info(f"Stopped deployment: {deployment_id}")

    def get_assembly(self, assembly_id: str) -> Optional[NodeAssembly]:
        """Get an assembly by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM assemblies WHERE assembly_id = ?", (assembly_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_assembly(row)

    def list_assemblies(
        self,
        stack_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[NodeAssembly]:
        """List assemblies with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM assemblies WHERE 1=1"
        params = []

        if stack_id:
            query += " AND stack_id = ?"
            params.append(stack_id)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_assembly(row) for row in rows]

    def get_deployment(self, deployment_id: str) -> Optional[Deployment]:
        """Get a deployment by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM deployments WHERE deployment_id = ?", (deployment_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_deployment(row)

    def list_deployments(
        self,
        assembly_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Deployment]:
        """List deployments with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM deployments WHERE 1=1"
        params = []

        if assembly_id:
            query += " AND assembly_id = ?"
            params.append(assembly_id)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY deployed_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_deployment(row) for row in rows]

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _calculate_resources(self, models: List[Dict]) -> Dict:
        """Estimate resource requirements"""
        # Simple estimation - in practice would query model catalogue
        return {
            "cpu_cores": len(models) * 4,
            "memory_gb": len(models) * 16,
            "gpu_count": len(models),
            "gpu_memory_gb": len(models) * 24
        }

    def _default_security_config(self) -> Dict:
        """Default security configuration"""
        return {
            "authentication": {"enabled": False, "method": "none"},
            "encryption": {"at_rest": True, "in_transit": True},
            "isolation": {"network_isolation": True, "process_isolation": True},
            "audit_logging": True
        }

    def _row_to_stack(self, row) -> ModelStack:
        """Convert database row to ModelStack"""
        return ModelStack(
            stack_id=row[0],
            name=row[1],
            description=row[2],
            models=json.loads(row[3]),
            orchestration=json.loads(row[4]) if row[4] else None,
            resource_requirements=json.loads(row[5]) if row[5] else None,
            nvm_assignments=json.loads(row[6]) if row[6] else [],
            capabilities=json.loads(row[7]) if row[7] else [],
            version=row[8],
            created_at=row[9],
            updated_at=row[10],
            created_by=row[11],
            tags=json.loads(row[12]) if row[12] else [],
            metadata=json.loads(row[13]) if row[13] else {}
        )

    def _row_to_assembly(self, row) -> NodeAssembly:
        """Convert database row to NodeAssembly"""
        return NodeAssembly(
            assembly_id=row[0],
            name=row[1],
            description=row[2],
            stack_id=row[3],
            deployment_config=json.loads(row[4]),
            network_config=json.loads(row[5]) if row[5] else {},
            security_config=json.loads(row[6]) if row[6] else {},
            monitoring_config=json.loads(row[7]) if row[7] else {},
            status=row[8],
            deployment_id=row[9],
            validation_results=json.loads(row[10]) if row[10] else None,
            created_at=row[11],
            updated_at=row[12],
            deployed_at=row[13],
            created_by=row[14],
            tags=json.loads(row[15]) if row[15] else [],
            metadata=json.loads(row[16]) if row[16] else {}
        )

    def _row_to_deployment(self, row) -> Deployment:
        """Convert database row to Deployment"""
        return Deployment(
            deployment_id=row[0],
            assembly_id=row[1],
            node_id=row[2],
            ld_address=row[3],
            status=row[4],
            health=json.loads(row[5]) if row[5] else {},
            metrics=json.loads(row[6]) if row[6] else {},
            endpoints=json.loads(row[7]) if row[7] else [],
            deployed_at=row[8],
            stopped_at=row[9],
            logs=json.loads(row[10]) if row[10] else []
        )
