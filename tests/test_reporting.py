from __future__ import annotations

import json
import importlib
import tempfile
from pathlib import Path
import unittest


class ReportingExportTests(unittest.TestCase):
    def test_reporting_package_exports_public_api(self) -> None:
        reporting = importlib.import_module("intelligence.reporting")

        for name in (
            "Report",
            "ReportBlock",
            "render_json_report",
            "render_markdown_report",
            "render_html_report",
        ):
            self.assertTrue(hasattr(reporting, name), name)


class ReportingRendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.reporting = importlib.import_module("intelligence.reporting")
        self.Report = getattr(self.reporting, "Report", None)
        self.ReportBlock = getattr(self.reporting, "ReportBlock", None)
        if self.Report is None or self.ReportBlock is None:
            self.fail("reporting package is missing Report or ReportBlock")

    def _sample_report(self):
        return self.Report(
            title="Jade Pack Report",
            summary="A concise summary of the workflow findings.",
            evidence_buckets=(
                self.ReportBlock(
                    title="Core evidence",
                    fields=(("sample count", "12"), ("coverage", "broad")),
                    bullets=("Repeated jade silhouettes", "Consistent silver accents"),
                ),
            ),
            validation_states=(
                self.ReportBlock(
                    title="Workflow validation",
                    fields=(("state", "validated"), ("note", "Reviewed against notes")),
                ),
            ),
            trend_clusters=(
                self.ReportBlock(
                    title="Quiet shine cluster",
                    fields=(("signal", "layered shine"),),
                    bullets=("Good for everyday wear",),
                ),
            ),
            product_priorities=(
                self.ReportBlock(
                    title="Build now",
                    fields=(("direction", "bracelet stack"), ("why", "clear demand")),
                ),
            ),
            design_briefs=(
                self.ReportBlock(
                    title="Soft geometry",
                    fields=(("target audience", "women 25-34"), ("material mix", "jade and silver")),
                    bullets=("Keep it light",),
                ),
            ),
        )

    def test_json_renderer_serializes_the_report_deterministically(self) -> None:
        json_report = importlib.import_module("intelligence.reporting.json_report")
        render_json_report = getattr(json_report, "render_json_report", None)
        if render_json_report is None:
            self.fail("json_report module is missing render_json_report")

        rendered = render_json_report(self._sample_report())

        expected = json.dumps(
            {
                "title": "Jade Pack Report",
                "summary": "A concise summary of the workflow findings.",
                "evidence_buckets": [
                    {
                        "title": "Core evidence",
                        "fields": [
                            {"label": "sample count", "value": "12"},
                            {"label": "coverage", "value": "broad"},
                        ],
                        "bullets": [
                            "Repeated jade silhouettes",
                            "Consistent silver accents",
                        ],
                    }
                ],
                "validation_states": [
                    {
                        "title": "Workflow validation",
                        "fields": [
                            {"label": "state", "value": "validated"},
                            {"label": "note", "value": "Reviewed against notes"},
                        ],
                        "bullets": [],
                    }
                ],
                "trend_clusters": [
                    {
                        "title": "Quiet shine cluster",
                        "fields": [
                            {"label": "signal", "value": "layered shine"},
                        ],
                        "bullets": ["Good for everyday wear"],
                    }
                ],
                "product_priorities": [
                    {
                        "title": "Build now",
                        "fields": [
                            {"label": "direction", "value": "bracelet stack"},
                            {"label": "why", "value": "clear demand"},
                        ],
                        "bullets": [],
                    }
                ],
                "design_briefs": [
                    {
                        "title": "Soft geometry",
                        "fields": [
                            {"label": "target audience", "value": "women 25-34"},
                            {"label": "material mix", "value": "jade and silver"},
                        ],
                        "bullets": ["Keep it light"],
                    }
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        self.assertEqual(rendered, expected)

    def test_markdown_renderer_renders_clear_sections(self) -> None:
        markdown_report = importlib.import_module("intelligence.reporting.markdown_report")
        render_markdown_report = getattr(markdown_report, "render_markdown_report", None)
        if render_markdown_report is None:
            self.fail("markdown_report module is missing render_markdown_report")

        rendered = render_markdown_report(self._sample_report())

        self.assertIn("# Jade Pack Report", rendered)
        self.assertIn("A concise summary of the workflow findings.", rendered)
        self.assertIn("## Evidence Buckets", rendered)
        self.assertIn("### Core evidence", rendered)
        self.assertIn("- sample count: 12", rendered)
        self.assertIn("- Repeated jade silhouettes", rendered)
        self.assertIn("## Product Priorities", rendered)
        self.assertIn("## Design Briefs", rendered)

    def test_html_renderer_uses_template_and_escapes_content(self) -> None:
        html_report = importlib.import_module("intelligence.reporting.html_report")
        render_html_report = getattr(html_report, "render_html_report", None)
        if render_html_report is None:
            self.fail("html_report module is missing render_html_report")

        report = self.Report(
            title="Jade <Report>",
            summary="Use <b>care</b> & precision.",
            evidence_buckets=(
                self.ReportBlock(title="Evidence", bullets=("<tag>",)),
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "report.html"
            template_path.write_text(
                "<html><head><title>$title</title></head><body><main>$summary$sections</main></body></html>",
                encoding="utf-8",
            )

            rendered = render_html_report(report, template_path=template_path)

        self.assertIn("<title>Jade &lt;Report&gt;</title>", rendered)
        self.assertIn("Use &lt;b&gt;care&lt;/b&gt; &amp; precision.", rendered)
        self.assertIn("<h2>Evidence Buckets</h2>", rendered)
        self.assertIn("&lt;tag&gt;", rendered)
        self.assertNotIn("<tag>", rendered)


if __name__ == "__main__":
    unittest.main()
