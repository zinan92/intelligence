"""Tests for the real-pilot prepare_input.py helper."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "designer_streetwear"
    / "real_pilot"
    / "prepare_input.py"
)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
    )


def test_merges_and_deduplicates(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()

    rows_a = [
        {"note_id": "aaa111", "title": "street look", "desc": "nice", "tag_list": "穿搭"},
        {"note_id": "bbb222", "title": "bape haul", "desc": "unbox", "tag_list": "开箱"},
    ]
    rows_b = [
        {"note_id": "aaa111", "title": "street look", "desc": "nice", "tag_list": "穿搭"},
        {"note_id": "ccc333", "title": "vintage fit", "desc": "cool", "tag_list": "复古"},
    ]
    _write_jsonl(src / "search_contents_2026-03-24.jsonl", rows_a)
    _write_jsonl(src / "search_contents_2026-03-25.jsonl", rows_b)

    out = tmp_path / "merged.jsonl"
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(src), "--out", str(out)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    lines = [json.loads(l) for l in out.read_text().strip().splitlines()]
    ids = [r["note_id"] for r in lines]
    assert len(ids) == 3
    assert sorted(ids) == ["aaa111", "bbb222", "ccc333"]


def test_rejects_fake_ids(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()

    rows = [
        {"note_id": "pilot-001", "title": "fake", "desc": "fabricated"},
        {"note_id": "real123abc", "title": "real post", "desc": "legit"},
    ]
    _write_jsonl(src / "search_contents_2026-03-24.jsonl", rows)

    out = tmp_path / "merged.jsonl"
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(src), "--out", str(out)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    lines = [json.loads(l) for l in out.read_text().strip().splitlines()]
    assert len(lines) == 1
    assert lines[0]["note_id"] == "real123abc"
    assert "skipped (fake IDs): 1" in result.stderr


def test_no_files_returns_error(tmp_path: Path) -> None:
    src = tmp_path / "empty"
    src.mkdir()
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(src)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "no search_contents_*.jsonl files found" in result.stderr
