"""Skill invocation tool — bridges Skills registry to the agent tool surface."""
from __future__ import annotations

from typing import Any

from paperchase.skills.registry import SkillRegistry


def invoke_skill(registry: SkillRegistry, name: str, args: dict[str, Any]) -> dict[str, Any]:
    try:
        return registry.invoke(name, args)
    except KeyError:
        return {"ok": False, "error": f"skill '{name}' not registered"}
    except Exception as e:
        return {"ok": False, "error": str(e), "kind": type(e).__name__}
