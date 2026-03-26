# Intelligence Pipeline End-to-End Audit

## Pipeline Overview

```
Raw JSONL → Adapter (mediacrawler) → CanonicalSample → Pack Scoring → ScoringResult → Report → Output Files
```

The pipeline is orchestrated by `pack_runner.py::run_pack_flow()`. The individual workflow files (`ingest.py`, `normalize.py`, `score.py`, `shortlist.py`, `report.py`, `validate.py`) are **all empty placeholders** — all real logic lives in `pack_runner.py` and the pack-specific files (`jade_pack.py`, `streetwear_pack.py`).

---

## Stage 1: Raw Data (Input)

### Data Shape
JSONL file, one JSON object per line. Each row contains the full MediaCrawler/XHS export fields:

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `note_id` | string | `"mc-note-001"` | Unique post identifier |
| `type` | string | `"video"` / `"normal"` | Post type (video vs image) |
| `title` | string | `"jade pendant feature"` | Post title |
| `desc` | string | `"jade pendant body"` | Post body/description |
| `video_url` | string | `"https://example.com/video.mp4"` | Video URL (empty for image posts) |
| `time` | int (ms) | `1710000000000` | Published timestamp |
| `last_update_time` | int (ms) | `1710000005000` | Last update timestamp |
| `user_id` | string | `"creator-001"` | Creator's user ID |
| `nickname` | string | `"creator"` | Creator's display name |
| `avatar` | string | `"https://example.com/avatar.jpg"` | Creator's avatar URL |
| **`liked_count`** | string | `"10"` / `"10万+"` | **Likes count** |
| **`collected_count`** | string | `"5"` / `"2.1万"` | **Saves/collections count** |
| **`comment_count`** | string | `"2"` / `"9196"` | **Comment count** |
| **`share_count`** | string | `"1"` / `"1.3万"` | **Share count** |
| `ip_location` | string | `"Beijing"` | Creator's IP location |
| **`image_list`** | string | `"url1,url2,..."` | **Comma-separated image URLs** |
| `tag_list` | string | `"jade,pendant"` | Comma-separated tags |
| `last_modify_ts` | int (ms) | `1710000005000` | Crawl timestamp |
| `note_url` | string | XHS explore URL | Original post URL |
| `source_keyword` | string | `"jade pendant"` | Search keyword used for crawling |
| `xsec_token` | string | token value | XHS security token |

### Real-World Data Scale
The `real_pilot/streetwear_collected.jsonl` contains **293 posts** of real XHS data with engagement counts ranging from `"2317"` to `"10万+"` (100K+).

---

## Stage 2: Adapter Loading (mediacrawler.py → _common.py)

### Code Path
`adapters/mediacrawler.py::load_samples()` → `_common.py::build_sample()`

### Transform
1. Reads JSONL file line-by-line
2. For each row, calls `build_sample()` with field-name mappings
3. Extracts: `note_id` → `source_id`, `title`, `desc` → `text`, `note_url` → `url`, timestamps, tags
4. **Stores the entire raw row** in `provenance.raw_metadata` (preserving all fields)

### Output: `CanonicalSample`
```python
CanonicalSample(
    provenance=CanonicalProvenance(
        source="mediacrawler",
        source_id=str,          # from note_id
        url=str|None,           # from note_url
        captured_at=datetime|None,  # from last_modify_ts
        published_at=datetime|None, # from time
        raw_metadata=dict,      # ENTIRE original row preserved
    ),
    content=CanonicalContent(
        text=str,               # from desc (first non-empty of desc/text/content/title)
        title=str|None,         # from title
        summary=None,           # ALWAYS None - never populated
        tags=tuple[str,...],    # from tag_list (comma-split)
    ),
)
```

### ⚠️ Data Loss at This Stage

**Fields extracted into canonical schema:** `note_id`, `title`, `desc`, `note_url`, `time`, `last_modify_ts`, `tag_list`

