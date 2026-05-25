"""Skill registry — discovers builtin, local, and github-installed skills."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

from paperchase.skills.schema import SkillManifest


BUILTIN_ROOT = Path(__file__).parent / "builtin"


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, SkillManifest] = {}

    def list(self) -> list[SkillManifest]:
        return list(self._skills.values())

    def get(self, name: str) -> SkillManifest:
        return self._skills[name]

    def register(self, manifest: SkillManifest) -> None:
        self._skills[manifest.name] = manifest

    def discover_builtin(self) -> None:
        if not BUILTIN_ROOT.exists():
            return
        for sub in BUILTIN_ROOT.iterdir():
            if not sub.is_dir():
                continue
            toml = sub / "skill.toml"
            if not toml.exists():
                continue
            self.register(SkillManifest.load(sub))

    def discover_local(self, root: Path) -> None:
        toml = root / "skill.toml"
        if not toml.exists():
            raise FileNotFoundError(f"no skill.toml in {root}")
        self.register(SkillManifest.load(root))

    def invoke(self, name: str, args: dict) -> dict:
        m = self.get(name)
        # entry format 'module:function' — module is relative to skill dir
        mod_name, func_name = m.entry.split(":")
        # ensure skill dir is on path
        if m.path and str(m.path) not in sys.path:
            sys.path.insert(0, str(m.path))
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        return func(args)
