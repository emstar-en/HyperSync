"""
HyperSync TUI Layout Engine

Responsive layout engine with breakpoint logic and panel orchestration.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum, auto


logger = logging.getLogger(__name__)


class LayoutTier(Enum):
    """Layout tiers matching terminal tiers."""
    MICRO = auto()
    SMALL = auto()
    STANDARD = auto()
    LARGE = auto()
    ULTRA = auto()


@dataclass
class PanelPosition:
    """Panel position and dimensions."""
    row: int
    col: int
    height: int
    width: int
    z_order: int = 0


@dataclass
class PanelConstraints:
    """Panel size constraints."""
    min_height: int = 1
    min_width: int = 1
    max_height: Optional[int] = None
    max_width: Optional[int] = None
    preferred_height: Optional[int] = None
    preferred_width: Optional[int] = None


@dataclass
class Panel:
    """Panel definition."""
    id: str
    type: str
    title: str
    position: PanelPosition
    constraints: PanelConstraints
    visible: bool = True
    priority: int = 0


class LayoutEngine:
    """
    Adaptive layout engine.

    Manages panel positioning, sizing, and visibility based on terminal
    capabilities and tier.
    """

    def __init__(self, rows: int, cols: int, tier: LayoutTier):
        self.rows = rows
        self.cols = cols
        self.tier = tier
        self.panels: Dict[str, Panel] = {}
        self.grid: List[List[Optional[str]]] = [[None for _ in range(cols)] for _ in range(rows)]
        logger.info(f"LayoutEngine initialized: {rows}x{cols}, tier={tier.name}")

    def add_panel(
        self,
        panel_id: str,
        panel_type: str,
        title: str,
        position: PanelPosition,
        constraints: PanelConstraints,
        priority: int = 0
    ) -> bool:
        """
        Add panel to layout.

        Args:
            panel_id: Unique panel identifier
            panel_type: Panel type
            title: Panel title
            position: Panel position and dimensions
            constraints: Panel size constraints
            priority: Panel priority (higher = more important)

        Returns:
            True if panel was added successfully
        """
        # Validate position
        if not self._validate_position(position):
            logger.warning(f"Invalid position for panel {panel_id}")
            return False

        # Check for conflicts
        if self._has_conflict(panel_id, position):
            logger.warning(f"Position conflict for panel {panel_id}")
            return False

        # Create panel
        panel = Panel(
            id=panel_id,
            type=panel_type,
            title=title,
            position=position,
            constraints=constraints,
            priority=priority
        )

        self.panels[panel_id] = panel
        self._update_grid(panel_id, position)

        logger.debug(f"Added panel {panel_id} at ({position.row},{position.col}) {position.height}x{position.width}")

        return True

    def remove_panel(self, panel_id: str) -> bool:
        """Remove panel from layout."""
        if panel_id not in self.panels:
            return False

        panel = self.panels[panel_id]
        self._clear_grid(panel_id, panel.position)
        del self.panels[panel_id]

        logger.debug(f"Removed panel {panel_id}")

        return True

    def move_panel(self, panel_id: str, new_position: PanelPosition) -> bool:
        """Move panel to new position."""
        if panel_id not in self.panels:
            return False

        panel = self.panels[panel_id]

        # Validate new position
        if not self._validate_position(new_position):
            return False

        # Check for conflicts (excluding self)
        if self._has_conflict(panel_id, new_position):
            return False

        # Update position
        self._clear_grid(panel_id, panel.position)
        panel.position = new_position
        self._update_grid(panel_id, new_position)

        logger.debug(f"Moved panel {panel_id} to ({new_position.row},{new_position.col})")

        return True

    def resize_panel(self, panel_id: str, new_height: int, new_width: int) -> bool:
        """Resize panel."""
        if panel_id not in self.panels:
            return False

        panel = self.panels[panel_id]

        # Check constraints
        if new_height < panel.constraints.min_height or new_width < panel.constraints.min_width:
            return False

        if panel.constraints.max_height and new_height > panel.constraints.max_height:
            return False

        if panel.constraints.max_width and new_width > panel.constraints.max_width:
            return False

        # Create new position
        new_position = PanelPosition(
            row=panel.position.row,
            col=panel.position.col,
            height=new_height,
            width=new_width,
            z_order=panel.position.z_order
        )

        # Validate and update
        if not self._validate_position(new_position):
            return False

        self._clear_grid(panel_id, panel.position)
        panel.position = new_position
        self._update_grid(panel_id, new_position)

        logger.debug(f"Resized panel {panel_id} to {new_height}x{new_width}")

        return True

    def get_panel(self, panel_id: str) -> Optional[Panel]:
        """Get panel by ID."""
        return self.panels.get(panel_id)

    def list_panels(self) -> List[Panel]:
        """List all panels."""
        return list(self.panels.values())

    def reflow(self):
        """
        Reflow layout based on current tier and constraints.

        Adjusts panel sizes and positions to fit current terminal size.
        """
        # Sort panels by priority
        sorted_panels = sorted(self.panels.values(), key=lambda p: p.priority, reverse=True)

        # Clear grid
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        # Reposition panels
        for panel in sorted_panels:
            # Adjust size to fit constraints and terminal
            new_height = min(panel.position.height, self.rows - panel.position.row)
            new_width = min(panel.position.width, self.cols - panel.position.col)

            new_height = max(new_height, panel.constraints.min_height)
            new_width = max(new_width, panel.constraints.min_width)

            # Update position
            panel.position.height = new_height
            panel.position.width = new_width

            # Update grid
            self._update_grid(panel.id, panel.position)

        logger.info(f"Reflowed layout with {len(self.panels)} panels")

    def _validate_position(self, position: PanelPosition) -> bool:
        """Validate panel position."""
        if position.row < 0 or position.col < 0:
            return False

        if position.row + position.height > self.rows:
            return False

        if position.col + position.width > self.cols:
            return False

        return True

    def _has_conflict(self, panel_id: str, position: PanelPosition) -> bool:
        """Check if position conflicts with existing panels."""
        for row in range(position.row, position.row + position.height):
            for col in range(position.col, position.col + position.width):
                if 0 <= row < self.rows and 0 <= col < self.cols:
                    existing = self.grid[row][col]
                    if existing and existing != panel_id:
                        return True

        return False

    def _update_grid(self, panel_id: str, position: PanelPosition):
        """Update grid with panel position."""
        for row in range(position.row, position.row + position.height):
            for col in range(position.col, position.col + position.width):
                if 0 <= row < self.rows and 0 <= col < self.cols:
                    self.grid[row][col] = panel_id

    def _clear_grid(self, panel_id: str, position: PanelPosition):
        """Clear panel from grid."""
        for row in range(position.row, position.row + position.height):
            for col in range(position.col, position.col + position.width):
                if 0 <= row < self.rows and 0 <= col < self.cols:
                    if self.grid[row][col] == panel_id:
                        self.grid[row][col] = None


def create_layout_engine(rows: int, cols: int, tier: str) -> LayoutEngine:
    """Create layout engine instance."""
    tier_enum = LayoutTier[tier.upper()]
    return LayoutEngine(rows, cols, tier_enum)
