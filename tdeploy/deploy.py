from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from tdeploy.compose import ComposeFileNotFoundError, find_compose_file, parse_services
from tdeploy.docker_rollout import check_or_install, rollout_service
from tdeploy.history import get_current_commit, record_commit
from tdeploy.registry import login_if_configured
from tdeploy.runner import CommandError, run_streaming
from tdeploy.ui import confirm, console, print_banner, print_error, print_step, print_success, print_warning


def select_services(services: list[str]) -> list[str]:
    # Single service -> nothing to choose, auto-select it.
    if len(services) == 1:
        console.print("  [dim]Only one service available — auto-selected.[/dim]")
        return list(services)
    return inquirer.checkbox(
        message="Select services to deploy:",
        choices=[Choice(value=s, name=s) for s in services],
        validate=lambda result: len(result) >= 1,
        invalid_message="Select at least one service.",
        instruction="(Space = toggle, Enter = confirm)",
    ).execute()


def run_deploy(skip_git_pull: bool = False):
    print_banner()

    # 1. docker-rollout check
    print_step(1, 6, "Checking docker-rollout...")
    check_or_install()
    print_success("docker-rollout ready")

    # Optional registry login from .tdeploy (no-op if not configured)
    login_if_configured()

    # 2. Find compose file
    print_step(2, 6, "Finding compose file...")
    try:
        compose_file = find_compose_file()
    except ComposeFileNotFoundError as e:
        print_error(str(e))
        raise SystemExit(1)

    console.print(f"  Found: [bold]{compose_file.name}[/bold]")

    # 3. Git pull (before service selection, so the compose file is up to date)
    if not skip_git_pull:
        if confirm("Git pull?", default=True):
            print_step(3, 6, "Pulling latest changes...")
            exit_code = run_streaming(["git", "pull"], status_message="Running git pull...")
            if exit_code != 0:
                print_error("Git pull failed.")
                raise SystemExit(1)
            print_success("Git pull complete")

    # 4. Parse services (after the pull) and select
    print_step(4, 6, "Service selection")
    services, excluded = parse_services(compose_file)

    if excluded:
        print_warning(
            "Excluded from rollout (incompatible with docker-rollout):"
        )
        for name, reasons in excluded.items():
            console.print(f"    [dim]- {name} ({', '.join(reasons)})[/dim]")

    if not services:
        print_error("No eligible services found in compose file.")
        raise SystemExit(1)

    selected = select_services(services)
    console.print(f"  Selected: [bold cyan]{', '.join(selected)}[/bold cyan]")

    # 5. Docker compose build
    if confirm("Docker compose build?", default=True):
        print_step(5, 6, "Building services...")
        build_cmd = ["docker", "compose", "-f", str(compose_file), "build"] + selected
        exit_code = run_streaming(build_cmd, status_message="Building images...")
        if exit_code != 0:
            print_error("Docker compose build failed.")
            raise SystemExit(1)
        print_success("Build complete")

    # 6. Rolling deploy
    print_step(6, 6, "Deploying services...")
    failed = []
    for service in selected:
        exit_code = rollout_service(compose_file, service)
        if exit_code == 0:
            print_success(f"'{service}' rolled out")
        else:
            print_error(f"'{service}' rollout failed")
            failed.append(service)

    if failed:
        print_error(f"Failed services: {', '.join(failed)}")
        raise SystemExit(1)

    # Record commit
    try:
        commit_id = get_current_commit()
        record_commit(commit_id)
        print_success(f"Deployment recorded: {commit_id[:12]}")
    except CommandError:
        print_warning("Could not record commit (not a git repo?)")

    console.print("\n[bold green]Deployment complete![/bold green]")
