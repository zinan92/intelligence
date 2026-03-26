from __future__ import annotations

import unittest

from intelligence.schema import CanonicalEngagement, CanonicalSample, CanonicalProvenance, CanonicalContent
from intelligence.workflows.jade_pack import _bucket_scores as jade_bucket_scores
from intelligence.workflows.streetwear_pack import _bucket_scores as streetwear_bucket_scores


class EngagementScoringTests(unittest.TestCase):
    """Tests for engagement-derived scoring buckets."""

    def test_high_engagement_post_scores_higher_than_low_engagement_jade(self) -> None:
        """High engagement post scores higher than low engagement with identical content."""
        provenance = CanonicalProvenance(source="test", source_id="test-001")
        content = CanonicalContent(
            text="jade pendant modern design feature",
            title="jade pendant",
            tags=("jade", "modern"),
        )
        
        high_engagement = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=CanonicalEngagement(likes=100000, saves=50000, comments=2000, shares=1000),
        )
        
        low_engagement = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=CanonicalEngagement(likes=10, saves=2, comments=0, shares=0),
        )
        
        high_scores = jade_bucket_scores(high_engagement)
        low_scores = jade_bucket_scores(low_engagement)
        
        # Keyword buckets should be identical (same content)
        self.assertEqual(high_scores["jade_signal"], low_scores["jade_signal"])
        self.assertEqual(high_scores["modernity"], low_scores["modernity"])
        self.assertEqual(high_scores["commerce"], low_scores["commerce"])
        
        # Engagement buckets should differ
        self.assertGreater(high_scores["interaction_strength"], low_scores["interaction_strength"])
        self.assertGreater(high_scores["commercial_intent"], low_scores["commercial_intent"])
        self.assertGreater(high_scores["propagation_velocity"], low_scores["propagation_velocity"])

    def test_high_engagement_post_scores_higher_than_low_engagement_streetwear(self) -> None:
        """High engagement post scores higher than low engagement with identical content."""
        provenance = CanonicalProvenance(source="test", source_id="test-001")
        content = CanonicalContent(
            text="oversized graphic streetwear ootd",
            title="streetwear outfit",
            tags=("streetwear", "ootd"),
        )
        
        high_engagement = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=CanonicalEngagement(likes=100000, saves=50000, comments=2000, shares=1000),
        )
        
        low_engagement = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=CanonicalEngagement(likes=10, saves=2, comments=0, shares=0),
        )
        
        high_scores = streetwear_bucket_scores(high_engagement)
        low_scores = streetwear_bucket_scores(low_engagement)
        
        # Keyword buckets should be identical (same content)
        for key in ["silhouette", "graphic", "layering", "brand", "material", "commerce"]:
            self.assertEqual(high_scores[key], low_scores[key])
        
        # Engagement buckets should differ
        self.assertGreater(high_scores["interaction_strength"], low_scores["interaction_strength"])
        self.assertGreater(high_scores["commercial_intent"], low_scores["commercial_intent"])
        self.assertGreater(high_scores["propagation_velocity"], low_scores["propagation_velocity"])

    def test_no_engagement_data_scores_correctly_jade(self) -> None:
        """Posts with engagement=None still score correctly using keyword buckets alone."""
        provenance = CanonicalProvenance(source="test", source_id="test-001")
        content = CanonicalContent(
            text="jade pendant modern design",
            title="jade pendant",
            tags=("jade", "pendant"),
        )
        
        sample = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=None,
        )
        
        scores = jade_bucket_scores(sample)
        
        # Should have all expected buckets
        self.assertIn("jade_signal", scores)
        self.assertIn("modernity", scores)
        self.assertIn("commerce", scores)
        self.assertIn("interaction_strength", scores)
        self.assertIn("commercial_intent", scores)
        self.assertIn("propagation_velocity", scores)
        
        # Engagement buckets should be 0.0 (neutral, not penalized)
        self.assertEqual(scores["interaction_strength"], 0.0)
        self.assertEqual(scores["commercial_intent"], 0.0)
        self.assertEqual(scores["propagation_velocity"], 0.0)
        
        # Keyword buckets should work normally
        self.assertEqual(scores["jade_signal"], 1.0)
        self.assertGreater(scores["modernity"], 0.0)
        self.assertGreater(scores["commerce"], 0.0)

    def test_no_engagement_data_scores_correctly_streetwear(self) -> None:
        """Posts with engagement=None still score correctly using keyword buckets alone."""
        provenance = CanonicalProvenance(source="test", source_id="test-001")
        content = CanonicalContent(
            text="oversized graphic streetwear",
            title="streetwear",
            tags=("streetwear",),
        )
        
        sample = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=None,
        )
        
        scores = streetwear_bucket_scores(sample)
        
        # Should have all expected buckets
        for key in ["silhouette", "graphic", "layering", "brand", "material", "commerce"]:
            self.assertIn(key, scores)
        self.assertIn("interaction_strength", scores)
        self.assertIn("commercial_intent", scores)
        self.assertIn("propagation_velocity", scores)
        
        # Engagement buckets should be 0.0 (neutral)
        self.assertEqual(scores["interaction_strength"], 0.0)
        self.assertEqual(scores["commercial_intent"], 0.0)
        self.assertEqual(scores["propagation_velocity"], 0.0)

    def test_interaction_strength_scales_with_total_engagement(self) -> None:
        """interaction_strength increases with total engagement volume."""
        provenance = CanonicalProvenance(source="test", source_id="test-001")
        content = CanonicalContent(text="test")
        
        low = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=CanonicalEngagement(likes=10, saves=5, comments=2, shares=1),
        )
        
        medium = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=CanonicalEngagement(likes=1000, saves=500, comments=100, shares=50),
        )
        
        high = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=CanonicalEngagement(likes=100000, saves=50000, comments=5000, shares=2000),
        )
        
        low_scores = jade_bucket_scores(low)
        medium_scores = jade_bucket_scores(medium)
        high_scores = jade_bucket_scores(high)
        
        self.assertLess(low_scores["interaction_strength"], medium_scores["interaction_strength"])
        self.assertLess(medium_scores["interaction_strength"], high_scores["interaction_strength"])
        
        # All should be in 0.0-1.0 range
        self.assertGreaterEqual(low_scores["interaction_strength"], 0.0)
        self.assertLessEqual(high_scores["interaction_strength"], 1.0)

    def test_commercial_intent_increases_with_save_to_like_ratio(self) -> None:
        """commercial_intent increases with save-to-like ratio."""
        provenance = CanonicalProvenance(source="test", source_id="test-001")
        content = CanonicalContent(text="test")
        
        # Low save-to-like ratio
        low_intent = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=CanonicalEngagement(likes=1000, saves=10, comments=0, shares=0),
        )
        
        # High save-to-like ratio
        high_intent = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=CanonicalEngagement(likes=1000, saves=800, comments=0, shares=0),
        )
        
        low_scores = jade_bucket_scores(low_intent)
        high_scores = jade_bucket_scores(high_intent)
        
        self.assertLess(low_scores["commercial_intent"], high_scores["commercial_intent"])

    def test_commercial_intent_handles_zero_likes(self) -> None:
        """commercial_intent returns 0.0 when likes=0 to avoid division by zero."""
        provenance = CanonicalProvenance(source="test", source_id="test-001")
        content = CanonicalContent(text="test")
        
        sample = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=CanonicalEngagement(likes=0, saves=100, comments=0, shares=0),
        )
        
        scores = jade_bucket_scores(sample)
        self.assertEqual(scores["commercial_intent"], 0.0)

    def test_propagation_velocity_increases_with_share_to_like_ratio(self) -> None:
        """propagation_velocity increases with share-to-like ratio."""
        provenance = CanonicalProvenance(source="test", source_id="test-001")
        content = CanonicalContent(text="test")
        
        # Low share-to-like ratio
        low_velocity = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=CanonicalEngagement(likes=1000, saves=0, comments=0, shares=5),
        )
        
        # High share-to-like ratio
        high_velocity = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=CanonicalEngagement(likes=1000, saves=0, comments=0, shares=500),
        )
        
        low_scores = jade_bucket_scores(low_velocity)
        high_scores = jade_bucket_scores(high_velocity)
        
        self.assertLess(low_scores["propagation_velocity"], high_scores["propagation_velocity"])

    def test_propagation_velocity_handles_zero_likes(self) -> None:
        """propagation_velocity returns 0.0 when likes=0 to avoid division by zero."""
        provenance = CanonicalProvenance(source="test", source_id="test-001")
        content = CanonicalContent(text="test")
        
        sample = CanonicalSample(
            provenance=provenance,
            content=content,
            engagement=CanonicalEngagement(likes=0, saves=0, comments=0, shares=100),
        )
        
        scores = jade_bucket_scores(sample)
        self.assertEqual(scores["propagation_velocity"], 0.0)


if __name__ == "__main__":
    unittest.main()
