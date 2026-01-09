"""
Query Planner & Cost Model

Geodesic-aware query planning with curvature-based cost estimation
and hyperbolic join ordering.
"""
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import math

from hypersync.db.query.parser import (
    ASTNode, HyperSelect, GeodesicJoin, JoinClause,
    WhereClause, ColumnRef, BinaryOp
)

logger = logging.getLogger(__name__)


class PlanNodeType(Enum):
    """Query plan node types."""
    SCAN = "scan"
    INDEX_SCAN = "index_scan"
    GEODESIC_SCAN = "geodesic_scan"
    FILTER = "filter"
    JOIN = "join"
    GEODESIC_JOIN = "geodesic_join"
    AGGREGATE = "aggregate"
    SORT = "sort"
    LIMIT = "limit"


@dataclass
class CostEstimate:
    """Cost estimate for query plan."""
    cpu_cost: float
    io_cost: float
    network_cost: float
    curvature_penalty: float
    total_cost: float
    estimated_rows: int

    @classmethod
    def create(
        cls,
        cpu_cost: float,
        io_cost: float,
        network_cost: float = 0.0,
        curvature_penalty: float = 0.0,
        estimated_rows: int = 0
    ) -> 'CostEstimate':
        """Create cost estimate."""
        total = cpu_cost + io_cost + network_cost + curvature_penalty
        return cls(
            cpu_cost=cpu_cost,
            io_cost=io_cost,
            network_cost=network_cost,
            curvature_penalty=curvature_penalty,
            total_cost=total,
            estimated_rows=estimated_rows
        )


@dataclass
class PlanNode:
    """Query plan node."""
    node_type: PlanNodeType
    cost: CostEstimate
    children: List['PlanNode'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'type': self.node_type.value,
            'cost': {
                'cpu': self.cost.cpu_cost,
                'io': self.cost.io_cost,
                'network': self.cost.network_cost,
                'curvature': self.cost.curvature_penalty,
                'total': self.cost.total_cost,
                'rows': self.cost.estimated_rows
            },
            'metadata': self.metadata,
            'children': [child.to_dict() for child in self.children]
        }


@dataclass
class TableStats:
    """Statistics for a table."""
    row_count: int
    page_count: int
    avg_row_size: int
    curvature_distribution: Dict[float, int]  # curvature -> count
    index_stats: Dict[str, dict]


