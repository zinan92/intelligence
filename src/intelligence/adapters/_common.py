"""Shared helpers for adapter loaders."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from intelligence.schema import CanonicalContent, CanonicalProvenance, CanonicalSample


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def first_value(row: Mapping[str, Any], keys: Sequence[str]) -> Any:
    for key in keys:
        if key not in row:
            continue
        value = row[key]
        if value is not None and value != "":
            return value
    return None


def parse_datetime(value: Any) -> datetime | None:
    if value is None or value == "":
        return None

    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)

    if isinstance(value, (int, float)):
        timestamp = float(value)
        if abs(timestamp) >= 1_000_000_000_000:
            timestamp /= 1000.0
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None

        try:
            return parse_datetime(float(text))
        except ValueError:
            pass

        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None

    return None


def parse_tags(value: Any) -> tuple[str, ...]:
    if value is None or value == "":
        return ()

    if isinstance(value, str):
        parts: Sequence[Any] = value.split(",")
    elif isinstance(value, (list, tuple, set)):
        parts = value
    else:
        parts = (value,)

    tags: list[str] = []
    for part in parts:
        text = str(part).strip()
        if text:
            tags.append(text)
    return tuple(tags)


def build_sample(
    *,
    source: str,
    row: Mapping[str, Any],
    source_id_keys: Sequence[str],
    title_keys: Sequence[str] = (),
    text_keys: Sequence[str] = (),
    url_keys: Sequence[str] = (),
    published_at_keys: Sequence[str] = (),
    captured_at_keys: Sequence[str] = (),
    tag_keys: Sequence[str] = (),
) -> CanonicalSample:
    source_id = first_value(row, source_id_keys)
    if source_id is None:
        raise ValueError(f"missing source id for {source}")

    title = first_value(row, title_keys)
    text = first_value(row, text_keys)
    if text is None:
        text = title or ""

    provenance = CanonicalProvenance(
        source=source,
        source_id=str(source_id),
        url=first_value(row, url_keys),
        captured_at=parse_datetime(first_value(row, captured_at_keys)),
        published_at=parse_datetime(first_value(row, published_at_keys)),
        raw_metadata=dict(row),
    )
    content = CanonicalContent(
        text=str(text),
        title=str(title) if title is not None else None,
        tags=parse_tags(first_value(row, tag_keys)),
    )
    return CanonicalSample(provenance=provenance, content=content)
