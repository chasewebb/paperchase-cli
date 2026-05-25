import os
from pathlib import Path
import tempfile

import pytest

from paperchase.config import Config, load_config


def test_load_config_defaults_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    cfg = load_config()
    assert cfg.runtime_default == "ollama"
    assert cfg.ollama_host == "http://localhost:11434"
    assert cfg.max_iterations == 25
    assert cfg.workspace_root == Path.cwd()


def test_load_config_reads_user_file(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    cfg_dir = tmp_path / ".paperchase"
    cfg_dir.mkdir()
    (cfg_dir / "config.toml").write_text(
        'runtime_default = "anthropic"\nmax_iterations = 10\n'
    )
    cfg = load_config()
    assert cfg.runtime_default == "anthropic"
    assert cfg.max_iterations == 10
