"""Rich-based codec-styled output for the REPL.

MGS1 codec aesthetic — phosphor green on near-black, FREQ 140.85 readout,
channel-tuning boot lines, rabbit mascot in a thin codec frame, sign-offs.
"""
from __future__ import annotations

import time
from typing import Sequence

from rich.console import Console
from rich.text import Text

from paperchase import __version__
from paperchase.manifesto import (
    BOOT_LINES,
    CHANNEL,
    FREQ,
    RABBIT,
    SEP_BAR,
    SEP_DASH,
    SLASH_HELP,
    SLASH_HINT,
    TAGLINE,
    TITLE,
    sign_off_for,
)


_console = Console()


def banner(
    *,
    animate: bool = True,
    model: str = "ollama",
    tool_count: int = 9,
    active_runtimes: int = 1,
    total_runtimes: int = 3,
    skill_count: int = 1,
) -> None:
    """Render the full codec banner. Optionally play a tuning-in animation."""
    # [ INCOMING TRANSMISSION ] marker
    _console.print()
    _console.print(Text(f"[ INCOMING TRANSMISSION · {FREQ} ]", style="bright_green"))
    _console.print(Text(SEP_BAR, style="green"))
    _console.print()

    if animate:
        _animate_boot()

    # Title block
    _console.print(Text(TITLE, style="bold bright_green"))
    _console.print(Text(TAGLINE, style="bright_green"))
    _console.print()

    # Codec frame around the rabbit + version/model/tools
    _render_rabbit_box(model=model, tool_count=tool_count)
    _console.print()

    # Status tag row
    tags = [
        CHANNEL,
        FREQ,
        "PYTHON",
        "MULTI-AGENT",
        f"{tool_count} TOOLS",
        f"{active_runtimes}/{total_runtimes} RUNTIMES",
        f"{skill_count} SKILLS",
        "PAPERCHASEWEBB INC.",
    ]
    _console.print(Text(" · ".join(tags), style="dim bright_green"))
    _console.print()

    # Slash hint
    _console.print(Text("[ TRANSMISSION SIGNED BY PAPERCHASELABS ]", style="bright_green"))
    _console.print(Text(SLASH_HINT, style="dim"))
    _console.print()


def _animate_boot() -> None:
    """Tuning-in lines printed one at a time, codec-style."""
    for line in BOOT_LINES:
        _console.print(Text(f"  {line}", style="dim bright_green"))
        time.sleep(0.16)
    _console.print()


def _render_rabbit_box(*, model: str, tool_count: int) -> None:
    """Thin codec frame with the rabbit + version/model/tools inline."""
    inner_width = 44
    top = "╭" + "─" * inner_width + "╮"
    bot = "╰" + "─" * inner_width + "╯"
    side = "│"

    def _row(text: str, style: str = "bright_green") -> None:
        padded = text.ljust(inner_width)
        _console.print(
            Text.assemble(
                (side, "green"),
                (padded, style),
                (side, "green"),
            )
        )

    _console.print(Text(top, style="green"))
    _row("")
    _row(f"   {RABBIT[0]}   {TITLE} v{__version__}")
    _row(f"   {RABBIT[1]} {model} · {tool_count} tools")
    _row(f"   {RABBIT[2]}")
    _row("")
    _row("   follow the white rabbit ⇣", style="dim bright_green")
    _row("")
    _console.print(Text(bot, style="green"))


def sign_off(turn_count: int = 0) -> None:
    _console.print()
    _console.print(Text(SEP_DASH, style="dim green"))
    _console.print(Text(sign_off_for(turn_count), style="bright_green"))
    _console.print()


def slash_help() -> None:
    _console.print(Text(SLASH_HELP.strip(), style="bright_green"))


def alert(message: str) -> None:
    """Codec alert line — used for permission gates, errors, halts."""
    _console.print(Text(f"  !  {message}", style="bold red"))


def print_assistant(text: str) -> None:
    _console.print(Text(text, style="white"))


def print_meta(text: str) -> None:
    _console.print(Text(text, style="dim"))


def print_links() -> None:
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


def print_section(label: str, items: Sequence[tuple[str, str]]) -> None:
    _console.print(Text(f"\n[ {label} ]", style="bright_green"))
    for k, v in items:
        _console.print(
            Text.assemble(
                (f"  {k:<14}", "dim"),
                (v, "white"),
            )
        )


def follow_the_rabbit() -> None:
    """`/follow` easter egg. Codec moment with the rabbit hopping off-screen."""
    frames = [
        r"  (\(    follow",
        r"  ( ·.·) follow the white",
        r'  c("")("")  follow the white rabbit',
        r"                          ⇣",
        r"                  ...into the runtime...",
    ]
    for line in frames:
        _console.print(Text(line, style="bright_green"))
        time.sleep(0.22)
    _console.print()
