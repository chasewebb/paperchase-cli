"""Rich-based codec-styled output for the REPL.

Three-pane MGS1 codec view: [ OPERATOR | PTT/FREQ/MEMORY dial | AGENT ].
Phosphor green on near-black. Konami-style boot atmosphere.
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

# Each pane is 24 chars wide (inner). Three panes + two spaces = 78 cols total.
PANE_W = 24
GAP = "  "


def banner(
    *,
    animate: bool = False,
    model: str = "ollama",
    tool_count: int = 9,
    active_runtimes: int = 1,
    total_runtimes: int = 3,
    skill_count: int = 1,
    cwd: str | None = None,
) -> None:
    """Compact 3-line banner — rabbit mascot left, identity/runtime/cwd right.

    Modeled on Claude Code's startup. Tight, professional, gets out of the way.
    The MGS codec atmosphere lives in /status, /help, and sign-offs.
    """
    import os as _os
    from pathlib import Path as _Path

    if cwd is None:
        cwd = _os.environ.get("PWD") or str(_Path.cwd())
    cwd = _short_path(cwd)

    runtime_line = f"{model} · {tool_count} tools · {skill_count} skill" + ("s" if skill_count != 1 else "")
    runtime_line += f" · {active_runtimes}/{total_runtimes} runtimes"
    rabbit_pad = 11  # widest rabbit line is c("")("") = 9 + 2 trailing spaces

    _console.print()
    _console.print(
        Text.assemble(
            (RABBIT[0].ljust(rabbit_pad), "bright_green"),
            (f"{TITLE}", "bold white"),
            (f" v{__version__}", "bright_green"),
        )
    )
    _console.print(
        Text.assemble(
            (RABBIT[1].ljust(rabbit_pad), "bright_green"),
            (runtime_line, "dim white"),
        )
    )
    _console.print(
        Text.assemble(
            (RABBIT[2].ljust(rabbit_pad), "bright_green"),
            (cwd, "dim white"),
        )
    )
    _console.print()


def _short_path(p: str) -> str:
    """Collapse $HOME → ~ and shorten deeply nested paths to ~/.../tail."""
    import os as _os

    home = _os.environ.get("HOME", "")
    if home and p.startswith(home):
        p = "~" + p[len(home):]
    parts = p.split("/")
    if len(parts) <= 5:
        return p
    return "/".join(parts[:2] + ["..."] + parts[-2:])


def _animate_boot() -> None:
    """Optional tuning-in lines — only when banner(animate=True)."""
    for line in BOOT_LINES:
        _console.print(Text(f"  {line}", style="dim bright_green"))
        time.sleep(0.16)
    _console.print()


def sign_off(turn_count: int = 0) -> None:
    _console.print()
    _console.print(Text(SEP_DASH, style="dim green"))
    _console.print(Text(sign_off_for(turn_count), style="bright_green"))
    _console.print()


def slash_help() -> None:
    _console.print(Text(SLASH_HELP.strip(), style="bright_green"))


def alert(message: str) -> None:
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