**Fields available in raw_metadata but NOT in canonical schema:**
| Field | Available | Used in Schema | Used in Scoring | Used in Report |
|-------|-----------|----------------|-----------------|----------------|
| `liked_count` | ✅ raw_metadata | ❌ | ❌ | ❌ |
| `collected_count` | ✅ raw_metadata | ❌ | ❌ | ❌ |
| `comment_count` | ✅ raw_metadata | ❌ | ❌ | ❌ |
| `share_count` | ✅ raw_metadata | ❌ | ❌ | ❌ |
| `video_url` | ✅ raw_metadata | ❌ | ❌ | ❌ |
| `image_list` | ✅ raw_metadata | ❌ | ❌ | ❌ |
| `user_id` | ✅ raw_metadata | ❌ | ❌ | ❌ |
| `nickname` | ✅ raw_metadata | ❌ | ❌ | ❌ |
| `avatar` | ✅ raw_metadata | ❌ | ❌ | ❌ |
| `ip_location` | ✅ raw_metadata | ❌ | ❌ | ❌ |
| `type` (video/normal) | ✅ raw_metadata | ❌ | ❌ | ❌ |
| `source_keyword` | ✅ raw_metadata | ❌ | ❌ | ❌ |
| `content.summary` | Field exists | ❌ always None | ❌ | ❌ |

**Key insight:** While `raw_metadata` preserves everything, the canonical schema only surfaces 7 of ~18 fields. Everything else is technically accessible via `sample.provenance.raw_metadata["liked_count"]` but no code uses it.

---

## Stage 3: Normalization Output (_sample_payload)

### Code Path
`pack_runner.py::_sample_payload()`

### Transform
Serializes `CanonicalSample` to a flat dict for `normalized_samples.json`.

### Output Shape
```json
{
  "provenance": {
    "source": "mediacrawler",
    "source_id": "...",
    "url": "...",
    "captured_at": "ISO-8601",
    "published_at": "ISO-8601",
    "raw_metadata": { /* entire original row */ }
  },
  "content": {
    "text": "...",
    "title": "...",
    "summary": null,
    "tags": ["tag1", "tag2"]
  }
}
```

### ⚠️ Data Characteristics
- `summary` is always `null` (never computed)
- `raw_metadata` blob carries all original data, but nothing downstream reads it
- This is a 1:1 faithful serialization of `CanonicalSample`

---

## Stage 4: Scoring (Pack-specific → ScoringEngine)

### Code Path
1. Pack-specific: `jade_pack.py::_bucket_scores()` or `streetwear_pack.py::_bucket_scores()`
2. Engine: `scoring/engine.py::ScoringEngine.score()`

### Input
`CanonicalSample` — but scoring functions **only read text fields**:
```python
text_parts = [
    sample.content.title or "",
    sample.content.text,
    " ".join(sample.content.tags),
]
text = " ".join(text_parts).lower()
```

### Transform — Jade Pack
Simple keyword matching, binary scores:
- `jade_signal` = 1.0 if "jade" or "翡翠" in text, else 0.0
- `modernity` = 0.5 if "design"/"modern"/"feature" in text, else 0.0
- `commerce` = 0.7 if "pendant"/"necklace"/"bracelet"/"ring" in text, else 0.0

Weights: `jade_signal=0.5, modernity=0.25, commerce=0.25`

### Transform — Streetwear Pack
More sophisticated keyword matching with 6 buckets:
- `silhouette` = 1.0 if oversized/boxy/wide-leg/ootd/街拍 keywords
- `graphic` = 0.8 if graphic/print/logo/潮流/美式复古 keywords
- `layering` = 0.7 if layering/穿搭/叠穿 keywords
- `brand` = 0.6 if nike/stussy/supreme/潮牌 keywords
- `material` = 0.5 if nylon/denim/机能风 keywords
- `commerce` = 0.5 if buy/购物/测评/性价比 keywords

