from __future__ import annotations

import unittest

from intelligence.scoring import (
    ClassificationRule,
    ConfidenceRule,
    ScoringConfig,
    ScoringEngine,
)


class ScoringEngineTests(unittest.TestCase):
    def test_score_uses_bucket_weights_and_rule_sets(self) -> None:
        engine = ScoringEngine(
            ScoringConfig(
                bucket_weights={"signal_a": 0.6, "signal_b": 0.4},
                confidence_rules=(
                    ConfidenceRule(minimum_score=4.0, label="high"),
                    ConfidenceRule(minimum_score=3.0, label="medium"),
                ),
                classification_rules=(
                    ClassificationRule(minimum_score=4.0, label="confirmed"),
                    ClassificationRule(minimum_score=2.5, label="watchlist"),
                ),
            )
        )

        result = engine.score({"signal_a": 5, "signal_b": 3})

        self.assertEqual(result.weighted_score, 4.2)
        self.assertEqual(result.confidence, "high")
        self.assertEqual(result.classification, "confirmed")
        self.assertEqual(result.bucket_scores, {"signal_a": 5, "signal_b": 3})

    def test_score_falls_back_to_default_labels_when_no_rule_matches(self) -> None:
        engine = ScoringEngine(
            ScoringConfig(
                bucket_weights={"signal_a": 1.0},
                confidence_rules=(ConfidenceRule(minimum_score=4.0, label="high"),),
                classification_rules=(
                    ClassificationRule(minimum_score=4.0, label="confirmed"),
                ),
                default_confidence="low",
                default_classification="unclassified",
            )
        )

        result = engine.score({"signal_a": 1})

        self.assertEqual(result.weighted_score, 1.0)
        self.assertEqual(result.confidence, "low")
        self.assertEqual(result.classification, "unclassified")


if __name__ == "__main__":
    unittest.main()
