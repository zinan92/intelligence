from __future__ import annotations

import importlib
import unittest


class WorkflowImportTests(unittest.TestCase):
    def test_placeholder_workflow_modules_import(self) -> None:
        for module_name in (
            "intelligence.workflows.ingest",
            "intelligence.workflows.shortlist",
            "intelligence.workflows.normalize",
            "intelligence.workflows.score",
            "intelligence.workflows.validate",
            "intelligence.workflows.report",
        ):
            module = importlib.import_module(module_name)
            self.assertEqual(module.__name__, module_name)

    def test_required_package_modules_import(self) -> None:
        for module_name in (
            "intelligence.adapters",
            "intelligence.reporting",
            "intelligence.schema",
            "intelligence.scoring",
            "intelligence.workflows",
        ):
            module = importlib.import_module(module_name)
            self.assertEqual(module.__name__, module_name)


if __name__ == "__main__":
    unittest.main()
