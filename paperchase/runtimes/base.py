"""Abstract Runtime interface + registry."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Protocol


@dataclass
class Message:
    role: str  # 'system' | 'user' | 'assistant' | 'tool'
    content: str
    name: str | None = None
    tool_call_id: str | None = None


@dataclass
class ToolSchema:
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema


@dataclass
class StreamChunk:
    content: str
    done: bool = False
    tool_calls: list[dict[str, Any]] | None = None


@dataclass
class Response:
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    raw: dict[str, Any] | None = None


class Runtime(Protocol):
    name: str

    def chat(self, messages: list[Message], tools: list[ToolSchema] | None = None) -> Response: ...

    def stream(
        self, messages: list[Message], tools: list[ToolSchema] | None = None
    ) -> Iterator[StreamChunk]: ...


_REGISTRY: dict[str, Runtime] = {}


def register(runtime: Runtime) -> None:
    _REGISTRY[runtime.name] = runtime


def get_runtime(name: str) -> Runtime:
    if name not in _REGISTRY:
        raise KeyError(f"Runtime '{name}' not registered. Available: {list(_REGISTRY)}")
    return _REGISTRY[name]


def registered_runtimes() -> list[str]:
    return list(_REGISTRY.keys())
