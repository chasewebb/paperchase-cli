"""Codec banner — MGS1 + Konami atmosphere.

Rendered by paperchase/repl/renderer.py.
"""
from __future__ import annotations


TITLE = "PaperChase"
TAGLINE = "LEVEL HEADED NEVER GROUNDED™"

CHANNEL = "CH 401"
FREQ = "FREQ 140.85"

# Rabbit mascot — sits in the codec frame with version + model + tool count.
RABBIT = [
    r"(\(  ",
    r"( ·.·)",
    r'c("")("")',
]

SEP_BAR = "━" * 64
SEP_DASH = "─" * 64

BOOT_LINES = [
    "...tuning frequency",
    "...node sync established",
    "...memory engine online",
    "...autonomous agents active",
]

SLASH_HINT = "Type to chat. Slash for commands. /help · /quit"

SLASH_HELP = """
[ CODEC COMMANDS · FREQ 140.85 ]

  /help        show this list
  /status      runtimes, vault, skills, links
  /skills      list installed skills
  /reflect     distill recent sessions into ~/.paperchase/learnings.md
  /quit        leave the codec
"""

ALERT = "!"

SIGN_OFFS = [
    "[ TRANSMISSION COMPLETE · FREQ 140.85 ]",
    "[ SIGNAL LOST · OPERATOR LEFT THE CHANNEL ]",
    "[ THIS IS BIG BOSS · OVER AND OUT ]",
    "[ KEPT YOU WAITING, HUH? ]",
]


def sign_off_for(turn_count: int) -> str:
    return SIGN_OFFS[turn_count % len(SIGN_OFFS)]
