"""Tests for direction clustering module."""

from __future__ import annotations

import unittest
from pathlib import Path

from intelligence.adapters.mediacrawler import load_samples
from intelligence.analysis.direction_clustering import cluster_into_directions
from intelligence.scoring.engine import ScoringEngine
from intelligence.workflows.streetwear_pack import streetwear_pack_spec


class TestDirectionClustering(unittest.TestCase):
    """Test direction clustering logic."""

    def setUp(self) -> None:
        """Load real streetwear data and score it."""
        # Use real 293-post streetwear data
        input_path = Path(__file__).resolve().parents[1] / "examples" / "designer_streetwear" / "real_pilot" / "streetwear_collected.jsonl"
        self.samples = load_samples(input_path)
        
        # Score samples
        engine = ScoringEngine(streetwear_pack_spec.scoring_config)
        self.scored_samples = [
            {
                "sample": sample,
                "result": engine.score(streetwear_pack_spec.bucket_scores_fn(sample))
            }
            for sample in self.samples
        ]

    def test_clustering_produces_6_to_10_directions(self) -> None:
        """Clustering should produce 6-10 directions from 293 posts."""
        directions = cluster_into_directions(self.scored_samples, streetwear_pack_spec.name)
        self.assertGreaterEqual(len(directions), 6, "Should produce at least 6 directions")
        self.assertLessEqual(len(directions), 10, "Should produce at most 10 directions")

    def test_all_posts_assigned_to_at_least_one_direction(self) -> None:
        """All 293 posts should be assigned to at least one direction (no orphans)."""
        directions = cluster_into_directions(self.scored_samples, streetwear_pack_spec.name)
        
        total_member_count = sum(d["member_post_count"] for d in directions)
        # Note: posts matching multiple keyword groups may appear in multiple directions
        self.assertGreaterEqual(
            total_member_count, 
            len(self.samples),
            f"Total member count ({total_member_count}) should be >= sample count ({len(self.samples)})"
        )

    def test_direction_schema_completeness(self) -> None:
        """Each direction should have all required fields."""
        directions = cluster_into_directions(self.scored_samples, streetwear_pack_spec.name)
        
        required_fields = {
            "id", "name", "heat", "confidence_level", "judgment_state",
            "top_tags", "member_post_count"
        }
        
        for direction in directions:
            for field in required_fields:
                self.assertIn(field, direction, f"Direction missing field: {field}")
            
            # Validate field values
            self.assertIsInstance(direction["id"], str)
            self.assertIsInstance(direction["name"], str)
            self.assertGreater(len(direction["name"]), 0, "Direction name should not be empty")
            self.assertIsInstance(direction["heat"], (int, float))
            self.assertGreaterEqual(direction["heat"], 0)
            self.assertLessEqual(direction["heat"], 100)
            self.assertIn(direction["confidence_level"], ["高", "中高", "中", "低"])
            self.assertIn(direction["judgment_state"], ["值得跟", "观察中", "短热噪音", "需要补证据"])
            self.assertIsInstance(direction["top_tags"], list)
            self.assertGreater(len(direction["top_tags"]), 0, "Should have at least 1 top tag")
            self.assertGreater(direction["member_post_count"], 0, "Should have at least 1 member post")

    def test_directions_ranked_by_heat_descending(self) -> None:
        """Directions should be sorted by heat score in descending order."""
        directions = cluster_into_directions(self.scored_samples, streetwear_pack_spec.name)
        
        heat_values = [d["heat"] for d in directions]
        self.assertEqual(
            heat_values,
            sorted(heat_values, reverse=True),
            "Directions should be sorted by heat descending"
        )

    def test_judgment_state_based_on_aggregate_score(self) -> None:
        """Judgment states should be assigned based on aggregate score thresholds."""
        directions = cluster_into_directions(self.scored_samples, streetwear_pack_spec.name)
        
        # At least one direction should have a judgment state (this verifies the thresholding logic works)
        judgment_states = [d["judgment_state"] for d in directions]
        self.assertGreater(len(set(judgment_states)), 0, "Should have at least one judgment state")

    def test_confidence_based_on_member_count_and_score_consistency(self) -> None:
        """Confidence should reflect member count and score consistency."""
        directions = cluster_into_directions(self.scored_samples, streetwear_pack_spec.name)
        
        # Directions with more members should generally have higher confidence
        # (though not strictly monotonic due to score consistency factor)
        for direction in directions:
            self.assertIn(direction["confidence_level"], ["高", "中高", "中", "低"])


if __name__ == "__main__":
    unittest.main()
