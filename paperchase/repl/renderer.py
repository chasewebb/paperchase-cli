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
    animate: bool = True,
    model: str = "ollama",
    tool_count: int = 9,
    active_runtimes: int = 1,
    total_runtimes: int = 3,
    skill_count: int = 1,
) -> None:
    """Render the three-pane codec banner."""
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

    # Three-pane codec view
    left_lines = _operator_pane()
    mid_lines = _ptt_dial_pane(active_runtimes=active_runtimes, total_runtimes=total_runtimes)
    right_lines = _agent_pane(model=model, tool_count=tool_count, skill_count=skill_count)

    rows = max(len(left_lines), len(mid_lines), len(right_lines))
    left_lines += [" " * PANE_W] * (rows - len(left_lines))
    mid_lines += [" " * PANE_W] * (rows - len(mid_lines))
    right_lines += [" " * PANE_W] * (rows - len(right_lines))

    for l, m, r in zip(left_lines, mid_lines, right_lines):
        _console.print(Text(l + GAP + m + GAP + r, style="bright_green"))

    _console.print()
    _console.print(Text("[ TRANSMISSION SIGNED BY PAPERCHASELABS ]", style="bright_green"))
    _console.print(Text(SLASH_HINT, style="dim"))
    _console.print()


def _pane(lines: list[str]) -> list[str]:
    """Wrap a list of inner lines in a thin codec frame of width PANE_W."""
    inner = PANE_W - 2  # account for │ borders
    top = "╭" + "─" * inner + "╮"
    bot = "╰" + "─" * inner + "╯"
    body = [f"│{line[:inner].ljust(inner)}│" for line in lines]
    return [top] + body + [bot]


def _operator_pane() -> list[str]:
    """Left pane — the operator (rabbit mascot + label)."""
    inside = [
        "",
        "   " + RABBIT[0],
        "   " + RABBIT[1],
        "   " + RABBIT[2],
        "",
        "    OPERATOR",
        "",
    ]
    return _pane(inside)


def _ptt_dial_pane(*, active_runtimes: int, total_runtimes: int) -> list[str]:
    """Center pane — PTT / FREQ readout / MEMORY (the codec dial)."""
    freq_seven_seg = "140.85"
    runtime_bar = _bar(active_runtimes, total_runtimes, width=10)
    inside = [
        "",
        "    [ PTT ]",
        "  ╭──────────╮",
        f"  │ {freq_seven_seg:>8} │",
        "  ╰──────────╯",
        f"   {runtime_bar}",
        "   [ MEMORY ]",
        "",
    ]
    return _pane(inside)


def _agent_pane(*, model: str, tool_count: int, skill_count: int) -> list[str]:
    """Right pane — the agent identification (title, version, model, tools, skills)."""
    inside = [
        "",
        "    PAPERCHASE",
        f"     v{__version__}",
        "",
        f"   {model} · {tool_count} tools",
        f"   {skill_count} skill" + ("" if skill_count == 1 else "s"),
        "",
        "      AGENT",
        "",
    ]
    return _pane(inside)


def _bar(filled: int, total: int, *, width: int = 10) -> str:
    """Codec-style progress bar: filled blocks ▰ + empty blocks ▱."""
    if total <= 0:
        return "▱" * width
    n = max(0, min(width, round(width * filled / total)))
    return ("▰" * n) + ("▱" * (width - n))


def _animate_boot() -> None:
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
