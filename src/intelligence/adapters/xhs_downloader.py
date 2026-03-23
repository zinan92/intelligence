"""Loader for XHS downloader exports."""

from __future__ import annotations

from pathlib import Path

from intelligence.schema import CanonicalSample

from ._common import build_sample, read_jsonl

__all__ = ["load_samples"]


def load_samples(path: str | Path) -> list[CanonicalSample]:
    rows = read_jsonl(path)
    return [
        build_sample(
            source="xhs_downloader",
            row=row,
            source_id_keys=("note_id", "id"),
            title_keys=("title",),
            text_keys=("desc", "text", "content", "title"),
            url_keys=("note_url", "url", "share_url"),
            published_at_keys=("time", "published_at", "publish_time", "create_time"),
            captured_at_keys=("last_modify_ts", "last_update_time", "captured_at", "crawl_time"),
            tag_keys=("tag_list", "tags"),
        )
        for row in rows
    ]
