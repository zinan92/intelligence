"""Markdown report rendering."""

from __future__ import annotations

from .model import Report


def _render_block(block) -> str:
    lines = [f"### {block.title}"]
    for label, value in block.fields:
        lines.append(f"- {label}: {value}")
    for bullet in block.bullets:
        lines.append(f"- {bullet}")
    return "\n".join(lines)


def _render_section(title: str, blocks: tuple[object, ...]) -> str:
    lines = [f"## {title}"]
    for block in blocks:
        lines.append(_render_block(block))
    return "\n\n".join(lines)


def render_markdown_report(report: Report) -> str:
    sections = [
        f"# {report.title}",
        report.summary,
        _render_section("Evidence Buckets", report.evidence_buckets),
        _render_section("Validation States", report.validation_states),
        _render_section("Trend Clusters", report.trend_clusters),
        _render_section("Product Priorities", report.product_priorities),
        _render_section("Design Briefs", report.design_briefs),
    ]
    return "\n\n".join(sections) + "\n"


render_markdown = render_markdown_report

