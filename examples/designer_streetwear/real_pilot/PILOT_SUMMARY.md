# Designer Streetwear — Real-Data Pilot Summary

**Date**: 2026-03-24
**Pack**: `designer_streetwear`
**Input**: `real_pilot/streetwear_collected.jsonl` (293 real posts from MediaCrawler)
**Type**: First real collected-data pilot — genuine XHS content, not curated

## Data Source

Real posts collected via MediaCrawler-jade-trend-research using CDP mode
(existing browser state) against Xiaohongshu search, in 3 consecutive runs
across 15 keywords:

| Group | Keywords | Posts | Purpose |
|-------|----------|-------|---------|
| 1 — Core streetwear | 街头穿搭, 潮牌穿搭, oversize穿搭, 工装穿搭, 机能穿搭 | 99 | Primary streetwear signal |
| 2 — Brand/product | Supreme开箱, BAPE测评, Off-White搭配, Fear of God穿搭, sacai联名 | 100 | Brand + commerce buckets |
| 3 — Noise control | 日系穿搭, 复古穿搭, 通勤穿搭, 百元穿搭, 春季穿搭 | 94 | General fashion noise |

- 20 posts per keyword (CRAWLER_MAX_NOTES_COUNT=20)
- 299 raw → 293 after dedup (5 duplicates + 2 invalid JSON lines removed)
- Mix of `video` (majority) and `normal` (image) post types
- All posts have real note IDs and xiaohongshu.com URLs

## Results (after heuristic update)

### Score Distribution

| Classification | Count | % | Notes |
|----------------|-------|---|-------|
| strong_trend_signal (≥0.70) | 1 | 0.3% | BAPE品牌深度测评 |
| emerging_pattern (0.50–0.69) | 22 | 7.5% | Brand collabs, rich outfit posts |
| weak_signal (0.25–0.49) | 125 | 42.7% | Bulk of streetwear content |
| noise (<0.25) | 145 | 49.5% | Mix of true negatives + borderline |

### Group Separation

| Group | Mean Score | Noise % |
|-------|-----------|---------|
| Group 1 (core streetwear) | 0.310 | 38% |
| Group 2 (brand/product) | 0.285 | 50% |
| Group 3 (noise control) | 0.226 | 57% |

Group 1 scores higher than Group 3 — the pack is separating streetwear from
general fashion, though the gap (0.084) is modest.

### Top 5 Scored Posts

1. **0.70** BAPE测评 — 日潮品牌质量做工个人分享
2. **0.65** Supreme开箱 — 首尔开箱#supreme #openyy #carhartt
3. **0.65** BAPE测评 — 拆箱一件bape猿人短袖
4. **0.61** 机能穿搭 — 双层废土风卫衣外套+机能弯刀工装裤
5. **0.60** 潮牌穿搭 — Stussy才是掌管潮流圈的神吧

## Heuristic Changes Made During This Pilot

Added 8 keywords based on real-data analysis:

| Bucket | Added Keywords | Reason |
|--------|---------------|--------|
| silhouette | `ootd`, `街拍`, `fit check`, `fitcheck` | 13/73 false negatives had OOTD tags; 街拍 appeared in 7 |
| graphic | `潮流`, `美式复古` | Common style descriptors in real posts |
| material | `机能风`, `工装裤` | Frequent in techwear/workwear posts, more specific than existing `机能`/`工装` |

Impact: noise classification dropped from 80% → 49%, Group 1 mean rose 0.208 → 0.310.

## What Works

1. **Brand detection is effective** — posts mentioning Supreme, BAPE, Off-White, sacai
   consistently score in weak_signal or emerging_pattern range
2. **Multi-bucket posts rank highest** — BAPE brand review (0.70) hits brand + material +
   commerce + graphic, correctly rewarded by the weighting system
3. **Group separation is real** — Group 1 mean (0.310) > Group 3 mean (0.226)
4. **Noise control catches irrelevant posts** — 57% of Group 3 correctly classified as noise
5. **Visual report is readable** — report.html renders correctly with all evidence blocks

## What Still Fails

1. **38/99 Group 1 posts still classified as noise** — remaining false negatives are
   posts where the text is minimal (just a title + emojis) or uses vocabulary outside
   any keyword list. Example: "法国人……" tagged as 街头穿搭 but has no detectable
   streetwear vocabulary in text.
2. **Image-dependent content is invisible** — many XHS streetwear posts communicate
   entirely through images/video with minimal text. The pack can only score text.
   This is a fundamental limitation of keyword heuristics.
3. **Score ceiling is low** — only 1 post reaches strong_trend_signal (0.70). The
   6-bucket binary scoring makes it hard for any single post to score very high.
4. **Group 3 false positives exist** — 9 Group 3 posts score ≥ 0.35 (e.g., "东京街头
   穷人与富人穿搭区别" from 日系穿搭 keyword). These are actually streetwear-adjacent,
   so they may not be true false positives — they're borderline content that legitimately
   overlaps.

## Is the Pack Useful on Real Data Yet?

**Partially.** It can reliably rank brand-heavy streetwear content and separate
streetwear from completely unrelated content. But its text-only heuristics miss
~38% of genuine streetwear posts because real XHS content is visual-first with
minimal text.

For a **curated research use case** (sorting a feed of collected posts into
"probably streetwear" vs "probably not"), it is useful today as a first-pass
filter. For **automated trend detection**, it needs either:
- Graduated scoring (density instead of binary)
- Image analysis integration
- A scene/occasion bucket

## What Should Improve Next

1. **Graduated scoring** — count keyword hits per bucket, use 0.0/0.3/0.6/1.0 tiers
   instead of binary 0/1. A post with 3 brand mentions should outscore one with 1.
2. **Scene bucket** — add scoring for scene/occasion terms: 音乐节, 通勤, citywalk, 校园
3. **Lower classification thresholds** — the current `noise` cutoff at 0.25 is too
   aggressive for real data. Consider 0.15 for the noise → weak_signal boundary.
4. **Cross-pack test** — run both jade and streetwear packs on the same mixed input
   to verify they discriminate correctly between categories.
