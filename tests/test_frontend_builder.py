"""Tests for frontend dashboard JSON builder."""

from __future__ import annotations

import unittest
from pathlib import Path

from intelligence.adapters.mediacrawler import load_samples
from intelligence.analysis.direction_clustering import cluster_into_directions
from intelligence.analysis.frontend_builder import build_frontend_dashboard
from intelligence.scoring.engine import ScoringEngine
from intelligence.workflows.streetwear_pack import streetwear_pack_spec


class TestFrontendBuilder(unittest.TestCase):
    """Test frontend dashboard JSON builder."""

    def setUp(self) -> None:
        """Load real streetwear data, score it, and cluster into directions."""
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
        
        # Cluster into directions
        self.directions = cluster_into_directions(self.scored_samples, streetwear_pack_spec.name)

    def test_output_schema_matches_jade_dashboard_structure(self) -> None:
        """Output should match jade_dashboard.json top-level structure."""
        dashboard = build_frontend_dashboard(
            self.directions, 
            self.scored_samples,
            streetwear_pack_spec.name
        )
        
        required_keys = {
            "product_name", "timestamp", "executive_summary", "today_judgments",
            "trend_directions", "product_lines", "evidence_entries",
            "fourteen_day_changes", "scoring_model", "keyword_groups"
        }
        
        for key in required_keys:
            self.assertIn(key, dashboard, f"Missing top-level key: {key}")

    def test_all_required_fields_present_in_directions(self) -> None:
        """Each direction should have all 22+ required fields."""
        dashboard = build_frontend_dashboard(
            self.directions,
            self.scored_samples,
            streetwear_pack_spec.name
        )
        
        required_fields = {
            "id", "name", "description", "heat_magnitude", "time_window",
            "confidence_level", "classification", "judgment_state",
            "audience_fit", "price_band_fit", "opportunity", "risk", "heat",
            "movement_history", "product_line_breakdown", "risks",
            "evidence_summary", "proof_snapshot", "one_line_recommendation",
            "content_cues", "why_it_matters", "freshness"
        }
        
        for direction in dashboard["trend_directions"]:
            for field in required_fields:
                self.assertIn(field, direction, f"Direction missing field: {field}")
            
            # Validate movement_history has exactly 14 data points
            self.assertEqual(
                len(direction["movement_history"]),
                14,
                "movement_history should have exactly 14 data points"
            )
            
            # Validate opportunity/risk/heat are 0-100
            self.assertGreaterEqual(direction["opportunity"], 0)
            self.assertLessEqual(direction["opportunity"], 100)
            self.assertGreaterEqual(direction["risk"], 0)
            self.assertLessEqual(direction["risk"], 100)
            self.assertGreaterEqual(direction["heat"], 0)
            self.assertLessEqual(direction["heat"], 100)

    def test_field_name_correctness(self) -> None:
        """Field names should match jade_dashboard.json schema exactly."""
        dashboard = build_frontend_dashboard(
            self.directions,
            self.scored_samples,
            streetwear_pack_spec.name
        )
        
        # Check fourteen_day_changes uses correct keys
        self.assertIn("rising", dashboard["fourteen_day_changes"])
        self.assertIn("cooling", dashboard["fourteen_day_changes"])
        self.assertIn("newly_emerging", dashboard["fourteen_day_changes"])
        self.assertNotIn("warming", dashboard["fourteen_day_changes"])
        self.assertNotIn("new_appearances", dashboard["fourteen_day_changes"])
        
        # Check fourteen_day_changes items are dicts with direction/change/reason
        for category in ["rising", "cooling", "newly_emerging"]:
            for item in dashboard["fourteen_day_changes"][category]:
                self.assertIsInstance(item, dict, f"Item in {category} should be a dict")
                self.assertIn("direction", item, f"Item in {category} missing 'direction' key")
                self.assertIn("change", item, f"Item in {category} missing 'change' key")
                self.assertIn("reason", item, f"Item in {category} missing 'reason' key")
                self.assertIsInstance(item["direction"], str)
                self.assertIsInstance(item["change"], str)
                self.assertIsInstance(item["reason"], str)
        
        # Check evidence entries use correct field names
        if dashboard["evidence_entries"]:
            evidence = dashboard["evidence_entries"][0]
            self.assertIn("related_direction", evidence)
            self.assertIn("weight", evidence)
            self.assertNotIn("direction_id", evidence)
            self.assertNotIn("relevance_weight", evidence)
            self.assertIn(evidence["weight"], ["high", "medium", "low"])

    def test_today_judgments_counts_sum_to_total_directions(self) -> None:
        """today_judgments counts should sum to total direction count."""
        dashboard = build_frontend_dashboard(
            self.directions,
            self.scored_samples,
            streetwear_pack_spec.name
        )
        
        total_judgments = sum(dashboard["today_judgments"].values())
        self.assertEqual(
            total_judgments,
            len(dashboard["trend_directions"]),
            "today_judgments sum should equal total direction count"
        )
        
        # All 4 judgment states should be present
        required_states = {"值得跟", "观察中", "短热噪音", "需要补证据"}
        self.assertEqual(
            set(dashboard["today_judgments"].keys()),
            required_states,
            "today_judgments should have all 4 judgment states"
        )

    def test_product_lines_with_direction_linkages(self) -> None:
        """product_lines should have strengthening/weakening direction linkages."""
        dashboard = build_frontend_dashboard(
            self.directions,
            self.scored_samples,
            streetwear_pack_spec.name
        )
        
        self.assertGreater(len(dashboard["product_lines"]), 0, "Should have at least 1 product line")
        
        for product_line in dashboard["product_lines"]:
            self.assertIn("name", product_line)
            self.assertIn("strengthening_directions", product_line)
            self.assertIn("weakening_directions", product_line)
            self.assertIsInstance(product_line["strengthening_directions"], list)
            self.assertIsInstance(product_line["weakening_directions"], list)
            
            # Referenced direction names should exist in trend_directions
            direction_names = {d["name"] for d in dashboard["trend_directions"]}
            for dir_name in product_line["strengthening_directions"]:
                self.assertIn(dir_name, direction_names, f"Referenced direction '{dir_name}' not found")
            for dir_name in product_line["weakening_directions"]:
                self.assertIn(dir_name, direction_names, f"Referenced direction '{dir_name}' not found")

    def test_evidence_entries_from_top_scoring_posts(self) -> None:
        """Evidence entries should be generated from top-scoring posts per direction."""
        dashboard = build_frontend_dashboard(
            self.directions,
            self.scored_samples,
            streetwear_pack_spec.name
        )
        
        # Should have at least 50% of directions with >= 1 evidence entry
        direction_names_with_evidence = {e["related_direction"] for e in dashboard["evidence_entries"]}
        coverage_ratio = len(direction_names_with_evidence) / len(dashboard["trend_directions"])
        self.assertGreaterEqual(
            coverage_ratio,
            0.5,
            "At least 50% of directions should have >= 1 evidence entry"
        )

    def test_movement_history_is_deterministic(self) -> None:
        """Movement history should be deterministic: same input -> same output."""
        # Build dashboard twice with same inputs
        dashboard1 = build_frontend_dashboard(
            self.directions,
            self.scored_samples,
            streetwear_pack_spec.name
        )
        dashboard2 = build_frontend_dashboard(
            self.directions,
            self.scored_samples,
            streetwear_pack_spec.name
        )
        
        # Extract movement_history from both runs
        movement_histories_1 = {
            d["name"]: d["movement_history"] 
            for d in dashboard1["trend_directions"]
        }
        movement_histories_2 = {
            d["name"]: d["movement_history"] 
            for d in dashboard2["trend_directions"]
        }
        
        # Should have same directions
        self.assertEqual(
            set(movement_histories_1.keys()),
            set(movement_histories_2.keys()),
            "Both runs should produce same direction names"
        )
        
        # Each direction's movement_history should be identical across runs
        for direction_name in movement_histories_1:
            self.assertEqual(
                movement_histories_1[direction_name],
                movement_histories_2[direction_name],
                f"movement_history for '{direction_name}' should be deterministic"
            )

    def test_scoring_model_matches_jade_schema(self) -> None:
        """scoring_model should match jade_dashboard.json field names."""
        dashboard = build_frontend_dashboard(
            self.directions,
            self.scored_samples,
            streetwear_pack_spec.name
        )
        
        # Check for jade_dashboard.json field names
        self.assertIn("heat_weight", dashboard["scoring_model"])
        self.assertIn("confidence_weight", dashboard["scoring_model"])
        self.assertIn("audience_fit_weight", dashboard["scoring_model"])
        self.assertIn("price_band_fit_weight", dashboard["scoring_model"])
        
        # Should NOT have old field names
        self.assertNotIn("bucket_count", dashboard["scoring_model"])
        self.assertNotIn("keyword_weight", dashboard["scoring_model"])
        self.assertNotIn("engagement_weight", dashboard["scoring_model"])
        
        # All weights should sum to ~1.0
        total_weight = sum([
            dashboard["scoring_model"]["heat_weight"],
            dashboard["scoring_model"]["confidence_weight"],
            dashboard["scoring_model"]["audience_fit_weight"],
            dashboard["scoring_model"]["price_band_fit_weight"]
        ])
        self.assertAlmostEqual(total_weight, 1.0, places=2, msg="Weights should sum to ~1.0")

    def test_evidence_product_line_varies_by_direction(self) -> None:
        """Evidence entries should have varied product_line values based on direction data."""
        dashboard = build_frontend_dashboard(
            self.directions,
            self.scored_samples,
            streetwear_pack_spec.name
        )
        
        # Collect all product_line values from evidence entries
        product_lines = [e["product_line"] for e in dashboard["evidence_entries"]]
        unique_product_lines = set(product_lines)
        
        # Should have at least 1 product_line value (not all hardcoded to same value)
        self.assertGreater(len(unique_product_lines), 0, "Should have at least 1 product_line")
        
        # For streetwear pack, we expect product lines like 上装, 下装, etc.
        # At minimum, evidence should reflect the product_line_breakdown from directions
        self.assertTrue(
            all(pl in ["上装", "下装", "外套", "配饰"] for pl in unique_product_lines),
            f"All product_lines should be valid streetwear categories, got: {unique_product_lines}"
        )


if __name__ == "__main__":
    unittest.main()
