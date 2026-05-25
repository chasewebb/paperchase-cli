"""REPL session — one ReplSession per attended chat."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from paperchase.repl.prompts import OPERATOR_SYSTEM
from paperchase.runtimes.base import Message


class ReplSession:
    def __init__(self, runtime, vault, workspace_root: Path):
        self.runtime = runtime
        self.vault = vault
        self.workspace_root = workspace_root
        self.session_id: str | None = None
        self.history: list[Message] = [Message(role="system", content=OPERATOR_SYSTEM)]

    def start(self) -> str:
        self.session_id = self.vault.create_session(mode="repl")
        return self.session_id

    def handle_user_input(self, text: str) -> str:
        assert self.session_id, "call start() first"
        self.history.append(Message(role="user", content=text))
        self.vault.add_turn(self.session_id, role="user", content={"text": text})
        response = self.runtime.chat(self.history)
        self.history.append(Message(role="assistant", content=response.content))
        self.vault.add_turn(
            self.session_id,
            role="assistant",
            content={"text": response.content, "tool_calls": response.tool_calls},
        )
        return response.content

    def stop(self) -> None:
        if self.session_id:
            self.vault.end_session(self.session_id, status="done")
            self.session_id = None
