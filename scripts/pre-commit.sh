#!/bin/bash
# Pre-commit hook script
# Run this before committing to ensure code quality

set -e  # Exit on any error

echo "🔧 Running pre-commit checks..."

# Check if we're in git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository"
    exit 1
fi

# Check for staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [ -z "$STAGED_FILES" ]; then
    echo "ℹ️  No Python files staged for commit"
    exit 0
fi

echo "📝 Checking staged Python files:"
echo "$STAGED_FILES"

# Format and lint only staged files
echo "Running black on staged files..."
echo "$STAGED_FILES" | xargs uv run black

echo "Running isort on staged files..."
echo "$STAGED_FILES" | xargs uv run isort

echo "Running ruff check on staged files..."
echo "$STAGED_FILES" | xargs uv run ruff check --fix

# Re-stage the files after formatting
echo "Re-staging formatted files..."
echo "$STAGED_FILES" | xargs git add

echo "✅ Pre-commit checks passed!"