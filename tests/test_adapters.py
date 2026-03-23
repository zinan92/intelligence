from __future__ import annotations

import json
import tempfile
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


def _write_jsonl(tmpdir: str, filename: str, rows: list[dict[str, object]]) -> Path:
    path = Path(tmpdir) / filename
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )
    return path


class AdapterTests(unittest.TestCase):
    def test_mediacrawler_loads_real_export_into_canonical_samples(self) -> None:
        with MEDIACRAWLER_FIXTURE.open("r", encoding="utf-8") as handle:
            first_row = json.loads(handle.readline())

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
        row = {
            "note_id": "xhs-note-001",
            "title": "jade pendant",
            "desc": "jade pendant body",
            "note_url": "https://www.xiaohongshu.com/explore/xhs-note-001",
            "time": 1710000000000,
            "last_modify_ts": 1710000005000,
            "tag_list": "jade,pendant",
            "xsec_token": "token-xhs",
            "image_list": "https://example.com/image.jpg",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = _write_jsonl(tmpdir, "xhs.jsonl", [row])
            samples = load_xhs_samples(fixture)

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
        self.assertEqual(sample.provenance.raw_metadata["xsec_token"], "token-xhs")

    def test_douyin_loader_maps_export_fields_to_canonical_samples(self) -> None:
        row = {
            "aweme_id": "douyin-001",
            "desc": "douyin body",
            "share_url": "https://www.douyin.com/video/douyin-001",
            "create_time": 1711000000000,
            "update_time": 1711000009000,
            "tag_list": "short video,jade",
            "nickname": "creator",
            "music_title": "sample track",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            fixture = _write_jsonl(tmpdir, "douyin.jsonl", [row])
            samples = load_douyin_samples(fixture)

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
        self.assertEqual(sample.provenance.raw_metadata["nickname"], "creator")


if __name__ == "__main__":
    unittest.main()
