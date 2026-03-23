"""Category-neutral scoring engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ConfidenceRule:
    """Confidence label selected when a score crosses a threshold."""

    minimum_score: float
    label: str


@dataclass(frozen=True, slots=True)
class ClassificationRule:
    """Classification label selected when a score crosses a threshold."""

    minimum_score: float
    label: str


@dataclass(frozen=True, slots=True)
class ScoringConfig:
    """Configuration for a scoring engine."""

    bucket_weights: Mapping[str, float]
    confidence_rules: tuple[ConfidenceRule, ...] = field(default_factory=tuple)
    classification_rules: tuple[ClassificationRule, ...] = field(default_factory=tuple)
    default_confidence: str = "low"
    default_classification: str = "unclassified"


@dataclass(frozen=True, slots=True)
class ScoringResult:
    """Result of a scoring run."""

    bucket_scores: dict[str, float]
    weighted_score: float
    confidence: str
    classification: str


class ScoringEngine:
    """Calculate weighted scores and map them to labels."""

    def __init__(self, config: ScoringConfig) -> None:
        self._config = config

    def score(self, bucket_scores: Mapping[str, float]) -> ScoringResult:
        weighted_score = self._weighted_score(bucket_scores)
        return ScoringResult(
            bucket_scores=dict(bucket_scores),
            weighted_score=weighted_score,
            confidence=self.confidence_for(weighted_score),
            classification=self.classification_for(weighted_score),
        )

    def confidence_for(self, score: float) -> str:
        return self._label_for(score, self._config.confidence_rules, self._config.default_confidence)

    def classification_for(self, score: float) -> str:
        return self._label_for(
            score,
            self._config.classification_rules,
            self._config.default_classification,
        )

    def _weighted_score(self, bucket_scores: Mapping[str, float]) -> float:
        if not bucket_scores:
            return 0.0

        total_weight = 0.0
        total_score = 0.0
        for bucket, value in bucket_scores.items():
            weight = self._config.bucket_weights[bucket]
            total_weight += weight
            total_score += float(value) * weight

        if total_weight == 0.0:
            return 0.0

        return round(total_score / total_weight, 2)

    @staticmethod
    def _label_for(score: float, rules: tuple[object, ...], default: str) -> str:
        for rule in sorted(rules, key=lambda item: item.minimum_score, reverse=True):
            if score >= rule.minimum_score:
                return rule.label
        return default
