"""Multi-agent dispatch — spawn a child autonomous loop for a subgoal.

The parent loop calls `spawn_subagent(goal, ...)` via the `SpawnAgent` tool.
The subagent runs its own PLAN/ACT/CRITIQUE cycle with a reduced iteration
budget, then returns a structured summary. Hermes-class fan-out, MIT.
"""
from __future__ import annotations

from typing import Any

from paperchase.loop.critic import critique as do_critique
from paperchase.loop.executor import make_executor
from paperchase.loop.planner import plan as do_plan
from paperchase.loop.state import LoopState, Phase, Verdict


DEFAULT_SUBAGENT_BUDGET = 10


def spawn_subagent(
    goal: str,
    *,
    runtime,
    shell_gate,
    skill_registry,
    max_iterations: int = DEFAULT_SUBAGENT_BUDGET,
) -> dict[str, Any]:
    """Run a child autonomous loop until it halts.

    Returns:
        {
          "ok": bool,
          "halt_reason": str,          # DONE | LOOP_DETECTED | MAX_ITERATIONS | PLANNER_FAILURE | HALT
          "iterations": int,
          "summary": str,              # last critic reason or planner trace tail
          "last_result": dict | None,
          "plan_steps": int,
        }
    """
    if max_iterations <= 0:
        return {
            "ok": False,
            "halt_reason": "NO_BUDGET",
            "iterations": 0,
            "summary": "subagent refused — no iteration budget remaining",
            "last_result": None,
            "plan_steps": 0,
        }

    execute = make_executor(shell_gate=shell_gate, skill_registry=skill_registry)
    state = LoopState(goal=goal, max_iterations=max_iterations)
    last_critique: dict[str, Any] | None = None

    while not state.halted:
        if state.phase == Phase.PLAN:
            try:
                steps = do_plan(runtime, state.goal, tools=[], context="")
                state.set_plan(steps)
            except ValueError as e:
                state.record_planner_failure()
                last_critique = {"verdict": "halt", "reason": f"planner: {e}"}
                continue
        elif state.phase == Phase.ACT:
            if state.cursor >= len(state.plan):
                # plan exhausted — go back to planning
                state.phase = Phase.PLAN
                continue
            step = state.plan[state.cursor]
            result = execute(step)
            state.record_step_result(result)
        elif state.phase == Phase.CRITIQUE:
            step = state.plan[state.cursor]
            critique_result = do_critique(runtime, state.goal, step, state.last_result or {})
            last_critique = critique_result
            verdict = Verdict(critique_result.get("verdict", "halt"))
            state.apply_verdict(verdict, reason=critique_result.get("reason", ""))

    halt = state.halt_reason or "UNKNOWN"
    ok = halt == "DONE"
    summary = (last_critique or {}).get("reason", halt)
    return {
        "ok": ok,
        "halt_reason": halt,
        "iterations": state.iteration,
        "summary": summary,
        "last_result": state.last_result,
        "plan_steps": len(state.plan),
    }
