from tdeploy.deploy import run_deploy
from tdeploy.history import get_previous_commit, read_history
from tdeploy.runner import CommandError, run
from tdeploy.ui import console, print_banner, print_error, print_step, print_success


def run_rollback():
    print_banner()

    # 1. Read history
    print_step(1, 3, "Reading deployment history...")
    previous = get_previous_commit()

    if previous is None:
        history = read_history()
        if not history:
            print_error("No deployment history found. Cannot rollback.")
        else:
            print_error("Only one deployment recorded. No previous version to rollback to.")
        raise SystemExit(1)

    console.print(f"  Rolling back to commit: [bold yellow]{previous[:12]}[/bold yellow]")

    # 2. Checkout previous commit
    print_step(2, 3, "Checking out previous commit...")
    try:
        run(
            ["git", "checkout", previous],
            status_message=f"Checking out {previous[:12]}...",
        )
        print_success(f"Checked out {previous[:12]}")
    except CommandError as e:
        print_error(f"Git checkout failed: {e.stderr}")
        raise SystemExit(1)

    # 3. Deploy (skip git pull)
    print_step(3, 3, "Starting rollback deployment...")
    run_deploy(skip_git_pull=True)
