"""
HyperSync Hyperbolic Storage Engine

Provides foundational storage and query substrate for curved-space data model
with transactional safety, schema awareness, and hyperbolic cost modeling.
"""
import logging
import struct
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class PageType(Enum):
    """Types of storage pages."""
    DATA = 1
    INDEX = 2
    METADATA = 3
    WAL = 4


@dataclass
class PageHeader:
    """Header for storage page."""
    page_id: int
    page_type: PageType
    checksum: bytes
    curvature: float
    next_page: Optional[int]
    record_count: int

    def to_bytes(self) -> bytes:
        """Serialize header to bytes."""
        return struct.pack(
            "!IB32sfdI",
            self.page_id,
            self.page_type.value,
            self.checksum,
            self.curvature,
            self.next_page or 0,
            self.record_count
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> 'PageHeader':
        """Deserialize header from bytes."""
        page_id, page_type, checksum, curvature, next_page, record_count = struct.unpack(
            "!IB32sfdI", data[:53]
        )
        return cls(
            page_id=page_id,
            page_type=PageType(page_type),
            checksum=checksum,
            curvature=curvature,
            next_page=next_page if next_page > 0 else None,
            record_count=record_count
        )


class WriteAheadLog:
    """
    Write-Ahead Log for durability guarantees.

    Provides append-only log with checksum validation and recovery replay.
    """

    def __init__(self, wal_path: Path):
        self.wal_path = wal_path
        self.wal_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = None
        self._position = 0
        self._open()

    def _open(self):
        """Open WAL file."""
        self._file = open(self.wal_path, 'ab+')
        self._file.seek(0, 2)  # Seek to end
        self._position = self._file.tell()

    def append(self, entry: bytes) -> int:
        """
        Append entry to WAL.

        Returns:
            Position of written entry
        """
        # Calculate checksum
        checksum = hashlib.sha256(entry).digest()

        # Write length, checksum, and entry
        length = len(entry)
        self._file.write(struct.pack("!I", length))
        self._file.write(checksum)
        self._file.write(entry)
        self._file.flush()

        position = self._position
        self._position += 4 + 32 + length

        logger.debug(f"WAL append at position {position}, length {length}")
        return position

    def read_entry(self, position: int) -> Optional[bytes]:
        """Read entry at position."""
        self._file.seek(position)

        # Read length
        length_bytes = self._file.read(4)
        if len(length_bytes) < 4:
            return None

        length = struct.unpack("!I", length_bytes)[0]

        # Read checksum and entry
        checksum = self._file.read(32)
        entry = self._file.read(length)

        # Verify checksum
        computed = hashlib.sha256(entry).digest()
        if computed != checksum:
            raise ValueError(f"Checksum mismatch at position {position}")

        return entry

    def replay(self, callback):
        """Replay all entries in WAL."""
        self._file.seek(0)
        position = 0

        while True:
            entry = self.read_entry(position)
            if entry is None:
                break

            callback(entry)
            position = self._file.tell()

    def checkpoint(self, position: int):
        """Mark checkpoint position."""
        checkpoint_path = self.wal_path.with_suffix('.checkpoint')
        with open(checkpoint_path, 'w') as f:
            f.write(str(position))

    def close(self):
        """Close WAL file."""
        if self._file:
            self._file.close()
            self._file = None


class GeodesicPageManager:
    """
    Manages storage pages with geodesic awareness.

    Pages are addressed in Poincaré disk coordinates.
    """

    def __init__(self, page_bytes: int = 8192):
        self.page_bytes = page_bytes
        self.header_size = 53  # Size of PageHeader
        self.data_size = page_bytes - self.header_size
        self._pages: Dict[int, bytes] = {}
        self._next_page_id = 1
        self._free_list: List[int] = []

    def allocate_page(self, page_type: PageType, curvature: float = -1.0) -> int:
        """
        Allocate new page.

        Args:
            page_type: Type of page to allocate
            curvature: Curvature value for page

        Returns:
            Page ID
        """
        if self._free_list:
            page_id = self._free_list.pop()
        else:
            page_id = self._next_page_id
            self._next_page_id += 1

        # Create empty page with header
        header = PageHeader(
            page_id=page_id,
            page_type=page_type,
            checksum=b'\x00' * 32,
            curvature=curvature,
            next_page=None,
            record_count=0
        )

        page_data = header.to_bytes() + (b'\x00' * self.data_size)
        self._pages[page_id] = page_data

        logger.debug(f"Allocated page {page_id}, type={page_type}, curvature={curvature}")
        return page_id

    def write(self, page_id: int, data: bytes, offset: int = 0):
        """Write data to page."""
        if page_id not in self._pages:
            raise ValueError(f"Page {page_id} not found")

        page = bytearray(self._pages[page_id])

        # Write data after header
        data_offset = self.header_size + offset
        page[data_offset:data_offset + len(data)] = data

        # Update checksum
        data_portion = bytes(page[self.header_size:])
        checksum = hashlib.sha256(data_portion).digest()
        page[5:37] = checksum

        self._pages[page_id] = bytes(page)

    def read(self, page_id: int) -> Tuple[PageHeader, bytes]:
        """Read page."""
        if page_id not in self._pages:
            raise ValueError(f"Page {page_id} not found")

        page = self._pages[page_id]
        header = PageHeader.from_bytes(page[:self.header_size])
        data = page[self.header_size:]

        return header, data

    def select_target(self, relation: str, record: dict, curvature: float = -1.0) -> int:
        """
        Select target page for record based on geodesic placement.

        Args:
            relation: Relation name
            record: Record to place
            curvature: Target curvature

        Returns:
            Page ID
        """
        # Find pages with matching curvature
        candidates = [
            pid for pid, page in self._pages.items()
            if PageHeader.from_bytes(page[:self.header_size]).curvature == curvature
        ]

        if not candidates:
            # Allocate new page
            return self.allocate_page(PageType.DATA, curvature)

        # Select page with most free space
        # For now, just return first candidate
        return candidates[0]

    def scan_geodesic(self, start_page: int, predicate) -> List[bytes]:
        """
        Scan pages along geodesic path.

        Args:
            start_page: Starting page ID
            predicate: Filter predicate

        Returns:
            List of matching records
        """
        results = []
        current_page = start_page

        while current_page is not None:
            header, data = self.read(current_page)

            # Extract records from page
            # (Simplified - would need proper record format)
            if predicate(data):
                results.append(data)

            current_page = header.next_page

        return results

    def free_page(self, page_id: int):
        """Free page for reuse."""
        if page_id in self._pages:
            del self._pages[page_id]
            self._free_list.append(page_id)


class Catalog:
    """
    System catalog for metadata.

    Stores relation schemas, indices, and statistics.
    """

    def __init__(self):
        self.relations: Dict[str, dict] = {}
        self.indices: Dict[str, List[dict]] = {}
        self.statistics: Dict[str, dict] = {}

    @classmethod
    def load(cls, path: Optional[Path] = None) -> 'Catalog':
        """Load catalog from disk."""
        catalog = cls()

        if path and path.exists():
            with open(path, 'r') as f:
                data = json.load(f)
                catalog.relations = data.get('relations', {})
                catalog.indices = data.get('indices', {})
                catalog.statistics = data.get('statistics', {})

        return catalog

    def save(self, path: Path):
        """Save catalog to disk."""
        data = {
            'relations': self.relations,
            'indices': self.indices,
            'statistics': self.statistics
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def register_relation(self, name: str, schema: dict):
        """Register relation schema."""
        self.relations[name] = schema
        self.indices[name] = []
        self.statistics[name] = {}

    def pack(self, relation: str, record: dict) -> bytes:
        """Pack record according to schema."""
        # Simplified packing - would use proper serialization
        return json.dumps(record).encode('utf-8')

    def unpack(self, relation: str, data: bytes) -> dict:
        """Unpack record according to schema."""
        return json.loads(data.decode('utf-8'))


class HyperbolicStorageEngine:
    """
    Core hyperbolic storage engine.

    Provides transactional storage with curvature-aware indexing and
    geodesic query support.
    """

    def __init__(self, data_dir: Path, page_bytes: int = 8192):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.catalog = Catalog.load(self.data_dir / 'catalog.json')
        self.wal = WriteAheadLog(self.data_dir / 'wal.log')
        self.page_manager = GeodesicPageManager(page_bytes)

        logger.info(f"Initialized HyperbolicStorageEngine at {data_dir}")

    def create_relation(self, name: str, schema: dict):
        """Create new relation."""
        self.catalog.register_relation(name, schema)
        self.catalog.save(self.data_dir / 'catalog.json')
        logger.info(f"Created relation: {name}")

    def insert(self, relation: str, record: dict) -> int:
        """
        Insert record into relation.

        Args:
            relation: Relation name
            record: Record to insert

        Returns:
            Record ID
        """
        # Pack record
        entry = self.catalog.pack(relation, record)

        # Append to WAL
        wal_position = self.wal.append(entry)

        # Select target page
        curvature = record.get('_curvature', -1.0)
        page_id = self.page_manager.select_target(relation, record, curvature)

        # Write to page
        self.page_manager.write(page_id, entry)

        logger.debug(f"Inserted record into {relation}, page={page_id}")
        return wal_position

    def scan(self, relation: str, predicate=None) -> List[dict]:
        """
        Scan relation.

        Args:
            relation: Relation name
            predicate: Optional filter predicate

        Returns:
            List of matching records
        """
        results = []

        # Find all pages for relation
        # (Simplified - would use catalog metadata)
        for page_id in self.page_manager._pages.keys():
            header, data = self.page_manager.read(page_id)

            if header.page_type == PageType.DATA:
                try:
                    record = self.catalog.unpack(relation, data.rstrip(b'\x00'))
                    if predicate is None or predicate(record):
                        results.append(record)
                except:
                    pass

        return results

    def close(self):
        """Close storage engine."""
        self.catalog.save(self.data_dir / 'catalog.json')
        self.wal.close()
        logger.info("Closed HyperbolicStorageEngine")


# Export public API
__all__ = [
    'HyperbolicStorageEngine',
    'WriteAheadLog',
    'GeodesicPageManager',
    'Catalog',
    'PageType',
    'PageHeader'
]
