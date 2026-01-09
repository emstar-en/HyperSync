from rich.console import Console
from rich.theme import Theme

_console = Console(theme=Theme({
    "info": "cyan",
    "good": "green",
    "warn": "yellow",
    "err": "bold red"
}))

info = _console.print
