"""Tool surface exposed via MCP protocol."""
from __future__ import annotations


def builtin_tool_schemas() -> list[dict]:
    return [
        {
            "name": "Read",
            "description": "Read the entire content of a text file.",
            "inputSchema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
        {
            "name": "Write",
            "description": "Write content to a file (overwrites).",
            "inputSchema": {
                "type": "object",
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
            },
        },
        {
            "name": "Edit",
            "description": "Exact-string replacement in a file. old must appear exactly once.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old": {"type": "string"},
                    "new": {"type": "string"},
                },
                "required": ["path", "old", "new"],
            },
        },
        {
            "name": "Glob",
            "description": "Glob pattern match.",
            "inputSchema": {
                "type": "object",
                "properties": {"pattern": {"type": "string"}},
                "required": ["pattern"],
            },
        },
        {
            "name": "Grep",
            "description": "Recursive grep through a tree.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "root": {"type": "string"},
                    "max_hits": {"type": "integer", "default": 100},
                },
                "required": ["pattern", "root"],
            },
        },
        {
            "name": "Bash",
            "description": "Execute a shell command. Subject to permission gate.",
            "inputSchema": {
                "type": "object",
                "properties": {"cmd": {"type": "string"}},
                "required": ["cmd"],
            },
        },
        {
            "name": "WebFetch",
            "description": "HTTPS-only HTTP GET. Returns body + status + headers.",
            "inputSchema": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
        {
            "name": "Skill",
            "description": "Invoke a registered skill by name.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "args": {"type": "object"},
                },
                "required": ["name"],
            },
        },
        {
            "name": "SpawnAgent",
            "description": (
                "Spawn a child autonomous agent to pursue a subgoal. The child runs its own "
                "PLAN/ACT/CRITIQUE loop with a reduced iteration budget and returns a halt summary."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string"},
                    "max_iterations": {"type": "integer", "default": 10},
                },
                "required": ["goal"],
            },
        },
    ]
