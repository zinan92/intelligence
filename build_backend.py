"""Minimal local build backend for offline editable installs.

This backend keeps the repository self-contained and avoids any network fetches
for build requirements. It supports editable installs by publishing a wheel
that adds the `src/` directory to `sys.path` through a `.pth` file.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

NAME = "intelligence"
VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST_INFO = f"{NAME}-{VERSION}.dist-info"
WHEEL_NAME = f"{NAME}-{VERSION}-py3-none-any.whl"


def _metadata() -> str:
    return (
        "Metadata-Version: 2.1\n"
        f"Name: {NAME}\n"
        f"Version: {VERSION}\n"
        "Summary: Multi-category research engine for collected social content\n"
    )


def _wheel_file_bytes() -> dict[str, bytes]:
    entry_points = (
        "[console_scripts]\n"
        "intelligence = intelligence.cli:main\n"
    )
    files: dict[str, bytes] = {
        f"{NAME}.pth": (str(SRC) + os.linesep).encode(),
        f"{DIST_INFO}/METADATA": _metadata().encode(),
        f"{DIST_INFO}/WHEEL": (
            "Wheel-Version: 1.0\n"
            "Generator: intelligence.build_backend\n"
            "Root-Is-Purelib: true\n"
            "Tag: py3-none-any\n"
        ).encode(),
        f"{DIST_INFO}/entry_points.txt": entry_points.encode(),
        f"{DIST_INFO}/top_level.txt": f"{NAME}\n".encode(),
    }
    return files


def _record_bytes(files: dict[str, bytes]) -> bytes:
    rows: list[list[str]] = []
    for path, data in sorted(files.items()):
        digest = hashlib.sha256(data).digest()
        b64 = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        rows.append([path, f"sha256={b64}", str(len(data))])
    rows.append([f"{DIST_INFO}/RECORD", "", ""])
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerows(rows)
    return buffer.getvalue().encode()


def _build_wheel(wheel_directory: str) -> str:
    wheel_path = Path(wheel_directory) / WHEEL_NAME
    files = _wheel_file_bytes()
    files[f"{DIST_INFO}/RECORD"] = _record_bytes(files)

    wheel_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(wheel_path, "w", compression=ZIP_DEFLATED) as zf:
        for path, data in files.items():
            zf.writestr(path, data)
    return WHEEL_NAME


def get_requires_for_build_wheel(config_settings=None):  # noqa: D401
    return []


def get_requires_for_build_editable(config_settings=None):  # noqa: D401
    return []


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    dist_info = Path(metadata_directory) / DIST_INFO
    dist_info.mkdir(parents=True, exist_ok=True)
    (dist_info / "METADATA").write_text(_metadata(), encoding="utf-8")
    (dist_info / "WHEEL").write_text(
        "Wheel-Version: 1.0\n"
        "Generator: intelligence.build_backend\n"
        "Root-Is-Purelib: true\n"
        "Tag: py3-none-any\n",
        encoding="utf-8",
    )
    (dist_info / "entry_points.txt").write_text(
        "[console_scripts]\nintelligence = intelligence.cli:main\n",
        encoding="utf-8",
    )
    (dist_info / "top_level.txt").write_text(f"{NAME}\n", encoding="utf-8")
    return DIST_INFO


def prepare_metadata_for_build_editable(metadata_directory, config_settings=None):
    return prepare_metadata_for_build_wheel(metadata_directory, config_settings)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    return _build_wheel(wheel_directory)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    return _build_wheel(wheel_directory)
