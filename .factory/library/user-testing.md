# User Testing

Testing surface, required testing skills/tools, resource cost classification per surface.

**What belongs here:** How to test the prototype, what tools to use, concurrency limits.

---

## Validation Surface

**Surface type:** Web browser (static HTML pages served via Python http.server)
**URL:** http://localhost:8765/
**Pages to test:**
- http://localhost:8765/index.html (Homepage / 首页)
- http://localhost:8765/direction-detail.html?id=18k-gold-jade (Direction Detail)
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
