from pathlib import Path

import yaml

CONFIG_FILE = ".tdeploy"


def _path(directory: Path | None = None) -> Path:
    return (directory or Path.cwd()) / CONFIG_FILE


def load(directory: Path | None = None) -> dict:
    """Load the unified .tdeploy YAML config. Missing/invalid -> empty dict."""
    path = _path(directory)
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text()) or {}
    return data if isinstance(data, dict) else {}


def save(data: dict, directory: Path | None = None) -> None:
    """Write the config back as YAML.

    Machine-managed file: hand-written comments are not preserved. Keys are
    written in insertion order so the human-edited `registry` block stays on top.
    """
    _path(directory).write_text(
        yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
    )
