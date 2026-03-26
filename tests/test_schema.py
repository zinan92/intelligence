from __future__ import annotations

import dataclasses
import unittest
from datetime import datetime, timezone

from intelligence.schema import (
    CanonicalContent,
    CanonicalCreator,
    CanonicalEngagement,
    CanonicalMedia,
    CanonicalProvenance,
    CanonicalSample,
)
from intelligence.schema.review import (
    ReviewRecord,
    ReviewState,
    ValidationRecord,
    ValidationState,
)


class SchemaTests(unittest.TestCase):
    def test_canonical_sample_keeps_provenance_and_content_separate(self) -> None:
        provenance = CanonicalProvenance(
            source="collector",
            source_id="note-001",
            url="https://example.com/note/001",
            captured_at=datetime(2026, 3, 23, tzinfo=timezone.utc),
        )
        content = CanonicalContent(text="sample body", title="sample title")

        sample = CanonicalSample(provenance=provenance, content=content)

        self.assertEqual(sample.provenance.source, "collector")
        self.assertEqual(sample.content.text, "sample body")
        self.assertEqual(sample.content.title, "sample title")

    def test_canonical_sample_has_no_review_or_scoring_fields(self) -> None:
        field_names = {field.name for field in dataclasses.fields(CanonicalSample)}

        self.assertEqual(field_names, {"provenance", "content", "engagement", "creator", "media"})

    def test_review_and_validation_state_are_explicit_and_defaulted(self) -> None:
        review = ReviewRecord()
        validation = ValidationRecord()

        self.assertEqual(review.state, ReviewState.PENDING)
        self.assertEqual(validation.state, ValidationState.UNVALIDATED)
        self.assertEqual(review.note, "")
        self.assertEqual(validation.note, "")

    def test_canonical_engagement_has_all_metrics_with_defaults(self) -> None:
        """CanonicalEngagement should have likes, saves, comments, shares with None defaults."""
        engagement = CanonicalEngagement()
        
        self.assertIsNone(engagement.likes)
        self.assertIsNone(engagement.saves)
        self.assertIsNone(engagement.comments)
        self.assertIsNone(engagement.shares)

    def test_canonical_engagement_accepts_values(self) -> None:
        """CanonicalEngagement should accept int values for all fields."""
        engagement = CanonicalEngagement(likes=100, saves=50, comments=20, shares=10)
        
        self.assertEqual(engagement.likes, 100)
        self.assertEqual(engagement.saves, 50)
        self.assertEqual(engagement.comments, 20)
        self.assertEqual(engagement.shares, 10)

    def test_canonical_creator_has_all_fields_with_defaults(self) -> None:
        """CanonicalCreator should have id, name, avatar_url, location with None defaults."""
        creator = CanonicalCreator()
        
        self.assertIsNone(creator.id)
        self.assertIsNone(creator.name)
        self.assertIsNone(creator.avatar_url)
        self.assertIsNone(creator.location)

    def test_canonical_creator_accepts_values(self) -> None:
        """CanonicalCreator should accept str values for all fields."""
        creator = CanonicalCreator(
            id="user-001",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg",
            location="Beijing"
        )
        
        self.assertEqual(creator.id, "user-001")
        self.assertEqual(creator.name, "Test User")
        self.assertEqual(creator.avatar_url, "https://example.com/avatar.jpg")
        self.assertEqual(creator.location, "Beijing")

    def test_canonical_media_has_all_fields_with_defaults(self) -> None:
        """CanonicalMedia should have content_type, image_urls, video_url with proper defaults."""
        media = CanonicalMedia()
        
        self.assertIsNone(media.content_type)
        self.assertEqual(media.image_urls, ())
        self.assertIsNone(media.video_url)

    def test_canonical_media_accepts_values(self) -> None:
        """CanonicalMedia should accept values for all fields."""
        media = CanonicalMedia(
            content_type="video",
            image_urls=("https://example.com/img1.jpg", "https://example.com/img2.jpg"),
            video_url="https://example.com/video.mp4"
        )
        
        self.assertEqual(media.content_type, "video")
        self.assertEqual(media.image_urls, ("https://example.com/img1.jpg", "https://example.com/img2.jpg"))
        self.assertEqual(media.video_url, "https://example.com/video.mp4")

    def test_canonical_sample_accepts_engagement_creator_media(self) -> None:
        """CanonicalSample should accept engagement, creator, media fields with None defaults."""
        provenance = CanonicalProvenance(
            source="test",
            source_id="001"
        )
        content = CanonicalContent(text="test")
        
        # Test with None (default)
        sample1 = CanonicalSample(provenance=provenance, content=content)
        self.assertIsNone(sample1.engagement)
        self.assertIsNone(sample1.creator)
        self.assertIsNone(sample1.media)
        
        # Test with values
        engagement = CanonicalEngagement(likes=100)
        creator = CanonicalCreator(id="user-001", name="Test")
        media = CanonicalMedia(content_type="video")
        
        sample2 = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=engagement,
            creator=creator,
            media=media
        )
        self.assertEqual(sample2.engagement, engagement)
        self.assertEqual(sample2.creator, creator)
        self.assertEqual(sample2.media, media)


if __name__ == "__main__":
    unittest.main()
