from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from intelligence.cli import main


class DashboardOutputTests(unittest.TestCase):
    """Tests for dashboard.json output generation."""

    def test_dashboard_json_is_generated_by_pack_runner(self) -> None:
        """VAL-DASH-001: dashboard.json is generated alongside existing outputs."""
        with TemporaryDirectory() as tmpdir:
            exit_code = main(["run-pack", "jade", "--output-dir", tmpdir])
            self.assertEqual(exit_code, 0)

            output_dir = Path(tmpdir)
            dashboard_path = output_dir / "dashboard.json"
            self.assertTrue(dashboard_path.is_file(), "dashboard.json should exist")

    def test_all_six_output_files_exist(self) -> None:
        """VAL-DASH-004: All 5 existing files plus dashboard.json are generated."""
        with TemporaryDirectory() as tmpdir:
            exit_code = main(["run-pack", "jade", "--output-dir", tmpdir])
            self.assertEqual(exit_code, 0)

            output_dir = Path(tmpdir)
            expected_files = (
                "normalized_samples.json",
                "scored_samples.json",
                "report.json",
                "report.md",
                "report.html",
                "dashboard.json",
            )
            for filename in expected_files:
                self.assertTrue((output_dir / filename).is_file(), f"{filename} should exist")

    def test_dashboard_json_contains_required_structure(self) -> None:
        """VAL-DASH-002: dashboard.json contains samples with structured fields."""
        with TemporaryDirectory() as tmpdir:
            exit_code = main(["run-pack", "jade", "--output-dir", tmpdir])
            self.assertEqual(exit_code, 0)

            dashboard = json.loads(
                (Path(tmpdir) / "dashboard.json").read_text(encoding="utf-8")
            )

            # Check top-level structure
            self.assertIn("generated_at", dashboard)
            self.assertIn("pack_name", dashboard)
            self.assertIn("total_count", dashboard)
            self.assertIn("samples", dashboard)
            self.assertIn("summary", dashboard)

            self.assertEqual(dashboard["pack_name"], "jade")
            self.assertGreater(len(dashboard["generated_at"]), 0)
            self.assertIsInstance(dashboard["samples"], list)
            self.assertIsInstance(dashboard["summary"], dict)

    def test_dashboard_samples_have_structured_fields(self) -> None:
        """VAL-DASH-002: Samples have engagement/creator/media as top-level fields."""
        with TemporaryDirectory() as tmpdir:
            exit_code = main(["run-pack", "jade", "--output-dir", tmpdir])
            self.assertEqual(exit_code, 0)

            dashboard = json.loads(
                (Path(tmpdir) / "dashboard.json").read_text(encoding="utf-8")
            )

            self.assertGreater(len(dashboard["samples"]), 0)
            sample = dashboard["samples"][0]

            # Each sample should have basic content fields
            self.assertIn("title", sample)
            self.assertIn("content", sample)
            self.assertIn("tags", sample)
            self.assertIn("score", sample)

            # Score should have structure
            self.assertIn("weighted_score", sample["score"])
            self.assertIn("bucket_scores", sample["score"])
            self.assertIn("confidence", sample["score"])
            self.assertIn("classification", sample["score"])

            # engagement/creator/media may be present or None depending on fixture data
            # Just check that the keys exist
            self.assertIn("engagement", sample)
            self.assertIn("creator", sample)
            self.assertIn("media", sample)

    def test_dashboard_summary_contains_aggregations(self) -> None:
        """VAL-DASH-003: Summary contains tag_frequency, score_distribution, engagement_range."""
        with TemporaryDirectory() as tmpdir:
            exit_code = main(["run-pack", "jade", "--output-dir", tmpdir])
            self.assertEqual(exit_code, 0)

            dashboard = json.loads(
                (Path(tmpdir) / "dashboard.json").read_text(encoding="utf-8")
            )

            summary = dashboard["summary"]
            
            # Check for required summary fields
            self.assertIn("tag_frequency", summary)
            self.assertIn("score_distribution", summary)
            self.assertIn("engagement_range", summary)

            # tag_frequency should be a dict
            self.assertIsInstance(summary["tag_frequency"], dict)

            # score_distribution should have min/max/mean/median
            score_dist = summary["score_distribution"]
            self.assertIn("min", score_dist)
            self.assertIn("max", score_dist)
            self.assertIn("mean", score_dist)
            self.assertIn("median", score_dist)

            # engagement_range should have min/max for likes and saves
            engagement_range = summary["engagement_range"]
            self.assertIn("min_likes", engagement_range)
            self.assertIn("max_likes", engagement_range)
            self.assertIn("min_saves", engagement_range)
            self.assertIn("max_saves", engagement_range)

    def test_dashboard_tag_frequency_counts_correctly(self) -> None:
        """Tag frequency should count tag occurrences across all samples."""
        with TemporaryDirectory() as tmpdir:
            # Create a multi-sample input
            input_path = Path(tmpdir) / "multi.jsonl"
            outdir = Path(tmpdir) / "out"
            rows = [
                {
                    "note_id": "test-001",
                    "title": "jade bracelet",
                    "desc": "Beautiful jade",
                    "note_url": "https://example.com/001",
                    "time": 1710000000000,
                    "last_modify_ts": 1710000005000,
                    "tag_list": "jade,bracelet",
                },
                {
                    "note_id": "test-002",
                    "title": "jade pendant",
                    "desc": "Another jade piece",
                    "note_url": "https://example.com/002",
                    "time": 1710100000000,
                    "last_modify_ts": 1710100005000,
                    "tag_list": "jade,pendant,modern",
                },
            ]
            input_path.write_text(
                "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                encoding="utf-8",
            )

            exit_code = main([
                "run-pack", "jade",
                "--input", str(input_path),
                "--output-dir", str(outdir),
            ])
            self.assertEqual(exit_code, 0)

            dashboard = json.loads((outdir / "dashboard.json").read_text(encoding="utf-8"))
            tag_freq = dashboard["summary"]["tag_frequency"]

            # "jade" appears in both samples
            self.assertEqual(tag_freq.get("jade"), 2)
            # "bracelet", "pendant", "modern" appear once each
            self.assertEqual(tag_freq.get("bracelet"), 1)
            self.assertEqual(tag_freq.get("pendant"), 1)
            self.assertEqual(tag_freq.get("modern"), 1)

    def test_dashboard_score_distribution_calculates_correctly(self) -> None:
        """Score distribution should calculate min/max/mean/median from weighted scores."""
        with TemporaryDirectory() as tmpdir:
            exit_code = main(["run-pack", "jade", "--output-dir", tmpdir])
            self.assertEqual(exit_code, 0)

            dashboard = json.loads(
                (Path(tmpdir) / "dashboard.json").read_text(encoding="utf-8")
            )

            score_dist = dashboard["summary"]["score_distribution"]
            
            # Verify all scores are numbers
            self.assertIsInstance(score_dist["min"], (int, float))
            self.assertIsInstance(score_dist["max"], (int, float))
            self.assertIsInstance(score_dist["mean"], (int, float))
            self.assertIsInstance(score_dist["median"], (int, float))

            # Basic sanity: min <= median <= max, min <= mean <= max
            self.assertLessEqual(score_dist["min"], score_dist["median"])
            self.assertLessEqual(score_dist["median"], score_dist["max"])
            self.assertLessEqual(score_dist["min"], score_dist["mean"])
            self.assertLessEqual(score_dist["mean"], score_dist["max"])

    def test_streetwear_pack_also_generates_dashboard(self) -> None:
        """VAL-CROSS-009: Streetwear pack also produces dashboard.json."""
        with TemporaryDirectory() as tmpdir:
            exit_code = main(["run-pack", "designer_streetwear", "--output-dir", tmpdir])
            self.assertEqual(exit_code, 0)

            output_dir = Path(tmpdir)
            dashboard_path = output_dir / "dashboard.json"
            self.assertTrue(dashboard_path.is_file(), "dashboard.json should exist for streetwear")

            dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))
            self.assertEqual(dashboard["pack_name"], "designer_streetwear")
            self.assertIn("samples", dashboard)
            self.assertIn("summary", dashboard)

    def test_dashboard_total_count_matches_sample_length(self) -> None:
        """total_count should match the number of samples."""
        with TemporaryDirectory() as tmpdir:
            exit_code = main(["run-pack", "jade", "--output-dir", tmpdir])
            self.assertEqual(exit_code, 0)

            dashboard = json.loads(
                (Path(tmpdir) / "dashboard.json").read_text(encoding="utf-8")
            )

            self.assertEqual(dashboard["total_count"], len(dashboard["samples"]))


if __name__ == "__main__":
    unittest.main()
