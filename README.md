# TDeploy

Interactive CLI tool for **zero-downtime** Docker Compose deployments via [docker-rollout](https://github.com/wowu/docker-rollout).

## Features

- Automatic `docker-rollout` installation if missing
- Multi-select checkbox for service selection
- Optional git pull before deployment
- Optional docker compose build
- Rolling deploy service by service (`docker rollout`)
- Deployment history tracking (`.tdeploy_history`)
- One-command rollback to previous commit

## Prerequisites

- Python >= 3.11
- Docker with Docker Compose v2
- Git
- [uv](https://docs.astral.sh/uv/) for project management

## Installation

```bash
uv sync
```

## Usage

### Deploy

```bash
uv run tdeploy
```

Interactive flow:
1. Checks/installs `docker-rollout`
2. Detects `docker-compose.yaml` / `docker-compose.yml` in current directory
3. Presents service selection (multi-select checkbox)
4. Asks whether to git pull
5. Asks whether to docker compose build
6. Runs `docker rollout` for each selected service
7. Records commit ID in `.tdeploy_history`

### Rollback

```bash
uv run tdeploy rollback
```

Checks out the previous commit (from `.tdeploy_history`), then runs the deployment flow without the git pull prompt.

### Other commands

```bash
uv run tdeploy --version
uv run tdeploy --help
```

## Binary build (Nuitka)

System prerequisites:
```bash
sudo apt install patchelf ccache
```

Build:
```bash
uv run python -m nuitka --onefile --python-flag=-m --output-dir=dist --output-filename=tdeploy --include-package=rich._unicode_data tdeploy
```

Produces a standalone `dist/tdeploy` binary you can copy to any server.

## Project structure

```
tdeploy/
  __init__.py          # Version
  __main__.py          # python -m tdeploy
  cli.py               # Arg parsing, command dispatch
  ui.py                # Rich console, display helpers
  runner.py            # Subprocess execution with spinners
  compose.py           # Docker-compose file detection and YAML parsing
  docker_rollout.py    # docker-rollout install/check/execution
  history.py           # .tdeploy_history management
  deploy.py            # Deploy flow orchestration
  rollback.py          # Rollback flow orchestration
```

## Dependencies

| Package | Role |
|---------|------|
| [rich](https://github.com/Textualize/rich) | Terminal UI (panels, spinners, colors) |
| [InquirerPy](https://github.com/kazhala/InquirerPy) | Interactive prompts (checkbox, confirm) |
| [PyYAML](https://github.com/yaml/pyyaml) | Docker-compose YAML parsing |
| [Nuitka](https://nuitka.net/) | Standalone binary compilation |
