#!/usr/bin/env python3
"""
HyperSync Privacy Geometry System
Manages tenant region partitioning and isolation
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class TenantRegion:
    region_id: str
    tenant_id: str
    center_coords: Tuple[float, float, float]  # (r, theta, phi) in B3
    radius: float
    capacity: int
    current_devices: int

class PrivacyGeometrySystem:
    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)
        self.min_separation = self.config['tenant_region_partitioning']['min_separation_dH']
        self.buffer_eps = self.config['tenant_region_partitioning']['buffer_eps']
        self.max_tenants_per_region = self.config['tenant_region_partitioning']['max_tenants_per_region']
        self.regions: Dict[str, TenantRegion] = {}

    def _load_config(self, path: Path) -> Dict:
        """Load privacy geometry configuration"""
        with open(path, 'r') as f:
            return json.load(f)

    def hyperbolic_distance(self, p1: Tuple[float, float, float], 
                           p2: Tuple[float, float, float]) -> float:
        """
        Calculate hyperbolic distance in Poincaré ball B3

        dH(p1, p2) = arcosh(1 + 2 * ||p1 - p2||^2 / ((1 - ||p1||^2)(1 - ||p2||^2)))
        """
        p1_arr = np.array(p1)
        p2_arr = np.array(p2)

        diff = p1_arr - p2_arr
        diff_norm_sq = np.dot(diff, diff)

        p1_norm_sq = np.dot(p1_arr, p1_arr)
        p2_norm_sq = np.dot(p2_arr, p2_arr)

        numerator = 2 * diff_norm_sq
        denominator = (1 - p1_norm_sq) * (1 - p2_norm_sq)

        if denominator <= 0:
            return float('inf')

        arg = 1 + numerator / denominator
        if arg < 1:
            return 0.0

        return np.arccosh(arg)

    def validate_separation(self, new_coords: Tuple[float, float, float], 
                          tenant_id: str) -> bool:
        """
        Validate that new region maintains minimum separation
        """
        for region in self.regions.values():
            if region.tenant_id == tenant_id:
                continue  # Same tenant can be closer

            distance = self.hyperbolic_distance(new_coords, region.center_coords)

            if distance < self.min_separation:
                return False

        return True

    def assign_device_to_region(self, device_id: str, tenant_id: str) -> Optional[str]:
        """
        Assign device to appropriate tenant region

        Returns region_id or None if assignment fails
        """
        # Find regions for this tenant
        tenant_regions = [r for r in self.regions.values() if r.tenant_id == tenant_id]

        # Find region with capacity
        for region in tenant_regions:
            if region.current_devices < region.capacity:
                region.current_devices += 1
                return region.region_id

        # No capacity, would need to create new region
        return None

    def validate_cross_tenant_transfer(self, source_region_id: str, 
                                      target_region_id: str,
                                      warrant_id: str) -> bool:
        """
        Validate cross-tenant transfer with warrant
        """
        if source_region_id not in self.regions or target_region_id not in self.regions:
            return False

        source_region = self.regions[source_region_id]
        target_region = self.regions[target_region_id]

        # Check if different tenants
        if source_region.tenant_id == target_region.tenant_id:
            return True  # Same tenant, no warrant needed

        # Different tenants, warrant required
        if not warrant_id:
            return False

        # Would validate warrant here
        return True

    def get_region_isolation_status(self, region_id: str) -> Dict:
        """Get isolation status for region"""
        if region_id not in self.regions:
            return {"error": "Region not found"}

        region = self.regions[region_id]

        # Calculate minimum distance to other tenant regions
        min_distance = float('inf')
        for other_region in self.regions.values():
            if other_region.region_id == region_id:
                continue
            if other_region.tenant_id == region.tenant_id:
                continue

            distance = self.hyperbolic_distance(region.center_coords, other_region.center_coords)
            min_distance = min(min_distance, distance)

        return {
            "region_id": region_id,
            "tenant_id": region.tenant_id,
            "min_separation_to_other_tenants": min_distance,
            "required_separation": self.min_separation,
            "isolation_valid": min_distance >= self.min_separation,
            "current_devices": region.current_devices,
            "capacity": region.capacity
        }

# Example usage
if __name__ == "__main__":
    privacy_system = PrivacyGeometrySystem(Path("config/privacy_geometry.json"))

    # Example: validate separation
    coords1 = (0.1, 0.0, 0.0)
    coords2 = (0.6, 0.0, 0.0)

    distance = privacy_system.hyperbolic_distance(coords1, coords2)
    print(f"Hyperbolic distance: {distance:.4f}")
    print(f"Separation valid: {distance >= privacy_system.min_separation}")
