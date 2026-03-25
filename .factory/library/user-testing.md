# User Testing

Testing surface, required testing skills/tools, resource cost classification per surface.

**What belongs here:** How to test the prototype, what tools to use, concurrency limits.

---

## Validation Surface

**Surface type:** Web browser (static HTML pages served via Python http.server)
**URL:** http://localhost:8765/
**Pages to test:**
- http://localhost:8765/index.html (Homepage / 首页)
- http://localhost:8765/direction-detail.html?id=dir_001 (Direction Detail — 18K 金镶翡翠)
- http://localhost:8765/direction-map.html (Direction Map / 方向地图)
- http://localhost:8765/evidence.html (Evidence Library / 证据库)
- http://localhost:8765/product-line.html (Product Line Watch / 产品线观察)

**Testing tool:** agent-browser
**Setup required:**
1. Start the dashboard server: `cd /Users/wendy/work/content-co/intelligence && python3 -m http.server 8765 --directory dashboard`
2. Verify it's running: `curl -sf http://localhost:8765/`
3. Navigate pages with agent-browser

**Teardown:**
- `lsof -ti :8765 | xargs kill 2>/dev/null || true`

## Validation Concurrency

**Max concurrent agent-browser validators:** 3

**Rationale:**
- Machine: 16GB RAM, 10 CPU cores
- Each agent-browser session: ~300MB RAM (browser renderer + overhead)
- Each droid subagent: ~200-260MB RAM
- Combined per validator: ~500-560MB
- System baseline: ~4-5GB used
- Available headroom at 70%: ~7.7GB
- 3 validators × 560MB = 1.68GB — well within budget
- Conservative limit of 3 due to CPU contention with other running processes

## Content Verification Notes

- All UI text must be verified as Chinese (Simplified)
- Judgment states must use consistent color coding across pages
- The product name 翡翠信号图谱 should appear in branding
- Navigation between pages should be tested as cross-area flows

## Flow Validator Guidance: agent-browser

**Isolation rules:**
- Each flow validator subagent MUST use its own unique browser session ID (e.g., `6c7a7e7a0e55__homepage`, `6c7a7e7a0e55__detail`)
- Subagents testing different pages do NOT interfere — the app is read-only static HTML with no shared mutable state
- All subagents connect to the SAME server at http://localhost:8765/ (no need for separate server instances)
- Do NOT modify any files on disk during testing — read-only validation

**Browser session naming convention:**
- Data validation: no browser needed (curl/JSON inspection)
- Homepage validation: `--session "6c7a7e7a0e55__homepage"`
- Direction detail validation: `--session "6c7a7e7a0e55__detail"`

**Evidence capture:**
- Save screenshots to the evidence directory assigned in your prompt
- Name screenshots descriptively (e.g., `homepage-movement-board.png`, `detail-overview.png`)

**Testing approach:**
1. Invoke `agent-browser` skill at the start of your session
2. Navigate to the target page URL
3. Take screenshots and accessibility snapshots for each assertion
4. Check browser console for JavaScript errors
5. Close your browser session when done

**Known quirks:**
- The server is already running — do NOT start a new one
- Direction detail page URL format: `http://localhost:8765/direction-detail.html?id=dir_001`
- Pages load data from `data/jade_dashboard.json` via fetch() — wait for content to render

## Flow Validator Guidance: data-inspection

**Testing approach:**
- Use `curl` to fetch the JSON data file directly from `http://localhost:8765/data/jade_dashboard.json`
- Parse and validate using `python3 -c "..."` commands
- No browser needed for data assertions
- Verify JSON structure, field completeness, and content accuracy
