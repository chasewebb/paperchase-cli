"""Vault retrieval helpers — recent sessions summary for self-reflection."""
from __future__ import annotations

import json
from typing import Any


def get_recent_sessions_summary(vault, limit: int = 10) -> str:
    """Return a markdown summary of the most recent `limit` sessions.

    Used by `paperchase reflect` to feed prior operator behavior into the
    runtime so it can distill patterns into a `learnings.md` memo.
    """
    assert vault.conn, "vault not connected"
    rows = vault.conn.execute(
        """
        SELECT id, mode, goal, status, started_at, ended_at
        FROM sessions
        ORDER BY started_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    if not rows:
        return "_no sessions yet_"

    out: list[str] = ["# RECENT SESSIONS", ""]
    for r in rows:
        sid = r["id"]
        out.append(f"## {sid}")
        out.append(f"- mode: {r['mode']}")
        if r["goal"]:
            out.append(f"- goal: {r['goal']}")
        out.append(f"- status: {r['status']}")
        # Turns summary
        turns = vault.conn.execute(
            "SELECT seq, role, content_json FROM turns WHERE session_id = ? ORDER BY seq ASC",
            (sid,),
        ).fetchall()
        out.append(f"- turns: {len(turns)}")
        if turns:
            roles = ", ".join(t["role"] for t in turns[:8])
            if len(turns) > 8:
                roles += ", …"
            out.append(f"- trace: {roles}")
            # Surface the first user message + last critic verdict if present
            for t in turns:
                if t["role"] == "user":
                    try:
                        first_user = json.loads(t["content_json"]).get("text", "")
                        if first_user:
                            out.append(f"- first user input: {first_user[:140]}")
                    except json.JSONDecodeError:
                        pass
                    break
            last_critic = next(
                (json.loads(t["content_json"]) for t in reversed(turns) if t["role"] == "critic"),
                None,
            )
            if last_critic:
                out.append(
                    f"- final verdict: {last_critic.get('verdict', '?')} — "
                    f"{(last_critic.get('reason', '') or '')[:140]}"
                )
        # Tool call tally
        tool_rows = vault.conn.execute(
            """
            SELECT tool, COUNT(*) AS n, SUM(CASE WHEN status = 'ok' THEN 1 ELSE 0 END) AS ok
            FROM tool_calls
            JOIN turns ON tool_calls.turn_id = turns.id
            WHERE turns.session_id = ?
            GROUP BY tool
            ORDER BY n DESC
            """,
            (sid,),
        ).fetchall()
        if tool_rows:
            parts = [f"{t['tool']}({t['n']})" for t in tool_rows]
            out.append(f"- tool calls: {', '.join(parts)}")
        out.append("")
    return "\n".join(out).strip()


def load_learnings(home: Any) -> str:
    """Read ~/.paperchase/learnings.md if it exists. Return '' otherwise."""
    from pathlib import Path

    p = Path(home) / ".paperchase" / "learnings.md"
    if not p.exists():
        return ""
    return p.read_text()


def save_learnings(home: Any, content: str) -> None:
    from pathlib import Path

    d = Path(home) / ".paperchase"
    d.mkdir(parents=True, exist_ok=True)
    (d / "learnings.md").write_text(content)
