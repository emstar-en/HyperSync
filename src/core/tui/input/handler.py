"""
HyperSync TUI Input Handler

Multimodal input dispatch with keyboard, mouse, and touch gesture normalization.
"""

import logging
import re
from typing import Optional, Callable, Dict, Any, List
from enum import Enum, auto
from dataclasses import dataclass


logger = logging.getLogger(__name__)


class InputType(Enum):
    """Input event types."""
    KEY = auto()
    MOUSE = auto()
    RESIZE = auto()
    PASTE = auto()


class MouseButton(Enum):
    """Mouse buttons."""
    LEFT = auto()
    MIDDLE = auto()
    RIGHT = auto()
    SCROLL_UP = auto()
    SCROLL_DOWN = auto()


@dataclass
class KeyEvent:
    """Keyboard event."""
    key: str
    ctrl: bool = False
    alt: bool = False
    shift: bool = False


@dataclass
class MouseEvent:
    """Mouse event."""
    button: MouseButton
    row: int
    col: int
    pressed: bool = True


@dataclass
class ResizeEvent:
    """Terminal resize event."""
    rows: int
    cols: int


class InputHandler:
    """
    Multimodal input handler.

    Normalizes keyboard, mouse, and touch input into consistent events.
    """

    def __init__(self):
        self.key_bindings: Dict[str, Callable] = {}
        self.mouse_enabled = False
        self.buffer = ""
        logger.info("InputHandler initialized")

    def enable_mouse(self):
        """Enable mouse input."""
        # SGR mouse mode
        import sys
        sys.stdout.write("\033[?1000h\033[?1002h\033[?1006h")
        sys.stdout.flush()
        self.mouse_enabled = True
        logger.info("Mouse input enabled")

    def disable_mouse(self):
        """Disable mouse input."""
        import sys
        sys.stdout.write("\033[?1000l\033[?1002l\033[?1006l")
        sys.stdout.flush()
        self.mouse_enabled = False
        logger.info("Mouse input disabled")

    def bind_key(self, key: str, callback: Callable):
        """
        Bind key to callback.

        Args:
            key: Key sequence (e.g., "ctrl+c", "alt+enter")
            callback: Callback function
        """
        self.key_bindings[key] = callback
        logger.debug(f"Bound key: {key}")

    def unbind_key(self, key: str):
        """Unbind key."""
        if key in self.key_bindings:
            del self.key_bindings[key]
            logger.debug(f"Unbound key: {key}")

    def parse_input(self, data: str) -> List[Any]:
        """
        Parse input data into events.

        Args:
            data: Raw input data

        Returns:
            List of events
        """
        self.buffer += data
        events = []

        while self.buffer:
            # Try to parse escape sequence
            if self.buffer.startswith("\033"):
                event, consumed = self._parse_escape_sequence()
                if event:
                    events.append(event)
                    self.buffer = self.buffer[consumed:]
                else:
                    break
            else:
                # Regular character
                char = self.buffer[0]
                self.buffer = self.buffer[1:]

                # Check for control characters
                if ord(char) < 32:
                    event = self._parse_control_char(char)
                    if event:
                        events.append(event)
                else:
                    events.append(KeyEvent(key=char))

        return events

    def _parse_escape_sequence(self) -> tuple:
        """Parse ANSI escape sequence."""
        # Mouse SGR mode: \033[<Cb;Cx;Cy(M/m)
        mouse_match = re.match(r"\033\[<(\d+);(\d+);(\d+)([Mm])", self.buffer)
        if mouse_match:
            button_code = int(mouse_match.group(1))
            col = int(mouse_match.group(2)) - 1
            row = int(mouse_match.group(3)) - 1
            pressed = mouse_match.group(4) == 'M'

            # Decode button
            button = self._decode_mouse_button(button_code)

            event = MouseEvent(button=button, row=row, col=col, pressed=pressed)
            return event, mouse_match.end()

        # Function keys: \033[<number>~
        func_match = re.match(r"\033\[(\d+)~", self.buffer)
        if func_match:
            num = int(func_match.group(1))
            key = self._decode_function_key(num)
            return KeyEvent(key=key), func_match.end()

        # Arrow keys: \033[A/B/C/D
        arrow_match = re.match(r"\033\[([ABCD])", self.buffer)
        if arrow_match:
            direction = arrow_match.group(1)
            key_map = {'A': 'up', 'B': 'down', 'C': 'right', 'D': 'left'}
            return KeyEvent(key=key_map[direction]), arrow_match.end()

        # Alt+key: \033<char>
        if len(self.buffer) >= 2:
            char = self.buffer[1]
            return KeyEvent(key=char, alt=True), 2

        return None, 0

    def _parse_control_char(self, char: str) -> Optional[KeyEvent]:
        """Parse control character."""
        code = ord(char)

        if code == 9:  # Tab
            return KeyEvent(key='tab')
        elif code == 10 or code == 13:  # Enter
            return KeyEvent(key='enter')
        elif code == 27:  # Escape
            return KeyEvent(key='escape')
        elif code == 127:  # Backspace
            return KeyEvent(key='backspace')
        elif 1 <= code <= 26:  # Ctrl+A to Ctrl+Z
            key = chr(ord('a') + code - 1)
            return KeyEvent(key=key, ctrl=True)

        return None

    def _decode_mouse_button(self, code: int) -> MouseButton:
        """Decode mouse button from code."""
        base = code & 0x03

        if base == 0:
            return MouseButton.LEFT
        elif base == 1:
            return MouseButton.MIDDLE
        elif base == 2:
            return MouseButton.RIGHT

        # Scroll
        if code == 64:
            return MouseButton.SCROLL_UP
        elif code == 65:
            return MouseButton.SCROLL_DOWN

        return MouseButton.LEFT

    def _decode_function_key(self, num: int) -> str:
        """Decode function key from number."""
        func_keys = {
            1: 'home', 2: 'insert', 3: 'delete', 4: 'end',
            5: 'pageup', 6: 'pagedown',
            11: 'f1', 12: 'f2', 13: 'f3', 14: 'f4', 15: 'f5',
            17: 'f6', 18: 'f7', 19: 'f8', 20: 'f9', 21: 'f10',
            23: 'f11', 24: 'f12'
        }
        return func_keys.get(num, f'f{num}')

    def dispatch(self, event: Any) -> bool:
        """
        Dispatch event to bound callback.

        Args:
            event: Input event

        Returns:
            True if event was handled
        """
        if isinstance(event, KeyEvent):
            # Build key string
            parts = []
            if event.ctrl:
                parts.append('ctrl')
            if event.alt:
                parts.append('alt')
            if event.shift:
                parts.append('shift')
            parts.append(event.key)

            key_str = '+'.join(parts)

            # Check bindings
            if key_str in self.key_bindings:
                self.key_bindings[key_str](event)
                return True

            # Check without modifiers
            if event.key in self.key_bindings:
                self.key_bindings[event.key](event)
                return True

        return False


def create_input_handler() -> InputHandler:
    """Create input handler instance."""
    return InputHandler()
