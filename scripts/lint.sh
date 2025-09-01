#!/bin/bash
# Run code quality checks

echo "🔍 Running code quality checks..."

echo "Running ruff check..."
uv run ruff check . --fix

echo "Running ruff format check..."
uv run ruff format --check .

echo "✅ Code quality checks complete!"