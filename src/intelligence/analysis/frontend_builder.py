"""Frontend dashboard JSON builder: convert directions to jade_dashboard.json-compatible format."""

from __future__ import annotations

import hashlib
import random
import statistics
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from intelligence.schema import CanonicalSample

__all__ = ["build_frontend_dashboard"]


def build_frontend_dashboard(
    directions: list[dict[str, Any]],
    scored_samples: list[dict[str, Any]],
    pack_name: str,
) -> dict[str, Any]:
    """
    Build frontend_dashboard.json from trend directions and scored samples.
    
    Must match jade_dashboard.json schema exactly with all required fields.
    
    Args:
        directions: List of direction dicts from cluster_into_directions()
        scored_samples: List of scored sample dicts
        pack_name: Pack name for product_name field
    
    Returns:
        Dashboard JSON dict matching jade_dashboard.json schema
    """
    # Build fully-specified trend_directions and enrich directions with product_line_breakdown
    trend_directions = []
    for i, d in enumerate(directions):
        trend_dir = _build_trend_direction(d, i+1)
        # Store product_line_breakdown back in direction for evidence generation
        d["_product_line_breakdown"] = trend_dir["product_line_breakdown"]
        trend_directions.append(trend_dir)
    
    # Count judgment states
    today_judgments = {
        "值得跟": sum(1 for d in directions if d["judgment_state"] == "值得跟"),
        "观察中": sum(1 for d in directions if d["judgment_state"] == "观察中"),
        "短热噪音": sum(1 for d in directions if d["judgment_state"] == "短热噪音"),
        "需要补证据": sum(1 for d in directions if d["judgment_state"] == "需要补证据"),
    }
    
    # Generate product lines
    product_lines = _generate_product_lines(directions, pack_name)
    
    # Generate evidence entries (now has access to product_line_breakdown)
    evidence_entries = _generate_evidence_entries(directions, scored_samples)
    
    # Generate fourteen_day_changes
    fourteen_day_changes = _generate_fourteen_day_changes(directions)
    
    # Generate executive summary
    executive_summary = _generate_executive_summary(directions, pack_name)
    
    # Generate keyword groups
    keyword_groups = _generate_keyword_groups(pack_name)
    
    # Generate scoring model info (matching jade_dashboard.json schema)
    scoring_model = {
        "heat_weight": 0.3,
        "confidence_weight": 0.25,
        "audience_fit_weight": 0.25,
        "price_band_fit_weight": 0.2,
    }
    
    return {
        "product_name": "潮流信号图谱" if pack_name == "designer_streetwear" else "翡翠信号图谱",
        "timestamp": datetime.now(timezone.utc).date().isoformat(),
        "executive_summary": executive_summary,
        "today_judgments": today_judgments,
        "trend_directions": trend_directions,
        "product_lines": product_lines,
        "evidence_entries": evidence_entries,
        "fourteen_day_changes": fourteen_day_changes,
        "scoring_model": scoring_model,
        "keyword_groups": keyword_groups,
    }


