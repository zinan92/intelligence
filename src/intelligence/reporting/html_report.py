"""HTML report rendering."""

from __future__ import annotations

import re
from html import escape
from pathlib import Path
from string import Template

from .model import Report

_URL_RE = re.compile(r"(https?://[^\s<>\"]+)")

_SECTION_CSS = {
    "Evidence Buckets": "evidence-buckets",
    "Validation States": "validation-states",
    "Trend Clusters": "trend-clusters",
    "Product Priorities": "product-priorities",
    "Design Briefs": "design-briefs",
}


def _default_template_path() -> Path:
    return Path(__file__).with_name("templates").joinpath("report.html")


def _linkify(escaped_text: str) -> str:
    """Turn URLs in already-escaped text into clickable links."""
    return _URL_RE.sub(
        r'<a href="\1" target="_blank" rel="noopener">\1</a>',
        escaped_text,
    )


def _render_field_grid(fields: tuple) -> str:
    if not fields:
        return '<div class="field-grid"></div>'
    items = "".join(
        f'<div class="field">'
        f'<span class="label">{escape(label)}</span>'
        f'<span class="value">{escape(value)}</span>'
        f"</div>"
        for label, value in fields
    )
    return f'<div class="field-grid">{items}</div>'


def _render_bullets(bullets: tuple) -> str:
    if not bullets:
        return ""
    items = "".join(
        f"<li>{_linkify(escape(bullet))}</li>" for bullet in bullets
    )
    return f'<ul class="bullets">{items}</ul>'


def _render_block(block) -> str:
    return (
        f'<div class="card">'
        f"<h3>{escape(block.title)}</h3>"
        f"{_render_field_grid(block.fields)}"
        f"{_render_bullets(block.bullets)}"
        f"</div>"
    )


def _render_section(title: str, blocks: tuple[object, ...]) -> str:
    if not blocks:
        return ""
    css_class = _SECTION_CSS.get(title, "")
    block_html = "".join(_render_block(block) for block in blocks)
    cls = f"report-section {css_class}" if css_class else "report-section"
    return f'<section class="{cls}"><h2>{escape(title)}</h2>{block_html}</section>'


def _extract_hero_metrics(report: Report) -> str:
    """Build a score-bar div from the first trend_clusters block."""
    if not report.trend_clusters:
        return ""
    fields: dict[str, str] = {}
    for label, value in report.trend_clusters[0].fields:
        key = label.lower().replace(" ", "_")
        if key in ("weighted_score", "confidence", "classification"):
            fields[key] = value

    if not fields:
        return ""

    parts: list[str] = []
    if "weighted_score" in fields:
        parts.append(
            f'<span class="badge score">{escape(fields["weighted_score"])}</span>'
        )
    if "confidence" in fields:
        level = fields["confidence"].lower()
        parts.append(
            f'<span class="badge confidence confidence-{escape(level)}">'
            f"{escape(fields['confidence'])}</span>"
        )
    if "classification" in fields:
        parts.append(
            f'<span class="badge classification">'
            f"{escape(fields['classification'])}</span>"
        )
    return f'<div class="score-bar">{"".join(parts)}</div>'


def render_html_report(report: Report, *, template_path: Path | None = None) -> str:
    path = template_path or _default_template_path()
    template = Template(path.read_text(encoding="utf-8"))

    hero_metrics = _extract_hero_metrics(report)

    sections = "".join(
        [
            _render_section("Evidence Buckets", report.evidence_buckets),
            _render_section("Validation States", report.validation_states),
            _render_section("Trend Clusters", report.trend_clusters),
            _render_section("Product Priorities", report.product_priorities),
            _render_section("Design Briefs", report.design_briefs),
        ]
    )
    return template.safe_substitute(
        title=escape(report.title),
        summary=escape(report.summary),
        hero_metrics=hero_metrics,
        sections=sections,
    )


render_html = render_html_report
