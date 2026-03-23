# Intelligence Architecture

`intelligence` is the research layer that sits above collection tools and below any future presentation or productization layers.

## Layers

- `MediaCrawler`: collection engine
- `intelligence`: research engine
- `project packs`: category-specific configuration, keywords, scoring context, and output templates

## v1 Scope

The first version should stay thin:

- ingest upstream collection outputs
- normalize them into a canonical schema
- score evidence consistently across categories
- emit reports that are useful to humans and machines

## First Project Pack

`jade` is the first validated pack. Future packs should reuse the same engine and only swap project-specific config, labels, and templates.

