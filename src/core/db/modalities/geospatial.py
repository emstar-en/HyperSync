"""
Geospatial Engine - Spatial queries with PostGIS compatibility.

Provides coordinate conversion, spatial query operators, and PostGIS
compatibility layer for geographic data.
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class Point:
    """Geographic point."""
    lat: float
    lon: float
    metadata: Dict[str, Any]


@dataclass
class BoundingBox:
    """Geographic bounding box."""
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float


class GeospatialEngine:
    """
    Geospatial storage and query engine.

    Stores geographic data with spatial indexing and provides
    PostGIS-compatible query operators.
    """

    def __init__(self):
        self.points: Dict[str, Point] = {}
        self.spatial_index: Dict[Tuple[int, int], List[str]] = {}  # grid_cell -> point_ids
        self.grid_size = 1.0  # degrees

    def insert_point(self, point_id: str, lat: float, lon: float,
                    metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Insert geographic point.

        Args:
            point_id: Point identifier
            lat: Latitude
            lon: Longitude
            metadata: Optional metadata
        """
        point = Point(lat=lat, lon=lon, metadata=metadata or {})
        self.points[point_id] = point

        # Add to spatial index
        grid_cell = self._get_grid_cell(lat, lon)
        if grid_cell not in self.spatial_index:
            self.spatial_index[grid_cell] = []
        self.spatial_index[grid_cell].append(point_id)

    def query_within_radius(self, center_lat: float, center_lon: float,
                           radius_km: float) -> List[Tuple[str, float]]:
        """
        Query points within radius of center.

        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            radius_km: Radius in kilometers

        Returns:
            List of (point_id, distance_km) tuples
        """
        results = []

        # Check relevant grid cells
        cells_to_check = self._get_nearby_cells(center_lat, center_lon, radius_km)

        for cell in cells_to_check:
            for point_id in self.spatial_index.get(cell, []):
                point = self.points[point_id]
                distance = self._haversine_distance(
                    center_lat, center_lon,
                    point.lat, point.lon
                )

                if distance <= radius_km:
                    results.append((point_id, distance))

        # Sort by distance
        results.sort(key=lambda x: x[1])
        return results

    def query_within_bbox(self, bbox: BoundingBox) -> List[str]:
        """
        Query points within bounding box.

        Args:
            bbox: Bounding box

        Returns:
            List of point IDs
        """
        results = []

        for point_id, point in self.points.items():
            if (bbox.min_lat <= point.lat <= bbox.max_lat and
                bbox.min_lon <= point.lon <= bbox.max_lon):
                results.append(point_id)

        return results

    def nearest_neighbors(self, lat: float, lon: float, k: int = 10) -> List[Tuple[str, float]]:
        """
        Find k nearest neighbors to point.

        Args:
            lat: Query latitude
            lon: Query longitude
            k: Number of neighbors

        Returns:
            List of (point_id, distance_km) tuples
        """
        distances = []

        for point_id, point in self.points.items():
            distance = self._haversine_distance(lat, lon, point.lat, point.lon)
            distances.append((point_id, distance))

        distances.sort(key=lambda x: x[1])
        return distances[:k]

    def _haversine_distance(self, lat1: float, lon1: float,
                           lat2: float, lon2: float) -> float:
        """
        Compute Haversine distance between two points in kilometers.

        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            Distance in kilometers
        """
        R = 6371.0  # Earth radius in km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2)**2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _get_grid_cell(self, lat: float, lon: float) -> Tuple[int, int]:
        """Get grid cell for coordinates."""
        return (int(lat / self.grid_size), int(lon / self.grid_size))

    def _get_nearby_cells(self, lat: float, lon: float, radius_km: float) -> List[Tuple[int, int]]:
        """Get grid cells within radius."""
        # Approximate degrees per km
        deg_per_km = 1.0 / 111.0
        radius_deg = radius_km * deg_per_km

        center_cell = self._get_grid_cell(lat, lon)
        cell_radius = int(radius_deg / self.grid_size) + 1

        cells = []
        for i in range(-cell_radius, cell_radius + 1):
            for j in range(-cell_radius, cell_radius + 1):
                cells.append((center_cell[0] + i, center_cell[1] + j))

        return cells

    def get_stats(self) -> Dict[str, Any]:
        """Get geospatial index statistics."""
        return {
            "num_points": len(self.points),
            "num_grid_cells": len(self.spatial_index),
            "grid_size_deg": self.grid_size
        }
