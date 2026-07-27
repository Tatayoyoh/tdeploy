import subprocess
from pathlib import Path

from tdeploy import config
from tdeploy.ui import console, print_error, print_success


def login_if_configured(directory: Path | None = None) -> None:
    """Run `docker login` when registry credentials are set in .tdeploy.

    Reads the `registry` block (login / token / url). No-op when login or token
    is absent (falls back to whatever `docker login` the user already did).
    Empty/absent url targets Docker Hub. The token is passed via stdin
    (--password-stdin), never on the command line.
    """
    registry = config.load(directory).get("registry") or {}
    login = registry.get("login")
    token = registry.get("token")
    url = registry.get("url")  # empty/None -> Docker Hub

    if not login or not token:
        return

    label = url or "Docker Hub"
    cmd = ["docker", "login", "-u", str(login), "--password-stdin"]
    if url:
        cmd.append(str(url))

    with console.status(f"[bold cyan]Logging in to {label}...[/bold cyan]", spinner="dots"):
        result = subprocess.run(cmd, input=str(token), text=True, capture_output=True)

    if result.returncode != 0:
        print_error(f"Docker login to {label} failed: {result.stderr.strip()}")
        raise SystemExit(1)
    print_success(f"Logged in to {label} as {login}")
