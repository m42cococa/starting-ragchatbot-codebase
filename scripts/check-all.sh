#!/bin/bash
# Run all code quality checks and formatting

set -e  # Exit on any error

echo "🚀 Running complete code quality pipeline..."

echo "📋 Step 1: Formatting code..."
./scripts/format.sh

echo "📋 Step 2: Running linting..."
./scripts/lint.sh

echo "📋 Step 3: Running tests (if available)..."
if [ -d "backend/tests" ] || [ -d "tests" ]; then
    echo "Running pytest..."
    cd backend && uv run pytest -v || cd ..
else
    echo "No tests directory found, skipping tests"
fi

echo "✅ All code quality checks passed!"