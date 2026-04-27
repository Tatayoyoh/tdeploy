from rich.console import Console
from rich.panel import Panel

from tdeploy import __version__

console = Console()


def print_banner():
    console.print(
        Panel(
            f"[bold cyan]tdeploy[/bold cyan] v{__version__}\n"
            "[dim]Zero-downtime Docker Compose deployments[/dim]",
            border_style="cyan",
        )
    )


def print_success(message: str):
    console.print(f"  [bold green]✓[/bold green] {message}")


def print_error(message: str):
    console.print(f"  [bold red]✗[/bold red] {message}")


def print_warning(message: str):
    console.print(f"  [bold yellow]![/bold yellow] {message}")


def print_step(step_num: int, total: int, message: str):
    console.print(f"\n[bold][{step_num}/{total}][/bold] {message}")


def confirm(message: str, default: bool = False) -> bool:
    from InquirerPy import inquirer

    return inquirer.confirm(message=message, default=default).execute()
