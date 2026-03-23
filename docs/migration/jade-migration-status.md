# Jade Migration Status

Status at the end of Task 7.

## Already moved into `intelligence`

- Canonical sample shape and provenance handling
- Loading `MediaCrawler` exports for jade fixtures
- Normalization, scoring, and reporting flow
- Jade pack config, seed keywords, and output templates
- Case-study docs for the jade sample frame and scoring notes
- CLI support for `run-pack jade`

## Intentionally deferred

- Any broader `MediaCrawler` refactor beyond the current export contract
- Richer validation or taxonomy systems that would slow the first pack
- Non-jade output formats and multi-service orchestration
- Pack automation that is not needed to validate jade end to end

## What remains for a second category

- A new pack directory with its own config, keywords, and templates
- Category-specific scoring context and output language
- Small registration or wiring updates so the CLI can discover the new pack
- Pack-local docs or case-study notes needed to explain that category
