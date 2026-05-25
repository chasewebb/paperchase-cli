"""Skill manifest schema."""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SkillManifest:
    name: str
    version: str
    description: str
    entry: str  # 'module:function' path within the skill package
    tools_required: list[str] = field(default_factory=list)
    runtime: str = "any"
    path: Path | None = None  # filled at load

    @classmethod
    def load(cls, skill_dir: Path) -> "SkillManifest":
        toml_path = skill_dir / "skill.toml"
        data = tomllib.loads(toml_path.read_text())
        sk = data["skill"]
        m = cls(
            name=sk["name"],
            version=sk["version"],
            description=sk["description"],
            entry=sk["entry"],
            tools_required=sk.get("tools_required", {}).get("tools", []),
            runtime=sk.get("tools_required", {}).get("runtime", "any"),
        )
        m.path = skill_dir
        return m
