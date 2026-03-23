# intelligence

`intelligence` is a multi-category research engine for turning collected social content into structured signals, trend maps, and product briefs.

Its boundary is intentionally split into three layers:

- `MediaCrawler` = collection engine
- `intelligence` = research engine
- `jade` = first project pack

This repository is the research layer. It consumes outputs from collection tools and project-specific packs, normalizes them into a shared schema, scores evidence, and produces decision-oriented reports.

## What this repo is for

- ingesting collected content from upstream tools
- normalizing research samples into a canonical structure
- scoring evidence across multiple categories
- generating human-readable and machine-readable outputs

## Install

```bash
pip install -e .
```

## CLI

After installation, run:

```bash
intelligence --help
```

