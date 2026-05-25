"""File operation tools: Read, Write, Edit, Glob, Grep."""
from __future__ import annotations

import glob as _glob
import re
from pathlib import Path
from typing import Any


def read_file(path: str) -> str:
    return Path(path).read_text()


def write_file(path: str, content: str) -> int:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p.write_text(content)


def edit_file(path: str, old: str, new: str) -> int:
    """Exact string replace. Raises if `old` is not present or appears multiple times."""
    p = Path(path)
    text = p.read_text()
    occurrences = text.count(old)
    if occurrences == 0:
        raise ValueError(f"old string not found in {path}")
    if occurrences > 1:
        raise ValueError(
            f"old string appears {occurrences} times in {path}; provide more context to make it unique"
        )
    return p.write_text(text.replace(old, new, 1))


def glob_files(pattern: str) -> list[str]:
    return _glob.glob(pattern, recursive=True)


def grep_files(pattern: str, root: str, max_hits: int = 100) -> list[dict[str, Any]]:
    """Recursive grep through files under root. Returns [{path, line_no, line}]."""
    rx = re.compile(pattern)
    hits: list[dict[str, Any]] = []
    for path in Path(root).rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(errors="replace")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            if rx.search(line):
                hits.append({"path": str(path), "line_no": i, "line": line})
                if len(hits) >= max_hits:
                    return hits
    return hits
