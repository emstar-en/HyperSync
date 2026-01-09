"""
HyperSync TUI Client Runtime

Terminal client core: capability detection, ANSI render pipeline, diff buffering.
"""

import sys
import os
import termios
import tty
import select
import logging
from typing import Optional, Tuple, List
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class TerminalSize:
    """Terminal dimensions."""
    rows: int
    cols: int


class RenderBuffer:
    """Double-buffer for efficient terminal rendering."""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.front_buffer = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.back_buffer = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.dirty = True

    def clear(self):
        """Clear back buffer."""
        self.back_buffer = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.dirty = True

    def write(self, row: int, col: int, text: str, style: Optional[str] = None):
        """Write text to back buffer."""
        if 0 <= row < self.rows:
            for i, char in enumerate(text):
                if 0 <= col + i < self.cols:
                    self.back_buffer[row][col + i] = char
                    self.dirty = True

    def swap(self):
        """Swap front and back buffers."""
        self.front_buffer, self.back_buffer = self.back_buffer, self.front_buffer
        self.dirty = False

    def get_diff(self) -> List[Tuple[int, int, str]]:
        """
        Get differences between front and back buffers.

        Returns:
            List of (row, col, text) tuples
        """
        if not self.dirty:
            return []

        diffs = []

        for row in range(self.rows):
            col = 0
            while col < self.cols:
                if self.front_buffer[row][col] != self.back_buffer[row][col]:
                    # Find run of changed characters
                    start_col = col
                    text = []

                    while col < self.cols and self.front_buffer[row][col] != self.back_buffer[row][col]:
                        text.append(self.back_buffer[row][col])
                        col += 1

                    diffs.append((row, start_col, ''.join(text)))
                else:
                    col += 1

        return diffs


class TUIRuntime:
    """
    TUI client runtime.

    Manages render loop, resize detection, and diff engine.
    """

    def __init__(self):
        self.running = False
        self.size = self._get_terminal_size()
        self.buffer = RenderBuffer(self.size.rows, self.size.cols)
        self.old_settings = None
        logger.info(f"TUIRuntime initialized: {self.size.rows}x{self.size.cols}")

    def _get_terminal_size(self) -> TerminalSize:
        """Get current terminal size."""
        try:
            import shutil
            cols, rows = shutil.get_terminal_size()
            return TerminalSize(rows, cols)
        except Exception as e:
            logger.warning(f"Failed to get terminal size: {e}, using defaults")
            return TerminalSize(24, 80)

    def start(self):
        """Start TUI runtime."""
        self.running = True

        # Save terminal settings
        try:
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        except Exception as e:
            logger.warning(f"Failed to set terminal mode: {e}")

        # Clear screen and hide cursor
        self._write_ansi("\033[2J\033[?25l")

        logger.info("TUI runtime started")

    def stop(self):
        """Stop TUI runtime."""
        self.running = False

        # Restore terminal settings
        if self.old_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            except Exception as e:
                logger.warning(f"Failed to restore terminal settings: {e}")

        # Show cursor and clear screen
        self._write_ansi("\033[?25h\033[2J\033[H")

        logger.info("TUI runtime stopped")

    def check_resize(self) -> bool:
        """
        Check if terminal has been resized.

        Returns:
            True if resized
        """
        new_size = self._get_terminal_size()

        if new_size.rows != self.size.rows or new_size.cols != self.size.cols:
            logger.info(f"Terminal resized: {self.size.rows}x{self.size.cols} -> {new_size.rows}x{new_size.cols}")
            self.size = new_size
            self.buffer = RenderBuffer(self.size.rows, self.size.cols)
            return True

        return False

    def render(self):
        """Render current buffer to terminal."""
        diffs = self.buffer.get_diff()

        if not diffs:
            return

        # Apply diffs
        for row, col, text in diffs:
            self._write_ansi(f"\033[{row + 1};{col + 1}H{text}")

        # Swap buffers
        self.buffer.swap()

    def clear_buffer(self):
        """Clear render buffer."""
        self.buffer.clear()

    def write_text(self, row: int, col: int, text: str, style: Optional[str] = None):
        """Write text to buffer."""
        self.buffer.write(row, col, text, style)

    def _write_ansi(self, sequence: str):
        """Write ANSI sequence to stdout."""
        sys.stdout.write(sequence)
        sys.stdout.flush()

    def read_input(self, timeout: float = 0.1) -> Optional[str]:
        """
        Read input from stdin.

        Args:
            timeout: Timeout in seconds

        Returns:
            Input character or None
        """
        if select.select([sys.stdin], [], [], timeout)[0]:
            return sys.stdin.read(1)
        return None


def create_runtime() -> TUIRuntime:
    """Create TUI runtime instance."""
    return TUIRuntime()
