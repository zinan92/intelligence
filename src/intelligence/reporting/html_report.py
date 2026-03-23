"""HTML report rendering."""

from __future__ import annotations

from html import escape
from pathlib import Path
from string import Template

from .model import Report


def _default_template_path() -> Path:
    return Path(__file__).with_name("templates").joinpath("report.html")


def _render_block(block) -> str:
    field_items = "".join(
        f"<li><strong>{escape(label)}</strong>: {escape(value)}</li>"
        for label, value in block.fields
    )
    bullet_items = "".join(f"<li>{escape(bullet)}</li>" for bullet in block.bullets)
    items = field_items + bullet_items
    return f"<section><h3>{escape(block.title)}</h3><ul>{items}</ul></section>"


def _render_section(title: str, blocks: tuple[object, ...]) -> str:
    block_html = "".join(_render_block(block) for block in blocks)
    return f"<section><h2>{escape(title)}</h2>{block_html}</section>"


def render_html_report(report: Report, *, template_path: Path | None = None) -> str:
    path = template_path or _default_template_path()
    template = Template(path.read_text(encoding="utf-8"))
    sections = "".join(
        [
            _render_section("Evidence Buckets", report.evidence_buckets),
            _render_section("Validation States", report.validation_states),
            _render_section("Trend Clusters", report.trend_clusters),
            _render_section("Product Priorities", report.product_priorities),
            _render_section("Design Briefs", report.design_briefs),
        ]
    )
    return template.substitute(
        title=escape(report.title),
        summary=escape(report.summary),
        sections=sections,
    )


render_html = render_html_report

