from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from intelligence.cli import main
from intelligence.projects import validate_project_pack


class ValidatePackCLITests(unittest.TestCase):
    """Tests for the validate-pack CLI command."""

    def test_validate_jade_succeeds(self) -> None:
        exit_code = main(["validate-pack", "jade"])
        self.assertEqual(exit_code, 0)

    def test_validate_designer_streetwear_succeeds(self) -> None:
        exit_code = main(["validate-pack", "designer_streetwear"])
        self.assertEqual(exit_code, 0)

    def test_validate_unknown_pack_fails(self) -> None:
        exit_code = main(["validate-pack", "nonexistent"])
        self.assertNotEqual(exit_code, 0)

    def test_validate_malformed_pack_fails(self) -> None:
        with TemporaryDirectory() as tmpdir:
            packs_root = Path(tmpdir)
            pack_root = packs_root / "broken"
            pack_root.mkdir()
            # Missing everything

            with patch("intelligence.projects._PACKS_ROOT", packs_root):
                exit_code = main(["validate-pack", "broken"])
            self.assertNotEqual(exit_code, 0)


class ValidateProjectPackTests(unittest.TestCase):
    """Tests for the validate_project_pack function."""

    def test_valid_jade_returns_no_errors(self) -> None:
        errors = validate_project_pack("jade")
        self.assertEqual(errors, [])

    def test_valid_streetwear_returns_no_errors(self) -> None:
        errors = validate_project_pack("designer_streetwear")
        self.assertEqual(errors, [])

    def test_nonexistent_pack_returns_error(self) -> None:
        errors = validate_project_pack("nonexistent")
        self.assertTrue(len(errors) > 0)
        self.assertTrue(any("not found" in e.lower() or "does not exist" in e.lower() for e in errors))

    def test_missing_config_returns_error(self) -> None:
        with TemporaryDirectory() as tmpdir:
            packs_root = Path(tmpdir)
            pack_root = packs_root / "noconfig"
            pack_root.mkdir()
            (pack_root / "keywords").mkdir()
            (pack_root / "keywords" / "seed_keywords.csv").write_text("group,keyword\n", encoding="utf-8")
            (pack_root / "templates").mkdir()

            with patch("intelligence.projects._PACKS_ROOT", packs_root):
                errors = validate_project_pack("noconfig")
            self.assertTrue(any("config" in e.lower() for e in errors))

    def test_missing_keywords_returns_error(self) -> None:
        with TemporaryDirectory() as tmpdir:
            packs_root = Path(tmpdir)
            pack_root = packs_root / "nokeywords"
            (pack_root / "config").mkdir(parents=True)
            (pack_root / "config" / "project.yaml").write_text("name: nokeywords\n", encoding="utf-8")
            (pack_root / "templates").mkdir()

            with patch("intelligence.projects._PACKS_ROOT", packs_root):
                errors = validate_project_pack("nokeywords")
            self.assertTrue(any("keyword" in e.lower() for e in errors))

    def test_missing_templates_returns_error(self) -> None:
        with TemporaryDirectory() as tmpdir:
            packs_root = Path(tmpdir)
            pack_root = packs_root / "notemplates"
            (pack_root / "config").mkdir(parents=True)
            (pack_root / "config" / "project.yaml").write_text("name: notemplates\n", encoding="utf-8")
            (pack_root / "keywords").mkdir()
            (pack_root / "keywords" / "seed_keywords.csv").write_text("group,keyword\n", encoding="utf-8")

            with patch("intelligence.projects._PACKS_ROOT", packs_root):
                errors = validate_project_pack("notemplates")
            self.assertTrue(any("template" in e.lower() for e in errors))

    def test_empty_keywords_file_returns_error(self) -> None:
        with TemporaryDirectory() as tmpdir:
            packs_root = Path(tmpdir)
            pack_root = packs_root / "emptykw"
            (pack_root / "config").mkdir(parents=True)
            (pack_root / "config" / "project.yaml").write_text("name: emptykw\n", encoding="utf-8")
            (pack_root / "keywords").mkdir()
            (pack_root / "keywords" / "seed_keywords.csv").write_text("", encoding="utf-8")
            (pack_root / "templates").mkdir()

            with patch("intelligence.projects._PACKS_ROOT", packs_root):
                errors = validate_project_pack("emptykw")
            self.assertTrue(any("keyword" in e.lower() or "header" in e.lower() for e in errors))

    def test_multiple_errors_reported(self) -> None:
        with TemporaryDirectory() as tmpdir:
            packs_root = Path(tmpdir)
            pack_root = packs_root / "allfail"
            pack_root.mkdir()
            # Missing config, keywords, templates

            with patch("intelligence.projects._PACKS_ROOT", packs_root):
                errors = validate_project_pack("allfail")
            self.assertGreaterEqual(len(errors), 3)


class ExampleOutputTests(unittest.TestCase):
    """Tests that example outputs exist for both packs."""

    def test_jade_example_outputs_exist(self) -> None:
        example_dir = Path(__file__).resolve().parents[1] / "examples" / "jade" / "sample_output"
        for filename in ("normalized_samples.json", "scored_samples.json", "report.json", "report.md"):
            self.assertTrue((example_dir / filename).is_file(), f"missing: {filename}")

    def test_streetwear_example_outputs_exist(self) -> None:
        example_dir = Path(__file__).resolve().parents[1] / "examples" / "designer_streetwear" / "sample_output"
        for filename in ("normalized_samples.json", "scored_samples.json", "report.json", "report.md"):
            self.assertTrue((example_dir / filename).is_file(), f"missing: {filename}")


if __name__ == "__main__":
    unittest.main()
