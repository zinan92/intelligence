---
name: jade-dashboard-v2-worker
description: Builds and refines the Jade dashboard v2 showcase prototype with static HTML/CSS/JS and richer believable mock data
---

# Jade Dashboard V2 Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

Use for work that is specifically about the v2 Jade dashboard showcase, including:
- Creating or refining v2 dashboard pages in static HTML/CSS/JS
- Expanding or tuning the v2 mock data in `dashboard/data/jade_dashboard.json`
- Building high-fidelity showcase modules such as the bubble matrix, evidence wall, and homepage sparklines
- Improving the believability, consistency, and presentation quality of the v2 prototype
- Tightening cross-page visual consistency for the approved v2 direction

Do not use this skill for backend systems, crawling pipelines, authentication, production APIs, or report-engine work.

## Required Skills

None. Use standard file editing, validation, and local static-server tools only.

## V2 Operating Constraints

These are non-negotiable for v2:
- **Showcase-first:** optimize for a believable, decision-ready demo surface before optimizing for architecture purity or future extensibility.
- **Static only:** HTML, CSS, JSON, and vanilla JavaScript only. No backend, no login, no database, no real crawl, no build tooling.
- **No scope drift:** do not invent auth states, admin flows, ingestion pipelines, syncing, or "real data" plumbing.
- **Keep the data contract additive:** extend the JSON schema in backward-friendly ways instead of rewriting existing structures unless the task explicitly requires it.
- **Believable mock data matters:** every new direction, evidence item, summary metric, and chart value must agree with nearby content and not feel random.
- **Quality bar is visual and editorial:** the bubble matrix, evidence wall, and homepage sparklines must read as polished product surfaces, not placeholder widgets.

## Work Procedure

### 1. Read Context Before Touching Files

Before making changes:
- Read `README.md` and `dashboard/README.md`
- Read the task instructions in full, especially any requested page or module
- Read the existing shared files that your change depends on (`dashboard/css/style.css`, `dashboard/js/*.js`, relevant HTML pages)
- Read `dashboard/data/jade_dashboard.json` before changing data-driven UI
- If modifying an existing component, inspect the current implementation first and preserve working patterns where possible

### 2. Anchor Every Decision to the Approved V2 Direction

Assume the approved target is:
- showcase-first, high-fidelity, believable prototype
- static HTML/CSS/JS only
- no backend, no login, no crawl
- roughly 8-10 directions and 25-30 evidence items
- strong signature modules: bubble matrix, evidence wall, homepage sparklines

When several implementation choices are possible, choose the one that most improves perceived product quality in a static demo.

### 3. Change Data Carefully and Additively

When updating `dashboard/data/jade_dashboard.json`:
- Prefer adding fields over renaming or removing existing fields
- Preserve compatibility with current pages unless the task explicitly calls for coordinated page updates
- Keep counts, labels, statuses, direction summaries, and evidence references internally consistent
- Ensure each direction feels distinct in signal pattern, audience, price band, product-line relevance, and supporting evidence
- Target believable v2 density: around 8-10 directions and 25-30 evidence items unless the task specifies otherwise

If a schema change would force broad breakage or invalidate existing pages, stop and return to the orchestrator.

### 4. Build UI for Believability, Not for Engineering Theater

For HTML/CSS/JS work:
- Prefer clear semantic HTML and reusable shared styles
- Prefer SVG and vanilla JavaScript for data visualization over canvas or external libraries
- Keep visualizations lightweight, inspectable, and easy to tune
- Use motion and hover states sparingly; polish matters more than complexity
- Avoid exposing fake controls that imply unsupported backend behavior

For signature v2 modules:
- **Bubble matrix:** must feel analytically useful at a glance; spacing, axis labeling, bubble sizing, and color meaning should be immediately legible
- **Evidence wall:** must feel rich and editorial, with enough variation in card content, tags, timestamps, thumbnails, and takeaways to sell the demo
- **Homepage sparklines:** must support the surrounding narrative, be visually clean, and use data patterns that match each direction's stated momentum

### 5. Implement Incrementally

Preferred order:
1. Update or extend data model only as needed
2. Validate JSON syntax immediately after data edits
3. Implement shared rendering/helpers before page-specific glue when reuse is obvious
4. Build or refine the page/module markup
5. Tune styles for polish and consistency
6. Verify all affected pages still load cleanly in the static server

### 6. Verify Before Handoff

Run the checks that fit the task. For v2 page or data work, this usually means all of the following:
- `python3 -c "import json; json.load(open('dashboard/data/jade_dashboard.json')); print('JSON valid')"` after JSON edits
- `python3 -m pytest tests/ -x -q`
- Start local server for `dashboard/` and verify affected pages with `curl -sf`
- If page output changed, inspect the rendered result in a browser-capable tool when available and confirm no obvious console/runtime issues

Do not report success if the static pages fail to load, the JSON is invalid, or tests fail.

## Example Handoff

```json
{
  "salientSummary": "Upgraded the v2 showcase to emphasize decision-ready storytelling: homepage sparklines now reflect each direction's actual momentum pattern, direction map includes a bubble matrix comparing heat vs confidence, and the evidence page now presents a denser editorial evidence wall tied to 9 directions and 28 evidence items.",
  "whatWasImplemented": "Extended dashboard/data/jade_dashboard.json additively with sparkline series, bubble-matrix plotting fields, richer evidence metadata, and expanded cross-links between directions and evidence. Updated static rendering code to draw SVG sparklines and the bubble matrix in vanilla JS, and refined evidence cards to show stronger thumbnails, tags, timestamps, and takeaways.",
  "whatWasLeftUndone": "Did not add backend APIs, authentication, crawling hooks, or any non-static filtering persistence.",
  "verification": {
    "commandsRun": [
      {
        "command": "python3 -c \"import json; json.load(open('dashboard/data/jade_dashboard.json')); print('JSON valid')\"",
        "exitCode": 0,
        "observation": "JSON valid"
      },
      {
        "command": "python3 -m pytest tests/ -x -q",
        "exitCode": 0,
        "observation": "Existing tests passed"
      },
      {
        "command": "curl -sf http://localhost:8765/index.html > /dev/null && curl -sf http://localhost:8765/direction-map.html > /dev/null && curl -sf http://localhost:8765/evidence.html > /dev/null",
        "exitCode": 0,
        "observation": "Affected static pages loaded successfully"
      }
    ]
  }
}
```

## When to Return to Orchestrator

Return instead of forcing a solution when:
- The request would require backend services, login, persistence, or real crawling/integration
- A proposed data-schema change would require a rewrite rather than an additive extension
- The requested UI cannot be delivered convincingly within static HTML/CSS/JS
- The task conflicts with the approved v2 scope or quality bar
- The existing data/content is too thin to produce a believable result without broader product-direction decisions
