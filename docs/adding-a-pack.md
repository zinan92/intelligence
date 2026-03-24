# Adding a Pack

A project pack teaches the intelligence engine about a specific research category.

## Required assets

Create a directory under `src/intelligence/projects/<pack_name>/` with:

```
<pack_name>/
├── __init__.py              # Docstring only, e.g. """My pack."""
├── config/
│   └── project.yaml         # Pack metadata (name, domain, purpose, keyword_groups)
├── keywords/
│   └── seed_keywords.csv    # CSV with group,keyword columns (at least 1 keyword row)
└── templates/               # At least one .md template (report.md recommended)
    └── report.md
```

### project.yaml

```yaml
name: my_pack
domain: xiaohongshu
purpose: my_research_purpose
contract:
  config: config/project.yaml
  keywords: keywords/seed_keywords.csv
  templates: templates/
  examples: optional
keyword_groups:
  - group_one
  - group_two
```

### seed_keywords.csv

```csv
group,keyword
group_one,关键词一
group_one,关键词二
group_two,keyword_three
```

## Required workflow module

Create `src/intelligence/workflows/<pack_name>_pack.py` with:

1. A `_bucket_scores(sample: CanonicalSample) -> dict[str, float]` function with your category-specific heuristics
2. A `ScoringConfig` defining bucket weights, confidence rules, and classification rules
3. A `PackSpec` instance wiring the above together
4. A thin `run_<pack_name>_pack()` wrapper calling `run_pack_flow()`

See `jade_pack.py` or `streetwear_pack.py` for working examples.

## Register in CLI

Add your `PackSpec` to `_PACK_SPECS` in `src/intelligence/cli.py`:

```python
from .workflows.my_pack import my_pack_spec

_PACK_SPECS = {
    "jade": jade_pack_spec,
    "designer_streetwear": streetwear_pack_spec,
    "my_pack": my_pack_spec,
}
```

## Add a fixture (recommended)

Create a small JSONL fixture at `tests/fixtures/mediacrawler_<pack_name>_export.jsonl` with representative samples. Include at least one on-category and one off-category row to test scoring differentiation.

## Validate

```bash
python -m intelligence validate-pack my_pack
```

This checks that all required assets exist and are well-formed.

## Run

```bash
# With fixture fallback
python -m intelligence run-pack my_pack --output-dir /tmp/my-output

# With real input
python -m intelligence run-pack my_pack --input path/to/export.jsonl --output-dir /tmp/my-output
```

## Outputs

Every pack produces the same five files:

- `normalized_samples.json` — canonical schema samples
- `scored_samples.json` — samples with bucket scores, weighted score, confidence, classification
- `report.json` — structured report
- `report.md` — human-readable markdown report
- `report.html` — HTML report
