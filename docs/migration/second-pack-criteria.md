# Second Pack Criteria

Add category #2 only when jade proves the engine can be reused without new core logic.

## Readiness criteria

- Jade runs end to end with the current canonical sample path
- The first pack is stable enough that its core modules do not need category-specific branches
- The new category has a clear source fixture and a clear owner for review
- Its differences can be expressed mostly through config, keywords, and templates
- The current reporting shape is still the right shape for the new category

## What success looks like

- The second pack uses the same ingest, normalize, score, and report flow
- Most of the work is pack assets, not engine rewrites
- Any code change is small and reusable, not a one-off category fork
- Outputs are comparable to jade at the same canonical boundaries

## Guardrails

- Do not rewrite schema or scoring just to fit one category
- Do not expand `MediaCrawler` unless the category truly needs new collection behavior
- Do not add orchestration or multi-pack management before the second pack is proven
