"""Ollama runtime — local, free, default."""
from __future__ import annotations

from typing import Iterator

import httpx

from paperchase.runtimes.base import Message, Response, StreamChunk, ToolSchema


class OllamaRuntime:
    name = "ollama"

    def __init__(self, host: str = "http://localhost:11434", model: str = "llama3.2"):
        self.host = host.rstrip("/")
        self.model = model

    def _messages_payload(self, messages: list[Message]) -> list[dict]:
        return [
            {k: v for k, v in {"role": m.role, "content": m.content, "name": m.name}.items() if v is not None}
            for m in messages
        ]

    def chat(self, messages: list[Message], tools: list[ToolSchema] | None = None) -> Response:
        payload: dict = {
            "model": self.model,
            "messages": self._messages_payload(messages),
            "stream": False,
        }
        if tools:
            payload["tools"] = [
                {"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.parameters}}
                for t in tools
            ]
        with httpx.Client(timeout=120) as c:
            r = c.post(f"{self.host}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
        msg = data.get("message", {})
        return Response(
            content=msg.get("content", ""),
            tool_calls=msg.get("tool_calls"),
            raw=data,
        )

    def stream(
        self, messages: list[Message], tools: list[ToolSchema] | None = None
    ) -> Iterator[StreamChunk]:
        import json as _json

        payload: dict = {
            "model": self.model,
            "messages": self._messages_payload(messages),
            "stream": True,
        }
        if tools:
            payload["tools"] = [
                {"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.parameters}}
                for t in tools
            ]
        with httpx.Client(timeout=300) as c:
            with c.stream("POST", f"{self.host}/api/chat", json=payload) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line:
                        continue
                    data = _json.loads(line)
                    msg = data.get("message", {})
                    yield StreamChunk(
                        content=msg.get("content", ""),
                        done=data.get("done", False),
                        tool_calls=msg.get("tool_calls"),
                    )
