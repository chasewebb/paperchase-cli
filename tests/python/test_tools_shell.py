from paperchase.tools.shell import shell_exec, ShellGate


def test_shell_exec_echo():
    gate = ShellGate(auto_allow_patterns=["echo *"])
    result = shell_exec("echo hello", gate=gate)
    assert result["status"] == "ok"
    assert result["stdout"].strip() == "hello"
    assert result["exit_code"] == 0


def test_shell_exec_failing_command():
    gate = ShellGate(auto_allow_patterns=["false"])
    result = shell_exec("false", gate=gate)
    assert result["status"] == "ok"  # status of the call, not the command's exit
    assert result["exit_code"] != 0


def test_shell_exec_denied_by_gate():
    gate = ShellGate(deny_patterns=["rm *"])
    result = shell_exec("rm -rf /", gate=gate)
    assert result["status"] == "denied"
    assert result["exit_code"] is None
