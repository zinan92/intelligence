"""Designer streetwear pack: category-specific scoring and config."""

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

__all__ = ["streetwear_pack_spec", "run_streetwear_pack"]

_FIXTURE_PATH = (
    Path(__file__).resolve().parents[3]
    / "tests" / "fixtures" / "mediacrawler_streetwear_export.jsonl"
)

# ---- keyword sets for heuristic scoring ----

_SILHOUETTE_KEYWORDS = (
    "oversized", "oversize", "boxy", "wide-leg", "wide leg", "baggy",
    "relaxed", "loose", "boyfriend", "straight-leg", "廓形", "宽松",
    "阔腿", "落肩", "直筒", "silhouette",
    # added from real-data pilot — common in actual XHS streetwear posts
    "ootd", "街拍", "fit check", "fitcheck",
)

_GRAPHIC_KEYWORDS = (
    "graphic", "print", "logo", "embroidered", "embroidery", "slogan",
    "graffiti", "印花", "涂鸦", "标语", "字母", "卡通", "图案",
    # added from real-data pilot
    "潮流", "美式复古",
)

_LAYERING_KEYWORDS = (
    "layering", "layer", "outfit", "穿搭", "叠穿", "叠戴", "混搭",
    "内搭", "外穿", "搭配",
)

_BRAND_KEYWORDS = (
    "nike", "stussy", "supreme", "off-white", "bape", "undercover",
    "sacai", "fear of god", "essentials", "palm angels", "ambush",
    "潮牌", "联名", "collab", "限定", "国潮", "设计师",
)

_MATERIAL_KEYWORDS = (
    "nylon", "denim", "corduroy", "fleece", "mesh", "gore-tex",
    "尼龙", "丹宁", "灯芯绒", "卫衣", "冲锋衣", "机能",
    "网眼", "工装",
    # added from real-data pilot
    "机能风", "工装裤",
)

_COMMERCE_KEYWORDS = (
    "buy", "bought", "purchase", "price", "worth", "review", "unbox",
    "值得", "购物", "开箱", "测评", "推荐", "入手", "性价比",
    "collected_count", "save",
)


def _bucket_scores(sample: CanonicalSample) -> dict[str, float]:
    text_parts = [
        sample.content.title or "",
        sample.content.text,
        " ".join(sample.content.tags),
    ]
    text = " ".join(text_parts).lower()

    # Keyword-based buckets
    silhouette = 1.0 if any(kw in text for kw in _SILHOUETTE_KEYWORDS) else 0.0
    graphic = 0.8 if any(kw in text for kw in _GRAPHIC_KEYWORDS) else 0.0
    layering = 0.7 if any(kw in text for kw in _LAYERING_KEYWORDS) else 0.0
    brand = 0.6 if any(kw in text for kw in _BRAND_KEYWORDS) else 0.0
    material = 0.5 if any(kw in text for kw in _MATERIAL_KEYWORDS) else 0.0
    commerce = 0.5 if any(kw in text for kw in _COMMERCE_KEYWORDS) else 0.0

    # Engagement-based buckets
    engagement_buckets = compute_engagement_buckets(sample.engagement)

    return {
        "silhouette": silhouette,
        "graphic": graphic,
        "layering": layering,
        "brand": brand,
        "material": material,
        "commerce": commerce,
        **engagement_buckets,
    }


_SCORING_CONFIG = ScoringConfig(
    bucket_weights={
        # Keyword buckets (70% total weight - remain dominant)
        "silhouette": 0.15,
        "graphic": 0.10,
        "layering": 0.15,
        "brand": 0.10,
        "material": 0.08,
        "commerce": 0.12,
        # Engagement buckets (30% total weight - meaningful differentiation)
        "interaction_strength": 0.15,
        "commercial_intent": 0.10,
        "propagation_velocity": 0.05,
    },
    # NOTE: The 70/30 keyword-to-engagement weight split means posts with engagement=None
    # max out at ~70% of possible score. These confidence thresholds are calibrated for
    # the full scoring model. Posts without engagement data can still reach "high" confidence
    # (0.7 threshold) if they have strong keyword signals across multiple buckets. This design
    # intentionally incentivizes having engagement data while not completely penalizing posts
    # that lack it.
    confidence_rules=(
        ConfidenceRule(0.7, "high"),
        ConfidenceRule(0.4, "medium"),
        ConfidenceRule(0.2, "low"),
    ),
    classification_rules=(
        ClassificationRule(0.7, "strong_trend_signal"),
        ClassificationRule(0.5, "emerging_pattern"),
        ClassificationRule(0.25, "weak_signal"),
    ),
    default_confidence="low",
    default_classification="noise",
)


streetwear_pack_spec = PackSpec(
    name="designer_streetwear",
    report_title="Designer Streetwear Pack Report",
    fixture_path=_FIXTURE_PATH,
    scoring_config=_SCORING_CONFIG,
    bucket_scores_fn=_bucket_scores,
    trend_label="Streetwear Style Signal",
    trend_bullets=(
        "silhouette, graphic, and layering cues detected",
        "brand and commerce signals used as supporting evidence",
    ),
    direction_label="designer streetwear trend line",
    direction_why="social content shows repeatable style and outfit composition patterns",
    audience_label="streetwear trend research",
    material_label="silhouette, graphic language, layering, and brand cues",
)


def run_streetwear_pack(
    output_dir: str | Path,
    *,
    input_path: str | Path | None = None,
) -> None:
    """Run the designer streetwear pack flow via the shared runner."""
    run_pack_flow(streetwear_pack_spec, output_dir, input_path=input_path)
