from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from intelligence.cli import main


class JadePackFlowTests(unittest.TestCase):
    def test_run_pack_jade_writes_demo_outputs(self) -> None:
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
            )
            for filename in expected_files:
                self.assertTrue((output_dir / filename).is_file(), filename)

            normalized = json.loads((output_dir / "normalized_samples.json").read_text(encoding="utf-8"))
            scored = json.loads((output_dir / "scored_samples.json").read_text(encoding="utf-8"))
            report_json = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
            report_md = (output_dir / "report.md").read_text(encoding="utf-8")
            report_html = (output_dir / "report.html").read_text(encoding="utf-8")

            self.assertEqual(len(normalized), 1)
            self.assertEqual(normalized[0]["provenance"]["source"], "mediacrawler")
            self.assertEqual(normalized[0]["provenance"]["source_id"], "mc-note-001")
            self.assertEqual(normalized[0]["content"]["title"], "jade pendant feature")

            self.assertEqual(len(scored), 1)
            self.assertEqual(scored[0]["sample"]["provenance"]["source_id"], "mc-note-001")
            self.assertIn("weighted_score", scored[0])
            self.assertIn("confidence", scored[0])
            self.assertIn("classification", scored[0])

            self.assertEqual(report_json["title"], "Jade Pack Report")
            self.assertIn("jade", report_json["summary"].lower())
            self.assertIn("# Jade Pack Report", report_md)
            self.assertIn("## Evidence Buckets", report_md)
            self.assertIn("<html", report_html.lower())

    def test_examples_directory_contains_jade_readme(self) -> None:
        readme = Path(__file__).resolve().parents[1] / "examples" / "jade" / "README.md"
        self.assertTrue(readme.is_file())
        self.assertIn("run-pack jade", readme.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
