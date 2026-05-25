"""Executor — dispatches a step to the tool layer."""
from __future__ import annotations

from typing import Any, Callable

from paperchase.tools.files import read_file, write_file, edit_file, glob_files, grep_files
from paperchase.tools.shell import shell_exec
from paperchase.tools.web import web_fetch


def make_executor(shell_gate, skill_registry) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Return a closure that dispatches one step. Step shape: {tool, args, why}."""

    from paperchase.tools.skills import invoke_skill

    def execute(step: dict[str, Any]) -> dict[str, Any]:
        tool = step.get("tool")
        args = step.get("args", {})
        if tool == "Read":
            return {"ok": True, "data": read_file(**args)}
        if tool == "Write":
            return {"ok": True, "bytes": write_file(**args)}
        if tool == "Edit":
            return {"ok": True, "bytes": edit_file(**args)}
        if tool == "Glob":
            return {"ok": True, "matches": glob_files(**args)}
        if tool == "Grep":
            return {"ok": True, "hits": grep_files(**args)}
        if tool == "Bash":
            return shell_exec(args["cmd"], gate=shell_gate)
        if tool == "WebFetch":
            return web_fetch(**args)
        if tool == "Skill":
            return invoke_skill(skill_registry, args["name"], args.get("args", {}))
        return {"ok": False, "error": f"unknown tool: {tool!r}"}

    return execute
