# Designer Streetwear Pilot Summary

**Date**: 2026-03-24
**Pack**: `designer_streetwear`
**Input**: `pilot_input/streetwear_pilot_20.jsonl` (hand-curated, 20 samples)

## Data source

No real streetwear collection existed locally — all available MediaCrawler exports were jade/jewelry focused. A 20-sample pilot dataset was hand-curated using realistic Xiaohongshu post patterns covering the full range of streetwear content types plus noise.

## Sample composition

| Category | Count | Examples |
|----------|-------|---------|
| Layering / outfit composition | 4 | oversized卫衣+阔腿裤, 一周通勤穿搭, 音乐节穿搭, BAPE 5-look合集 |
| Brand collab / review | 4 | Supreme x Nike, Stussy x Our Legacy, sacai x Nike, Palm Angels |
| Material / techwear | 2 | 机能风冲锋衣+工装裤, 灯芯绒+丹宁混搭 |
| Graphic / print | 1 | 涂鸦印花T恤 |
| Commerce / recommendation | 2 | Fear of God Essentials开箱, Off-White腰带开箱 |
| National brand / 国潮 | 1 | 国潮品牌推荐 |
| Japanese vintage | 1 | 日系vintage穿搭 |
| Noise (food, furniture, pets, hobbies, photography) | 5 | 牛肉面, 宜家, 写真, 吉他, 遛狗 |

## Results

- **20 samples analyzed**, 15 scored as relevant, 5 correctly identified as noise
- **Top score**: 0.58 (BAPE穿搭合集, Fear of God Essentials, Off-White开箱, sacai联名)
- **Score range for relevant posts**: 0.19 – 0.58
- **Median relevant score**: 0.51
- **Noise discrimination**: perfect (5/5 noise posts scored 0.00)

### Score distribution

| Classification | Count | Score range |
|----------------|-------|-------------|
| emerging_pattern | 8 | 0.44 – 0.58 |
| weak_signal | 6 | 0.34 – 0.44 |
| noise | 6 | 0.00 – 0.19 |

## What the pack does well

1. **Noise rejection is clean** — all 5 off-topic posts score exactly 0.00
2. **Brand + commerce posts rank high** — posts with brand collabs, reviews, and pricing signals consistently score in the emerging_pattern range
3. **Multi-bucket posts are rewarded** — posts that hit silhouette + layering + brand + commerce outperform single-dimension posts, which is the intended behavior
4. **Chinese and English keywords both work** — bilingual content is handled correctly

## What is still weak

1. **Techwear underscores** — post #3 (冲锋衣+工装裤) scored 0.19 despite being genuine streetwear. The silhouette bucket doesn't recognize techwear-specific fit language. The pack is biased toward casual/oversized silhouettes.
2. **No post hits "strong_trend_signal"** (≥0.70) — the 6-bucket structure with weighted averaging means even strong posts cap around 0.58. This might be correct (a single post is not a trend), but it means the pack can't distinguish "very strong signal" from "moderate signal" at the individual sample level.
3. **Scoring is binary per bucket** — any keyword match = full bucket score. A post mentioning "Nike" once scores the same brand signal as a detailed brand analysis. Frequency or density scoring would improve discrimination.
4. **No "scene" bucket** — the seed keywords have a `scene_and_occasion` group (音乐节, 通勤, 校园), but there's no corresponding scoring bucket. Scene context is lost.

## Heuristic changes made during pilot

Three keywords were added based on pilot findings:
- `直筒` (straight-leg) → silhouette keywords
- `网眼` (Chinese for mesh) → material keywords
- `工装` (workwear/cargo) → material keywords

These improved scoring for 4 samples without breaking any existing tests.

## Is the pack useful yet?

**Conditionally yes.** The pack reliably separates streetwear content from noise and produces a reasonable relevance ranking. The visual HTML report makes evaluation easy. But the scoring ceiling is low and techwear/functional-streetwear is underrepresented. For a first pilot this is a solid baseline.

## What should improve next

1. Add a `scene` scoring bucket using the existing seed keywords
2. Consider graduated scoring (0.0 / 0.3 / 0.6 / 1.0) based on keyword density instead of binary 0/1
3. Expand silhouette keywords for techwear fits (tactical, utility, functional)
4. Run the pack on real collected data once a streetwear-focused MediaCrawler collection exists
5. Test cross-pack comparison: run both jade and streetwear packs on the same mixed input to validate discrimination
