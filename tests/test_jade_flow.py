from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from intelligence.cli import main

_FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "mediacrawler_jade_export.jsonl"


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
            self.assertIn("Fixture Coverage", report_md)
            self.assertIn("fixture-only execution", report_md)
            self.assertIn("<html", report_html.lower())

    def test_run_pack_jade_with_explicit_input(self) -> None:
        with TemporaryDirectory() as tmpdir:
            exit_code = main([
                "run-pack", "jade",
                "--input", str(_FIXTURE_PATH),
                "--output-dir", tmpdir,
            ])

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

            self.assertEqual(len(normalized), 1)
            self.assertEqual(normalized[0]["provenance"]["source"], "mediacrawler")
            self.assertEqual(len(scored), 1)
            self.assertIn("weighted_score", scored[0])
            self.assertEqual(report_json["title"], "Jade Pack Report")
            self.assertIn("# Jade Pack Report", report_md)
            # --input provided → report should NOT say "fixture"
            self.assertNotIn("Fixture Coverage", report_md)
            self.assertNotIn("fixture-only execution", report_md)
            self.assertIn("Input Coverage", report_md)

    def test_run_pack_jade_with_multi_sample_input(self) -> None:
        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "multi.jsonl"
            outdir = Path(tmpdir) / "out"
            rows = [
                {
                    "note_id": "real-001",
                    "title": "jade bracelet modern design",
                    "desc": "Beautiful jade bracelet with modern design elements",
                    "note_url": "https://www.xiaohongshu.com/explore/real-001",
                    "time": 1710000000000,
                    "last_modify_ts": 1710000005000,
                    "tag_list": "jade,bracelet,modern",
                },
                {
                    "note_id": "real-002",
                    "title": "random food post",
                    "desc": "Today I ate a sandwich",
                    "note_url": "https://www.xiaohongshu.com/explore/real-002",
                    "time": 1710100000000,
                    "last_modify_ts": 1710100005000,
                    "tag_list": "food,lunch",
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
            normalized = json.loads((outdir / "normalized_samples.json").read_text(encoding="utf-8"))
            scored = json.loads((outdir / "scored_samples.json").read_text(encoding="utf-8"))
            self.assertEqual(len(normalized), 2)
            self.assertEqual(len(scored), 2)

            # First sample has jade + bracelet + modern → should score higher
            self.assertGreater(scored[0]["weighted_score"], scored[1]["weighted_score"])

            # Report should reflect real input, not fixture
            report_md = (outdir / "report.md").read_text(encoding="utf-8")
            self.assertIn("Input Coverage", report_md)
            self.assertIn("user input: multi.jsonl", report_md)

    def test_run_pack_jade_input_file_not_found(self) -> None:
        with TemporaryDirectory() as tmpdir:
            exit_code = main([
                "run-pack", "jade",
                "--input", "/nonexistent/path/data.jsonl",
                "--output-dir", tmpdir,
            ])
            self.assertNotEqual(exit_code, 0)

    def test_run_pack_jade_input_empty_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "empty.jsonl"
            input_path.write_text("", encoding="utf-8")
            outdir = Path(tmpdir) / "out"

            exit_code = main([
                "run-pack", "jade",
                "--input", str(input_path),
                "--output-dir", str(outdir),
            ])

            self.assertEqual(exit_code, 0)
            normalized = json.loads((outdir / "normalized_samples.json").read_text(encoding="utf-8"))
            self.assertEqual(len(normalized), 0)

    def test_examples_directory_contains_jade_readme(self) -> None:
        readme = Path(__file__).resolve().parents[1] / "examples" / "jade" / "README.md"
        self.assertTrue(readme.is_file())
        self.assertIn("run-pack jade", readme.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
