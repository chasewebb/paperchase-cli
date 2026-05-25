"""Critic — decides {continue|replan|done|halt} after each step."""
from __future__ import annotations

import json
from typing import Any

from paperchase.runtimes.base import Message, Runtime


CRITIC_SYSTEM = """You are PaperChase's critic. Given the GOAL, the latest STEP, and its RESULT,
output strict JSON: {"verdict": "continue"|"replan"|"done"|"halt", "reason": "<short>"}.
- "continue" — keep executing the current plan
- "replan" — current plan is wrong; redo planning
- "done" — goal is fully achieved
- "halt" — irrecoverable failure
Return JSON only.
"""


def critique(runtime: Runtime, goal: str, step: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    msgs = [
        Message(role="system", content=CRITIC_SYSTEM),
        Message(
            role="user",
            content=f"GOAL: {goal}\n\nSTEP: {json.dumps(step)}\n\nRESULT: {json.dumps(result)[:2000]}",
        ),
    ]
    response = runtime.chat(msgs)
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").lstrip("json\n").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"verdict": "replan", "reason": f"critic non-JSON: {raw[:120]}"}
