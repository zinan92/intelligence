# User Testing

**What belongs here:** How to test the pipeline, what tools to use, concurrency limits.

---

## Validation Surface

**Surface type:** CLI + output file inspection (no browser needed)
**Test command:** `python3 -m pytest tests/ -x -q`
**Pack run commands:**
- `python -m intelligence run-pack jade --output-dir /tmp/jade-test`
- `python -m intelligence run-pack designer_streetwear --output-dir /tmp/sw-test`
- `python -m intelligence run-pack designer_streetwear --input examples/designer_streetwear/real_pilot/streetwear_collected.jsonl --output-dir /tmp/sw-real-test`

**Testing tool:** pytest + shell commands (no agent-browser needed)

## Validation Concurrency

**Max concurrent validators:** 3

**Rationale:**
- Machine: 16GB RAM, 10 CPU cores
- Each validator runs pytest (lightweight, ~3s) or a pack CLI command (~5s for 293 posts)
- No browser, no server, no long-running process
- Conservative limit of 3 is well within resource budget
