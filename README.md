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

Interactive rollout flow:
1. Checks/installs `docker-rollout`
2. Detects `docker-compose.yaml` / `docker-compose.yml` in current directory
3. Presents service selection (multi-select checkbox)
4. Asks whether to git pull
5. Asks whether to docker compose build
6. Runs `docker rollout` for each selected service
7. Records commit ID in `.tdeploy_history`

## Prerequisites

- Python >= 3.11
- Docker with Docker Compose v2
- Git
- [uv](https://docs.astral.sh/uv/) for project management

## Installation

### Quick install (prebuilt binary)

```bash
curl -LsSf https://raw.githubusercontent.com/Tatayoyoh/tdeploy/main/install.sh | sh
```

Downloads the latest release binary to `~/.local/bin/tdeploy`.

## Usage

**Deploy**
```bash
tdeploy
```

**Rollback**
```bash
tdeploy rollback
```

Checks out the previous commit (from `.tdeploy_history`), then runs the deployment flow without the git pull prompt.

## Development

```bash
uv sync
ln -s docker-compose-sample.yaml docker-compose.yaml
docker compose up -d
uv run tdeploy
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


