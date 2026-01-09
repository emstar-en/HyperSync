"""
HyperSync Initialization Assistant - Tools Bridge

Thin bridge layer that connects IAM tools to existing HyperSync modules.
Enforces policy checks and provides unified error handling.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import logging

# Import existing HyperSync modules
from hypersync.nvm.ld_manager import LDManager
from hypersync.nvm.ico_router import ICORouter
from hypersync.composition.composition_engine import CompositionEngine
from hypersync.security.policy_manager import PolicyManager

# Initialize module-level instances
_ldm = LDManager()
_router = ICORouter(_ldm)
_comp = CompositionEngine()
_policy = PolicyManager()
_logger = logging.getLogger(__name__)


class PolicyViolation(Exception):
    """Raised when an action violates policy"""
    pass


class NodeNotFound(Exception):
    """Raised when a node is not found"""
    pass


class DomainNotFound(Exception):
    """Raised when a domain is not found"""
    pass


class InvalidParameters(Exception):
    """Raised when parameters are invalid"""
    pass


def _enforce(action: str, payload: Dict[str, Any]) -> None:
    """
    Enforce policy check before executing action.

    Args:
        action: Action name (e.g., "create_ld")
        payload: Action parameters

    Raises:
        PolicyViolation: If action is not allowed
    """
    try:
        _policy.assert_allowed(action, payload)
    except Exception as e:
        _logger.error(f"Policy violation for {action}: {e}")
        raise PolicyViolation(f"Action '{action}' not allowed by policy") from e


def _validate_required(payload: Dict[str, Any], required: List[str]) -> None:
    """
    Validate required parameters are present.

    Args:
        payload: Parameters dict
        required: List of required parameter names

    Raises:
        InvalidParameters: If required parameter is missing
    """
    for param in required:
        if param not in payload or payload[param] is None:
            raise InvalidParameters(f"Missing required parameter: {param}")


def create_ld(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new Lorentzian Domain.

    Args:
        payload: {
            "name": str (required),
            "security_level": str (optional, default: "isolated"),
            "dimension": int (optional, default: 4),
            "curvature": float (optional, default: 0.0),
            "metric_type": str (optional, default: "minkowski")
        }

    Returns:
        {"ld_id": str, "name": str}

    Raises:
        PolicyViolation: If action not allowed
        InvalidParameters: If required parameters missing
    """
    _validate_required(payload, ["name"])
    _enforce("create_ld", payload)

    try:
        ld = _ldm.create_domain(
            name=payload["name"],
            security_level=payload.get("security_level", "isolated"),
            dimension=payload.get("dimension", 4),
            curvature=payload.get("curvature", 0.0),
            metric_type=payload.get("metric_type", "minkowski")
        )

        _logger.info(f"Created LD: {ld.ld_id} ({ld.name})")
        return {"ld_id": ld.ld_id, "name": ld.name}

    except Exception as e:
        _logger.error(f"Failed to create LD: {e}")
        raise


