import sys

from tdeploy import __version__


def main():
    try:
        _dispatch(sys.argv[1:])
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(130)


def _dispatch(args: list[str]):
    if "--version" in args or "-v" in args:
        print(f"tdeploy {__version__}")
        return

    if "--help" in args or "-h" in args:
        _print_help()
        return

    if not args or args[0] == "deploy":
        from tdeploy.deploy import run_deploy

        run_deploy()
    elif args[0] == "rollback":
        from tdeploy.rollback import run_rollback

        run_rollback()
    else:
        from tdeploy.ui import print_error

        print_error(f"Unknown command: {args[0]}")
        _print_help()
        sys.exit(1)


def _print_help():
    from tdeploy.ui import console

    console.print("[bold]tdeploy[/bold] — Zero-downtime Docker Compose deployments\n")
    console.print("[bold]Usage:[/bold]")
    console.print("  tdeploy              Deploy services (default)")
    console.print("  tdeploy rollback     Rollback to previous deployment")
    console.print("  tdeploy --version    Show version")
    console.print("  tdeploy --help       Show this help")
