from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from intelligence.cli import main

_FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "mediacrawler_streetwear_export.jsonl"


class DesignerStreetwearPackFlowTests(unittest.TestCase):
    """End-to-end tests for the designer_streetwear pack."""

    def test_run_pack_streetwear_writes_all_outputs(self) -> None:
        with TemporaryDirectory() as tmpdir:
            exit_code = main(["run-pack", "designer_streetwear", "--output-dir", tmpdir])
            self.assertEqual(exit_code, 0)

            output_dir = Path(tmpdir)
            for filename in (
                "normalized_samples.json",
                "scored_samples.json",
                "report.json",
                "report.md",
                "report.html",
            ):
                self.assertTrue((output_dir / filename).is_file(), filename)

            normalized = json.loads((output_dir / "normalized_samples.json").read_text(encoding="utf-8"))
            scored = json.loads((output_dir / "scored_samples.json").read_text(encoding="utf-8"))
            report_json = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
            report_md = (output_dir / "report.md").read_text(encoding="utf-8")
            report_html = (output_dir / "report.html").read_text(encoding="utf-8")

            self.assertEqual(len(normalized), 3)
            self.assertEqual(normalized[0]["provenance"]["source"], "mediacrawler")
            self.assertEqual(normalized[0]["provenance"]["source_id"], "sw-note-001")

            self.assertEqual(len(scored), 3)
            self.assertIn("weighted_score", scored[0])
            self.assertIn("confidence", scored[0])
            self.assertIn("classification", scored[0])

            self.assertEqual(report_json["title"], "Designer Streetwear Pack Report")
            self.assertIn("# Designer Streetwear Pack Report", report_md)
            self.assertIn("## Evidence Buckets", report_md)
            self.assertIn("Fixture Coverage", report_md)
            self.assertIn("<html", report_html.lower())

    def test_run_pack_streetwear_with_explicit_input(self) -> None:
        with TemporaryDirectory() as tmpdir:
            exit_code = main([
                "run-pack", "designer_streetwear",
                "--input", str(_FIXTURE_PATH),
                "--output-dir", tmpdir,
            ])
            self.assertEqual(exit_code, 0)

            output_dir = Path(tmpdir)
            report_md = (output_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("Input Coverage", report_md)
            self.assertNotIn("Fixture Coverage", report_md)

    def test_streetwear_scores_relevant_higher_than_irrelevant(self) -> None:
        """Streetwear content should score higher than food content."""
        with TemporaryDirectory() as tmpdir:
            exit_code = main(["run-pack", "designer_streetwear", "--output-dir", tmpdir])
            self.assertEqual(exit_code, 0)

            scored = json.loads(
                (Path(tmpdir) / "scored_samples.json").read_text(encoding="utf-8")
            )
            # sw-note-001 (layering, graphic, silhouette) and sw-note-002 (brand, bomber)
            # should both score higher than sw-note-003 (food post)
            self.assertGreater(scored[0]["weighted_score"], scored[2]["weighted_score"])
            self.assertGreater(scored[1]["weighted_score"], scored[2]["weighted_score"])

    def test_streetwear_report_title_is_pack_specific(self) -> None:
        with TemporaryDirectory() as tmpdir:
            exit_code = main(["run-pack", "designer_streetwear", "--output-dir", tmpdir])
            self.assertEqual(exit_code, 0)

            report_json = json.loads(
                (Path(tmpdir) / "report.json").read_text(encoding="utf-8")
            )
            # Must NOT say "Jade"
            self.assertNotIn("Jade", report_json["title"])
            self.assertNotIn("jade", report_json["summary"].lower().split("from")[0])

    def test_examples_directory_contains_streetwear_readme(self) -> None:
        readme = Path(__file__).resolve().parents[1] / "examples" / "designer_streetwear" / "README.md"
        self.assertTrue(readme.is_file())
        self.assertIn("run-pack designer_streetwear", readme.read_text(encoding="utf-8"))


class SharedWorkflowTests(unittest.TestCase):
    """Tests proving both packs exercise the same shared flow."""

    def test_both_packs_produce_identical_output_structure(self) -> None:
        """Both packs should produce the same set of output files with matching top-level keys."""
        with TemporaryDirectory() as tmpdir:
            jade_dir = Path(tmpdir) / "jade"
            sw_dir = Path(tmpdir) / "streetwear"

            self.assertEqual(main(["run-pack", "jade", "--output-dir", str(jade_dir)]), 0)
            self.assertEqual(main(["run-pack", "designer_streetwear", "--output-dir", str(sw_dir)]), 0)

            for filename in ("normalized_samples.json", "scored_samples.json", "report.json"):
                jade_data = json.loads((jade_dir / filename).read_text(encoding="utf-8"))
                sw_data = json.loads((sw_dir / filename).read_text(encoding="utf-8"))

                if isinstance(jade_data, list) and isinstance(sw_data, list):
                    # Both produce lists; check inner structure keys match if non-empty
                    if jade_data and sw_data:
                        self.assertEqual(sorted(jade_data[0].keys()), sorted(sw_data[0].keys()))
                elif isinstance(jade_data, dict) and isinstance(sw_data, dict):
                    self.assertEqual(sorted(jade_data.keys()), sorted(sw_data.keys()))

    def test_both_packs_share_normalized_sample_schema(self) -> None:
        with TemporaryDirectory() as tmpdir:
            jade_dir = Path(tmpdir) / "jade"
            sw_dir = Path(tmpdir) / "streetwear"

            main(["run-pack", "jade", "--output-dir", str(jade_dir)])
            main(["run-pack", "designer_streetwear", "--output-dir", str(sw_dir)])

            jade_sample = json.loads((jade_dir / "normalized_samples.json").read_text(encoding="utf-8"))[0]
            sw_sample = json.loads((sw_dir / "normalized_samples.json").read_text(encoding="utf-8"))[0]

            self.assertEqual(sorted(jade_sample.keys()), sorted(sw_sample.keys()))
            self.assertEqual(sorted(jade_sample["provenance"].keys()), sorted(sw_sample["provenance"].keys()))
            self.assertEqual(sorted(jade_sample["content"].keys()), sorted(sw_sample["content"].keys()))


if __name__ == "__main__":
    unittest.main()
