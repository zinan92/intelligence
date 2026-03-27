# Environment

**What belongs here:** Required env vars, external API keys/services, dependency quirks, platform-specific notes.
**What does NOT belong here:** Service ports/commands (use `.factory/services.yaml`).

---

## Runtime

- Python 3.13.7 on macOS (darwin 25.2.0)
- No external dependencies — stdlib only
- pytest installed
- Git 2.50.1

## Dependencies

Zero. The project has `dependencies = []` in pyproject.toml. Keep it that way.

## Data Sources

- Test fixtures in `tests/fixtures/` (JSONL files, 1-3 rows each)
- Real pilot data in `examples/designer_streetwear/real_pilot/streetwear_collected.jsonl` (293 posts)
- Real engagement data uses Chinese number formats: "10万+", "2.1万", "9196"
- Dashboard mock data in `dashboard/data/jade_dashboard.json` (9 jade directions, 28 evidence)

## Dashboard

- Static HTML/CSS/JS in `dashboard/` directory
- Served via `python3 -m http.server 8765 --directory dashboard`
- No build step, no npm, no bundling
- Charts are pure SVG (no D3, Chart.js, or other libraries)
