# Environment

Environment variables, external dependencies, and setup notes.

**What belongs here:** Required env vars, external API keys/services, dependency quirks, platform-specific notes.
**What does NOT belong here:** Service ports/commands (use `.factory/services.yaml`).

---

## Runtime

- Python 3.13.7 on macOS (darwin 25.2.0)
- No npm/node required — prototype is pure static HTML/CSS/JS
- Python's built-in `http.server` used for local serving
- Git 2.50.1 available

## External Dependencies

None. The prototype is fully self-contained with no external APIs, CDNs, or network dependencies.

## Data Sources

The mock data for the dashboard is crafted from jade research artifacts within the repo and the reference repo at `/Users/wendy/work/content-co/MediaCrawler-jade-trend-merge-main/`.
