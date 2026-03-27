"""Shared pack workflow: load → normalize → score → report → write."""

from __future__ import annotations

import json
import statistics
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from intelligence.adapters.mediacrawler import load_samples
from intelligence.analysis import build_frontend_dashboard, cluster_into_directions
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
    
    # Prepare scored samples with both sample and result for clustering
    scored_samples_for_clustering = [
        {"sample": sample, "result": engine.score(spec.bucket_scores_fn(sample))}
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
    
    # Generate dashboard.json
    dashboard = _build_dashboard(spec.name, samples, scored_samples)
    _write_json(output_path / "dashboard.json", dashboard)
    
    # Generate frontend_dashboard.json (new)
    directions = cluster_into_directions(scored_samples_for_clustering, spec.name)
    frontend_dashboard = build_frontend_dashboard(directions, scored_samples_for_clustering, spec.name)
    _write_json(output_path / "frontend_dashboard.json", frontend_dashboard)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _isoformat(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _sample_payload(sample: CanonicalSample) -> dict[str, object]:
    payload: dict[str, object] = {
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
    
    # Add engagement if present
    if sample.engagement is not None:
        payload["engagement"] = {
            "likes": sample.engagement.likes,
            "saves": sample.engagement.saves,
            "comments": sample.engagement.comments,
            "shares": sample.engagement.shares,
        }
    
    # Add creator if present
    if sample.creator is not None:
        payload["creator"] = {
            "id": sample.creator.id,
            "name": sample.creator.name,
            "avatar_url": sample.creator.avatar_url,
            "location": sample.creator.location,
        }
    
    # Add media if present
    if sample.media is not None:
        payload["media"] = {
            "content_type": sample.media.content_type,
            "image_urls": list(sample.media.image_urls),
            "video_url": sample.media.video_url,
        }
    
    return payload


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


def _build_dashboard(
    pack_name: str,
    samples: list[CanonicalSample],
    scored_samples: list[dict[str, object]],
) -> dict[str, object]:
    """Build dashboard.json payload with samples and aggregation summaries."""
    
    # Build dashboard samples with structured fields
    dashboard_samples = []
    for scored in scored_samples:
        sample = scored["sample"]
        dashboard_sample: dict[str, object] = {
            "title": sample.get("content", {}).get("title"),
            "content": sample.get("content", {}).get("text"),
            "tags": sample.get("content", {}).get("tags", []),
            "engagement": sample.get("engagement"),
            "creator": sample.get("creator"),
            "media": sample.get("media"),
            "score": {
                "weighted_score": scored["weighted_score"],
                "bucket_scores": scored["bucket_scores"],
                "confidence": scored["confidence"],
                "classification": scored["classification"],
            },
        }
        dashboard_samples.append(dashboard_sample)
    
    # Calculate summary statistics
    summary = _calculate_summary(samples, scored_samples)
    
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pack_name": pack_name,
        "total_count": len(samples),
        "summary": summary,
        "samples": dashboard_samples,
    }


def _calculate_summary(
    samples: list[CanonicalSample],
    scored_samples: list[dict[str, object]],
) -> dict[str, object]:
    """Calculate aggregation summaries for dashboard."""
    
    # Tag frequency
    tag_frequency: dict[str, int] = {}
    for sample in samples:
        for tag in sample.content.tags:
            tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
    
    # Score distribution
    weighted_scores = [scored["weighted_score"] for scored in scored_samples]
    if weighted_scores:
        score_distribution = {
            "min": min(weighted_scores),
            "max": max(weighted_scores),
            "mean": statistics.mean(weighted_scores),
            "median": statistics.median(weighted_scores),
        }
    else:
        score_distribution = {
            "min": 0.0,
            "max": 0.0,
            "mean": 0.0,
            "median": 0.0,
        }
    
    # Engagement range
    likes_list: list[int] = []
    saves_list: list[int] = []
    for sample in samples:
        if sample.engagement is not None:
            if sample.engagement.likes is not None:
                likes_list.append(sample.engagement.likes)
            if sample.engagement.saves is not None:
                saves_list.append(sample.engagement.saves)
    
    engagement_range = {
        "min_likes": min(likes_list) if likes_list else None,
        "max_likes": max(likes_list) if likes_list else None,
        "min_saves": min(saves_list) if saves_list else None,
        "max_saves": max(saves_list) if saves_list else None,
    }
    
    return {
        "tag_frequency": tag_frequency,
        "score_distribution": score_distribution,
        "engagement_range": engagement_range,
    }


def _build_report(
    spec: PackSpec,
    samples: list[CanonicalSample],
    scored_samples: list[dict[str, object]],
    *,
    source_path: Path,
    is_fixture: bool,
) -> Report:
    sample_count = len(samples)

    if scored_samples:
        top_idx = max(range(len(scored_samples)), key=lambda i: scored_samples[i]["weighted_score"])
        top_sample = samples[top_idx]
        top_score = scored_samples[top_idx]
    else:
        top_sample = None
        top_score = None
    tags = _join_unique(tag for sample in samples for tag in sample.content.tags)

    pack_label = spec.report_title.removesuffix(" Report").removesuffix(" Pack")
    summary = (
        f"{pack_label} pack processed"
        f" {sample_count} MediaCrawler sample"
        f"{'s' if sample_count != 1 else ''} from {source_path.name}"
        f" and produced a compact research report."
    )
    if top_score is not None:
        summary = (
            f"{summary} The top signal scored {top_score['weighted_score']:.2f}"
            f" with {top_score['confidence']} confidence."
        )

    evidence_bullets: list[str] = [
        top_sample.content.title if top_sample and top_sample.content.title else "No title available",
        f"tags: {tags}" if tags else "tags: none",
    ]
    source_urls = [
        sample.provenance.url
        for sample in samples
        if sample.provenance.url
    ]
    if source_urls:
        evidence_bullets.extend(source_urls[:5])
        if len(source_urls) > 5:
            evidence_bullets.append(f"... and {len(source_urls) - 5} more sources")

    evidence_buckets = (
        ReportBlock(
            title="Fixture Coverage" if is_fixture else "Input Coverage",
            fields=(
                ("sample count", str(sample_count)),
                ("source", "mediacrawler"),
                ("input", source_path.name),
            ),
            bullets=tuple(evidence_bullets),
        ),
    )

    execution_label = "fixture-only execution" if is_fixture else f"user input: {source_path.name}"
    validation_states = (
        ReportBlock(
            title="Runtime Check",
            fields=(
                ("normalized outputs", str(sample_count)),
                ("scored outputs", str(len(scored_samples))),
                ("report files", "6"),
            ),
            bullets=(execution_label, "shared renderers for JSON, Markdown, HTML, and dashboard.json"),
        ),
    )

    trend_clusters = (
        ReportBlock(
            title=spec.trend_label,
            fields=(
                ("weighted score", f"{top_score['weighted_score']:.2f}" if top_score else "0.00"),
                ("confidence", top_score["confidence"] if top_score else spec.scoring_config.default_confidence),
                ("classification", top_score["classification"] if top_score else spec.scoring_config.default_classification),
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
