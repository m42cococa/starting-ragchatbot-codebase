#!/bin/bash
# Format code with black and isort

echo "🎨 Formatting Python code..."

echo "Running black..."
uv run black .

echo "Running isort..."
uv run isort .

echo "✅ Code formatting complete!"