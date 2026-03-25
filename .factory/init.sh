#!/usr/bin/env bash
set -euo pipefail

cd /Users/wendy/work/content-co/intelligence

# Create dashboard directory structure if it doesn't exist
mkdir -p dashboard/css dashboard/js dashboard/data

# Ensure no stale server on port 8765
lsof -ti :8765 | xargs kill 2>/dev/null || true

echo "Init complete. Dashboard directory ready."