Weights: `silhouette=0.20, graphic=0.15, layering=0.20, brand=0.15, material=0.10, commerce=0.20`

### Engine Computation
```
weighted_score = Σ(bucket_value × bucket_weight) / Σ(bucket_weight)
confidence = threshold_label(weighted_score)  # high/medium/low
classification = threshold_label(weighted_score)  # various categories
```

### Output: `ScoringResult`
```python
ScoringResult(
    bucket_scores={"jade_signal": 1.0, "modernity": 0.5, "commerce": 0.7},
    weighted_score=0.80,
    confidence="high",
    classification="confirmed_continuation",
)
```

### ⚠️ What Scoring IGNORES (but Could Use)

| Data Available | Currently Used | Potential Value |
|----------------|---------------|-----------------|
| `liked_count` | ❌ | Engagement signal — viral content = validated trend |
| `collected_count` | ❌ | Save rate = commercial intent proxy |
| `comment_count` | ❌ | Discussion volume = trend controversy/interest |
| `share_count` | ❌ | Shareability = trend propagation potential |
| `video_url` presence | ❌ | Video vs image content type affects engagement |
| `image_list` | ❌ | Visual content analysis (future) |
| `nickname` / `user_id` | ❌ | Creator influence / repeat-creator patterns |
| `ip_location` | ❌ | Geographic trend clustering |
| `source_keyword` | ❌ | Which search terms surfaced this content |
| Comment text content | ❌ (not crawled) | Sentiment and demand signals |

**Critical gap:** Scoring is 100% text-keyword-based. A post with 100K+ likes and 20K saves gets the same score as a post with 10 likes if they mention the same keywords.

---

## Stage 5: Scored Output (_score_payload)

### Code Path
`pack_runner.py::_score_payload()`

### Transform
Merges `_sample_payload()` + `ScoringResult` into:

```json
{
  "sample": { /* same as normalized_samples.json entry */ },
  "bucket_scores": {"jade_signal": 1.0, "modernity": 0.5, "commerce": 0.7},
  "weighted_score": 0.80,
  "confidence": "high",
  "classification": "confirmed_continuation"
}
```

### ⚠️ Data Characteristics
- Contains full `raw_metadata` in the nested sample
- No ranking/sorting applied at this stage
- No filtering/shortlisting applied (all samples scored, all emitted)

---

## Stage 6: Report Building (_build_report)

### Code Path
`pack_runner.py::_build_report()`

### Transform
Aggregates scored samples into a `Report` model:
1. Counts total samples
2. Finds top-scoring sample by `weighted_score`
3. Extracts top sample's title, tags, and first 5 URLs
4. Builds fixed-structure report blocks

### Output: `Report` Model
```python
Report(
    title=str,                    # "Jade Pack Report"
    summary=str,                  # "...processed N samples..."
    evidence_buckets=(ReportBlock(...),),    # 1 block: sample count, source, evidence
    validation_states=(ReportBlock(...),),   # 1 block: runtime check
    trend_clusters=(ReportBlock(...),),      # 1 block: top score, confidence, class
    product_priorities=(ReportBlock(...),),  # 1 block: direction + why
    design_briefs=(ReportBlock(...),),       # 1 block: audience + material mix
)
```

Each `ReportBlock`:
```python
ReportBlock(
    title=str,
    fields=tuple[tuple[str,str],...],  # key-value pairs
    bullets=tuple[str,...],            # bullet points
)
```

### ⚠️ Massive Data Loss at Report Stage

The report compresses N scored samples into a **single-page summary**:

| What Report Shows | What Dashboard Needs |
|---|---|
| 1 top score | All scores, ranked |
| 1 summary sentence | Per-sample detail cards |
| 5 source URLs | All source URLs with thumbnails |
| Tag list (joined) | Tag frequency analysis |
| Pack-level confidence | Per-sample confidence |
| No engagement data | Likes/saves/comments per post |
| No media | Image galleries, video embeds |
| No creator info | Creator profiles, influence metrics |
| No time series | Trend over time charts |
| No geographic data | Location-based clustering |
| Static text blocks | Interactive filtering/sorting |

