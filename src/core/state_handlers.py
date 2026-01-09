"""
Panel State Handlers - Receive data from adapters and update panel state.

These handlers act as the bridge between data adapters and UI panels.
They transform raw telemetry data into panel-ready state.
"""
import logging
from typing import Any, Dict
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


# Shared state storage (in production, this would be a proper state manager)
_panel_state: Dict[str, Any] = {
    "anchor": {},
    "geodesic": {},
    "curvature": {},
    "boundary": {},
    "metrics": {}
}


def get_panel_state(panel_id: str) -> Dict[str, Any]:
    """Get current state for a panel."""
    return _panel_state.get(panel_id, {})


async def anchor_state_handler(data: Dict[str, Any]) -> None:
    """
    Handle anchor telemetry data.

    Args:
        data: Anchor data from AnchorAdapter
            Expected keys: anchors, total_count, active_count, timestamp
    """
    try:
        _panel_state["anchor"] = {
            "anchors": data.get("anchors", []),
            "total_count": data.get("total_count", 0),
            "active_count": data.get("active_count", 0),
            "last_update": datetime.now().isoformat(),
            "raw_data": data
        }
        logger.debug(f"Updated anchor state: {_panel_state['anchor']['total_count']} anchors")
    except Exception as e:
        logger.error(f"Error in anchor_state_handler: {e}")


async def geodesic_state_handler(data: Dict[str, Any]) -> None:
    """
    Handle geodesic activity data.

    Args:
        data: Geodesic data from GeodesicAdapter
            Expected keys: paths, active_routes, throughput, timestamp
    """
    try:
        _panel_state["geodesic"] = {
            "paths": data.get("paths", []),
            "active_routes": data.get("active_routes", 0),
            "throughput": data.get("throughput", 0.0),
            "last_update": datetime.now().isoformat(),
            "raw_data": data
        }
        logger.debug(f"Updated geodesic state: {_panel_state['geodesic']['active_routes']} routes")
    except Exception as e:
        logger.error(f"Error in geodesic_state_handler: {e}")


async def curvature_state_handler(data: Dict[str, Any]) -> None:
    """
    Handle curvature field data.

    Args:
        data: Curvature data from CurvatureAdapter
            Expected keys: curvature_map, ricci_flow, avg_curvature, timestamp
    """
    try:
        _panel_state["curvature"] = {
            "curvature_map": data.get("curvature_map", {}),
            "ricci_flow": data.get("ricci_flow", []),
            "avg_curvature": data.get("avg_curvature", 0.0),
            "last_update": datetime.now().isoformat(),
            "raw_data": data
        }
        logger.debug(f"Updated curvature state: avg={_panel_state['curvature']['avg_curvature']:.4f}")
    except Exception as e:
        logger.error(f"Error in curvature_state_handler: {e}")


async def boundary_state_handler(data: Dict[str, Any]) -> None:
    """
    Handle boundary condition data (aggregates from multiple sources).

    Args:
        data: Data from any adapter that affects boundary conditions
    """
    try:
        # Initialize if needed
        if "boundary_events" not in _panel_state["boundary"]:
            _panel_state["boundary"]["boundary_events"] = []

        # Extract boundary-relevant information
        if "anchors" in data:
            # Check for anchors near boundary
            boundary_anchors = [
                a for a in data["anchors"]
                if a.get("distance_to_boundary", float('inf')) < 0.1
            ]
            if boundary_anchors:
                _panel_state["boundary"]["boundary_events"].append({
                    "type": "anchor_near_boundary",
                    "count": len(boundary_anchors),
                    "timestamp": datetime.now().isoformat()
                })

        if "paths" in data:
            # Check for geodesics crossing boundary
            boundary_paths = [
                p for p in data["paths"]
                if p.get("crosses_boundary", False)
            ]
            if boundary_paths:
                _panel_state["boundary"]["boundary_events"].append({
                    "type": "geodesic_boundary_crossing",
                    "count": len(boundary_paths),
                    "timestamp": datetime.now().isoformat()
                })

        # Keep only recent events (last 100)
        _panel_state["boundary"]["boundary_events"] =             _panel_state["boundary"]["boundary_events"][-100:]

        _panel_state["boundary"]["last_update"] = datetime.now().isoformat()

    except Exception as e:
        logger.error(f"Error in boundary_state_handler: {e}")


async def metrics_state_handler(data: Dict[str, Any]) -> None:
    """
    Handle system metrics (aggregates from multiple sources).

    Args:
        data: Data from any adapter that contributes to metrics
    """
    try:
        # Initialize metrics if needed
        if "metrics" not in _panel_state["metrics"]:
            _panel_state["metrics"]["metrics"] = {
                "total_anchors": 0,
                "total_geodesics": 0,
                "avg_curvature": 0.0,
                "throughput": 0.0,
                "uptime": 0.0
            }

        metrics = _panel_state["metrics"]["metrics"]

        # Update from various sources
        if "total_count" in data:
            metrics["total_anchors"] = data["total_count"]

        if "active_routes" in data:
            metrics["total_geodesics"] = data["active_routes"]

        if "throughput" in data:
            metrics["throughput"] = data["throughput"]

        if "avg_curvature" in data:
            metrics["avg_curvature"] = data["avg_curvature"]

        _panel_state["metrics"]["last_update"] = datetime.now().isoformat()

        logger.debug(f"Updated metrics state: {metrics}")

    except Exception as e:
        logger.error(f"Error in metrics_state_handler: {e}")
