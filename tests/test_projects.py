from __future__ import annotations

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

from intelligence.projects import discover_project_pack, list_project_packs


ROOT = Path(__file__).resolve().parents[1]
CASE_STUDY_ROOT = ROOT / "docs" / "case-studies" / "jade"


class ProjectPackDiscoveryTests(unittest.TestCase):
    def test_list_project_packs_includes_both_packs(self) -> None:
        packs = list_project_packs()
        self.assertIn("jade", packs)
        self.assertIn("designer_streetwear", packs)
        self.assertEqual(len(packs), 2)

    def test_list_project_packs_uses_asset_layout_without_init_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            packs_root = Path(tmpdir)
            pack_root = packs_root / "orchid"
            (pack_root / "config").mkdir(parents=True)
            (pack_root / "keywords").mkdir()
            (pack_root / "templates").mkdir()
            (pack_root / "config" / "project.yaml").write_text("name: orchid\n", encoding="utf-8")
            (pack_root / "keywords" / "seed_keywords.csv").write_text("group,keyword\n", encoding="utf-8")

            with patch("intelligence.projects._PACKS_ROOT", packs_root):
                self.assertEqual(list_project_packs(), ("orchid",))

    def test_discover_project_pack_returns_expected_paths(self) -> None:
        pack = discover_project_pack("jade")

        self.assertEqual(pack.name, "jade")
        self.assertEqual(pack.root, ROOT / "src" / "intelligence" / "projects" / "jade")
        self.assertEqual(pack.config_path, pack.root / "config" / "project.yaml")
        self.assertEqual(pack.keywords_path, pack.root / "keywords" / "seed_keywords.csv")
        self.assertEqual(pack.templates_path, pack.root / "templates")
        self.assertEqual(pack.examples_path, pack.root / "examples")

        self.assertTrue(pack.config_path.is_file())
        self.assertTrue(pack.keywords_path.is_file())
        self.assertTrue(pack.templates_path.is_dir())
        self.assertFalse(pack.examples_path.exists())

    def test_jade_pack_keeps_runtime_config_lean_and_exposes_case_study_assets(self) -> None:
        pack = discover_project_pack("jade")
        config_text = pack.config_path.read_text(encoding="utf-8")

        self.assertIn("keyword_groups:", config_text)
        self.assertNotIn("sample_frame:", config_text)
        self.assertNotIn("selection_rules:", config_text)

        self.assertTrue((CASE_STUDY_ROOT / "README.md").is_file())
        self.assertTrue((CASE_STUDY_ROOT / "sample_frame.md").is_file())
        self.assertTrue((CASE_STUDY_ROOT / "scoring_notes.md").is_file())

        keyword_batch_text = (pack.templates_path / "keyword_batch.md").read_text(encoding="utf-8")
        report_text = (pack.templates_path / "report.md").read_text(encoding="utf-8")
        trend_map_text = (pack.templates_path / "trend_map.md").read_text(encoding="utf-8")
        product_priority_text = (pack.templates_path / "product_priority.md").read_text(
            encoding="utf-8"
        )
        design_brief_text = (pack.templates_path / "design_brief.md").read_text(encoding="utf-8")

        self.assertNotIn("Placeholder", keyword_batch_text)
        self.assertNotIn("Placeholder", report_text)
        self.assertIn("Batch Metadata", keyword_batch_text)
        self.assertIn("Executive Summary", report_text)
        self.assertIn("Product Translation", trend_map_text)
        self.assertIn("Build Now", product_priority_text)
        self.assertIn("Guardrails", design_brief_text)

    def test_discover_project_pack_rejects_unknown_name(self) -> None:
        with self.assertRaises(FileNotFoundError):
            discover_project_pack("unknown")

    def test_discover_project_pack_rejects_malformed_assets(self) -> None:
        with TemporaryDirectory() as tmpdir:
            packs_root = Path(tmpdir)
            pack_root = packs_root / "broken"
            (pack_root / "config").mkdir(parents=True)
            (pack_root / "keywords").mkdir()
            (pack_root / "templates").mkdir()
            (pack_root / "config" / "project.yaml").mkdir()
            (pack_root / "keywords" / "seed_keywords.csv").write_text("group,keyword\n", encoding="utf-8")

            with patch("intelligence.projects._PACKS_ROOT", packs_root):
                with self.assertRaises(FileNotFoundError):
                    discover_project_pack("broken")

            config_as_dir = packs_root / "config-dir"
            (config_as_dir / "config").mkdir(parents=True)
            (config_as_dir / "keywords").mkdir()
            (config_as_dir / "templates").mkdir()
            (config_as_dir / "config" / "project.yaml").mkdir()
            (config_as_dir / "keywords" / "seed_keywords.csv").write_text(
                "group,keyword\n",
                encoding="utf-8",
            )

            with patch("intelligence.projects._PACKS_ROOT", packs_root):
                with self.assertRaises(FileNotFoundError):
                    discover_project_pack("config-dir")

            keywords_as_dir = packs_root / "keywords-dir"
            (keywords_as_dir / "config").mkdir(parents=True)
            (keywords_as_dir / "keywords").mkdir()
            (keywords_as_dir / "templates").mkdir()
            (keywords_as_dir / "config" / "project.yaml").write_text(
                "name: keywords-dir\n",
                encoding="utf-8",
            )
            (keywords_as_dir / "keywords" / "seed_keywords.csv").mkdir()

            with patch("intelligence.projects._PACKS_ROOT", packs_root):
                with self.assertRaises(FileNotFoundError):
                    discover_project_pack("keywords-dir")

            templates_as_file = packs_root / "templates-file"
            (templates_as_file / "config").mkdir(parents=True)
            (templates_as_file / "keywords").mkdir()
            (templates_as_file / "config" / "project.yaml").write_text(
                "name: templates-file\n",
                encoding="utf-8",
            )
            (templates_as_file / "keywords" / "seed_keywords.csv").write_text(
                "group,keyword\n",
                encoding="utf-8",
            )
            (templates_as_file / "templates").write_text("not-a-directory", encoding="utf-8")

            with patch("intelligence.projects._PACKS_ROOT", packs_root):
                with self.assertRaises(FileNotFoundError):
                    discover_project_pack("templates-file")


if __name__ == "__main__":
    unittest.main()
