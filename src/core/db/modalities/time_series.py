"""
Time-Series Engine - Temporal storage with anomaly detection.

Provides time-series storage, windowed aggregations, anomaly detection,
and forecasting capabilities.
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


@dataclass
class TimeSeriesPoint:
    """Time-series data point."""
    timestamp: datetime
    value: float
    tags: Dict[str, str]
    metadata: Dict[str, Any]


@dataclass
class Anomaly:
    """Detected anomaly."""
    timestamp: datetime
    value: float
    expected_value: float
    deviation: float
    severity: str  # low, medium, high


class TimeSeriesEngine:
    """
    Time-series storage and analysis engine.

    Stores time-series data with efficient windowed queries, anomaly
    detection, and basic forecasting capabilities.
    """

    def __init__(self):
        self.series: Dict[str, List[TimeSeriesPoint]] = defaultdict(list)
        self.anomalies: Dict[str, List[Anomaly]] = defaultdict(list)

    def write(self, series_name: str, timestamp: datetime, value: float,
              tags: Optional[Dict[str, str]] = None,
              metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Write time-series point.

        Args:
            series_name: Series identifier
            timestamp: Point timestamp
            value: Point value
            tags: Optional tags
            metadata: Optional metadata
        """
        point = TimeSeriesPoint(
            timestamp=timestamp,
            value=value,
            tags=tags or {},
            metadata=metadata or {}
        )

        self.series[series_name].append(point)

        # Keep series sorted by timestamp
        self.series[series_name].sort(key=lambda p: p.timestamp)

    def query(self, series_name: str, start: datetime, end: datetime,
              tags: Optional[Dict[str, str]] = None) -> List[TimeSeriesPoint]:
        """
        Query time-series data within time range.

        Args:
            series_name: Series identifier
            start: Start timestamp
            end: End timestamp
            tags: Optional tag filters

        Returns:
            List of matching points
        """
        if series_name not in self.series:
            return []

        points = self.series[series_name]

        # Filter by time range
        filtered = [p for p in points if start <= p.timestamp <= end]

        # Filter by tags if provided
        if tags:
            filtered = [
                p for p in filtered
                if all(p.tags.get(k) == v for k, v in tags.items())
            ]

        return filtered

    def aggregate(self, series_name: str, start: datetime, end: datetime,
                  window: timedelta, func: str = "avg") -> List[Tuple[datetime, float]]:
        """
        Aggregate time-series data over windows.

        Args:
            series_name: Series identifier
            start: Start timestamp
            end: End timestamp
            window: Window size
            func: Aggregation function (avg, sum, min, max, count)

        Returns:
            List of (timestamp, aggregated_value) tuples
        """
        points = self.query(series_name, start, end)

        if not points:
            return []

        # Group points into windows
        windows = defaultdict(list)
        current = start

        while current < end:
            window_end = current + window
            window_points = [p for p in points if current <= p.timestamp < window_end]

            if window_points:
                windows[current] = [p.value for p in window_points]

            current = window_end

        # Apply aggregation function
        results = []
        for timestamp, values in sorted(windows.items()):
            if func == "avg":
                agg_value = statistics.mean(values)
            elif func == "sum":
                agg_value = sum(values)
            elif func == "min":
                agg_value = min(values)
            elif func == "max":
                agg_value = max(values)
            elif func == "count":
                agg_value = len(values)
            else:
                agg_value = statistics.mean(values)

            results.append((timestamp, agg_value))

        return results

    def detect_anomalies(self, series_name: str, start: datetime, end: datetime,
                        threshold_std: float = 3.0) -> List[Anomaly]:
        """
        Detect anomalies using standard deviation threshold.

        Args:
            series_name: Series identifier
            start: Start timestamp
            end: End timestamp
            threshold_std: Number of standard deviations for anomaly

        Returns:
            List of detected anomalies
        """
        points = self.query(series_name, start, end)

        if len(points) < 10:
            return []  # Need sufficient data

        values = [p.value for p in points]
        mean = statistics.mean(values)
        std = statistics.stdev(values)

        anomalies = []

        for point in points:
            deviation = abs(point.value - mean) / std if std > 0 else 0

            if deviation > threshold_std:
                # Determine severity
                if deviation > threshold_std * 2:
                    severity = "high"
                elif deviation > threshold_std * 1.5:
                    severity = "medium"
                else:
                    severity = "low"

                anomaly = Anomaly(
                    timestamp=point.timestamp,
                    value=point.value,
                    expected_value=mean,
                    deviation=deviation,
                    severity=severity
                )

                anomalies.append(anomaly)
                self.anomalies[series_name].append(anomaly)

        return anomalies

    def forecast(self, series_name: str, periods: int,
                 method: str = "moving_average") -> List[Tuple[datetime, float]]:
        """
        Forecast future values (simple methods).

        Args:
            series_name: Series identifier
            periods: Number of periods to forecast
            method: Forecasting method (moving_average, last_value)

        Returns:
            List of (timestamp, forecasted_value) tuples
        """
        if series_name not in self.series or not self.series[series_name]:
            return []

        points = self.series[series_name]
        last_point = points[-1]

        # Estimate period duration from recent points
        if len(points) >= 2:
            period_duration = (points[-1].timestamp - points[-2].timestamp)
        else:
            period_duration = timedelta(minutes=1)

        forecasts = []

        if method == "moving_average":
            # Use last 10 points for moving average
            recent_values = [p.value for p in points[-10:]]
            forecast_value = statistics.mean(recent_values)
        else:  # last_value
            forecast_value = last_point.value

        # Generate forecasts
        for i in range(1, periods + 1):
            forecast_timestamp = last_point.timestamp + (period_duration * i)
            forecasts.append((forecast_timestamp, forecast_value))

        return forecasts

    def get_stats(self, series_name: str) -> Dict[str, Any]:
        """Get statistics for time series."""
        if series_name not in self.series or not self.series[series_name]:
            return {}

        points = self.series[series_name]
        values = [p.value for p in points]

        return {
            "count": len(points),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0,
            "first_timestamp": points[0].timestamp,
            "last_timestamp": points[-1].timestamp
        }
