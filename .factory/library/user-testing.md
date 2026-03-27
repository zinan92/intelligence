# User Testing

**What belongs here:** How to test the dashboard and pipeline, tools, concurrency limits.

---

## Validation Surfaces

### Surface 1: Pipeline (pytest + CLI)
- **Test command:** `python3 -m pytest tests/ -x -q`
- **Pack commands:**
  - `python3 -m intelligence run-pack designer_streetwear --input examples/designer_streetwear/real_pilot/streetwear_collected.jsonl --output-dir /tmp/sw-real-test`
  - `python3 -m intelligence run-pack jade --output-dir /tmp/jade-test`
- **Validation:** JSON schema checks, file existence, field-by-field assertions

### Surface 2: Dashboard (agent-browser)
- **Server:** `python3 -m http.server 8765 --directory dashboard`
- **Pages to test:**
  - http://localhost:8765/index.html (homepage)
  - http://localhost:8765/direction-map.html (bubble matrix)
  - http://localhost:8765/direction-detail.html?id=<id> (direction detail)
  - http://localhost:8765/evidence.html (evidence library)
  - http://localhost:8765/product-line.html (product line watch)
- **Validation:** Screenshots, DOM inspection, console error checks, interaction tests

## Validation Concurrency

**Max concurrent validators:** 3

**Rationale:**
- Machine: 16GB RAM, 10 CPU cores
- Each agent-browser session: ~488MB (Chromium + HTTP server)
- Baseline usage: ~6GB
- Available headroom: ~10GB * 0.7 = 7GB
- 3 sessions: ~1.5GB (well within budget)

## Data Sources for Testing

- **Streetwear real data:** `examples/designer_streetwear/real_pilot/streetwear_collected.jsonl` (293 posts)
- **Jade mock data:** `dashboard/data/jade_dashboard.json` (9 directions, 28 evidence — for backward compat testing)
- **Pipeline-generated:** `frontend_dashboard.json` in output directory (generated from streetwear real data)

## Important: Backward Compatibility Testing

Every frontend change must be tested with BOTH:
1. Pipeline-generated streetwear data (primary)
2. Existing jade_dashboard.json (backward compat)

The data.js loader should support both data sources.
