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


def _pack_paths(root: Path) -> tuple[Path, Path, Path, Path]:
    return (
        root / "config" / "project.yaml",
        root / "keywords" / "seed_keywords.csv",
        root / "templates",
        root / "examples",
    )


def _is_project_pack(root: Path) -> bool:
    config_path, keywords_path, templates_path, _ = _pack_paths(root)
    return config_path.is_file() and keywords_path.is_file() and templates_path.is_dir()


def list_project_packs() -> tuple[str, ...]:
    names = []
    for child in _PACKS_ROOT.iterdir():
        if not child.is_dir():
            continue
        if child.name.startswith("_"):
            continue
        if not _is_project_pack(child):
            continue
        names.append(child.name)
    return tuple(sorted(names))


def discover_project_pack(name: str) -> ProjectPack:
    root = _PACKS_ROOT / name
    if not root.is_dir():
        raise FileNotFoundError(f"unknown project pack: {name}")

    config_path, keywords_path, templates_path, examples_path = _pack_paths(root)

    if not config_path.is_file():
        raise FileNotFoundError(f"missing project pack asset: {config_path}")
    if not keywords_path.is_file():
        raise FileNotFoundError(f"missing project pack asset: {keywords_path}")
    if not templates_path.is_dir():
        raise FileNotFoundError(f"missing project pack asset: {templates_path}")

    return ProjectPack(
        name=name,
        root=root,
        config_path=config_path,
        keywords_path=keywords_path,
        templates_path=templates_path,
        examples_path=examples_path,
    )
