"""Shared helpers for adapter loaders."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from intelligence.schema import (
    CanonicalContent,
    CanonicalCreator,
    CanonicalEngagement,
    CanonicalMedia,
    CanonicalProvenance,
    CanonicalSample,
)


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


def parse_chinese_number(value: Any) -> int | None:
    """Parse Chinese abbreviated numbers like '10万+' or '2.1万' to integers.
    
    Handles:
    - '10万+' → 100000 (万 = 10000, strip trailing +)
    - '2.1万' → 21000 (decimal 万)
    - '1.5千' → 1500 (千 = 1000)
    - '9196' → 9196 (plain digits)
    - None, '', whitespace → None
    - non-numeric → None
    """
    if value is None:
        return None
    
    if isinstance(value, (int, float)):
        return int(value)
    
    if not isinstance(value, str):
        value = str(value)
    
    text = value.strip()
    if not text:
        return None
    
    # Remove trailing + suffix
    if text.endswith("+"):
        text = text[:-1].strip()
    
    # Check for 万 (10K) or 千 (1K)
    if "万" in text:
        try:
            number_part = text.replace("万", "").strip()
            base = float(number_part)
            return round(base * 10000)
        except (ValueError, TypeError):
            return None
    elif "千" in text:
        try:
            number_part = text.replace("千", "").strip()
            base = float(number_part)
            return round(base * 1000)
        except (ValueError, TypeError):
            return None
    else:
        # Plain digit string
        try:
            return int(float(text))
        except (ValueError, TypeError):
            return None


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
    engagement_keys: Mapping[str, Sequence[str]] | None = None,
    creator_keys: Mapping[str, Sequence[str]] | None = None,
    media_keys: Mapping[str, Sequence[str]] | None = None,
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

    # Extract engagement if keys provided
    engagement: CanonicalEngagement | None = None
    if engagement_keys:
        likes = parse_chinese_number(first_value(row, engagement_keys.get("likes", ())))
        saves = parse_chinese_number(first_value(row, engagement_keys.get("saves", ())))
        comments = parse_chinese_number(first_value(row, engagement_keys.get("comments", ())))
        shares = parse_chinese_number(first_value(row, engagement_keys.get("shares", ())))
        if any(v is not None for v in (likes, saves, comments, shares)):
            engagement = CanonicalEngagement(likes=likes, saves=saves, comments=comments, shares=shares)

    # Extract creator if keys provided
    creator: CanonicalCreator | None = None
    if creator_keys:
        creator_id = first_value(row, creator_keys.get("id", ()))
        name = first_value(row, creator_keys.get("name", ()))
        avatar_url = first_value(row, creator_keys.get("avatar_url", ()))
        location = first_value(row, creator_keys.get("location", ()))
        if any(v is not None for v in (creator_id, name, avatar_url, location)):
            creator = CanonicalCreator(
                id=str(creator_id) if creator_id is not None else None,
                name=str(name) if name is not None else None,
                avatar_url=str(avatar_url) if avatar_url is not None else None,
                location=str(location) if location is not None else None,
            )

    # Extract media if keys provided
    media: CanonicalMedia | None = None
    if media_keys:
        content_type = first_value(row, media_keys.get("content_type", ()))
        image_list = first_value(row, media_keys.get("image_urls", ()))
        video_url = first_value(row, media_keys.get("video_url", ()))
        
        # Parse image_urls from comma-separated string to tuple
        image_urls: tuple[str, ...] = ()
        if image_list:
            images = str(image_list).split(",")
            image_urls = tuple(img.strip() for img in images if img.strip())
        
        if any(v is not None for v in (content_type, video_url)) or image_urls:
            media = CanonicalMedia(
                content_type=str(content_type) if content_type is not None else None,
                image_urls=image_urls,
                video_url=str(video_url) if video_url is not None else None,
            )

    return CanonicalSample(
        provenance=provenance,
        content=content,
        engagement=engagement,
        creator=creator,
        media=media,
    )
