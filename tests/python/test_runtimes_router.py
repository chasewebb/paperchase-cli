"""Tests for the multi-runtime router."""
from __future__ import annotations

from paperchase.runtimes.router import pick_backend, route_explain


def test_pick_default_when_no_intent():
    backend = pick_backend("hi how are you", available=["ollama", "anthropic"])
    assert backend in {"ollama", "anthropic"}


def test_force_override_when_available():
    assert pick_backend("anything", force="anthropic", available=["ollama", "anthropic"]) == "anthropic"


def test_force_ignored_when_unavailable():
    # force points to an unregistered backend — falls through to heuristic
    chosen = pick_backend("anything", force="anthropic", available=["ollama"])
    assert chosen == "ollama"


def test_code_intent_prefers_anthropic_when_available():
    chosen = pick_backend(
        "debug this python function that's throwing TypeError",
        available=["ollama", "anthropic"],
    )
    assert chosen == "anthropic"


def test_vision_intent_prefers_vision_capable():
    chosen = pick_backend(
        "describe this screenshot.png",
        available=["ollama", "anthropic", "openai"],
    )
    # both anthropic and openai have vision=3; either is a valid pick over ollama (vision=0)
    assert chosen in {"anthropic", "openai"}


def test_long_ctx_intent_prefers_long_ctx_runtime():
    chosen = pick_backend(
        "summarize the entire repo for me",
        available=["ollama", "anthropic"],
    )
    assert chosen == "anthropic"


def test_route_explain_returns_structured_dict():
    out = route_explain(
        "refactor this code",
        available=["ollama", "anthropic"],
    )
    assert out["chosen"] in {"ollama", "anthropic"}
    assert out["intent"]["code"] is True
    assert out["intent"]["vision"] is False
    assert "reason" in out
    assert out["available"] == ["ollama", "anthropic"]


def test_route_explain_empty_available_returns_default():
    out = route_explain("anything", available=[])
    assert out["chosen"] == "ollama"


def test_pick_backend_with_only_ollama_available():
    assert pick_backend("write me python", available=["ollama"]) == "ollama"