class CostModel:
    """
    Cost model for query planning.

    Integrates curvature tensors for geodesic-aware cost estimation.
    """

    # Cost constants
    CPU_COST_PER_ROW = 0.01
    IO_COST_PER_PAGE = 1.0
    NETWORK_COST_PER_KB = 0.1
    GEODESIC_COST_MULTIPLIER = 2.0

    def __init__(self, statistics: Optional[Dict[str, TableStats]] = None):
        self.statistics = statistics or {}

    def estimate_scan(self, table: str, predicate: Optional[ASTNode] = None) -> CostEstimate:
        """
        Estimate cost of table scan.

        Args:
            table: Table name
            predicate: Optional filter predicate

        Returns:
            Cost estimate
        """
        stats = self.statistics.get(table)
        if not stats:
            # Default estimates
            return CostEstimate.create(
                cpu_cost=100.0,
                io_cost=10.0,
                estimated_rows=1000
            )

        # Base scan cost
        io_cost = stats.page_count * self.IO_COST_PER_PAGE
        cpu_cost = stats.row_count * self.CPU_COST_PER_ROW

        # Apply selectivity if predicate exists
        selectivity = self._estimate_selectivity(predicate) if predicate else 1.0
        estimated_rows = int(stats.row_count * selectivity)

        return CostEstimate.create(
            cpu_cost=cpu_cost,
            io_cost=io_cost,
            estimated_rows=estimated_rows
        )

    def estimate_index_scan(
        self,
        table: str,
        index: str,
        predicate: Optional[ASTNode] = None
    ) -> CostEstimate:
        """Estimate cost of index scan."""
        stats = self.statistics.get(table)
        if not stats:
            return CostEstimate.create(
                cpu_cost=50.0,
                io_cost=5.0,
                estimated_rows=100
            )

        # Index scan is cheaper than full scan
        selectivity = self._estimate_selectivity(predicate) if predicate else 0.1
        estimated_rows = int(stats.row_count * selectivity)

        # Cost based on index height and selectivity
        index_pages = max(1, int(stats.page_count * 0.1))  # Assume 10% for index
        io_cost = (math.log2(index_pages) + estimated_rows * 0.01) * self.IO_COST_PER_PAGE
        cpu_cost = estimated_rows * self.CPU_COST_PER_ROW

        return CostEstimate.create(
            cpu_cost=cpu_cost,
            io_cost=io_cost,
            estimated_rows=estimated_rows
        )

    def estimate_geodesic_scan(
        self,
        table: str,
        start_point: tuple,
        radius: float
    ) -> CostEstimate:
        """
        Estimate cost of geodesic scan.

        Args:
            table: Table name
            start_point: Starting point in hyperbolic space
            radius: Geodesic radius

        Returns:
            Cost estimate
        """
        stats = self.statistics.get(table)
        if not stats:
            return CostEstimate.create(
                cpu_cost=150.0,
                io_cost=15.0,
                curvature_penalty=50.0,
                estimated_rows=500
            )

        # Estimate selectivity based on hyperbolic area
        # Area of hyperbolic disk: A = 2π(sinh(r) - r)
        hyperbolic_area = 2 * math.pi * (math.sinh(radius) - radius)
        selectivity = min(1.0, hyperbolic_area / (2 * math.pi))  # Normalize

        estimated_rows = int(stats.row_count * selectivity)

        # Geodesic operations are more expensive
        cpu_cost = estimated_rows * self.CPU_COST_PER_ROW * self.GEODESIC_COST_MULTIPLIER
        io_cost = estimated_rows * 0.01 * self.IO_COST_PER_PAGE

        # Curvature penalty based on radius
        curvature_penalty = radius * 10.0

        return CostEstimate.create(
            cpu_cost=cpu_cost,
            io_cost=io_cost,
            curvature_penalty=curvature_penalty,
            estimated_rows=estimated_rows
        )

    def estimate_join(
        self,
        left_rows: int,
        right_rows: int,
        join_type: str = "INNER"
    ) -> CostEstimate:
        """
        Estimate cost of join.

        Args:
            left_rows: Estimated rows from left input
            right_rows: Estimated rows from right input
            join_type: Type of join

        Returns:
            Cost estimate
        """
        # Nested loop join cost
        cpu_cost = left_rows * right_rows * self.CPU_COST_PER_ROW

        # Assume hash join if large enough
        if left_rows > 1000 and right_rows > 1000:
            # Hash join cost
            cpu_cost = (left_rows + right_rows) * self.CPU_COST_PER_ROW * 2

        estimated_rows = int(left_rows * right_rows * 0.1)  # Assume 10% selectivity

        return CostEstimate.create(
            cpu_cost=cpu_cost,
            io_cost=0.0,
            estimated_rows=estimated_rows
        )

    def estimate_geodesic_join(
        self,
        left_rows: int,
        right_rows: int,
        distance_threshold: float
    ) -> CostEstimate:
        """
        Estimate cost of geodesic join.

        Args:
            left_rows: Estimated rows from left input
            right_rows: Estimated rows from right input
            distance_threshold: Distance threshold

        Returns:
            Cost estimate
        """
        # Geodesic distance computation for each pair
        cpu_cost = left_rows * right_rows * self.CPU_COST_PER_ROW * self.GEODESIC_COST_MULTIPLIER

        # Selectivity based on distance threshold
        selectivity = min(1.0, distance_threshold)
        estimated_rows = int(left_rows * right_rows * selectivity)

        # Curvature penalty
        curvature_penalty = distance_threshold * left_rows * 0.01

        return CostEstimate.create(
            cpu_cost=cpu_cost,
            io_cost=0.0,
            curvature_penalty=curvature_penalty,
            estimated_rows=estimated_rows
        )

    def _estimate_selectivity(self, predicate: Optional[ASTNode]) -> float:
        """Estimate selectivity of predicate."""
        if not predicate:
            return 1.0

        # Simplified selectivity estimation
        # In production, would use histograms and statistics
        return 0.1


