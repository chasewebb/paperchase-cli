"""Skill manifest schema.

Two skill formats are supported:

1. **TOML + Python entry** (`skill.toml` + a Python module).
   Used for skills that execute code at invocation time.

2. **Markdown** (`SKILL.md` with YAML frontmatter).
   Claude-Code-style skills — a markdown prompt-augmentation that
   extends the agent's persona for the duration of a task.
   No Python execution required.
"""
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass
class SkillManifest:
    name: str
    description: str
    kind: str = "toml"  # 'toml' (Python entry) or 'markdown' (prompt skill)
    version: str = "0.1.0"
    entry: str = ""  # 'module:function' (only used by kind='toml')
    body: str = ""  # the markdown body (only used by kind='markdown')
    tools_required: list[str] = field(default_factory=list)
    runtime: str = "any"
    path: Path | None = None  # filled at load

    @classmethod
    def load(cls, skill_dir: Path) -> "SkillManifest":
        """Load a manifest from skill_dir. Detects TOML or Markdown format."""
        toml_path = skill_dir / "skill.toml"
        md_path = skill_dir / "SKILL.md"
        if toml_path.exists():
            return cls._load_toml(skill_dir, toml_path)
        if md_path.exists():
            return cls._load_markdown(skill_dir, md_path)
        raise FileNotFoundError(
            f"no skill.toml or SKILL.md in {skill_dir}"
        )

    @classmethod
    def _load_toml(cls, skill_dir: Path, toml_path: Path) -> "SkillManifest":
        data = tomllib.loads(toml_path.read_text())
        sk = data["skill"]
        m = cls(
            name=sk["name"],
            version=sk.get("version", "0.1.0"),
            description=sk["description"],
            kind="toml",
            entry=sk.get("entry", ""),
            tools_required=sk.get("tools_required", {}).get("tools", []),
            runtime=sk.get("tools_required", {}).get("runtime", "any"),
        )
        m.path = skill_dir
        return m

    @classmethod
    def _load_markdown(cls, skill_dir: Path, md_path: Path) -> "SkillManifest":
        """Parse YAML-frontmatter markdown skill (Claude Code format)."""
        raw = md_path.read_text()
        match = _FRONTMATTER_RE.match(raw)
        if not match:
            raise ValueError(
                f"{md_path}: missing YAML frontmatter (expected '---' delimited block at top)"
            )
        front = match.group(1)
        body = raw[match.end():].strip()

        # Parse the minimal YAML we need: name + description (single-line each).
        # Skill authors use this in the wild — we don't want a full YAML dep.
        meta: dict[str, str] = {}
        current_key: str | None = None
        for line in front.splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if line.startswith(" ") and current_key:
                # continuation of a multiline value
                meta[current_key] = meta[current_key] + " " + line.strip()
                continue
            if ":" in line:
                k, _, v = line.partition(":")
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                meta[k] = v
                current_key = k

        if "name" not in meta or "description" not in meta:
            raise ValueError(
                f"{md_path}: frontmatter must declare 'name' and 'description'"
            )

        m = cls(
            name=meta["name"],
            description=meta["description"],
            kind="markdown",
            version=meta.get("version", "0.1.0"),
            body=body,
        )
        m.path = skill_dir
        return m
