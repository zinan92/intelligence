#!/usr/bin/env python3
"""Merge and validate MediaCrawler search outputs into a single pilot input.

Usage:
    python prepare_input.py <dir_with_jsonl_files> [--out streetwear_collected.jsonl]

Reads all search_contents_*.jsonl files from the given directory, deduplicates
by note_id, validates minimum field presence, and writes one merged JSONL file.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


_REQUIRED_FIELDS = ("note_id", "title")
_FAKE_ID_PREFIXES = ("pilot-", "sw-note-", "test-", "example-")


def _is_fake(note_id: str) -> bool:
    lower = note_id.lower()
    return any(lower.startswith(p) for p in _FAKE_ID_PREFIXES)


def main() -> int:
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <jsonl_dir> [--out output.jsonl]", file=sys.stderr)
        return 1

    source_dir = Path(sys.argv[1])
    out_path = Path("streetwear_collected.jsonl")

    if "--out" in sys.argv:
        idx = sys.argv.index("--out")
        if idx + 1 < len(sys.argv):
            out_path = Path(sys.argv[idx + 1])

    files = sorted(source_dir.glob("search_contents_*.jsonl"))
    if not files:
        print(f"error: no search_contents_*.jsonl files found in {source_dir}", file=sys.stderr)
        return 1

    seen_ids: set[str] = set()
    rows: list[dict[str, object]] = []
    skipped_fake = 0
    skipped_missing = 0
    skipped_dupe = 0

    for f in files:
        print(f"  reading {f.name} ...", file=sys.stderr)
        for line_num, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                print(f"  warning: {f.name}:{line_num} invalid JSON, skipped", file=sys.stderr)
                continue

            note_id = str(row.get("note_id", ""))
            if not note_id:
                skipped_missing += 1
                continue
            if _is_fake(note_id):
                skipped_fake += 1
                continue
            if not all(row.get(k) for k in _REQUIRED_FIELDS):
                skipped_missing += 1
                continue
            if note_id in seen_ids:
                skipped_dupe += 1
                continue

            seen_ids.add(note_id)
            rows.append(row)

    print(f"\n  collected: {len(rows)} unique posts", file=sys.stderr)
    if skipped_fake:
        print(f"  skipped (fake IDs): {skipped_fake}", file=sys.stderr)
    if skipped_dupe:
        print(f"  skipped (duplicates): {skipped_dupe}", file=sys.stderr)
    if skipped_missing:
        print(f"  skipped (missing fields): {skipped_missing}", file=sys.stderr)

    if len(rows) < 50:
        print(
            f"\n  WARNING: only {len(rows)} posts collected. "
            f"Minimum viable pilot needs 50+.",
            file=sys.stderr,
        )

    keywords = set()
    for row in rows:
        kw = row.get("source_keyword", "")
        if kw:
            keywords.add(kw)
    if keywords:
        print(f"  keyword coverage: {', '.join(sorted(keywords))}", file=sys.stderr)

    out_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )
    print(f"\n  wrote {out_path} ({len(rows)} posts)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
