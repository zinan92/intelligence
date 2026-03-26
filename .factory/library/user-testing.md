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

## Flow Validator Guidance: CLI

**Surface:** Python CLI + pytest + output file inspection
**Working directory:** `/Users/wendy/work/content-co/intelligence`
**No services needed:** This is a pure Python pipeline with no database, no network, no server.

**Isolation rules:**
- Each validator should use its own output directory (e.g., `/tmp/val-<group-id>/`) for CLI runs
- Validators do NOT modify source code — they only run tests and inspect outputs
- pytest tests are read-only and can safely run in parallel
- CLI pack runs write to separate output dirs, no shared state

**Testing approach:**
- For pytest-based assertions: run `python3 -m pytest tests/ -k <test_pattern> -v` to target specific tests
- For CLI output assertions: run `python -m intelligence run-pack <pack> --output-dir /tmp/val-<id>/` then inspect JSON files
- For schema assertions: use Python one-liners to import and construct dataclasses
- Evidence: capture command output and exit codes

**Key paths:**
- Schema: `src/intelligence/schema/canonical.py`
- Adapters: `src/intelligence/adapters/` (mediacrawler.py, xhs_downloader.py, douyin_downloader.py, _common.py)
- Scoring: `src/intelligence/scoring/engine.py`
- Pack runner: `src/intelligence/workflows/pack_runner.py`
- Tests: `tests/`