---

## Stage 7: Report Rendering

### Three Renderers
1. **JSON** (`json_report.py`): Serializes `Report` → JSON (faithful 1:1)
2. **Markdown** (`markdown_report.py`): Renders `Report` → MD with `#`/`##`/`###` headers + bullets
3. **HTML** (`html_report.py`): Template-based with CSS styling, linkified URLs, hero metrics bar

### All 5 Output Files
```
output_dir/
  normalized_samples.json    # All samples, canonical schema + raw_metadata
  scored_samples.json        # All samples + bucket_scores + weighted_score
  report.json                # Compressed summary (Report model)
  report.md                  # Markdown render of report
  report.html                # HTML render of report
```

---

## Complete CanonicalSample Schema

```python
@dataclass(frozen=True, slots=True)
class CanonicalProvenance:
    source: str                    # "mediacrawler" | "xhs_downloader" | "douyin_downloader"
    source_id: str                 # post unique ID
    url: str | None                # original post URL
    captured_at: datetime | None   # when crawled
    published_at: datetime | None  # when posted
    raw_metadata: dict[str, Any]   # ENTIRE original JSON row

@dataclass(frozen=True, slots=True)
class CanonicalContent:
    text: str                      # post body
    title: str | None              # post title
    summary: str | None            # ⚠️ ALWAYS None (never populated)
    tags: tuple[str, ...]          # parsed from tag_list

@dataclass(frozen=True, slots=True)
class CanonicalSample:
    provenance: CanonicalProvenance
    content: CanonicalContent
```

### Schema Also Defines (But Pipeline Never Uses):
```python
class ReviewState(str, Enum):    # PENDING / APPROVED / REJECTED
class ValidationState(str, Enum): # UNVALIDATED / VALID / INVALID
class ReviewRecord              # state + note
class ValidationRecord          # state + note
```
These are exported from `schema/__init__.py` but **never instantiated or used anywhere** in the pipeline.

---

## Scoring Engine: Computes vs Could Compute

### Currently Computes
- Weighted average of keyword-match bucket scores (binary 0/1 × fixed values)
- Threshold-based confidence label
- Threshold-based classification label

### Could Compute (with current data)
| Enhancement | Data Source | Impact |
|-------------|------------|--------|
| **Engagement-weighted scoring** | `liked_count`, `collected_count`, `share_count` from `raw_metadata` | Differentiate viral signals from noise |
| **Comment volume factor** | `comment_count` from `raw_metadata` | Controversy/interest signal |
| **Save-to-like ratio** | `collected_count / liked_count` | Commercial intent indicator |
| **Share-to-like ratio** | `share_count / liked_count` | Trend propagation velocity |
| **Content type scoring** | `type` field (video vs normal) | Video content trends differently |
| **Creator influence factor** | `nickname` frequency, engagement patterns | Repeat influencer detection |
| **Geographic clustering** | `ip_location` from `raw_metadata` | Regional trend identification |
| **Time-decay scoring** | `published_at` relative to collection | Recent = more relevant |
| **Keyword density scoring** | Count matches per bucket (not just binary) | Stronger signals from more matches |
| **Cross-sample signals** | Tag co-occurrence across samples | Topic cluster detection |

---

## Report Model: Can Express vs Dashboard Needs

### Report Model Can Express
- Title + summary string
- N sections, each with N blocks
- Each block: title + key-value fields + bullet list
- All text-based, flat structure

