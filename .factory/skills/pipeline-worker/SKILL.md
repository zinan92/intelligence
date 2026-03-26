---
name: pipeline-worker
description: Upgrades Python pipeline code (schema, adapters, scoring, reporting) with TDD and backward compatibility
---

# Pipeline Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

Use for features that involve:
- Modifying Python dataclasses in the schema layer
- Upgrading adapter extraction logic
- Adding or modifying scoring engine buckets
- Adding or modifying report/output generation
- Adding utility functions (parsers, helpers)
- Writing tests for any of the above

## Required Skills

None.

## Work Procedure

### 1. Read Context First

Before writing any code:
- Read `AGENTS.md` for architecture, conventions, and boundaries
- Read the feature's `description`, `preconditions`, `expectedBehavior`, and `verificationSteps`
- Read the specific source files you'll be modifying
- Read existing tests that cover the code you're changing to understand test conventions

### 2. Write Tests First

For every behavioral change:
- Write a failing test FIRST that captures the expected behavior
- Run `python3 -m pytest tests/ -x -q` to confirm the test fails (red)
- Then implement the code to make it pass (green)

Match existing test style:
- `unittest.TestCase` subclasses preferred
- `TemporaryDirectory` for output isolation
- JSONL fixtures in `tests/fixtures/` if needed
- Descriptive test method names: `test_<what>_<expected_behavior>`

### 3. Implement Incrementally

- Make the smallest change that passes the test
- Run the full test suite after each change: `python3 -m pytest tests/ -x -q`
- If any existing test breaks, fix the issue before continuing
- Keep dataclasses frozen with `slots=True`
- All new fields must have defaults for backward compatibility

### 4. Verify Backward Compatibility

After implementation:
- Run `python3 -m pytest tests/ -x -q` — ALL tests must pass (existing + new)
- Verify existing construction patterns still work:
  ```python
  sample = CanonicalSample(provenance=..., content=...)  # no new args
  ```
- If the feature modifies pack output, run the pack CLI and inspect output:
  ```bash
  python -m intelligence run-pack jade --output-dir /tmp/jade-test
  python -m intelligence run-pack designer_streetwear --output-dir /tmp/sw-test
  ```

### 5. Commit

Commit with a clear message. Only commit source files in `src/intelligence/` and test files in `tests/`.

## Example Handoff

```json
{
  "salientSummary": "Added CanonicalEngagement dataclass with likes/saves/comments/shares fields. Updated mediacrawler adapter to parse Chinese number formats and populate engagement. Added 8 new tests: 3 for parsing (万-format, plain digits, edge cases), 3 for schema (construction, defaults, backward compat), 2 for adapter extraction. All 82 tests pass (74 existing + 8 new).",
  "whatWasImplemented": "src/intelligence/schema/canonical.py: Added CanonicalEngagement frozen dataclass. Added engagement field to CanonicalSample with default=None. src/intelligence/adapters/_common.py: Added parse_chinese_number() function handling 万/千 formats. src/intelligence/adapters/mediacrawler.py: Updated build call to extract liked_count/collected_count/comment_count/share_count into CanonicalEngagement.",
  "whatWasLeftUndone": "",
  "verification": {
    "commandsRun": [
      { "command": "python3 -m pytest tests/ -x -q", "exitCode": 0, "observation": "82 passed in 3.1s" },
      { "command": "python -m intelligence run-pack jade --output-dir /tmp/jade-test", "exitCode": 0, "observation": "All 6 output files written" }
    ],
    "interactiveChecks": [
      { "action": "Inspected /tmp/jade-test/normalized_samples.json", "observed": "engagement field present with likes=10, saves=5, comments=2, shares=1" },
      { "action": "Verified backward compat: CanonicalSample(provenance=p, content=c) still works", "observed": "No error, engagement defaults to None" }
    ]
  },
  "tests": {
    "added": [
      { "file": "tests/test_parsing.py", "cases": [
        { "name": "test_wan_format_parses_correctly", "verifies": "10万+ → 100000" },
        { "name": "test_decimal_wan_parses_correctly", "verifies": "2.1万 → 21000" },
        { "name": "test_edge_cases_return_none", "verifies": "None/empty/invalid → None" }
      ]}
    ]
  },
  "discoveredIssues": []
}
```

## When to Return to Orchestrator

- The feature requires modifying `pack_runner.py` flow in ways that could break existing output structure
- Existing tests fail in ways you can't resolve without architectural decisions
- The scoring upgrade needs design decisions about bucket weights that aren't specified
- The feature requires adding external dependencies (NEVER do this — return instead)
