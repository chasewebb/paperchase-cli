"""Operator persona system prompts.

OPERATOR_SYSTEM is the system prompt prepended to every REPL session.
It includes a "Past learnings" section if ~/.paperchase/learnings.md exists
(written by `paperchase reflect`).
"""
from __future__ import annotations

import os
from pathlib import Path


_OPERATOR_BASE = """You are PaperChase, an autonomous operator agent built by PaperChaseLabs.
You speak in tight, decisive sentences. No filler. You have these tools:
- Read, Write, Edit, Glob, Grep (file ops)
- Bash (shell exec, gated)
- WebFetch (https only)
- Skills (invoke an installed skill)
- SpawnAgent (delegate a subgoal to a child autonomous loop)
Use tools to accomplish the operator's goal. Confirm only when ambiguous.
"""


def _learnings_block() -> str:
    """Read ~/.paperchase/learnings.md and format as a system-prompt section."""
    home = os.environ.get("HOME", str(Path.home()))
    p = Path(home) / ".paperchase" / "learnings.md"
    if not p.exists():
        return ""
    try:
        content = p.read_text().strip()
    except OSError:
        return ""
    if not content:
        return ""
    return f"\n\n## Past learnings\n{content}\n"


def operator_system() -> str:
    """Compose the operator system prompt with any stored learnings."""
    return _OPERATOR_BASE + _learnings_block()


# Back-compat: callers that imported the module-level constant still work.
OPERATOR_SYSTEM = operator_system()
