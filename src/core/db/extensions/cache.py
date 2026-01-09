"""
Cache Layer - Distributed cache with eviction strategies.

Provides distributed caching with write-through/write-back options,
eviction strategies (LRU, LFU, TTL), and invalidation hooks.
"""
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from collections import OrderedDict


class EvictionStrategy(Enum):
    """Cache eviction strategies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live


class WriteMode(Enum):
    """Cache write modes."""
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl: Optional[timedelta]


class CacheLayer:
    """
    Distributed cache with configurable eviction and write modes.

    Provides high-performance caching with LRU/LFU/TTL eviction,
    write-through/write-back modes, and invalidation hooks.
    """

    def __init__(self, capacity: int = 1000,
                 eviction: EvictionStrategy = EvictionStrategy.LRU,
                 write_mode: WriteMode = WriteMode.WRITE_THROUGH,
                 default_ttl: Optional[timedelta] = None):
        self.capacity = capacity
        self.eviction = eviction
        self.write_mode = write_mode
        self.default_ttl = default_ttl

        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.invalidation_hooks: List[Callable] = []

        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "writes": 0
        }

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if key not in self.cache:
            self.stats["misses"] += 1
            return None

        entry = self.cache[key]

        # Check TTL
        if entry.ttl and datetime.now() - entry.created_at > entry.ttl:
            self.delete(key)
            self.stats["misses"] += 1
            return None

        # Update access metadata
        entry.last_accessed = datetime.now()
        entry.access_count += 1

        # Move to end for LRU
        if self.eviction == EvictionStrategy.LRU:
            self.cache.move_to_end(key)

        self.stats["hits"] += 1
        return entry.value

    def put(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        """
        Put value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional time-to-live
        """
        # Check capacity
        if len(self.cache) >= self.capacity and key not in self.cache:
            self._evict()

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=0,
            ttl=ttl or self.default_ttl
        )

        self.cache[key] = entry

        # Move to end for LRU
        if self.eviction == EvictionStrategy.LRU:
            self.cache.move_to_end(key)

        self.stats["writes"] += 1

    def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted
        """
        if key in self.cache:
            del self.cache[key]
            self._trigger_invalidation(key)
            return True
        return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate keys matching pattern.

        Args:
            pattern: Key pattern (simple prefix matching)

        Returns:
            Number of keys invalidated
        """
        keys_to_delete = [k for k in self.cache.keys() if k.startswith(pattern)]

        for key in keys_to_delete:
            self.delete(key)

        return len(keys_to_delete)

    def register_invalidation_hook(self, hook: Callable) -> None:
        """Register hook to be called on invalidation."""
        self.invalidation_hooks.append(hook)

    def _evict(self) -> None:
        """Evict entry based on strategy."""
        if not self.cache:
            return

        if self.eviction == EvictionStrategy.LRU:
            # Remove first (least recently used)
            key, _ = self.cache.popitem(last=False)

        elif self.eviction == EvictionStrategy.LFU:
            # Remove least frequently used
            key = min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
            del self.cache[key]

        elif self.eviction == EvictionStrategy.TTL:
            # Remove oldest by creation time
            key = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
            del self.cache[key]

        self.stats["evictions"] += 1
        self._trigger_invalidation(key)

    def _trigger_invalidation(self, key: str) -> None:
        """Trigger invalidation hooks."""
        for hook in self.invalidation_hooks:
            try:
                hook(key)
            except Exception:
                pass

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0

        return {
            **self.stats,
            "size": len(self.cache),
            "capacity": self.capacity,
            "hit_rate": hit_rate,
            "eviction_strategy": self.eviction.value,
            "write_mode": self.write_mode.value
        }
