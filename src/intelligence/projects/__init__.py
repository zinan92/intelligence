"""Project pack discovery helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = ["ProjectPack", "discover_project_pack", "list_project_packs"]

_PACKS_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True, slots=True)
class ProjectPack:
    """File-based project pack contract."""

    name: str
    root: Path
    config_path: Path
    keywords_path: Path
    templates_path: Path
    examples_path: Path


def list_project_packs() -> tuple[str, ...]:
    names = []
    for child in _PACKS_ROOT.iterdir():
        if not child.is_dir():
            continue
        if child.name.startswith("_"):
            continue
        if not (child / "__init__.py").is_file():
            continue
        names.append(child.name)
    return tuple(sorted(names))


def discover_project_pack(name: str) -> ProjectPack:
    root = _PACKS_ROOT / name
    if not root.is_dir():
        raise FileNotFoundError(f"unknown project pack: {name}")

    config_path = root / "config" / "project.yaml"
    keywords_path = root / "keywords" / "seed_keywords.csv"
    templates_path = root / "templates"
    examples_path = root / "examples"

    for required_path in (config_path, keywords_path, templates_path):
        if not required_path.exists():
            raise FileNotFoundError(f"missing project pack asset: {required_path}")

    return ProjectPack(
        name=name,
        root=root,
        config_path=config_path,
        keywords_path=keywords_path,
        templates_path=templates_path,
        examples_path=examples_path,
    )
