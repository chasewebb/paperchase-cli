"""Planner — goal → JSON step list via the runtime."""
from __future__ import annotations

import json
from typing import Any

from paperchase.runtimes.base import Message, Runtime, ToolSchema


PLANNER_SYSTEM = """You are PaperChase's planner. Given a GOAL and available TOOLS, output a JSON array of steps.
Each step: {"tool": "<ToolName>", "args": {...}, "why": "<short reason>"}.
Return strict JSON only — no prose.
"""


def plan(runtime: Runtime, goal: str, tools: list[ToolSchema], context: str = "") -> list[dict[str, Any]]:
    """Returns a list of steps. Raises ValueError on malformed JSON."""
    msgs = [
        Message(role="system", content=PLANNER_SYSTEM),
        Message(role="user", content=f"GOAL: {goal}\n\nCONTEXT:\n{context}"),
    ]
    response = runtime.chat(msgs, tools=tools)
    raw = response.content.strip()
    # tolerate code fences
    if raw.startswith("```"):
        raw = raw.strip("`").lstrip("json\n").strip()
    try:
        steps = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"planner returned non-JSON: {e}; raw: {raw[:200]}")
    if not isinstance(steps, list):
        raise ValueError(f"planner returned non-list: {type(steps).__name__}")
    return steps
