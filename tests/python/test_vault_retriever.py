"""Vault retriever tests — recent session summary shape + content."""
from __future__ import annotations

from paperchase.vault.retriever import get_recent_sessions_summary, load_learnings, save_learnings
from paperchase.vault.store import VaultStore


def test_summary_empty_vault(tmp_path):
    v = VaultStore(tmp_path / "vault.db")
    v.connect()
    out = get_recent_sessions_summary(v)
    v.close()
    assert "_no sessions yet_" in out


def test_summary_two_sessions(tmp_path):
    v = VaultStore(tmp_path / "vault.db")
    v.connect()
    s1 = v.create_session(mode="repl")
    v.add_turn(s1, role="user", content={"text": "hello operator"})
    v.add_turn(s1, role="assistant", content={"text": "acknowledged"})
    v.end_session(s1, status="done")

    s2 = v.create_session(mode="auto", goal="summarize a url")
    t1 = v.add_turn(s2, role="planner", content={"steps": [{"tool": "WebFetch"}]})
    v.add_tool_call(t1, tool="WebFetch", args={"url": "x"}, result={"ok": True}, duration_ms=10, status="ok")
    v.add_turn(s2, role="critic", content={"verdict": "done", "reason": "complete"})
    v.end_session(s2, status="done")

    out = get_recent_sessions_summary(v, limit=10)
    v.close()
    assert "RECENT SESSIONS" in out
    assert "summarize a url" in out
    assert "WebFetch" in out
    assert "done" in out


def test_learnings_roundtrip(tmp_path):
    save_learnings(tmp_path, "## Patterns\n- always check vault first")
    out = load_learnings(tmp_path)
    assert "always check vault" in out
