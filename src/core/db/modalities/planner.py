"""
Cross-Modal Query Planner - Compose multi-modal queries.

Routes queries to appropriate modality engines and combines results
for unified query execution across storage modalities.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Modality(Enum):
    """Storage modality types."""
    GRAPH = "graph"
    TIME_SERIES = "time_series"
    VECTOR = "vector"
    TEXT = "text"
    GEOSPATIAL = "geospatial"
    DOCUMENT = "document"
    STREAMING = "streaming"


@dataclass
class SubPlan:
    """Sub-plan for specific modality."""
    modality: Modality
    operation: str
    parameters: Dict[str, Any]
    estimated_cost: float


@dataclass
class MultiModalPlan:
    """Multi-modal query execution plan."""
    sub_plans: List[SubPlan]
    total_cost: float
    execution_order: List[int]


class CrossModalPlanner:
    """
    Cross-modal query planner.

    Analyzes queries and routes to appropriate modality engines,
    composing multi-modal execution plans.
    """

    def __init__(self):
        self.modality_costs = {
            Modality.GRAPH: 1.0,
            Modality.TIME_SERIES: 0.5,
            Modality.VECTOR: 2.0,
            Modality.TEXT: 1.5,
            Modality.GEOSPATIAL: 1.2,
            Modality.DOCUMENT: 0.8,
            Modality.STREAMING: 0.3
        }

    def plan(self, query: Dict[str, Any]) -> MultiModalPlan:
        """
        Create execution plan for multi-modal query.

        Args:
            query: Query specification

        Returns:
            MultiModalPlan with sub-plans
        """
        sub_plans = []

        # Analyze query and determine required modalities
        if "graph" in query:
            sub_plans.append(self._plan_graph(query["graph"]))

        if "time_series" in query:
            sub_plans.append(self._plan_time_series(query["time_series"]))

        if "vector" in query:
            sub_plans.append(self._plan_vector(query["vector"]))

        if "text" in query:
            sub_plans.append(self._plan_text(query["text"]))

        if "geospatial" in query:
            sub_plans.append(self._plan_geospatial(query["geospatial"]))

        if "document" in query:
            sub_plans.append(self._plan_document(query["document"]))

        if "streaming" in query:
            sub_plans.append(self._plan_streaming(query["streaming"]))

        # Determine execution order (topological sort based on dependencies)
        execution_order = list(range(len(sub_plans)))

        # Calculate total cost
        total_cost = sum(sp.estimated_cost for sp in sub_plans)

        return MultiModalPlan(
            sub_plans=sub_plans,
            total_cost=total_cost,
            execution_order=execution_order
        )

    def explain(self, plan: MultiModalPlan) -> str:
        """
        Generate human-readable explanation of plan.

        Args:
            plan: Multi-modal plan

        Returns:
            Explanation string
        """
        lines = ["Multi-Modal Query Plan:", ""]

        for i, idx in enumerate(plan.execution_order):
            sub_plan = plan.sub_plans[idx]
            lines.append(f"Step {i+1}: {sub_plan.modality.value}")
            lines.append(f"  Operation: {sub_plan.operation}")
            lines.append(f"  Cost: {sub_plan.estimated_cost:.2f}")
            lines.append("")

        lines.append(f"Total Cost: {plan.total_cost:.2f}")

        return "
".join(lines)

    def _plan_graph(self, spec: Dict[str, Any]) -> SubPlan:
        """Plan graph query."""
        return SubPlan(
            modality=Modality.GRAPH,
            operation=spec.get("operation", "shortest_path"),
            parameters=spec,
            estimated_cost=self.modality_costs[Modality.GRAPH]
        )

    def _plan_time_series(self, spec: Dict[str, Any]) -> SubPlan:
        """Plan time-series query."""
        return SubPlan(
            modality=Modality.TIME_SERIES,
            operation=spec.get("operation", "query"),
            parameters=spec,
            estimated_cost=self.modality_costs[Modality.TIME_SERIES]
        )

    def _plan_vector(self, spec: Dict[str, Any]) -> SubPlan:
        """Plan vector search."""
        return SubPlan(
            modality=Modality.VECTOR,
            operation=spec.get("operation", "search"),
            parameters=spec,
            estimated_cost=self.modality_costs[Modality.VECTOR]
        )

    def _plan_text(self, spec: Dict[str, Any]) -> SubPlan:
        """Plan text search."""
        return SubPlan(
            modality=Modality.TEXT,
            operation=spec.get("operation", "search"),
            parameters=spec,
            estimated_cost=self.modality_costs[Modality.TEXT]
        )

    def _plan_geospatial(self, spec: Dict[str, Any]) -> SubPlan:
        """Plan geospatial query."""
        return SubPlan(
            modality=Modality.GEOSPATIAL,
            operation=spec.get("operation", "within_radius"),
            parameters=spec,
            estimated_cost=self.modality_costs[Modality.GEOSPATIAL]
        )

    def _plan_document(self, spec: Dict[str, Any]) -> SubPlan:
        """Plan document query."""
        return SubPlan(
            modality=Modality.DOCUMENT,
            operation=spec.get("operation", "find"),
            parameters=spec,
            estimated_cost=self.modality_costs[Modality.DOCUMENT]
        )

    def _plan_streaming(self, spec: Dict[str, Any]) -> SubPlan:
        """Plan streaming query."""
        return SubPlan(
            modality=Modality.STREAMING,
            operation=spec.get("operation", "get_window"),
            parameters=spec,
            estimated_cost=self.modality_costs[Modality.STREAMING]
        )
