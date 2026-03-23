"""Explicit review and validation state separate from scoring."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReviewState(str, Enum):
    """Human review state for a sample."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ValidationState(str, Enum):
    """Validation state for a sample."""

    UNVALIDATED = "unvalidated"
    VALID = "valid"
    INVALID = "invalid"


@dataclass(frozen=True, slots=True)
class ReviewRecord:
    """Human review metadata for a sample."""

    state: ReviewState = ReviewState.PENDING
    note: str = ""


@dataclass(frozen=True, slots=True)
class ValidationRecord:
    """Validation metadata for a sample."""

    state: ValidationState = ValidationState.UNVALIDATED
    note: str = ""
