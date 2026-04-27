from pathlib import Path

from tdeploy.runner import run

HISTORY_FILE = ".tdeploy_history"


def get_current_commit() -> str:
    result = run(
        ["git", "rev-parse", "HEAD"],
        status_message="Reading current commit...",
        capture_output=True,
    )
    return result.stdout.strip()


def read_history(directory: Path | None = None) -> list[str]:
    history_path = (directory or Path.cwd()) / HISTORY_FILE
    if not history_path.is_file():
        return []
    return [line.strip() for line in history_path.read_text().splitlines() if line.strip()]


def get_previous_commit(directory: Path | None = None) -> str | None:
    history = read_history(directory)
    if len(history) < 2:
        return None
    return history[-2]


def record_commit(commit_id: str, directory: Path | None = None):
    history_path = (directory or Path.cwd()) / HISTORY_FILE
    history = read_history(directory)
    if history and history[-1] == commit_id:
        return
    with open(history_path, "a") as f:
        f.write(commit_id + "\n")
