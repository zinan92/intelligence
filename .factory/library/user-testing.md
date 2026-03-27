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

## Flow Validator Guidance: Pipeline (pytest + CLI)

**Testing tool:** Direct shell commands (python3, jq, pytest)

**Isolation:** Pipeline validators operate on separate output directories. Each validator uses /tmp/sw-real-test for streetwear data. Since pipeline operations are read-only against input data and write to separate output dirs, they can run concurrently.

**Key constraints:**
- Do NOT modify source code or test files
- Run pipeline command first if output doesn't exist: `python3 -m intelligence run-pack designer_streetwear --input examples/designer_streetwear/real_pilot/streetwear_collected.jsonl --output-dir /tmp/sw-real-test`
- Validate generated JSON files using python3 -c or jq
- For pytest assertions, run `python3 -m pytest tests/ -x -q`
- Output data is at /tmp/sw-real-test/frontend_dashboard.json

## Flow Validator Guidance: Dashboard (agent-browser)

**Testing tool:** agent-browser skill (Chromium browser automation)

**Server:** Dashboard server must be running on port 8765. Healthcheck: `curl -sf http://localhost:8765/index.html`

**Isolation:** Browser validators share the same HTTP server on port 8765. This is safe because all browser operations are read-only (no mutations). Each subagent must use its own --session name to avoid conflicts.

**Key constraints:**
- Always invoke agent-browser skill at session start for full documentation
- Use unique session names (e.g., "dfe7911c4702__browser1", "dfe7911c4702__browser2")
- Close sessions when done: `agent-browser --session "<session>" close`
- Default data: http://localhost:8765/index.html loads frontend_dashboard.json (streetwear data)
- Jade data: append ?data=jade_dashboard.json to any URL
- Check for JS console errors on every page load
- Save evidence screenshots to mission evidence directory
- Direction IDs from streetwear data can be discovered by loading the data JSON first
- For direction-detail testing, load the data to find valid direction IDs first

**Page URLs:**
- Homepage: http://localhost:8765/index.html
- Direction Map: http://localhost:8765/direction-map.html
- Direction Detail: http://localhost:8765/direction-detail.html?id=<direction_id>
- Evidence Library: http://localhost:8765/evidence.html
- Product Line: http://localhost:8765/product-line.html