### Dashboard Needs (Not Expressible)
| Need | Current Support |
|------|----------------|
| Per-sample cards with thumbnails | ❌ No image URLs in report |
| Engagement metrics (likes/saves/comments) | ❌ Not in report model |
| Sort/filter by score, date, engagement | ❌ Report is static summary |
| Creator profiles with follower data | ❌ Not tracked |
| Trend-over-time visualization | ❌ No time-series data |
| Tag frequency heatmap | ❌ Tags joined into string |
| Geographic distribution map | ❌ Location data ignored |
| Video/image preview gallery | ❌ Media URLs not surfaced |
| Per-sample drill-down | ❌ Only top sample shown |
| Score distribution histogram | ❌ Only top score in report |

**Key insight:** `scored_samples.json` already has most of what the dashboard needs (including `raw_metadata` with all engagement data, media URLs, creator info). The dashboard should read `scored_samples.json` directly rather than the compressed `report.json`.

---

## Pipeline Stage Upgrade Recommendations

### Priority 1: Engagement Data into Scoring (HIGH IMPACT)
**Stage:** Scoring (Stage 4)
**What:** Parse engagement counts from `raw_metadata` and incorporate into scoring
**Why:** A post with 100K likes is a fundamentally different signal than one with 10 likes
**How:**
1. Add engagement parsing to `_common.py` (handle Chinese number formats like "10万+", "2.1万")
2. Add `CanonicalEngagement` to canonical schema: `likes`, `saves`, `comments`, `shares`
3. Add engagement buckets to pack scoring functions
4. Or add an engagement multiplier to `ScoringEngine`

### Priority 2: Structured Engagement in CanonicalSample (HIGH IMPACT)
**Stage:** Schema (canonical.py) + Adapter (Stage 2)
**What:** Add `engagement` field to `CanonicalSample`
**Why:** Currently engagement lives only in opaque `raw_metadata` dict; should be first-class
**How:**
```python
@dataclass(frozen=True, slots=True)
class CanonicalEngagement:
    likes: int | None = None
    saves: int | None = None
    comments: int | None = None
    shares: int | None = None

@dataclass(frozen=True, slots=True)
class CanonicalSample:
    provenance: CanonicalProvenance
    content: CanonicalContent
    engagement: CanonicalEngagement | None = None  # NEW
```

### Priority 3: Media URLs as First-Class Fields (MEDIUM IMPACT)
**Stage:** Schema + Adapter (Stage 2)
**What:** Surface `image_list` and `video_url` in canonical schema
**Why:** Dashboard needs thumbnails; future scoring could use media presence
**How:** Add `media_urls: tuple[str, ...]` and `video_url: str | None` to `CanonicalContent` or new `CanonicalMedia` dataclass

### Priority 4: Creator Info as First-Class Fields (MEDIUM IMPACT)
**Stage:** Schema + Adapter (Stage 2)
**What:** Surface `user_id`, `nickname`, `avatar` in canonical schema
**Why:** Creator influence patterns, repeat-creator detection
**How:** Add `CanonicalCreator` dataclass with `id`, `name`, `avatar_url`, `location`

### Priority 5: Dashboard-Oriented Output Format (HIGH IMPACT)
**Stage:** Report (Stage 6-7)
**What:** Generate a dashboard-ready JSON output alongside current reports
**Why:** Current `report.json` compresses 293 samples into a 1-page summary; dashboard needs per-sample data
**How:** Either:
- Point dashboard directly at `scored_samples.json` (already exists, has everything)
- Or create a new `dashboard.json` with engagement stats, media URLs, score distributions, tag frequency

### Priority 6: Chinese Number Parsing (QUICK WIN)
**Stage:** Adapter/Common (Stage 2)
**What:** Parse "10万+", "2.1万" into integers
**Why:** Real data uses Chinese abbreviated numbers; current pipeline ignores these completely
**How:** Add parser in `_common.py` for `万` (10K), `千` (1K), strip `+`

### Priority 7: Populate summary Field (LOW EFFORT)
**Stage:** Scoring or Post-scoring
**What:** Auto-generate `content.summary` using first N chars or LLM
**Why:** Field exists in schema but is always `None`

