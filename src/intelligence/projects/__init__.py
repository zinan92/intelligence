"""Project pack discovery helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = ["ProjectPack", "discover_project_pack", "list_project_packs", "validate_project_pack"]

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


def validate_project_pack(name: str) -> list[str]:
    """Validate a project pack's assets and return a list of errors.

    Returns an empty list when the pack is valid.
    """
    errors: list[str] = []
    root = _PACKS_ROOT / name

    if not root.is_dir():
        return [f"pack directory not found: {name}"]

    config_path, keywords_path, templates_path, _ = _pack_paths(root)

    if not config_path.is_file():
        errors.append(f"missing config: {config_path.relative_to(root)}")

    if not keywords_path.is_file():
        errors.append(f"missing keywords: {keywords_path.relative_to(root)}")
    elif keywords_path.stat().st_size == 0:
        errors.append(f"empty keywords file: {keywords_path.relative_to(root)}")
    else:
        header = keywords_path.read_text(encoding="utf-8").split("\n", 1)[0].strip()
        if "keyword" not in header.lower():
            errors.append(f"keywords file missing header row: {keywords_path.relative_to(root)}")
        else:
            lines = [
                line for line in keywords_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            if len(lines) < 2:
                errors.append(f"keywords file has header but no keyword rows: {keywords_path.relative_to(root)}")

    if not templates_path.is_dir():
        errors.append(f"missing templates directory: {templates_path.relative_to(root)}")
    elif not any(templates_path.iterdir()):
        errors.append(f"templates directory is empty: {templates_path.relative_to(root)}")

    return errors


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
