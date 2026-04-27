import os
import stat
from pathlib import Path

from tdeploy.runner import run, run_streaming
from tdeploy.ui import confirm, print_error, print_success, print_warning

PLUGIN_PATH = Path.home() / ".docker" / "cli-plugins" / "docker-rollout"
INSTALL_URL = "https://raw.githubusercontent.com/wowu/docker-rollout/main/docker-rollout"


def is_installed() -> bool:
    return PLUGIN_PATH.is_file() and os.access(PLUGIN_PATH, os.X_OK)


def install():
    PLUGIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    run(
        ["curl", "-fsSL", INSTALL_URL, "-o", str(PLUGIN_PATH)],
        status_message="Downloading docker-rollout...",
    )
    PLUGIN_PATH.chmod(PLUGIN_PATH.stat().st_mode | stat.S_IEXEC)
    print_success("docker-rollout installed")


def check_or_install():
    if is_installed():
        return
    print_warning("docker-rollout is not installed.")
    if confirm("Install docker-rollout now?", default=True):
        install()
    else:
        print_error("docker-rollout is required. Aborting.")
        raise SystemExit(1)


def rollout_service(compose_file: Path, service: str) -> int:
    return run_streaming(
        ["docker", "rollout", "-f", str(compose_file), service],
        status_message=f"Rolling out {service}...",
    )
