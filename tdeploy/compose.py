from pathlib import Path

import yaml

COMPOSE_FILENAMES = [
    "docker-compose.yaml",
    "docker-compose.yml",
    "compose.yaml",
    "compose.yml",
]


class ComposeFileNotFoundError(Exception):
    pass


def find_compose_file(directory: Path | None = None) -> Path:
    search_dir = directory or Path.cwd()
    for name in COMPOSE_FILENAMES:
        candidate = search_dir / name
        if candidate.is_file():
            return candidate
    raise ComposeFileNotFoundError(
        f"No compose file found in {search_dir}. "
        f"Expected one of: {', '.join(COMPOSE_FILENAMES)}"
    )


def parse_services(compose_file: Path) -> tuple[list[str], dict[str, list[str]]]:
    """Parse compose file and return (eligible_services, excluded_services).

    excluded_services maps service name to list of reasons (e.g. ["container_name", "ports"]).
    Services with container_name or ports are incompatible with docker-rollout.
    """
    with open(compose_file, "r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "services" not in data:
        raise ValueError(f"Invalid compose file: no 'services' key in {compose_file}")

    eligible = []
    excluded: dict[str, list[str]] = {}

    for name, config in sorted(data["services"].items()):
        if not isinstance(config, dict):
            eligible.append(name)
            continue
        reasons = []
        if "container_name" in config:
            reasons.append("container_name")
        if "ports" in config:
            reasons.append("ports")
        if reasons:
            excluded[name] = reasons
        else:
            eligible.append(name)

    return eligible, excluded
