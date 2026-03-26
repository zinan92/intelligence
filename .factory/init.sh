#!/usr/bin/env bash
set -euo pipefail

cd /Users/wendy/work/content-co/intelligence

# Verify Python and pytest are available
python3 --version
python3 -m pytest --version

# Run existing test suite to confirm baseline
python3 -m pytest tests/ -x -q

echo "Init complete. 74 tests passing."