### Priority 8: Implement Workflow Modules (ARCHITECTURAL)
**Stage:** All placeholder files
**What:** Move logic from `pack_runner.py` monolith into proper `ingest.py`, `normalize.py`, `score.py`, `shortlist.py`, `report.py`, `validate.py`
**Why:** Better separation of concerns, testability, and extensibility
**Current state:** All 6 workflow files are empty placeholders

### Priority 9: Use ReviewRecord/ValidationRecord (LOW PRIORITY)
**Stage:** Schema integration
**What:** Wire `ReviewRecord` and `ValidationRecord` into the pipeline
**Why:** Schema defines them but nothing uses them; could enable human-in-the-loop review

---

## Data Flow Summary Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  RAW JSONL (18+ fields per row)                                 │
│  note_id, type, title, desc, video_url, time,                   │
│  user_id, nickname, avatar, liked_count, collected_count,       │
│  comment_count, share_count, ip_location, image_list,           │
│  tag_list, note_url, source_keyword, xsec_token                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ADAPTER: build_sample()                                        │
│  Extracts: note_id, title, desc, note_url, timestamps, tags     │
│  Preserves: raw_metadata = entire original row                  │
│  DROPS from schema: engagement, media, creator, location, type  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  CanonicalSample                                                │
│  ├─ provenance.source_id       ✅ used                         │
│  ├─ provenance.url             ✅ used in report evidence       │
│  ├─ provenance.captured_at     ✅ serialized, not used          │
│  ├─ provenance.published_at    ✅ serialized, not used          │
│  ├─ provenance.raw_metadata    ⚠️  serialized, never queried    │
│  ├─ content.text               ✅ used in scoring               │
│  ├─ content.title              ✅ used in scoring + report       │
│  ├─ content.summary            ❌ always None                   │
│  └─ content.tags               ✅ used in scoring + report       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  SCORING: _bucket_scores() + ScoringEngine.score()              │
│  INPUT: title + text + tags (concatenated, lowercased)          │
│  METHOD: keyword substring matching → binary bucket scores      │
│  IGNORES: engagement, media, creator, location, timestamps      │
│  OUTPUT: bucket_scores + weighted_score + confidence + class     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  REPORT: _build_report()                                        │
│  INPUT: all samples + all scored samples                        │
│  COMPRESSES: N samples → 1 summary + 1 top score + 5 URLs      │
│  DROPS: per-sample detail, score distribution, time series      │
│  OUTPUT: Report model (5 sections × 1 block each)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT FILES                                                    │
│  ├─ normalized_samples.json  (has raw_metadata with everything) │
│  ├─ scored_samples.json      (has scores + raw_metadata)        │
│  ├─ report.json              (compressed summary only)          │
│  ├─ report.md                (same as report.json in markdown)  │
│  └─ report.html              (same as report.json in HTML)      │
└─────────────────────────────────────────────────────────────────┘
```

## Key Findings

1. **Engagement data flows through the entire pipeline but is NEVER used** — liked_count, collected_count, comment_count, share_count are preserved in raw_metadata but never extracted, parsed, or scored

2. **Media URLs flow through but are NEVER surfaced** — video_url and image_list are in raw_metadata but never used for display or analysis

3. **Creator info flows through but is NEVER used** — user_id, nickname, avatar enable influencer analysis but are ignored

4. **Scoring is entirely text-based** — keyword matching on title+desc+tags only; no engagement weighting

5. **Report compresses everything to a single page** — 293 posts become 1 summary paragraph + 1 top score

6. **scored_samples.json is actually the best output** — it has everything the dashboard needs, including raw_metadata with all engagement and media data

7. **Chinese number format engagement data is unparsed** — "10万+" (100K+), "2.1万" (21K) are stored as strings, never converted to integers

8. **6 of 7 workflow files are empty placeholders** — all logic lives in pack_runner.py

9. **ReviewRecord/ValidationRecord schemas exist but are never used**

10. **content.summary is always None** — the field exists but nothing populates it
