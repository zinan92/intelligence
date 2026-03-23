"""Tiny jade pack runner used by the CLI and tests."""

from __future__ import annotations

import json
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
from intelligence.scoring.engine import (
    ClassificationRule,
    ConfidenceRule,
    ScoringConfig,
    ScoringEngine,
)

__all__ = ["run_jade_pack"]

_FIXTURE_PATH = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "mediacrawler_jade_export.jsonl"


def _isoformat(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _sample_payload(sample) -> dict[str, object]:
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


def _score_payload(sample, result) -> dict[str, object]:
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


def _bucket_scores(sample) -> dict[str, float]:
    text_parts = [
        sample.content.title or "",
        sample.content.text,
        " ".join(sample.content.tags),
    ]
    text = " ".join(text_parts).lower()

    jade_signal = 1.0 if any(keyword in text for keyword in ("jade", "翡翠")) else 0.0
    modernity = 0.5 if any(keyword in text for keyword in ("design", "modern", "feature")) else 0.0
    commerce = 0.7 if any(keyword in text for keyword in ("pendant", "necklace", "bracelet", "ring")) else 0.0

    return {
        "jade_signal": jade_signal,
        "modernity": modernity,
        "commerce": commerce,
    }


def _scoring_engine() -> ScoringEngine:
    return ScoringEngine(
        ScoringConfig(
            bucket_weights={
                "jade_signal": 0.5,
                "modernity": 0.25,
                "commerce": 0.25,
            },
            confidence_rules=(
                ConfidenceRule(0.8, "high"),
                ConfidenceRule(0.5, "medium"),
                ConfidenceRule(0.25, "low"),
            ),
            classification_rules=(
                ClassificationRule(0.8, "confirmed_continuation"),
                ClassificationRule(0.6, "emerging_opportunity"),
                ClassificationRule(0.3, "watchlist_experiment"),
            ),
            default_confidence="low",
            default_classification="avoid_for_now",
        )
    )


def _build_report(samples, scored_samples, *, fixture_path: Path) -> Report:
    sample_count = len(samples)
    top_sample = samples[0] if samples else None
    top_score = scored_samples[0] if scored_samples else None
    tags = _join_unique(tag for sample in samples for tag in sample.content.tags)

    summary = (
        f"Jade pack demo processed {sample_count} repo-local MediaCrawler sample"
        f"{'s' if sample_count != 1 else ''} and produced a compact jade research report."
    )
    if top_score is not None:
        summary = (
            f"{summary} The top signal scored {top_score['weighted_score']:.2f}"
            f" with {top_score['confidence']} confidence."
        )

    evidence_buckets = (
        ReportBlock(
            title="Fixture Coverage",
            fields=(
                ("sample count", str(sample_count)),
                ("source", "mediacrawler"),
                ("fixture", fixture_path.name),
            ),
            bullets=(
                top_sample.content.title if top_sample and top_sample.content.title else "No title available",
                f"tags: {tags}" if tags else "tags: none",
            ),
        ),
    )

    validation_states = (
        ReportBlock(
            title="Runtime Check",
            fields=(
                ("normalized outputs", str(sample_count)),
                ("scored outputs", str(len(scored_samples))),
                ("report files", "5"),
            ),
            bullets=("fixture-only execution", "shared renderers for JSON, Markdown, and HTML"),
        ),
    )

    trend_clusters = (
        ReportBlock(
            title="Jade Pendant Signal",
            fields=(
                ("weighted score", f"{top_score['weighted_score']:.2f}" if top_score else "0.00"),
                ("confidence", top_score["confidence"] if top_score else "low"),
                ("classification", top_score["classification"] if top_score else "avoid_for_now"),
            ),
            bullets=(
                "category-specific cue: jade + pendant language",
                "kept intentionally small for repo-local validation",
            ),
        ),
    )

    product_priorities = (
        ReportBlock(
            title="Build Now",
            fields=(
                ("direction", "jade pendant feature line"),
                ("why", "the fixture shows a clear, repeatable category cue"),
            ),
            bullets=("use the same pack flow with real collection inputs later",),
        ),
    )

    design_briefs = (
        ReportBlock(
            title="Keep It Compact",
            fields=(
                ("target audience", "jade trend research"),
                ("material mix", "jade, pendant, and modern design cues"),
            ),
            bullets=("avoid overfitting this demo to one fixture", "prefer explicit heuristics over hidden config"),
        ),
    )

    return Report(
        title="Jade Pack Report",
        summary=summary,
        evidence_buckets=evidence_buckets,
        validation_states=validation_states,
        trend_clusters=trend_clusters,
        product_priorities=product_priorities,
        design_briefs=design_briefs,
    )


def run_jade_pack(output_dir: str | Path) -> None:
    """Run the tiny jade pack demo against repo-local fixtures only."""

    discover_project_pack("jade")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    samples = load_samples(_FIXTURE_PATH)
    normalized_samples = [_sample_payload(sample) for sample in samples]

    engine = _scoring_engine()
    scored_samples = [_score_payload(sample, engine.score(_bucket_scores(sample))) for sample in samples]

    report = _build_report(samples, scored_samples, fixture_path=_FIXTURE_PATH)

    _write_json(output_path / "normalized_samples.json", normalized_samples)
    _write_json(output_path / "scored_samples.json", scored_samples)
    _write_json(output_path / "report.json", json.loads(render_json_report(report)))
    (output_path / "report.md").write_text(render_markdown_report(report), encoding="utf-8")
    (output_path / "report.html").write_text(render_html_report(report), encoding="utf-8")
