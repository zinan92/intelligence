# Jade Pack Example

Run the tiny jade proof flow from the repo root:

```bash
python -m intelligence run-pack jade --output-dir /tmp/jade-pack-demo
```

The command uses only the repo-local fixture at `tests/fixtures/mediacrawler_jade_export.jsonl` and writes:

- `normalized_samples.json`
- `scored_samples.json`
- `report.json`
- `report.md`
- `report.html`

This example is intentionally small so the jade pack can be validated without external services or live collection inputs.
