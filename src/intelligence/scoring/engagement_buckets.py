"""Engagement-derived scoring bucket functions."""

from __future__ import annotations

import math

from intelligence.schema import CanonicalEngagement


def interaction_strength(engagement: CanonicalEngagement | None) -> float:
    """
    Normalized total engagement volume (likes + saves + comments + shares).
    
    Uses log scale to bucket into 0.0-1.0 range.
    Posts with no engagement data return 0.0 (neutral, not penalized).
    
    Args:
        engagement: Engagement metrics or None
        
    Returns:
        Score between 0.0 and 1.0
    """
    if engagement is None:
        return 0.0
    
    total = (
        (engagement.likes or 0) +
        (engagement.saves or 0) +
        (engagement.comments or 0) +
        (engagement.shares or 0)
    )
    
    if total == 0:
        return 0.0
    
    # Log scale: 1-10 interactions → ~0.1, 100-1000 → ~0.3-0.5, 10K+ → ~0.7-0.9, 100K+ → ~0.95+
    # Using log10(total + 1) / 6.0 to normalize roughly to 0-1 range
    # 1M interactions → log10(1000001) ≈ 6.0 → 1.0
    score = math.log10(total + 1) / 6.0
    
    # Clamp to 0-1 range
    return min(1.0, max(0.0, score))


def commercial_intent(engagement: CanonicalEngagement | None) -> float:
    """
    Save-to-like ratio indicating purchase interest.
    
    High saves relative to likes indicates commercial/shopping intent.
    Handles division by zero (likes=0 → 0.0).
    
    Args:
        engagement: Engagement metrics or None
        
    Returns:
        Score between 0.0 and 1.0
    """
    if engagement is None:
        return 0.0
    
    likes = engagement.likes or 0
    saves = engagement.saves or 0
    
    if likes == 0:
        return 0.0
    
    # Ratio capped at 1.0 (100% save rate is theoretical max)
    ratio = saves / likes
    return min(1.0, ratio)


def propagation_velocity(engagement: CanonicalEngagement | None) -> float:
    """
    Share-to-like ratio indicating trend spreading velocity.
    
    High shares relative to likes indicates viral/trend propagation.
    Handles division by zero (likes=0 → 0.0).
    
    Args:
        engagement: Engagement metrics or None
        
    Returns:
        Score between 0.0 and 1.0
    """
    if engagement is None:
        return 0.0
    
    likes = engagement.likes or 0
    shares = engagement.shares or 0
    
    if likes == 0:
        return 0.0
    
    # Ratio capped at 1.0 (100% share rate is theoretical max)
    ratio = shares / likes
    return min(1.0, ratio)


def compute_engagement_buckets(engagement: CanonicalEngagement | None) -> dict[str, float]:
    """
    Compute all engagement-derived scoring buckets.
    
    Args:
        engagement: Engagement metrics or None
        
    Returns:
        Dictionary with interaction_strength, commercial_intent, and propagation_velocity buckets
    """
    return {
        "interaction_strength": interaction_strength(engagement),
        "commercial_intent": commercial_intent(engagement),
        "propagation_velocity": propagation_velocity(engagement),
    }
