---
name: bridge-worker
description: Builds the data bridge between pipeline and dashboard — direction clustering, frontend JSON generation, data source switching, frontend bug fixes
---

# Bridge Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

Use for features that involve:
- Direction clustering logic (grouping scored posts into trends)
- Frontend dashboard JSON generation (building jade_dashboard.json-compatible output)
- Data source switching (updating data.js to load pipeline output)
- Frontend bug fixes (hardcoded product lines, missing judgment states, error handling)
- Both Python pipeline code and JavaScript dashboard code

## Required Skills

- `agent-browser` — for verifying frontend changes render correctly with real data

## Work Procedure

### 1. Read Context

- Read `AGENTS.md` for architecture, schema reference, conventions
- Read the feature description thoroughly
- For pipeline work: read existing `pack_runner.py`, `jade_dashboard.json` (schema reference)
- For frontend work: read the specific HTML/JS files you'll modify, plus `data.js` and `components.js`

### 2. Write Tests First (Pipeline Code)

For Python code:
- Write failing tests FIRST
- Run `python3 -m pytest tests/ -x -q` to confirm red
- Implement to make green
- Run full suite to verify no regressions

### 3. Implement

- Pipeline: create new modules in `src/intelligence/analysis/`
- Frontend: modify existing HTML/JS files
- Match the jade_dashboard.json schema EXACTLY — the frontend JS expects specific field names
- Use `related_direction` (not direction_id), `weight` (not relevance_weight), `rising`/`cooling`/`newly_emerging`

### 4. Verify Frontend Changes

For any feature that modifies dashboard HTML/JS:
- Start server: `python3 -m http.server 8765 --directory dashboard &`
- Use agent-browser to load affected pages
- Screenshot and verify rendering
- Check console for 0 errors
- Test with BOTH streetwear data AND jade data (backward compatibility)
- Kill server when done

### 5. Run Full Verification

- `python3 -m pytest tests/ -x -q` — all tests pass
- If feature generates frontend_dashboard.json: run pack and verify output schema
- If feature modifies frontend: verify in browser with agent-browser

### 6. Commit

Commit with clear message describing what was changed.

## Example Handoff

```json
{
  "salientSummary": "Implemented direction clustering for streetwear pack. 293 posts grouped into 8 trend directions using keyword_group overlap. Generated frontend_dashboard.json with full jade_dashboard.json schema compatibility. All 135 tests pass (123 existing + 12 new).",
  "whatWasImplemented": "src/intelligence/analysis/direction_clustering.py: cluster_into_directions() groups scored posts by keyword_group tag overlap, assigns judgment states based on aggregate score thresholds. src/intelligence/analysis/frontend_builder.py: build_frontend_dashboard() produces jade_dashboard.json-compatible JSON with trend_directions, product_lines, evidence_entries, today_judgments, fourteen_day_changes, executive_summary. tests/test_direction_clustering.py: 8 tests for clustering logic. tests/test_frontend_builder.py: 4 tests for schema conformance.",
  "whatWasLeftUndone": "",
  "verification": {
    "commandsRun": [
      { "command": "python3 -m pytest tests/ -x -q", "exitCode": 0, "observation": "135 passed in 3.2s" },
      { "command": "python3 -m intelligence run-pack designer_streetwear --input examples/designer_streetwear/real_pilot/streetwear_collected.jsonl --output-dir /tmp/bridge-test", "exitCode": 0, "observation": "7 output files including frontend_dashboard.json" }
    ],
    "interactiveChecks": [
      { "action": "Loaded index.html with streetwear data via agent-browser", "observed": "8 directions in Movement Board, judgment counts sum to 8, all modules populated" },
      { "action": "Loaded index.html with jade data (backward compat)", "observed": "9 jade directions, 4 judgment states, all modules work" }
    ]
  },
  "tests": {
    "added": [
      { "file": "tests/test_direction_clustering.py", "cases": [
        { "name": "test_clustering_produces_6_to_10_directions", "verifies": "293 posts → 6-10 directions" },
        { "name": "test_all_posts_assigned_to_at_least_one_direction", "verifies": "No orphaned posts" }
      ]}
    ]
  },
  "discoveredIssues": []
}
```

## When to Return to Orchestrator

- Schema mismatch between generated JSON and what frontend JS expects that you can't resolve
- Clustering produces < 6 or > 10 directions and threshold tuning is needed
- Frontend changes break jade data backward compatibility and you can't make both work
- Feature requires modifying files outside the agreed scope
