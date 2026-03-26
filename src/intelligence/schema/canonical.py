"""Category-neutral canonical content and provenance schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class CanonicalProvenance:
    """Source metadata for a normalized sample."""

    source: str
    source_id: str
    url: str | None = None
    captured_at: datetime | None = None
    published_at: datetime | None = None
    raw_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CanonicalContent:
    """Content fields that belong to the sample itself."""

    text: str
    title: str | None = None
    summary: str | None = None
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CanonicalEngagement:
    """Engagement metrics for a sample."""

    likes: int | None = None
    saves: int | None = None
    comments: int | None = None
    shares: int | None = None


@dataclass(frozen=True, slots=True)
class CanonicalCreator:
    """Creator/author information for a sample."""

    id: str | None = None
    name: str | None = None
    avatar_url: str | None = None
    location: str | None = None


@dataclass(frozen=True, slots=True)
class CanonicalMedia:
    """Media type and URLs for a sample."""

    content_type: str | None = None
    image_urls: tuple[str, ...] = ()
    video_url: str | None = None


@dataclass(frozen=True, slots=True)
class CanonicalSample:
    """Canonical research sample composed only of provenance and content."""

    provenance: CanonicalProvenance
    content: CanonicalContent
    engagement: CanonicalEngagement | None = None
    creator: CanonicalCreator | None = None
    media: CanonicalMedia | None = None
