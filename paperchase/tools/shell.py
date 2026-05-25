"""Bash exec with a permission gate."""
from __future__ import annotations

import fnmatch
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ShellGate:
    """Permission decisions cached for a session."""

    auto_allow_patterns: list[str] = field(default_factory=list)
    deny_patterns: list[str] = field(default_factory=list)
    interactive: bool = False  # True only inside an attended REPL session

    def decide(self, cmd: str) -> str:
        """Return 'allow' | 'deny' | 'ask'."""
        for p in self.deny_patterns:
            if fnmatch.fnmatch(cmd, p):
                return "deny"
        for p in self.auto_allow_patterns:
            if fnmatch.fnmatch(cmd, p):
                return "allow"
        return "ask" if self.interactive else "deny"


def shell_exec(cmd: str, gate: ShellGate, timeout_s: int = 60) -> dict[str, Any]:
    """Execute a shell command if the gate permits it."""
    decision = gate.decide(cmd)
    if decision == "deny":
        return {
            "status": "denied",
            "exit_code": None,
            "stdout": "",
            "stderr": f"shell command denied by gate: {cmd!r}",
            "duration_ms": 0,
        }
    if decision == "ask":
        return {
            "status": "denied",
            "exit_code": None,
            "stdout": "",
            "stderr": "shell command needs interactive approval (not available in current context)",
            "duration_ms": 0,
        }
    started = time.time()
    try:
        r = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        return {
            "status": "ok",
            "exit_code": r.returncode,
            "stdout": r.stdout,
            "stderr": r.stderr,
            "duration_ms": int((time.time() - started) * 1000),
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "exit_code": None,
            "stdout": "",
            "stderr": f"timeout after {timeout_s}s",
            "duration_ms": timeout_s * 1000,
        }
