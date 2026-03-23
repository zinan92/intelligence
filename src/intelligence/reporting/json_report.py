"""JSON report rendering."""

from __future__ import annotations

import json

from .model import Report


def _block_payload(block) -> dict[str, object]:
    return {
        "title": block.title,
        "fields": [{"label": label, "value": value} for label, value in block.fields],
        "bullets": list(block.bullets),
    }


def _report_payload(report: Report) -> dict[str, object]:
    return {
        "title": report.title,
        "summary": report.summary,
        "evidence_buckets": [_block_payload(block) for block in report.evidence_buckets],
        "validation_states": [_block_payload(block) for block in report.validation_states],
        "trend_clusters": [_block_payload(block) for block in report.trend_clusters],
        "product_priorities": [_block_payload(block) for block in report.product_priorities],
        "design_briefs": [_block_payload(block) for block in report.design_briefs],
    }


def render_json_report(report: Report) -> str:
    return json.dumps(_report_payload(report), indent=2, ensure_ascii=False)


render_json = render_json_report

