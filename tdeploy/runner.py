import subprocess

from tdeploy.ui import console, print_error


class CommandError(Exception):
    def __init__(self, command: str, returncode: int, stderr: str):
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"Command failed: {command} (exit {returncode})")


def run(
    command: list[str],
    status_message: str,
    capture_output: bool = False,
    cwd: str | None = None,
) -> subprocess.CompletedProcess:
    with console.status(f"[bold cyan]{status_message}[/bold cyan]", spinner="dots"):
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=True,
            cwd=cwd,
        )
    if result.returncode != 0:
        print_error(f"Command failed: {' '.join(command)}")
        raise CommandError(" ".join(command), result.returncode, result.stderr or "")
    return result


def run_streaming(
    command: list[str],
    status_message: str,
    cwd: str | None = None,
) -> int:
    console.print(f"  [bold cyan]{status_message}[/bold cyan]")
    result = subprocess.run(command, cwd=cwd)
    return result.returncode
