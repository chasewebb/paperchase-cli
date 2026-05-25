"""Codec banner + white-rabbit lore + Konami vibes.

The CLI's visual identity:
- MGS1 codec aesthetic (FREQ 140.85, channel tuning, [ TRANSMISSION ] markers,
  codec-style separators)
- Matrix lore (the white rabbit — operator's invitation into the lab's runtime)
- Konami nostalgia (kept-you-waiting easter eggs, the alert glyph)

Rendered by paperchase/repl/renderer.py.
"""
from __future__ import annotations


TITLE = "PaperChase"
TAGLINE = "LEVEL HEADED NEVER GROUNDED™"

CHANNEL = "CH 401"
FREQ = "FREQ 140.85"

# The white rabbit — Matrix lore. Sits inline with version/model/tool count.
RABBIT = [
    r"(\(  ",
    r"( ·.·)",
    r'c("")("")',
]

# Codec separators
SEP_BAR = "━" * 64
SEP_DASH = "─" * 64

# Boot sequence — printed line by line on REPL startup. Codec tuning-in.
BOOT_LINES = [
    "...tuning frequency",
    "...node sync established",
    "...memory engine online",
    "...autonomous agents active",
    "...follow the white rabbit",
]

# Slash command hint shown after the banner.
SLASH_HINT = "Type to chat. Slash for commands. /help · /quit"

# Help text for /help
SLASH_HELP = """
[ CODEC COMMANDS · FREQ 140.85 ]

  /help        show this list
  /status      runtimes, vault, skills, links
  /skills      list installed skills
  /reflect     distill recent sessions into ~/.paperchase/learnings.md
  /follow      follow the white rabbit
  /quit        leave the codec
"""

# Konami-style easter eggs
KEPT_YOU_WAITING = "[ KEPT YOU WAITING, HUH? ]"
ALERT = "!"

# Sign-off lines (rotated on /quit)
SIGN_OFFS = [
    "[ TRANSMISSION COMPLETE · FREQ 140.85 ]",
    "[ SIGNAL LOST · OPERATOR LEFT THE CHANNEL ]",
    "[ THE WHITE RABBIT VANISHES INTO THE NETWORK ]",
    "[ THIS IS BIG BOSS · OVER AND OUT ]",
]


def sign_off_for(turn_count: int) -> str:
    """Rotate sign-off based on session turn count — adds variety."""
    return SIGN_OFFS[turn_count % len(SIGN_OFFS)]
