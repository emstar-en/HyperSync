"""
Consensus Mechanism Selection API - Updated with Runtime Activation
Provides consensus mechanism selection with runtime activation and receipts.
"""
from typing import Dict, Any, Optional, List
from consensus.runtime_loader import activate_mechanism, deactivate_mechanism
from receipts.store import emit_receipt
import logging

logger = logging.getLogger(__name__)


def select_mechanism(
    tier: str,
    domain_type: str,
    requirements: Optional[Dict[str, Any]] = None,
    user_id: str = None,
    session_id: str = None
) -> Dict[str, Any]:
    """
    Select and activate consensus mechanism for given tier and domain.

    Args:
        tier: Service tier (FOUNDATION, PROFESSIONAL, etc.)
        domain_type: Domain type identifier
        requirements: Optional requirements dict (latency, throughput, etc.)
        user_id: User identifier for audit
        session_id: Session identifier

    Returns:
        Selected mechanism configuration and activation status
    """
    try:
        # Determine optimal mechanism
        mechanism_id, config = _determine_mechanism(tier, domain_type, requirements)

        # Activate mechanism in runtime
        activation_result = activate_mechanism(mechanism_id, config)

        # Emit audit receipt
        receipt_id = emit_receipt(
            event="consensus-selected",
            tier=tier,
            payload={
                "mechanism_id": mechanism_id,
                "domain_type": domain_type,
                "requirements": requirements or {},
                "config": config
            },
            result=activation_result,
            user_id=user_id,
            session_id=session_id,
            status="success" if activation_result["activated"] else "failed"
        )

        return {
            "success": True,
            "mechanism_id": mechanism_id,
            "mechanism_name": config.get("name"),
            "config": config,
            "activated": activation_result["activated"],
            "runtime_id": activation_result.get("runtime_id"),
            "receipt_id": receipt_id,
            "tier": tier
        }

    except Exception as e:
        logger.error(f"Consensus selection failed: {e}")

        # Emit failure receipt
        receipt_id = emit_receipt(
            event="consensus-selected",
            tier=tier,
            payload={
                "domain_type": domain_type,
                "requirements": requirements or {}
            },
            result={"error": str(e)},
            user_id=user_id,
            session_id=session_id,
            status="failed"
        )

        return {
            "success": False,
            "error": str(e),
            "receipt_id": receipt_id,
            "tier": tier
        }


def _determine_mechanism(
    tier: str,
    domain_type: str,
    requirements: Optional[Dict[str, Any]]
) -> tuple:
    """
    Determine optimal consensus mechanism based on tier and requirements.

    Returns:
        Tuple of (mechanism_id, config_dict)
    """
    # Tier-based mechanism mapping
    tier_mechanisms = {
        "FOUNDATION": "raft",
        "PROFESSIONAL": "pbft",
        "ENTERPRISE": "hotstuff",
        "RESEARCH": "tendermint",
        "CUSTOM": "custom-bft"
    }

    mechanism_id = tier_mechanisms.get(tier, "raft")

    # Build configuration
    config = {
        "name": mechanism_id.upper(),
        "tier": tier,
        "domain_type": domain_type,
        "fault_tolerance": _get_fault_tolerance(tier),
        "finality_time": _get_finality_time(tier, requirements),
        "throughput_target": _get_throughput_target(tier, requirements)
    }

    return mechanism_id, config


def _get_fault_tolerance(tier: str) -> str:
    """Get fault tolerance level for tier."""
    tolerance_map = {
        "FOUNDATION": "crash",
        "PROFESSIONAL": "byzantine-f1",
        "ENTERPRISE": "byzantine-f2",
        "RESEARCH": "byzantine-adaptive",
        "CUSTOM": "byzantine-configurable"
    }
    return tolerance_map.get(tier, "crash")


def _get_finality_time(tier: str, requirements: Optional[Dict]) -> int:
    """Get target finality time in milliseconds."""
    if requirements and "finality_ms" in requirements:
        return requirements["finality_ms"]

    defaults = {
        "FOUNDATION": 5000,
        "PROFESSIONAL": 2000,
        "ENTERPRISE": 1000,
        "RESEARCH": 500,
        "CUSTOM": 1000
    }
    return defaults.get(tier, 5000)


def _get_throughput_target(tier: str, requirements: Optional[Dict]) -> int:
    """Get target throughput in transactions per second."""
    if requirements and "throughput_tps" in requirements:
        return requirements["throughput_tps"]

    defaults = {
        "FOUNDATION": 100,
        "PROFESSIONAL": 500,
        "ENTERPRISE": 2000,
        "RESEARCH": 5000,
        "CUSTOM": 1000
    }
    return defaults.get(tier, 100)


def get_active_mechanisms(
    tier: Optional[str] = None,
    user_id: str = None,
    session_id: str = None
) -> Dict[str, Any]:
    """
    Get list of currently active consensus mechanisms.

    Args:
        tier: Optional tier filter
        user_id: User identifier
        session_id: Session identifier

    Returns:
        List of active mechanisms
    """
    from consensus.runtime_loader import get_active_runtimes

    try:
        active = get_active_runtimes(tier=tier)

        receipt_id = emit_receipt(
            event="consensus-query-active",
            tier=tier or "ALL",
            payload={"tier_filter": tier},
            result={"count": len(active)},
            user_id=user_id,
            session_id=session_id
        )

        return {
            "success": True,
            "active_mechanisms": active,
            "count": len(active),
            "receipt_id": receipt_id
        }

    except Exception as e:
        logger.error(f"Failed to query active mechanisms: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def deselect_mechanism(
    runtime_id: str,
    user_id: str = None,
    session_id: str = None
) -> Dict[str, Any]:
    """
    Deactivate a consensus mechanism runtime.

    Args:
        runtime_id: Runtime identifier to deactivate
        user_id: User identifier
        session_id: Session identifier

    Returns:
        Deactivation result
    """
    try:
        result = deactivate_mechanism(runtime_id)

        receipt_id = emit_receipt(
            event="consensus-deselected",
            tier="UNKNOWN",
            payload={"runtime_id": runtime_id},
            result=result,
            user_id=user_id,
            session_id=session_id
        )

        return {
            "success": True,
            "runtime_id": runtime_id,
            "deactivated": result["deactivated"],
            "receipt_id": receipt_id
        }

    except Exception as e:
        logger.error(f"Deactivation failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
