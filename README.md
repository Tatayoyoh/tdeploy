# TDeploy

Interactive CLI tool for **zero-downtime** Docker Compose deployments via [docker-rollout](https://github.com/wowu/docker-rollout).

## Features

- Automatic `docker-rollout` installation if missing
- Optional private registry login before pulling (`.tdeploy` config)
- Optional git pull before deployment (compose file re-read afterwards)
- Multi-select checkbox for service selection (auto-selected when only one service)
- Optional docker compose build
- Rolling deploy service by service (`docker rollout`)
- Deployment history tracking (`.tdeploy`)
- One-command rollback to previous commit

Interactive rollout flow:
1. Checks/installs `docker-rollout`
2. Logs in to the registry if credentials are set in `.tdeploy`
3. Detects `docker-compose.yaml` / `docker-compose.yml` in current directory
4. Asks whether to git pull (before selection, so the compose file is up to date)
5. Presents service selection (multi-select checkbox; auto-selected if only one)
6. Asks whether to docker compose build
7. Runs `docker rollout` for each selected service
8. Records commit ID in `.tdeploy`

## Installation

### Quick install (prebuilt binary)

```bash
curl -LsSf https://raw.githubusercontent.com/Tatayoyoh/tdeploy/main/install.sh | sh
```

Downloads the latest release binary to `~/.local/bin/tdeploy`.

Server Prerequisites
- Docker with Docker Compose v2
- Git

## Usage

**Deploy**
```bash
tdeploy
```

**Rollback**
```bash
tdeploy rollback
```

Checks out the previous commit (from `.tdeploy`), then runs the deployment flow without the git pull prompt.

## Configuration (`.tdeploy`)

`tdeploy` keeps its state and optional settings in a single `.tdeploy` YAML file in the current directory. It is created/updated automatically and should be **gitignored** (it may hold a registry token).

```yaml
# Optional — auto docker login before pulling private images.
# Omit this block entirely to rely on an existing `docker login`.
registry:
  login: myuser
  token: dckr_pat_xxxxx   # use a scoped, read-only access token
  url:                    # empty = Docker Hub; else e.g. registry.example.com

# Machine-managed — deployment history, oldest first.
history:
  - <commit-sha>
```

Notes:
- The token is passed to `docker login` via `--password-stdin` (never on the command line). `chmod 600 .tdeploy` and gitignore it.
- The file is rewritten on each recorded deploy, so hand-written comments are not preserved.
- A legacy `.tdeploy_history` file (one SHA per line) is still read as a fallback and migrated into `.tdeploy` on the next deploy.

## Development

```bash
uv sync
ln -s docker-compose-sample.yaml docker-compose.yaml
docker compose up -d
uv run tdeploy
```

Host Prerequisites
- Python >= 3.11
- Docker with Docker Compose v2
- Git
- [uv](https://docs.astral.sh/uv/) for project management

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


