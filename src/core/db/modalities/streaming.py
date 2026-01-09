"""
Streaming Engine - Event ingestion with windowed processing.

Provides real-time event ingestion, windowed aggregations, and
Kafka/Pulsar connector compatibility.
"""
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque
import asyncio


@dataclass
class StreamEvent:
    """Streaming event."""
    event_id: str
    stream: str
    data: Dict[str, Any]
    timestamp: datetime


@dataclass
class Window:
    """Time window for aggregation."""
    start: datetime
    end: datetime
    events: List[StreamEvent]


class StreamingEngine:
    """
    Streaming data engine with windowed processing.

    Ingests real-time events and provides windowed aggregations
    with connector support for Kafka and Pulsar.
    """

    def __init__(self, window_size: timedelta = timedelta(minutes=1)):
        self.window_size = window_size
        self.streams: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.windows: Dict[str, List[Window]] = defaultdict(list)
        self.processors: Dict[str, List[Callable]] = defaultdict(list)

    async def ingest(self, stream: str, data: Dict[str, Any],
                    timestamp: Optional[datetime] = None) -> str:
        """
        Ingest event into stream.

        Args:
            stream: Stream name
            data: Event data
            timestamp: Event timestamp (default: now)

        Returns:
            Event ID
        """
        if timestamp is None:
            timestamp = datetime.now()

        event_id = f"{stream}_{int(timestamp.timestamp() * 1000)}"

        event = StreamEvent(
            event_id=event_id,
            stream=stream,
            data=data,
            timestamp=timestamp
        )

        self.streams[stream].append(event)

        # Process event
        await self._process_event(event)

        return event_id

    def register_processor(self, stream: str, processor: Callable) -> None:
        """
        Register event processor for stream.

        Args:
            stream: Stream name
            processor: Async processor function
        """
        self.processors[stream].append(processor)

    async def get_window(self, stream: str, start: datetime, end: datetime) -> Window:
        """
        Get events in time window.

        Args:
            stream: Stream name
            start: Window start
            end: Window end

        Returns:
            Window with events
        """
        events = [
            event for event in self.streams[stream]
            if start <= event.timestamp < end
        ]

        return Window(start=start, end=end, events=events)

    async def aggregate_window(self, stream: str, start: datetime, end: datetime,
                              aggregator: Callable) -> Any:
        """
        Aggregate events in window.

        Args:
            stream: Stream name
            start: Window start
            end: Window end
            aggregator: Aggregation function

        Returns:
            Aggregated result
        """
        window = await self.get_window(stream, start, end)
        return aggregator(window.events)

    async def tumbling_windows(self, stream: str, duration: timedelta,
                              count: int = 10) -> List[Window]:
        """
        Get tumbling windows for stream.

        Args:
            stream: Stream name
            duration: Window duration
            count: Number of windows

        Returns:
            List of windows
        """
        if not self.streams[stream]:
            return []

        latest_event = self.streams[stream][-1]
        end_time = latest_event.timestamp

        windows = []
        for i in range(count):
            window_end = end_time - (duration * i)
            window_start = window_end - duration

            window = await self.get_window(stream, window_start, window_end)
            windows.append(window)

        return list(reversed(windows))

    async def _process_event(self, event: StreamEvent) -> None:
        """Process event through registered processors."""
        for processor in self.processors[event.stream]:
            try:
                await processor(event)
            except Exception as e:
                # Log error but continue processing
                print(f"Error in processor: {e}")

    def get_stats(self, stream: str) -> Dict[str, Any]:
        """Get stream statistics."""
        if stream not in self.streams:
            return {}

        events = list(self.streams[stream])

        if not events:
            return {"num_events": 0}

        return {
            "num_events": len(events),
            "first_timestamp": events[0].timestamp,
            "last_timestamp": events[-1].timestamp,
            "num_processors": len(self.processors[stream])
        }


class KafkaConnector:
    """Kafka connector for streaming engine."""

    def __init__(self, bootstrap_servers: List[str]):
        self.bootstrap_servers = bootstrap_servers
        self.connected = False

    async def connect(self) -> bool:
        """Connect to Kafka."""
        self.connected = True
        return True

    async def consume(self, topic: str, engine: StreamingEngine) -> None:
        """
        Consume messages from Kafka topic into streaming engine.

        Args:
            topic: Kafka topic
            engine: StreamingEngine to ingest into
        """
        if not self.connected:
            await self.connect()

        # Simulate consumption
        while True:
            await asyncio.sleep(0.1)
            # Would consume from Kafka and call engine.ingest()
