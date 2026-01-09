"""
Mutation Workflows - Validate and execute agent write requests.

Auto-generates schema if absent, requires policy approvals, and maintains
audit logs with before/after snapshots.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio


class MutationStatus(Enum):
    """Mutation request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


@dataclass
class MutationRequest:
    """Agent mutation request."""
    request_id: str
    agent_id: str
    relation: str
    operation: str  # insert, update, delete
    data: Dict[str, Any]
    filters: Optional[Dict[str, Any]]
    status: MutationStatus
    created_at: datetime
    executed_at: Optional[datetime] = None


@dataclass
class AuditLog:
    """Mutation audit log entry."""
    log_id: str
    request_id: str
    agent_id: str
    relation: str
    operation: str
    before_snapshot: Optional[Dict[str, Any]]
    after_snapshot: Optional[Dict[str, Any]]
    timestamp: datetime


class MutationPipeline:
    """
    Mutation workflow manager for agent write operations.

    Validates requests, enforces policies, auto-generates schemas,
    and maintains comprehensive audit logs.
    """

    def __init__(self, require_approval: bool = True):
        self.require_approval = require_approval
        self.pending_requests: Dict[str, MutationRequest] = {}
        self.audit_logs: List[AuditLog] = []
        self.schema_registry: Dict[str, Dict[str, Any]] = {}

    async def submit_mutation(
        self,
        agent_id: str,
        relation: str,
        operation: str,
        data: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None
    ) -> MutationRequest:
        """
        Submit mutation request for processing.

        Args:
            agent_id: Agent identifier
            relation: Target relation
            operation: Mutation operation (insert/update/delete)
            data: Mutation data
            filters: Optional filters for update/delete

        Returns:
            MutationRequest with status
        """
        request_id = f"mut_{agent_id}_{int(datetime.now().timestamp())}"

        request = MutationRequest(
            request_id=request_id,
            agent_id=agent_id,
            relation=relation,
            operation=operation,
            data=data,
            filters=filters,
            status=MutationStatus.PENDING,
            created_at=datetime.now()
        )

        # Validate request
        validation_result = await self._validate_request(request)
        if not validation_result["valid"]:
            request.status = MutationStatus.REJECTED
            return request

        # Check if schema exists, auto-generate if needed
        if relation not in self.schema_registry:
            await self._auto_generate_schema(relation, data)

        # Store pending request
        self.pending_requests[request_id] = request

        # If approval not required, execute immediately
        if not self.require_approval:
            await self.execute_mutation(request_id)

        return request

    async def approve_mutation(self, request_id: str) -> bool:
        """
        Approve pending mutation request.

        Args:
            request_id: Request identifier

        Returns:
            True if approved and executed successfully
        """
        if request_id not in self.pending_requests:
            return False

        request = self.pending_requests[request_id]
        request.status = MutationStatus.APPROVED

        return await self.execute_mutation(request_id)

    async def reject_mutation(self, request_id: str, reason: str) -> bool:
        """
        Reject pending mutation request.

        Args:
            request_id: Request identifier
            reason: Rejection reason

        Returns:
            True if rejected successfully
        """
        if request_id not in self.pending_requests:
            return False

        request = self.pending_requests[request_id]
        request.status = MutationStatus.REJECTED

        # Log rejection
        await self._create_audit_log(request, None, None, {"rejection_reason": reason})

        return True

    async def execute_mutation(self, request_id: str) -> bool:
        """
        Execute approved mutation request.

        Args:
            request_id: Request identifier

        Returns:
            True if executed successfully
        """
        if request_id not in self.pending_requests:
            return False

        request = self.pending_requests[request_id]

        # Capture before snapshot
        before_snapshot = await self._capture_snapshot(request)

        try:
            # Execute mutation
            if request.operation == "insert":
                await self._execute_insert(request)
            elif request.operation == "update":
                await self._execute_update(request)
            elif request.operation == "delete":
                await self._execute_delete(request)

            # Capture after snapshot
            after_snapshot = await self._capture_snapshot(request)

            # Update status
            request.status = MutationStatus.EXECUTED
            request.executed_at = datetime.now()

            # Create audit log
            await self._create_audit_log(request, before_snapshot, after_snapshot)

            return True

        except Exception as e:
            request.status = MutationStatus.FAILED
            await self._create_audit_log(request, before_snapshot, None, {"error": str(e)})
            return False

    async def get_audit_logs(
        self,
        agent_id: Optional[str] = None,
        relation: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Retrieve audit logs with optional filters.

        Args:
            agent_id: Filter by agent ID
            relation: Filter by relation
            limit: Maximum number of logs

        Returns:
            List of audit logs
        """
        logs = self.audit_logs

        if agent_id:
            logs = [log for log in logs if log.agent_id == agent_id]

        if relation:
            logs = [log for log in logs if log.relation == relation]

        return logs[-limit:]

    async def _validate_request(self, request: MutationRequest) -> Dict[str, Any]:
        """Validate mutation request."""
        # Check if relation exists or can be created
        if request.operation in ["update", "delete"] and request.relation not in self.schema_registry:
            return {"valid": False, "reason": "Relation does not exist"}

        # Validate data structure
        if not request.data and request.operation != "delete":
            return {"valid": False, "reason": "No data provided"}

        return {"valid": True}

    async def _auto_generate_schema(self, relation: str, sample_data: Dict[str, Any]) -> None:
        """Auto-generate schema from sample data."""
        schema = {
            "relation": relation,
            "fields": {},
            "auto_generated": True,
            "created_at": datetime.now()
        }

        # Infer field types from sample data
        for key, value in sample_data.items():
            schema["fields"][key] = {
                "type": type(value).__name__,
                "nullable": True
            }

        self.schema_registry[relation] = schema

    async def _capture_snapshot(self, request: MutationRequest) -> Optional[Dict[str, Any]]:
        """Capture data snapshot before/after mutation."""
        if request.operation == "insert":
            return None  # No before snapshot for inserts

        # Simulate snapshot capture
        return {
            "relation": request.relation,
            "filters": request.filters,
            "timestamp": datetime.now()
        }

    async def _execute_insert(self, request: MutationRequest) -> None:
        """Execute insert operation."""
        await asyncio.sleep(0.01)  # Simulate DB operation

    async def _execute_update(self, request: MutationRequest) -> None:
        """Execute update operation."""
        await asyncio.sleep(0.01)

    async def _execute_delete(self, request: MutationRequest) -> None:
        """Execute delete operation."""
        await asyncio.sleep(0.01)

    async def _create_audit_log(
        self,
        request: MutationRequest,
        before: Optional[Dict[str, Any]],
        after: Optional[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create audit log entry."""
        log_id = f"log_{request.request_id}_{int(datetime.now().timestamp())}"

        log = AuditLog(
            log_id=log_id,
            request_id=request.request_id,
            agent_id=request.agent_id,
            relation=request.relation,
            operation=request.operation,
            before_snapshot=before,
            after_snapshot=after,
            timestamp=datetime.now()
        )

        self.audit_logs.append(log)
