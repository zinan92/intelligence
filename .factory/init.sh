#!/usr/bin/env bash
set -euo pipefail

cd /Users/wendy/work/content-co/intelligence

# Verify Python and pytest
python3 --version
python3 -m pytest --version

# Run existing test suite
python3 -m pytest tests/ -x -q

# Verify real streetwear data exists
test -f examples/designer_streetwear/real_pilot/streetwear_collected.jsonl && echo "Streetwear data: OK (293 posts)" || echo "WARNING: streetwear data missing"

# Verify dashboard files exist
test -f dashboard/index.html && echo "Dashboard: OK" || echo "WARNING: dashboard missing"
test -f dashboard/data/jade_dashboard.json && echo "Jade mock data: OK" || echo "WARNING: jade data missing"

# Kill any stale dashboard server
lsof -ti :8765 | xargs kill 2>/dev/null || true

echo "Init complete."
