"""Jade pack: category-specific scoring and config for the shared pack flow."""

from __future__ import annotations

from pathlib import Path

from intelligence.schema import CanonicalSample
from intelligence.scoring.engine import (
    ClassificationRule,
    ConfidenceRule,
    ScoringConfig,
)
from intelligence.scoring.engagement_buckets import compute_engagement_buckets

from .pack_runner import PackSpec, run_pack_flow

__all__ = ["jade_pack_spec", "run_jade_pack"]

_FIXTURE_PATH = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "mediacrawler_jade_export.jsonl"


def _bucket_scores(sample: CanonicalSample) -> dict[str, float]:
    text_parts = [
        sample.content.title or "",
        sample.content.text,
        " ".join(sample.content.tags),
    ]
    text = " ".join(text_parts).lower()

    # Keyword-based buckets
    jade_signal = 1.0 if any(kw in text for kw in ("jade", "翡翠")) else 0.0
    modernity = 0.5 if any(kw in text for kw in ("design", "modern", "feature")) else 0.0
    commerce = 0.7 if any(kw in text for kw in ("pendant", "necklace", "bracelet", "ring")) else 0.0

    # Engagement-based buckets
    engagement_buckets = compute_engagement_buckets(sample.engagement)

    return {
        "jade_signal": jade_signal,
        "modernity": modernity,
        "commerce": commerce,
        **engagement_buckets,
    }


_SCORING_CONFIG = ScoringConfig(
    bucket_weights={
        # Keyword buckets (70% total weight - remain dominant)
        "jade_signal": 0.40,
        "modernity": 0.15,
        "commerce": 0.15,
        # Engagement buckets (30% total weight - meaningful differentiation)
        "interaction_strength": 0.15,
        "commercial_intent": 0.10,
        "propagation_velocity": 0.05,
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


jade_pack_spec = PackSpec(
    name="jade",
    report_title="Jade Pack Report",
    fixture_path=_FIXTURE_PATH,
    scoring_config=_SCORING_CONFIG,
    bucket_scores_fn=_bucket_scores,
    trend_label="Jade Pendant Signal",
    trend_bullets=(
        "category-specific cue: jade + pendant language",
        "kept intentionally small for repo-local validation",
    ),
    direction_label="jade pendant feature line",
    direction_why="the fixture shows a clear, repeatable category cue",
    audience_label="jade trend research",
    material_label="jade, pendant, and modern design cues",
)


def run_jade_pack(
    output_dir: str | Path,
    *,
    input_path: str | Path | None = None,
) -> None:
    """Run the jade pack flow via the shared runner."""
    run_pack_flow(jade_pack_spec, output_dir, input_path=input_path)