def _build_trend_direction(direction: dict[str, Any], idx: int) -> dict[str, Any]:
    """Build a fully-specified trend direction with all required fields."""
    # Extract metadata from clustering
    aggregate_score = direction.get("_aggregate_score", 0.5)
    members = direction.get("_members", [])
    
    # Generate synthetic movement_history (14 data points)
    # Simulate trend from engagement distribution
    heat = direction["heat"]
    movement_history = _generate_movement_history(heat, members, direction["name"])
    
    # Map confidence to classification
    classification_map = {
        "值得跟": "confirmed_continuation",
        "观察中": "watchlist_experiment",
        "短热噪音": "avoid_for_now",
        "需要补证据": "emerging_opportunity",
    }
    classification = classification_map.get(direction["judgment_state"], "watchlist_experiment")
    
    # Generate product_line_breakdown
    product_line_breakdown = _generate_product_line_breakdown(direction, aggregate_score)
    
    # Calculate opportunity and risk (already in direction, but ensure 0-100)
    opportunity = min(max(int(aggregate_score * 100), 0), 100)
    risk = min(max(int((1 - aggregate_score) * 80), 10), 100)
    
    return {
        "id": direction["id"],
        "name": direction["name"],
        "description": f"{direction['name']}趋势方向的核心特征和受众定位",
        "heat_magnitude": f"+{heat // 3}%",
        "time_window": "最近30天",
        "confidence_level": direction["confidence_level"],
        "classification": classification,
        "judgment_state": direction["judgment_state"],
        "audience_fit": "18-35 核心群体",
        "price_band_fit": "中/低中",
        "opportunity": opportunity,
        "risk": risk,
        "heat": heat,
        "movement_history": movement_history,
        "product_line_breakdown": product_line_breakdown,
        "risks": [
            {
                "description": "市场饱和风险",
                "severity": "medium",
                "mitigation": "差异化定位"
            }
        ],
        "evidence_summary": f"{direction['member_post_count']} 个相关内容，评论聚焦核心标签",
        "proof_snapshot": {
            "sample_count": direction["member_post_count"],
            "strongest_examples": [f"示例 #{i+1}" for i in range(min(3, direction["member_post_count"]))],
            "comment_themes": direction["top_tags"][:3],
            "cross_category_support": "多场景适配"
        },
        "one_line_recommendation": f"基于 {direction['member_post_count']} 个样本的趋势判断",
        "content_cues": {
            "how_to_photograph": "清晰展示产品特征",
            "how_to_narrate": "突出核心卖点",
            "what_not_to_do": "避免过度修图"
        },
        "why_it_matters": f"{direction['name']}在最近数据中显示出稳定的趋势特征，值得关注。",
        "freshness": "最近30天"
    }


