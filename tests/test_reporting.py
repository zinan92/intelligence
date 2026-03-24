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


class HtmlVisualReportTests(unittest.TestCase):
    """Tests for the upgraded visual HTML report layer."""

    def setUp(self) -> None:
        from intelligence.reporting.model import Report, ReportBlock
        from intelligence.reporting.html_report import render_html_report

        self.Report = Report
        self.ReportBlock = ReportBlock
        self.render = render_html_report

    def _sample_report(self):
        return self.Report(
            title="Jade Pack Report",
            summary="Processed 1 sample. Top signal scored 0.80 with high confidence.",
            evidence_buckets=(
                self.ReportBlock(
                    title="Fixture Coverage",
                    fields=(("sample count", "1"), ("source", "mediacrawler")),
                    bullets=("jade pendant feature", "tags: jade, pendant"),
                ),
            ),
            validation_states=(
                self.ReportBlock(
                    title="Runtime Check",
                    fields=(("normalized outputs", "1"), ("scored outputs", "1")),
                ),
            ),
            trend_clusters=(
                self.ReportBlock(
                    title="Jade Pendant Signal",
                    fields=(
                        ("weighted score", "0.80"),
                        ("confidence", "high"),
                        ("classification", "confirmed_continuation"),
                    ),
                    bullets=("category-specific cue detected",),
                ),
            ),
            product_priorities=(
                self.ReportBlock(
                    title="Build Now",
                    fields=(("direction", "jade pendant line"), ("why", "clear demand")),
                ),
            ),
            design_briefs=(
                self.ReportBlock(
                    title="Keep It Compact",
                    fields=(("target audience", "jade research"), ("material mix", "jade + silver")),
                    bullets=("avoid overfitting",),
                ),
            ),
        )

    def test_html_embeds_stylesheet(self):
        html = self.render(self._sample_report())
        self.assertIn("<style>", html)

    def test_hero_score_bar_renders(self):
        html = self.render(self._sample_report())
        self.assertIn("score-bar", html)
        self.assertIn("0.80", html)

    def test_confidence_badge_has_level_class(self):
        html = self.render(self._sample_report())
        self.assertIn("confidence-high", html)

    def test_confidence_medium_badge(self):
        report = self.Report(
            title="Test",
            summary="Test",
            trend_clusters=(
                self.ReportBlock(
                    title="Signal",
                    fields=(
                        ("weighted score", "0.50"),
                        ("confidence", "medium"),
                        ("classification", "emerging"),
                    ),
                ),
            ),
        )
        html = self.render(report)
        self.assertIn("confidence-medium", html)

    def test_field_grid_renders(self):
        html = self.render(self._sample_report())
        self.assertIn("field-grid", html)

    def test_section_cards_render(self):
        html = self.render(self._sample_report())
        self.assertIn('class="card"', html)

    def test_all_section_headings_present(self):
        html = self.render(self._sample_report())
        for heading in (
            "Evidence Buckets",
            "Validation States",
            "Trend Clusters",
            "Product Priorities",
            "Design Briefs",
        ):
            self.assertIn(heading, html, f"Missing heading: {heading}")

    def test_section_css_classes(self):
        html = self.render(self._sample_report())
        for css_class in (
            "evidence-buckets",
            "trend-clusters",
            "product-priorities",
            "design-briefs",
        ):
            self.assertIn(css_class, html, f"Missing CSS class: {css_class}")

    def test_urls_in_bullets_become_links(self):
        report = self.Report(
            title="Test",
            summary="Test",
            evidence_buckets=(
                self.ReportBlock(
                    title="Sources",
                    bullets=("https://example.com/note-001",),
                ),
            ),
        )
        html = self.render(report)
        self.assertIn('href="https://example.com/note-001"', html)
        self.assertIn("target=", html)

    def test_empty_report_renders_cleanly(self):
        report = self.Report(title="Empty Report", summary="No data available.")
        html = self.render(report)
        self.assertIn("Empty Report", html)
        self.assertIn("No data available.", html)
        self.assertNotIn('<div class="score-bar">', html)

    def test_classification_badge_renders(self):
        html = self.render(self._sample_report())
        self.assertIn("confirmed_continuation", html)
        self.assertIn('class="badge classification"', html)

    def test_empty_sections_not_rendered(self):
        report = self.Report(
            title="Partial",
            summary="Only trend data.",
            trend_clusters=(
                self.ReportBlock(
                    title="Signal",
                    fields=(("weighted score", "0.50"),),
                ),
            ),
        )
        html = self.render(report)
        self.assertIn("Trend Clusters", html)
        self.assertNotIn("Evidence Buckets", html)
        self.assertNotIn("Product Priorities", html)

    def test_html_escaping_preserved_in_visual_report(self):
        report = self.Report(
            title="<script>alert('xss')</script>",
            summary="Safe & sound",
            evidence_buckets=(
                self.ReportBlock(title="<b>Bold</b>", bullets=("<img src=x>",)),
            ),
        )
        html = self.render(report)
        self.assertNotIn("<script>", html)
        self.assertNotIn("<b>Bold</b>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("Safe &amp; sound", html)

    def test_field_labels_and_values_render_in_grid(self):
        html = self.render(self._sample_report())
        self.assertIn('class="label"', html)
        self.assertIn('class="value"', html)
        self.assertIn("sample count", html)
        self.assertIn("mediacrawler", html)


if __name__ == "__main__":
    unittest.main()
