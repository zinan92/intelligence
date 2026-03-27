---
name: dashboard-visual-worker
description: Upgrades dashboard pages with pure SVG/CSS charts and visual enhancements
---

# Dashboard Visual Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

Use for features that involve:
- Adding SVG charts to dashboard pages (area charts, donut charts, radar charts, bar charts)
- Enhancing existing SVG elements (bubble matrix quadrant shading, tooltips)
- Adding visual statistics sections

## Required Skills

- `agent-browser` — REQUIRED for every feature. Every visual change must be verified in browser.

## Work Procedure

### 1. Read Context

- Read `AGENTS.md` for color codes, chart conventions, off-limits libraries
- Read the feature description and the specific HTML/JS/CSS files
- Read `dashboard/data/jade_dashboard.json` to understand the data shape your chart consumes
- If the feature depends on pipeline-generated data, run the pipeline first to get `frontend_dashboard.json`

### 2. Plan the Chart

Before coding:
- Determine SVG viewBox dimensions
- Plan data→visual mapping (what data field → what visual attribute)
- Plan colors (use CSS custom properties from style.css)
- Plan interaction behavior (hover, click, filter)

### 3. Implement the Chart

- Create SVG elements programmatically in JS (document.createElementNS)
- Use viewBox for responsive sizing
- All labels/legends in Chinese
- Colors from CSS custom properties:
  - 值得跟: var(--color-judgment-zhidegeng) / #10b981
  - 观察中: var(--color-judgment-guancharzhong) / #3b82f6
  - 短热噪音: var(--color-judgment-duanrezaoyin) / #f59e0b
  - 需要补证据: var(--color-judgment-xuyaobuzhengju) / #6b7280

### 4. Verify in Browser (REQUIRED)

For EVERY feature:
- Start server: `python3 -m http.server 8765 --directory dashboard &`
- Use agent-browser to load the page
- Take screenshots showing the chart
- Verify chart is visible, correctly sized, properly colored
- Verify no console errors
- Test with BOTH streetwear and jade data if applicable
- For interactive features (tooltips, filter updates): test the interaction
- Kill server when done

### 5. Verify No Library Dependencies

- Search all HTML files for script tags — none should reference external charting libraries
- All chart code must be inline JS creating SVG elements

### 6. Commit

Commit with clear message.

## Example Handoff

```json
{
  "salientSummary": "Added 14-day trend area chart to direction detail page. Pure SVG, 400x180px, shows movement_history as filled area with gradient. Works with both streetwear and jade data.",
  "whatWasImplemented": "dashboard/direction-detail.html: Added renderTrendChart(direction) function creating SVG area chart. Path computed from movement_history array (14 points). Green gradient fill, 2px stroke line. Axis labels for day 1 and day 14. Responsive via viewBox. dashboard/css/style.css: Added .trend-chart-container styles.",
  "whatWasLeftUndone": "",
  "verification": {
    "commandsRun": [
      { "command": "python3 -m http.server 8765 --directory dashboard &", "exitCode": 0, "observation": "Server started" }
    ],
    "interactiveChecks": [
      { "action": "Loaded direction-detail.html?id=dir_001 with jade data", "observed": "Area chart visible, 400x180px, green gradient fill, 14 data points plotted correctly" },
      { "action": "Loaded direction-detail.html?id=sw_001 with streetwear data", "observed": "Same chart style, different data shape, renders correctly" },
      { "action": "Checked for external libraries", "observed": "No D3/Chart.js script tags found, SVG created by renderTrendChart() function" }
    ]
  },
  "tests": { "added": [] },
  "discoveredIssues": []
}
```

## When to Return to Orchestrator

- SVG chart cannot be implemented without an external library (explain why)
- Data shape from pipeline doesn't match what the chart needs
- Chart causes performance issues (e.g., 293 data points overwhelming the SVG)
- Backward compatibility with jade data cannot be maintained
