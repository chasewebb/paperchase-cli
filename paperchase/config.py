"""Loads ~/.paperchase/config.toml with defaults."""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path


@dataclass
class Config:
    runtime_default: str = "ollama"
    ollama_host: str = "http://localhost:11434"
    max_iterations: int = 25
    workspace_root: Path = field(default_factory=Path.cwd)
    bash_call_budget: int = 30
    webfetch_call_budget: int = 50
    files_call_budget: int = 200


def load_config() -> Config:
    """Load config from ~/.paperchase/config.toml, falling back to defaults."""
    home = Path(os.environ.get("HOME", str(Path.home())))
    cfg_path = home / ".paperchase" / "config.toml"
    if not cfg_path.exists():
        return Config()
    data = tomllib.loads(cfg_path.read_text())
    valid_fields = {f.name for f in fields(Config)}
    kwargs = {k: v for k, v in data.items() if k in valid_fields}
    if "workspace_root" in kwargs:
        kwargs["workspace_root"] = Path(kwargs["workspace_root"])
    return Config(**kwargs)
