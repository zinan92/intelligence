# Task 2 Engine Scaffolding Design

**Goal:** Add category-neutral schema and scoring scaffolding for the research engine using only Python standard library primitives.

## Design Summary

The engine core stays generic and pack-agnostic. Canonical sample data will separate provenance metadata from research judgments, and review/validation state will be modeled explicitly instead of being inferred from scores.

The schema layer will use `dataclass` models plus `Enum` values for small, stable state vocabularies. The scoring layer will expose a configurable engine that accepts bucket weights, confidence rules, and classification rules supplied by the caller, while the engine itself remains neutral about category labels.

Workflow modules for ingest, shortlist, normalize, score, validate, and report will be placeholders only. Their purpose in this task is to stabilize the package shape for later migration tasks.

## Testing Strategy

- Add tests for canonical schema defaults and separation of concerns.
- Add tests for explicit review and validation state structures.
- Add tests for configurable score calculation, confidence evaluation, and classification.
- Add tests for placeholder workflow module import stability.

## Tradeoff

This task intentionally avoids a runtime validation framework. The result is lighter and easier to evolve early on, but field validation remains minimal until later tasks add richer normalization and input checks.
