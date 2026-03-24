# Jade Pack Example

Run the jade pack flow on your own MediaCrawler export:

```bash
python -m intelligence run-pack jade \
  --input path/to/your_export.jsonl \
  --output-dir /tmp/jade-output
```

Or use the built-in fixture for a quick demo:

```bash
python -m intelligence run-pack jade --output-dir /tmp/jade-pack-demo
```

When `--input` is omitted the command falls back to the repo-local fixture at `tests/fixtures/mediacrawler_jade_export.jsonl`.

## Outputs

- `normalized_samples.json`
- `scored_samples.json`
- `report.json`
- `report.md`
- `report.html`

## Input format

The input file should be a JSONL file (one JSON object per line) in MediaCrawler export format. Required fields per row:

| Field | Purpose |
|-------|---------|
| `note_id` | Unique identifier |
| `title` | Post title |
| `desc` | Post description / body text |
| `note_url` | Original URL |
| `time` | Published timestamp (ms) |
| `last_modify_ts` | Captured timestamp (ms) |
| `tag_list` | Comma-separated tags |
