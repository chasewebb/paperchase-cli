"""SQLite-backed memory vault with versioned migrations."""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any

from paperchase.vault.migrations import ALL as MIGRATIONS


def _ulid() -> str:
    """Lexicographically sortable ID. Good enough for v0.1."""
    return f"{int(time.time() * 1000):013d}-{uuid.uuid4().hex[:12]}"


class VaultStore:
    def __init__(self, path: Path):
        self.path = path
        self.conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._migrate()

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def _migrate(self) -> None:
        assert self.conn
        for m in MIGRATIONS:
            self.conn.executescript(m.SQL)
        self.conn.commit()

    # ---- sessions ----

    def create_session(self, mode: str, goal: str | None = None) -> str:
        assert self.conn
        sid = _ulid()
        self.conn.execute(
            "INSERT INTO sessions(id, started_at, mode, goal, status) VALUES (?, ?, ?, ?, 'active')",
            (sid, int(time.time()), mode, goal),
        )
        self.conn.commit()
        return sid

    def end_session(self, sid: str, status: str = "done") -> None:
        assert self.conn
        self.conn.execute(
            "UPDATE sessions SET ended_at = ?, status = ? WHERE id = ?",
            (int(time.time()), status, sid),
        )
        self.conn.commit()

    def get_session(self, sid: str) -> dict[str, Any] | None:
        assert self.conn
        row = self.conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
        return dict(row) if row else None

    # ---- turns ----

    def add_turn(self, session_id: str, role: str, content: dict[str, Any]) -> str:
        assert self.conn
        tid = _ulid()
        seq_row = self.conn.execute(
            "SELECT COALESCE(MAX(seq), -1) + 1 AS s FROM turns WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        seq = seq_row["s"]
        self.conn.execute(
            "INSERT INTO turns(id, session_id, seq, role, content_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (tid, session_id, seq, role, json.dumps(content), int(time.time())),
        )
        self.conn.commit()
        return tid

    def list_turns(self, session_id: str) -> list[dict[str, Any]]:
        assert self.conn
        rows = self.conn.execute(
            "SELECT * FROM turns WHERE session_id = ? ORDER BY seq ASC", (session_id,)
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["content"] = json.loads(d.pop("content_json"))
            out.append(d)
        return out

    # ---- tool calls ----

    def add_tool_call(
        self,
        turn_id: str,
        tool: str,
        args: dict[str, Any],
        result: dict[str, Any],
        duration_ms: int,
        status: str,
    ) -> str:
        assert self.conn
        cid = _ulid()
        self.conn.execute(
            "INSERT INTO tool_calls(id, turn_id, tool, args_json, result_json, duration_ms, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                cid,
                turn_id,
                tool,
                json.dumps(args),
                json.dumps(result),
                duration_ms,
                status,
                int(time.time()),
            ),
        )
        self.conn.commit()
        return cid

    # ---- skills ----

    def record_skill_install(self, name: str, source: str, version: str) -> None:
        assert self.conn
        self.conn.execute(
            "INSERT OR REPLACE INTO skills_installed(name, source, version, installed_at) VALUES (?, ?, ?, ?)",
            (name, source, version, int(time.time())),
        )
        self.conn.commit()

    def list_skills(self) -> list[dict[str, Any]]:
        assert self.conn
        rows = self.conn.execute("SELECT * FROM skills_installed ORDER BY installed_at DESC").fetchall()
        return [dict(r) for r in rows]
