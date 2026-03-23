# Migration Boundary Map

The rule is simple: `MediaCrawler` collects, `intelligence` interprets, and anything unrelated to those two stays out for now.

## Stays in `MediaCrawler`

- Site access, scraping, downloader logic, retries, and rate limiting
- Source authentication and session handling
- Raw export shape and collection-specific field capture
- Any fix whose only job is to get content out reliably

## Belongs in `intelligence`

- Canonical sample schema and normalization
- Adapters that read `MediaCrawler` exports into the research schema
- Scoring, validation, shortlist, and report generation
- Project-pack config, keywords, templates, and case-study docs
- CLI entry points and pack wiring for `jade`

## Intentionally outside both repos for now

- Dashboards, BI layers, and presentation apps
- Long-term storage and warehouse modeling
- Cross-service orchestration beyond file exchange
- Category governance or approval systems that do not change the research engine
- Reusable UX polish that is not needed to validate the first pack
