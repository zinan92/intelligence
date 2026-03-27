"""Direction clustering: group scored posts into trend directions."""

from __future__ import annotations

import statistics
from collections import Counter
from collections.abc import Sequence
from typing import Any

from intelligence.schema import CanonicalSample

__all__ = ["cluster_into_directions"]


def cluster_into_directions(
    scored_samples: Sequence[dict[str, Any]],
    pack_name: str,
) -> list[dict[str, Any]]:
    """
    Group scored posts into 6-10 trend directions based on keyword group overlap.
    
    Each direction represents a coherent trend with:
    - id: unique identifier
    - name: display name (Chinese, derived from top tags)
    - heat: 0-100 heat score
    - confidence_level: 高/中高/中/低
    - judgment_state: 值得跟/观察中/短热噪音/需要补证据
    - top_tags: list of representative tags
    - member_post_count: number of posts in this direction
    
    Args:
        scored_samples: List of scored sample dicts with "sample" and "result" keys
        pack_name: Pack name (jade or designer_streetwear)
    
    Returns:
        List of direction dicts, sorted by heat descending
    """
    # Get keyword groups for this pack
    keyword_groups = _get_keyword_groups(pack_name)
    
    # Assign each sample to matching keyword group(s) based on tag/content overlap
    group_assignments: dict[str, list[dict[str, Any]]] = {
        group_name: [] for group_name in keyword_groups
    }
    # Add a fallback group for unmatched posts
    group_assignments["其他趋势"] = []
    
    for scored in scored_samples:
        sample: CanonicalSample = scored["sample"]
        result = scored["result"]
        
        # Find matching groups based on tag/content overlap
        matching_groups = _find_matching_groups(sample, keyword_groups)
        
        # Assign to strongest matching group (or all if multi-keyword)
        if matching_groups:
            # For now, assign to the first matching group
            # (multi-group assignment could be added later)
            group_assignments[matching_groups[0]].append(scored)
        else:
            # Assign to fallback "其他趋势" group
            group_assignments["其他趋势"].append(scored)
    
    # Build directions from groups with enough members
    # Merge small groups into "其他趋势" to avoid orphaned posts
    # Start with lower threshold to maximize direction count
    threshold = 3
    fallback_members = group_assignments.get("其他趋势", []).copy()
    
    directions = []
    direction_id = 1
    
    for group_name, members in group_assignments.items():
        if group_name == "其他趋势":
            continue  # Handle fallback group later
        
        # For other groups, require minimum threshold
        if len(members) < threshold:
            # Merge into fallback group
            fallback_members.extend(members)
            continue
        
        direction = _build_direction(
            direction_id=f"dir_{direction_id:03d}",
            group_name=group_name,
            members=members,
        )
        directions.append(direction)
        direction_id += 1
    
    # Add fallback group if it has any members
    if len(fallback_members) > 0:
        direction = _build_direction(
            direction_id=f"dir_{direction_id:03d}",
            group_name="其他趋势",
            members=fallback_members,
        )
        directions.append(direction)
    
    # Sort by heat descending
    directions.sort(key=lambda d: d["heat"], reverse=True)
    
    # Cap at 10 directions
    return directions[:10]


