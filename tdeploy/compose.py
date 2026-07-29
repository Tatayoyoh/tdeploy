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


def classify_services(compose_file: Path, service_names: list[str]) -> tuple[list[str], list[str]]:
    """Split service_names into (buildable, image_based).

    buildable: services that define a 'build:' key (need `docker compose build`).
    image_based: services based on an image only (skip build, always `docker compose pull`).

    A service with both 'build' and 'image' is buildable (image is the build output tag).

    A build-less service whose 'image' tag is the build output of another service in
    the compose file is neither built nor pulled (that tag exists only locally, so a
    pull would fail with 'pull access denied'); it is just rolled out.
    """
    with open(compose_file, "r") as f:
        data = yaml.safe_load(f)

    services = data.get("services", {}) if isinstance(data, dict) else {}

    # Image tags produced locally by a build: service — never pull these.
    built_images = {
        c["image"]
        for c in services.values()
        if isinstance(c, dict) and "build" in c and "image" in c
    }

    buildable = []
    image_based = []
    for name in service_names:
        config = services.get(name)
        if not isinstance(config, dict):
            continue
        if "build" in config:
            buildable.append(name)
        elif "image" in config and config["image"] not in built_images:
            image_based.append(name)

    return buildable, image_based
