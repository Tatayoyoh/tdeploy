# CLAUDE.md

## Project overview

**tdeploy** — CLI tool for zero-downtime Docker Compose deployments wrapping [docker-rollout](https://github.com/wowu/docker-rollout).

## Tech stack

- Python 3.11+, managed with `uv`
- `rich` for terminal UI (console, panels, spinners, colors)
- `InquirerPy` for interactive prompts (checkbox multi-select, confirm)
- `PyYAML` for parsing docker-compose files
- `Nuitka` for single-file binary compilation
- `hatchling` as build backend

## Project structure

```
tdeploy/              # Main package
  __init__.py         # __version__ constant
  __main__.py         # python -m tdeploy entry
  cli.py              # sys.argv parsing, dispatch to deploy/rollback/self-upgrade
  ui.py               # Rich Console singleton, print_success/error/warning/step, confirm()
  runner.py           # run() with spinner, run_streaming() for long ops, CommandError exception
  compose.py          # find_compose_file(), parse_services() via PyYAML
  docker_rollout.py   # check_or_install(), rollout_service()
  history.py          # .tdeploy_history read/write/get_previous_commit
  deploy.py           # run_deploy() — main deploy orchestration
  rollback.py         # run_rollback() — checkout previous commit + redeploy
  self_upgrade.py     # run_self_upgrade() — download latest binary from GitHub Releases
```

## Key conventions

- Entry point: `tdeploy.cli:main` (registered in pyproject.toml `[project.scripts]`)
- Single shared `console` instance from `ui.py` — all modules import from there
- Two subprocess modes: `run()` (spinner, capture) vs `run_streaming()` (raw output for build/rollout)
- Manual `sys.argv` parsing in cli.py (no argparse — only 2 commands + 2 flags)
- Lazy imports in cli.py for fast `--version`/`--help`
- History file: `.tdeploy_history` in cwd, one full SHA per line, no consecutive duplicates

## Commands

- `tdeploy` or `tdeploy deploy` — interactive deploy flow
- `tdeploy rollback` — checkout previous commit from history, redeploy (skip git pull)
- `tdeploy self-upgrade` — download latest binary from GitHub Releases
- `tdeploy --version` / `tdeploy --help`

## Development

```bash
uv sync              # Install deps
uv run tdeploy       # Run in dev mode
```

## Build

```bash
sudo apt install patchelf ccache   # Required by Nuitka
uv run python -m nuitka --onefile --python-flag=-m --output-dir=dist --output-filename=tdeploy --include-package=rich._unicode_data tdeploy
```

## Important notes

- docker-rollout requires services to NOT have both `container_name` and `ports` defined
- Rollback puts git in detached HEAD state (expected)
- Sequential rollouts per service (not parallel) to avoid resource contention
- `yaml.safe_load` used (never `yaml.load`) for security
