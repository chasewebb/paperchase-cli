import pytest

from paperchase.loop.state import LoopState, Phase, Verdict


def test_state_initial_phase_is_plan():
    s = LoopState(goal="test")
    assert s.phase == Phase.PLAN
    assert s.iteration == 0
    assert s.halted is False


def test_state_advance_act_to_critique():
    s = LoopState(goal="test")
    s.set_plan([{"tool": "Read", "args": {"path": "x"}, "why": "demo"}])
    s.phase = Phase.ACT
    s.record_step_result({"status": "ok"})
    assert s.phase == Phase.CRITIQUE


def test_state_replan_returns_to_plan():
    s = LoopState(goal="test")
    s.apply_verdict(Verdict.REPLAN, reason="needs more info")
    assert s.phase == Phase.PLAN
    assert s.replan_streak == 1


def test_state_three_replans_halts():
    s = LoopState(goal="test")
    s.apply_verdict(Verdict.REPLAN, reason="r1")
    s.apply_verdict(Verdict.REPLAN, reason="r2")
    s.apply_verdict(Verdict.REPLAN, reason="r3")
    assert s.halted
    assert s.halt_reason == "LOOP_DETECTED"


def test_state_done_halts():
    s = LoopState(goal="test")
    s.apply_verdict(Verdict.DONE, reason="all good")
    assert s.halted
    assert s.halt_reason == "DONE"
