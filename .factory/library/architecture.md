# Architecture

**What belongs here:** Key architectural choices, component patterns, data flow decisions.

---

## Pipeline Architecture

```
JSONL → adapter.load_samples() → CanonicalSample → pack._bucket_scores() → ScoringEngine.score() → ScoringResult
     → direction_clustering.cluster_into_directions() → TrendDirection[]
     → frontend_builder.build_frontend_dashboard() → frontend_dashboard.json
     → pack_runner._build_report() → report files (report.json, report.md, report.html)
     → pack_runner._build_dashboard() → dashboard.json (post-level stats)
```

### Key Patterns
- All logic lives in `pack_runner.py` — workflow files are empty placeholders
- Adapters use `_common.py::build_sample()` for shared field mapping
- Packs define `_bucket_scores(sample) → dict` and a `PackSpec` dataclass
- `ScoringEngine` takes bucket scores dict → produces `ScoringResult`
- NEW: `direction_clustering` groups scored posts into trend directions using keyword_groups
- NEW: `frontend_builder` produces jade_dashboard.json-compatible JSON from direction data

### Schema Design
- Frozen dataclasses with `slots=True`
- `CanonicalSample` = `CanonicalProvenance` + `CanonicalContent` + engagement/creator/media
- NEW: `TrendDirection` dataclass for direction-level aggregation

### Output Files (7 total)
1. `normalized_samples.json` — all samples in canonical form
2. `scored_samples.json` — all samples + scoring results
3. `report.json` — compressed summary
4. `report.md` — markdown render
5. `report.html` — HTML render
6. `dashboard.json` — post-level dashboard stats
7. `frontend_dashboard.json` — NEW: direction-level dashboard data matching jade_dashboard.json schema

## Dashboard Architecture

- 5 static HTML pages with shared CSS/JS
- Data loaded via fetch() from JSON file
- Charts: pure SVG created by vanilla JS (no external libraries)
- CSS custom properties for design system (colors, typography, spacing)
- Navigation bar on all pages with active-page highlighting
