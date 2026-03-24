"""Shared pack workflow: load → normalize → score → report → write."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from intelligence.adapters.mediacrawler import load_samples
from intelligence.projects import discover_project_pack
from intelligence.reporting import (
    Report,
    ReportBlock,
    render_html_report,
    render_json_report,
    render_markdown_report,
)
from intelligence.schema import CanonicalSample
from intelligence.scoring.engine import ScoringConfig, ScoringEngine, ScoringResult

__all__ = ["PackSpec", "run_pack_flow"]


@dataclass(frozen=True, slots=True)
class PackSpec:
    """Everything the shared flow needs from a specific pack."""

    name: str
    report_title: str
    fixture_path: Path
    scoring_config: ScoringConfig
    bucket_scores_fn: Callable[[CanonicalSample], dict[str, float]]
    trend_label: str = "Top Signal"
    trend_bullets: tuple[str, ...] = ()
    direction_label: str = ""
    direction_why: str = ""
    audience_label: str = ""
    material_label: str = ""


def run_pack_flow(
    spec: PackSpec,
    output_dir: str | Path,
    *,
    input_path: str | Path | None = None,
) -> None:
    """Execute the shared pack workflow."""

    discover_project_pack(spec.name)

    source_path = Path(input_path) if input_path is not None else spec.fixture_path
    is_fixture = input_path is None

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    samples = load_samples(source_path)
    normalized_samples = [_sample_payload(sample) for sample in samples]

    engine = ScoringEngine(spec.scoring_config)
    scored_samples = [
        _score_payload(sample, engine.score(spec.bucket_scores_fn(sample)))
        for sample in samples
    ]

    report = _build_report(
        spec, samples, scored_samples,
        source_path=source_path,
        is_fixture=is_fixture,
    )

    _write_json(output_path / "normalized_samples.json", normalized_samples)
    _write_json(output_path / "scored_samples.json", scored_samples)
    _write_json(output_path / "report.json", json.loads(render_json_report(report)))
    (output_path / "report.md").write_text(render_markdown_report(report), encoding="utf-8")
    (output_path / "report.html").write_text(render_html_report(report), encoding="utf-8")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _isoformat(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _sample_payload(sample: CanonicalSample) -> dict[str, object]:
    return {
        "provenance": {
            "source": sample.provenance.source,
            "source_id": sample.provenance.source_id,
            "url": sample.provenance.url,
            "captured_at": _isoformat(sample.provenance.captured_at),
            "published_at": _isoformat(sample.provenance.published_at),
            "raw_metadata": sample.provenance.raw_metadata,
        },
        "content": {
            "text": sample.content.text,
            "title": sample.content.title,
            "summary": sample.content.summary,
            "tags": list(sample.content.tags),
        },
    }


def _score_payload(sample: CanonicalSample, result: ScoringResult) -> dict[str, object]:
    return {
        "sample": _sample_payload(sample),
        "bucket_scores": result.bucket_scores,
        "weighted_score": result.weighted_score,
        "confidence": result.confidence,
        "classification": result.classification,
    }


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _join_unique(values: Iterable[str]) -> str:
    items: list[str] = []
    for value in values:
        text = value.strip()
        if text and text not in items:
            items.append(text)
    return ", ".join(items)


def _build_report(
    spec: PackSpec,
    samples: list[CanonicalSample],
    scored_samples: list[dict[str, object]],
    *,
    source_path: Path,
    is_fixture: bool,
) -> Report:
    sample_count = len(samples)
    top_sample = samples[0] if samples else None
    top_score = scored_samples[0] if scored_samples else None
    tags = _join_unique(tag for sample in samples for tag in sample.content.tags)

    summary = (
        f"{spec.report_title.removesuffix(' Report')} pack processed"
        f" {sample_count} MediaCrawler sample"
        f"{'s' if sample_count != 1 else ''} from {source_path.name}"
        f" and produced a compact research report."
    )
    if top_score is not None:
        summary = (
            f"{summary} The top signal scored {top_score['weighted_score']:.2f}"
            f" with {top_score['confidence']} confidence."
        )

    evidence_buckets = (
        ReportBlock(
            title="Fixture Coverage" if is_fixture else "Input Coverage",
            fields=(
                ("sample count", str(sample_count)),
                ("source", "mediacrawler"),
                ("input", source_path.name),
            ),
            bullets=(
                top_sample.content.title if top_sample and top_sample.content.title else "No title available",
                f"tags: {tags}" if tags else "tags: none",
            ),
        ),
    )

    execution_label = "fixture-only execution" if is_fixture else f"user input: {source_path.name}"
    validation_states = (
        ReportBlock(
            title="Runtime Check",
            fields=(
                ("normalized outputs", str(sample_count)),
                ("scored outputs", str(len(scored_samples))),
                ("report files", "5"),
            ),
            bullets=(execution_label, "shared renderers for JSON, Markdown, and HTML"),
        ),
    )

    trend_clusters = (
        ReportBlock(
            title=spec.trend_label,
            fields=(
                ("weighted score", f"{top_score['weighted_score']:.2f}" if top_score else "0.00"),
                ("confidence", top_score["confidence"] if top_score else "low"),
                ("classification", top_score["classification"] if top_score else "avoid_for_now"),
            ),
            bullets=spec.trend_bullets or (
                "category-specific signal detected",
                "kept intentionally small for validation",
            ),
        ),
    )

    product_priorities = (
        ReportBlock(
            title="Build Now",
            fields=(
                ("direction", spec.direction_label or spec.report_title),
                ("why", spec.direction_why or "repeatable category cue detected"),
            ),
            bullets=("use the same pack flow with real collection inputs later",),
        ),
    )

    design_briefs = (
        ReportBlock(
            title="Keep It Compact",
            fields=(
                ("target audience", spec.audience_label or f"{spec.name} trend research"),
                ("material mix", spec.material_label or "category-specific cues"),
            ),
            bullets=("avoid overfitting to one fixture", "prefer explicit heuristics over hidden config"),
        ),
    )

    return Report(
        title=spec.report_title,
        summary=summary,
        evidence_buckets=evidence_buckets,
        validation_states=validation_states,
        trend_clusters=trend_clusters,
        product_priorities=product_priorities,
        design_briefs=design_briefs,
    )
