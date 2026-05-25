from paperchase.mcp.tool_export import builtin_tool_schemas


def test_builtin_schemas_include_required_tools():
    schemas = builtin_tool_schemas()
    names = {s["name"] for s in schemas}
    assert "Read" in names
    assert "Write" in names
    assert "Edit" in names
    assert "Glob" in names
    assert "Grep" in names
    assert "Bash" in names
    assert "WebFetch" in names
    assert "Skill" in names


def test_schemas_have_input_schema():
    schemas = builtin_tool_schemas()
    for s in schemas:
        assert "inputSchema" in s
        assert s["inputSchema"]["type"] == "object"
