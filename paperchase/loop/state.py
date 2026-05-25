"""Finite state machine for the autonomous loop."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Phase(str, Enum):
    PLAN = "plan"
    ACT = "act"
    CRITIQUE = "critique"
    DONE = "done"


class Verdict(str, Enum):
    CONTINUE = "continue"
    REPLAN = "replan"
    DONE = "done"
    HALT = "halt"


@dataclass
class LoopState:
    goal: str
    phase: Phase = Phase.PLAN
    iteration: int = 0
    max_iterations: int = 25
    plan: list[dict[str, Any]] = field(default_factory=list)
    cursor: int = 0
    last_result: dict[str, Any] | None = None
    halted: bool = False
    halt_reason: str | None = None
    replan_streak: int = 0
    planner_failures: int = 0

    def set_plan(self, steps: list[dict[str, Any]]) -> None:
        self.plan = steps
        self.cursor = 0
        self.phase = Phase.ACT
        self.replan_streak = 0  # reset on a successful plan

    def record_step_result(self, result: dict[str, Any]) -> None:
        self.last_result = result
        self.phase = Phase.CRITIQUE

    def apply_verdict(self, verdict: Verdict, reason: str) -> None:
        if verdict == Verdict.CONTINUE:
            self.cursor += 1
            if self.cursor >= len(self.plan):
                self.phase = Phase.PLAN  # need more steps
            else:
                self.phase = Phase.ACT
            self.replan_streak = 0
        elif verdict == Verdict.REPLAN:
            self.phase = Phase.PLAN
            self.replan_streak += 1
            if self.replan_streak >= 3:
                self.halt("LOOP_DETECTED")
        elif verdict == Verdict.DONE:
            self.halt("DONE")
        elif verdict == Verdict.HALT:
            self.halt(reason or "HALT")
        self.iteration += 1
        if self.iteration >= self.max_iterations and not self.halted:
            self.halt("MAX_ITERATIONS")

    def halt(self, reason: str) -> None:
        self.halted = True
        self.halt_reason = reason
        self.phase = Phase.DONE

    def record_planner_failure(self) -> None:
        self.planner_failures += 1
        if self.planner_failures >= 2:
            self.halt("PLANNER_FAILURE")
