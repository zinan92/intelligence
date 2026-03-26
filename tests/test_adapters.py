from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from intelligence.adapters.douyin_downloader import load_samples as load_douyin_samples
from intelligence.adapters.mediacrawler import load_samples as load_mediacrawler_samples
from intelligence.adapters.xhs_downloader import load_samples as load_xhs_samples
from intelligence.schema import CanonicalSample


FIXTURES_DIR = Path(__file__).with_name("fixtures")
MEDIACRAWLER_FIXTURE = FIXTURES_DIR / "mediacrawler_jade_export.jsonl"
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

    def test_mediacrawler_extracts_engagement_data(self) -> None:
        """MediaCrawler adapter extracts engagement metrics from raw data."""
        first_row = _read_first_row(MEDIACRAWLER_FIXTURE)
        samples = load_mediacrawler_samples(MEDIACRAWLER_FIXTURE)
        sample = samples[0]

        self.assertIsNotNone(sample.engagement)
        self.assertEqual(sample.engagement.likes, 10)
        self.assertEqual(sample.engagement.saves, 5)
        self.assertEqual(sample.engagement.comments, 2)
        self.assertEqual(sample.engagement.shares, 1)

    def test_mediacrawler_extracts_creator_data(self) -> None:
        """MediaCrawler adapter extracts creator information from raw data."""
        first_row = _read_first_row(MEDIACRAWLER_FIXTURE)
        samples = load_mediacrawler_samples(MEDIACRAWLER_FIXTURE)
        sample = samples[0]

        self.assertIsNotNone(sample.creator)
        self.assertEqual(sample.creator.id, "creator-001")
        self.assertEqual(sample.creator.name, "creator")
        self.assertEqual(sample.creator.avatar_url, "https://example.com/avatar.jpg")
        self.assertEqual(sample.creator.location, "Beijing")

    def test_mediacrawler_extracts_media_data(self) -> None:
        """MediaCrawler adapter extracts media type and URLs from raw data."""
        first_row = _read_first_row(MEDIACRAWLER_FIXTURE)
        samples = load_mediacrawler_samples(MEDIACRAWLER_FIXTURE)
        sample = samples[0]

        self.assertIsNotNone(sample.media)
        self.assertEqual(sample.media.content_type, "video")
        self.assertEqual(sample.media.image_urls, ("https://example.com/image.jpg",))
        self.assertEqual(sample.media.video_url, "https://example.com/video.mp4")

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
        self.assertEqual(sample.provenance.url, row.get("aweme_url") or row.get("share_url"))
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
