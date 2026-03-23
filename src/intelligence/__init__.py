"""intelligence package."""

from __future__ import annotations

from importlib import metadata
from pathlib import Path
import tomllib

__all__ = ["__version__"]


def _project_version() -> str:
    try:
        return metadata.version("intelligence")
    except metadata.PackageNotFoundError:
        root = Path(__file__).resolve().parents[2]
        return tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"][
            "version"
        ]


__version__ = _project_version()
