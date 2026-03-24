# Designer Streetwear Pack Example

Run the designer streetwear pack flow on your own MediaCrawler export:

```bash
python -m intelligence run-pack designer_streetwear \
  --input path/to/your_export.jsonl \
  --output-dir /tmp/streetwear-output
```

Or use the built-in fixture for a quick demo:

```bash
python -m intelligence run-pack designer_streetwear --output-dir /tmp/streetwear-demo
```

When `--input` is omitted the command falls back to the repo-local fixture at `tests/fixtures/mediacrawler_streetwear_export.jsonl`.

## Scoring Buckets

The streetwear pack scores content across six signal dimensions:

| Bucket | Weight | Detects |
|--------|--------|---------|
| silhouette | 0.20 | oversized, boxy, wide-leg, relaxed fit cues |
| graphic | 0.15 | prints, logos, embroidery, graffiti elements |
| layering | 0.20 | outfit composition, styling, mix-and-match |
| brand | 0.15 | brand names, collabs, designer labels |
| material | 0.10 | fabric and material references |
| commerce | 0.20 | purchase intent, reviews, price language |

## Outputs

- `normalized_samples.json`
- `scored_samples.json`
- `report.json`
- `report.md`
- `report.html`

## Input format

Same MediaCrawler JSONL format as the jade pack. See `examples/jade/README.md` for field reference.
