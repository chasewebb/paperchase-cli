"""Skill registry — discovers builtin, local, and github-installed skills."""
from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path

from paperchase.skills.schema import SkillManifest


BUILTIN_ROOT = Path(__file__).parent / "builtin"


def _user_skill_root() -> Path:
    """Where remotely-installed skills land on disk."""
    home = Path(os.environ.get("HOME", str(Path.home())))
    root = home / ".paperchase" / "skills"
    root.mkdir(parents=True, exist_ok=True)
    return root


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
            if not sub.is_dir() or sub.name.startswith("_"):
                continue
            if (sub / "skill.toml").exists() or (sub / "SKILL.md").exists():
                self.register(SkillManifest.load(sub))

    def discover_local(self, root: Path) -> None:
        if not (root / "skill.toml").exists() and not (root / "SKILL.md").exists():
            raise FileNotFoundError(f"no skill.toml or SKILL.md in {root}")
        self.register(SkillManifest.load(root))

    def discover_github(self, spec: str) -> SkillManifest:
        """Install a skill from `github:owner/repo[@ref]`.

        Clones (or updates) the repo to ~/.paperchase/skills/<owner>__<repo>/
        and registers it. Validates a `skill.toml` exists at the repo root.

        Returns the registered SkillManifest.
        Raises ValueError if spec is malformed or no skill.toml at root.
        """
        if not spec.startswith("github:"):
            raise ValueError(f"expected github:owner/repo, got {spec!r}")
        body = spec[len("github:"):]
        ref: str | None = None
        if "@" in body:
            body, ref = body.split("@", 1)
        if body.count("/") != 1:
            raise ValueError(f"malformed github spec {spec!r}; expected github:owner/repo")
        owner, repo = body.split("/")
        dest = _user_skill_root() / f"{owner}__{repo}"

        if not dest.exists():
            subprocess.run(
                ["git", "clone", "--depth=1", f"https://github.com/{owner}/{repo}.git", str(dest)],
                check=True,
                capture_output=True,
                text=True,
            )
        else:
            subprocess.run(
                ["git", "-C", str(dest), "fetch", "--depth=1"],
                check=True,
                capture_output=True,
                text=True,
            )
        if ref:
            subprocess.run(
                ["git", "-C", str(dest), "checkout", ref],
                check=True,
                capture_output=True,
                text=True,
            )

        if not (dest / "skill.toml").exists() and not (dest / "SKILL.md").exists():
            raise ValueError(
                f"github:{owner}/{repo} cloned to {dest} but no skill.toml or SKILL.md at repo root"
            )
        manifest = SkillManifest.load(dest)
        self.register(manifest)
        return manifest

    def invoke(self, name: str, args: dict) -> dict:
        """Invoke a registered skill.

        - 'toml' skills run their Python entry function with the args dict.
        - 'markdown' skills return their body — callers load it into the system prompt
          (or display it for the operator). No code execution.
        """
        m = self.get(name)
        if m.kind == "markdown":
            return {
                "ok": True,
                "kind": "markdown",
                "name": m.name,
                "description": m.description,
                "body": m.body,
                "note": "load body into system prompt to activate this skill",
            }
        # TOML / Python entry skill
        if not m.entry:
            return {"ok": False, "error": f"skill '{name}' has no Python entry"}
        mod_name, func_name = m.entry.split(":")
        if m.path and str(m.path) not in sys.path:
            sys.path.insert(0, str(m.path))
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        return func(args)
