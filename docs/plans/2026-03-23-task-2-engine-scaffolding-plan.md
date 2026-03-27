# Task 2 Engine Scaffolding Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add stdlib-only schema, scoring, and workflow scaffolding for Task 2.

**Architecture:** Use package-local dataclasses and enums for canonical schema plus review structures. Use a small scoring engine configured by caller-provided weights and rule mappings. Provide no-op workflow placeholders so downstream imports have stable module paths.

**Tech Stack:** Python 3.10+, `dataclasses`, `enum`, `unittest`

---

### Task 1: Add failing tests

**Files:**
- Create: `tests/test_schema.py`
- Create: `tests/test_scoring_engine.py`
- Create: `tests/test_workflows.py`

**Step 1: Write the failing tests**

Add tests for:
- canonical sample structure and provenance/judgment separation
- explicit review and validation state modeling
- configurable weighted scoring, confidence, and classification
- placeholder workflow imports

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_schema.py tests/test_scoring_engine.py tests/test_workflows.py -q`

Expected: failures caused by missing modules or missing symbols.

### Task 2: Implement minimal scaffolding

**Files:**
- Create: `src/intelligence/adapters/__init__.py`
- Create: `src/intelligence/schema/__init__.py`
- Create: `src/intelligence/schema/canonical.py`
- Create: `src/intelligence/schema/review.py`
- Create: `src/intelligence/workflows/__init__.py`
- Create: `src/intelligence/workflows/ingest.py`
- Create: `src/intelligence/workflows/shortlist.py`
- Create: `src/intelligence/workflows/normalize.py`
- Create: `src/intelligence/workflows/score.py`
- Create: `src/intelligence/workflows/validate.py`
- Create: `src/intelligence/workflows/report.py`
- Create: `src/intelligence/scoring/__init__.py`
- Create: `src/intelligence/scoring/engine.py`
- Create: `src/intelligence/reporting/__init__.py`

**Step 1: Write the minimal implementation**

Implement only the dataclasses, enums, helpers, scoring engine, and workflow placeholders required by tests.

**Step 2: Run tests to verify they pass**

Run: `python -m pytest tests/test_schema.py tests/test_scoring_engine.py tests/test_workflows.py -q`

Expected: all targeted tests pass.

### Task 3: Verify and commit

**Files:**
- Verify current working tree

**Step 1: Run full test suite**

Run: `python -m pytest -q`

Expected: full suite passes.

**Step 2: Commit**

```bash
git add docs/plans tests src
git commit -m "feat: scaffold schema and scoring engine"
```
