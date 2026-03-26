"""Loader for MediaCrawler jade exports."""

from __future__ import annotations

from pathlib import Path

from intelligence.schema import CanonicalSample

from ._common import build_sample, read_jsonl

__all__ = ["load_samples"]


def load_samples(path: str | Path) -> list[CanonicalSample]:
    rows = read_jsonl(path)
    return [
        build_sample(
            source="mediacrawler",
            row=row,
            source_id_keys=("note_id",),
            title_keys=("title",),
            text_keys=("desc", "text", "content", "title"),
            url_keys=("note_url", "url"),
            published_at_keys=("time", "published_at", "publish_time", "create_time"),
            captured_at_keys=("last_modify_ts", "last_update_time", "captured_at", "crawl_time"),
            tag_keys=("tag_list", "tags"),
            engagement_keys={
                "likes": ("liked_count",),
                "saves": ("collected_count",),
                "comments": ("comment_count",),
                "shares": ("share_count",),
            },
            creator_keys={
                "id": ("user_id",),
                "name": ("nickname",),
                "avatar_url": ("avatar",),
                "location": ("ip_location",),
            },
            media_keys={
                "content_type": ("type",),
                "image_urls": ("image_list",),
                "video_url": ("video_url",),
            },
        )
        for row in rows
    ]
