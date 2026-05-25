from pathlib import Path

import pytest

from paperchase.vault.store import VaultStore


@pytest.fixture
def store(tmp_path):
    db_path = tmp_path / "vault.db"
    s = VaultStore(db_path)
    s.connect()
    yield s
    s.close()


def test_session_lifecycle(store):
    sid = store.create_session(mode="repl")
    assert sid
    sess = store.get_session(sid)
    assert sess["mode"] == "repl"
    assert sess["status"] == "active"
    store.end_session(sid, status="done")
    sess = store.get_session(sid)
    assert sess["status"] == "done"
    assert sess["ended_at"] is not None


def test_turn_and_tool_call(store):
    sid = store.create_session(mode="auto", goal="test goal")
    tid = store.add_turn(sid, role="executor", content={"step": "Read foo.txt"})
    assert tid
    cid = store.add_tool_call(
        tid, tool="Read", args={"path": "foo.txt"}, result={"ok": True}, duration_ms=12, status="ok"
    )
    assert cid
    turns = store.list_turns(sid)
    assert len(turns) == 1
    assert turns[0]["role"] == "executor"
