"""
Governance Manager

Manages approval workflows, policy enforcement, and audit trails.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json


class ApprovalStatus(str, Enum):
    """Approval request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    """Approval request for governance."""
    request_id: str
    resource_type: str
    resource_id: str
    operation: str
    requestor: str
    approvers: List[str]
    justification: str
    timeout: int = 3600
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: ApprovalStatus = ApprovalStatus.PENDING
    approvals: List[Dict[str, Any]] = field(default_factory=list)

    def is_expired(self) -> bool:
        """Check if request has expired."""
        expiry = self.created_at + timedelta(seconds=self.timeout)
        return datetime.utcnow() > expiry

    def is_approved(self) -> bool:
        """Check if request is fully approved."""
        if self.status != ApprovalStatus.PENDING:
            return self.status == ApprovalStatus.APPROVED

        approved_by = {a["approver"] for a in self.approvals if a["approved"]}
        return len(approved_by) >= len(self.approvers)


class GovernanceManager:
    """
    Manages governance workflows.

    Responsibilities:
    - Approval request management
    - Policy enforcement
    - Audit trail generation
    - Compliance reporting
    """

    def __init__(self):
        self.requests: Dict[str, ApprovalRequest] = {}
        self.audit_log: List[Dict[str, Any]] = []

    def submit_approval_request(self, request: ApprovalRequest) -> str:
        """Submit approval request."""
        self.requests[request.request_id] = request

        self._log_audit_event(
            "approval_request_submitted",
            request.resource_id,
            {"requestor": request.requestor, "operation": request.operation}
        )

        return request.request_id

    def approve(self, request_id: str, approver: str, comment: str = "") -> bool:
        """Approve a request."""
        request = self.requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False

        if approver not in request.approvers:
            return False

        # Add approval
        request.approvals.append({
            "approver": approver,
            "approved": True,
            "timestamp": datetime.utcnow().isoformat(),
            "comment": comment
        })

        # Check if fully approved
        if request.is_approved():
            request.status = ApprovalStatus.APPROVED
            self._log_audit_event(
                "approval_request_approved",
                request.resource_id,
                {"approver": approver}
            )

        return True

    def reject(self, request_id: str, approver: str, reason: str) -> bool:
        """Reject a request."""
        request = self.requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False

        if approver not in request.approvers:
            return False

        request.status = ApprovalStatus.REJECTED
        request.approvals.append({
            "approver": approver,
            "approved": False,
            "timestamp": datetime.utcnow().isoformat(),
            "comment": reason
        })

        self._log_audit_event(
            "approval_request_rejected",
            request.resource_id,
            {"approver": approver, "reason": reason}
        )

        return True

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get approval request."""
        return self.requests.get(request_id)

    def list_pending_requests(self, approver: Optional[str] = None) -> List[ApprovalRequest]:
        """List pending approval requests."""
        pending = [r for r in self.requests.values() if r.status == ApprovalStatus.PENDING]

        if approver:
            pending = [r for r in pending if approver in r.approvers]

        return pending

    def _log_audit_event(self, event_type: str, resource_id: str, metadata: Dict[str, Any]):
        """Log audit event."""
        event = {
            "event_type": event_type,
            "resource_id": resource_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata
        }
        self.audit_log.append(event)

    def get_audit_log(self, resource_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit log."""
        if resource_id:
            return [e for e in self.audit_log if e["resource_id"] == resource_id]
        return self.audit_log


# Global instance
_governance_manager: Optional[GovernanceManager] = None


def get_governance_manager() -> GovernanceManager:
    """Get global governance manager."""
    global _governance_manager
    if _governance_manager is None:
        _governance_manager = GovernanceManager()
    return _governance_manager