class QueryPlanner:
    """
    Query planner with geodesic awareness.

    Generates optimal execution plans for HyperQL queries.
    """

    def __init__(self, cost_model: Optional[CostModel] = None):
        self.cost_model = cost_model or CostModel()

    def plan(self, query: HyperSelect) -> PlanNode:
        """
        Generate execution plan for query.

        Args:
            query: Parsed query

        Returns:
            Root plan node
        """
        # Start with base scan
        plan = self._plan_scan(query.from_clause.table, query.where)

        # Add joins
        for join in query.joins:
            plan = self._plan_join(plan, join)

        # Add filters
        if query.where:
            plan = self._plan_filter(plan, query.where)

        # Add limit
        if query.limit:
            plan = self._plan_limit(plan, query.limit)

        return plan

    def _plan_scan(self, table: str, where: Optional[WhereClause]) -> PlanNode:
        """Plan table scan."""
        # Check if we can use index
        # For now, just do sequential scan

        predicate = where.condition if where else None
        cost = self.cost_model.estimate_scan(table, predicate)

        return PlanNode(
            node_type=PlanNodeType.SCAN,
            cost=cost,
            metadata={'table': table}
        )

    def _plan_join(self, left: PlanNode, join: ASTNode) -> PlanNode:
        """Plan join operation."""
        if isinstance(join, GeodesicJoin):
            return self._plan_geodesic_join(left, join)
        elif isinstance(join, JoinClause):
            return self._plan_regular_join(left, join)
        else:
            raise ValueError(f"Unknown join type: {type(join)}")

    def _plan_regular_join(self, left: PlanNode, join: JoinClause) -> PlanNode:
        """Plan regular join."""
        # Plan right side
        right_cost = self.cost_model.estimate_scan(join.table)
        right = PlanNode(
            node_type=PlanNodeType.SCAN,
            cost=right_cost,
            metadata={'table': join.table}
        )

        # Plan join
        join_cost = self.cost_model.estimate_join(
            left.cost.estimated_rows,
            right.cost.estimated_rows,
            join.join_type
        )

        return PlanNode(
            node_type=PlanNodeType.JOIN,
            cost=join_cost,
            children=[left, right],
            metadata={'join_type': join.join_type}
        )

    def _plan_geodesic_join(self, left: PlanNode, join: GeodesicJoin) -> PlanNode:
        """Plan geodesic join."""
        # Plan right side
        right_cost = self.cost_model.estimate_scan(join.table)
        right = PlanNode(
            node_type=PlanNodeType.SCAN,
            cost=right_cost,
            metadata={'table': join.table}
        )

        # Plan geodesic join
        join_cost = self.cost_model.estimate_geodesic_join(
            left.cost.estimated_rows,
            right.cost.estimated_rows,
            join.distance_threshold
        )

        return PlanNode(
            node_type=PlanNodeType.GEODESIC_JOIN,
            cost=join_cost,
            children=[left, right],
            metadata={
                'distance_threshold': join.distance_threshold,
                'left_point': join.left_point.column,
                'right_point': join.right_point.column
            }
        )

    def _plan_filter(self, input_plan: PlanNode, where: WhereClause) -> PlanNode:
        """Plan filter operation."""
        # Filter doesn't add much cost
        cost = CostEstimate.create(
            cpu_cost=input_plan.cost.estimated_rows * 0.001,
            io_cost=0.0,
            estimated_rows=int(input_plan.cost.estimated_rows * 0.5)
        )

        return PlanNode(
            node_type=PlanNodeType.FILTER,
            cost=cost,
            children=[input_plan],
            metadata={'condition': str(where.condition)}
        )

    def _plan_limit(self, input_plan: PlanNode, limit: int) -> PlanNode:
        """Plan limit operation."""
        cost = CostEstimate.create(
            cpu_cost=0.0,
            io_cost=0.0,
            estimated_rows=min(limit, input_plan.cost.estimated_rows)
        )

        return PlanNode(
            node_type=PlanNodeType.LIMIT,
            cost=cost,
            children=[input_plan],
            metadata={'limit': limit}
        )


class PlanVisualizer:
    """Visualize query plans for telemetry."""

    @staticmethod
    def explain(plan: PlanNode, indent: int = 0) -> str:
        """
        Generate EXPLAIN output.

        Args:
            plan: Plan node
            indent: Indentation level

        Returns:
            Formatted explanation
        """
        lines = []
        prefix = "  " * indent

        # Node info
        lines.append(f"{prefix}{plan.node_type.value.upper()}")
        lines.append(f"{prefix}  Cost: {plan.cost.total_cost:.2f} (cpu={plan.cost.cpu_cost:.2f}, io={plan.cost.io_cost:.2f})")
        lines.append(f"{prefix}  Rows: {plan.cost.estimated_rows}")

        if plan.metadata:
            lines.append(f"{prefix}  Metadata: {plan.metadata}")

        # Children
        for child in plan.children:
            lines.append(PlanVisualizer.explain(child, indent + 1))

        return "\n".join(lines)

    @staticmethod
    def to_json(plan: PlanNode) -> dict:
        """Convert plan to JSON."""
        return plan.to_dict()


# Export public API
__all__ = [
    'QueryPlanner',
    'CostModel',
    'PlanNode',
    'CostEstimate',
    'PlanVisualizer',
    'TableStats'
]
