"""Executor — dispatches a step to the tool layer."""
from __future__ import annotations

from typing import Any, Callable

from paperchase.tools.files import read_file, write_file, edit_file, glob_files, grep_files
from paperchase.tools.shell import shell_exec
from paperchase.tools.web import web_fetch


def make_executor(
    shell_gate,
    skill_registry,
    *,
    runtime=None,
    subagent_budget: int = 10,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Return a closure that dispatches one step. Step shape: {tool, args, why}.

    If ``runtime`` is provided, the executor can dispatch the ``SpawnAgent`` tool
    which runs a child autonomous loop and returns its halt summary.
    """

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
        if tool == "SpawnAgent":
            if runtime is None:
                return {"ok": False, "error": "SpawnAgent unavailable — executor lacks runtime"}
            from paperchase.loop.subagent import spawn_subagent

            return spawn_subagent(
                args["goal"],
                runtime=runtime,
                shell_gate=shell_gate,
                skill_registry=skill_registry,
                max_iterations=args.get("max_iterations", subagent_budget),
            )
        return {"ok": False, "error": f"unknown tool: {tool!r}"}

    return execute
