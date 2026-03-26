# Architecture

**What belongs here:** Key architectural choices, component patterns, data flow decisions.

---

## Pipeline Architecture

```
JSONL → adapter.load_samples() → CanonicalSample → pack._bucket_scores() → ScoringEngine.score() → ScoringResult → pack_runner._build_report() → output files
```

### Key Patterns
- All logic lives in `pack_runner.py` — workflow files are empty placeholders
- Adapters use `_common.py::build_sample()` for shared field mapping
- Packs define `_bucket_scores(sample) → dict` and a `PackSpec` dataclass
- `ScoringEngine` takes bucket scores dict → produces `ScoringResult`
- Report model uses `ReportBlock` (title + fields + bullets) — text-only, no structured data

### Schema Design
- Frozen dataclasses with `slots=True`
- `CanonicalSample` = `CanonicalProvenance` + `CanonicalContent`
- `raw_metadata` preserves full original data as safety net
- New fields (engagement, creator, media) use defaults for backward compatibility

### Output Files
1. `normalized_samples.json` — all samples in canonical form
2. `scored_samples.json` — all samples + scoring results
3. `report.json` — compressed summary (Report model)
4. `report.md` — markdown render
5. `report.html` — HTML render
6. `dashboard.json` — NEW: dashboard-ready output with structured fields
