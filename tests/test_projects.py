from __future__ import annotations

import unittest
from pathlib import Path

from intelligence.projects import discover_project_pack, list_project_packs


ROOT = Path(__file__).resolve().parents[1]


class ProjectPackDiscoveryTests(unittest.TestCase):
    def test_list_project_packs_includes_jade(self) -> None:
        self.assertEqual(list_project_packs(), ("jade",))

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

    def test_discover_project_pack_rejects_unknown_name(self) -> None:
        with self.assertRaises(FileNotFoundError):
            discover_project_pack("unknown")


if __name__ == "__main__":
    unittest.main()
