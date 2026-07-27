from pathlib import Path

from tdeploy import config
from tdeploy.runner import run

LEGACY_HISTORY_FILE = ".tdeploy_history"


def get_current_commit() -> str:
    result = run(
        ["git", "rev-parse", "HEAD"],
        status_message="Reading current commit...",
        capture_output=True,
    )
    return result.stdout.strip()


def read_history(directory: Path | None = None) -> list[str]:
    """Return deploy history (oldest first).

    Prefers the `history` list in the unified .tdeploy config. Falls back to the
    legacy `.tdeploy_history` file (one SHA per line) for pre-migration setups.
    """
    history = config.load(directory).get("history")
    if isinstance(history, list) and history:
        return [str(h).strip() for h in history if str(h).strip()]

    legacy = (directory or Path.cwd()) / LEGACY_HISTORY_FILE
    if legacy.is_file():
        return [line.strip() for line in legacy.read_text().splitlines() if line.strip()]
    return []


def get_previous_commit(directory: Path | None = None) -> str | None:
    history = read_history(directory)
    if len(history) < 2:
        return None
    return history[-2]


def record_commit(commit_id: str, directory: Path | None = None):
    history = read_history(directory)  # migrates legacy history on first write
    if history and history[-1] == commit_id:
        return
    history.append(commit_id)
    data = config.load(directory)
    data["history"] = history
    config.save(data, directory)
