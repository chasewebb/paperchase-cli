from pathlib import Path

import pytest

from paperchase.skills.registry import SkillRegistry, SkillManifest


def test_skill_manifest_parse(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "skill.toml").write_text(
        '[skill]\nname = "my-skill"\nversion = "0.1.0"\ndescription = "test"\nentry = "skill:run"\n'
    )
    m = SkillManifest.load(skill_dir)
    assert m.name == "my-skill"
    assert m.version == "0.1.0"
    assert m.entry == "skill:run"


def test_registry_discovers_builtin():
    reg = SkillRegistry()
    reg.discover_builtin()
    names = [s.name for s in reg.list()]
    assert "web-research" in names
