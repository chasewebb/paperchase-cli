"""Rich-based codec-styled output."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


_console = Console()


def banner(version: str) -> None:
    _console.print(
        Panel.fit(
            Text.assemble(
                ("PAPERCHASE", "bold bright_green"),
                ("  v", "dim"),
                (version, "bright_green"),
                ("  ·  FREQ 140.85", "dim"),
            ),
            border_style="green",
            padding=(0, 2),
        )
    )


def print_assistant(text: str) -> None:
    _console.print(Text(text, style="white"))


def print_meta(text: str) -> None:
    _console.print(Text(text, style="dim"))
