"""Loader for Douyin downloader exports."""

from __future__ import annotations

from pathlib import Path

from intelligence.schema import CanonicalSample

from ._common import build_sample, read_jsonl

__all__ = ["load_samples"]


def load_samples(path: str | Path) -> list[CanonicalSample]:
    rows = read_jsonl(path)
    return [
        build_sample(
            source="douyin_downloader",
            row=row,
            source_id_keys=("aweme_id", "item_id", "video_id"),
            title_keys=("title",),
            text_keys=("desc", "text", "content", "title"),
            url_keys=("share_url", "aweme_url", "url"),
            published_at_keys=("create_time", "publish_time", "time", "published_at"),
            captured_at_keys=("update_time", "last_modify_ts", "captured_at", "crawl_time"),
            tag_keys=("tag_list", "hashtags", "tags"),
        )
        for row in rows
    ]
