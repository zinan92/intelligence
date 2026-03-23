from __future__ import annotations

import dataclasses
import unittest
from datetime import datetime, timezone

from intelligence.schema import CanonicalContent, CanonicalProvenance, CanonicalSample
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

        self.assertEqual(field_names, {"provenance", "content"})

    def test_review_and_validation_state_are_explicit_and_defaulted(self) -> None:
        review = ReviewRecord()
        validation = ValidationRecord()

        self.assertEqual(review.state, ReviewState.PENDING)
        self.assertEqual(validation.state, ValidationState.UNVALIDATED)
        self.assertEqual(review.note, "")
        self.assertEqual(validation.note, "")


if __name__ == "__main__":
    unittest.main()
