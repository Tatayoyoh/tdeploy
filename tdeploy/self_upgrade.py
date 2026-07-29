import json
import os
import stat
import sys
import tempfile
import urllib.request
from pathlib import Path

from tdeploy import __version__
from tdeploy.ui import console, print_error, print_success, print_warning

REPO = "Tatayoyoh/tdeploy"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
ASSET_NAME = "tdeploy-linux-x86_64"


def _get_latest_release() -> tuple[str, str]:
    """Return (version_tag, asset_download_url) for latest release."""
    req = urllib.request.Request(API_URL, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())

    tag = data["tag_name"]  # e.g. "v0.4.0"
    for asset in data.get("assets", []):
        if asset["name"] == ASSET_NAME:
            return tag, asset["browser_download_url"]

    raise RuntimeError(f"Asset '{ASSET_NAME}' not found in release {tag}")


def _current_binary_path() -> Path:
    """Return path of running tdeploy binary."""
    # Nuitka defines the `__compiled__` module global only in compiled builds.
    if "__compiled__" not in globals():
        # Running via `uv run` / `python -m` — not a compiled binary
        raise RuntimeError(
            "self-upgrade only works with the compiled binary, not via python/uv"
        )
    # Nuitka onefile extracts its payload to a temp dir and runs it there, so
    # sys.executable points at the extracted payload, not the launched binary.
    # NUITKA_ONEFILE_BINARY holds the path of the actual onefile binary.
    onefile = os.environ.get("NUITKA_ONEFILE_BINARY")
    if onefile:
        return Path(onefile).resolve()
    return Path(sys.executable).resolve()


def run_self_upgrade():
    console.print(f"\n  Current version: [bold]{__version__}[/bold]")

    # Fetch latest release info
    with console.status("[bold cyan]Checking latest release...[/bold cyan]", spinner="dots"):
        try:
            tag, download_url = _get_latest_release()
        except Exception as e:
            print_error(f"Failed to check latest release: {e}")
            raise SystemExit(1)

    latest_version = tag.lstrip("v")
    console.print(f"  Latest version:  [bold]{latest_version}[/bold]")

    if latest_version == __version__:
        print_success("Already up to date.")
        return

    # Resolve binary path
    try:
        binary_path = _current_binary_path()
    except RuntimeError as e:
        print_error(str(e))
        raise SystemExit(1)

    # Check write permission
    if not os.access(binary_path, os.W_OK):
        print_error(f"No write permission on {binary_path}. Try with sudo.")
        raise SystemExit(1)

    # Download to temp file in same directory (same filesystem for atomic rename)
    target_dir = binary_path.parent
    try:
        with console.status("[bold cyan]Downloading...[/bold cyan]", spinner="dots"):
            fd, tmp_path = tempfile.mkstemp(dir=target_dir, prefix=".tdeploy_upgrade_")
            os.close(fd)
            urllib.request.urlretrieve(download_url, tmp_path)

        # Preserve original permissions, ensure executable
        original_mode = binary_path.stat().st_mode
        os.chmod(tmp_path, original_mode | stat.S_IEXEC)

        # Atomic replace
        os.replace(tmp_path, binary_path)
        print_success(f"Upgraded: {__version__} → {latest_version}")

    except Exception as e:
        # Cleanup temp file on failure
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        print_error(f"Upgrade failed: {e}")
        raise SystemExit(1)
