"""
HyperSync Local Dimensional Profile Module

Provides deterministic hyperbolic dimensional defaults and calibration flows
for standalone stacks (agents + nodes on a single machine).
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import math


@dataclass
class DimensionalPreset:
    """Predefined dimensional configuration preset."""
    name: str
    base_dimensions: int
    max_dimensions: int
    default_curvature: float
    description: str
    use_cases: List[str]


class CurvatureGuard:
    """Validates and enforces curvature stability constraints."""

    def __init__(self, min_curvature: float = -1.0, max_curvature: float = -0.1,
                 stability_threshold: float = 0.95):
        self.min_curvature = min_curvature
        self.max_curvature = max_curvature
        self.stability_threshold = stability_threshold
        self.history: List[Tuple[float, float]] = []  # (timestamp, curvature)

    def validate(self, curvature: float) -> Tuple[bool, Optional[str]]:
        """
        Validate proposed curvature value.

        Returns:
            (is_valid, error_message)
        """
        if not (-1.0 <= curvature <= 0.0):
            return False, f"Curvature must be in hyperbolic range [-1.0, 0.0], got {curvature}"

        if not (self.min_curvature <= curvature <= self.max_curvature):
            return False, f"Curvature {curvature} outside policy bounds [{self.min_curvature}, {self.max_curvature}]"

        # Check stability if we have history
        if len(self.history) >= 2:
            recent_variance = self._compute_variance(window=5)
            if recent_variance > (1.0 - self.stability_threshold):
                return False, f"Curvature change would exceed stability threshold (variance: {recent_variance:.3f})"

        return True, None

    def record(self, curvature: float):
        """Record curvature value in history."""
        self.history.append((datetime.now().timestamp(), curvature))
        # Keep last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]

    def _compute_variance(self, window: int = 5) -> float:
        """Compute variance of recent curvature values."""
        if len(self.history) < 2:
            return 0.0

        recent = [c for _, c in self.history[-window:]]
        mean = sum(recent) / len(recent)
        variance = sum((c - mean) ** 2 for c in recent) / len(recent)
        return math.sqrt(variance)

    def get_stability_score(self) -> float:
        """Get current stability score (0.0 = unstable, 1.0 = stable)."""
        if len(self.history) < 2:
            return 1.0

        variance = self._compute_variance()
        return max(0.0, 1.0 - variance)


class LocalDimensionalProfile:
    """
    Manages dimensional configuration for a local HyperSync stack.

    Provides preset configurations, curvature management, and persistence.
    """

    # Predefined presets
    PRESETS = {
        "minimal": DimensionalPreset(
            name="minimal",
            base_dimensions=2,
            max_dimensions=4,
            default_curvature=-0.5,
            description="Minimal dimensional space for basic operations",
            use_cases=["development", "testing", "resource-constrained environments"]
        ),
        "standard": DimensionalPreset(
            name="standard",
            base_dimensions=4,
            max_dimensions=8,
            default_curvature=-0.75,
            description="Standard configuration for production workloads",
            use_cases=["production", "general purpose", "balanced performance"]
        ),
        "extended": DimensionalPreset(
            name="extended",
            base_dimensions=6,
            max_dimensions=12,
            default_curvature=-0.85,
            description="Extended dimensional space for complex routing",
            use_cases=["multi-agent systems", "complex workflows", "high-dimensional data"]
        ),
        "research": DimensionalPreset(
            name="research",
            base_dimensions=8,
            max_dimensions=16,
            default_curvature=-0.95,
            description="Maximum dimensional space for research and experimentation",
            use_cases=["research", "experimentation", "advanced analytics"]
        )
    }

    def __init__(self, stack_id: str, preset: str = "standard"):
        self.stack_id = stack_id
        self.preset_name = preset
        self.preset = self.PRESETS.get(preset, self.PRESETS["standard"])

        self.base_dimensions = self.preset.base_dimensions
        self.max_dimensions = self.preset.max_dimensions
        self.curvature = self.preset.default_curvature

        self.curvature_guard = CurvatureGuard(
            min_curvature=-1.0,
            max_curvature=-0.1,
            stability_threshold=0.95
        )

        self.agent_bindings: Dict[str, Dict] = {}
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }

    @classmethod
    def load_default(cls, stack: str = "core") -> "LocalDimensionalProfile":
        """
        Load default profile for a given stack type.

        Args:
            stack: Stack identifier (e.g., "core", "dev", "prod")

        Returns:
            LocalDimensionalProfile instance
        """
        preset_map = {
            "core": "standard",
            "dev": "minimal",
            "prod": "standard",
            "research": "research"
        }

        preset = preset_map.get(stack, "standard")
        return cls(stack_id=stack, preset=preset)

    @classmethod
    def load_from_file(cls, path: str) -> "LocalDimensionalProfile":
        """Load profile from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)

        profile = cls(
            stack_id=data["stack_id"],
            preset=data["dimensional_config"]["preset"]
        )

        # Override with saved values
        profile.base_dimensions = data["dimensional_config"]["base_dimensions"]
        profile.max_dimensions = data["dimensional_config"]["max_dimensions"]
        profile.curvature = data["curvature_policy"]["default_curvature"]
        profile.agent_bindings = {
            binding["agent_id"]: binding 
            for binding in data.get("agent_bindings", [])
        }
        profile.metadata = data.get("metadata", profile.metadata)

        return profile

    def apply(self, curvature: Optional[float] = None, 
              max_dims: Optional[int] = None) -> bool:
        """
        Apply dimensional configuration changes.

        Args:
            curvature: New curvature value (optional)
            max_dims: New maximum dimensions (optional)

        Returns:
            True if changes applied successfully
        """
        if curvature is not None:
            is_valid, error = self.curvature_guard.validate(curvature)
            if not is_valid:
                raise ValueError(f"Invalid curvature: {error}")

            self.curvature = curvature
            self.curvature_guard.record(curvature)

        if max_dims is not None:
            if not (2 <= max_dims <= 16):
                raise ValueError(f"max_dims must be in range [2, 16], got {max_dims}")
            self.max_dimensions = max_dims

        self.metadata["updated_at"] = datetime.now().isoformat()
        return True

    def bind_agent(self, agent_id: str, dimensions: int, 
                   curvature_override: Optional[float] = None):
        """
        Bind agent-specific dimensional configuration.

        Args:
            agent_id: Agent identifier
            dimensions: Number of dimensions for this agent
            curvature_override: Optional curvature override
        """
        if not (2 <= dimensions <= self.max_dimensions):
            raise ValueError(
                f"Agent dimensions must be in range [2, {self.max_dimensions}], got {dimensions}"
            )

        binding = {
            "agent_id": agent_id,
            "dimensions": dimensions
        }

        if curvature_override is not None:
            is_valid, error = self.curvature_guard.validate(curvature_override)
            if not is_valid:
                raise ValueError(f"Invalid curvature override: {error}")
            binding["curvature_override"] = curvature_override

        self.agent_bindings[agent_id] = binding
        self.metadata["updated_at"] = datetime.now().isoformat()

    def get_agent_config(self, agent_id: str) -> Dict:
        """Get dimensional configuration for a specific agent."""
        if agent_id in self.agent_bindings:
            binding = self.agent_bindings[agent_id]
            return {
                "dimensions": binding["dimensions"],
                "curvature": binding.get("curvature_override", self.curvature)
            }

        return {
            "dimensions": self.base_dimensions,
            "curvature": self.curvature
        }

    def persist(self, path: str):
        """
        Persist profile to JSON file.

        Args:
            path: File path (e.g., ~/.hypersync/dimensional/local.json)
        """
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": self.metadata["version"],
            "stack_id": self.stack_id,
            "dimensional_config": {
                "base_dimensions": self.base_dimensions,
                "max_dimensions": self.max_dimensions,
                "preset": self.preset_name
            },
            "curvature_policy": {
                "default_curvature": self.curvature,
                "bounds": {
                    "min": self.curvature_guard.min_curvature,
                    "max": self.curvature_guard.max_curvature
                },
                "stability_threshold": self.curvature_guard.stability_threshold,
                "auto_calibrate": False
            },
            "agent_bindings": list(self.agent_bindings.values()),
            "metadata": self.metadata
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_stability_report(self) -> Dict:
        """Generate stability report for current configuration."""
        return {
            "stack_id": self.stack_id,
            "stability_score": self.curvature_guard.get_stability_score(),
            "current_curvature": self.curvature,
            "dimensions": {
                "base": self.base_dimensions,
                "max": self.max_dimensions
            },
            "agent_count": len(self.agent_bindings),
            "history_size": len(self.curvature_guard.history)
        }

    def __repr__(self) -> str:
        return (
            f"LocalDimensionalProfile(stack={self.stack_id}, "
            f"preset={self.preset_name}, dims={self.base_dimensions}/{self.max_dimensions}, "
            f"curvature={self.curvature:.3f})"
        )
