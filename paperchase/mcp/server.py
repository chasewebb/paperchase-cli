"""MCP server — minimal stdio transport implementing the JSON-RPC subset.

For v0.1 this is a skeleton that handles `initialize`, `tools/list`, and `tools/call`.
A full MCP SDK adoption is deferred to v0.2 when the official Python SDK stabilizes
on the version we want to pin.
"""
from __future__ import annotations

import json
import sys
from typing import Any

from paperchase.loop.executor import make_executor
from paperchase.mcp.tool_export import builtin_tool_schemas
from paperchase.skills.registry import SkillRegistry
from paperchase.tools.shell import ShellGate


def _executor():
    reg = SkillRegistry()
    reg.discover_builtin()
    gate = ShellGate(auto_allow_patterns=["echo *"], interactive=False)
    return make_executor(shell_gate=gate, skill_registry=reg)


def _handle(request: dict[str, Any]) -> dict[str, Any]:
    method = request.get("method")
    rid = request.get("id")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "paperchase", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": builtin_tool_schemas()}}
    if method == "tools/call":
        params = request.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})
        execute = _executor()
        result = execute({"tool": name, "args": args})
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
        }
    return {
        "jsonrpc": "2.0",
        "id": rid,
        "error": {"code": -32601, "message": f"method not found: {method}"},
    }


def serve_stdio() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = _handle(req)
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()
