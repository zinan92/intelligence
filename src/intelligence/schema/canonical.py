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
class CanonicalSample:
    """Canonical research sample composed only of provenance and content."""

    provenance: CanonicalProvenance
    content: CanonicalContent
