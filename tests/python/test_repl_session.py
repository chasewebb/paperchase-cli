from unittest.mock import MagicMock

from paperchase.repl.session import ReplSession
from paperchase.runtimes.base import Message, Response


def test_session_turn_records_to_vault(tmp_path):
    runtime = MagicMock()
    runtime.name = "fake"
    runtime.chat.return_value = Response(content="acknowledged.")
    vault = MagicMock()
    vault.create_session.return_value = "S1"
    vault.add_turn.return_value = "T1"

    sess = ReplSession(runtime=runtime, vault=vault, workspace_root=tmp_path)
    sess.start()
    reply = sess.handle_user_input("hello operator")
    assert "acknowledged" in reply
    assert vault.create_session.called
    assert vault.add_turn.call_count >= 2  # user + assistant
