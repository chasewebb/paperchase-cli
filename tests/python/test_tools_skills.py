from paperchase.skills.registry import SkillRegistry
from paperchase.tools.skills import invoke_skill


def test_invoke_skill_builtin_web_research():
    reg = SkillRegistry()
    reg.discover_builtin()
    result = invoke_skill(reg, "web-research", {"url": "missing-scheme"})
    # web-research will return ok=False because the URL is invalid
    assert "ok" in result
