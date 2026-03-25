---
name: prototype-worker
description: Builds static HTML/CSS/JS dashboard pages for the Jade Signal Atlas prototype
---

# Prototype Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

Use for features that involve:
- Creating or modifying HTML pages for the dashboard prototype
- Creating or modifying CSS styles and JS logic
- Creating or modifying the mock data JSON file
- Building UI components (cards, modules, panels, navigation)
- Cross-page polish and consistency work

## Required Skills

None. This worker uses standard file creation/editing tools and shell commands.

## Work Procedure

### 1. Read Context First

Before writing any code:
- Read `AGENTS.md` for architecture, conventions, and mock data values
- Read the feature's `description`, `preconditions`, `expectedBehavior`, and `verificationSteps`
- If building a page that depends on shared CSS/JS, read those files first to understand existing patterns
- If building a page that loads data, read `dashboard/data/jade_dashboard.json` to understand the data schema
- If the feature references the approved design spec or HTML brainstorm artifacts, read those for design guidance

### 2. Plan Your Implementation

For each page/component:
- Identify what HTML structure is needed
- Identify what CSS classes and custom properties to use/create
- Identify what JS data loading and rendering logic is needed
- Check what shared utilities already exist in `js/` to avoid duplication

### 3. Build Incrementally

For data features:
- Create the JSON file with the full schema
- Validate it: `python3 -c "import json; json.load(open('dashboard/data/jade_dashboard.json')); print('Valid')"`
- Verify it contains all required fields per the feature description

For page features:
- Create the HTML file with proper `<meta charset="UTF-8">`, `<html lang="zh-CN">`, and shared CSS/JS references
- Build the page structure with semantic HTML
- Add CSS styles (in shared `css/style.css` for reusable styles, inline `<style>` only for truly page-specific overrides)
- Add JS rendering logic (prefer shared `js/` modules, page-specific `<script>` for page init)
- Ensure all text content is in Chinese

For CSS/JS foundation features:
- Define CSS custom properties for the full design system (colors, typography, spacing, card styles, badge styles)
- Create reusable JS functions for data loading, component rendering, navigation
- Build the navigation bar component that all pages share

### 4. Verify Your Work

**Automated checks (run ALL of these):**
- `python3 -c "import json; json.load(open('dashboard/data/jade_dashboard.json')); print('JSON valid')"` (if data file exists)
- Start the server: `cd /Users/wendy/work/content-co/intelligence && python3 -m http.server 8765 --directory dashboard &` and note the PID
- `curl -sf http://localhost:8765/` to verify server is running
- `curl -sf http://localhost:8765/index.html` (and other pages you built) to verify they load
- Kill the server when done: `kill <PID>` or `lsof -ti :8765 | xargs kill`

**Manual verification with agent-browser (REQUIRED for page features):**
- Start the dashboard server (background)
- Use agent-browser to open each page you built
- Take a screenshot of each page
- Verify via accessibility snapshot that Chinese text is present
- Check for console errors
- Verify the visual layout matches expectations
- Stop the server

**Content checks:**
- All visible text is in Chinese
- Direction names, judgment states, product lines use the exact strings from AGENTS.md
- Navigation bar shows all nav items
- Color coding is consistent with the design system

### 5. Run Existing Tests

Run `python3 -m pytest tests/ -x -q` to ensure existing tests still pass. The dashboard should not break existing Python tests.

### 6. Commit

Commit with a clear message describing what was built. Only commit files in the `dashboard/` directory and `.factory/` if library updates are needed.

## Example Handoff

```json
{
  "salientSummary": "Built the homepage dashboard with all 7 modules (Movement Board, Judgment Summary, Watchlist Cards, Risk Alerts, Evidence Feed, Product Line Snapshot, 14-Day Change). Verified with agent-browser: all modules render with Chinese content, signal-first layout confirmed, color-coded judgment badges visible. No console errors. pytest passes.",
  "whatWasImplemented": "dashboard/index.html with 7 dashboard modules using grid layout. Shared CSS custom properties for judgment state colors (green=值得跟, blue=观察中, orange=短热噪音, gray=需要补证据). Navigation bar with 翡翠信号图谱 branding and 4 nav links. Data loaded from jade_dashboard.json via fetch(). Responsive grid: 2-column for Movement Board row, 3-column for middle row, 2-column for bottom row.",
  "whatWasLeftUndone": "",
  "verification": {
    "commandsRun": [
      { "command": "python3 -c \"import json; json.load(open('dashboard/data/jade_dashboard.json')); print('Valid')\"", "exitCode": 0, "observation": "JSON valid" },
      { "command": "python3 -m pytest tests/ -x -q", "exitCode": 0, "observation": "12 passed" },
      { "command": "curl -sf http://localhost:8765/index.html", "exitCode": 0, "observation": "HTML returned successfully" }
    ],
    "interactiveChecks": [
      { "action": "Opened http://localhost:8765/index.html in agent-browser", "observed": "Homepage loaded with all 7 modules visible. Movement Board is first module (above fold). Navigation bar shows 翡翠信号图谱 | 首页 | 方向地图 | 产品线观察 | 证据库" },
      { "action": "Checked accessibility snapshot for Chinese content", "observed": "All module titles in Chinese: 实时异动榜, 今日判断, 值得关注方向, 风险提醒, 最近证据, 产品线观察, 14天变化. Direction names: 18K 金镶翡翠, 多巴胺色系耳饰, 沉香 + 翡翠叠戴, 冰感小件吊坠" },
      { "action": "Verified judgment state color coding", "observed": "值得跟 badges are green, 观察中 blue, 短热噪音 orange. Consistent across Movement Board and Watchlist Cards" },
      { "action": "Checked browser console for errors", "observed": "0 errors, 0 warnings" }
    ]
  },
  "tests": {
    "added": []
  },
  "discoveredIssues": []
}
```

## When to Return to Orchestrator

- The feature depends on a shared CSS/JS file or data file that doesn't exist yet
- The existing shared CSS/JS has patterns that conflict with the feature's needs
- Mock data schema needs to change in ways that would break other pages
- A page requires functionality beyond static HTML/CSS/JS (e.g., server-side logic)
- Cannot achieve the visual quality expected without external assets (fonts, icons)
