"""Rich-based codec-styled output for the REPL.

All terminal UI lives here — banner, status lines, assistant replies, meta
text, and the codec-styled boot sequence. Phosphor green on near-black,
modeled on MGS1 codec aesthetics.
"""
from __future__ import annotations

import time
from typing import Sequence

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from paperchase.manifesto import BANNER, BOOT_STATUS, SIGN_OFF


_console = Console()


def banner(animate: bool = True) -> None:
    """Render the full codec banner. Optionally play a brief tuning-in animation."""
    _console.print(Text(BANNER, style="bright_green"))
    if animate:
        _animate_boot()


def _animate_boot() -> None:
    """Print boot status lines one at a time with a brief delay (codec tuning-in)."""
    for line in BOOT_STATUS:
        _console.print(Text(f"  {line}", style="bright_green"))
        time.sleep(0.18)
    _console.print()


def sign_off() -> None:
    """Closing line on exit."""
    _console.print(Text(SIGN_OFF, style="dim green"))


def print_assistant(text: str) -> None:
    _console.print(Text(text, style="white"))


def print_meta(text: str) -> None:
    _console.print(Text(text, style="dim"))


def print_links() -> None:
    """The lab + repo + community cross-links — shown in status, on welcome."""
    rows = [
        ("LAB", "https://paperchaselabs.com"),
        ("REPO", "https://github.com/chasewebb/paperchase-cli"),
        ("DISCORD", "https://discord.gg/5vYFCcKVrB"),
        ("BOOK A CALL", "https://calendly.com/paperchasewebb/15min"),
    ]
    for label, url in rows:
        _console.print(
            Text.assemble(
                (f"  {label:<13}", "dim bright_green"),
                (url, "white"),
            )
        )


def print_panel(title: str, body: str) -> None:
    """Generic codec-frame panel for one-shot status output."""
    _console.print(
        Panel(
            Text(body, style="white"),
            title=Text(f"[ {title} ]", style="bright_green"),
            border_style="green",
            padding=(0, 2),
        )
    )


def print_section(label: str, items: Sequence[tuple[str, str]]) -> None:
    """Two-column section: phosphor-green label, white value."""
    _console.print(Text(f"\n[ {label} ]", style="bright_green"))
    for k, v in items:
        _console.print(
            Text.assemble(
                (f"  {k:<14}", "dim"),
                (v, "white"),
            )
        )