def _generate_movement_history(heat: int, members: list[dict[str, Any]], direction_name: str) -> list[int]:
    """Generate synthetic 14-day movement history from heat and member distribution.
    
    Args:
        heat: Current heat value (0-100)
        members: List of member post dicts
        direction_name: Direction name for deterministic seeding
    
    Returns:
        List of 14 integers representing movement history
    """
    # Seed random with deterministic hash of direction name (using hashlib for reproducibility)
    # Python's built-in hash() is randomized across processes for security
    seed = int(hashlib.md5(direction_name.encode('utf-8')).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    
    # Simulate trend curve: start lower, trend upward to current heat
    base = max(heat - 30, 20)
    trend = []
    for i in range(14):
        # Linear growth from base to heat
        value = base + (heat - base) * i / 13
        # Add some randomness (now deterministic)
        noise = rng.randint(-3, 3)
        trend.append(max(0, min(100, int(value + noise))))
    return trend


def _generate_product_line_breakdown(direction: dict[str, Any], score: float) -> dict[str, Any]:
    """Generate product_line_breakdown for a direction."""
    # Default product lines vary by pack
    # For streetwear: tops, bottoms, outerwear, accessories
    # For jade: necklace, earrings, rings, bracelets
    
    # Generate varied breakdown based on direction characteristics
    # Use deterministic hash to pick primary product line
    direction_name = direction["name"]
    seed = int(hashlib.md5(direction_name.encode('utf-8')).hexdigest(), 16)
    
    # Product line priorities based on direction name hash (deterministic)
    product_lines = ["上装", "下装", "外套", "配饰"]
    # Rotate product lines based on seed to vary primary line
    primary_idx = seed % len(product_lines)
    secondary_idx = (seed + 1) % len(product_lines)
    tertiary_idx = (seed + 2) % len(product_lines)
    fourth_idx = (seed + 3) % len(product_lines)
    
    primary_line = product_lines[primary_idx]
    secondary_line = product_lines[secondary_idx]
    tertiary_line = product_lines[tertiary_idx]
    fourth_line = product_lines[fourth_idx]
    
    # Generate opportunity/risk based on score
    if score >= 0.7:
        primary_opp, primary_risk = "高", "低中"
        secondary_opp, secondary_risk = "中高", "中"
    elif score >= 0.5:
        primary_opp, primary_risk = "中高", "中"
        secondary_opp, secondary_risk = "中", "中高"
    else:
        primary_opp, primary_risk = "中", "中高"
        secondary_opp, secondary_risk = "低中", "高"
    
    return {
        primary_line: {
            "opportunity": primary_opp,
            "risk": primary_risk,
            "rationale": f"趋势得分 {score:.2f}，{primary_line}适配度高"
        },
        secondary_line: {
            "opportunity": secondary_opp,
            "risk": secondary_risk,
            "rationale": "与核心趋势匹配"
        },
        tertiary_line: {
            "opportunity": "中",
            "risk": "中",
            "rationale": "证据中等"
        },
        fourth_line: {
            "opportunity": "低中",
            "risk": "中高",
            "rationale": "证据较少"
        }
    }


def _generate_product_lines(directions: list[dict[str, Any]], pack_name: str) -> list[dict[str, Any]]:
    """Generate product_lines array with strengthening/weakening direction linkages."""
    if pack_name == "designer_streetwear":
        product_line_names = ["上装", "下装", "外套", "配饰"]
    else:
        product_line_names = ["项链/吊坠", "耳饰", "戒指", "手串/叠戴"]
    
    product_lines = []
    for pl_name in product_line_names:
        # Pick top directions as strengthening
        strengthening = [d["name"] for d in directions[:3] if d["heat"] >= 50]
        weakening = [d["name"] for d in directions if d["heat"] < 40][:2]
        
        product_lines.append({
            "id": f"pl_{len(product_lines)+1:03d}",
            "name": pl_name,
            "opportunity_level": "高" if strengthening else "中",
            "risk_level": "低中" if not weakening else "中",
            "movement_status": "上升" if strengthening else "稳定",
            "reasoning": f"{len(strengthening)} 个趋势支持，{len(weakening)} 个趋势削弱",
            "strengthening_directions": strengthening,
            "weakening_directions": weakening
        })
    
    return product_lines


def _generate_evidence_entries(
    directions: list[dict[str, Any]],
    scored_samples: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate evidence_entries from top-scoring posts per direction."""
    evidence_entries = []
    entry_id = 1
    
    for direction in directions:
        members = direction.get("_members", [])
        if not members:
            continue
        
        # Derive primary product line from direction's product_line_breakdown
        product_line_breakdown = direction.get("_product_line_breakdown", {})
        if product_line_breakdown:
            # Pick the product line with highest opportunity
            primary_product_line = max(
                product_line_breakdown.keys(),
                key=lambda k: {"高": 3, "中高": 2, "中": 1, "低": 0, "低中": 0.5}.get(
                    product_line_breakdown[k].get("opportunity", "中"), 1
                )
            )
        else:
            # Fallback to "上装" if no breakdown available
            primary_product_line = "上装"
        
        # Get top 3 scoring members
        top_members = sorted(members, key=lambda m: m["result"].weighted_score, reverse=True)[:3]
        
        for member in top_members:
            sample: CanonicalSample = member["sample"]
            result = member["result"]
            
            # Determine weight based on score
            if result.weighted_score >= 0.7:
                weight = "high"
            elif result.weighted_score >= 0.4:
                weight = "medium"
            else:
                weight = "low"
            
            evidence_entries.append({
                "id": f"evid_{entry_id:03d}",
                "type": "笔记",
                "title": sample.content.title or f"内容 #{entry_id}",
                "source": sample.provenance.source,
                "related_direction": direction["name"],
                "freshness": "最近7天",
                "relevance_explanation": f"得分 {result.weighted_score:.2f}",
                "weight": weight,
                "product_line": primary_product_line,
                "timestamp": sample.provenance.published_at.date().isoformat() if sample.provenance.published_at else "2026-03-27"
            })
            entry_id += 1
            
            # Limit total evidence entries
            if entry_id > 50:
                break
        
        if entry_id > 50:
            break
    
    return evidence_entries


def _generate_fourteen_day_changes(directions: list[dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    """Generate fourteen_day_changes with rising/cooling/newly_emerging keys.
    
    Each item is a dict with:
    - direction: direction name (str)
    - change: change indicator like '+12%' or 'new' (str)
    - reason: short Chinese explanation (str)
    """
    # Top 30% by heat are rising
    # Bottom 30% are cooling
    # Middle can be newly_emerging if heat is moderate
    
    sorted_dirs = sorted(directions, key=lambda d: d["heat"], reverse=True)
    
    rising_count = max(1, len(sorted_dirs) // 3)
    cooling_count = max(1, len(sorted_dirs) // 3)
    
    rising_dirs = sorted_dirs[:rising_count]
    cooling_dirs = sorted_dirs[-cooling_count:]
    
    # Newly emerging: directions with moderate heat but low member count (small but growing)
    newly_emerging_dirs = [
        d for d in directions
        if 40 <= d["heat"] <= 70 and d["member_post_count"] < 30 and d["name"] not in [d["name"] for d in rising_dirs]
    ][:2]
    
    # Build dicts with direction/change/reason
    rising = [
        {
            "direction": d["name"],
            "change": f"+{d['heat'] // 3}%",
            "reason": f"热度上升至 {d['heat']}/100，样本量 {d['member_post_count']}"
        }
        for d in rising_dirs
    ]
    
    cooling = [
        {
            "direction": d["name"],
            "change": f"-{(100 - d['heat']) // 4}%",
            "reason": f"热度降至 {d['heat']}/100，关注度下降"
        }
        for d in cooling_dirs
    ]
    
    newly_emerging = [
        {
            "direction": d["name"],
            "change": "new",
            "reason": f"新兴趋势，当前热度 {d['heat']}/100"
        }
        for d in newly_emerging_dirs
    ]
    
    return {
        "rising": rising,
        "cooling": cooling,
        "newly_emerging": newly_emerging
    }


def _generate_executive_summary(directions: list[dict[str, Any]], pack_name: str) -> dict[str, str]:
    """Generate executive summary from top directions."""
    top_dir = directions[0] if directions else None
    
    if not top_dir:
        return {
            "one_line": "暂无明确趋势",
            "key_opportunity": "数据不足",
            "key_risk": "需要更多证据"
        }
    
    # Find highest-heat direction
    opportunity_dir = max(directions, key=lambda d: d["heat"])
    
    # Find direction with most posts
    risk_dirs = [d for d in directions if d["judgment_state"] in ["短热噪音", "需要补证据"]]
    risk_dir = risk_dirs[0] if risk_dirs else directions[-1]
    
    return {
        "one_line": f"{top_dir['name']}领先，{len(directions)} 个趋势方向值得关注",
        "key_opportunity": f"{opportunity_dir['name']}热度 {opportunity_dir['heat']}/100，样本量 {opportunity_dir['member_post_count']}",
        "key_risk": f"{risk_dir['name']}需要更多验证"
    }


def _generate_keyword_groups(pack_name: str) -> dict[str, list[str]]:
    """Generate keyword_groups metadata."""
    if pack_name == "jade":
        return {
            "成熟高端": ["金镶", "冰种", "玻璃种"],
            "年轻时尚": ["多巴胺", "色系", "耳饰"],
            "文化小众": ["沉香", "叠戴", "文化"],
            "入门简约": ["小件", "吊坠", "简约"]
        }
    elif pack_name == "designer_streetwear":
        return {
            "廓形风格": ["oversized", "宽松", "廓形"],
            "图案印花": ["graphic", "印花", "图案"],
            "日常穿搭": ["ootd", "穿搭", "搭配"],
            "潮牌联名": ["潮牌", "联名", "限定"]
        }
    else:
        return {}
