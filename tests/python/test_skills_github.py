"""GitHub skill installer tests — mock git clone, never hit the network."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from paperchase.skills.registry import SkillRegistry


SKILL_TOML = """
[skill]
name = "fake-remote"
version = "0.2.3"
description = "fake remote skill"
entry = "skill:run"
"""


def _seed_clone_target(monkeypatch, tmp_home: Path) -> Path:
    """When git clone is invoked, create the destination dir with a real skill.toml."""
    monkeypatch.setenv("HOME", str(tmp_home))
    skills_root = tmp_home / ".paperchase" / "skills"

    def fake_run(cmd, **_kw):
        # cmd is a list starting with "git"
        if "clone" in cmd:
            dest = Path(cmd[-1])
            dest.mkdir(parents=True, exist_ok=True)
            (dest / "skill.toml").write_text(SKILL_TOML)
            # Provide a stub Python module so SkillManifest's invoke path doesn't choke
            # (we never call invoke in this test — purely registration)
            return MagicMock(returncode=0, stdout="", stderr="")
        return MagicMock(returncode=0, stdout="", stderr="")

    return skills_root, fake_run


def test_discover_github_clones_and_registers(tmp_path, monkeypatch):
    skills_root, fake_run = _seed_clone_target(monkeypatch, tmp_path)
    with patch("paperchase.skills.registry.subprocess.run", side_effect=fake_run):
        reg = SkillRegistry()
        m = reg.discover_github("github:someone/fake-remote-skill")
    assert m.name == "fake-remote"
    assert m.version == "0.2.3"
    assert "fake-remote" in {s.name for s in reg.list()}
    # Check the dest path exists with the expected naming
    assert (skills_root / "someone__fake-remote-skill").exists()


def test_discover_github_malformed_spec():
    reg = SkillRegistry()
    with pytest.raises(ValueError):
        reg.discover_github("not-a-github-spec")
    with pytest.raises(ValueError):
        reg.discover_github("github:no-slash-here")


def test_discover_github_missing_skill_toml(tmp_path, monkeypatch):
    """Clone succeeds but skill.toml is missing — must raise."""
    monkeypatch.setenv("HOME", str(tmp_path))

    def fake_run(cmd, **_kw):
        if "clone" in cmd:
            dest = Path(cmd[-1])
            dest.mkdir(parents=True, exist_ok=True)
            # Intentionally do NOT write skill.toml
            return MagicMock(returncode=0, stdout="", stderr="")
        return MagicMock(returncode=0, stdout="", stderr="")

    with patch("paperchase.skills.registry.subprocess.run", side_effect=fake_run):
        reg = SkillRegistry()
        with pytest.raises(ValueError, match="no skill.toml"):
            reg.discover_github("github:owner/repo")
