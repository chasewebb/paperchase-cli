from click.testing import CliRunner

from paperchase.cli import main


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_status_lists_no_runtimes_when_none_registered():
    runner = CliRunner()
    # status should not crash even with zero runtimes
    result = runner.invoke(main, ["status"])
    assert result.exit_code == 0
