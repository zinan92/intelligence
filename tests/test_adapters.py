from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from intelligence.adapters.douyin_downloader import load_samples as load_douyin_samples
from intelligence.adapters.mediacrawler import load_samples as load_mediacrawler_samples
from intelligence.adapters.xhs_downloader import load_samples as load_xhs_samples
from intelligence.schema import CanonicalSample


MEDIACRAWLER_FIXTURE = Path(
    "/Users/wendy/work/content-co/MediaCrawler-jade-trend-research/data/research/"
    "jade_trends/raw/2026-03-23/crawler_pool_b/search_contents_2026-03-23.jsonl"
)
FIXTURES_DIR = Path(__file__).with_name("fixtures")
XHS_FIXTURE = FIXTURES_DIR / "xhs_downloader.jsonl"
DOUYIN_FIXTURE = FIXTURES_DIR / "douyin_downloader.jsonl"


def _read_first_row(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.loads(handle.readline())


class AdapterTests(unittest.TestCase):
    def test_mediacrawler_loads_real_export_into_canonical_samples(self) -> None:
        first_row = _read_first_row(MEDIACRAWLER_FIXTURE)

        samples = load_mediacrawler_samples(MEDIACRAWLER_FIXTURE)

        self.assertGreater(len(samples), 0)

        sample = samples[0]
        self.assertIsInstance(sample, CanonicalSample)
        self.assertEqual(sample.provenance.source, "mediacrawler")
        self.assertEqual(sample.provenance.source_id, first_row["note_id"])
        self.assertEqual(sample.provenance.url, first_row["note_url"])
        self.assertEqual(sample.content.title, first_row["title"])
        self.assertEqual(sample.content.text, first_row["desc"])
        self.assertEqual(
            sample.content.tags,
            tuple(first_row["tag_list"].split(",")),
        )
        self.assertEqual(
            sample.provenance.published_at,
            datetime.fromtimestamp(first_row["time"] / 1000, tz=timezone.utc),
        )
        self.assertEqual(
            sample.provenance.captured_at,
            datetime.fromtimestamp(first_row["last_modify_ts"] / 1000, tz=timezone.utc),
        )
        self.assertEqual(sample.provenance.raw_metadata["xsec_token"], first_row["xsec_token"])

    def test_xhs_loader_maps_export_fields_to_canonical_samples(self) -> None:
        row = _read_first_row(XHS_FIXTURE)
        samples = load_xhs_samples(XHS_FIXTURE)

        self.assertEqual(len(samples), 1)

        sample = samples[0]
        self.assertIsInstance(sample, CanonicalSample)
        self.assertEqual(sample.provenance.source, "xhs_downloader")
        self.assertEqual(sample.provenance.source_id, row["note_id"])
        self.assertEqual(sample.provenance.url, row["note_url"])
        self.assertEqual(sample.content.title, row["title"])
        self.assertEqual(sample.content.text, row["desc"])
        self.assertEqual(sample.content.tags, ("jade", "pendant"))
        self.assertEqual(
            sample.provenance.published_at,
            datetime.fromtimestamp(row["time"] / 1000, tz=timezone.utc),
        )
        self.assertEqual(
            sample.provenance.captured_at,
            datetime.fromtimestamp(row["last_modify_ts"] / 1000, tz=timezone.utc),
        )
        self.assertEqual(sample.provenance.raw_metadata["xsec_token"], row["xsec_token"])

    def test_douyin_loader_maps_export_fields_to_canonical_samples(self) -> None:
        row = _read_first_row(DOUYIN_FIXTURE)
        samples = load_douyin_samples(DOUYIN_FIXTURE)

        self.assertEqual(len(samples), 1)

        sample = samples[0]
        self.assertIsInstance(sample, CanonicalSample)
        self.assertEqual(sample.provenance.source, "douyin_downloader")
        self.assertEqual(sample.provenance.source_id, row["aweme_id"])
        self.assertEqual(sample.provenance.url, row["share_url"])
        self.assertIsNone(sample.content.title)
        self.assertEqual(sample.content.text, row["desc"])
        self.assertEqual(sample.content.tags, ("short video", "jade"))
        self.assertEqual(
            sample.provenance.published_at,
            datetime.fromtimestamp(row["create_time"] / 1000, tz=timezone.utc),
        )
        self.assertEqual(
            sample.provenance.captured_at,
            datetime.fromtimestamp(row["update_time"] / 1000, tz=timezone.utc),
        )
        self.assertEqual(sample.provenance.raw_metadata["nickname"], row["nickname"])


if __name__ == "__main__":
    unittest.main()
