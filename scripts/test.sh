#!/bin/bash
# Run all tests (backend + frontend, excluding E2E)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "Running Backend Tests"
echo "========================================"
cd "$ROOT_DIR/backend"
python3 -m pytest --ignore=tests/e2e -v

echo ""
echo "========================================"
echo "Running Frontend Tests"
echo "========================================"
cd "$ROOT_DIR/frontend"
npm run test:run

echo ""
echo "========================================"
echo "All tests passed!"
echo "========================================"
