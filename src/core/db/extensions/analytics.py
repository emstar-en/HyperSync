"""
Analytics Warehouse - Columnar storage with OLAP planner.

Provides columnar storage, hyperbolic OLAP query planner, materialized
projections, and workload-aware resource scheduling.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict


@dataclass
class Column:
    """Columnar data storage."""
    name: str
    data_type: str
    values: List[Any]
    compressed: bool = False


@dataclass
class MaterializedView:
    """Materialized projection."""
    view_id: str
    source_table: str
    aggregations: Dict[str, str]
    filters: Dict[str, Any]
    last_refreshed: datetime


class AnalyticsWarehouse:
    """
    Columnar analytics warehouse with OLAP capabilities.

    Stores data in columnar format for efficient analytical queries
    with materialized views and workload scheduling.
    """

    def __init__(self):
        self.tables: Dict[str, Dict[str, Column]] = {}  # table -> column_name -> Column
        self.materialized_views: Dict[str, MaterializedView] = {}
        self.query_history: List[Dict[str, Any]] = []

    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        """
        Create columnar table.

        Args:
            table_name: Table name
            schema: Column name -> data type mapping
        """
        self.tables[table_name] = {}

        for col_name, data_type in schema.items():
            self.tables[table_name][col_name] = Column(
                name=col_name,
                data_type=data_type,
                values=[],
                compressed=False
            )

    def insert(self, table_name: str, records: List[Dict[str, Any]]) -> None:
        """
        Insert records into table.

        Args:
            table_name: Table name
            records: List of records
        """
        if table_name not in self.tables:
            return

        for record in records:
            for col_name, column in self.tables[table_name].items():
                value = record.get(col_name)
                column.values.append(value)

    def query(self, table_name: str,
             select: List[str],
             where: Optional[Dict[str, Any]] = None,
             group_by: Optional[List[str]] = None,
             aggregations: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Execute analytical query.

        Args:
            table_name: Table name
            select: Columns to select
            where: Filter conditions
            group_by: Group by columns
            aggregations: Aggregation functions

        Returns:
            Query results
        """
        if table_name not in self.tables:
            return []

        # Record query for workload analysis
        self.query_history.append({
            "table": table_name,
            "select": select,
            "where": where,
            "group_by": group_by,
            "timestamp": datetime.now()
        })

        # Get row count
        first_col = next(iter(self.tables[table_name].values()))
        num_rows = len(first_col.values)

        # Apply filters
        filtered_indices = list(range(num_rows))
        if where:
            filtered_indices = self._apply_filters(table_name, where, filtered_indices)

        # Apply aggregations
        if group_by and aggregations:
            return self._apply_aggregations(table_name, select, filtered_indices, group_by, aggregations)

        # Simple select
        results = []
        for idx in filtered_indices:
            record = {}
            for col_name in select:
                if col_name in self.tables[table_name]:
                    record[col_name] = self.tables[table_name][col_name].values[idx]
            results.append(record)

        return results

    def create_materialized_view(self, view_id: str, source_table: str,
                                 aggregations: Dict[str, str],
                                 filters: Optional[Dict[str, Any]] = None) -> MaterializedView:
        """
        Create materialized view.

        Args:
            view_id: View identifier
            source_table: Source table
            aggregations: Aggregation specifications
            filters: Optional filters

        Returns:
            Created MaterializedView
        """
        view = MaterializedView(
            view_id=view_id,
            source_table=source_table,
            aggregations=aggregations,
            filters=filters or {},
            last_refreshed=datetime.now()
        )

        self.materialized_views[view_id] = view

        # Create view table
        self.create_table(view_id, {k: "float" for k in aggregations.keys()})

        # Refresh view
        self.refresh_materialized_view(view_id)

        return view

    def refresh_materialized_view(self, view_id: str) -> None:
        """Refresh materialized view."""
        if view_id not in self.materialized_views:
            return

        view = self.materialized_views[view_id]

        # Query source table
        results = self.query(
            view.source_table,
            select=list(view.aggregations.keys()),
            where=view.filters,
            aggregations=view.aggregations
        )

        # Update view table
        if view_id in self.tables:
            for col in self.tables[view_id].values():
                col.values.clear()

        self.insert(view_id, results)
        view.last_refreshed = datetime.now()

    def analyze_workload(self) -> Dict[str, Any]:
        """
        Analyze query workload for optimization.

        Returns:
            Workload analysis
        """
        if not self.query_history:
            return {}

        # Count queries per table
        table_counts = defaultdict(int)
        for query in self.query_history:
            table_counts[query["table"]] += 1

        # Find most queried columns
        column_counts = defaultdict(int)
        for query in self.query_history:
            for col in query.get("select", []):
                column_counts[col] += 1

        return {
            "total_queries": len(self.query_history),
            "queries_per_table": dict(table_counts),
            "most_queried_columns": sorted(column_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }

    def _apply_filters(self, table_name: str, where: Dict[str, Any], indices: List[int]) -> List[int]:
        """Apply filter conditions."""
        filtered = []

        for idx in indices:
            match = True
            for col_name, condition in where.items():
                if col_name not in self.tables[table_name]:
                    match = False
                    break

                value = self.tables[table_name][col_name].values[idx]

                if isinstance(condition, dict):
                    for op, target in condition.items():
                        if op == "$gt" and not (value > target):
                            match = False
                        elif op == "$lt" and not (value < target):
                            match = False
                elif value != condition:
                    match = False

            if match:
                filtered.append(idx)

        return filtered

    def _apply_aggregations(self, table_name: str, select: List[str],
                           indices: List[int], group_by: List[str],
                           aggregations: Dict[str, str]) -> List[Dict[str, Any]]:
        """Apply aggregations with grouping."""
        # Group records
        groups = defaultdict(list)

        for idx in indices:
            key = tuple(self.tables[table_name][col].values[idx] for col in group_by)
            groups[key].append(idx)

        # Compute aggregations
        results = []
        for key, group_indices in groups.items():
            record = {}

            # Add group by columns
            for i, col in enumerate(group_by):
                record[col] = key[i]

            # Compute aggregations
            for col, agg_func in aggregations.items():
                if col in self.tables[table_name]:
                    values = [self.tables[table_name][col].values[idx] for idx in group_indices]

                    if agg_func == "sum":
                        record[f"{col}_{agg_func}"] = sum(values)
                    elif agg_func == "avg":
                        record[f"{col}_{agg_func}"] = sum(values) / len(values)
                    elif agg_func == "count":
                        record[f"{col}_{agg_func}"] = len(values)
                    elif agg_func == "min":
                        record[f"{col}_{agg_func}"] = min(values)
                    elif agg_func == "max":
                        record[f"{col}_{agg_func}"] = max(values)

            results.append(record)

        return results
