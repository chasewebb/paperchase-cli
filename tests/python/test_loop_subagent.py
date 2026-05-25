"""Subagent dispatch tests — mock the runtime, verify halt summary shape."""
from __future__ import annotations

import json
from unittest.mock import MagicMock

from paperchase.loop.subagent import spawn_subagent
from paperchase.runtimes.base import Response
from paperchase.skills.registry import SkillRegistry
from paperchase.tools.shell import ShellGate


def _mock_runtime_done() -> MagicMock:
    """A runtime that returns a 1-step plan, then a 'done' critic verdict."""
    rt = MagicMock()
    rt.name = "mock"
    # Alternate planner -> critic responses
    responses = iter(
        [
            Response(content=json.dumps([{"tool": "Glob", "args": {"pattern": "*"}, "why": "list"}])),
            Response(content=json.dumps({"verdict": "done", "reason": "complete"})),
        ]
    )
    rt.chat = MagicMock(side_effect=lambda *a, **kw: next(responses))
    return rt


def test_subagent_returns_done_on_success(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("")
    rt = _mock_runtime_done()
    out = spawn_subagent(
        "list files",
        runtime=rt,
        shell_gate=ShellGate(),
        skill_registry=SkillRegistry(),
        max_iterations=5,
    )
    assert out["ok"] is True
    assert out["halt_reason"] == "DONE"
    assert out["plan_steps"] == 1


def test_subagent_refuses_when_no_budget():
    rt = _mock_runtime_done()
    out = spawn_subagent(
        "anything",
        runtime=rt,
        shell_gate=ShellGate(),
        skill_registry=SkillRegistry(),
        max_iterations=0,
    )
    assert out["ok"] is False
    assert out["halt_reason"] == "NO_BUDGET"


def test_subagent_via_executor(tmp_path, monkeypatch):
    """The SpawnAgent tool dispatches through make_executor when runtime is provided."""
    from paperchase.loop.executor import make_executor

    monkeypatch.chdir(tmp_path)
    rt = _mock_runtime_done()
    execute = make_executor(
        shell_gate=ShellGate(),
        skill_registry=SkillRegistry(),
        runtime=rt,
    )
    result = execute({"tool": "SpawnAgent", "args": {"goal": "do thing", "max_iterations": 4}})
    assert result["ok"] is True
    assert result["halt_reason"] == "DONE"


def test_executor_rejects_spawn_without_runtime():
    from paperchase.loop.executor import make_executor

    execute = make_executor(shell_gate=ShellGate(), skill_registry=SkillRegistry())
    result = execute({"tool": "SpawnAgent", "args": {"goal": "anything"}})
    assert result["ok"] is False
    assert "lacks runtime" in result["error"]
