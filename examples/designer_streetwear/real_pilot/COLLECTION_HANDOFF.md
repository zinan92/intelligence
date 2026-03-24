# Designer Streetwear — Real-Data Collection Handoff

## Status

**No real streetwear collected data exists locally.** All MediaCrawler data on this
machine is jade/jewelry-focused. The existing `pilot_input/streetwear_pilot_20.jsonl`
uses fabricated note IDs (`pilot-001` … `pilot-020`) and `example.com` URLs — it is
curated synthetic data, not collected output.

This document specifies exactly what to collect so the real pilot can run.

## What Is Missing

A JSONL file of **real xiaohongshu posts** collected via MediaCrawler `search` mode
using streetwear/fashion keywords. The file must use standard MediaCrawler output
format (same schema the jade collection already produces).

## Recommended Keyword Groups

Collect across **3 keyword groups** to cover the streetwear spectrum. Each group
should be run as a separate `KEYWORDS` value in MediaCrawler's
`config/base_config.py`.

### Group 1 — Core streetwear styling (highest priority)

```
街头穿搭,潮牌穿搭,oversize穿搭,工装穿搭,机能穿搭
```

These target outfit-composition posts — the primary signal the pack is designed
to detect (silhouette, layering, material cues).

### Group 2 — Brand and product focus

```
Supreme开箱,BAPE测评,Off-White搭配,Fear of God穿搭,sacai联名
```

These target brand-specific content — tests the brand and commerce buckets.

### Group 3 — Broader fashion noise (control group)

```
日系穿搭,复古穿搭,通勤穿搭,百元穿搭,春季穿搭
```

These overlap with streetwear but include general fashion posts. Essential for
testing whether the pack correctly separates streetwear signals from generic
outfit content. False positives from this group reveal heuristic weaknesses.

## Recommended Sample Size

- **Minimum viable pilot**: 60 posts total (20 per keyword group)
- **Preferred**: 100–150 posts total for reliable distribution analysis
- **Maximum useful**: 300 posts (beyond this, diminishing returns for a pilot)

The MediaCrawler default collection per keyword yields ~20–30 posts per run.
Running all 3 groups once should produce 60–90 posts — sufficient for the
minimum pilot.

## What Counts as Sufficient Pilot Coverage

The pilot is sufficient when:

1. At least 50 posts are collected across all 3 groups combined
2. Each group contributes at least 10 posts
3. The data contains real `note_id` values (not `pilot-*` or `sw-note-*`)
4. Posts have real `note_url` values pointing to `xiaohongshu.com/explore/...`
5. Both `normal` (image) and `video` post types are present

## Exact Collection Steps

### Using MediaCrawler-jade-trend-research (recommended — already has browser state)

```bash
cd ~/work/content-co/MediaCrawler-jade-trend-research

# 1. Edit config to set streetwear keywords (Group 1)
#    In config/base_config.py, change:
#      KEYWORDS = "街头穿搭,潮牌穿搭,oversize穿搭,工装穿搭,机能穿搭"
#      CRAWLER_TYPE = "search"
#      PLATFORM = "xhs"

# 2. Activate venv and run
source .venv/bin/activate
python main.py

# 3. Output lands in: data/xhs/jsonl/search_contents_YYYY-MM-DD.jsonl

# 4. Repeat for Group 2 and Group 3 keywords

# 5. Merge all search_contents files into one pilot input:
cat data/xhs/jsonl/search_contents_*.jsonl > streetwear_collected.jsonl
```

### Alternative: Using MediaCrawler (base install)

```bash
cd ~/work/content-co/MediaCrawler
# Same steps — edit config/base_config.py, run, collect from data/xhs/jsonl/
```

## Running the Pilot After Collection

```bash
cd ~/work/content-co/intelligence

python -m intelligence run-pack designer_streetwear \
  --input /path/to/streetwear_collected.jsonl \
  --output-dir examples/designer_streetwear/real_pilot/output
```

This produces all 5 output files in `real_pilot/output/`. Open `report.html`
in a browser for visual evaluation.

## Evaluation Criteria for the Real Pilot

After running, check:

| Question | Where to look |
|----------|---------------|
| Do high-scoring posts actually show streetwear content? | `scored_samples.json` — sort by `weighted_score` desc |
| Do Group 3 (noise) posts score lower than Group 1? | Compare scores by `source_keyword` in metadata |
| Are there obvious false positives? | Posts scoring > 0.5 that aren't streetwear |
| Are there obvious false negatives? | Posts scoring < 0.25 that clearly are streetwear |
| Does the visual report look plausible? | `report.html` — check summary and top signal |

## Input Format Reference

Each line in the JSONL must be a JSON object with at least:

```json
{
  "note_id": "real-xhs-id",
  "type": "normal",
  "title": "post title",
  "desc": "post description with tags",
  "tag_list": "tag1,tag2,tag3",
  "note_url": "https://www.xiaohongshu.com/explore/...",
  "time": 1711900000000,
  "last_update_time": 1711900005000,
  "liked_count": "123",
  "collected_count": "45",
  "comment_count": "6",
  "source_keyword": "街头穿搭"
}
```

This is the standard MediaCrawler `search_contents` output format — no
transformation needed.