def _get_keyword_groups(pack_name: str) -> dict[str, list[str]]:
    """Get keyword groups for the specified pack."""
    if pack_name == "jade":
        return {
            "成熟高端": ["18K", "金镶", "冰种", "玻璃种", "高品质", "传家", "成熟", "大气", "价值"],
            "年轻时尚": ["多巴胺", "黄翡", "紫罗兰", "红翡", "可爱", "减龄", "显白", "情绪", "年轻"],
            "文化小众": ["沉香", "叠戴", "禅修", "茶艺", "文化", "气质", "独特", "小众"],
            "入门简约": ["冰感", "小件", "简约", "清爽", "入门", "日常", "通勤", "百搭"],
        }
    elif pack_name == "designer_streetwear":
        return {
            "廓形风格": ["oversized", "oversize", "boxy", "wide-leg", "baggy", "廓形", "宽松", "阔腿", "落肩"],
            "图案印花": ["graphic", "print", "logo", "印花", "涂鸦", "标语", "字母", "卡通"],
            "日常穿搭": ["ootd", "outfit", "穿搭", "搭配", "日常", "通勤"],
            "复古美式": ["vintage", "retro", "复古", "美式", "美式复古", "old school"],
            "街拍风格": ["街拍", "街头", "street", "fitcheck", "fit check"],
            "潮牌联名": ["nike", "stussy", "supreme", "bape", "潮牌", "联名", "限定", "国潮"],
            "机能工装": ["nylon", "gore-tex", "尼龙", "机能", "工装", "冲锋衣", "机能风", "工装裤"],
            "丹宁牛仔": ["denim", "丹宁", "牛仔", "jeans"],
        }
    else:
        # Fallback: create generic groups from bucket names
        return {
            "默认方向": ["trend", "signal", "cue"],
        }


def _find_matching_groups(
    sample: CanonicalSample,
    keyword_groups: dict[str, list[str]],
) -> list[str]:
    """Find keyword groups that match this sample's tags/content."""
    text_parts = [
        sample.content.title or "",
        sample.content.text,
        " ".join(sample.content.tags),
    ]
    text = " ".join(text_parts).lower()
    
    matching_groups = []
    for group_name, keywords in keyword_groups.items():
        if any(kw.lower() in text for kw in keywords):
            matching_groups.append(group_name)
    
    return matching_groups


def _build_direction(
    direction_id: str,
    group_name: str,
    members: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a direction dict from a group of scored samples."""
    # Extract weighted scores
    weighted_scores = [m["result"].weighted_score for m in members]
    aggregate_score = statistics.mean(weighted_scores)
    
    # Extract confidence levels
    confidence_levels = [m["result"].confidence for m in members]
    confidence_counter = Counter(confidence_levels)
    most_common_confidence = confidence_counter.most_common(1)[0][0]
    
    # Map confidence to Chinese
    confidence_map = {
        "high": "高",
        "medium": "中",
        "low": "低",
    }
    confidence_cn = confidence_map.get(most_common_confidence, "中")
    
    # Determine judgment state based on aggregate score thresholds
    if aggregate_score >= 0.7:
        judgment_state = "值得跟"
    elif aggregate_score >= 0.5:
        judgment_state = "观察中"
    elif aggregate_score >= 0.3:
        judgment_state = "短热噪音"
    else:
        judgment_state = "需要补证据"
    
    # Calculate heat, opportunity, risk (0-100 scale)
    heat = int(aggregate_score * 100)
    
    # Opportunity based on score + member count
    opportunity_raw = (aggregate_score * 0.7 + min(len(members) / 100, 1.0) * 0.3)
    opportunity = int(opportunity_raw * 100)
    
    # Risk based on score consistency (std deviation)
    if len(weighted_scores) > 1:
        score_std = statistics.stdev(weighted_scores)
        risk_raw = min(score_std * 2, 1.0)  # Higher std = higher risk
    else:
        risk_raw = 0.5  # Default medium risk for single-member groups
    risk = int(risk_raw * 100)
    
    # Extract top tags
    tag_counter: Counter[str] = Counter()
    for member in members:
        sample: CanonicalSample = member["sample"]
        tag_counter.update(sample.content.tags)
    
    top_tags = [tag for tag, _count in tag_counter.most_common(10)]
    
    return {
        "id": direction_id,
        "name": group_name,
        "heat": heat,
        "confidence_level": confidence_cn,
        "judgment_state": judgment_state,
        "top_tags": top_tags,
        "member_post_count": len(members),
        # Additional metadata for frontend builder
        "_aggregate_score": aggregate_score,
        "_members": members,
    }