def register_node(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register a node in a Lorentzian Domain.

    Args:
        payload: {
            "ld_id": str (required),
            "node_id": str (required),
            "address_type": str (optional, default: "model"),
            "coordinates": dict (optional, default: origin)
        }

    Returns:
        {"node_id": str, "ld_id": str}

    Raises:
        PolicyViolation: If action not allowed
        InvalidParameters: If required parameters missing
        DomainNotFound: If domain doesn't exist
    """
    _validate_required(payload, ["ld_id", "node_id"])
    _enforce("register_node", payload)

    try:
        nid = payload["node_id"]
        ld_id = payload["ld_id"]
        coords = payload.get("coordinates") or {"t": 0, "x": 0, "y": 0, "z": 0}
        address_type = payload.get("address_type", "model")

        _router.register_node(
            ld_id=ld_id,
            node_id=nid,
            coordinates=coords,
            address_type=address_type
        )

        _logger.info(f"Registered node: {nid} in LD {ld_id}")
        return {"node_id": nid, "ld_id": ld_id}

    except KeyError as e:
        raise DomainNotFound(f"Domain {ld_id} not found") from e
    except Exception as e:
        _logger.error(f"Failed to register node: {e}")
        raise


def compute_route(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute a route between two nodes.

    Args:
        payload: {
            "src": str (required),
            "dst": str (required),
            "constraints": dict (optional)
        }

    Returns:
        {"path": List[str]}

    Raises:
        PolicyViolation: If action not allowed
        InvalidParameters: If required parameters missing
        NodeNotFound: If source or destination not found
    """
    _validate_required(payload, ["src", "dst"])
    _enforce("compute_route", payload)

    try:
        path = _router.compute_route(
            src=payload["src"],
            dst=payload["dst"],
            constraints=payload.get("constraints")
        )

        _logger.info(f"Computed route: {payload['src']} -> {payload['dst']}")
        return {"path": path}

    except KeyError as e:
        raise NodeNotFound(f"Node not found: {e}") from e
    except Exception as e:
        _logger.error(f"Failed to compute route: {e}")
        raise


def catalog_models(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Catalog model descriptors from .hypersync/models/.

    Args:
        payload: {} (no parameters required)

    Returns:
        {"count": int, "models": List[dict]}

    Raises:
        PolicyViolation: If action not allowed
    """
    _enforce("catalog_models", payload)

    try:
        models_dir = Path(".hypersync/models")
        models_dir.mkdir(parents=True, exist_ok=True)

        found: List[Dict[str, Any]] = []
        for p in models_dir.glob("*.json"):
            try:
                meta = json.loads(p.read_text(encoding="utf-8"))
                if "name" in meta:  # Validate minimum required fields
                    found.append(meta)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                _logger.warning(f"Skipping invalid descriptor {p.name}: {e}")
                continue

        _logger.info(f"Cataloged {len(found)} models")
        return {"count": len(found), "models": found}

    except Exception as e:
        _logger.error(f"Failed to catalog models: {e}")
        raise


def compose_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compose a network operator agent from multiple models.

    Args:
        payload: {
            "name": str (required),
            "capabilities": List[str] (required),
            "members": List[str] (required),
            "ld_id": str (optional, uses default if not specified)
        }

    Returns:
        {"agent_id": str, "ld_id": str}

    Raises:
        PolicyViolation: If action not allowed
        InvalidParameters: If required parameters missing
    """
    _validate_required(payload, ["name", "capabilities", "members"])
    _enforce("compose_agent", payload)

    try:
        agent_id = _comp.compose({
            "name": payload["name"],
            "capabilities": payload["capabilities"],
            "members": payload["members"]
        })

        # Register agent as a node
        ld_id = payload.get("ld_id") or _ldm.default_domain_id()
        _router.register_node(
            ld_id=ld_id,
            node_id=agent_id,
            coordinates={"t": 0, "x": 0, "y": 0, "z": 0},
            address_type="agent"
        )

        _logger.info(f"Composed agent: {agent_id} in LD {ld_id}")
        return {"agent_id": agent_id, "ld_id": ld_id}

    except Exception as e:
        _logger.error(f"Failed to compose agent: {e}")
        raise


def status_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a summary of the current HyperSync environment.

    Args:
        payload: {} (no parameters required)

    Returns:
        {
            "domains": List[{"ld_id": str, "name": str, "node_count": int}],
            "total_nodes": int,
            "total_agents": int
        }

    Raises:
        PolicyViolation: If action not allowed
    """
    _enforce("status_summary", payload)

    try:
        domains = []
        total_nodes = 0
        total_agents = 0

        for ld in _ldm.list_domains():
            nodes = _router.list_nodes(ld.ld_id)
            node_count = len(nodes)
            agent_count = sum(1 for n in nodes if n.get("address_type") == "agent")

            domains.append({
                "ld_id": ld.ld_id,
                "name": ld.name,
                "node_count": node_count
            })

            total_nodes += node_count
            total_agents += agent_count

        _logger.info(f"Status: {len(domains)} domains, {total_nodes} nodes, {total_agents} agents")
        return {
            "domains": domains,
            "total_nodes": total_nodes,
            "total_agents": total_agents
        }

    except Exception as e:
        _logger.error(f"Failed to get status: {e}")
        raise


# Export all tool functions
__all__ = [
    "create_ld",
    "register_node",
    "compute_route",
    "catalog_models",
    "compose_agent",
    "status_summary",
    "PolicyViolation",
    "NodeNotFound",
    "DomainNotFound",
    "InvalidParameters"
]
