"""Shared reporting data model."""

from __future__ import annotations

from dataclasses import dataclass, field


FieldPair = tuple[str, str]


@dataclass(frozen=True, slots=True)
class ReportBlock:
    """A named report section with key/value fields and optional bullets."""

    title: str
    fields: tuple[FieldPair, ...] = field(default_factory=tuple)
    bullets: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class Report:
    """Structured report content for JSON, Markdown, and HTML renderers."""

    title: str
    summary: str
    evidence_buckets: tuple[ReportBlock, ...] = field(default_factory=tuple)
    validation_states: tuple[ReportBlock, ...] = field(default_factory=tuple)
    trend_clusters: tuple[ReportBlock, ...] = field(default_factory=tuple)
    product_priorities: tuple[ReportBlock, ...] = field(default_factory=tuple)
    design_briefs: tuple[ReportBlock, ...] = field(default_factory=tuple)
